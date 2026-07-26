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
    --state PATH         state/signal-state.json. Read-only. Needed by the
                         open-loop (SPEC §3.7) and results-ledger breadth
                         (SPEC §3.11) checks. Auto-discovered from the repo root
                         when omitted.
    --run-date YYYY-MM-DD
                         The run/publish date, used to decide which open loops
                         have MATURED (SPEC §3.7) and which calendar events
                         concluded in-window (SPEC §3.11). Defaults to a date
                         parsed from the filename, else today (UTC).

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
import datetime
import json
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

# ─────────────────────────────────────────────────────────────────────────────
# Design-system-unification WP-0 (spec 2026-07-18, Part 4 item b).
#
# LAW-3 body-copy word FLOORS (Part 1, Law 3) — NEW-SYSTEM issues only.
# An issue is "new-system" when its real <html> or <body> tag carries a
# `data-mx` attribute, or the body carries `data-skin` (the furniture-core
# marker). Old-system archive issues are exempt: retro-failing the archive is
# not the point of the gate (same reasoning as LENGTH_FLOORS being weekly-only).
# Measured on VISIBLE PROSE (comments/style/script stripped, then tags) with
# <figcaption>/<caption> blocks removed; other chrome (nav, masthead, credits)
# is NOT excluded, so the measured count slightly OVERSTATES body copy — the
# floor is therefore mildly lenient, never spuriously strict.
# ─────────────────────────────────────────────────────────────────────────────
LAW3_WORD_FLOORS = {
    "weekly":        6000,
    "deep-dive":     8000,
    "season-review": 6500,
    "rewind":        7000,
    "versus":        4500,
    "guide":         3500,
    "shortlist":     3500,   # folded into guide; same floor for back-compat slugs
    "starter-kit":   3500,
    "next":          3000,
    "countdown":     4500,
    "field-guide":   6000,
}

# LAW-9 minimum DISTINCT named external voices (Part 1, Law 9) — new-system
# issues only. A "voice" is a quote-object (blockquote, or an element whose
# class contains 'quote') carrying a visible attribution that is not
# THE SIGNAL itself. Self-quotes ("— The Signal") are capped at 1 per issue.
LAW9_VOICE_FLOORS = {
    "weekly":        4,
    "deep-dive":     5,
    "season-review": 5,
    "rewind":        3,
    "countdown":     6,   # trip specials
    "field-guide":   6,   # trip specials
    "versus":        3,
    "guide":         3,
    "shortlist":     3,
    "starter-kit":   3,
    "next":          3,
}

# F-14 scaffold tokens that must never appear in VISIBLE PROSE. Checked after
# stripping comments/<style>/<script> and then all tags — so id="ch2-1"
# anchors, CSS selectors, and commented-out examples can never false-fire.
F14_SCAFFOLD_PATTERNS = [
    ("issue-number-placeholder", re.compile(r"(?:Issue\s*)?#\[N\]")),
    ("chapter-token-narrated",   re.compile(r"\bch\d+-\d+\b")),
    ("viz-slot-token",           re.compile(r"\bviz_\d\b")),
    ("research-bundle-phrase",   re.compile(r"\bresearch bundle\b", re.IGNORECASE)),
]

# Tool-credit leaks (F-14): a shipped page crediting the tool that generated it
# (the countdown-wcq footer shipped "Created with Perplexity Computer").
# Deliberately narrow — 'Created with' is case-sensitive and needs a tool name,
# so prose like "the tension it created with Washington" never fires.
F14_TOOL_CREDIT_PATTERNS = [
    re.compile(r"\b(?:Created|Made|Generated|Built)\s+with\s+(?:[A-Z][\w.]*\s+){0,3}Computer\b"),
    re.compile(r"\bPerplexity\s+Computer\b"),
    re.compile(r"\b(?:Created|Made|Generated|Built)\s+with\s+(?:Claude|ChatGPT|Gemini|Copilot|Anthropic|OpenAI)\b"),
]

# Raw CDN hostnames in visible copy (F-14): reader copy credits publications
# ("Photo: The Guardian"), never asset infrastructure ("cdn.libemaweb.com").
# Curated to CDN/asset hosts only — publisher domains cited as sources in
# legacy issues (goal.com, formula1.com, …) are deliberately NOT matched.
# HARD FAIL on new-system (data-mx) issues; WARN on legacy archive issues,
# which shipped credit lines like "content.presspage.com" before this gate.
F14_CDN_HOST_RE = re.compile(
    r"\b(?:[a-z0-9-]+\.)*("
    r"cloudfront\.net|akamaihd\.net|staticflickr\.com|b-cdn\.net|imgix\.net|"
    r"fastly\.net|steamstatic\.com|brightspotcdn\.com|arcpublishing\.com|"
    r"ctfassets\.net|nflxso\.net|squarespace-cdn\.com|storyblok\.com|"
    r"bynder\.com|googleusercontent\.com|tmdb\.org|srcdn\.com|cbrimages\.com|"
    r"colliderimages\.com|s-nbcnews\.com|tosshub\.com|libemaweb\.com|"
    r"presspage\.com|amazonaws\.com|cdn-si-edu\.com|gettyimages\.com|"
    r"shutterstock\.com"
    r")\b"
    r"|\bcdn\.[a-z0-9][a-z0-9.-]+\.[a-z]{2,}\b"
    r"|\b(?:media|static|assets|img|images)\.[a-z0-9-]+\.(?:com|net|org|co\.uk|nl|io)\b",
    re.IGNORECASE,
)

# F-14 internal STRATEGY VOCABULARY that must never reach reader copy.
# Same visible-prose scope. Each entry: (label, compiled regex).
# "skin" and "Phase N" are false-positive-prone in normal prose, so:
#   - skin only fires in system compounds (event/editorial/transmission skin);
#   - Phase 1–6 only fires within 120 chars of another strategy term
#     ("Phase 3 sessions/week" in a training issue must not fire);
#   - Phase 0 and WP-0..WP-9 always fire (no legitimate prose use).
F14_STRATEGY_PATTERNS = [
    ("furniture-first",  re.compile(r"\bfurniture[\s-]first\b", re.IGNORECASE)),
    ("motif-pack",       re.compile(r"\bmotif packs?\b", re.IGNORECASE)),
    ("design-system",    re.compile(r"\bdesign systems?\b", re.IGNORECASE)),
    ("skin-as-system",   re.compile(r"\b(?:event|editorial|transmission) skins?\b", re.IGNORECASE)),
    ("kit-as-system",    re.compile(
        r"\b(?:dossier|matchday|broadcast|scrapbook|scorecard|paddock|inventory|cinema|library|logbook) kits?\b",
        re.IGNORECASE)),
    ("wp-name",          re.compile(r"\bWP-\d\b")),
    ("phase-0",          re.compile(r"\bPhase 0\b")),
    ("ev-per-screen",    re.compile(r"\bev(?:ents)?/screen\b", re.IGNORECASE)),
    ("publish-gate",     re.compile(r"\bpublish[\s-]gate\b", re.IGNORECASE)),
    ("parity-gate",      re.compile(r"\bparity[\s-]gate\b", re.IGNORECASE)),
]
F14_PHASE_N_RE = re.compile(r"\bPhase [1-6]\b")
F14_STRATEGY_CONTEXT_RE = re.compile(
    r"furniture[\s-]first|motif pack|design system|publish[\s-]gate|parity[\s-]gate|\bWP-\d\b",
    re.IGNORECASE,
)

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

    def soft_warn(self, check: str, detail: str) -> None:
        """A warning that --strict must NOT promote to a failure.

        Exactly one class of finding needs this: an unrecognised `data-sport`
        token (SPEC §3.11 / data-contracts.md § Sport tokens). The 22-token list
        is closed-with-an-extension-path, so a genuinely new sport — the
        multi-sport-games long tail: lawn bowls, para events, judo — must never
        block a ship. "A breadth check that blocks breadth is self-defeating."
        Everything else uses warn() and stays strict-promotable.
        """
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


# New-system (data-mx) pages carry the Law-2 closed-list census vocabulary as
# data-mx-event markers (9 types total: figure, ephemera, ledger, statband,
# quote, plate, chart, marquee, cheatsheet). The legacy floors (7–9) are scaled
# against ~15 legacy component groups; against a 9-type vocabulary the
# equivalent floors are:
MX_VARIETY_FLOOR: dict[str, int] = {
    "deep-dive": 6, "rewind": 6, "starter-kit": 6, "guide": 6,
    "season-review": 5, "shortlist": 5, "versus": 5, "lookahead": 5, "next": 5,
    # data-mx holiday formats get variety here in lieu of the legacy hol- check:
    "countdown": 6, "field-guide": 6,
}


def check_mx_component_variety(html: str, fmt: str, report: Report) -> None:
    """special-variety for data-mx pages: count distinct data-mx-event types."""
    floor = MX_VARIETY_FLOOR.get(fmt)
    if floor is None:
        return  # weekly / unknown — not gated here
    types = set(re.findall(r'data-mx-event\s*=\s*"([a-z-]+)"', body_text_only(html)))
    n = len(types)
    if n < floor:
        report.fail(
            "special-variety",
            f"{fmt} (data-mx) deploys only {n} distinct data-mx-event type(s); "
            f"floor is {floor}. Present: {', '.join(sorted(types)) or '(none)'}. "
            f"A special must render with real visual variety — see "
            f"references/core-components.md for the component catalog.",
        )
    else:
        report.ok(
            "special-variety",
            f"{fmt} (data-mx): {n} distinct event type(s) (floor {floor}) — "
            + ", ".join(sorted(types)),
        )


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


# ─────────────────────────────────────────────────────────────────────────────
# Design-system-unification WP-0 checks (spec 2026-07-18, Part 4 item b):
# F-14 scaffold tokens + strategy vocabulary, Law-3 word floors, Law-9 voice
# minimums, F-16 external-src images.
# ─────────────────────────────────────────────────────────────────────────────

def visible_prose(html: str, drop_captions: bool = False) -> str:
    """Return the VISIBLE reader copy of an issue.

    Strip order matters: comments first, then <style>/<script> (via
    body_text_only — code and commented examples can never fire a prose
    check), optionally <figcaption>/<caption>, then ALL remaining tags —
    so attribute values (id="ch2-1", class names, data-*) never fire either.
    """
    out = body_text_only(html)
    if drop_captions:
        out = re.sub(r"<figcaption\b[^>]*>.*?</figcaption>", " ", out, flags=re.DOTALL | re.IGNORECASE)
        out = re.sub(r"<caption\b[^>]*>.*?</caption>", " ", out, flags=re.DOTALL | re.IGNORECASE)
    out = re.sub(r"<[^>]+>", " ", out)
    return re.sub(r"[ \t]+", " ", out)


def is_new_system(html: str) -> bool:
    """True when the issue is a NEW-SYSTEM (furniture-core) artifact:
    `data-mx` on the real <html> or <body> tag, or `data-skin` on <body>."""
    html_tag_m = re.search(r"<html\b[^>]*>", strip_html_comments(html), re.IGNORECASE)
    html_tag = html_tag_m.group(0) if html_tag_m else ""
    body = find_real_body_tag(html)
    body_tag = body[1] if body else ""
    return bool(
        re.search(r"\bdata-mx\b", html_tag)
        or re.search(r"\bdata-mx\b", body_tag)
        or re.search(r"\bdata-skin\s*=", body_tag)
    )


def resolve_law_format(html: str, fmt: str, path: Path) -> str:
    """Format slug used for Law-3/Law-9 floor lookup.

    Priority: body data-format attr > resolved --format/data-special fmt >
    filename slug. Filename matching handles fixtures named e.g.
    'attempt2-stub-flat-season-review.html' (longest slug wins so
    'season-review' beats nothing and 'field-guide' beats 'guide')."""
    body = find_real_body_tag(html)
    if body:
        m = re.search(r'data-format\s*=\s*"([^"]+)"', body[1])
        if m:
            return normalize_format(m.group(1))
    if fmt and fmt in (set(LAW3_WORD_FLOORS) | set(LAW9_VOICE_FLOORS)):
        return fmt
    name = path.name.lower().replace("_", "-")
    slugs = sorted(set(LAW3_WORD_FLOORS) | set(LAW9_VOICE_FLOORS), key=len, reverse=True)
    for slug in slugs:
        if slug in name:
            return slug
    return fmt


