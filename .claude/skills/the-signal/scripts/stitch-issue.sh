#!/usr/bin/env bash
# stitch-issue.sh — Deterministic chapter concatenation, scaffold wrapping,
# and CSS/JS injection for The Signal pipeline.
#
# Usage:
#   bash scripts/stitch-issue.sh \
#     --plan /tmp/signal-build/chapter-plan.json \
#     [--build-dir /tmp/signal-build] \
#     [--out signal_countdown_2026-06-15.html]
#
# Behaviour:
#   1. Reads chapter-plan.json (via python3 for JSON parsing)
#   2. Verifies all chapters/<chapter_id>.html files exist
#   3. Concatenates chapters in chapter_num order
#   4. Wraps in scaffold parts (from assets/template-parts/)
#   5. Injects CSS (assets/css/*.css alphabetical) and JS (assets/script.js)
#   6. Prints summary: chapter count, CSS bytes, JS bytes, output path
#
# Supports both placeholder conventions:
#   - <!-- INJECT:CSS --> / <!-- INJECT:JS --> (new pipeline)
#   - <style>/* PASTE ... */</style> / <script>/* ... */</script> (legacy template)
#
# NOTE: This script supersedes scripts/inject-assets.sh for pipeline runs.
# inject-assets.sh is kept for ad-hoc single-file edits outside the pipeline.
#
# Exit codes:
#   0 — success
#   1 — missing plan, missing chapter file, missing scaffold part, no CSS placeholder
#
# v8.11.0

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Defaults
# ─────────────────────────────────────────────────────────────────────────────

PLAN_PATH=""
BUILD_DIR="/tmp/signal-build"
OUT_PATH=""
ISSUE_NUMBER=""
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# ─────────────────────────────────────────────────────────────────────────────
# Arg parsing
# ─────────────────────────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
  case "$1" in
    --plan)         PLAN_PATH="$2";     shift 2 ;;
    --build-dir)    BUILD_DIR="$2";     shift 2 ;;
    --out)          OUT_PATH="$2";      shift 2 ;;
    --issue-number) ISSUE_NUMBER="$2";  shift 2 ;;
    *)              echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ -z "$PLAN_PATH" ]]; then
  PLAN_PATH="${BUILD_DIR}/chapter-plan.json"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Validate inputs
# ─────────────────────────────────────────────────────────────────────────────

if [[ ! -f "$PLAN_PATH" ]]; then
  echo "ERROR: Plan file not found: $PLAN_PATH"
  echo "       Run the Planner subagent (Phase 4) first, then the validator."
  exit 1
fi

CHAPTERS_DIR="${BUILD_DIR}/chapters"
TEMPLATE_DIR="${SKILL_DIR}/assets/template-parts"
CSS_DIR="${SKILL_DIR}/assets/css"
JS_FILE="${SKILL_DIR}/assets/script.js"

if [[ ! -d "$TEMPLATE_DIR" ]]; then
  echo "ERROR: Template parts directory not found: $TEMPLATE_DIR"
  exit 1
fi

if [[ ! -f "$JS_FILE" ]]; then
  echo "ERROR: JS file not found: $JS_FILE"
  exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# Parse plan with Python (stdlib only)
# ─────────────────────────────────────────────────────────────────────────────

echo "=== stitch-issue.sh: reading plan ==="

PLAN_DATA=$(python3 - "$PLAN_PATH" <<'PYEOF'
import json, sys

plan_path = sys.argv[1]
with open(plan_path) as f:
    plan = json.load(f)

meta = plan["issue_meta"]
chapters = sorted(plan["chapters"], key=lambda c: c["chapter_num"])
scaffold_parts = plan["assets"].get("scaffold_parts_used", [])
css_marker = plan["assets"].get("css_inject_marker", "<!-- INJECT:CSS -->")
js_marker  = plan["assets"].get("js_inject_marker",  "<!-- INJECT:JS -->")

# Print format usable by bash
print(f"FORMAT={meta['format']}")
print(f"DATE={meta['date']}")
print(f"SPECIAL_ID={meta.get('special_id') or ''}")
print(f"EXECUTION_MODE={meta['execution_mode']}")
print(f"CSS_MARKER={css_marker}")
print(f"JS_MARKER={js_marker}")
print(f"SCAFFOLD_PARTS={','.join(scaffold_parts)}")
# Each chapter: NUM:ID
for ch in chapters:
    print(f"CHAPTER={ch['chapter_num']}:{ch['chapter_id']}")
PYEOF
)

