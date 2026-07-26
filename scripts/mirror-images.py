#!/usr/bin/env python3
"""
Mirror external images referenced in HTML files into a local cache, and
maintain the durable provenance record for everything in that cache.

For each external image URL found in an HTML file (in <img src="..."> or
CSS url('...')), downloads the image to /assets/cached/<hash>.<ext> and
rewrites the HTML to reference the local path. Idempotent — re-running on
already-mirrored issues is a no-op.

Failed downloads (404, timeout, etc.) leave the original URL in place so
the issue still renders online, and the failure is logged.

WP-8 / SPEC §3.10 — assets/cached/manifest.json
------------------------------------------------
The cache is content-addressed as sha256(url)[:12], which is one-way: once
the HTML has been rewritten to /assets/cached/<hash>.<ext>, the source URL is
gone and a caption's provenance claim can no longer be audited. (Verified the
hard way: ~400 Wikimedia Commons candidates and their thumbnail variants were
reverse-hashed against Issue #18's cached files and none matched.)

So every run now writes `assets/cached/manifest.json`, keyed by the same
12-char hash:

    { "<sha256(url)[:12]>": {
        "url":          "https://…"        | "UNKNOWN",
        "fetched_at":   "2026-07-26T…Z"    | "UNKNOWN",
        "licence": { "holder": "…" | "UNKNOWN",
                     "code":   "CC-BY-2.5" | "UNKNOWN",
                     "url":    "https://…" | "UNKNOWN",
                     "allows_derivatives": true | false | null },
        "shows":        "in_engine"        | "UNKNOWN",
        "capture_year": 2007 | null        | "UNKNOWN",
        "issues":       [18],              // weekly issue numbers
        "led":          [18],              // issues where this was the cover
        "issue_slugs":  ["signal_weekly_2026-07-26"],
        "led_slugs":    ["signal_weekly_2026-07-26"],
        "notes":        "…" } }

Unknowns are written explicitly, never omitted. A missing key is silent; an
explicit marker is auditable. Note the two distinct markers:
  * `"UNKNOWN"` (the string) for anything whose absence is a gap in the record.
  * `null` for `licence.allows_derivatives`, because booleans have no string
    form and callers must be able to tell "known permissive" from "unknown".
  * `capture_year` uses `"UNKNOWN"` because `null` is a *legitimate* value
    there (SPEC §3.2: null when `shows` ∈ {diagram, chart} and synthetic).

What this script can and cannot know
------------------------------------
Its inputs are HTML/CSS documents, so it knows `url`, `fetched_at`, and — by
scanning the rendered issues — `issues`/`led`. It does **not** know `licence`,
`shows` or `capture_year`: those originate upstream in the research bundle's
`image_candidates[]` (SPEC §3.2) and this script must never invent them.

  | field                     | filled by                                  |
  |---------------------------|--------------------------------------------|
  | url, fetched_at           | this script, at download time              |
  | issues, led, *_slugs      | this script, by scanning /issues/*.html    |
  | licence{holder,code,url,  | research bundle → manifest; contract owned |
  |   allows_derivatives}     | by WP-1 (§3.2), presence enforced by WP-5  |
  | shows, capture_year       | (validate-research-bundle.py), and wired   |
  |                           | into the publish phase by WP-9 (SKILL.md)  |

Until that wiring lands, licence/shows/capture_year stay "UNKNOWN" for new
images too — which is the honest state, and is what makes the gap visible.

Files cached before the manifest existed are backfilled with unknown
provenance and a note saying so. Their source URLs are genuinely
unrecoverable (the hash is one-way and the pre-rewrite HTML was never
committed); they are not guessed from credit strings.

Merge-on-write: this file is durable provenance. Existing entries are never
dropped and a known value is never overwritten with an unknown one. The write
is atomic (temp file + os.replace), and a manifest that fails to parse aborts
the run rather than being silently replaced.

Usage:
    python3 scripts/mirror-images.py                       # all /issues/*.html
    python3 scripts/mirror-images.py path/to/x.html        # specific files
    python3 scripts/mirror-images.py --include-index       # also index.html
    python3 scripts/mirror-images.py --report-only         # show what would change
    python3 scripts/mirror-images.py --manifest-only       # reconcile manifest, no network
    python3 scripts/mirror-images.py --manifest PATH       # write elsewhere (tests)
"""

import argparse
import hashlib
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = REPO_ROOT / "assets" / "cached"
ISSUES_DIR = REPO_ROOT / "issues"
MANIFEST_PATH = CACHE_DIR / "manifest.json"
ARCHIVE_MANIFEST = REPO_ROOT / "archive-manifest.json"