def _f14_findings(text: str, patterns) -> list[str]:
    found = []
    for label, pat in patterns:
        hits = pat.findall(text)
        if hits:
            sample = sorted({h if isinstance(h, str) else h[0] for h in hits})[:4]
            found.append(f"{label} x{len(hits)} (e.g. {', '.join(repr(s.strip()) for s in sample if s.strip()) or repr(hits[0])})")
    return found


def check_f14_scaffold_tokens(html: str, new_system: bool, report: Report) -> None:
    """F-14: scaffold/build tokens rendered as visible reader copy.

    Hard-fails on: '#[N]' / 'Issue #[N]' placeholders, chapter tokens
    (ch2-1) NARRATED in prose, viz-slot tokens (viz_3), the phrase
    'research bundle', and tool-credit leaks ('Created with … Computer').
    Raw CDN hostnames in visible copy hard-fail on new-system (data-mx)
    issues and WARN on legacy archive issues (which shipped credit lines
    like 'content.presspage.com' before this gate existed).
    All checks run on visible prose only — anchors like id="ch2-1", CSS,
    and commented examples cannot fire."""
    text = visible_prose(html)

    found = _f14_findings(text, F14_SCAFFOLD_PATTERNS)
    credit_hits = []
    for pat in F14_TOOL_CREDIT_PATTERNS:
        credit_hits.extend(m.group(0) for m in pat.finditer(text))
    if credit_hits:
        found.append("tool-credit-leak x%d (%s)" % (len(credit_hits), ", ".join(repr(h) for h in sorted(set(credit_hits))[:3])))

    if found:
        report.fail("f14-scaffold-tokens",
                    "scaffold/build tokens in VISIBLE reader copy: " + "; ".join(found)
                    + ". These are pipeline internals (F-14) — a reader must never see them.")
    else:
        report.ok("f14-scaffold-tokens", "no scaffold tokens or tool credits in visible prose")

    cdn_hits = sorted({m.group(0).lower() for m in F14_CDN_HOST_RE.finditer(text)})
    if cdn_hits:
        detail = ("raw CDN hostname(s) in visible copy: " + ", ".join(cdn_hits[:6])
                  + (f" (+{len(cdn_hits)-6} more)" if len(cdn_hits) > 6 else "")
                  + ". Reader copy credits publications/institutions, never asset infrastructure (F-14).")
        if new_system:
            report.fail("f14-cdn-hostnames", detail)
        else:
            report.warn("f14-cdn-hostnames", detail + " (legacy issue — warning only)")
    else:
        report.ok("f14-cdn-hostnames", "no raw CDN hostnames in visible prose")


def check_f14_strategy_vocab(html: str, report: Report) -> None:
    """F-14: internal strategy vocabulary in reader copy.

    'furniture-first', 'motif pack', 'design system', skin/kit names used as
    system terms, WP-0..WP-9, 'ev/screen', 'publish-gate', 'parity gate' etc.
    must never appear in what a reader sees. Calibrated for near-zero false
    positives: bare 'skin' never fires (only event/editorial/transmission
    compounds); 'Phase 1'..'Phase 6' only fires within 120 chars of another
    strategy term, so 'Phase 1 of the ceasefire plan' or a training plan's
    'Phase 3 sessions/week' pass; 'Phase 0' and 'WP-N' always fire."""
    text = visible_prose(html)
    found = _f14_findings(text, F14_STRATEGY_PATTERNS)

    for m in F14_PHASE_N_RE.finditer(text):
        window = text[max(0, m.start() - 120):m.end() + 120]
        if F14_STRATEGY_CONTEXT_RE.search(window):
            found.append(f"phase-name ({m.group(0)!r} adjacent to strategy vocabulary)")

    if found:
        report.fail("f14-strategy-vocab",
                    "internal strategy vocabulary in VISIBLE reader copy: " + "; ".join(found)
                    + ". System language (kits/skins/phases/gates) is for builders, never readers (F-14; "
                    "attempt #2 printed FURNITURE-FIRST in a cover meta).")
    else:
        report.ok("f14-strategy-vocab", "no internal strategy vocabulary in visible prose")


def check_law3_word_floor(html: str, fmt: str, path: Path, report: Report) -> None:
    """Law-3 body-copy word floor — NEW-SYSTEM (data-mx) issues only.

    'Density by shortness is a FAIL': attempt #2's 542-word Season Review
    stub 'passed' density (F-18). Words are counted on visible prose with
    figcaption/caption blocks excluded; remaining chrome (masthead, nav
    labels) is NOT excluded, so the count mildly overstates true body copy —
    the floor errs lenient, never spuriously strict."""
    law_fmt = resolve_law_format(html, fmt, path)
    floor = LAW3_WORD_FLOORS.get(law_fmt)
    if floor is None:
        report.ok("law3-word-floor", f"no Law-3 floor defined for format '{law_fmt}' — skipped")
        return
    words = len(visible_prose(html, drop_captions=True).split())
    if words < floor:
        report.fail(
            "law3-word-floor",
            f"{words:,} words of visible body copy is under the Law-3 {law_fmt} floor of {floor:,}. "
            f"An issue below its floor fails regardless of any other metric (F-18: the 542-word "
            f"Season Review stub). Do not pad — go back for more material.",
        )
    else:
        report.ok("law3-word-floor", f"{words:,} words clears the Law-3 {law_fmt} floor of {floor:,}")


# Quote-object detection for Law-9. A quote-object is a <blockquote> or an
# element whose class contains 'quote'. Attribution is read from <cite>, an
# attribution/source-classed child, or a trailing em-dash line.
_BLOCKQUOTE_RE = re.compile(r"<blockquote\b[^>]*>.*?</blockquote>", re.DOTALL | re.IGNORECASE)
_QUOTE_CLASS_OPEN_RE = re.compile(r"<(?:div|figure|aside|section|p)\b[^>]*class\s*=\s*\"[^\"]*quote[^\"]*\"[^>]*>", re.IGNORECASE)
_CITE_RE = re.compile(r"<cite\b[^>]*>(.*?)</cite>", re.DOTALL | re.IGNORECASE)
_ATTR_CLASS_RE = re.compile(
    r"<[a-z0-9]+\b[^>]*class\s*=\s*\"[^\"]*(?:attribution|quote-source|quote__source|source-line|speaker|byline|iq-credit)[^\"]*\"[^>]*>(.*?)</[a-z0-9]+>",
    re.DOTALL | re.IGNORECASE)
_DASH_ATTR_RE = re.compile(r"[—–]\s*([A-Z][^—–<\n]{1,80})")


def _quote_regions(body_html: str) -> list[str]:
    """Return non-overlapping quote-object regions (HTML fragments)."""
    spans: list[tuple[int, int]] = []
    for m in _BLOCKQUOTE_RE.finditer(body_html):
        spans.append((m.start(), m.end()))
    for m in _QUOTE_CLASS_OPEN_RE.finditer(body_html):
        # Regex cannot balance tags; take a bounded window after the opener.
        spans.append((m.start(), min(len(body_html), m.end() + 1200)))
    spans.sort()
    merged: list[tuple[int, int]] = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return [body_html[s:e] for s, e in merged]


def _extract_attribution(region: str) -> str | None:
    for rx in (_CITE_RE, _ATTR_CLASS_RE):
        m = rx.search(region)
        if m:
            txt = re.sub(r"<[^>]+>", " ", m.group(1))
            txt = re.sub(r"\s+", " ", txt).strip(" —–-“”\"'")
            if txt:
                return txt
    flat = re.sub(r"<[^>]+>", " ", region)
    flat = re.sub(r"\s+", " ", flat)
    dashes = _DASH_ATTR_RE.findall(flat)
    if dashes:
        return dashes[-1].strip(" —–-“”\"'.,")
    return None


def check_law9_voices(html: str, fmt: str, path: Path, report: Report) -> None:
    """Law-9 named-external-voice minimum — NEW-SYSTEM (data-mx) issues only.

    Counts DISTINCT named voices rendered as quote-objects (blockquote /
    class*='quote' elements) with a visible attribution that is not THE
    SIGNAL. Distinctness keys on the attribution's name segment (text before
    the first comma, casefolded). Self-quotes ('— The Signal') do not count
    and are capped at 1 per issue. HONESTY NOTE (printed in output): this is
    a markup-level count — it cannot judge whether a quote is verbatim or
    its speaker real; that stays a Part-6 human verification duty."""
    law_fmt = resolve_law_format(html, fmt, path)
    floor = LAW9_VOICE_FLOORS.get(law_fmt)
    if floor is None:
        report.ok("law9-voices", f"no Law-9 voice floor defined for format '{law_fmt}' — skipped")
        return
    body = body_text_only(html)
    regions = _quote_regions(body)
    voices: dict[str, str] = {}
    self_renderings = 0
    unattributed = 0
    for region in regions:
        attr = _extract_attribution(region)
        if not attr:
            unattributed += 1
            continue
        if "the signal" in attr.casefold():
            self_renderings += 1
            continue
        key = attr.split(",")[0].strip().casefold()
        if key:
            voices.setdefault(key, attr)
    n = len(voices)
    names = ", ".join(sorted(v for v in voices.values()))[:400]
    counted_note = (
        f"counted {n} distinct named external voice(s) from {len(regions)} quote-object(s) "
        f"[{unattributed} unattributed, {self_renderings} self-quote rendering(s)]"
        + (f": {names}" if names else "")
        + ". Markup-level count only — attribution text is trusted as written; verbatim accuracy is "
          "verified elsewhere."
    )
    if n < floor:
        report.fail(
            "law9-voices",
            f"{counted_note} — BELOW the Law-9 {law_fmt} floor of {floor}. The magazine has "
            f"arguments carried by named voices, not unsourced experiences (attempt #2 shipped zero).",
        )
    else:
        report.ok("law9-voices", f"{counted_note} — clears the Law-9 {law_fmt} floor of {floor}")
    if self_renderings > 1:
        report.fail(
            "law9-self-quotes",
            f"{self_renderings} '— THE SIGNAL' self-quote renderings; the cap is 1 per issue (Law 9).",
        )


def check_external_img_src(html: str, report: Report) -> None:
    """F-16 — NEW-SYSTEM (data-mx) issues only: every <img> src must be local
    (/assets/... or relative). The old system hotlinked and shipped 10/10 dead
    externals on a Next issue; the new system mirrors to assets/cached/ first.
    Legacy archive issues keep the reachability checks (image-urls) instead."""
    body = body_text_only(html)
    offenders = [u for u in IMG_SRC_RE.findall(body)
                 if u.strip().lower().startswith(("http://", "https://", "//"))]
    if offenders:
        uniq = sorted(set(offenders))
        lines = [f"{len(offenders)} external <img> src(s) — new-system issues must ship local images "
                 f"(/assets/... or relative), F-16:"]
        lines += [f"    • {u}" for u in uniq[:12]]
        if len(uniq) > 12:
            lines.append(f"    … +{len(uniq)-12} more")
        report.fail("f16-external-img-src", "\n".join(lines))
    else:
        n = len(IMG_SRC_RE.findall(body))
        report.ok("f16-external-img-src", f"all {n} <img> src(s) local or data:")


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


# ═════════════════════════════════════════════════════════════════════════════
# COVERAGE-REBUILD CHECKS  (WP-4 of docs/editorial-coverage-rebuild-SPEC-2026-07-26.md)
#
# These are the layer that makes a defective issue FAIL. They land INSIDE the two
# existing mechanical gates — gate 1 = image checks, gate 2 = markup contracts —
# because SPEC §0 forbids a fourth ship gate.
#
# What each check exists for (defect → structure → check):
#   A  an evergreen Long Read reading as breaking news
#        → data-vintage / .lr-vintage / date-free byline  (§3.4, §3.4a; criterion #2)
#        → data-lr-framing="feature" in The Letter        (§3.4)
#   B  a 2007 photograph illustrating a 2021 breakthrough
#        → caption vintage                                (§3.9; criterion #3)
#   D  Sunday-concluding events vanishing; one sport saturating the band
#        → data-resolves-loop per matured loop            (§3.7; criterion #6)
#        → results-ledger sport breadth                   (§3.11; criterion #7)
#   E  safe, boring, key-art imagery
#        → image shape budgets                            (§3.8; criterion #8)
#        → figure provenance presence                     (§3.4a note 6)
#
# The attribute VALUES are all fixed by SPEC §3.4 and §3.4a is the as-built
# reconciliation these implement against. Two rules from §3.4a matter here:
#   • never name or match an attribute `data-station*` — check_weekly_structure's
#     navigator tally is `\bdata-station\b` and `-` is a regex word boundary, so
#     `data-station-band` double-counted every station (§3.4a note 2). Nothing
#     below introduces a new attribute name at all; every name is WP-3's.
#   • `data-capture-year=""` is the LEGAL null rendering — empty string, not
#     "UNKNOWN", not absent. §3.9 applies only to a non-empty 4-digit value; a
#     value that is neither empty nor 4 digits FAILS, because the stitcher never
#     emits one, so it came from a writer (§3.4a note 3).
#
# All scanning is done on body_text_only() output. This is not cosmetic: the
# inlined <style> bundle contains `.mx-scorecard[data-table-kind="…"]` and
# `.lr-title .lr-vintage{`, so a naive whole-document scan reads CSS selectors as
# rendered markup.
# ═════════════════════════════════════════════════════════════════════════════

