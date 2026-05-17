#!/usr/bin/env python3
"""validate-issue.py — Post-stitch mandatory gate for The Signal issues.

Runs structural, asset, and integrity checks on a stitched HTML file.
Exits 0 on PASS, non-zero on any FAIL. WARN lines never fail the build.

USAGE
    python3 scripts/validate-issue.py <html-path> --format <format> [options]

OPTIONS
    --format <name>      Issue format: weekly | countdown | field-guide | rewind |
                         versus | season-review | deep-dive | blueprint | shortlist |
                         starter-kit. Underscores are accepted (field_guide → field-guide).
    --multi-venue        Assert body has data-multi-venue="true" and at least two
                         distinct data-venue values are present.
    --skip-image-urls    Skip HTTP HEAD checks on image URLs. Use only when offline
                         or when image attribution has been verified out-of-band.
    --image-timeout N    Per-URL timeout in seconds for HEAD requests. Default 5.
    --workers N          Parallel workers for URL checks. Default 16.
    --strict             Promote warnings to failures.

DESIGN
    The orchestrator (not a subagent) runs this and reads the exit code.
    Subagent self-reports of "gate passed" are not acceptable substitutes —
    the gate's verdict is its exit code, full stop.

EXIT CODES
    0   all checks passed
    1   structural / activation / asset failure
    2   bad invocation (missing file, unknown format, etc.)
"""

from __future__ import annotations

import argparse
import concurrent.futures
import re
import sys
import urllib.request
import urllib.error
import urllib.parse
from collections import Counter
from pathlib import Path

HOLIDAY_FORMATS = {"countdown", "field-guide"}
SPECIAL_FORMATS = {
    "countdown", "field-guide", "rewind", "versus", "season-review",
    "deep-dive", "blueprint", "shortlist", "starter-kit",
}
KNOWN_FORMATS = {"weekly"} | SPECIAL_FORMATS

# Literal placeholder strings that must never ship.
BANNED_PLACEHOLDERS = [
    'src="..."',
    'src="…"',
    'href="#TODO"',
    "[PLACEHOLDER]",
    "[TODO]",
    "[DATE RANGE]",
    "[YEAR]",
    "PASTE contents of",
    "See assets/script.js",
    "<!-- INJECT:CSS -->",
    "<!-- INJECT:JS -->",
]


# ─────────────────────────────────────────────────────────────────────────────
# Reporting helpers
# ─────────────────────────────────────────────────────────────────────────────

class Report:
    def __init__(self, strict: bool = False) -> None:
        self.strict = strict
        self.failures: list[tuple[str, str]] = []
        self.warnings: list[tuple[str, str]] = []
        self.passes:   list[tuple[str, str]] = []

    def fail(self, check: str, detail: str) -> None:
        self.failures.append((check, detail))

    def warn(self, check: str, detail: str) -> None:
        if self.strict:
            self.failures.append((check, detail))
        else:
            self.warnings.append((check, detail))

    def ok(self, check: str, detail: str) -> None:
        self.passes.append((check, detail))

    def render(self) -> int:
        for check, detail in self.passes:
            print(f"[PASS] {check}: {detail}")
        for check, detail in self.warnings:
            print(f"[WARN] {check}: {detail}")
        for check, detail in self.failures:
            print(f"[FAIL] {check}: {detail}")
        print()
        if self.failures:
            print(f"{len(self.failures)} failure(s) — issue NOT shippable.")
            return 1
        if self.warnings:
            print(f"{len(self.warnings)} warning(s). PASS.")
        else:
            print("All checks PASS.")
        return 0


# ─────────────────────────────────────────────────────────────────────────────
# Comment stripper — for finding the real <body> tag, not an example in a
# documentation comment.
# ─────────────────────────────────────────────────────────────────────────────

def strip_html_comments(html: str) -> str:
    return re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)