# Explicit unknown markers — see module docstring.
UNKNOWN = "UNKNOWN"

PRE_MANIFEST_NOTE = (
    "Cached before assets/cached/manifest.json existed (WP-8, 2026-07-26). "
    "Source URL is unrecoverable: sha256(url)[:12] is one-way and the "
    "pre-rewrite HTML was never committed. Not inferred from the credit line."
)

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


# ---------------------------------------------------------------------------
# WP-8 / SPEC §3.10 — assets/cached/manifest.json
# ---------------------------------------------------------------------------

# A rewritten reference to a cached asset: /assets/cached/<hash>.<ext>
CACHED_REF_RE = re.compile(r"/assets/cached/([0-9a-f]{12})\.[A-Za-z0-9]+")

# Cover regions, in priority order. Kept in step with extract-covers.py — the
# two scripts must agree on which figure "led" an issue. They cannot share a
# helper module because SPEC §2 makes file ownership exclusive and WP-8 owns no
# third file; see the handoff note in the WP-8 evidence file.
COVER_REGION_RES = [
    re.compile(r'<header\s+class="[^"]*\bcover\b[^"]*"[^>]*>(.*?)</header>', re.I | re.S),
    re.compile(r'<section\s+class="[^"]*\bhol-cover\b[^"]*"[^>]*>(.*?)</section>', re.I | re.S),
    re.compile(r'<section\s+class="[^"]*\bmx-cover\b[^"]*"[^>]*>(.*?)</section>', re.I | re.S),
]


def _dom_only(html: str) -> str:
    """Strip comments/<style>/<script> so example markup in inlined CSS is not
    mistaken for real DOM (same guard as extract-covers.py)."""
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    html = re.sub(r"<style\b[^>]*>.*?</style>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<script\b[^>]*>.*?</script>", " ", html, flags=re.S | re.I)
    return html


def blank_entry() -> dict:
    """A provenance record with every field present and explicitly unknown."""
    return {
        "url": UNKNOWN,
        "fetched_at": UNKNOWN,
        "licence": {
            "holder": UNKNOWN,
            "code": UNKNOWN,          # SPDX-ish token per SPEC §3.2
            "url": UNKNOWN,
            "allows_derivatives": None,   # null == unknown; true/false == known
        },
        "shows": UNKNOWN,             # enum SPEC §3.3 once known
        "capture_year": UNKNOWN,      # int, or null when legitimately n/a
        "issues": [],
        "led": [],
        "issue_slugs": [],
        "led_slugs": [],
        "notes": "",
    }


def _is_unknown(value) -> bool:
    """True when `value` carries no information. `None` counts as unknown only
    for allows_derivatives; capture_year handles its own null separately."""
    return value is None or value == UNKNOWN


def _merge_scalar(entry: dict, key: str, incoming: dict, *, null_is_known: bool = False) -> None:
    """Fill a gap from `incoming[key]`; never overwrite a known value with an
    unknown one, and never invent a value for a key `incoming` does not carry.

    `null_is_known=True` marks a field where `null` is meaningful data rather
    than a gap (capture_year, SPEC §3.2)."""
    if key not in incoming:
        return
    value = incoming[key]
    if value is None and not null_is_known:
        return
    if value == UNKNOWN:
        return
    current = entry.get(key, UNKNOWN)
    unknown_now = current == UNKNOWN if null_is_known else _is_unknown(current)
    if unknown_now:
        entry[key] = value


def _merge_list(entry: dict, key: str, incoming) -> None:
    """Union, stable-sorted. Usage history is append-only: an image that
    appeared in issue 17 appeared in issue 17 even if 17 is later edited."""
    merged = list(entry.get(key) or [])
    for item in incoming or []:
        if item not in merged:
            merged.append(item)
    entry[key] = sorted(merged, key=lambda v: (isinstance(v, str), v))