SKILL_ROOT = Path(__file__).resolve().parent.parent   # .claude/skills/the-signal

VINTAGE_VALUES = ("news", "evergreen")
COVER_LEADS_ON_VALUES = ("news", "long_read")
# SPEC §3.4 / §3.11: the legal `.mx-scorecard` shapes. A value outside the set
# renders as the unstyled base card. READ FROM weekly.json at runtime (see
# load_table_kinds) — the structure of record is the single source. This literal
# is the fallback only, and it carries `finance`, the sixth kind added by the
# 2026-07-26 §3.11 amendment: the first five were all sport, while The Desk
# already used .mx-scorecard for a financial card, so the enum could not name an
# existing legitimate use. A hardcoded enum here is what stopped WP-3b from
# stamping that card without taking the golden to exit 1.
TABLE_KINDS_FALLBACK = ("league", "medal", "gc", "leaderboard", "championship", "finance")
# SPEC §3.4 / §3.4a note 6 — the machine record every .plate-img must carry.
FIGURE_PROVENANCE_ATTRS = (
    "data-shows", "data-capture-year", "data-licence", "data-allows-derivatives",
)
# Canonical homes, with SPEC literals as fallbacks so there is no hard dependency
# on another WP's file (same discipline as stitch_weekly.py).
SHOWS_ENUM_FALLBACK = (
    "event_photo", "gameplay", "in_engine", "key_art", "product_shot", "portrait",
    "diagram", "map", "chart", "artefact", "document",
)                                                                    # SPEC §3.3
INFORMATION_SHAPES_FALLBACK = ("diagram", "map", "chart", "artefact")  # SPEC §3.8
NEVER_LEAD_FALLBACK = ("key_art", "product_shot", "portrait")          # SPEC §3.8
# SPEC §3.8 "Never-lead, resolved 2026-07-26": every never-lead shape is an
# issue-wide hard FAIL as a lead figure, with ONE conditional exception —
# product_shot may lead a band whose subject IS the product (a hardware launch or
# review). The exception is named here rather than the ban list, so if WP-6 adds a
# shape to never_lead_shapes it propagates as a hard fail (the plain reading of
# "never lead") instead of quietly needing a code change.
CONDITIONAL_LEAD_SHAPES = ("product_shot",)
SPORT_TOKENS_FALLBACK = (
    "football", "golf", "cricket", "cycling", "athletics", "motorsport", "rugby",
    "tennis", "boxing", "mma", "snooker", "darts", "gaelic_games", "swimming",
    "diving", "gymnastics", "netball", "hockey", "ice_hockey", "horse_racing",
    "basketball", "american_football",
)                            # data-contracts.md § The closed sport-token list (22)

MIN_DISTINCT_SHOWS = 3       # SPEC §3.8 / §3.14 min_distinct_shapes
YEAR_RE = re.compile(r"\b(1[5-9]\d{2}|20\d{2}|2100)\b")

# ─────────────────────────────────────────────────────────────────────────────
# §3.9 claim-year extraction — digits are not the only way prose dates a claim.
#
# WP-3b's finding, and it is the important one: THREE captions in the mx golden
# PASSED §3.9 while being wrong, because a first version of this check measured
# claim_max as the largest 4-DIGIT year in the band's prose. A band that writes
# "one hundred and forty-nine years after the first Championships" or "sixty-four
# years ago this week" contributes nothing, so the check reported "band makes no
# dated claim" for a 2009 photograph captioned as THIS WEEK's Wimbledon final —
# a live defect-B instance, invisible to the gate that exists for defect B.
#
# Three sources of a claim year are now read, and every failure quotes the
# evidence phrase so the reasoning is auditable rather than magic:
#   1. digits            — "In March 2021 a team at UCL…"
#   2. spelled-out forms — "nineteen sixty-five", "two thousand and four",
#                          "the nineteen-seventies", "the twentieth century"
#   3. this-week deixis  — "this week", "today", "on Monday": in a weekly, a
#                          present-tense claim IS a claim about the issue's own
#                          year, which is taken from --run-date. This is the class
#                          that produced the miss above.
# Anything recognisably a date expression but NOT resolvable to a year (a
# relative span, "the turn of the century", a bare decade) is reported as a
# WARNING that quotes what could not be parsed — see check_caption_vintage. A
# check that explains its own blind spot is worth more than one that pretends not
# to have one; silently passing and falsely failing are both worse.
# ─────────────────────────────────────────────────────────────────────────────
_W_UNIT = "one|two|three|four|five|six|seven|eight|nine"
_W_TEEN = "ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen"
_W_TENS = "twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety"
_W_TENS_PL = "twenties|thirties|forties|fifties|sixties|seventies|eighties|nineties"
# Only these can open a spelled year, which is what keeps "sixty-four years ago"
# and "one hundred and forty-nine years" out of the year parser entirely.
_W_CENTURY = "fifteen|sixteen|seventeen|eighteen|nineteen|twenty"
_WORD_VALUES = {
    **{w: i + 1 for i, w in enumerate(_W_UNIT.split("|"))},
    **{w: i + 10 for i, w in enumerate(_W_TEEN.split("|"))},
    **{w: (i + 2) * 10 for i, w in enumerate(_W_TENS.split("|"))},
    **{w: (i + 2) * 10 for i, w in enumerate(_W_TENS_PL.split("|"))},
}
# "fifteen hundred years", "nineteen hundred people" — a count, not a year.
_QUANTITY_NOUNS = (r"years?|months?|weeks?|days?|hours?|people|men|women|miles?|"
                   r"kilometres?|kilometers?|metres?|meters?|feet|foot|pounds?|"
                   r"dollars?|euros?|words?|copies|times|fragments?|gears?|teeth")
SPELLED_YEAR_RE = re.compile(
    rf"\b(?P<c>{_W_CENTURY})[\s‐-―-]+(?:"
    rf"hundred(?!\s+(?:and\s+[\w-]+\s+)?(?:{_QUANTITY_NOUNS})\b)"
    rf"(?:\s+and)?(?:[\s‐-―-]+(?P<hu>{_W_TENS}(?:[\s‐-―-]+(?:{_W_UNIT}))?"
    rf"|{_W_TEEN}|{_W_UNIT}))?"
    rf"|(?:oh|o)[\s‐-―-]+(?P<oh>{_W_UNIT})"
    rf"|(?P<pl>{_W_TENS_PL})"
    rf"|(?P<t>{_W_TENS})(?:[\s‐-―-]+(?P<tu>{_W_UNIT}))?"
    rf"|(?P<teen>{_W_TEEN})"
    rf")\b", re.IGNORECASE)
# "two thousand and four". A numeric tail is REQUIRED: "two thousand years in
# seawater" (issue #18's own Long Read) is a duration, not the year 2000.
THOUSAND_YEAR_RE = re.compile(
    rf"\btwo\s+thousand(?:\s+and)?[\s‐-―-]+"
    rf"(?P<n>(?:{_W_TENS})(?:[\s‐-―-]+(?:{_W_UNIT}))?|{_W_TEEN}|{_W_UNIT})\b",
    re.IGNORECASE)
_ORDINAL_CENTURIES = {
    "fifteenth": 15, "sixteenth": 16, "seventeenth": 17, "eighteenth": 18,
    "nineteenth": 19, "twentieth": 20, "twenty-first": 21, "twenty first": 21,
}
CENTURY_RE = re.compile(
    r"\b(fifteenth|sixteenth|seventeenth|eighteenth|nineteenth|twentieth|"
    r"twenty[\s-]first)\s+century\b", re.IGNORECASE)
# Present-week deixis. In a weekly these are claims about the issue's own week.
THIS_WEEK_RE = re.compile(
    r"\bthis (?:week|weekend|morning|afternoon|evening|month)\b"
    r"|\b(?:today|tonight|yesterday|tomorrow)\b"
    r"|\blast night\b|\bas this is read\b|\bthis year\b", re.IGNORECASE)
WEEKDAY_RE = re.compile(
    r"\b(?:on|last|this|by|since|from)\s+"
    r"(Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)\b", re.IGNORECASE)
# Recognisably a date expression, NOT resolvable to a year here.
UNRESOLVED_DATE_RES = (
    ("turn-of-century", re.compile(r"\bturn of the (?:century|millennium)\b", re.IGNORECASE)),
    ("relative-span", re.compile(
        rf"\b(?:\d{{1,4}}|{_W_UNIT}|{_W_TEEN}|(?:{_W_TENS})(?:[\s-]+(?:{_W_UNIT}))?"
        rf"|(?:{_W_UNIT})\s+hundred(?:\s+and\s+(?:(?:{_W_TENS})(?:[\s-]+(?:{_W_UNIT}))?"
        rf"|{_W_TEEN}|{_W_UNIT}))?)"
        rf"[\s-]+(?:years?|decades?|centuries|century)\s+"
        rf"(?:ago|after|since|before|earlier|later|prior)\b", re.IGNORECASE)),
    ("bare-decade", re.compile(rf"\bthe\s+(?:{_W_TENS_PL})\b", re.IGNORECASE)),
    ("vague-span", re.compile(
        r"\b(?:half\s+)?a\s+(?:century|decade|millennium)\s+(?:ago|earlier|later|before)\b"
        r"|\bdecades\s+(?:ago|earlier|later)\b", re.IGNORECASE)),
)


def _spelled_year(m: re.Match) -> int | None:
    base = _WORD_VALUES[m.group("c").lower()] * 100
    if m.group("oh"):
        return base + _WORD_VALUES[m.group("oh").lower()]
    if m.group("pl"):
        return base + _WORD_VALUES[m.group("pl").lower()]          # decade START
    if m.group("t"):                          # "nineteen sixty-five" → 1900+60+5
        total = _WORD_VALUES[m.group("t").lower()]
        if m.group("tu"):
            total += _WORD_VALUES[m.group("tu").lower()]
        return base + total
    for grp in ("hu", "teen"):
        val = m.group(grp)
        if val:
            parts = re.split(r"[\s‐-―-]+", val.strip().lower())
            return base + sum(_WORD_VALUES.get(p, 0) for p in parts)
    return base                                                     # "nineteen hundred"


def band_claim_years(prose: str, issue_year: int | None) -> tuple[list[tuple[int, str]], list[str]]:
    """(claim years with the evidence that produced each, unresolved date phrases).

    Years are clamped to 1500–2100, the same window §3.9 gives the digit form.
    """
    claims: list[tuple[int, str]] = []
    for m in YEAR_RE.finditer(prose):
        claims.append((int(m.group(1)), f"digits {m.group(1)!r}"))
    for m in SPELLED_YEAR_RE.finditer(prose):
        y = _spelled_year(m)
        if y and 1500 <= y <= 2100:
            note = "spelled decade (start of decade)" if m.group("pl") else "spelled"
            claims.append((y, f"{note} {m.group(0)!r} → {y}"))
    for m in THOUSAND_YEAR_RE.finditer(prose):
        parts = re.split(r"[\s‐-―-]+", m.group("n").strip().lower())
        y = 2000 + sum(_WORD_VALUES.get(p, 0) for p in parts)
        if 1500 <= y <= 2100:
            claims.append((y, f"spelled {m.group(0)!r} → {y}"))
    for m in CENTURY_RE.finditer(prose):
        key = re.sub(r"\s+", " ", m.group(1).lower()).replace(" ", "-")
        n = _ORDINAL_CENTURIES.get(key) or _ORDINAL_CENTURIES.get(m.group(1).lower())
        if n:
            claims.append(((n - 1) * 100, f"century {m.group(0)!r} → {(n - 1) * 100} (century start)"))
    if issue_year is not None:
        m = THIS_WEEK_RE.search(prose)
        if m:
            claims.append((issue_year, f"this-week deixis {m.group(0)!r} → the issue's year {issue_year}"))
        else:
            for wm in WEEKDAY_RE.finditer(prose):
                # "on Monday 15 July 1965" is a historical date, not this week.
                if YEAR_RE.search(prose[wm.end():wm.end() + 30]):
                    continue
                claims.append((issue_year,
                               f"this-week deixis {wm.group(0)!r} → the issue's year {issue_year}"))
                break
    unresolved: list[str] = []
    for label, rx in UNRESOLVED_DATE_RES:
        for m in rx.finditer(prose):
            phrase = re.sub(r"\s+", " ", m.group(0)).strip()
            entry = f"{label}: {phrase!r}"
            if entry not in unresolved:
                unresolved.append(entry)
    return claims, unresolved