# Parse outputs safely (avoid eval on lines with spaces like HTML comments)
FORMAT=$(echo "$PLAN_DATA" | grep '^FORMAT=' | cut -d= -f2-)
DATE=$(echo "$PLAN_DATA" | grep '^DATE=' | cut -d= -f2-)
SPECIAL_ID=$(echo "$PLAN_DATA" | grep '^SPECIAL_ID=' | cut -d= -f2-)
EXECUTION_MODE=$(echo "$PLAN_DATA" | grep '^EXECUTION_MODE=' | cut -d= -f2-)
CSS_MARKER=$(echo "$PLAN_DATA" | grep '^CSS_MARKER=' | cut -d= -f2-)
JS_MARKER=$(echo "$PLAN_DATA" | grep '^JS_MARKER=' | cut -d= -f2-)
SCAFFOLD_PARTS=$(echo "$PLAN_DATA" | grep '^SCAFFOLD_PARTS=' | cut -d= -f2-)

# Holiday formats (countdown, field_guide/field-guide) MUST NOT ship the legacy
# default-chrome scaffold parts (01-masthead.html, 03-cover.html, 18-footer.html).
# Holiday Identity tier 11 styles .hol-masthead / .hol-cover / .hol-footer-row
# but does NOT hide the legacy .mast / header.cover / footer.footer — those
# would still render alongside the holiday equivalents, producing a duplicate
# masthead, duplicate cover, and duplicate footer in the same issue.
# Force scaffold_parts_used to only head + closing on holiday formats regardless
# of what the planner specified.
HOLIDAY_FORMATS_RE="^(countdown|field_guide|field-guide)$"
if [[ "$FORMAT" =~ $HOLIDAY_FORMATS_RE ]]; then
  ORIGINAL_PARTS="$SCAFFOLD_PARTS"
  SCAFFOLD_PARTS="00-head-open.html,19-closing.html"
  if [[ "$ORIGINAL_PARTS" != "$SCAFFOLD_PARTS" ]]; then
    echo "  HOLIDAY FORMAT — overrode scaffold_parts_used:"
    echo "    plan said:   $ORIGINAL_PARTS"
    echo "    stitcher uses: $SCAFFOLD_PARTS"
    echo "    (legacy .mast / header.cover / .footer dropped — would duplicate .hol-* chrome)"
  fi
fi

# v8.24.3: non-holiday special editions get the wax-stamp seal scaffold part.
# 02-wax-seal.html supplies the rotating seal + film-grain overlay AND opens the
# centred <div class="mag"> paper sheet that 19-closing.html closes. Without it,
# specials had no sheet (full-bleed flat paper) and a stray </div>. Inject it
# right after 00-head-open.html if the plan didn't list it.
NONHOLIDAY_SPECIAL_RE="^(deep_dive|versus|rewind|season_review|starter_kit|shortlist|next|lookahead)$"
if [[ "$FORMAT" =~ $NONHOLIDAY_SPECIAL_RE ]]; then
  if [[ ",$SCAFFOLD_PARTS," != *",02-wax-seal.html,"* ]]; then
    if [[ ",$SCAFFOLD_PARTS," == *",00-head-open.html,"* ]]; then
      SCAFFOLD_PARTS="${SCAFFOLD_PARTS/00-head-open.html,/00-head-open.html,02-wax-seal.html,}"
    else
      SCAFFOLD_PARTS="02-wax-seal.html,$SCAFFOLD_PARTS"
    fi
    echo "  NON-HOLIDAY SPECIAL — injected 02-wax-seal.html (opens .mag sheet + seal + grain): $SCAFFOLD_PARTS"
  fi
fi

# Collect chapters in order
CHAPTER_IDS_ORDERED=()
while IFS= read -r line; do
  if [[ "$line" == CHAPTER=* ]]; then
    val="${line#CHAPTER=}"
    id="${val#*:}"
    CHAPTER_IDS_ORDERED+=("$id")
  fi
done <<< "$PLAN_DATA"

echo "  Format:    $FORMAT"
echo "  Date:      $DATE"
echo "  Chapters:  ${#CHAPTER_IDS_ORDERED[@]} ($(IFS=', '; echo "${CHAPTER_IDS_ORDERED[*]}"))"
echo "  Mode:      $EXECUTION_MODE"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Verify all chapter HTML files exist
# ─────────────────────────────────────────────────────────────────────────────

echo "=== Verifying chapter files ==="
MISSING_CHAPTERS=()
for id in "${CHAPTER_IDS_ORDERED[@]}"; do
  ch_file="${CHAPTERS_DIR}/${id}.html"
  if [[ ! -f "$ch_file" ]]; then
    MISSING_CHAPTERS+=("$ch_file")
    echo "  MISSING: $ch_file"
  else
    lines=$(wc -l < "$ch_file")
    echo "  OK: ${id}.html ($lines lines)"
  fi
done