def merge_entry(existing: dict | None, incoming: dict) -> dict:
    """Merge `incoming` into `existing` without losing anything."""
    entry = blank_entry()
    if existing:
        # Preserve every key already on disk, including any this script does
        # not know about (a later phase may have added fields).
        entry.update(existing)
    licence = blank_entry()["licence"]
    licence.update(entry.get("licence") or {})
    entry["licence"] = licence

    _merge_scalar(entry, "url", incoming)
    _merge_scalar(entry, "fetched_at", incoming)
    _merge_scalar(entry, "shows", incoming)
    _merge_scalar(entry, "capture_year", incoming, null_is_known=True)

    incoming_licence = incoming.get("licence") or {}
    for key in incoming_licence:
        if key == "allows_derivatives":
            value = incoming_licence[key]
            if value is not None and entry["licence"].get("allows_derivatives") is None:
                entry["licence"]["allows_derivatives"] = value
        else:
            _merge_scalar(entry["licence"], key, incoming_licence)

    for key in ("issues", "led", "issue_slugs", "led_slugs"):
        _merge_list(entry, key, incoming.get(key))

    if not entry.get("notes") and incoming.get("notes"):
        entry["notes"] = incoming["notes"]

    for key, value in incoming.items():
        if key not in entry:
            entry[key] = value
    return entry


def load_manifest(path: Path) -> dict:
    """Read the manifest. A corrupt manifest aborts — silently starting fresh
    would destroy provenance, which is the one thing this file exists to keep."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        sys.exit(
            f"FATAL: {path} exists but is not valid JSON ({exc}).\n"
            "Refusing to overwrite it — that would lose provenance. "
            "Fix or move the file, then re-run."
        )
    if not isinstance(data, dict):
        sys.exit(f"FATAL: {path} must contain a JSON object keyed by asset hash.")
    return data


def write_manifest(path: Path, manifest: dict) -> None:
    """Atomic write, so an interrupted run cannot truncate the record."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(tmp, path)