FOUR_DIGIT_RE = re.compile(r"^\d{4}$")
# WP-3 normalises the Long Read byline to `· DD MON YYYY`; accept long month
# names and unpadded days too, so this reads a writer's date as well as a
# stitched one. ISO dates count as a date as well.
BYLINE_DATE_RE = re.compile(
    r"\b\d{1,2}\s+(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Za-z]*\.?\s+\d{4}\b"
    r"|\b\d{4}-\d{2}-\d{2}\b",
    re.IGNORECASE,
)
# SPEC §3.8: "any figure captioned as a concluded result must be event_photo".
# Deliberately narrow — DECIDED outcomes only, so a preview caption ("on his way
# to pole … the race is still hours from its first corner") cannot fire. Bare
# "championship"/"title" are excluded on purpose: they appear in event NAMES.
RESULT_CAPTION_RES = (
    re.compile(r"\b(?:won|wins|beat|beats|beaten|defeat(?:ed|s)|"
               r"victory|clinch(?:ed|es)|seal(?:ed|s)|retain(?:ed|s)|"
               r"crowned|winner|runner-up|champion(?:s)?\b(?=[^A-Za-z]*$))\b",
               re.IGNORECASE),
    re.compile(r"\b\d{1,3}\s*[-–]\s*\d{1,3}\b"),                       # a scoreline
    re.compile(r"\bby \d+ (?:shots?|strokes?|seconds?|points?|lengths?|laps?)\b",
               re.IGNORECASE),
)

BAND_MARKER_RE = re.compile(r'\bdata-band\s*=\s*["\']([^"\']+)["\']')
# The contract renders .plate-img as a <div>, but the tag is captured rather than
# hardcoded: a writer who reaches for <figure class="plate-img"> must not slip
# past the provenance and shape budgets on a technicality.
FIGURE_OPEN_RE = re.compile(
    r'<([a-z0-9]+)\b[^>]*\bclass\s*=\s*"[^"]*\bplate-img\b[^"]*"[^>]*>', re.IGNORECASE)
ATTR_PAIR_RE = re.compile(r'([A-Za-z][A-Za-z0-9-]*)\s*=\s*"([^"]*)"')
_CLASS_OPEN_TMPL = r'<([a-z0-9]+)\b[^>]*\bclass\s*=\s*"[^"]*\b{cls}\b[^"]*"[^>]*>'


# ─── parsing helpers ─────────────────────────────────────────────────────────

def _element_html(html: str, start: int, tag: str) -> str:
    """Return the full HTML of the element whose opening tag begins at `start`.

    Nesting-aware (counts same-tag opens), so a .plate-img containing nested
    <div>s is not truncated at the first </div>. Regex cannot balance tags; this
    small scanner can, and every element it is used on (div/span) is never
    self-closing.
    """
    gt = html.find(">", start)
    if gt == -1:
        return html[start:]
    open_re = re.compile(rf"<{tag}\b", re.IGNORECASE)
    close_re = re.compile(rf"</{tag}\s*>", re.IGNORECASE)
    pos, depth = gt + 1, 1
    while depth:
        c = close_re.search(html, pos)
        if not c:
            return html[start:]           # unbalanced markup — take the tail
        o = open_re.search(html, pos)
        if o and o.start() < c.start():
            depth += 1
            pos = o.end()
        else:
            depth -= 1
            pos = c.end()
    return html[start:pos]


def _first_class_element(html: str, cls: str) -> str | None:
    """HTML of the first element carrying class `cls`, or None."""
    m = re.search(_CLASS_OPEN_TMPL.format(cls=re.escape(cls)), html, re.IGNORECASE)
    if not m:
        return None
    return _element_html(html, m.start(), m.group(1))


def _strip_class_blocks(html: str, cls: str) -> str:
    """Remove every element carrying class `cls`, contents included."""
    rx = re.compile(_CLASS_OPEN_TMPL.format(cls=re.escape(cls)), re.IGNORECASE)
    out = html
    while True:
        m = rx.search(out)
        if not m:
            return out
        frag = _element_html(out, m.start(), m.group(1))
        out = out[:m.start()] + " " + out[m.start() + len(frag):]


