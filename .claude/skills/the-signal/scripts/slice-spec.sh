#!/usr/bin/env bash
# slice-spec.sh — Deterministically slices references/editorial-spec.md into
# role-targeted files under references/spec/, using HEADER-ANCHORED extraction.
#
# v8.16 — rewritten to be robust to line-number drift. Each declared slice
# names a Markdown heading (H2 by default, or H3 with `h3:` prefix) and the
# extractor pulls content from that heading to the next heading at the same
# level. No hardcoded line ranges anywhere.
#
# Run: bash scripts/slice-spec.sh [path-to-spec] [out-dir]
# Idempotent: safe to re-run after editorial-spec.md edits.

set -euo pipefail

SPEC="${1:-$(dirname "$0")/../references/editorial-spec.md}"
OUT_DIR="${2:-$(dirname "$0")/../references/spec}"

SPEC="$(realpath "$SPEC")"
OUT_DIR="$(realpath "$OUT_DIR")"

mkdir -p "$OUT_DIR/global" "$OUT_DIR/weekly" "$OUT_DIR/specials" \
         "$OUT_DIR/formats" "$OUT_DIR/triggers"

TOTAL_LINES=$(wc -l < "$SPEC")
written=0

# ─────────────────────────────────────────────────────────────────────────────
# Heading extractor.
#
# extract_heading <outfile> <H2-heading-text>
#   Extract content from "## <heading-text>" up to (but not including) the
#   next "## " heading. Heading match is exact-prefix on the text after "## ".
#
# extract_h3 <outfile> <H3-heading-text>
#   Same, but for "### <heading>" up to the next "### " or "## ".
#
# extract_multi <outfile> <h2|h3> <heading-1> <heading-2> ...
#   Extract multiple headings and concatenate into one outfile.
#
# Headings are matched case-sensitively against the exact text after the
# "## " (or "### "). Empty result is a hard error — fail fast on spec drift.
# ─────────────────────────────────────────────────────────────────────────────

extract_heading() {
  local outfile="$1"
  local heading="$2"
  mkdir -p "$(dirname "$outfile")"
  awk -v h="$heading" '
    BEGIN { inside = 0 }
    /^## / {
      if (inside) { exit }
      stripped = $0
      sub(/^## /, "", stripped)
      if (stripped == h) { inside = 1; print; next }
    }
    inside { print }
  ' "$SPEC" > "$outfile"
  local count=$(wc -l < "$outfile")
  if [ "$count" -lt 2 ]; then
    echo "  FAIL: $outfile — heading '## $heading' not found in spec (only $count lines extracted)"
    return 1
  fi
  written=$(( written + 1 ))
  echo "  wrote: $outfile ($count lines, anchor='## $heading')"
}

extract_h3() {
  local outfile="$1"
  local heading="$2"
  mkdir -p "$(dirname "$outfile")"
  awk -v h="$heading" '
    BEGIN { inside = 0 }
    /^### / {
      if (inside) { exit }
      stripped = $0
      sub(/^### /, "", stripped)
      if (stripped == h) { inside = 1; print; next }
    }
    /^## / { if (inside) { exit } }
    inside { print }
  ' "$SPEC" > "$outfile"
  local count=$(wc -l < "$outfile")
  if [ "$count" -lt 2 ]; then
    echo "  FAIL: $outfile — heading '### $heading' not found in spec (only $count lines extracted)"
    return 1
  fi
  written=$(( written + 1 ))
  echo "  wrote: $outfile ($count lines, anchor='### $heading')"
}

# Concatenate multiple H2 sections into one outfile.
# Usage: extract_h2_multi <outfile> "Heading 1" "Heading 2" ...
extract_h2_multi() {
  local outfile="$1"; shift
  mkdir -p "$(dirname "$outfile")"
  : > "$outfile"
  for h in "$@"; do
    awk -v h="$h" '
      BEGIN { inside = 0 }
      /^## / {
        if (inside) { exit }
        stripped = $0
        sub(/^## /, "", stripped)
        if (stripped == h) { inside = 1; print; next }
      }
      inside { print }
    ' "$SPEC" >> "$outfile"
    echo "" >> "$outfile"
  done
  local count=$(wc -l < "$outfile")
  if [ "$count" -lt 2 ]; then
    echo "  FAIL: $outfile — none of the requested H2 headings matched"
    return 1
  fi
  written=$(( written + 1 ))
  echo "  wrote: $outfile ($count lines, concatenated $# H2 sections)"
}

