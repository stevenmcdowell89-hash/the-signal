#!/usr/bin/env python3
"""validate-issue.py — Post-stitch mandatory gate for The Signal issues.

Runs structural, asset, and integrity checks on a stitched HTML file.
Exits 0 on PASS, non-zero on any FAIL. WARN lines never fail the build.

USAGE
    python3 scripts/validate-issue.py <html-path> --format <format> [options]

OPTIONS
    --format <name>      Issue format: weekly | countdown | field-guide | rewind |
                         versus | season-review | deep-dive | shortlist | starter-kit |
                         lookahead | next. Underscores are accepted (field_guide → field-guide).
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
    "deep-dive", "guide", "shortlist", "starter-kit", "lookahead", "next",
}  # v8.31: +lookahead/+next (live slugs); -blueprint (retired v8.22).
   # v8.39 (S4): +guide (merged recommendation format). shortlist + starter-kit
   # are FOLDED into guide but kept here as recognised slugs for back-compat with
   # the archive. v8.39 (S2): lookahead is RETIRED/FOLDED into the weekly but its
   # slug stays recognised for the two archived drafts.
KNOWN_FORMATS = {"weekly"} | SPECIAL_FORMATS

# ─────────────────────────────────────────────────────────────────────────────
# Per-format hard length ceilings (v8.39, S6).
# A ship-quality FAIL: a special that overshoots its ceiling is "too long for a
# Sunday with coffee" (Field Guide came in ~15k, a retired Deep Dive ~24k). Caps
# are HARD maxima sitting well above each format's target band, tuned so every
# currently-shipping issue passes and only genuine runaways trip. Word count is
# measured on rendered body text (chrome included) — see check_length_band.
# Deep Dive is the flagship and gets the most generous cap; the light
# recommendation formats get the least. Formats absent from this map are not
# ceilinged (the check reports OK and moves on — never crashes).
# ─────────────────────────────────────────────────────────────────────────────
LENGTH_CEILINGS = {
    "deep-dive":     20000,  # flagship; 12,000+ where earned. 24k WWI DD trips it.
    "rewind":        15000,  # literary panorama, 8-12k target
    "season-review": 13000,  # 7-10k target
    "field-guide":   12000,  # 6-10k target; the ~15k over-long sample trips it
    "weekly":        11000,  # ~6-9k four-movement target
    "countdown":     11000,  # hype format
    "versus":        10000,  # 5-7k target
    "lookahead":      8000,  # retired/folded; kept for back-compat
    "guide":          7500,  # merged format, capped at the more generous beginner mode
    "starter-kit":    7500,  # back-compat alias for guide beginner mode
    "next":           7000,  # 3.5-5.5k target
    "shortlist":      6500,  # back-compat alias for guide category mode
}

# ─────────────────────────────────────────────────────────────────────────────
# Per-format hard length FLOORS (2026-07-13 quality-consistency handoff, A1).
# The first Transmission weekly shipped at ~3,960 words against a 6-9k target
# because no gate had a floor — the ceiling-only check passed a half-length
# issue silently. The floor sits at the target band's lower bound and mirrors
# the ceiling: below it is a hard ship FAIL, inside the same markup-contracts
# gate (no new gate; the ledger stays at three). WEEKLY ONLY for now — adding
# floors to other formats would retroactively red-flag legacy specials in the
# archive. Formats absent from this map have no floor (the check reports OK
# and moves on — never crashes). Measured the same way as the ceiling: rendered
# body text, chrome included — see check_length_band.
# ─────────────────────────────────────────────────────────────────────────────
LENGTH_FLOORS = {
    "weekly": 6000,  # ~6-9k four-movement target; 3,960-word first run trips it
}

# ─────────────────────────────────────────────────────────────────────────────
# Per-format minimum REAL-image counts (2026-07-13 handoff, A2).
# The first Transmission weekly shipped with ZERO <img> tags and every image
# gate passed trivially (they all only inspect images that already exist).
# This is the presence floor: real <img> tags in the rendered body. CSS
# placeholder plates (.plate-box glyph boxes with no <img>) do NOT count — the
# floor exists precisely because placeholder boxes were standing in for
# pictures. Markup-only, so it holds even offline / with --skip-image-urls.
# WEEKLY ONLY for now; formats absent from this map have no floor.
# ─────────────────────────────────────────────────────────────────────────────
MIN_IMAGES = {
    "weekly": 8,  # §5 A2 recommends 8-10; Issue #16 shipped 4 after hand-fixes
}

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
# Check: back-to-archive link ("Return to The Signal" main-menu button)
# ─────────────────────────────────────────────────────────────────────────────

BACK_LINK_MARKER = "<!-- the-signal:back -->"
BACK_LINK_ANCHOR_RE = re.compile(
    r'<a\b[^>]*class\s*=\s*"[^"]*\bsignal-back-to-archive\b[^"]*"[^>]*>',
    re.IGNORECASE,
)


def check_back_link(html: str, report: Report) -> None:
    """Every issue must carry the fixed "Return to The Signal" pill — the
    top-left button that takes the reader back to the archive index.

    History: the button was added to the stitch pipeline in v8.22.15 (injected
    after <body>), but nothing ever VERIFIED that injection landed — not the
    stitcher's own post-write checks, not this gate. So any issue assembled
    through a path that skipped or bypassed that single step shipped without the
    button (signal_next_2026-05-31, signal_weekly_2026-06-01 and
    signal_weekly_2026-06-07 all missed it). This gate closes the hole: the
    button is now a hard ship requirement, independent of HOW the HTML was
    assembled. To re-add it to a stitched issue, re-run scripts/stitch-issue.sh
    (idempotent — keys off the marker below) or inject
    assets/template-parts/back-link.html right after <body>.

    Asserts BOTH the injection marker and the rendered anchor: a half-present
    block (marker but no <a>, or an <a> with the wrong href) also fails, and a
    missing marker would make the stitcher re-inject and duplicate the pill.
    """
    has_marker = BACK_LINK_MARKER in html
    anchor = BACK_LINK_ANCHOR_RE.search(html)
    href_ok = bool(anchor and re.search(r'href\s*=\s*"\.\./?"', anchor.group(0)))

    problems = []
    if not has_marker:
        problems.append(f"injection marker '{BACK_LINK_MARKER}' absent")
    if anchor is None:
        problems.append("no <a class=\"signal-back-to-archive\"> anchor in DOM")
    elif not href_ok:
        problems.append(
            "back-link anchor present but href is not \"../\" (the archive index) — "
            f"tag is: {anchor.group(0)}"
        )

    if problems:
        report.fail(
            "back-link",
            "the 'Return to The Signal' archive button is missing or malformed: "
            + "; ".join(problems)
            + ". Re-run scripts/stitch-issue.sh (idempotent) or inject "
            "assets/template-parts/back-link.html right after <body>.",
        )
    else:
        report.ok("back-link", "'Return to The Signal' archive button present (marker + anchor → \"../\")")


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
# Check: non-holiday special component variety
#
# Parallels check_holiday_components: turns the soft "use N-M component types"
# guidance in formats.md into a hard gate so a special edition cannot ship as a
# plain page. Counts DISTINCT presentational component GROUPS in the rendered
# body (immune to the inlined CSS bundle via body_text_only).
# ─────────────────────────────────────────────────────────────────────────────

# group-name -> set of anchor classes. A group counts ONCE if ANY anchor is
# present. Anchors are DOM-only component markers — never utility or scaffold.
#
# Deliberately NOT listed (so they can never inflate the count):
#   • scaffold:   chapter*, cover*, foreword*, mast*, sp-footer*
#   • animation:  reveal, sp-rise*, sp-fade*, sp-parallax*, sp-band*
#   • modifiers:  is-left, is-wide, is-fullbleed, is-half, is-low, is-wildcard,
#                 is-throughline, is-special
#   • children:   wp-day, kd-medium, sc-bar, cal-row … (their PARENT group is
#                 the single source of truth, so a component counts exactly once)
SPECIAL_COMPONENT_GROUPS: dict[str, set[str]] = {
    # baseline editorial flair (available to every non-holiday special)
    "dropcap":       {"has-dropcap", "lede"},
    "pullquote":     {"pullquote"},
    "marginalia":    {"marginalia"},
    "bignum":        {"bignum", "bignum-row"},
    "source-strip":  {"source-strip"},
    "ornament":      {"sp-ornament"},
    "kicker":        {"sp-kicker"},
    "figure":        {"fig"},
    "image-quote":   {"image-quote"},
    "sp-number":     {"sp-number"},
    # cross-format rich containers
    "pick":          {"pick"},
    "pick-stats":    {"pick-stats"},
    "also-cards":    {"also-cards"},
    "meanwhile":     {"meanwhile-list"},
    # Deep Dive
    "argument":      {"argument"},
    "keep-digging":  {"keep-digging", "kd-item"},
    # Versus
    "vs-tape":       {"vs-tape"},
    "vs-pair":       {"vs-pair"},
    "vs-verdict":    {"vs-verdict"},
    "vs-scoreboard": {"vs-scoreboard"},
    # Rewind
    "year-band":     {"year-band"},
    "rewind-cards":  {"rewind-cards", "rewind-card"},
    "memory-test":   {"memory-test"},
    "throughline":   {"throughline-mark"},
    # Season Review
    "scorecards":    {"scorecards", "scorecard"},
    "rating":        {"rating", "rating-bar"},
    "scoreboard":    {"scoreboard"},
    "milestones":    {"milestones", "milestone"},
    # Shortlist
    "lens":          {"lens"},
    "tier-band":     {"tier-band"},
    "cheat-sheet":   {"cheat-sheet"},
    # Next
    "next-tier":     {"next-tier"},
    "on-ramp":       {"on-ramp"},
    "only-one":      {"only-one"},
    # Lookahead
    "calendar":      {"calendar"},
    "crunch-week":   {"crunch-week"},
    # Starter Kit
    "essentials":    {"essentials"},
    "week-plan":     {"week-plan"},
    "sk-mistake":    {"sk-mistake"},
    "sk-takeaway":   {"sk-takeaway"},
}

# Enforced floor = (formats.md guidance lower bound) − 1, honoring the old
# Starter-Kit variety bar (~10) while leaving a small margin against false fails.
SPECIAL_VARIETY_FLOOR: dict[str, int] = {
    "deep-dive":     9,   # guidance "10-14"
    "rewind":        9,   # guidance "10-14"
    "starter-kit":   9,   # guidance "10-14"
    "season-review": 7,   # guidance "8-12"
    "shortlist":     7,   # guidance "8-12"
    "versus":        7,   # guidance "8-12"
    "lookahead":     7,   # guidance "8-12"
    "next":          7,   # guidance "8-12"
}


def check_special_component_variety(html: str, fmt: str, report: Report) -> None:
    """Hard-fail a non-holiday special that deploys too few distinct
    presentational component types — the rule that stops a plain-page Deep Dive
    (or a thin Starter Kit) from passing every other gate.
    """
    floor = SPECIAL_VARIETY_FLOOR.get(fmt)
    if floor is None:
        return  # weekly / holiday / unknown — not gated here
    tokens = extract_class_tokens(body_text_only(html))
    present = sorted(
        group for group, anchors in SPECIAL_COMPONENT_GROUPS.items()
        if anchors & tokens
    )
    n = len(present)
    if n < floor:
        report.fail(
            "special-variety",
            f"{fmt} deploys only {n} distinct presentational component type(s); "
            f"floor is {floor}. Present: {', '.join(present) or '(none)'}. "
            f"A special edition must render with real visual variety — see the "
            f"'{fmt}' kit in references/spec/formats.md and the component list in "
            f"references/spec/specials.md. Add components from the format's flair "
            f"kit (e.g. .pick + .pick-stats, .bignum-row, .pullquote, .also-cards, "
            f"figure.image-quote), not just prose chapters.",
        )
    else:
        report.ok(
            "special-variety",
            f"{fmt}: {n} distinct component type(s) (floor {floor}) — "
            + ", ".join(present[:8]) + (f", +{n-8} more" if n > 8 else ""),
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


def check_image_urls(html: str, timeout: float, workers: int, report: Report, html_path: Path | None = None) -> None:
    urls = extract_image_urls(html)
    if not urls:
        report.warn("image-urls", "no <img src> or background-image URLs found")
        return

    # Partition local in-repo paths (e.g. /assets/cached/<hash>.jpg added by
    # the image-mirroring step) from remote URLs. Local paths are verified
    # by checking the file exists on disk relative to the repo root; HEAD
    # over HTTP would fail with "unknown url type" on a root-absolute path.
    repo_root = html_path.parent.parent if html_path else Path.cwd()
    local_urls = [u for u in urls if u.startswith("/")]
    remote_urls = [u for u in urls if not u.startswith("/")]

    results: list[tuple[str, int | str]] = []

    # Local: file-existence check.
    for u in local_urls:
        candidate = repo_root / u.lstrip("/")
        if candidate.is_file():
            results.append((u, 200))
        else:
            results.append((u, f"failed:local file missing ({candidate})"))

    # Remote: parallel HEAD checks as before.
    if remote_urls:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(head_check_one, u, timeout) for u in remote_urls]
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


def check_toc_anchors(html: str, report: Report) -> None:
    """Every <a class="toc-row" href="#X"> must point to a <section id="X">.

    The 24 May 2026 weekly rebuild shipped with three broken TOC links
    (#foreword / #pixel / #touchline) where the linked anchor didn't
    exist as a section id in the body — the orchestrator hand-wrote the
    navigator and picked arbitrary anchor names instead of using the
    scaffold canon (#tech, #football) or matching an existing id.

    Catches missing-anchor and orphaned-section problems.
    """
    toc_hrefs = re.findall(r'<a[^>]+class="toc-row[^"]*"[^>]+href="(#[^"]+)"', html)
    if not toc_hrefs:
        return  # No TOC in this issue — nothing to check
    section_ids = set(re.findall(r'<section[^>]+id="([^"]+)"', html))
    broken = [h for h in toc_hrefs if h.lstrip('#') not in section_ids]
    if broken:
        report.fail(
            "toc-anchors",
            "TOC links to anchors that don't exist as section ids: "
            + ", ".join(sorted(set(broken)))
            + f" — section ids in body: {sorted(section_ids)}",
        )
    else:
        report.ok("toc-anchors", f"all {len(toc_hrefs)} TOC links resolve to a section id")


def check_weekly_navigator(html: str, fmt: str, report: Report) -> None:
    """Weeklies must use the canonical .nav-card grid (04-navigator.html),
    NOT the .toc-row variant (04-navigator-toc.html, which is specials-only).

    The toc-row variant is documented in spec/global.md as "for longer, more
    literary issues — special editions, deep dives, field guides." Weeklies
    that opt into it get a book-frontmatter visual that doesn't match the
    rest of the issue.

    The May 17 and May 24 2026 weeklies both shipped with the TOC variant
    by mistake (the orchestrator hand-wrote the navigator); both were
    repaired to .nav-card in v8.22.10. This gate stops a recurrence.
    """
    if fmt != "weekly":
        return
    # Find the nav-section opener
    m = re.search(r'<section[^>]+class="([^"]*nav-section[^"]*)"', html)
    if not m:
        return  # No navigator; nothing to enforce
    nav_classes = m.group(1).split()
    if 'toc-style' in nav_classes:
        report.fail(
            "weekly-navigator",
            "weekly issue uses the TOC-style navigator variant "
            "(class='nav-section toc-style'). The TOC variant is for "
            "specials only — see references/spec/global.md § Navigator "
            "variants. Weeklies must use the canonical .nav-card grid from "
            "04-navigator.html (NOT 04-navigator-toc.html).",
        )
        return
    # Belt-and-braces: any .toc-row markup anywhere fails too
    if re.search(r'<a[^>]+class="[^"]*\btoc-row\b', html):
        report.fail(
            "weekly-navigator",
            "weekly issue contains .toc-row markup. That's the specials-only "
            "TOC-style navigator variant. Weeklies must use .nav-card grid.",
        )
        return
    report.ok("weekly-navigator", "uses canonical .nav-card navigator")


def check_toc_numerals(html: str, fmt: str, report: Report) -> None:
    """Standard weeklies use UPPERCASE Roman numerals starting at I in the TOC
    (e.g. I, II, III, IV, ...). The 24 May 2026 rebuild shipped with lowercase
    book-frontmatter numerals starting at iii (iii, iv, v, ...), which gave
    the weekly a "special edition / frontmatter" visual feel rather than the
    standard weekly look.

    This check runs for weekly format only — specials may legitimately use
    other conventions per their own spec.
    """
    if fmt != "weekly":
        return
    numerals = re.findall(r'<div class="toc-roman">([^<]+)</div>', html)
    if not numerals:
        return  # No toc-roman in this issue — older nav-card style, skip
    # Standard weekly convention: uppercase Roman, starting at I
    UPPER_ROMAN = {
        'I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV','XVI','XVII','XVIII','XIX','XX',
    }
    not_uppercase = [n for n in numerals if n.strip() not in UPPER_ROMAN]
    if not_uppercase:
        report.fail(
            "toc-numerals",
            f"weekly TOC uses non-standard numeral style. Found: {numerals[:5]}... "
            "Standard weekly convention is UPPERCASE Roman starting at I "
            "(I, II, III, IV, …). Lowercase or book-frontmatter starts (iii, iv, …) "
            "are a special-edition convention and shouldn't appear in weeklies.",
        )
    elif numerals[0].strip() != 'I':
        report.fail(
            "toc-numerals",
            f"weekly TOC numerals don't start at I — first numeral is {numerals[0]!r}. "
            "Standard weekly convention starts at I (no frontmatter prelim numbering).",
        )
    else:
        report.ok("toc-numerals", f"weekly TOC numerals are uppercase Roman starting at I ({len(numerals)} entries)")


COLOPHON_STATS_RE = re.compile(
    r'<ul\b[^>]*\bclass="[^"]*\bcolophon-stats\b[^"]*"[^>]*>(.*?)</ul>',
    re.IGNORECASE | re.DOTALL,
)
COLOPHON_SIGN_RE = re.compile(
    r'class="[^"]*\bcolophon-sign\b[^"]*"[^>]*>.*?Issue\s*#\s*(\d+)',
    re.IGNORECASE | re.DOTALL,
)
STRONG_INT_RE = re.compile(r'<strong\b[^>]*>\s*([\d,]+)\s*</strong>', re.IGNORECASE)


def check_issue_in_numbers_stats(html: str, report: Report) -> None:
    """Lightweight markup-safety assertion (v8.38, W-4): the Colophon's
    "Issue in Numbers" stats must be real and distinct — not all identical,
    and not just the issue number repeated.

    The recurring defect is a placeholder Colophon that shipped 13/13/13/13
    (every stat left at the issue number). This is mechanically detectable
    from the text alone, so it lives here in the markup gate rather than as a
    standalone script (per the gate-ledger: exactly three ship gates, no new
    scripts). Absent on special editions (they use Meanwhile, not a Colophon)
    — the check no-ops when there is no .colophon-stats block.
    """
    body = body_text_only(html)
    m = COLOPHON_STATS_RE.search(body)
    if not m:
        return  # no Issue-in-Numbers block (specials / older issues) — nothing to assert
    nums: list[int] = []
    for raw in STRONG_INT_RE.findall(m.group(1)):
        try:
            nums.append(int(raw.replace(",", "")))
        except ValueError:
            continue
    if len(nums) < 2:
        report.ok("issue-in-numbers", f"{len(nums)} numeric stat(s) — too few to compare")
        return

    sign = COLOPHON_SIGN_RE.search(body)
    issue_no = int(sign.group(1)) if sign else None

    if len(set(nums)) == 1:
        val = nums[0]
        if issue_no is not None and val == issue_no:
            report.fail(
                "issue-in-numbers",
                f"all {len(nums)} Issue-in-Numbers stats are the issue number ({val}) — "
                f"the 13/13/13/13 placeholder defect. Fill each figure with its real count "
                f"(word count, sections, links, images are all different numbers).",
            )
        else:
            report.fail(
                "issue-in-numbers",
                f"all {len(nums)} Issue-in-Numbers stats are identical ({val}). "
                f"These count different things (words, sections, links, images) and must differ.",
            )
    elif issue_no is not None and all(n == issue_no for n in nums):
        # Unreachable given the identical branch, but explicit for clarity.
        report.fail(
            "issue-in-numbers",
            f"every Issue-in-Numbers stat equals the issue number ({issue_no}).",
        )
    else:
        report.ok(
            "issue-in-numbers",
            f"{len(nums)} distinct-enough stats {nums}"
            + (f" (issue #{issue_no})" if issue_no is not None else ""),
        )


def check_weekly_structure(html: str, fmt: str, report: Report) -> None:
    """Weekly four-movement structural adherence (Transmission identity — the
    2026-07 rebuild). Weeklies must render as four labelled movements with The
    Desk collapsed into ONE nested department and Release Radar folded into
    Screen & Sound. Keys on the stable, invisible data-* hooks the Transmission
    templates emit (data-movement / data-role / data-desk-column / data-station
    / data-band) rather than display class names, so the gate is decoupled from
    the CSS. Single source of truth: references/format-skeletons/weekly.json §
    invariants. Weekly-only; each violation is a hard FAIL.

    Comments are stripped first so scaffold examples never trip the checks.
    """
    if fmt != "weekly":
        return

    clean = strip_html_comments(html)

    def data_vals(attr: str) -> list[str]:
        return [m.group(1).strip() for m in
                re.finditer(rf'\b{attr}\s*=\s*["\']([^"\']*)["\']', clean)]

    # 1. four movement bands -------------------------------------------------
    REQUIRED_MOVEMENTS = ["open", "long-read", "rounds", "close"]
    found_movements = set(data_vals("data-movement"))
    missing = [m for m in REQUIRED_MOVEMENTS if m not in found_movements]
    if missing:
        report.fail("weekly-structure/movement-bands",
                    "missing movement band(s): " + ", ".join(missing)
                    + f" (found: {sorted(found_movements) or 'none'})")
    else:
        report.ok("weekly-structure/movement-bands",
                  "all four movement bands present (open, long-read, rounds, close)")

    # 2. exactly one Long Read ----------------------------------------------
    roles = data_vals("data-role")
    n_lr = roles.count("long-read")
    if n_lr == 0:
        report.fail("weekly-structure/long-read", "no Long Read section (data-role='long-read')")
    elif n_lr > 1:
        report.fail("weekly-structure/long-read",
                    f"{n_lr} Long Read sections; exactly one allowed")
    else:
        report.ok("weekly-structure/long-read", "exactly one Long Read (data-role='long-read')")

    # 3. The Desk = one nested department -----------------------------------
    desk_failed = False
    n_desk = roles.count("desk")
    if n_desk == 0:
        report.fail("weekly-structure/desk-container",
                    "no Desk department (data-role='desk')")
        desk_failed = True
    elif n_desk > 1:
        report.fail("weekly-structure/desk-container",
                    f"{n_desk} Desk departments; exactly one allowed")
        desk_failed = True

    n_cols = len(re.findall(r'\bdata-desk-column\b', clean))
    if n_cols == 0:
        report.fail("weekly-structure/desk-container", "The Desk has no nested columns")
        desk_failed = True
    elif n_cols >= 3:
        report.fail("weekly-structure/desk-container",
                    f"The Desk runs {n_cols} columns; cap is 2 "
                    "(this is the 2026-07-12 'Desk exploded into 3 sections' failure)")
        desk_failed = True

    # a Desk column must never render as its OWN band or nav station
    band_ids = set(data_vals("data-band"))
    for name in ("session", "ledger", "itinerary", "toolkit"):
        if name in band_ids:
            report.fail("weekly-structure/desk-container",
                        f"Desk column '{name}' rendered as its own band (data-band='{name}'); "
                        "columns must nest inside the one Desk department")
            desk_failed = True

    if not desk_failed:
        report.ok("weekly-structure/desk-container",
                  f"The Desk is one department with {n_cols} nested column(s), "
                  "no exploded columns")

    # 4. Release Radar folded into Screen & Sound ---------------------------
    if "release_radar" in band_ids:
        report.fail("weekly-structure/release-radar-fold",
                    "Release Radar rendered as its own band (data-band='release_radar'); "
                    "it must be a rail inside Screen & Sound")
    elif "release-radar" not in roles:
        report.warn("weekly-structure/release-radar-fold",
                    "no Release Radar rail (data-role='release-radar') found inside Screen & Sound")
    else:
        # verify it sits inside the screen_sound band region (between the
        # screen_sound band marker and the next data-band marker)
        ss = re.search(r'data-band=["\']screen_sound["\']', clean)
        rr = re.search(r'data-role=["\']release-radar["\']', clean)
        inside = False
        if ss and rr and rr.start() > ss.start():
            nxt = re.search(r'data-band=["\'][^"\']+["\']', clean[ss.end():])
            boundary = ss.end() + nxt.start() if nxt else len(clean)
            inside = rr.start() < boundary
        if inside:
            report.ok("weekly-structure/release-radar-fold",
                      "Release Radar folded inside Screen & Sound")
        else:
            report.fail("weekly-structure/release-radar-fold",
                        "Release Radar rail is not inside the Screen & Sound band")

    # 5. navigator (tuner station) count ------------------------------------
    n_nav = len(re.findall(r'\bdata-station\b', clean))
    if n_nav > 13:
        report.fail("weekly-structure/nav-count",
                    f"{n_nav} navigator stations; target <=13")
    elif n_nav < 4:
        report.warn("weekly-structure/nav-count",
                    f"only {n_nav} navigator stations; a weekly usually surfaces 4-13")
    else:
        report.ok("weekly-structure/nav-count",
                  f"{n_nav} navigator stations (4-13)")

    # 6. Caught Up hard cap: <= 8 digest lines ------------------------------
    dig = re.search(r'<ol\b[^>]*\bclass="[^"]*\bdigest\b[^"]*"[^>]*>(.*?)</ol>',
                    clean, re.IGNORECASE | re.DOTALL)
    if dig:
        n_li = len(re.findall(r'<li\b', dig.group(1)))
        if n_li > 8:
            report.fail("weekly-structure/caught-up-cap",
                        f"Caught Up has {n_li} lines; the hard cap is 8")
        else:
            report.ok("weekly-structure/caught-up-cap", f"Caught Up within cap ({n_li}/8 lines)")

    # 7. Long Read carries >=1 real image ------------------------------------
    # (weekly.json § invariants: long_read_has_image, 2026-07-13 handoff A2.)
    # The anchor piece must be illustrated: >=1 real <img> inside the section
    # carrying data-role='long-read'. Empty .plate-box glyph placeholders do
    # not count. Region delimited the same way as the release-radar fold check:
    # from the data-role marker to the next data-band marker (or end of doc).
    if n_lr == 1:
        lr = re.search(r'data-role=["\']long-read["\']', clean)
        nxt = re.search(r'data-band=["\'][^"\']+["\']', clean[lr.end():])
        boundary = lr.end() + nxt.start() if nxt else len(clean)
        lr_region = clean[lr.end():boundary]
        n_lr_imgs = len(re.findall(r'<img\b', lr_region, re.IGNORECASE))
        if n_lr_imgs == 0:
            report.fail("weekly-structure/long-read-image",
                        "the Long Read carries no real <img> — the anchor piece "
                        "must be illustrated (>=1 captioned + credited image; an "
                        "empty .plate-box glyph placeholder does not count)")
        else:
            report.ok("weekly-structure/long-read-image",
                      f"Long Read carries {n_lr_imgs} real <img> tag(s)")
    # (n_lr != 1 already hard-failed in check 2 — nothing to measure here.)


# Special/holiday CSS + font markers that must NEVER appear in a weekly's
# injected assets — the weekly wears the constant warm Transmission identity,
# never the special/holiday costume. See weekly.json § visual_consistency and
# docs/weekly-visual-identity-groundup-2026-07.md Part 7.4.
WEEKLY_FORBIDDEN_STYLE_MARKERS = [
    "sp-chapter-gate", "sp-spread", "sp-marginalia", "hol-masthead", "hol-cover",
    "hol-half", "is-special", "data-special",
    "--touchline-bg", "--screen-bg", "--saga-bg", "--shelf-bg", "--listen-bg",
    "--channel-bg", "--eft-paper", "--bee-paper", "--sp-chapter-ff",
]
# Fonts legitimately loaded by a Transmission weekly. Any OTHER Google-Font
# family linked in the head is a holiday/special decorative font leaking in.
WEEKLY_ALLOWED_FONTS = {"Instrument Serif", "Newsreader", "JetBrains Mono"}


def check_weekly_visual_consistency(html: str, fmt: str, report: Report) -> None:
    """The weekly must wear the constant warm Transmission identity — never the
    special/holiday costume (the 'incoherent halfway' the redesign kills). Hard
    FAIL if a weekly loads special/holiday CSS or fonts, uses .sp-* body
    components, or ships the special dark hero instead of the weekly masthead.
    Weekly-only. See weekly.json § visual_consistency.
    """
    if fmt != "weekly":
        return

    # a. injected <style> must not carry special/holiday CSS
    styles = "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", html,
                                  re.DOTALL | re.IGNORECASE))
    leaked = sorted({mk for mk in WEEKLY_FORBIDDEN_STYLE_MARKERS if mk in styles})
    if leaked:
        report.fail("weekly-visual/no-special-css",
                    "weekly injected the special/holiday CSS bundle — found markers: "
                    + ", ".join(leaked)
                    + ". A weekly must load ONLY assets/css/weekly/*.css.")
    else:
        report.ok("weekly-visual/no-special-css",
                  "no special/holiday CSS markers in the injected stylesheet")

    # b. head fonts limited to the three Transmission faces
    head = html[:html.lower().find("</head>")] if "</head>" in html.lower() else html
    fam_found = set()
    for m in re.finditer(r"family=([^&:\"']+)", head):
        fam = m.group(1).replace("+", " ").strip()
        fam_found.add(fam)
    stray = sorted(f for f in fam_found if f not in WEEKLY_ALLOWED_FONTS)
    if stray:
        report.fail("weekly-visual/fonts",
                    "weekly links non-Transmission font families: " + ", ".join(stray)
                    + f". Allowed: {sorted(WEEKLY_ALLOWED_FONTS)}.")
    else:
        report.ok("weekly-visual/fonts",
                  f"fonts limited to the Transmission set ({sorted(fam_found) or 'none linked'})")

    # c. no .sp-* body components (mirror of the stitch gate; last line of defence)
    body = body_text_only(html)
    ALLOWED_SP = {"sp-chapter-beads", "sp-wipe-layer", "sp-word", "sp-fade"}
    sp = {}
    for m in re.finditer(r'class="[^"]*?\b(sp-[a-z][a-z0-9-]*)\b', body, re.IGNORECASE):
        if m.group(1) not in ALLOWED_SP:
            sp[m.group(1)] = sp.get(m.group(1), 0) + 1
    if sp:
        report.fail("weekly-visual/no-sp-components",
                    "weekly body uses special .sp-* components: "
                    + ", ".join(f"{t}×{n}" for t, n in sorted(sp.items())))
    else:
        report.ok("weekly-visual/no-sp-components", "no special .sp-* body components")

    # d. weekly masthead, not the special dark hero; and Transmission declared
    body_tag = find_real_body_tag(html)
    is_special_body = bool(body_tag and ("is-special" in body_tag[1] or "data-special" in body_tag[1]))
    has_masthead = bool(re.search(r'class="[^"]*\bmasthead\b', body))
    has_poster = bool(re.search(r'class="[^"]*\bcover-poster\b', body))
    if is_special_body or has_poster or not has_masthead:
        report.fail("weekly-visual/masthead",
                    "weekly does not use the constant Transmission masthead "
                    f"(is-special body={is_special_body}, cover-poster={has_poster}, "
                    f"masthead={has_masthead}). The dark special hero is reserved for specials.")
    else:
        report.ok("weekly-visual/masthead", "uses the constant Transmission masthead")

    # e. Transmission declared: .issue wrapper present
    if 'class="issue"' in body or "class='issue'" in body:
        report.ok("weekly-visual/transmission", "Transmission .issue wrapper present")
    else:
        report.fail("weekly-visual/transmission",
                    "missing the Transmission .issue page wrapper")


# Leaked scaffold / template tokens that must never render as body text
# (handoff 2026-07-12 §8b — the Rewind shipped 'Pick title' / '[Title of the
# pick]' / stray spec lines as visible content). Extends the placeholder check.
SCAFFOLD_LEAK_LITERALS = [
    "Pick title", "[Title of the pick]", "[Title]", "[Name of", "[Pick",
    "researcher to confirm", "TODO:", "TKTK", "[headline_hint]", "[why_it_matters]",
    "lorem ipsum",
]


def check_scaffold_leak(html: str, report: Report) -> None:
    """Catch unfilled scaffold/template tokens rendered as visible body text —
    the handoff §8b defect class (Pillar C scaffold detector). DOM-only, so
    example strings inside comments/style/script don't trip it."""
    body = body_text_only(html)
    low = body.lower()
    found = [lit for lit in SCAFFOLD_LEAK_LITERALS if lit.lower() in low]
    # generic bracketed template token: [Word ...] up to ~40 chars, but not a
    # citation like [1] or a real aside like [sic]. Require a leading capital
    # letter + a space or 'of'/'the' inside — the shape of a scaffold slot.
    for m in re.finditer(r'\[[A-Z][A-Za-z][^\]]{2,38}\]', body):
        tok = m.group(0)
        if tok in found:
            continue
        if re.search(r'\b(of|the|title|name|pick|date|insert|your)\b', tok, re.IGNORECASE):
            found.append(tok)
    if found:
        report.fail("scaffold-leak",
                    "unfilled scaffold/template token(s) rendered as body text: "
                    + ", ".join(sorted(set(found))[:8]))
    else:
        report.ok("scaffold-leak", "no leaked scaffold/template tokens in DOM")


# F-14 — pipeline scaffold tokens that must NEVER render as visible prose. These
# are the concrete leak classes the 2026-07-18 special-editions audit found
# shipped in the public archive, each with a hard-fail grep here (design-system
# unification spec §10 Phase 0, F-14):
#   • signal_rewind_2026-07-12  — masthead literally read "Issue #[N]".
#   • signal_deep-dive_2026-05-26 — 30+ "ch2-1"-style chapter IDs narrated in
#     prose, "viz_3" figure-caption tokens, and "research bundle" credits.
# Each pattern is matched against VISIBLE PROSE ONLY (comments/style/script and
# then all tags stripped), so legitimate scaffold anchors (id="ch2-1",
# href="#ch2-1") and documentation examples inside comments never trip it.
SCAFFOLD_TOKEN_PATTERNS = [
    (r'#?\[N\]',        'issue-number placeholder ("#[N]"/"[N]")'),
    (r'\bch\d+-\d+\b',  'chapter-ID reference in prose ("ch2-1")'),
    (r'\bviz_\d+',      'research-viz caption token ("viz_3")'),
    (r'research bundle', '"research bundle" pipeline phrase in prose'),
    # Tool-credit leak (review Part 5 §1 — countdown-wcq shipped this publicly).
    # Same scaffold/tool-leak family as F-14; unmistakable and zero legit use.
    (r'Created with [A-Za-z][A-Za-z ]*Computer', 'tooling credit leak ("Created with … Computer")'),
]


def check_scaffold_tokens(html: str, report: Report) -> None:
    """F-14 hard gate: leaked pipeline scaffold tokens rendered as reader copy.

    Distinct from check_scaffold_leak (unfilled [Title]-shape template slots):
    this catches the *production-leakage* classes — internal chapter IDs,
    viz/research-bundle credits, and the `#[N]` masthead placeholder — that
    reached readers in the archive because the publish gate did not police them.
    """
    text = re.sub(r"<[^>]+>", " ", body_text_only(html))  # visible prose only
    hits = []
    for pattern, label in SCAFFOLD_TOKEN_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            hits.append(f"{label} ×{len(matches)}")
    if hits:
        report.fail("scaffold-tokens",
                    "leaked pipeline scaffold token(s) in visible prose (F-14): "
                    + "; ".join(hits))
    else:
        report.ok("scaffold-tokens", "no leaked pipeline scaffold tokens in prose")


def check_length_band(html: str, fmt: str, report: Report) -> None:
    """Hard per-format word band: ceiling (v8.39, S6) + floor (2026-07-13, A1).

    'Sunday with coffee' means an issue a person actually finishes. A Field
    Guide that came in ~15k words and a retired Deep Dive at ~24k both broke
    that contract — the CEILING catches runaways. The first Transmission weekly
    then shipped at ~3,960 words against a 6-9k target because nothing pushed
    back UP — the FLOOR catches thinness. Both are hard ship FAILs folded into
    the existing markup/ship gate, not a new script. Formats with no ceiling
    (or no floor — currently everything but the weekly) skip that side with an
    OK (never a crash).
    """
    ceiling = LENGTH_CEILINGS.get(fmt)
    floor = LENGTH_FLOORS.get(fmt)
    if ceiling is None and floor is None:
        report.ok("length-band", f"no ceiling or floor defined for format '{fmt}' — skipped")
        return
    # Count words on rendered body text: strip comments/style/script, then tags.
    text = body_text_only(html)
    text = re.sub(r"<[^>]+>", " ", text)
    words = len(text.split())
    if ceiling is not None and words > ceiling:
        report.fail(
            "length-ceiling",
            f"{words:,} words exceeds the {fmt} ceiling of {ceiling:,} — "
            f"too long for a Sunday with coffee. Cut to the format's target band "
            f"(the ceiling sits well above target; overshooting it means bloat, "
            f"not depth). Deep Dive is the flagship and gets the most generous cap.",
        )
    elif ceiling is not None:
        report.ok("length-ceiling", f"{words:,} words within {fmt} ceiling {ceiling:,}")
    if floor is not None and words < floor:
        report.fail(
            "length-floor",
            f"{words:,} words is under the {fmt} floor of {floor:,} — "
            f"a half-length issue (the ~3,960-word first-run defect). The 6-9k "
            f"target must be allocated per band and written to, not yielded away. "
            f"Do not pad: go back to the planner for more material/research.",
        )
    elif floor is not None:
        report.ok("length-floor", f"{words:,} words clears the {fmt} floor {floor:,}")


def check_image_floor(html: str, fmt: str, report: Report) -> None:
    """Per-format minimum REAL-image count (2026-07-13 handoff, A2).

    Counts actual <img> tags in the rendered issue body. CSS placeholder plates
    (.plate-box glyph boxes with no <img>) do NOT count — an empty box is not a
    picture, and the zero-image first run passed every image gate precisely
    because they all only inspect images that already exist. Markup-only by
    design: no network, so it runs unconditionally — even offline and even
    under --skip-image-urls (that flag skips URL *reachability*, not image
    *presence*). Formats with no floor (currently everything but the weekly)
    report OK and are skipped. Below floor is a hard ship FAIL.
    """
    floor = MIN_IMAGES.get(fmt)
    if floor is None:
        report.ok("image-floor", f"no image floor defined for format '{fmt}' — skipped")
        return
    body = body_text_only(html)
    n_imgs = len(re.findall(r"<img\b", body, re.IGNORECASE))
    if n_imgs < floor:
        report.fail(
            "image-floor",
            f"{n_imgs} real <img> tag(s) in the body — below the {fmt} floor of "
            f"{floor}. CSS placeholder plates (.plate-box glyph boxes) do not "
            f"count: place real, captioned + credited images from the research "
            f"bundle's image_candidates (Long Read and every feature band lead "
            f"with one). A visually barren issue is not shippable.",
        )
    else:
        report.ok("image-floor", f"{n_imgs} real <img> tag(s) clears the {fmt} floor of {floor}")


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
    ap.add_argument("--format", default="", help="Issue format (e.g. field-guide). If omitted, auto-detected from <body data-special=\"...\">.")
    ap.add_argument("--multi-venue", action="store_true",
                    help="Assert multi-venue. If omitted, auto-detected from <body data-multi-venue=\"true\">.")
    ap.add_argument("--skip-image-urls", action="store_true")
    ap.add_argument("--image-timeout", type=float, default=5.0)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args(argv)

    path = Path(args.html_path)
    if not path.is_file():
        print(f"ERROR: file not found: {path}")
        return 2

    html = path.read_text(encoding="utf-8")

    # Auto-detect format + multi-venue from body attributes if not supplied
    # explicitly. Lets CI run with just the file path — no per-issue config.
    # Anchor to </head> first: the scaffold's AGENT INSTRUCTIONS comment in
    # 00-head-open.html contains a literal example <body> tag string
    # ('<body class="is-special" data-special="countdown"> (or field-guide).')
    # that a naive <body> regex hits before the real DOM body. Same trick the
    # stitcher uses (v8.13.4).
    fmt = normalize_format(args.format) if args.format else ""
    multi_venue = args.multi_venue
    head_end = re.search(r'</head\s*>', html, re.IGNORECASE)
    body_match = None
    if head_end:
        body_match = re.search(r'<body\b[^>]*>', html[head_end.end():], re.IGNORECASE)
    body_tag = body_match.group() if body_match else ""
    if not fmt:
        ds = re.search(r'data-special="([^"]+)"', body_tag)
        if ds:
            fmt = normalize_format(ds.group(1))
        else:
            # Fallback for weekly: no data-special on body
            fmt = "weekly"
        print(f"  (auto-detected format from <body>: {fmt})")
    if not multi_venue and 'data-multi-venue="true"' in body_tag:
        multi_venue = True
        print(f"  (auto-detected multi-venue from <body>)")

    if fmt not in KNOWN_FORMATS:
        print(f"ERROR: unknown format '{fmt}'. Known: {sorted(KNOWN_FORMATS)}")
        return 2

    print("=== validate-issue.py ===")
    print(f"File:   {path}")
    print(f"Format: {fmt}  Multi-venue: {multi_venue}  Strict: {args.strict}")
    print(f"Size:   {len(html):,} chars / {len(html.encode('utf-8')):,} bytes")
    print()

    report = Report(strict=args.strict)

    # Universal checks
    check_structure(html, report)
    check_back_link(html, report)
    check_placeholders(html, report)
    check_css_class_sanity(html, report)
    check_toc_anchors(html, report)
    check_weekly_navigator(html, fmt, report)
    check_toc_numerals(html, fmt, report)
    check_issue_in_numbers_stats(html, report)
    check_weekly_structure(html, fmt, report)
    check_weekly_visual_consistency(html, fmt, report)
    check_scaffold_leak(html, report)
    check_scaffold_tokens(html, report)
    check_length_band(html, fmt, report)
    # Image-presence floor: markup-only, network-free — runs unconditionally,
    # including under --skip-image-urls and in offline sandboxes (A2).
    check_image_floor(html, fmt, report)

    # Holiday-only checks
    if fmt in HOLIDAY_FORMATS:
        check_holiday_activation(html, fmt, multi_venue, report)
        check_holiday_components(html, report)
        if multi_venue:
            check_multi_venue(html, report)

    # Non-holiday special component-variety gate (parallel to the holiday
    # component gate; holiday formats keep their own check above).
    if fmt in SPECIAL_FORMATS and fmt not in HOLIDAY_FORMATS:
        check_special_component_variety(html, fmt, report)

    # Image URL static check — runs ALWAYS, even in restricted environments.
    # Catches page URLs used as image src regardless of egress policy.
    static_image_url_check(html, report)

    # Image URL HEAD checks (network-dependent)
    if args.skip_image_urls:
        report.warn("image-urls", "skipped per --skip-image-urls")
    else:
        check_image_urls(html, args.image_timeout, args.workers, report, path)

    return report.render()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