def slug_to_issue_number() -> dict[str, int]:
    """slug -> weekly issue number, from archive-manifest.json. Specials have
    no number; they are recorded by slug only."""
    if not ARCHIVE_MANIFEST.exists():
        return {}
    try:
        data = json.loads(ARCHIVE_MANIFEST.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
    out: dict[str, int] = {}
    for issue in data.get("issues") or []:
        slug, number = issue.get("slug"), issue.get("issue_number")
        if slug and isinstance(number, int):
            out[slug] = number
    return out


def scan_issue_usage() -> dict[str, dict]:
    """Which cached assets each published issue uses, and which one led it.

    Returns {hash: {"issues": [...], "led": [...], "issue_slugs": [...],
    "led_slugs": [...]}} — the honestly-knowable half of the record."""
    numbers = slug_to_issue_number()
    usage: dict[str, dict] = {}

    def touch(asset_hash: str) -> dict:
        return usage.setdefault(
            asset_hash,
            {"issues": [], "led": [], "issue_slugs": [], "led_slugs": []},
        )

    for html_path in sorted(ISSUES_DIR.glob("*.html")):
        slug = html_path.stem
        number = numbers.get(slug)
        dom = _dom_only(html_path.read_text(encoding="utf-8"))

        for asset_hash in {m.group(1) for m in CACHED_REF_RE.finditer(dom)}:
            record = touch(asset_hash)
            if slug not in record["issue_slugs"]:
                record["issue_slugs"].append(slug)
            if number is not None and number not in record["issues"]:
                record["issues"].append(number)

        lead_hash = None
        for region_re in COVER_REGION_RES:
            match = region_re.search(dom)
            if match:
                inner = CACHED_REF_RE.search(match.group(1))
                if inner:
                    lead_hash = inner.group(1)
                    break
        if lead_hash is None:
            first = CACHED_REF_RE.search(dom)
            lead_hash = first.group(1) if first else None
        if lead_hash:
            record = touch(lead_hash)
            if slug not in record["led_slugs"]:
                record["led_slugs"].append(slug)
            if number is not None and number not in record["led"]:
                record["led"].append(number)

    return usage


def update_manifest(
    manifest_path: Path,
    fetched: dict[str, str] | None = None,
    known_urls: set[str] | None = None,
) -> tuple[dict, dict[str, int]]:
    """Merge this run's findings into the manifest and write it back.

    `fetched`   url -> ISO8601 timestamp for URLs downloaded in this run.
    `known_urls` every URL seen in this run whose bytes are in the cache.
    """
    fetched = fetched or {}
    known_urls = set(known_urls or ()) | set(fetched)

    before = load_manifest(manifest_path)
    manifest = dict(before)
    counts = {"new": 0, "updated": 0, "backfilled": 0, "unchanged": 0, "total": 0}

    incoming: dict[str, dict] = {}

    # 1. URLs seen this run — the only place a source URL is ever learned.
    for url in known_urls:
        entry = incoming.setdefault(url_hash(url), {})
        entry["url"] = url
        if url in fetched:
            entry["fetched_at"] = fetched[url]

    # 2. Usage, scanned from the published issues.
    for asset_hash, usage in scan_issue_usage().items():
        incoming.setdefault(asset_hash, {}).update(usage)

    # 3. Backfill: every file already in the cache gets a record, even when all
    #    we can honestly say is "we don't know where this came from".
    if CACHE_DIR.exists():
        for path in sorted(CACHE_DIR.iterdir()):
            if not path.is_file() or path.name.startswith("manifest.json"):
                continue
            asset_hash = path.stem
            if len(asset_hash) != 12 or not re.fullmatch(r"[0-9a-f]{12}", asset_hash):
                continue
            entry = incoming.setdefault(asset_hash, {})
            if asset_hash not in before and "url" not in entry:
                entry["notes"] = PRE_MANIFEST_NOTE
                counts["backfilled"] += 1

    for asset_hash, values in incoming.items():
        existing = before.get(asset_hash)
        merged = merge_entry(existing, values)
        if existing is None:
            counts["new"] += 1
        elif merged != existing:
            counts["updated"] += 1
        else:
            counts["unchanged"] += 1
        manifest[asset_hash] = merged

    counts["total"] = len(manifest)
    # Entries on disk that this run had nothing new to say about — e.g. records
    # whose bytes are no longer in the cache. They are kept, never pruned.
    counts["carried"] = counts["total"] - (
        counts["new"] + counts["updated"] + counts["unchanged"]
    )
    if len(manifest) < len(before):
        sys.exit("FATAL: manifest merge would drop entries — refusing to write.")

    write_manifest(manifest_path, manifest)
    return manifest, counts


def unknown_provenance_count(manifest: dict) -> int:
    return sum(1 for entry in manifest.values() if entry.get("url", UNKNOWN) == UNKNOWN)


def unknown_licence_count(manifest: dict) -> int:
    return sum(
        1
        for entry in manifest.values()
        if (entry.get("licence") or {}).get("allows_derivatives") is None
    )


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
    ap.add_argument(
        "--manifest",
        default=str(MANIFEST_PATH),
        help="Path to the provenance manifest (default: assets/cached/manifest.json)",
    )
    ap.add_argument(
        "--manifest-only",
        action="store_true",
        help="Reconcile/backfill the manifest from the cache and the published "
             "issues. No network, no HTML rewriting.",
    )
    args = ap.parse_args()

    manifest_path = Path(args.manifest).resolve()

    if args.manifest_only:
        manifest, counts = update_manifest(manifest_path)
        print(f"Manifest: {manifest_path}")
        print(f"  entries: {counts['total']}  "
              f"(new {counts['new']}, updated {counts['updated']}, "
              f"unchanged {counts['unchanged']}, carried {counts['carried']})")
        print(f"  backfilled with unknown provenance this run: {counts['backfilled']}")
        print(f"  entries with no source URL: {unknown_provenance_count(manifest)}")
        print(f"  entries with unknown licence: {unknown_licence_count(manifest)}")
        print("  licence / shows / capture_year come from the research bundle "
              "(SPEC §3.2) — WP-1 contract, WP-5 enforcement, WP-9 wiring.")
        return

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
    fetched_at: dict[str, str] = {}
    resolved_urls: set[str] = set()

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
                resolved_urls.add(url)
                if status == "downloaded":
                    fetched_at[url] = (
                        datetime.now(timezone.utc)
                        .replace(microsecond=0)
                        .isoformat()
                        .replace("+00:00", "Z")
                    )
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

    # Provenance (SPEC §3.10). Written after the rewrite so the usage scan sees
    # the local refs this run just created.
    manifest, counts = update_manifest(
        manifest_path, fetched=fetched_at, known_urls=resolved_urls
    )

    # Report
    print()
    print(f"Downloaded: {stats['downloaded']}")
    print(f"Already cached: {stats['cached']}")
    print(f"Failed: {len(failures)}")
    print(f"Files modified: {modified_count}")
    print(
        f"Manifest: {manifest_path} — {counts['total']} entries "
        f"(new {counts['new']}, updated {counts['updated']}); "
        f"{unknown_provenance_count(manifest)} without a source URL, "
        f"{unknown_licence_count(manifest)} without a licence"
    )
    if failures:
        print("\nFailures:")
        for url, reason in failures:
            print(f"  {reason:40s}  {url}")

    sys.exit(0 if len(failures) == 0 else 1 if modified_count == 0 else 0)


if __name__ == "__main__":
    main()