def body_text_only(html: str) -> str:
    """Strip inlined <style>, <script>, and HTML comments.

    Order matters: comments first. HTML comments in the scaffold legitimately
    contain example strings like '<style>' or '</style>' — if we stripped
    style blocks first, the regex would extend from the documentation example
    all the way to the real </style>, eating the entire body.
    """
    out = strip_html_comments(html)
    out = re.sub(r"<style\b[^>]*>.*?</style>", "", out, flags=re.DOTALL | re.IGNORECASE)
    out = re.sub(r"<script\b[^>]*>.*?</script>", "", out, flags=re.DOTALL | re.IGNORECASE)
    return out


def extract_class_tokens(body_html: str) -> set[str]:
    tokens: set[str] = set()
    for m in re.findall(r'class\s*=\s*"([^"]+)"', body_html, re.IGNORECASE):
        for cls in m.split():
            tokens.add(cls)
    for m in re.findall(r"class\s*=\s*'([^']+)'", body_html, re.IGNORECASE):
        for cls in m.split():
            tokens.add(cls)
    return tokens


def find_real_body_tag(html: str) -> tuple[int, str] | None:
    """Return (line_number, body_tag_text) of the body tag that follows </head>.

    Returns None if not found.
    """
    head_end = re.search(r"</head\s*>", html, re.IGNORECASE)
    if not head_end:
        return None
    tail = html[head_end.end():]
    body = re.search(r"<body\b[^>]*>", tail, re.IGNORECASE)
    if not body:
        return None
    abs_start = head_end.end() + body.start()
    line_no = html.count("\n", 0, abs_start) + 1
    return (line_no, body.group(0))


# ─────────────────────────────────────────────────────────────────────────────
# Check: placeholders
# ─────────────────────────────────────────────────────────────────────────────

def check_placeholders(html: str, report: Report) -> None:
    # Scan body DOM only — inlined CSS/JS/comments may legitimately contain
    # example strings like src="..." inside documentation comment blocks.
    body = body_text_only(html)
    found = []
    for needle in BANNED_PLACEHOLDERS:
        count = body.count(needle)
        if count > 0:
            found.append(f"'{needle}' x{count}")
    if found:
        report.fail("placeholders", "literal placeholders present in DOM: " + ", ".join(found))
    else:
        report.ok("placeholders", "no banned literal placeholders in DOM")


# ─────────────────────────────────────────────────────────────────────────────
# Check: structure (basic well-formedness)
# ─────────────────────────────────────────────────────────────────────────────

def check_structure(html: str, report: Report) -> None:
    if "<!DOCTYPE html>" not in html and "<!doctype html>" not in html.lower():
        report.fail("structure", "missing <!DOCTYPE html>")
        return
    if "</html>" not in html:
        report.fail("structure", "missing </html>")
        return
    if "</body>" not in html:
        report.fail("structure", "missing </body>")
        return
    lines = html.count("\n") + 1
    report.ok("structure", f"{lines:,} lines, doctype + </html> + </body> present")


# ─────────────────────────────────────────────────────────────────────────────
# Check: holiday activation
# ─────────────────────────────────────────────────────────────────────────────

def check_holiday_activation(
    html: str, fmt: str, multi_venue: bool, report: Report
) -> None:
    found = find_real_body_tag(html)
    if not found:
        report.fail("holiday-activation", "could not locate real <body> tag after </head>")
        return
    line_no, body_tag = found

    if 'class="is-special"' not in body_tag and 'class=\'is-special\'' not in body_tag:
        # also allow class="... is-special ..."
        m = re.search(r'class\s*=\s*"([^"]*)"', body_tag)
        cls = m.group(1).split() if m else []
        if "is-special" not in cls:
            report.fail(
                "holiday-activation",
                f"<body> at line {line_no} has no 'is-special' class — tier 11+ CSS will not activate",
            )
            return

    if f'data-special="{fmt}"' not in body_tag:
        report.fail(
            "holiday-activation",
            f"<body> at line {line_no} missing data-special=\"{fmt}\" — tag is: {body_tag}",
        )
        return

    if multi_venue:
        if 'data-multi-venue="true"' not in body_tag:
            report.fail(
                "holiday-activation",
                f"<body> at line {line_no} missing data-multi-venue=\"true\" (multi-venue issue)",
            )
            return

    report.ok("holiday-activation", f"<body> at line {line_no}: {body_tag}")