# Concatenate multiple H3 sections into one outfile.
extract_h3_multi() {
  local outfile="$1"; shift
  mkdir -p "$(dirname "$outfile")"
  : > "$outfile"
  for h in "$@"; do
    awk -v h="$h" '
      BEGIN { inside = 0 }
      /^### / {
        if (inside) { exit }
        stripped = $0
        sub(/^### /, "", stripped)
        if (stripped == h) { inside = 1; print; next }
      }
      /^## / { if (inside) { exit } }
      inside { print }
    ' "$SPEC" >> "$outfile"
    echo "" >> "$outfile"
  done
  local count=$(wc -l < "$outfile")
  if [ "$count" -lt 2 ]; then
    echo "  FAIL: $outfile — none of the requested H3 headings matched"
    return 1
  fi
  written=$(( written + 1 ))
  echo "  wrote: $outfile ($count lines, concatenated $# H3 sections)"
}

echo "=== slice-spec.sh: header-anchored extraction (v8.16) ==="
echo "Source: $SPEC ($TOTAL_LINES lines)"
echo "Output: $OUT_DIR"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# SLICE MAPPING (outfile → spec heading)
#
# global/         — cross-cutting hard rules every role reads
# weekly/         — standard weekly format details
# specials/       — common rules across special editions
# formats/        — one file per format
# triggers/       — auto-trigger logic and search checklist
#
# H2 anchors are exact text of the spec heading.
# H3 anchors are exact text of sub-headings inside an H2.
# Format-section files use H3 anchors inside "Issue Formats".
# ─────────────────────────────────────────────────────────────────────────────

echo "── global/ ──"
# v8.38 (W-4) — the Editorial Charter (north-star + standing rules) leads every role read.
extract_heading  "$OUT_DIR/global/00-charter.md" "Editorial Charter"
# Identity is H2 "Identity" + "The Reader" (the reader intro continues identity)
extract_h2_multi "$OUT_DIR/global/01-identity.md" "Identity" "The Reader"
extract_heading  "$OUT_DIR/global/02-key-rules.md" "Key Rules"
# v8.15 / v8.27 — Article Structure (Lead + Catch-Up) — added to global so planner reads it
extract_heading  "$OUT_DIR/global/02a-article-structure.md" "Article Structure: Lead + Catch-Up"
# v8.15 / v8.18 — Topic Lock (sliding-window cap on repeat ongoing-story Leads)
extract_heading  "$OUT_DIR/global/02b-topic-lock.md" "Topic Lock: Recent Leads & Sliding-Window Cap"
# v8.15 — Per-section discipline rules (Toolkit / Session / Long Game ↔ Session boundary)
extract_heading  "$OUT_DIR/global/02c-per-section-discipline.md" "Per-section discipline rules"
extract_heading  "$OUT_DIR/global/03-visual-design.md" "Visual Design"
extract_h3       "$OUT_DIR/global/04-markup-contracts.md" "Markup contracts (v8.21 system — hard rule)"
extract_h3_multi "$OUT_DIR/global/05-image-integrity.md" \
  "Image-caption integrity (v8.10.3 — hard rule)" \
  "Image URL verification chain (v8.13.7+) — UNBREAKABLE RULE"
extract_h3       "$OUT_DIR/global/06-ground-discipline.md" "Ground discipline (v8.21 system)"
extract_h3       "$OUT_DIR/global/07-accent-lockdown.md"   "Accent lockdown (v8.21 system)"
extract_h3_multi "$OUT_DIR/global/08-stat-budget.md" \
  "Stat budget (v8.4 — hard cap per issue)" \
  "Held-attention moment (format-agnostic)" \
  "Issue accent" \
  "Chrome positioning ground rules" \
  "Visual features — auto-apply guarantee (v8.7.3)"

