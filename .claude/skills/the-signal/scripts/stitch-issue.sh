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
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# ─────────────────────────────────────────────────────────────────────────────
# Arg parsing
# ─────────────────────────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
  case "$1" in
    --plan)      PLAN_PATH="$2";   shift 2 ;;
    --build-dir) BUILD_DIR="$2";   shift 2 ;;
    --out)       OUT_PATH="$2";    shift 2 ;;
    *)           echo "Unknown arg: $1"; exit 1 ;;
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

python3 - \
  "$PLAN_PATH" "$CHAPTERS_DIR" "$TEMPLATE_DIR" "$CSS_DIR" "$JS_FILE" \
  "$OUT_PATH" "$CHAPTER_IDS_CSV" \
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

with open(plan_path) as f:
    plan = json.load(f)

assets = plan.get("assets", {})
scaffold_parts = assets.get("scaffold_parts_used", [])
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

# ── Assemble middle scaffold parts (everything between head and closing) ──
middle_parts = []
for part_name in scaffold_parts:
    # Skip head-open and closing — handled separately
    if part_name in ("00-head-open.html", "19-closing.html"):
        continue
    part_path = template_dir / part_name
    if part_path.exists():
        middle_parts.append(part_path.read_text(encoding="utf-8"))
    else:
        print(f"WARNING: Scaffold part '{part_name}' not found — skipping")

# ── Assemble chapter bodies ──
chapter_bodies = []
for ch_id in chapter_ids:
    ch_file = chapters_dir / f"{ch_id}.html"
    chapter_bodies.append(ch_file.read_text(encoding="utf-8"))

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

if issue_format_early in HOLIDAY_FORMATS:
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
        print("ERROR: No <body> tag after </head> — cannot activate holiday identity")
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