if [[ ${#MISSING_CHAPTERS[@]} -gt 0 ]]; then
  echo ""
  echo "ERROR: ${#MISSING_CHAPTERS[@]} chapter file(s) missing. Cannot stitch until all writers complete."
  exit 1
fi
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Verify scaffold parts
# ─────────────────────────────────────────────────────────────────────────────

echo "=== Verifying scaffold parts ==="
MISSING_PARTS=()
IFS=',' read -ra PARTS <<< "${SCAFFOLD_PARTS:-}"
for part in "${PARTS[@]}"; do
  part_file="${TEMPLATE_DIR}/${part}"
  if [[ ! -f "$part_file" ]]; then
    MISSING_PARTS+=("$part_file")
    echo "  MISSING: $part"
  else
    echo "  OK: $part"
  fi
done

# Always check 00-head-open.html and 19-closing.html
for required_part in "00-head-open.html" "19-closing.html"; do
  if [[ ! -f "${TEMPLATE_DIR}/${required_part}" ]]; then
    MISSING_PARTS+=("${TEMPLATE_DIR}/${required_part}")
    echo "  MISSING (required): $required_part"
  fi
done

if [[ ${#MISSING_PARTS[@]} -gt 0 ]]; then
  echo ""
  echo "ERROR: ${#MISSING_PARTS[@]} scaffold part(s) missing."
  exit 1
fi
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Determine output path
# ─────────────────────────────────────────────────────────────────────────────

if [[ -z "$OUT_PATH" ]]; then
  if [[ "$FORMAT" == "weekly" ]]; then
    OUT_PATH="signal_weekly_${DATE}.html"
  else
    SLUG="${FORMAT//_/-}"
    if [[ -n "$SPECIAL_ID" ]]; then
      OUT_PATH="signal_${SLUG}_${DATE}.html"
    else
      OUT_PATH="signal_${SLUG}_${DATE}.html"
    fi
  fi
fi

echo "=== Building stitched HTML ==="
echo "  Output: $OUT_PATH"

# ─────────────────────────────────────────────────────────────────────────────
# Stitch: scaffold + chapters (Python for reliable multi-line handling)
# ─────────────────────────────────────────────────────────────────────────────

CHAPTER_IDS_CSV=$(IFS=','; echo "${CHAPTER_IDS_ORDERED[*]}")

# Pass SCAFFOLD_PARTS to Python as argv[8] so the bash-level holiday override
# (which drops 01-masthead.html / 03-cover.html / 18-footer.html on holiday
# formats) reaches the assembly step. Without this, Python re-reads the plan
# and reuses the un-overridden list.
# argv[9] = ISSUE_NUMBER (string, may be empty) — substituted into footer [N]
# placeholder. Date-range and date substitution computed from plan's meta.date.
python3 - \
  "$PLAN_PATH" "$CHAPTERS_DIR" "$TEMPLATE_DIR" "$CSS_DIR" "$JS_FILE" \
  "$OUT_PATH" "$CHAPTER_IDS_CSV" "$SCAFFOLD_PARTS" "$ISSUE_NUMBER" \
  <<'PYEOF'

import sys, json, re
from pathlib import Path

plan_path    = Path(sys.argv[1])
chapters_dir = Path(sys.argv[2])
template_dir = Path(sys.argv[3])
css_dir      = Path(sys.argv[4])
js_file      = Path(sys.argv[5])
out_path     = Path(sys.argv[6])
chapter_ids  = sys.argv[7].split(',') if sys.argv[7] else []
scaffold_parts_override = sys.argv[8].split(',') if len(sys.argv) > 8 and sys.argv[8] else None
# v8.18.1 — issue number for footer [N] substitution; empty means leave as-is
# (orchestrator should pass --issue-number; if absent, validate-issue.py will
# catch the unresolved placeholder).
issue_number_str = sys.argv[9] if len(sys.argv) > 9 else ""

with open(plan_path) as f:
    plan = json.load(f)

assets = plan.get("assets", {})
# Use the bash-resolved override list (which may have been modified by the
# holiday-format rule above) in preference to the raw plan value.
scaffold_parts = scaffold_parts_override if scaffold_parts_override is not None \
                 else assets.get("scaffold_parts_used", [])
css_marker = assets.get("css_inject_marker", "<!-- INJECT:CSS -->")
js_marker  = assets.get("js_inject_marker",  "<!-- INJECT:JS -->")

# ── Assemble CSS ──
if css_dir.is_dir():
    css_files = sorted(css_dir.glob("*.css"))
    css_blocks = [f.read_text(encoding="utf-8") for f in css_files]
    css_content = "\n".join(css_blocks)
    css_files_used = len(css_files)
else:
    # Legacy fallback
    legacy = plan_path.parent.parent / "assets" / "styles.css"
    if legacy.exists():
        css_content = legacy.read_text(encoding="utf-8")
        css_files_used = 1
    else:
        print("ERROR: No CSS found in assets/css/ and no legacy assets/styles.css")
        sys.exit(1)

js_content = js_file.read_text(encoding="utf-8")

# ── Build scaffold head (00-head-open.html) ──
head_open = (template_dir / "00-head-open.html").read_text(encoding="utf-8")
closing   = (template_dir / "19-closing.html").read_text(encoding="utf-8")

# ── v8.18.1 — Scaffold placeholder substitution ──
# 00-head-open.html ships with `<title>The Signal — [DATE RANGE]</title>` and
# 18-footer.html ships with `Issue #[N] · [Date]`. These are structural
# placeholders the writers don't touch; the stitcher owns the substitution.
# Date-range format: "DD–DD Mon YYYY" (e.g. "18–24 May 2026") for weeklies;
# for specials, use the issue date alone (e.g. "24 May 2026") since specials
# don't span a week.
def _compute_date_range(date_str, fmt):
    """Return ('date range', 'pretty date') tuple for placeholder substitution."""
    from datetime import datetime, timedelta
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return ("[DATE RANGE]", "[Date]")  # leave as-is; gate will catch
    pretty_date = d.strftime("%-d %B %Y")  # e.g. "24 May 2026"
    if fmt == "weekly":
        start = d - timedelta(days=6)
        if start.month == d.month:
            range_str = f"{start.day}–{d.day} {d.strftime('%B %Y')}"
        else:
            range_str = f"{start.strftime('%-d %b')}–{d.strftime('%-d %b %Y')}"
    else:
        range_str = pretty_date
    return (range_str, pretty_date)

_issue_meta_local = plan.get("issue_meta", {}) if isinstance(plan, dict) else {}
_issue_date = _issue_meta_local.get("date", "")
_issue_fmt  = _issue_meta_local.get("format", "weekly")
_range_str, _pretty_date = _compute_date_range(_issue_date, _issue_fmt)
head_open = head_open.replace("[DATE RANGE]", _range_str)

def _substitute_footer_placeholders(text):
    """Replace [N], [Date], [DATE RANGE], [YEAR] in footer / scaffold parts."""
    text = text.replace("[DATE RANGE]", _range_str)
    text = text.replace("[Date]", _pretty_date)
    text = text.replace("[YEAR]", _pretty_date.split()[-1] if _pretty_date else "")
    if issue_number_str:
        text = text.replace("[N]", issue_number_str)
    # Wax-seal issue tag. Weeklies are numbered (Nº 011); specials are not, so
    # show a short format label instead of a literal [NNN] placeholder.
    if _issue_fmt == "weekly" and issue_number_str:
        text = text.replace("[NNN]", str(issue_number_str).zfill(3))
    else:
        _fmt_label = {
            "deep_dive": "Deep Dive", "versus": "Versus", "rewind": "Rewind",
            "season_review": "Season", "starter_kit": "Starter Kit",
            "shortlist": "Shortlist", "next": "Next", "lookahead": "Lookahead",
        }.get(_issue_fmt, "Special")
        text = text.replace("Nº [NNN]", _fmt_label)
        text = text.replace("[NNN]", "")
    return text

# ── Assemble middle scaffold parts (everything between head and closing) ──
middle_parts = []
for part_name in scaffold_parts:
    # Skip head-open and closing — handled separately
    if part_name in ("00-head-open.html", "19-closing.html"):
        continue
    part_path = template_dir / part_name
    if part_path.exists():
        middle_parts.append(_substitute_footer_placeholders(part_path.read_text(encoding="utf-8")))
    else:
        print(f"WARNING: Scaffold part '{part_name}' not found — skipping")

# ── Assemble chapter bodies ──
# v8.27 reality: cover/navigator/foreword/colophon/footer are full writer-agent
# chapters (not scaffold parts), and writers leave the [N]/[DATE RANGE]/[Date]/
# [YEAR] placeholders intact for the stitcher to own. So the same substitution
# applied to scaffold parts must run on chapter bodies too — otherwise the cover
# and footer ship the literal placeholders (caught by validate-issue.py).
chapter_bodies = []
for ch_id in chapter_ids:
    ch_file = chapters_dir / f"{ch_id}.html"
    chapter_bodies.append(_substitute_footer_placeholders(ch_file.read_text(encoding="utf-8")))

# ── Holiday half-wrap reorganisation (v8.13.5) ──
# On holiday + multi_venue issues, the .hol-half--N wrapper must contain
# the opener AND every subsequent venue chapter so they share the half's
# painted ground (tier 11/12 paints background on .hol-half--{one,two}).
# Writers naturally produce each chapter as a self-contained <section>,
# so we walk the chapter stream and merge same-venue runs inside one
# half wrapper. This is the structural counterpart to the scaffold
# override above — without it, only the half-opener gets the venue
# ground and the rest of the venue's chapters render against the body
# default.
issue_meta_pre = plan.get("issue_meta", {})
issue_format_pre = issue_meta_pre.get("format", "").lower().replace("_", "-")
multi_venue_pre = bool(issue_meta_pre.get("multi_venue", False))
if issue_format_pre in {"countdown", "field-guide"} and multi_venue_pre:
    HALF_OPEN_RE = re.compile(
        r'<section\b[^>]*\bclass="[^"]*\bhol-half\b[^"]*\bhol-half--(?P<half>one|two)\b[^"]*"[^>]*(?:\bdata-venue="(?P<venue>[^"]+)")?[^>]*>',
        re.IGNORECASE,
    )
    # Pull data-venue from each chapter body for stream-level pairing
    def venue_of(body):
        m = re.search(r'<section\b[^>]*\bdata-venue="([^"]+)"', body, re.IGNORECASE)
        return m.group(1).strip().lower() if m else None
    def is_half_opener(body):
        return bool(HALF_OPEN_RE.search(body))
    def strip_trailing_close(body):
        # Strip trailing </section> and the </div> that closes hol-half__inner.
        # The opener leaves the wrapper OPEN — subsequent venue chapters render
        # inside it. The matching close is appended to the LAST chapter of the
        # same venue's run.
        b = body.rstrip()
        if b.endswith('</section>'):
            b = b[:-len('</section>')].rstrip()
        if b.endswith('</div>'):
            b = b[:-len('</div>')].rstrip()
        return b + "\n"
    # Walk chapter_bodies, marking which need opener-strip and which need
    # half-close appended. We do TWO passes: first identify run boundaries,
    # then rewrite.
    venues_per_chapter = [venue_of(b) for b in chapter_bodies]
    half_opener_idx    = [is_half_opener(b) for b in chapter_bodies]
    # For each half-opener, find the index of the LAST consecutive chapter
    # with matching venue (could be the opener itself if no follow-ups).
    rewritten = list(chapter_bodies)
    n = len(chapter_bodies)
    i = 0
    transforms = 0
    while i < n:
        if half_opener_idx[i] and venues_per_chapter[i]:
            v = venues_per_chapter[i]
            # Find end of run
            end = i
            j = i + 1
            while j < n and venues_per_chapter[j] == v:
                end = j
                j += 1
            if end > i:
                # Strip the opener's closing </div></section> so the wrapper
                # stays open across the run.
                rewritten[i] = strip_trailing_close(rewritten[i])
                # Append matching close to the LAST chapter in the run.
                rewritten[end] = rewritten[end].rstrip() + "\n\n  </div>\n</section>\n"
                transforms += 1
            i = j
        else:
            i += 1
    if transforms:
        print(f"  HOLIDAY HALF-WRAP: nested {transforms} venue run(s) inside their .hol-half--N wrappers")
        chapter_bodies = rewritten

# ── Compose full HTML ──
# Structure: head_open → [middle scaffold parts] → [chapters] → closing
html_parts = [head_open] + middle_parts + chapter_bodies + [closing]
html = "\n".join(html_parts)

# ── Holiday activation gates (v8.13.3) ──
# Scans CHAPTER MARKUP ONLY (not the inlined stylesheet or JS, both of
# which legitimately reference .sp-* selectors and example HTML inside
# comment blocks).
issue_meta_early = plan.get("issue_meta", {})
issue_format_early = issue_meta_early.get("format", "").lower().replace("_", "-")
HOLIDAY_FORMATS = {"countdown", "field-guide"}
SPECIAL_FORMATS = {"countdown", "field-guide", "deep-dive", "versus", "rewind",
                   "season-review", "starter-kit", "shortlist", "next", "lookahead"}

# v8.22.12 — activate body for ALL special formats, not just holiday.
# The non-holiday v8.21 CSS bundle (23- through 32-) is scoped to
# `body.is-special:not([data-special="countdown"]):not([data-special="field-guide"])`,
# so without the body activation a deep-dive / versus / rewind / etc renders
# entirely unstyled (paper background, no chapter chrome, no cover styling).
# The 24 May 2026 WW1 Deep Dive shipped this way before the gate was added.
if issue_format_early in SPECIAL_FORMATS:
    # Activation rewrite — stamp the body tag deterministically.
    #
    # CRITICAL: anchor to </head>. The scaffold (00-head-open.html) contains
    # an HTML comment with an example body tag string ('<body class="is-special"
    # data-special="countdown"> (or field-guide).'). A naive `<body\b[^>]*>`
    # regex with count=1 matches that comment example FIRST and leaves the
    # real <body> bare. We find </head> first, then the next <body> after it.
    head_end_match = re.search(r'</head\s*>', html, re.IGNORECASE)
    if not head_end_match:
        print("ERROR: No </head> tag found in scaffold — cannot locate real <body>")
        sys.exit(1)
    body_search = re.search(r'<body\b[^>]*>', html[head_end_match.end():], re.IGNORECASE)
    if not body_search:
        print("ERROR: No <body> tag after </head> — cannot activate special-edition identity")
        sys.exit(1)
    body_abs_start = head_end_match.end() + body_search.start()
    body_abs_end   = head_end_match.end() + body_search.end()
    multi_venue_flag = bool(issue_meta_early.get("multi_venue", False))
    body_attrs = f'class="is-special" data-special="{issue_format_early}"'
    if multi_venue_flag:
        body_attrs += ' data-multi-venue="true"'
    desired_body = f'<body {body_attrs}>'
    html = html[:body_abs_start] + desired_body + html[body_abs_end:]
    mv_note = " + data-multi-venue=true" if multi_venue_flag else ""
    print(f"ACTIVATION: rewrote real <body> (after </head>) to is-special + data-special={issue_format_early}{mv_note}")

# Holiday-only gates: banned vocabulary scan, scaffold override, etc.
if issue_format_early in HOLIDAY_FORMATS:

    # Build the gate scan target: ONLY the concatenated chapter bodies.
    # Scaffolds (00-head-open.html / 19-closing.html) are clean by spec.
    # CSS and JS haven't been injected yet at this point in the script.
    chapter_scan_text = "\n".join(chapter_bodies)

    # Each pattern targets a single class-attribute token. The (?<!hol-)
    # lookbehind allows `hol-unmissable` and `hol-unmissable--reverse`
    # to pass while flagging bare `unmissable`.
    BANNED_HOLIDAY_PATTERNS = [
        ('sp-chapter-gate',   r'class="(?:[^"]* )?sp-chapter-gate\b'),
        ('sp-spread',         r'class="(?:[^"]* )?sp-spread\b'),
        ('sp-pull-break',     r'class="(?:[^"]* )?sp-pull-break\b'),
        ('sp-marginalia',     r'class="(?:[^"]* )?sp-marginalia\b'),
        ('sp-brief',          r'class="(?:[^"]* )?sp-brief\b'),
        ('sp-dash',           r'class="(?:[^"]* )?sp-dash\b'),
        ('sp-chapter-chrome', r'class="(?:[^"]* )?sp-chapter-chrome\b'),
        ('unmissables',       r'class="(?:[^"]* )?(?<!hol-)unmissables\b'),
        ('unmissable',        r'class="(?:[^"]* )?(?<!hol-)unmissable\b'),
    ]
    violations = []
    for token, pat in BANNED_HOLIDAY_PATTERNS:
        hits = len(re.findall(pat, chapter_scan_text))
        if hits > 0:
            violations.append(f"{token} — {hits} occurrence(s)")
    if violations:
        print("")
        print("═══ HOLIDAY ACTIVATION GATE FAILED ═══")
        print(f"Issue format is '{issue_format_early}' (holiday identity) but the chapter HTML")
        print("contains banned default-chrome vocabulary. Tier 11 (holiday-identity.css)")
        print("HIDES these components on holiday issues — they would render as blank.")
        print("")
        print("See references/pre-flight.md RT-13 and references/spec/specials.md")
        print("§ holiday-identity for the .hol-* vocabulary map.")
        print("")
        print("Violations (in chapter content):")
        for v in violations:
            print(f"  • {v}")
        print("")
        print("Action: re-run Phase 5 writer subagents with the holiday vocabulary brief.")
        sys.exit(1)

    # Positive check: at least one .hol-half must be present in chapter content.
    if 'class="hol-half ' not in chapter_scan_text and \
       'class="hol-half"' not in chapter_scan_text:
        print("")
        print("═══ HOLIDAY STRUCTURE GATE FAILED ═══")
        print(f"Issue format is '{issue_format_early}' but no .hol-half element found.")
        print("Every holiday issue must have at least one .hol-half--one (and a")
        print(".hol-half--two + .hol-transit for multi-venue issues).")
        sys.exit(1)

# ── Weekly-format gate: ban the SPECIAL vocabulary in weekly issues ──
# Mirror of the holiday gate above, in the other direction. The .sp-*
# editorial vocabulary (.sp-spread, .sp-marginalia, .sp-pullquote-huge,
# .sp-rail, .sp-margin, .sp-brief-kicker, .sp-spread-body, .sp-footer*,
# etc.) is defined only inside `body.is-special:not(holiday)` selectors.
# On a standard weekly (no .is-special on body) those rules don't match —
# the elements render unstyled.
#
# v8.22.7 hardening (after May 24 2026 rebuild leaked classes through):
#   - Added sp-footer* (v8.21 special-edition footer; missed in v8.22.5).
#   - Switched from sp-* token list to "any sp-* class" with a narrow
#     allowlist of universal/JS-artifact tokens (sp-chapter-beads,
#     sp-wipe-layer, sp-word, sp-fade). The deny-list approach kept
#     missing new tokens; the allow-list approach catches them by default.
#   - Scan target widened from chapter_bodies only to chapter_bodies +
#     ALL non-scaffold-template substitutions. Anything a writer adds is
#     in scope. (The scaffold parts themselves are checked against the
#     allowlist only — they shouldn't contain editorial vocabulary.)
if issue_format_early in {"", "weekly"}:
    # Allowlisted sp-* tokens that are LEGITIMATE on weeklies:
    #   - sp-chapter-beads: universal chapter-progress strip (PR #110 follow-up)
    #   - sp-wipe-layer: JS-injected empty <span> markers, no visual effect
    #   - sp-word:        JS-injected per-word spans for stagger reveal
    #   - sp-fade:        small fade utility class used by motion JS
    ALLOWED_SP_TOKENS = {
        'sp-chapter-beads',
        'sp-wipe-layer',
        'sp-word',
        'sp-fade',
    }

    # Scan target: ALL chapter bodies + the stitcher-controlled middle
    # parts (everything that isn't head/closing scaffold). Writers can put
    # sp-* in any of these; only the head/closing templates are skipped
    # since those are stitcher-owned and known clean.
    weekly_scan_text = "\n".join(chapter_bodies + middle_parts)

    # Find every sp-* token. Filter out the allowlist.
    sp_class_re = re.compile(r'class="[^"]*?\b(sp-[a-z][a-z0-9-]*)\b', re.IGNORECASE)
    found = {}
    for m in sp_class_re.finditer(weekly_scan_text):
        tok = m.group(1)
        if tok in ALLOWED_SP_TOKENS:
            continue
        found[tok] = found.get(tok, 0) + 1

    if found:
        print("")
        print("═══ WEEKLY-FORMAT GATE FAILED ═══")
        print("Issue format is 'weekly' but the chapter / scaffold HTML uses the")
        print("special-edition .sp-* vocabulary. Those classes are scoped to")
        print("body.is-special selectors and are undefined on weeklies — the")
        print("elements render unstyled.")
        print("")
        print("This is the May 24 2026 bug: writers reached for specials.md by")
        print("mistake instead of using the weekly section-component vocabulary")
        print("(.split-60-40, .sidebar, .stat-bar, .dyk, .also-cards, .pull-quote,")
        print("etc.) and the cascade silently dropped the styling.")
        print("")
        print("Disallowed tokens found:")
        for token, count in sorted(found.items(), key=lambda kv: -kv[1]):
            print(f"  • {token} — {count} occurrence(s)")
        print("")
        print(f"Allowlist (legitimate on weeklies): {sorted(ALLOWED_SP_TOKENS)}")
        print("")
        print("Action: re-run Phase 5 writer subagents with explicit weekly-format")
        print("vocabulary brief — see SKILL.md Phase 5 + references/component-")
        print("contracts.md § Weekly. The .sp-* vocabulary is for SPECIALS ONLY.")
        sys.exit(1)

# ── Inject CSS — support both placeholder conventions ──
# NOTE: Use plain string replace (not re.sub) — CSS content contains backslash
# patterns that confuse regex replacement (e.g. \w, \n inside @keyframes/selectors).
css_tag = f"<style>\n{css_content}\n</style>"

if css_marker in html:
    html = html.replace(css_marker, css_tag, 1)
else:
    # Legacy template placeholder: <style>/* PASTE contents of ... */</style>
    # Find the legacy block with a regex search but replace with plain str.replace
    legacy_css_match = re.search(r'<style>[^<]*PASTE[^<]*</style>', html, re.DOTALL)
    if legacy_css_match:
        legacy_block = legacy_css_match.group(0)
        html = html.replace(legacy_block, css_tag, 1)
    else:
        # Last resort: inject before </head>
        if '</head>' in html:
            html = html.replace('</head>', css_tag + '\n</head>', 1)
            print("WARNING: No CSS placeholder found — injected before </head>")
        else:
            print("ERROR: Cannot find CSS placeholder or </head> in scaffold")
            sys.exit(1)

# ── Inject JS — support both placeholder conventions ──
# Same approach: search with regex to locate block, replace with plain str.replace
js_tag = f"<script>\n{js_content}\n</script>"

if js_marker in html:
    html = html.replace(js_marker, js_tag, 1)
else:
    # Legacy placeholder: <script>/* See assets/script.js */</script>
    legacy_js_match = re.search(r'<script>[^<]*See assets/script\.js[^<]*</script>', html, re.DOTALL)
    if legacy_js_match:
        legacy_block = legacy_js_match.group(0)
        html = html.replace(legacy_block, js_tag, 1)
    else:
        # Last resort: inject before </body>
        if '</body>' in html:
            html = html.replace('</body>', js_tag + '\n</body>', 1)
            print("WARNING: No JS placeholder found — injected before </body>")
        else:
            print("ERROR: Cannot find JS placeholder or </body> in scaffold")
            sys.exit(1)

# ── Inject "← The Signal" back link after <body> ──
# Added v8.22.15: PR #89 originally added this block to every issue via a
# one-off direct-write script. That script was never integrated into the
# stitch pipeline, so issues stitched after the older HTMLs were written
# shipped without the back link (24 May 2026 weekly, 26 May 2026 Deep Dive).
# This step runs every stitch and is idempotent — if a scaffold ever starts
# including the block natively, the marker check below skips re-injection.
if '<!-- the-signal:back -->' not in html:
    # template_dir (argv[3]) is the bash-resolved assets/template-parts path;
    # do NOT recompute from __file__ — this block runs via `python3 - <<PY`
    # (stdin), so __file__ is "<stdin>" and resolve() makes it cwd-relative,
    # producing the wrong path (.claude/skills/assets instead of
    # .claude/skills/the-signal/assets). Use the already-correct template_dir.
    back_link_path = template_dir / "back-link.html"
    if back_link_path.exists():
        back_link_block = back_link_path.read_text(encoding="utf-8").rstrip() + "\n"
        # Reuse the </head>-anchored body finder from the activation rewrite —
        # the scaffold contains an example <body> string inside an HTML comment,
        # so naive regex matching grabs the wrong one. Find </head> first.
        bl_head_match = re.search(r'</head\s*>', html, re.IGNORECASE)
        if not bl_head_match:
            print("ERROR: No </head> tag found — cannot inject back link")
            sys.exit(1)
        bl_body_search = re.search(r'<body\b[^>]*>', html[bl_head_match.end():], re.IGNORECASE)
        if not bl_body_search:
            print("ERROR: No <body> tag after </head> — cannot inject back link")
            sys.exit(1)
        bl_insert_at = bl_head_match.end() + bl_body_search.end()
        html = html[:bl_insert_at] + "\n" + back_link_block + html[bl_insert_at:]
        print("BACK LINK: injected after <body>")
    else:
        print(f"WARNING: back-link template not found at {back_link_path} — skipping")
else:
    print("BACK LINK: marker already present in scaffold, skipping injection")

# ── Write output ──
out_path.write_text(html, encoding="utf-8")

# ── Verify injection succeeded ──
final = out_path.read_text(encoding="utf-8")

checks = []
if css_marker in final:
    checks.append(f"FAIL: CSS placeholder '{css_marker}' still present — injection failed")
if js_marker in final:
    checks.append(f"FAIL: JS placeholder '{js_marker}' still present — injection failed")
if '<style>' not in final:
    checks.append("FAIL: No <style> tag in output — CSS not injected")
if '<script>' not in final:
    checks.append("FAIL: No <script> tag in output — JS not injected")
# Back link ("Return to The Signal" pill) must have landed. The injection step
# above is the only thing that adds it; verifying it here turns a silent miss
# into a hard stitch failure (the gap that shipped 3 issues without the button).
if '<!-- the-signal:back -->' not in final or 'signal-back-to-archive' not in final:
    checks.append("FAIL: 'Return to The Signal' back link missing from output — injection did not land")

if checks:
    for c in checks:
        print(c)
    sys.exit(1)

css_bytes = len(css_content.encode('utf-8'))
js_bytes  = len(js_content.encode('utf-8'))
total_bytes = len(final.encode('utf-8'))

print(f"  Chapters stitched: {len(chapter_ids)}")
print(f"  CSS injected:      {css_bytes:,} bytes ({css_files_used} file(s))")
print(f"  JS injected:       {js_bytes:,} bytes")
print(f"  Output size:       {total_bytes:,} bytes ({total_bytes/1024:.1f} KB)")
print(f"  Output path:       {out_path}")

PYEOF

echo ""
echo "=== DONE ==="
echo "  Stitched issue: $OUT_PATH"
