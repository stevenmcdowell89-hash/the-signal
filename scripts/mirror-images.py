#!/usr/bin/env python3
"""
Mirror external images referenced in HTML files into a local cache.

For each external image URL found in an HTML file (in <img src="..."> or
CSS url('...')), downloads the image to /assets/cached/<hash>.<ext> and
rewrites the HTML to reference the local path. Idempotent — re-running on
already-mirrored issues is a no-op.

Failed downloads (404, timeout, etc.) leave the original URL in place so
the issue still renders online, and the failure is logged.

Usage:
    python3 scripts/mirror-images.py                       # all /issues/*.html
    python3 scripts/mirror-images.py path/to/x.html        # specific files
    python3 scripts/mirror-images.py --include-index       # also index.html
    python3 scripts/mirror-images.py --report-only         # show what would change
"""

import argparse
import hashlib
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = REPO_ROOT / "assets" / "cached"
ISSUES_DIR = REPO_ROOT / "issues"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

CONTENT_TYPE_EXT = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
    "image/svg+xml": "svg",
    "image/avif": "avif",
}

# <img src="https://..."> and similar attributes
SRC_RE = re.compile(
    r'(src=["\'])'
    r'(https?://[^"\']+?\.(?:jpe?g|png|webp|gif|svg|avif)(?:\?[^"\']*)?)'
    r'(["\'])',
    re.IGNORECASE,
)

# CSS url('https://...') / url("...") / url(...)
URL_RE = re.compile(
    r"(url\(\s*['\"]?)"
    r"(https?://[^)'\"\s]+)"
    r"(['\"]?\s*\))",
    re.IGNORECASE,
)


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:12]


def guess_ext(url: str, content_type: str | None = None) -> str:
    if content_type:
        ct = content_type.split(";")[0].strip().lower()
        if ct in CONTENT_TYPE_EXT:
            return CONTENT_TYPE_EXT[ct]
    path = urlparse(url).path.lower()
    for ext in ("avif", "webp", "jpeg", "jpg", "png", "gif", "svg"):
        if path.endswith("." + ext):
            return "jpg" if ext == "jpeg" else ext
    return "jpg"


def existing_cached(url: str) -> Path | None:
    matches = list(CACHE_DIR.glob(f"{url_hash(url)}.*"))
    return matches[0] if matches else None


def local_ref(target: Path) -> str:
    rel = target.relative_to(REPO_ROOT)
    return "/" + str(rel).replace("\\", "/")


def download(url: str, retries: int = 3) -> tuple[Path | None, str]:
    existing = existing_cached(url)
    if existing:
        return existing, "cached"

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    backoff = 2.0
    last_status = "failed:unknown"
    for attempt in range(retries):
        try:
            resp = requests.get(
                url,
                headers={"User-Agent": USER_AGENT, "Referer": "https://the-signal.steven-mcdowell-89.workers.dev/"},
                timeout=30,
                stream=True,
            )
            if resp.status_code == 429 or resp.status_code >= 500:
                last_status = f"failed:HTTP {resp.status_code}"
                import time
                time.sleep(backoff)
                backoff *= 2
                continue
            if resp.status_code != 200:
                return None, f"failed:HTTP {resp.status_code}"

            ct = resp.headers.get("Content-Type", "")
            if "image" not in ct.lower() and "octet-stream" not in ct.lower():
                return None, f"failed:not-image ({ct[:40]})"

            ext = guess_ext(url, ct)
            target = CACHE_DIR / f"{url_hash(url)}.{ext}"
            with open(target, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            size = target.stat().st_size
            if size < 200:
                target.unlink()
                return None, f"failed:tiny-response ({size}b)"
            return target, "downloaded"
        except requests.RequestException as e:
            last_status = f"failed:{type(e).__name__}"
            import time
            time.sleep(backoff)
            backoff *= 2
    return None, last_status


def find_urls_in(content: str) -> set[str]:
    urls: set[str] = set()
    for m in SRC_RE.finditer(content):
        urls.add(m.group(2))
    for m in URL_RE.finditer(content):
        # Only treat as image if the URL looks like one (extension or known image host)
        url = m.group(2)
        if re.search(r"\.(jpe?g|png|webp|gif|svg|avif)(\?|$)", url, re.IGNORECASE):
            urls.add(url)
    return urls


def rewrite_content(content: str, url_to_local: dict[str, str]) -> str:
    def sub_src(m):
        url = m.group(2)
        return m.group(1) + url_to_local.get(url, url) + m.group(3)

    def sub_url(m):
        url = m.group(2)
        return m.group(1) + url_to_local.get(url, url) + m.group(3)

    content = SRC_RE.sub(sub_src, content)
    content = URL_RE.sub(sub_url, content)
    return content


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="HTML files (default: all /issues/*.html)")
    ap.add_argument("--include-index", action="store_true")
    ap.add_argument("--report-only", action="store_true", help="Show URLs without downloading or rewriting")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    if args.files:
        targets = [Path(f).resolve() for f in args.files]
    else:
        targets = sorted(ISSUES_DIR.glob("*.html"))
        if args.include_index:
            targets.append(REPO_ROOT / "index.html")

    # Collect every unique URL across all targets first
    all_urls: set[str] = set()
    per_file_urls: dict[Path, set[str]] = {}
    for path in targets:
        content = path.read_text(encoding="utf-8")
        urls = find_urls_in(content)
        per_file_urls[path] = urls
        all_urls.update(urls)

    print(f"Found {len(all_urls)} unique external image URLs across {len(targets)} files.")

    if args.report_only:
        for u in sorted(all_urls):
            print(f"  {u}")
        return

    # Download (in parallel)
    url_to_local: dict[str, str] = {}
    stats: dict[str, int] = {"cached": 0, "downloaded": 0}
    failures: list[tuple[str, str]] = []

    def work(url: str) -> tuple[str, Path | None, str]:
        target, status = download(url)
        return url, target, status

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(work, u) for u in sorted(all_urls)]
        for i, fut in enumerate(as_completed(futures), 1):
            url, target, status = fut.result()
            if target:
                url_to_local[url] = local_ref(target)
                stats[status] = stats.get(status, 0) + 1
            else:
                failures.append((url, status))
            if i % 25 == 0 or i == len(futures):
                print(f"  progress: {i}/{len(futures)}")

    # Rewrite files
    modified_count = 0
    for path in targets:
        if not per_file_urls[path]:
            continue
        original = path.read_text(encoding="utf-8")
        new = rewrite_content(original, url_to_local)
        if new != original:
            path.write_text(new, encoding="utf-8")
            modified_count += 1
            print(f"  rewrote {path.relative_to(REPO_ROOT)}")

    # Report
    print()
    print(f"Downloaded: {stats['downloaded']}")
    print(f"Already cached: {stats['cached']}")
    print(f"Failed: {len(failures)}")
    print(f"Files modified: {modified_count}")
    if failures:
        print("\nFailures:")
        for url, reason in failures:
            print(f"  {reason:40s}  {url}")

    sys.exit(0 if len(failures) == 0 else 1 if modified_count == 0 else 0)


if __name__ == "__main__":
    main()