def _visible(html: str) -> str:
    """Tags out, whitespace collapsed — the text a reader actually sees."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _tag_attrs(tag_text: str) -> dict[str, str]:
    return {k.lower(): v for k, v in ATTR_PAIR_RE.findall(tag_text)}


def band_regions(body: str) -> list[tuple[str, int, int]]:
    """(band_id, start, end) for every data-band marker, in document order.

    A band's region runs from its marker to the next band marker. That is the
    same region model check_weekly_structure already uses for the release-radar
    fold, and it is the right one here: in a rendered weekly the `.band` div
    often closes right after the band-head, with the band's content following in
    sibling <section>s (see the Colophon in issue #18), so "inside the .band
    element" would find almost nothing.
    """
    marks = list(BAND_MARKER_RE.finditer(body))
    out: list[tuple[str, int, int]] = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        out.append((m.group(1), m.start(), end))
    return out


def _band_at(regions: list[tuple[str, int, int]], idx: int) -> tuple[str, int, int] | None:
    for band, start, end in regions:
        if start <= idx < end:
            return (band, start, end)
    return None


def collect_figures(body: str) -> list[dict]:
    """Every .plate-img in the rendered body, parsed into a record.

    Keys: band, is_lead, label, src, hash, attrs, cap_visible (the caption's
    VISIBLE sentence — `.plate-cap .txt` with the nested `.credit` span removed,
    which is exactly the scope SPEC §3.9 names), has_cap.
    """
    regions = band_regions(body)
    figs: list[dict] = []
    for i, m in enumerate(FIGURE_OPEN_RE.finditer(body)):
        tag = m.group(0)
        el = _element_html(body, m.start(), "div")
        attrs = _tag_attrs(tag)
        classes = (attrs.get("class") or "").split()
        src_m = re.search(r'<img\b[^>]*\bsrc\s*=\s*"([^"]*)"', el, re.IGNORECASE)
        src = src_m.group(1) if src_m else ""
        cap = _first_class_element(el, "plate-cap")
        label, cap_visible = "", None
        if cap:
            fig_span = _first_class_element(cap, "fig")
            if fig_span:
                label = _visible(fig_span)
            txt = _first_class_element(cap, "txt")
            if txt:
                # The credit span is NESTED INSIDE .txt in the shipped markup, so
                # excluding it means removing a child, not skipping a sibling.
                cap_visible = _visible(_strip_class_blocks(txt, "credit"))
            else:
                cap_visible = _visible(_strip_class_blocks(cap, "credit"))
        band = _band_at(regions, m.start())
        figs.append({
            "index": i + 1,
            "label": label or f"figure #{i + 1}",
            "src": src,
            "hash": Path(urllib.parse.urlparse(src).path).stem if src else "",
            "band": band[0] if band else "(no band)",
            "band_span": (band[1], band[2]) if band else (0, len(body)),
            "is_lead": "lead" in classes,
            "attrs": attrs,
            "has_cap": cap is not None,
            "cap_visible": cap_visible,
        })
    return figs


def _fig_id(fig: dict) -> str:
    return f"{fig['label']} [{fig['band']}{'/lead' if fig['is_lead'] else ''}, {fig['src'] or 'no <img>'}]"


# Date-bearing FURNITURE inside a band: the issue's own datestamps, not claims the
# band makes about its subject. SPEC §3.9 keys on the band's PROSE, so these come
# out before claim_max is measured. It matters: the Long Read's byline reads
# "· 26 JUL 2026", and counting that as a claim would set claim_max to the issue
# year in every band of every issue — turning "the prose claims 2021" into "the
# issue was published in 2026" and making the failure message undiagnostic.
# Ledger DATE CELLS are deliberately NOT excluded: "1901 Recovered / 2005 Scanned
# / 2021 Modelled" are claims of record, which is exactly what the rule reads.
BAND_FURNITURE_CLASSES = ("byline", "sigline", "dataline", "stamp", "lr-vintage",
                          "colophon", "runtime")


def band_prose(body: str, span: tuple[int, int]) -> str:
    """Visible prose of a band region, figure captions EXCLUDED (SPEC §3.9).

    Excludes `.plate-cap` blocks, <figcaption> and <caption> — a caption is not a
    claim the band is making, and including one would let a caption's own credit
    line ("… 2007 · CC BY 2.5") satisfy the very rule it is the subject of — and
    the dateline furniture above.
    """
    region = body[span[0]:span[1]]
    region = _strip_class_blocks(region, "plate-cap")
    for cls in BAND_FURNITURE_CLASSES:
        region = _strip_class_blocks(region, cls)
    region = re.sub(r"<figcaption\b[^>]*>.*?</figcaption>", " ", region,
                    flags=re.DOTALL | re.IGNORECASE)
    region = re.sub(r"<caption\b[^>]*>.*?</caption>", " ", region,
                    flags=re.DOTALL | re.IGNORECASE)
    return _visible(region)


# ─── canonical vocabularies, loaded from their owners' files ──────────────────

def load_shows_vocab() -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], str]:
    """(shows enum, information-figure shapes, never-lead shapes, provenance note).

    All three lists are READ FROM WP-6's references/image-source-types.json §
    shows at runtime, never hardcoded — that file's `_derived_lists_doc` names
    machine-vs-prose drift as a live failure mode (it already happened once:
    `never_lead_shapes` omitted `portrait` while the rank-5 prose said "key art /
    product shot / posed portrait — last resort, never a lead"). Reading the lists
    means a doctrine change propagates instead of silently diverging from this
    check. The SPEC literals remain only as a fallback, so there is no hard
    dependency on another WP's file.
    """
    path = SKILL_ROOT / "references" / "image-source-types.json"
    try:
        shows = json.loads(path.read_text(encoding="utf-8"))["shows"]
        enum = tuple(shows["values"].keys())
        info = tuple(shows.get("information_figure_shapes") or INFORMATION_SHAPES_FALLBACK)
        never = tuple(shows.get("never_lead_shapes") or NEVER_LEAD_FALLBACK)
        if len(enum) >= 5:
            return (enum, info, never,
                    f"shows vocab from {path.name}: {len(enum)} values, "
                    f"information={list(info)}, never_lead={list(never)}")
    except Exception:
        pass
    return (SHOWS_ENUM_FALLBACK, INFORMATION_SHAPES_FALLBACK, NEVER_LEAD_FALLBACK,
            "shows vocab from the SPEC §3.3/§3.8 literals (image-source-types.json unreadable)")


def load_table_kinds() -> tuple[tuple[str, ...], str]:
    """The legal `data-table-kind` values, READ FROM the structure of record.

    `references/format-skeletons/weekly.json` § structural_hooks.table_kind states
    the enum inline as `data-table-kind ∈ a|b|c…`. Parsing it means a seventh kind
    propagates the moment WP-3 adds it, instead of hard-failing a legitimate card
    because this file has not caught up — which is exactly what happened to the
    sixth kind (`finance`): the enum was hardcoded here, so the Desk's financial
    card could not be stamped without taking the golden to exit 1.
    """
    path = SKILL_ROOT / "references" / "format-skeletons" / "weekly.json"
    keypaths = (("structural_hooks", "table_kind"),                    # canonical hook
                ("furniture_layer", "components", "standings_card"))   # same list, restated
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        for keypath in keypaths:
            node: object = doc
            for key in keypath:
                node = node.get(key) if isinstance(node, dict) else None
                if node is None:
                    break
            if not isinstance(node, str):
                continue
            m = re.search(r"data-table-kind\s*∈\s*([a-z_]+(?:\s*\|\s*[a-z_]+)+)", node)
            if m:
                kinds = tuple(k.strip() for k in m.group(1).split("|") if k.strip())
                if len(kinds) >= 3:
                    return kinds, (f"{len(kinds)} table kind(s) from weekly.json § "
                                   f"{'.'.join(keypath)}")
    except Exception:
        pass
    return TABLE_KINDS_FALLBACK, (f"{len(TABLE_KINDS_FALLBACK)} table kind(s) from the "
                                  "SPEC §3.4 literal (weekly.json unreadable)")


def load_sport_tokens() -> tuple[tuple[str, ...], str]:
    """The closed sport-token list, PARSED from its canonical home.

    data-contracts.md § Sport tokens says adding a token is "a one-line change to
    this list, by WP-1 … and no consumer needs a code change". That is only true
    if consumers read the list rather than hardcoding it, so this parses the
    `a` · `b` · `c` token paragraph out of the markdown and keeps the 22-token
    literal only as a fallback.
    """
    path = SKILL_ROOT / "references" / "spec" / "data-contracts.md"
    try:
        text = path.read_text(encoding="utf-8")
        sec = text.split("### The closed sport-token list", 1)[1].split("\n### ", 1)[0]
        best: list[str] = []
        for para in re.split(r"\n\s*\n", sec):
            if para.count("·") < 5:
                continue        # the prose paragraphs have backticks but no ·-list
            toks = [t for t in re.findall(r"`([a-z][a-z_]*)`", para) if t != "snake_case"]
            if len(toks) > len(best):
                best = toks
        if len(best) >= 10:
            return tuple(dict.fromkeys(best)), f"{len(best)} sport tokens from {path.name}"
    except Exception:
        pass
    return SPORT_TOKENS_FALLBACK, (f"{len(SPORT_TOKENS_FALLBACK)} sport tokens from the "
                                   "data-contracts.md literal (file unreadable)")


# ─── GATE 2 · markup contracts: Long Read vintage (SPEC §3.4/§3.4a, crit. #2) ─

def long_read_section(body: str) -> tuple[str, dict] | None:
    m = re.search(r'<section\b[^>]*\bdata-role\s*=\s*["\']long-read["\'][^>]*>',
                  body, re.IGNORECASE)
    if not m:
        return None
    return (_element_html(body, m.start(), "section"), _tag_attrs(m.group(0)))


def check_long_read_vintage(body: str, report: Report) -> str | None:
    """SPEC §3.4 + §3.4a · acceptance criterion #2.

    `data-vintage` is ALWAYS present and is `news` or `evergreen`.
      evergreen ⇒ `.lr-vintage` present AND the `.byline` carries no issue date.
      news      ⇒ `.lr-vintage` absent  AND the `.byline` keeps its date.

    WP-3's stitcher is the only writer of this attribute, so this asserts the
    RENDERING rather than adjudicating a disagreement with the plan — which is
    why it is worth asserting at all: acceptance criterion #2 is about what the
    reader receives, and "the stitcher meant well" is not evidence.

    Returns the vintage value (or None) so the caller can drive the
    data-lr-framing check off it.
    """
    found = long_read_section(body)
    if not found:
        report.fail("long-read-vintage",
                    "no <section data-role=\"long-read\"> in the rendered body — "
                    "SPEC §3.4's vintage contract has nothing to attach to")
        return None
    section, attrs = found
    vintage = attrs.get("data-vintage")
    if vintage is None:
        report.fail("long-read-vintage",
                    "the Long Read section carries no data-vintage attribute. SPEC §3.4: "
                    "data-vintage is ALWAYS present, 'news' or 'evergreen'. Without it "
                    "nothing downstream can tell a standing story from this week's news "
                    "(defect A), and the anchor reads as a discovery just made.")
        return None
    if vintage not in VINTAGE_VALUES:
        report.fail("long-read-vintage",
                    f"data-vintage=\"{vintage}\" is not one of {list(VINTAGE_VALUES)} (SPEC §3.4)")
        return None

    title = _first_class_element(section, "lr-title") or section
    has_vintage_line = bool(_first_class_element(title, "lr-vintage"))
    byline_el = _first_class_element(title, "byline")
    byline = _visible(byline_el) if byline_el else ""
    date_m = BYLINE_DATE_RE.search(byline)

    problems: list[str] = []
    if vintage == "evergreen":
        if not has_vintage_line:
            problems.append("no .lr-vintage line in .lr-title (SPEC §3.4: present when evergreen)")
        if date_m:
            problems.append(
                f"the .byline carries an issue date ({date_m.group(0)!r}) — an evergreen "
                "anchor's byline must NOT be dated, or the standing story is stamped as news")
    else:
        if has_vintage_line:
            problems.append(".lr-vintage line present on a NEWS anchor (SPEC §3.4: absent when news)")
        if not byline:
            problems.append("no .byline found in .lr-title")
        elif not date_m:
            problems.append("the .byline carries no `· DD MON YYYY` date — a news anchor keeps its date")

    if problems:
        report.fail("long-read-vintage",
                    f"data-vintage=\"{vintage}\" but the rendering disagrees: "
                    + "; ".join(problems) + f". Byline reads: {byline or '(none)'!r}")
    else:
        report.ok("long-read-vintage",
                  f"data-vintage=\"{vintage}\" with a matching rendering "
                  f"(.lr-vintage {'present' if has_vintage_line else 'absent'}, "
                  f"byline {'dated' if date_m else 'date-free'})")
    return vintage


def check_lr_framing(body: str, vintage: str | None, report: Report) -> None:
    """SPEC §3.4 · The Letter frames an evergreen anchor as a feature.

    The paragraph in The Letter that introduces the Long Read carries
    data-lr-framing="feature". PRESENCE is what is checked; the wording stays
    editorial. WP-3 can only warn here (it cannot know which writer paragraph
    introduces the anchor), so the hard check is this one — but only when the
    anchor is evergreen, because a news anchor needs no such framing.
    """
    if vintage != "evergreen":
        return
    letter = None
    for band, start, end in band_regions(body):
        if band == "the_letter":
            letter = body[start:end]
            break
    scope, where = (letter, "The Letter band") if letter is not None else (body, "the issue")
    if re.search(r'\bdata-lr-framing\s*=\s*["\']feature["\']', scope):
        report.ok("lr-framing", f"data-lr-framing=\"feature\" present in {where} (evergreen anchor)")
        return
    stray = re.findall(r'\bdata-lr-framing\s*=\s*["\']([^"\']*)["\']', body)
    report.fail("lr-framing",
                f"the Long Read is evergreen but no data-lr-framing=\"feature\" paragraph is "
                f"in {where} (SPEC §3.4)"
                + (f" — found data-lr-framing={stray} instead" if stray else "")
                + ". The Letter must frame a standing story as a feature; otherwise the issue's "
                  "own introduction sells it as this week's news (defect A).")


def check_cover_leads_on(body: str, report: Report) -> None:
    """SPEC §3.4a note 1 · the cover declares what it leads on.

    `data-cover-leads-on="news|long_read"` on <header class="cover">. WP-3 added
    it beyond §3.4's list so the cover-lead decision is auditable in the rendered
    object; an auditable decision nobody audits is just a longer attribute, so
    presence + enum are checked here.
    """
    m = re.search(r'<header\b[^>]*\bclass\s*=\s*"[^"]*\bcover\b[^"]*"[^>]*>', body, re.IGNORECASE)
    if not m:
        report.warn("cover-leads-on", "no <header class=\"cover\"> found — nothing to assert")
        return
    val = _tag_attrs(m.group(0)).get("data-cover-leads-on")
    if val is None:
        report.fail("cover-leads-on",
                    "<header class=\"cover\"> carries no data-cover-leads-on attribute "
                    "(SPEC §3.4a note 1; values 'news' | 'long_read'). Without it the cover's "
                    "lead decision leaves no machine record, which is half of defect C.")
    elif val not in COVER_LEADS_ON_VALUES:
        report.fail("cover-leads-on",
                    f"data-cover-leads-on=\"{val}\" is not one of {list(COVER_LEADS_ON_VALUES)} "
                    "(SPEC §3.4a note 1)")
    else:
        report.ok("cover-leads-on", f"cover declares data-cover-leads-on=\"{val}\"")


def scorecards(body: str) -> list[dict]:
    """Every `.mx-scorecard` CARD ELEMENT (not its `__child` classes), with the
    band it sits in and its visible title — so an undeclared card can be named."""
    regions = band_regions(body)
    out: list[dict] = []
    rx = re.compile(r'<([a-z0-9]+)\b[^>]*\bclass\s*=\s*"[^"]*\bmx-scorecard\b[^"]*"[^>]*>',
                    re.IGNORECASE)
    for m in rx.finditer(body):
        el = _element_html(body, m.start(), m.group(1))
        title_el = _first_class_element(el, "mx-scorecard__title")
        band = _band_at(regions, m.start())
        out.append({
            "kind": _tag_attrs(m.group(0)).get("data-table-kind"),
            "band": band[0] if band else "(no band)",
            "title": _visible(title_el) if title_el else "(untitled)",
        })
    return out


def check_table_kind(body: str, report: Report) -> None:
    """SPEC §3.4 / §3.11 · `.mx-scorecard` is polymorphic, and the legal shapes are
    the ones the structure of record names.

    A value outside the set renders as the unstyled base card — the single
    right-aligned gap column that was the reason only a weekly-table sport could
    fill The Touchline's furniture. Value validity is a hard FAIL; a
    `.mx-scorecard` with NO data-table-kind is a WARN, because every issue in the
    archive predates the attribute and retro-failing them is not what the gate is
    for.

    Reported PER CARD, not per issue. WP-3b found the earlier per-issue form
    effectively silent: one declared card suppressed the warning for every
    undeclared one, so the Desk's financial card went unreported. Each card is
    now named by band and title, which is what makes the warning actionable.
    """
    kinds, kinds_note = load_table_kinds()
    cards = scorecards(body)
    # Read the values from the DOM as well as from the cards, so a data-table-kind
    # on something that is not a .mx-scorecard is still validated.
    values = re.findall(r'\bdata-table-kind\s*=\s*["\']([^"\']*)["\']', body)
    bad = sorted({v for v in values if v not in kinds})
    if bad:
        report.fail("table-kind",
                    f"data-table-kind value(s) outside the legal shapes: {bad}. "
                    f"Legal: {list(kinds)} ({kinds_note}). A value outside the set renders as "
                    f"the unstyled base card — CSS exists for exactly these shapes. If the shape "
                    f"is genuinely new, it is a weekly.json + CSS change (WP-3's files), not a "
                    f"value a writer can invent.")
        return
    declared = [c for c in cards if c["kind"]]
    undeclared = [c for c in cards if not c["kind"]]
    if values:
        report.ok("table-kind",
                  f"{len(values)} data-table-kind value(s), all legal: {sorted(set(values))} "
                  f"({kinds_note})")
    if undeclared:
        report.warn("table-kind/undeclared",
                    f"{len(undeclared)} of {len(cards)} .mx-scorecard card(s) carry no "
                    f"data-table-kind and render as the unstyled base shape:\n"
                    + "\n".join(f"    • band '{c['band']}' — \"{c['title']}\"" for c in undeclared)
                    + f"\n    Declare one of {list(kinds)} (SPEC §3.4 / §3.11). Reported per card: "
                      f"{len(declared)} card(s) in this issue DO declare a kind, and a per-issue "
                      f"check would have said nothing about these.")


# ─── GATE 2 · markup contracts: sport tokens (SPEC §3.11, criterion #7) ──────

def check_sport_tokens(body: str, report: Report) -> None:
    """SPEC §3.11 + data-contracts.md § Sport tokens.

    HARD FAIL on `data-sport="multi_sport"`: a result belongs to a sport, and
    `[motorsport, multi_sport]` would satisfy "≥2 distinct" while telling the
    reader nothing about breadth — the F1-saturation defect passing its own check.
    WARN (never fail, even under --strict) on a token outside the closed list:
    the list is closed-with-an-extension-path and a games long tail (lawn bowls,
    para events) must not block a ship.
    """
    tokens = re.findall(r'\bdata-sport\s*=\s*["\']([^"\']*)["\']', body)
    if not tokens:
        return
    allowed, vocab_note = load_sport_tokens()
    multi = [t for t in tokens if t == "multi_sport"]
    unknown = sorted({t for t in tokens if t != "multi_sport" and t not in allowed})
    known = sorted({t for t in tokens if t in allowed})

    if multi:
        report.fail("sport-tokens",
                    f"data-sport=\"multi_sport\" on {len(multi)} row(s) — FORBIDDEN in rendered "
                    "HTML (SPEC §3.11; legal only in state.sports_calendar[].sport, where it "
                    "classifies an EVENT). A result belongs to a specific sport: a Games "
                    "swimming final is data-sport=\"swimming\", a Games 10,000m is "
                    "data-sport=\"athletics\" — one row per sport, never one row for the games.")
    else:
        report.ok("sport-tokens",
                  f"{len(tokens)} data-sport value(s), no multi_sport; "
                  f"distinct: {known + unknown or ['(none)']} ({vocab_note})")
    if unknown:
        report.soft_warn(
            "sport-tokens/vocabulary",
            f"data-sport token(s) outside the closed list: {unknown}. Not a failure — the list "
            f"is extended by appending to references/spec/data-contracts.md § Sport tokens (WP-1), "
            f"and a check that blocks a genuinely new sport would block the breadth it exists to "
            f"force. Confirm the token is a SPORT (not a competition) and add it there.")


def _tracked_concluded_sports(state: dict, window_from: str | None, run_date: str) -> tuple[set[str], list[dict]]:
    """Sports whose tracked event CONCLUDED in (window_from, run_date].

    "Tracked" per data-contracts.md § interest_depth: a sport is tracked unless
    its depth is explicitly "off". An ABSENT key is unset, never off — reading it
    as off would recreate defect D's invisible-sport problem in a new place.
    Returns (specific sport tokens, multi-sport games rows).
    """
    depth = state.get("interest_depth") or {}
    specific: set[str] = set()
    games: list[dict] = []
    for ev in state.get("sports_calendar") or []:
        end = ev.get("end") or ev.get("start")
        if not isinstance(end, str) or not end:
            continue
        if end > run_date:
            continue                                  # not concluded yet
        if window_from and end <= window_from:
            continue                                  # concluded before the window opened
        if ev.get("reader_relevant") is False:
            continue
        sport = ev.get("sport")
        if not isinstance(sport, str):
            continue
        if depth.get(sport) == "off":
            continue
        if sport == "multi_sport":
            games.append(ev)
        else:
            specific.add(sport)
    return specific, games


def check_results_ledger_breadth(body: str, state: dict | None, window_from: str | None,
                                 run_date: str | None, report: Report) -> None:
    """SPEC §3.11 invariant `results_ledger_multi_sport` · acceptance criterion #7.

    The results ledger must carry ≥2 distinct `data-sport` values whenever ≥2
    tracked sports had an event conclude in-window. The HTML does not contain
    either input, so this reads state's `sports_calendar` and `interest_depth`
    (§3.4a note 7 — the reason --state exists) and the window
    (state.research_cut_at, run_date].

    A multi-sport games that concluded in-window counts as "≥2 sports concluded":
    that is what a games IS, and its results are required to be tagged per sport.
    Distinctness is counted over SPECIFIC tokens only.
    """
    if state is None or run_date is None:
        report.warn("results-ledger-multi-sport",
                    "skipped — needs --state (interest_depth + sports_calendar) and --run-date; "
                    "SPEC §3.4a note 7. Neither input exists in the rendered HTML.")
        return
    specific, games = _tracked_concluded_sports(state, window_from, run_date)
    applies = len(specific) >= 2 or bool(games)
    window_note = f"window ({window_from or 'unbounded'}, {run_date}]"
    if not applies:
        report.ok("results-ledger-multi-sport",
                  f"not applicable — {len(specific)} tracked sport(s) concluded in the "
                  f"{window_note}: {sorted(specific) or '[]'}; the invariant needs ≥2")
        return

    ledger = None
    m = re.search(r'<div\b[^>]*\bdata-role\s*=\s*["\']results-ledger["\'][^>]*>', body, re.IGNORECASE)
    if m:
        ledger = _element_html(body, m.start(), "div")
    scope, where = (ledger, "the results ledger") if ledger else (body, "the issue (NO results ledger element)")
    tokens = {t for t in re.findall(r'\bdata-sport\s*=\s*["\']([^"\']*)["\']', scope)
              if t and t != "multi_sport"}
    reason = (f"≥2 tracked sports concluded in the {window_note}: "
              f"{sorted(specific) or '[]'}"
              + (f" plus multi-sport event(s) {[g.get('event') for g in games]}" if games else ""))
    if len(tokens) >= 2:
        report.ok("results-ledger-multi-sport",
                  f"{len(tokens)} distinct sport token(s) in {where} ({sorted(tokens)}) — {reason}")
    else:
        report.fail("results-ledger-multi-sport",
                    f"{reason}, but {where} carries {len(tokens)} distinct data-sport value(s) "
                    f"({sorted(tokens) or '[]'}). SPEC §3.11 invariant "
                    f"results_ledger_multi_sport requires ≥2. One sport filling the band while "
                    f"another's concluded event goes unreported IS defect D — five bands of one "
                    f"race and a vanished World Cup final.")


# ─── GATE 2 · markup contracts: resolved loops (SPEC §3.7, criterion #6) ─────

def matured_loops(state: dict, run_date: str) -> list[dict]:
    """SPEC §3.7: a loop is MATURED when status == "open" and
    expected_resolution_date <= run_date. `dropped` and `resolved` do not mature
    — `dropped` is an honest terminal state for a loop that was never reported.
    """
    out = []
    for loop in state.get("open_loops") or []:
        if loop.get("status") != "open":
            continue
        erd = loop.get("expected_resolution_date")
        if isinstance(erd, str) and erd and erd <= run_date:
            out.append(loop)
    return out


def check_resolved_loops(body: str, state: dict | None, run_date: str | None,
                         report: Report) -> None:
    """SPEC §3.7 · acceptance criterion #6.

    FAIL if a matured loop's id has no `data-resolves-loop` in the rendered HTML.
    Both layers check this (the bundle gate is WP-5's) because a bundle can carry
    a resolving fact the writer then drops — which is exactly how the World Cup
    final was gate-checked as an upcoming fact and then never reported.
    """
    if state is None or run_date is None:
        report.warn("resolved-loops",
                    "skipped — needs --state (open_loops) and --run-date (SPEC §3.7)")
        return
    loops = matured_loops(state, run_date)
    rendered = set(re.findall(r'\bdata-resolves-loop\s*=\s*["\']([^"\']*)["\']', body))
    all_ids = {l.get("id") for l in (state.get("open_loops") or [])}
    orphans = sorted(v for v in rendered if v and v not in all_ids)
    if not loops:
        report.ok("resolved-loops",
                  f"no matured open loop as of {run_date} "
                  f"({len(state.get('open_loops') or [])} loop(s) in state; a 'dropped' or "
                  f"'resolved' loop does not mature) — "
                  f"{len(rendered)} data-resolves-loop attribute(s) rendered")
    else:
        missing = [l for l in loops if l.get("id") not in rendered]
        if missing:
            lines = [f"{len(missing)} of {len(loops)} matured open loop(s) have no "
                     f"data-resolves-loop in the rendered HTML (run-date {run_date}, SPEC §3.7):"]
            for l in missing:
                lines.append(f"    • {l.get('id')} — due {l.get('expected_resolution_date')}, "
                             f"band '{l.get('band')}', opened in issue {l.get('issue_opened')}: "
                             f"{l.get('claim')}")
            lines.append("    A carried-forward result must be reported and marked with "
                         "data-resolves-loop=\"<id>\", or the loop silently vanishes (defect D).")
            report.fail("resolved-loops", "\n".join(lines))
        else:
            report.ok("resolved-loops",
                      f"all {len(loops)} matured loop(s) resolved in the HTML: "
                      + ", ".join(sorted(l.get('id') or '?' for l in loops)))
    if orphans:
        report.warn("resolved-loops/unknown-id",
                    f"data-resolves-loop id(s) not present in state.open_loops: {orphans}. "
                    "The id is a foreign key, not a label (data-contracts.md § open_loops).")


# ─── GATE 1 · image checks: figure provenance (SPEC §3.4 / §3.4a note 6) ─────

def check_figure_provenance(figs: list[dict], shows_enum: tuple[str, ...],
                            vocab_note: str, report: Report) -> None:
    """SPEC §3.4 + §3.4a note 6 · every .plate-img carries the machine record.

    This check is ENTIRELY WP-4's to make bite. WP-3's stitcher stamps
    data-shows / data-capture-year / data-licence / data-allows-derivatives only
    from assets/cached/manifest.json, and all 438 of WP-8's entries are honest
    UNKNOWN back-fills, so today 0 of 14 figures get anything from the stitcher.
    Until the manifest carries real records, every attribute comes from the
    writer — and only this gate can fail its absence.

    Value validity, per §3.4a note 3: `data-capture-year=""` is the LEGAL null
    rendering (a synthetic diagram/chart has no capture year). A value that is
    neither empty nor a 4-digit year in 1500–2100 FAILS — the stitcher never
    emits one, so it came from a writer.
    """
    if not figs:
        report.warn("figure-provenance", "no .plate-img figures found — nothing to assert")
        return

    gaps: list[str] = []
    bad: list[str] = []
    soft: list[str] = []
    for f in figs:
        a = f["attrs"]
        missing = [k for k in FIGURE_PROVENANCE_ATTRS if k not in a]
        if missing:
            gaps.append(f"    • {_fig_id(f)} — missing {', '.join(missing)}")
        shows = a.get("data-shows")
        if shows is not None and shows not in shows_enum:
            bad.append(f"    • {_fig_id(f)} — data-shows=\"{shows}\" is not in the shows enum")
        cy = a.get("data-capture-year")
        if cy is not None and cy != "":
            if not FOUR_DIGIT_RE.match(cy) or not (1500 <= int(cy) <= 2100):
                bad.append(f"    • {_fig_id(f)} — data-capture-year=\"{cy}\" is neither empty "
                           f"nor a 4-digit year in 1500–2100")
        ad = a.get("data-allows-derivatives")
        if ad is not None and ad not in ("true", "false"):
            bad.append(f"    • {_fig_id(f)} — data-allows-derivatives=\"{ad}\" is not true|false")
        lic = a.get("data-licence")
        if lic is not None and not lic.strip():
            bad.append(f"    • {_fig_id(f)} — data-licence is empty")
        elif lic is not None and lic.strip().upper() == "UNKNOWN":
            soft.append(f"{_fig_id(f)}")

    if gaps:
        report.fail("figure-provenance",
                    f"{len(gaps)} of {len(figs)} .plate-img figure(s) are short of the SPEC §3.4 "
                    f"provenance record ({', '.join(FIGURE_PROVENANCE_ATTRS)}):\n"
                    + "\n".join(gaps)
                    + "\n    Fix upstream, not by hand: give the research bundle's image_candidate "
                      "its `shows`, `capture_year` and `licence` (SPEC §3.2) so mirror-images.py "
                      "writes them to assets/cached/manifest.json and the stitcher stamps them. "
                      "A writer-authored attribute is honoured and never overwritten.")
    else:
        report.ok("figure-provenance",
                  f"all {len(figs)} .plate-img figure(s) carry the four-attribute provenance "
                  f"record ({vocab_note})")
    if bad:
        report.fail("figure-provenance/values",
                    f"{len(bad)} invalid provenance value(s) — these came from a writer, because "
                    f"the stitcher refuses to stamp a placeholder (SPEC §3.4a notes 3 and 6):\n"
                    + "\n".join(bad)
                    + f"\n    shows enum: {list(shows_enum)}")
    if soft:
        report.warn("figure-provenance/licence-unknown",
                    f"{len(soft)} figure(s) render data-licence=\"UNKNOWN\": {'; '.join(soft[:4])}"
                    + (f" (+{len(soft)-4} more)" if len(soft) > 4 else "")
                    + ". UNKNOWN is legal in the research bundle as a signal not to build on the "
                      "asset — it is not a licence to publish or crop (data-contracts.md § licence).")


# ─── GATE 1 · image checks: caption vintage (SPEC §3.9, criterion #3) ────────

def check_caption_vintage(body: str, figs: list[dict], issue_year: int | None,
                          report: Report) -> None:
    """SPEC §3.9 · fixes defect B mechanically. Acceptance criterion #3.

    For each .plate-img with a NON-EMPTY 4-digit `data-capture-year`: let
    claim_max be the largest year in 1500–2100 in the enclosing band's prose
    (figure captions excluded). If capture_year < claim_max, the caption's
    VISIBLE sentence — `.plate-cap .txt`, excluding the nested `.credit` span —
    must contain the capture year as a 4-digit string.

    Worked example this is calibrated on (issue #18, FIG 03): capture_year 2007,
    the band claims 2021, and the `.txt` reads "A working modern reconstruction
    of the front dial…" with the year only in `.credit` → fails, correctly.
    Rewriting `.txt` to "a 2007 working reconstruction, built on the pre-2021
    understanding" → passes.

    `data-capture-year=""` means "no year to compare" and is skipped (§3.4a
    note 3); an absent attribute is the provenance check's business, not this
    one, so the two never double-report the same figure.
    """
    considered = 0
    failures: list[str] = []
    passes: list[str] = []
    blind: list[str] = []
    band_cache: dict[tuple[int, int], tuple[list[tuple[int, str]], list[str]]] = {}
    for f in figs:
        cy_raw = f["attrs"].get("data-capture-year")
        if cy_raw is None or cy_raw == "":
            continue
        if not FOUR_DIGIT_RE.match(cy_raw):
            continue                       # reported by check_figure_provenance
        cy = int(cy_raw)
        if not (1500 <= cy <= 2100):
            continue                       # ditto
        considered += 1
        span = f["band_span"]
        if span not in band_cache:
            band_cache[span] = band_claim_years(band_prose(body, span), issue_year)
        claims, unresolved = band_cache[span]
        visible = f["cap_visible"]
        stated = bool(visible and cy_raw in visible)
        # A band's unresolvable date expressions only matter for a figure that
        # would otherwise PASS — they are the reason the pass might be wrong.
        if unresolved and not stated:
            blind.append(f"    • {_fig_id(f)} — capture {cy}; band '{f['band']}' contains a date "
                         f"expression this check cannot resolve to a year: " + "; ".join(unresolved))
        if not claims:
            passes.append(f"{_fig_id(f)} — capture {cy}, band makes no dated claim")
            continue
        claim_max, evidence = max(claims, key=lambda c: c[0])
        if cy >= claim_max:
            passes.append(f"{_fig_id(f)} — capture {cy} ≥ band's latest claim {claim_max} ({evidence})")
            continue
        if stated:
            passes.append(f"{_fig_id(f)} — capture {cy} < claim {claim_max}, and the visible "
                          f"caption says so")
        else:
            failures.append(
                f"    • {_fig_id(f)}\n"
                f"        capture year {cy} is OLDER than the band's latest claim {claim_max} "
                f"[{evidence}], and \"{cy}\" does not appear in the caption's visible sentence.\n"
                f"        .plate-cap .txt (credit excluded) reads: "
                f"{(visible if visible is not None else '(no .plate-cap .txt)')!r}")

    if blind:
        report.warn("caption-vintage/unparsed-dates",
                    f"{len(blind)} dated figure(s) sit in a band whose prose carries a date "
                    f"expression that cannot be resolved to a year, so §3.9's claim_max may be "
                    f"UNDERSTATED and the verdict below may be a false pass:\n" + "\n".join(blind)
                    + "\n    This is the documented blind spot, reported rather than hidden: a "
                      "relative span ('one hundred and forty-nine years after the first "
                      "Championships'), 'the turn of the century' or a bare decade ('the sixties') "
                      "needs an anchor year this check does not have. Digits, spelled-out years and "
                      "this-week deixis ARE resolved. Check by eye that the caption is not older "
                      "than what the band claims — or write the year into the caption, which makes "
                      "both the reader and this check certain.")
    if failures:
        report.fail("caption-vintage",
                    f"{len(failures)} of {considered} dated figure(s) illustrate a later claim "
                    f"without saying so (SPEC §3.9):\n" + "\n".join(failures)
                    + "\n    A reader who is not told the picture is older than the claim reads it "
                      "as a picture OF the claim — a 2007 reconstruction illustrating a 2021 "
                      "breakthrough (defect B). Put the year in the sentence the reader sees; a "
                      "year in the .credit span does not count, because nobody reads a credit as "
                      "a date correction.")
    elif considered:
        report.ok("caption-vintage",
                  f"{considered} figure(s) with a dated capture year, all consistent with their "
                  f"band's claims: " + "; ".join(passes[:4])
                  + (f" (+{len(passes)-4} more)" if len(passes) > 4 else ""))
    else:
        report.warn("caption-vintage",
                    "no .plate-img carries a non-empty 4-digit data-capture-year, so SPEC §3.9 has "
                    "nothing to compare. This is NOT a pass: without a capture year, nothing can "
                    "tell that a photograph predates the claim it illustrates (defect B). See the "
                    "figure-provenance check.")


# ─── GATE 1 · image checks: shape budgets (SPEC §3.8, criterion #8) ──────────

def _caption_reports_result(fig: dict) -> str | None:
    if fig["attrs"].get("data-resolves-loop"):
        return "carries data-resolves-loop (a carried-forward result)"
    cap = fig["cap_visible"] or ""
    for rx in RESULT_CAPTION_RES:
        m = rx.search(cap)
        if m:
            return f"caption reports a decided result ({m.group(0)!r})"
    return None


def check_image_shape_budgets(figs: list[dict], info_shapes: tuple[str, ...],
                              never_lead: tuple[str, ...],
                              manifest: dict | None, issue_no: int | None,
                              report: Report) -> None:
    """SPEC §3.8 · acceptance criterion #8.

    Six budgets, each a hard FAIL:
      1. ≥3 distinct data-shows across the issue (min_distinct_shapes, §3.14).
      2. Pixel & Byte: at most one key_art, and key_art is never the band's lead.
      3. Never-lead, issue-wide: no lead figure may be a never_lead_shape
         (§3.8 "Never-lead, resolved 2026-07-26"), with product_shot conditional.
      4. The Long Read carries ≥1 of diagram|map|chart|artefact.
      5. A Touchline figure captioned as a concluded result must be event_photo.
      6. Cross-issue: a src that LED the previous issue may not lead this one.

    (1) and (4) are counted over what the figures DECLARE, so an issue with no
    data-shows at all fails them — correctly. The budget is a per-issue floor on
    what the reader is shown; "we didn't say what the pictures are" is not a way
    to satisfy it. (2), (3) and (5) can only speak about a declared value, so they
    stay silent when the attribute is absent rather than double-reporting a
    figure the provenance check has already failed.
    """
    if not figs:
        report.warn("image-shapes", "no .plate-img figures found — nothing to assert")
        return

    declared = [f for f in figs if f["attrs"].get("data-shows")]
    distinct = sorted({f["attrs"]["data-shows"] for f in declared})

    # 1 · distinct shapes per issue
    if len(distinct) < MIN_DISTINCT_SHOWS:
        report.fail("image-shapes/distinct",
                    f"{len(distinct)} distinct data-shows value(s) across {len(figs)} figure(s) "
                    f"({distinct or '[]'}); the floor is {MIN_DISTINCT_SHOWS} "
                    f"(SPEC §3.8 / §3.14 min_distinct_shapes)"
                    + (f" — only {len(declared)} of {len(figs)} figures declare data-shows at all"
                       if len(declared) < len(figs) else "")
                    + ". This floor replaced the retired Wikimedia CEILINGS: a ceiling reads as a "
                      "target, and nothing set a floor for the interesting shapes (defect E).")
    else:
        report.ok("image-shapes/distinct",
                  f"{len(distinct)} distinct data-shows value(s) (floor {MIN_DISTINCT_SHOWS}): {distinct}")

    # 2 · Pixel & Byte key-art budget
    pb = [f for f in figs if f["band"] == "pixel_byte"]
    if pb:
        key_art = [f for f in pb if f["attrs"].get("data-shows") == "key_art"]
        leads = [f for f in key_art if f["is_lead"]]
        problems = []
        if len(key_art) > 1:
            problems.append(f"{len(key_art)} key_art figures (cap is 1): "
                            + "; ".join(_fig_id(f) for f in key_art))
        if leads:
            problems.append("key_art is the band's LEAD figure (.plate-img.lead): "
                            + "; ".join(_fig_id(f) for f in leads))
        if problems:
            report.fail("image-shapes/pixel-byte-key-art",
                        "; ".join(problems)
                        + ". SPEC §3.8: at most one key_art in Pixel & Byte and never as the lead. "
                          "Key art with the logo composited in tells the reader nothing the "
                          "headline didn't — Steam's appdetails API returns a screenshots[] array "
                          "per game and shared.fastly.steamstatic.com is already in the domain map "
                          "(SPEC §3.13).")
        else:
            report.ok("image-shapes/pixel-byte-key-art",
                      f"Pixel & Byte: {len(key_art)} key_art figure(s), none leading "
                      f"({len(pb)} figure(s) in the band)")

    # 3 · never-lead shapes, issue-wide (SPEC §3.8, resolved 2026-07-26)
    hard_never = tuple(s for s in never_lead if s not in CONDITIONAL_LEAD_SHAPES)
    cond_never = tuple(s for s in never_lead if s in CONDITIONAL_LEAD_SHAPES)
    lead_figs = [f for f in figs if f["is_lead"] and f["attrs"].get("data-shows")]
    banned = [f for f in lead_figs if f["attrs"]["data-shows"] in hard_never]
    if banned:
        report.fail("image-shapes/never-lead",
                    f"{len(banned)} band lead figure(s) use a never-lead shape "
                    f"{list(hard_never)} (SPEC §3.8, resolved 2026-07-26 — issue-wide, any band):\n"
                    + "\n".join(f"    • {_fig_id(f)} — data-shows=\"{f['attrs']['data-shows']}\""
                                for f in banned)
                    + "\n    Both substitute for showing the thing itself: key art is the logo, and "
                      "a posed portrait is the person NOT doing the thing (the 'random Pope photo' "
                      "failure). A lead figure is the band's establishing image — lead with the "
                      "event, the gameplay, the diagram or the artefact.")
    else:
        report.ok("image-shapes/never-lead",
                  f"none of the {len(lead_figs)} declared lead figure(s) use a never-lead shape "
                  f"{list(hard_never)}")
    # product_shot is the ONE conditional case and the condition — "the band's
    # subject IS the product" — is not in the rendered HTML. A band carries no
    # machine-readable subject type: `data-band="pixel_byte"` covers hardware,
    # software, games and services alike, and inferring "this is a hardware
    # review" from prose would be a guess. So this is reported, not enforced:
    # per the SPEC's own reasoning, a check that guesses wrong on hardware
    # coverage is worse than one that only enforces the unambiguous shapes.
    cond_leads = [f for f in lead_figs if f["attrs"]["data-shows"] in cond_never]
    if cond_leads:
        report.warn("image-shapes/never-lead-conditional",
                    f"{len(cond_leads)} band lead figure(s) are "
                    f"{list(cond_never)}: "
                    + "; ".join(_fig_id(f) for f in cond_leads)
                    + f". SPEC §3.8 allows this ONLY when the band's subject IS the product (a "
                      f"hardware launch or review) and forbids it for a software, game or service "
                      f"band. The rendered HTML carries no machine-readable band subject, so this "
                      f"cannot be decided mechanically — confirm it by eye at gate 3. Reported, "
                      f"deliberately not failed: blocking it outright would break the legitimate "
                      f"hardware coverage this reader gets.")

    # 4 · Long Read information figure
    lr = [f for f in figs if f["band"] == "long_read"]
    if lr:
        info = [f for f in lr if f["attrs"].get("data-shows") in info_shapes]
        if not info:
            report.fail("image-shapes/long-read-information",
                        f"the Long Read's {len(lr)} figure(s) include none of "
                        f"{list(info_shapes)} (SPEC §3.8). Declared: "
                        + (", ".join(sorted({f["attrs"].get("data-shows") or "(no data-shows)"
                                             for f in lr})))
                        + ". The anchor piece needs at least one figure that carries information "
                          "the prose cannot — the Antikythera Long Read needed the 2021 Freeth "
                          "Scientific Reports figures (CC BY, already-whitelisted domain) and went "
                          "to Commons for a perspex model instead (SPEC §3.14).")
        else:
            report.ok("image-shapes/long-read-information",
                      f"the Long Read carries {len(info)} information figure(s): "
                      + ", ".join(f"{f['label']}={f['attrs']['data-shows']}" for f in info))

    # 5 · a concluded Touchline result is an event photo
    tl = [f for f in figs if f["band"] == "touchline"]
    result_figs = [(f, why) for f in tl for why in [_caption_reports_result(f)] if why]
    offenders = [(f, why) for f, why in result_figs
                 if f["attrs"].get("data-shows") and f["attrs"]["data-shows"] != "event_photo"]
    if offenders:
        report.fail("image-shapes/touchline-result",
                    f"{len(offenders)} Touchline figure(s) report a concluded result but are not "
                    f"event_photo (SPEC §3.8):\n"
                    + "\n".join(f"    • {_fig_id(f)} — data-shows=\"{f['attrs']['data-shows']}\", {why}"
                                for f, why in offenders)
                    + "\n    A result that happened has a photograph of it happening.")
    elif result_figs:
        report.ok("image-shapes/touchline-result",
                  f"{len(result_figs)} Touchline result figure(s), none mis-shaped "
                  + "; ".join(f"{f['label']}={f['attrs'].get('data-shows') or '(undeclared)'}"
                              for f, _ in result_figs))

    # 6 · cross-issue: last week's lead cannot lead again
    leads = [f for f in figs if f["is_lead"] and f["hash"]]
    if manifest is None or issue_no is None:
        report.warn("image-shapes/cross-issue-lead",
                    "skipped — needs assets/cached/manifest.json and this issue's number "
                    f"(manifest={'found' if manifest else 'missing'}, "
                    f"issue_no={issue_no}). SPEC §3.8 reads the manifest's led[].")
        return
    prev = issue_no - 1
    prev_led = {h for h, e in manifest.items() if isinstance(e, dict) and prev in (e.get("led") or [])}
    repeats = [f for f in leads if f["hash"] in prev_led]
    if repeats:
        report.fail("image-shapes/cross-issue-lead",
                    f"{len(repeats)} figure(s) led issue #{prev} and lead issue #{issue_no} again "
                    f"(SPEC §3.8):\n"
                    + "\n".join(f"    • {_fig_id(f)}" for f in repeats)
                    + "\n    A lead image is the issue's face; reusing last week's makes two "
                      "issues look like one.")
    else:
        report.ok("image-shapes/cross-issue-lead",
                  f"none of the {len(leads)} lead figure(s) led issue #{prev} "
                  f"({len(prev_led)} asset(s) recorded as leading #{prev})")


# ─── inputs: repo root, state, manifest, run-date, issue number ──────────────

def find_repo_root(html_path: Path) -> Path:
    """The repo root — where state/ and assets/cached/ live.

    Resolved from THIS SCRIPT's location first (the script always lives in the
    repo at .claude/skills/the-signal/scripts/), so the state-dependent checks
    still run when the HTML under test is a stitch in a temp directory — which is
    how verify-weekly-golden.sh invokes the gate. Falls back to the html-relative
    guess the image-URL check already uses.
    """
    for cand in [SKILL_ROOT, *SKILL_ROOT.parents]:
        if (cand / "state" / "signal-state.json").is_file():
            return cand
    for cand in [html_path.resolve().parent, *html_path.resolve().parents]:
        if (cand / "state" / "signal-state.json").is_file():
            return cand
    return html_path.resolve().parent.parent


def load_json_file(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def resolve_run_date(arg: str | None, path: Path) -> tuple[str, str]:
    """(YYYY-MM-DD, provenance). --run-date wins; then a date in the filename;
    then today (UTC). Never guessed silently — the provenance is printed."""
    if arg:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", arg):
            raise ValueError(f"--run-date must be YYYY-MM-DD, got {arg!r}")
        return arg, "--run-date"
    m = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
    if m:
        return m.group(1), f"parsed from the filename ({path.name})"
    return (datetime.datetime.now(datetime.timezone.utc).date().isoformat(),
            "today (UTC) — no --run-date and no date in the filename")


def resolve_issue_number(body: str, path: Path, manifest: dict | None) -> tuple[int | None, str]:
    """This issue's number, for the cross-issue lead budget.

    FOLIO is the masthead's own numbering and appears exactly once; the №
    stamps appear several times (masthead, colophon, and a "NEXT WEEK · №019"
    forward reference), so they are resolved by majority. Last resort: the
    filename slug looked up in the manifest's issue_slugs.
    """
    m = re.search(r"\bFOLIO\s+0*(\d+)\b", body)
    if m:
        return int(m.group(1)), "masthead FOLIO"
    nums = [int(n) for n in re.findall(r"№\s*0*(\d+)", body)]
    if nums:
        return Counter(nums).most_common(1)[0][0], "№ stamp (majority)"
    m = COLOPHON_SIGN_RE.search(body)
    if m:
        return int(m.group(1)), "colophon signature"
    if manifest:
        slug = path.stem
        for e in manifest.values():
            if isinstance(e, dict) and slug in (e.get("issue_slugs") or []):
                issues = e.get("issues") or []
                if issues:
                    return int(issues[-1]), f"manifest issue_slugs match on {slug}"
    return None, "not determinable"


def run_coverage_checks(html: str, fmt: str, new_system: bool, path: Path,
                        state_arg: str | None, run_date_arg: str | None,
                        report: Report) -> None:
    """Wire the coverage-rebuild checks into the two existing gates.

    SCOPE. The weekly-structure contracts (§3.4, §3.4a, §3.7, §3.8, §3.11) are
    asserted on NEW-SYSTEM WEEKLIES only — the same exemption the Law-3/Law-9/F-16
    checks already use, and for the same reason: retro-failing the old-system
    archive is not what the gate is for, and no special edition has a Long Read
    band, a Touchline or a results ledger to check. Issue #18 IS a new-system
    weekly, so it is fully in scope and is expected to fail (SPEC §1.3).

    Two checks run on EVERY format because they are self-gating and format-blind:
    caption vintage (§3.9 — inert unless a figure declares a capture year) and
    the sport-token vocabulary (§3.11 — inert unless something declares
    data-sport). A dated figure lying about its vintage is defect B wherever it
    is printed.
    """
    body = body_text_only(html)          # the inlined <style> carries
                                         # .mx-scorecard[data-table-kind="…"] and
                                         # .lr-title .lr-vintage — scanning the raw
                                         # document would read CSS as markup.
    figs = collect_figures(body)
    shows_enum, info_shapes, never_lead, vocab_note = load_shows_vocab()

    repo_root = find_repo_root(path)
    state_path = Path(state_arg) if state_arg else repo_root / "state" / "signal-state.json"
    state = load_json_file(state_path)
    manifest_path = repo_root / "assets" / "cached" / "manifest.json"
    manifest = load_json_file(manifest_path)
    run_date, rd_from = resolve_run_date(run_date_arg, path)
    issue_no, issue_from = resolve_issue_number(body, path, manifest)
    cut = (state or {}).get("research_cut_at")
    window_from = cut[:10] if isinstance(cut, str) and len(cut) >= 10 else None
    # The issue's own year, for §3.9's this-week deixis: in a weekly, "this week"
    # or "on Monday" IS a claim about this year, and taking it from the resolved
    # run-date is the only honest source (the masthead dateline is furniture that
    # band_prose strips, and it is not always present).
    issue_year = int(run_date[:4])

    print("  ── coverage-rebuild inputs (SPEC 2026-07-26) ──")
    print(f"     state:     {state_path} {'OK' if state else 'NOT READ'}")
    print(f"     manifest:  {manifest_path} "
          f"{f'OK ({len(manifest)} entries)' if manifest else 'NOT READ'}")
    print(f"     run-date:  {run_date}  ({rd_from})")
    print(f"     window:    ({window_from or 'unbounded'}, {run_date}]  "
          f"from state.research_cut_at")
    print(f"     issue no:  {issue_no}  ({issue_from})")
    print(f"     figures:   {len(figs)} .plate-img")
    print()

    # In scope: a weekly that is either a new-system (data-mx) artifact or carries
    # ANY post-rebuild attribute. The second clause closes a real hole: the mx
    # layer is OPT-IN (stitch_weekly.py:541 — `data-mx` is written only when
    # mx=True), so a weekly stitched on the legacy path is not "new-system" while
    # still being post-WP-3 output that emits the whole contract. Keying on the
    # presence of any rebuild-era attribute is not circular — one attribute
    # anywhere puts the issue in scope for ALL of them, so an issue cannot escape
    # the cover-leads-on check by omitting data-cover-leads-on.
    rebuild_era = bool(re.search(
        r'\bdata-(?:nav-band|cover-leads-on|vintage|shows|capture-year|licence|'
        r'allows-derivatives|lr-framing|table-kind|resolves-loop|sport)\s*=', body))
    weekly_new = (fmt == "weekly" and (new_system or rebuild_era))

    # ── GATE 1 · image checks ────────────────────────────────────────────────
    check_caption_vintage(body, figs, issue_year, report)           # §3.9, crit #3
    if weekly_new:
        check_figure_provenance(figs, shows_enum, vocab_note, report)   # §3.4a n6
        check_image_shape_budgets(figs, info_shapes, never_lead, manifest,
                                  issue_no, report)                        # §3.8, crit #8

    # ── GATE 2 · markup contracts ───────────────────────────────────────────
    check_sport_tokens(body, report)                               # §3.11, crit #7
    check_table_kind(body, report)                                 # §3.4
    if weekly_new:
        vintage = check_long_read_vintage(body, report)             # §3.4, crit #2
        check_lr_framing(body, vintage, report)                     # §3.4
        check_cover_leads_on(body, report)                          # §3.4a note 1
        check_results_ledger_breadth(body, state, window_from, run_date, report)  # §3.11, crit #7
        check_resolved_loops(body, state, run_date, report)          # §3.7, crit #6
    elif fmt == "weekly":
        report.warn("coverage-rebuild",
                    "pre-rebuild weekly (no data-mx marker and no rebuild-era attribute anywhere) "
                    "— the SPEC §3.4/§3.7/§3.8/§3.11 structure contracts are not asserted against "
                    "it, the same exemption the Law-3/Law-9/F-16 checks give the old-system "
                    "archive. Caption vintage and the sport-token vocabulary still ran. Anything "
                    "the current stitcher produces is in scope.")


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
    # Coverage-rebuild inputs (SPEC 2026-07-26 §3.4a note 7, §3.7). Both are
    # auto-resolved when omitted so the gate keeps working for callers that
    # cannot be edited from here (stitch-issue.sh / publish-gate.sh are WP-9's).
    ap.add_argument("--state", default=None,
                    help="state/signal-state.json (read-only). Needed by the open-loop and "
                         "results-ledger-breadth checks. Auto-discovered from the repo root.")
    ap.add_argument("--run-date", default=None,
                    help="YYYY-MM-DD run/publish date: decides which open loops have MATURED "
                         "and which calendar events concluded in-window. Defaults to a date in "
                         "the filename, else today (UTC).")
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
        # data-mx pages declare their format via data-format (core convention)
        df = re.search(r'data-format="([^"]+)"', body_tag)
        if ds:
            fmt = normalize_format(ds.group(1))
        elif df:
            fmt = normalize_format(df.group(1))
        else:
            # Fallback for weekly: no data-special/data-format on body
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
    check_length_band(html, fmt, report)

    # ── Design-system-unification WP-0 (spec 2026-07-18) ──
    # F-14 scaffold-token + strategy-vocabulary checks run on EVERY issue
    # (visible prose only). Law-3 floors, Law-9 voice minimums, and the F-16
    # local-src rule apply to NEW-SYSTEM issues only (data-mx / data-skin
    # markers) — old-system archive issues are exempt by design.
    new_system = is_new_system(html)
    check_f14_scaffold_tokens(html, new_system, report)
    check_f14_strategy_vocab(html, report)
    if new_system:
        check_law3_word_floor(html, fmt, path, report)
        check_law9_voices(html, fmt, path, report)
        check_external_img_src(html, report)
    # Image-presence floor: markup-only, network-free — runs unconditionally,
    # including under --skip-image-urls and in offline sandboxes (A2).
    check_image_floor(html, fmt, report)

    # Holiday-only checks — LEGACY pages only. A data-mx page is built on the
    # unified core (no hol-/is-special vocabulary by design, F-13); it gets the
    # mx variety gate below instead, and its structure is gated by the rendered
    # measure/parity suite (tools/measure-issue.mjs + Part-5 gate).
    if fmt in HOLIDAY_FORMATS and not new_system:
        check_holiday_activation(html, fmt, multi_venue, report)
        check_holiday_components(html, report)
        if multi_venue:
            check_multi_venue(html, report)

    # Component-variety gate: mx vocabulary for data-mx pages (incl. holiday
    # formats), legacy class-group vocabulary for old-system specials.
    if new_system:
        check_mx_component_variety(html, fmt, report)
    elif fmt in SPECIAL_FORMATS and fmt not in HOLIDAY_FORMATS:
        check_special_component_variety(html, fmt, report)

    # ── Coverage-rebuild checks (SPEC docs/editorial-coverage-rebuild-SPEC-2026-07-26.md) ──
    # Folded INTO the existing two mechanical gates — gate 1 image checks, gate 2
    # markup contracts — per SPEC §0 (no fourth ship gate). See
    # run_coverage_checks() for the scope rules.
    try:
        run_coverage_checks(html, fmt, new_system, path, args.state, args.run_date, report)
    except ValueError as e:                      # bad --run-date: an invocation error
        print(f"ERROR: {e}")
        return 2

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