# ─────────────────────────────────────────────────────────────────────────────
# Check: required holiday components
# ─────────────────────────────────────────────────────────────────────────────

REQUIRED_HOLIDAY_TOKENS = [
    ("hol-masthead", "holiday masthead band"),
    ("hol-cover",    "holiday cover section"),
    ("hol-half",     "holiday half-section block"),
]


def check_holiday_components(html: str, report: Report) -> None:
    tokens = extract_class_tokens(body_text_only(html))
    for token, label in REQUIRED_HOLIDAY_TOKENS:
        # Match the exact token OR a BEM child (`hol-x__y`) OR a modifier
        # (`hol-x--variant`). A child class implies the parent element exists.
        matches = [
            c for c in tokens
            if c == token
            or c.startswith(token + "__")
            or c.startswith(token + "--")
        ]
        if not matches:
            report.fail("holiday-components", f"required '.{token}' element not found ({label})")
        else:
            report.ok(
                "holiday-components",
                f".{token}: {len(matches)} class variant(s) present ({', '.join(sorted(matches)[:3])}"
                + (f", +{len(matches)-3} more" if len(matches) > 3 else "") + ")",
            )


# ─────────────────────────────────────────────────────────────────────────────
# Check: multi-venue distinct data-venue values
# ─────────────────────────────────────────────────────────────────────────────

def check_multi_venue(html: str, report: Report) -> None:
    body_only = body_text_only(html)
    venues = set(re.findall(r'data-venue\s*=\s*"([^"]+)"', body_only))
    if len(venues) < 2:
        report.fail(
            "multi-venue",
            f"expected ≥2 distinct data-venue values, found {len(venues)}: {sorted(venues)}",
        )
    else:
        report.ok("multi-venue", f"{len(venues)} venues: {', '.join(sorted(venues))}")


# ─────────────────────────────────────────────────────────────────────────────
# Check: image URLs (HEAD)
# ─────────────────────────────────────────────────────────────────────────────

IMG_SRC_RE = re.compile(r'<img\b[^>]*?\bsrc\s*=\s*"([^"]+)"', re.IGNORECASE)
BG_URL_RE  = re.compile(r"background(?:-image)?\s*:\s*[^;]*?url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", re.IGNORECASE)


def extract_image_urls(html: str) -> list[str]:
    body_only = body_text_only(html)

    urls: list[str] = []
    urls.extend(IMG_SRC_RE.findall(body_only))
    # Inline background-image declarations live in style="..." attrs inside the
    # body. We scan body_only (not full html) so we don't HEAD-check CSS rules
    # in the inlined stylesheet — those are skill-controlled, not writer output.
    urls.extend(BG_URL_RE.findall(body_only))

    cleaned: list[str] = []
    seen: set[str] = set()
    for u in urls:
        u = u.strip()
        if not u or u.startswith("data:") or u.startswith("#"):
            continue
        if u in seen:
            continue
        seen.add(u)
        cleaned.append(u)
    return cleaned