echo ""
echo "── weekly/ ──"
extract_h3       "$OUT_DIR/weekly/01-overview.md"        "Standard Weekly (default)"
extract_heading  "$OUT_DIR/weekly/02-sections.md"        "Section Structure (Standard Weekly)"
extract_heading  "$OUT_DIR/weekly/03-rotating.md"        "Rotation Mechanics"
extract_heading  "$OUT_DIR/weekly/04-anchor-piece.md"    "Anchor-Piece Rotation (deprecated v8.15)"
extract_heading  "$OUT_DIR/weekly/05-search-checklist.md" "Search Checklist"
extract_heading  "$OUT_DIR/weekly/06-image-budget.md"     "Component Quick Reference"

echo ""
echo "── specials/ ──"
# Specials overview = the content-first contract H3, inside Special Editions H2
extract_h3       "$OUT_DIR/specials/01-overview.md" "Content-first contract (non-negotiable)"
extract_h3_multi "$OUT_DIR/specials/02-cover.md" \
  "Authoring a special edition" \
  "Component list"
extract_heading  "$OUT_DIR/specials/03-meanwhile.md" "Auto-Triggered Specials"
extract_h3       "$OUT_DIR/specials/04-chapter-gate.md" \
  "Chapter gate — RETIRED (v8.21)"
extract_h3       "$OUT_DIR/specials/05-imagery-budget.md" \
  "Imagery budget — MANDATORY for loud special editions"
extract_h3       "$OUT_DIR/specials/06-editorial-body-kit.md" \
  "Editorial body kit — RETIRED (v8.21)"
extract_h3       "$OUT_DIR/specials/07-signature-moments.md" \
  "Signature moments — RETIRED (v8.21)"
extract_h3       "$OUT_DIR/specials/08-chapter-transitions.md" \
  "Chapter transitions + ambient (format-agnostic)"
# 09-multi-venue and 13-holiday-identity: synthetic / from holiday-identity H2
extract_heading  "$OUT_DIR/specials/13-holiday-identity.md" \
  "Holiday Identity (v8.12 — Countdown and Field Guide only)"

# Synthetic specials files (no clean H2/H3 mapping; hand-curated text)
cat > "$OUT_DIR/specials/09-multi-venue.md" <<'MV'
# Multi-venue Countdown

> See `formats/countdown.md` for the full Countdown spec; this file is a cross-format summary of multi-venue rules that live inside that section.

Multi-venue trips (e.g. Efteling + Beekse Bergen) get parallel treatment:
- Equal hype weight: words and images per venue sit within a 60/40 split.
- Each venue's full estate is researched, not just the marquee feature.
- A `data-multi-venue="true"` body flag activates per-venue palette tokens.
- Tier 33 (`33-countdown-destinations.css`) provides Efteling and Beekse Bergen
  palettes; Tier 36 (`36-holiday-identity.css`) provides the two-half + transit
  structural rhythm. The two layers compose.

For Field Guides, multi-venue rules live in `formats/field-guide.md`
(headline rule 7 — multi-venue balance).
MV
written=$(( written + 1 ))
echo "  wrote: $OUT_DIR/specials/09-multi-venue.md (synthetic — no clean H2/H3 anchor)"

cat > "$OUT_DIR/specials/10-hype-chapter-visuals.md" <<'HYPE'
# Hype-Chapter Visuals — RETIRED (v8.21 / v8.12)

The pre-v8.21 hype-chapter modifier system was deleted with the rest of the old special-edition chrome; its CSS file no longer exists. Hype register on Countdown / Field Guide is now carried entirely by the Holiday Identity layer (`.hol-*` components + `.theme-*` ambients — see § holiday-identity) and by the hype components in `43-holiday-hype.css` / `44-holiday-sprinkles.css`. Literary formats (Deep Dive, Versus, Rewind, Season Review) use the v8.21 editorial kit with no hype variants. Superseded by the unified core — see `references/core-components.md`.
HYPE
written=$(( written + 1 ))
echo "  wrote: $OUT_DIR/specials/10-hype-chapter-visuals.md (synthetic)"

cat > "$OUT_DIR/specials/11-readability-locks.md" <<'LOCKS'
# Readability Locks — RETIRED (v8.21)

The pre-v8.21 readability-lock CSS layer was deleted with the old chrome; its CSS file no longer exists. In the live v8.21 editorial system, each self-painting component locks its own text colour in its own rules — use the canonical markup from `references/component-contracts.md` (Gate 1E) and contrast is handled; never add inline styles or ground overrides. Superseded by the unified core — see `references/core-components.md`.
LOCKS
written=$(( written + 1 ))
echo "  wrote: $OUT_DIR/specials/11-readability-locks.md (synthetic)"

cat > "$OUT_DIR/specials/12-portrait-spread.md" <<'SPREAD'
# Portrait Spread — RETIRED (v8.21)

The pre-v8.21 three-column spread layout was deleted in the v8.21 redesign; no current CSS or JS implements it. Chapters are a single measured column (`.chapter-body`, 36rem) with `.is-wide` / `.is-fullbleed` breakouts; `.marginalia` floats into the right gutter and falls back inline at narrow widths (see the Component list in § cover). Superseded by the unified core — see `references/core-components.md`.
SPREAD
written=$(( written + 1 ))
echo "  wrote: $OUT_DIR/specials/12-portrait-spread.md (synthetic)"

echo ""
echo "── formats/ ──"
# weekly.md = the H3 "Standard Weekly (default)" inside "Issue Formats"
extract_h3 "$OUT_DIR/formats/weekly.md"        "Standard Weekly (default)"
extract_h3 "$OUT_DIR/formats/deep-dive.md"     "Deep Dive"
extract_h3 "$OUT_DIR/formats/countdown.md"     "The Countdown"
extract_h3 "$OUT_DIR/formats/season-review.md" "The Season Review"
extract_h3 "$OUT_DIR/formats/versus.md"        "The Versus"
extract_h3 "$OUT_DIR/formats/rewind.md"        "The Rewind"
extract_h3 "$OUT_DIR/formats/guide.md"         "The Guide"
extract_h3 "$OUT_DIR/formats/starter-kit.md"   "The Starter Kit"
extract_h3 "$OUT_DIR/formats/shortlist.md"     "The Shortlist"
extract_h3 "$OUT_DIR/formats/next.md"          "The Next"
extract_h3 "$OUT_DIR/formats/lookahead.md"     "The Lookahead"
extract_h3 "$OUT_DIR/formats/field-guide.md"   "The Field Guide"

echo ""
echo "── triggers/ ──"
# Trigger logic and guardrails live inside the "Auto-Triggered Specials" H2.
# Slice the relevant H3 sub-headings.
extract_h3 "$OUT_DIR/triggers/01-priority-1-calendar.md" "Auto-Trigger Logic"
extract_h3 "$OUT_DIR/triggers/02-priority-2-event.md"    "Auto-Trigger Logic"
extract_h3 "$OUT_DIR/triggers/03-priority-3-safety.md"   "Auto-Trigger Logic"
extract_h3 "$OUT_DIR/triggers/04-guardrails.md"          "Guardrails"
extract_heading "$OUT_DIR/triggers/05-search-checklist.md" "Search Checklist"

# ─────────────────────────────────────────────────────────────────────────────
# README — reading order per role
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "── README.md ──"

cat > "$OUT_DIR/README.md" <<'README'
# references/spec/ — Sliced Editorial Spec

This directory contains role-targeted slices of `references/editorial-spec.md`.
Generated by `scripts/slice-spec.sh` (v8.16, header-anchored). Re-run after any
editorial-spec.md edit.

## Reading Order Per Role

### Researcher
Reads: context on what to find and how to source it. Does NOT need visual/markup rules.

1. `global.md` § `key-rules` — Cardinal Rule, voice, content standards, section rules
2. `global.md` § `image-integrity` — image-caption integrity, what makes a valid image
3. `triggers.md` § `search-checklist` — core search groups (always-run)
4. `triggers.md` § `priority-1-calendar` + `priority-2-event` + `priority-3-safety` — trigger logic
5. `triggers.md` § `guardrails` — what NOT to trigger
6. `formats.md` § `<format>` — format-specific research requirements

### Planner
Reads: structural rules, constraints, and the format contract for the issue.