BROWSER_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def head_check_one(url: str, timeout: float) -> tuple[str, int | str]:
    """Return (url, status_code_or_error_str). Treats 2xx and 3xx as OK.
    Additionally rejects 200 responses whose Content-Type starts with
    text/html — that's a page being served at a URL the writer treated as
    an image (e.g. background-image:url('https://www.efteling.com/.../polles-keuken')
    returns HTML 200 OK in any environment, and renders nothing as an image).
    """
    def _check_content_type(resp, label):
        ct = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        if ct.startswith("text/") or ct in ("application/xhtml+xml",):
            return (url, f"{label} {resp.status} but Content-Type={ct} (page URL used as image src)")
        return None
    req = urllib.request.Request(url, method="HEAD", headers={
        "User-Agent": BROWSER_UA,
        "Accept": "image/*,*/*;q=0.5",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            bad = _check_content_type(resp, "HEAD")
            if bad: return bad
            return (url, resp.status)
    except urllib.error.HTTPError as e:
        # Some servers reject HEAD with 4xx but serve GET fine — fall back.
        if e.code in (403, 405, 501):
            try:
                req_get = urllib.request.Request(url, method="GET", headers={
                    "User-Agent": BROWSER_UA,
                    "Accept": "image/*,*/*;q=0.5",
                    "Range": "bytes=0-0",
                })
                with urllib.request.urlopen(req_get, timeout=timeout) as resp:
                    bad = _check_content_type(resp, "GET")
                    if bad: return bad
                    return (url, resp.status)
            except urllib.error.HTTPError as e2:
                # Try to surface egress-policy hints (managed-runtime proxies
                # often inject explanatory headers).
                hint = ""
                deny = e2.headers.get("x-deny-reason") if e2.headers else None
                if deny:
                    hint = f" [proxy: {deny}]"
                return (url, f"HEAD {e.code} / GET {e2.code}{hint}")
            except Exception as inner:
                return (url, f"HEAD {e.code} / GET {inner.__class__.__name__}")
        # Surface deny-reason on the HEAD response too.
        deny = e.headers.get("x-deny-reason") if e.headers else None
        if deny:
            return (url, f"HEAD {e.code} [proxy: {deny}]")
        return (url, e.code)
    except urllib.error.URLError as e:
        return (url, f"URLError: {e.reason}")
    except Exception as e:
        return (url, f"{e.__class__.__name__}: {e}")


def static_image_url_check(html: str, report: Report) -> bool:
    """Static-only check: any background-image:url(...) or <img src='...'>
    whose path lacks an image extension AND is not a data: URI is suspicious.
    Returns True if any failures registered. Runs even when network is blocked
    so the page-URL-as-image bug is caught regardless of environment.
    """
    urls = extract_image_urls(html)
    IMG_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".svg",
                ".JPG", ".JPEG", ".PNG", ".WEBP", ".GIF", ".AVIF", ".SVG")
    suspicious = []
    for u in urls:
        if u.startswith("data:"):
            continue
        try:
            parsed = urllib.parse.urlparse(u)
            path = parsed.path
        except Exception:
            suspicious.append((u, "unparseable URL"))
            continue
        if not path.endswith(IMG_EXTS):
            suspicious.append((u, "no image extension — looks like a page URL"))
    if suspicious:
        lines = [f"{len(suspicious)} suspicious image URL(s) — no image extension (likely a page URL used as <img src> or background-image):"]
        for u, reason in suspicious:
            lines.append(f"    • {u}  →  {reason}")
        lines.append("    Fix: replace with the direct CDN image URL (e.g. .jpg/.png/.webp). If this is a legitimate")
        lines.append("    extension-less CDN, the issue can be shipped after manual verification.")
        report.fail("image-urls-static", "\n".join(lines))
        return True
    return False


def check_image_urls(html: str, timeout: float, workers: int, report: Report) -> None:
    urls = extract_image_urls(html)
    if not urls:
        report.warn("image-urls", "no <img src> or background-image URLs found")
        return

    results: list[tuple[str, int | str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(head_check_one, u, timeout) for u in urls]
        for fut in concurrent.futures.as_completed(futures):
            results.append(fut.result())

    ok_urls, bad_urls = [], []
    for u, status in results:
        if isinstance(status, int) and 200 <= status < 400:
            ok_urls.append((u, status))
        else:
            bad_urls.append((u, status))

    if bad_urls:
        # Detect environments with restricted outbound HTTPS — most managed
        # runtimes that gate egress will reject EVERY external host with the
        # same proxy-injected error. Report that as a degraded mode rather
        # than failing the issue.
        unique_errors = {str(s) for _, s in bad_urls}
        all_failed_same = (
            len(bad_urls) == len(urls)
            and len(unique_errors) == 1
            and ("host_not_allowed" in next(iter(unique_errors))
                 or "proxy:" in next(iter(unique_errors)))
        )
        if all_failed_same:
            report.warn(
                "image-urls",
                f"all {len(urls)} URL(s) blocked identically — current environment "
                f"appears to restrict outbound HTTPS. Sample: {next(iter(unique_errors))}. "
                "Re-run from an unrestricted environment (your local machine or CI) "
                "before publishing, OR pass --skip-image-urls after manual verification.",
            )
            return
        lines = [f"{len(bad_urls)} of {len(urls)} image URL(s) failed:"]
        for u, status in sorted(bad_urls, key=lambda x: str(x[0])):
            lines.append(f"    • {u}  →  {status}")
        report.fail("image-urls", "\n".join(lines))
    else:
        report.ok("image-urls", f"{len(ok_urls)}/{len(urls)} reachable (HEAD 2xx/3xx)")


# ─────────────────────────────────────────────────────────────────────────────
# Check: CSS-class sanity
# ─────────────────────────────────────────────────────────────────────────────

CLASS_ATTR_RE = re.compile(r'class\s*=\s*"([^"]+)"', re.IGNORECASE)


def check_css_class_sanity(html: str, report: Report) -> None:
    style_match = re.search(r"<style\b[^>]*>(.*?)</style>", html, re.DOTALL | re.IGNORECASE)
    if not style_match:
        report.warn("css-class-sanity", "no <style> block — skipping class check")
        return
    css_text = style_match.group(1)
    body_only = body_text_only(html)

    counter: Counter[str] = Counter()
    for m in CLASS_ATTR_RE.findall(body_only):
        for cls in m.split():
            counter[cls] += 1

    top = [c for c, _ in counter.most_common(30)]
    missing = [c for c in top if c not in css_text]
    if missing:
        report.warn(
            "css-class-sanity",
            f"top-30 classes not referenced in <style>: {', '.join(missing[:8])}"
            + (f" (+{len(missing) - 8} more)" if len(missing) > 8 else ""),
        )
    else:
        report.ok("css-class-sanity", "top-30 classes all referenced in <style>")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def normalize_format(fmt: str) -> str:
    return fmt.lower().replace("_", "-")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Post-stitch validation gate for The Signal.")
    ap.add_argument("html_path")
    ap.add_argument("--format", required=True, help="Issue format (e.g. field-guide)")
    ap.add_argument("--multi-venue", action="store_true")
    ap.add_argument("--skip-image-urls", action="store_true")
    ap.add_argument("--image-timeout", type=float, default=5.0)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args(argv)

    path = Path(args.html_path)
    if not path.is_file():
        print(f"ERROR: file not found: {path}")
        return 2

    fmt = normalize_format(args.format)
    if fmt not in KNOWN_FORMATS:
        print(f"ERROR: unknown format '{fmt}'. Known: {sorted(KNOWN_FORMATS)}")
        return 2

    html = path.read_text(encoding="utf-8")

    print("=== validate-issue.py ===")
    print(f"File:   {path}")
    print(f"Format: {fmt}  Multi-venue: {args.multi_venue}  Strict: {args.strict}")
    print(f"Size:   {len(html):,} chars / {len(html.encode('utf-8')):,} bytes")
    print()

    report = Report(strict=args.strict)

    # Universal checks
    check_structure(html, report)
    check_placeholders(html, report)
    check_css_class_sanity(html, report)

    # Holiday-only checks
    if fmt in HOLIDAY_FORMATS:
        check_holiday_activation(html, fmt, args.multi_venue, report)
        check_holiday_components(html, report)
        if args.multi_venue:
            check_multi_venue(html, report)

    # Image URL static check — runs ALWAYS, even in restricted environments.
    # Catches page URLs used as image src regardless of egress policy.
    static_image_url_check(html, report)

    # Image URL HEAD checks (network-dependent)
    if args.skip_image_urls:
        report.warn("image-urls", "skipped per --skip-image-urls")
    else:
        check_image_urls(html, args.image_timeout, args.workers, report)

    return report.render()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