1. `global.md` § `identity` — what The Signal IS
2. `global.md` § `key-rules` — Cardinal Rule and editorial standards
3. `global.md` § `markup-contracts` — banned markup alternates
4. `global.md` § `accent-lockdown` — coral rules
5. `global.md` § `stat-budget` — stat cap per issue, held-attention moment rules
6. `formats.md` § `<format>` — canonical chapter order, word count targets
7. `specials.md` § `overview` — if format is any special edition

### Writer (per chapter)
Reads: markup contracts, ground rules, accent rules, and their format.

1. `references/pre-flight.md` — **ALWAYS first**
2. `global.md` § `markup-contracts` — banned markup alternates (full list)
3. `global.md` § `ground-discipline` — paper/ink/gallery ground rules
4. `global.md` § `accent-lockdown` — coral lockdown rules
5. `formats.md` § `<format>` — their issue's format spec
6. Chapter brief from `chapter-plan.json` — their specific chapter's requirements

### Repair Subagent
Same as writer, plus the failing chapter's gate report.

1. All writer reads above
2. Gate report for the failing chapter (passed in objective)
3. `references/compliance-checklist.md` — Gate 1E markup greps (run these after repair)

## Files

After running `slice-spec.sh`, the directory holds one consolidated `.md`
file per subdir (subdirs are removed in the consolidation stage):

- `global.md` — Identity, Key Rules, Visual Design, Markup Contracts, Image Integrity, Ground Discipline, Accent Lockdown, Stat Budget
- `weekly.md` — Standard Weekly overview + Section Structure + Rotation Mechanics + Anchor-Piece + Search Checklist + Component Reference
- `specials.md` — Content-first contract + Authoring + Component list + Auto-Triggered Specials + Imagery Budget + Chapter Beads ambient + Multi-venue + Holiday Identity (plus retirement stubs for the deleted pre-v8.21 chrome: chapter gate, body kit, signature moments, hype variants, readability locks, portrait spread)
- `formats.md` — One H2 per format: Standard Weekly, Deep Dive, Countdown, Season Review, Versus, Rewind, Guide (merged; Starter Kit + Shortlist folded in, retained for reference), Next, Lookahead (retired/folded), Field Guide
- `triggers.md` — Priority 1/2/3 trigger logic + Guardrails + Search Checklist

## Source

All slices derived from `references/editorial-spec.md`. Slicer is **header-anchored**
(v8.16): each output file is extracted from an H2 (`## Heading`) or H3
(`### Heading`) marker in the source, NOT a hardcoded line range. This means
the slicer is robust to edits that shift line numbers.

Re-generate with: `bash scripts/slice-spec.sh`
README

written=$(( written + 1 ))
echo "  wrote: $OUT_DIR/README.md"

echo ""
echo "=== DONE — $written files written ==="
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# CONSOLIDATION — concatenate each subdir into one .md file
# Skill library caps file count at 100. Consolidation keeps role-targeted
# reads (via H2 anchors) while staying under the file cap.
# ─────────────────────────────────────────────────────────────────────────────

echo "=== CONSOLIDATING (subdirs → flat .md files) ==="

cd "$OUT_DIR" || exit 1

for subdir in global weekly specials formats triggers; do
  if [ -d "$subdir" ]; then
    out="${subdir}.md"
    : > "$out"
    echo "# Spec slice — $subdir" >> "$out"
    echo "" >> "$out"
    echo "_This file consolidates the $subdir/ subdir into one file. Each former file becomes an H2 section. Anchor names use the original filename without the numeric prefix._" >> "$out"
    echo "" >> "$out"
    for f in $(ls "$subdir"/*.md 2>/dev/null | sort); do
      base=$(basename "$f" .md)
      anchor=$(echo "$base" | sed 's/^[0-9]*-//')
      echo "" >> "$out"
      echo "---" >> "$out"
      echo "" >> "$out"
      echo "## $anchor" >> "$out"
      echo "" >> "$out"
      sed '/^# /d' "$f" >> "$out"
      echo "" >> "$out"
    done
    rm -rf "$subdir"
    echo "  wrote: $out (consolidated, removed $subdir/)"
  fi
done

echo ""
echo "Final layout:"
ls -la "$OUT_DIR" | grep -v '^d' | awk '{print "  " $NF}'
