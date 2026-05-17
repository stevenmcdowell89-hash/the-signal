#!/usr/bin/env bash
# slice-spec.sh — Deterministically slices references/editorial-spec.md into
# role-targeted files under references/spec/.
#
# Run: bash scripts/slice-spec.sh [--spec-path <path>] [--out-dir <dir>]
# Idempotent: safe to re-run after editorial-spec.md edits.
#
# v8.11.0 — pipeline rework

set -euo pipefail

SPEC="${1:-$(dirname "$0")/../references/editorial-spec.md}"
OUT_DIR="${2:-$(dirname "$0")/../references/spec}"

SPEC="$(realpath "$SPEC")"
OUT_DIR="$(realpath "$OUT_DIR")"

# Create output directories
mkdir -p "$OUT_DIR/global" "$OUT_DIR/weekly" "$OUT_DIR/specials" \
         "$OUT_DIR/formats" "$OUT_DIR/triggers"

TOTAL_LINES=$(wc -l < "$SPEC")
written=0
covered_lines=0

# Helper: extract lines $2..$3 from SPEC into $1 (creating dirs as needed)
write_section() {
  local outfile="$1"
  local from="$2"
  local to="$3"
  local lines=$(( to - from + 1 ))
  mkdir -p "$(dirname "$outfile")"
  sed -n "${from},${to}p" "$SPEC" > "$outfile"
  written=$(( written + 1 ))
  covered_lines=$(( covered_lines + lines ))
  echo "  wrote: $outfile ($lines lines)"
}

echo "=== slice-spec.sh: slicing $SPEC into $OUT_DIR ==="
echo "Total source lines: $TOTAL_LINES"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL — cross-cutting hard rules every role reads
# ─────────────────────────────────────────────────────────────────────────────

echo "── global/ ──"

# 01-identity.md  — lines 1-19 (Identity + reader intro separator)
write_section "$OUT_DIR/global/01-identity.md" 1 19

# 02-key-rules.md — lines 516-574 (Key Rules section: Cardinal, Voice, Content, Section Rules)
write_section "$OUT_DIR/global/02-key-rules.md" 516 550

# 03-visual-design.md — lines 552-574 (Visual Design, fonts, backgrounds, output)
write_section "$OUT_DIR/global/03-visual-design.md" 552 574

# 04-markup-contracts.md — lines 850-880 (Markup contracts v8.10.3)
write_section "$OUT_DIR/global/04-markup-contracts.md" 850 867

# 05-image-integrity.md — lines 696-739 (Image-caption integrity v8.10.3 +
# Image URL verification chain v8.13.7+ unbreakable-rule chain). Re-check
# range if editorial-spec.md image-integrity sections are extended.
write_section "$OUT_DIR/global/05-image-integrity.md" 696 739

# 06-ground-discipline.md — lines 839-849 (Ground discipline v8.4)
write_section "$OUT_DIR/global/06-ground-discipline.md" 839 849

# 07-accent-lockdown.md — lines 868-894 (Accent lockdown v8.4)
write_section "$OUT_DIR/global/07-accent-lockdown.md" 868 880

# 08-stat-budget.md — lines 881-930 (Stat budget v8.4 + Held-attention + Issue accent + Chrome + Visual features)
write_section "$OUT_DIR/global/08-stat-budget.md" 881 969

# ─────────────────────────────────────────────────────────────────────────────
# WEEKLY — standard weekly format
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "── weekly/ ──"

# 01-overview.md — lines 249-253 (Standard Weekly format overview)
write_section "$OUT_DIR/weekly/01-overview.md" 249 253

# 02-sections.md — lines 21-96 (Section Structure, Fixed vs Rotating, Anchor Piece, Colophon)
write_section "$OUT_DIR/weekly/02-sections.md" 21 97

# 03-rotating.md — lines 98-157 (Rotation Mechanics, Cadence Table, Selection Rules, Placement)
write_section "$OUT_DIR/weekly/03-rotating.md" 98 157

# 04-anchor-piece.md — lines 37-76 (Anchor piece rotation in detail)
write_section "$OUT_DIR/weekly/04-anchor-piece.md" 37 76

# 05-search-checklist.md — lines 159-183 (Search Checklist: core groups)
write_section "$OUT_DIR/weekly/05-search-checklist.md" 159 183

# 06-image-budget.md — lines 185-247 (Component Quick Reference)
write_section "$OUT_DIR/weekly/06-image-budget.md" 185 247

# ─────────────────────────────────────────────────────────────────────────────
# SPECIALS — common rules across all special editions
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "── specials/ ──"

# 01-overview.md — lines 576-595 (Special editions: content-first contract)
write_section "$OUT_DIR/specials/01-overview.md" 576 595

# 02-cover.md — lines 596-630 (Authoring a special edition + component list)
write_section "$OUT_DIR/specials/02-cover.md" 596 630

# 03-meanwhile.md — lines 450-514 (Meanwhile section + auto-trigger logic + guardrails + trip-aware)
write_section "$OUT_DIR/specials/03-meanwhile.md" 450 514

# 04-chapter-gate.md — lines 774-838 (Chapter gate MANDATORY)
write_section "$OUT_DIR/specials/04-chapter-gate.md" 774 838

# 05-imagery-budget.md — lines 631-649 (Imagery budget MANDATORY)
write_section "$OUT_DIR/specials/05-imagery-budget.md" 631 649

# 06-editorial-body-kit.md — lines 685-731 (Editorial body kit MANDATORY)
write_section "$OUT_DIR/specials/06-editorial-body-kit.md" 685 703

# 07-signature-moments.md — lines 732-754 (Signature moments ONE per format)
write_section "$OUT_DIR/specials/07-signature-moments.md" 732 754

# 08-chapter-transitions.md — lines 755-773 (Chapter transitions + ambient)
write_section "$OUT_DIR/specials/08-chapter-transitions.md" 755 773

# 09-multi-venue.md — (Multi-venue theming — referenced in CSS tier 9; spec section is in CSS SKILL.md; 
#   this file captures the editorial rules from the CSS table reference in SKILL.md context)
# The editorial-spec.md doesn't have a standalone multi-venue H2, but the concept is embedded in 
# Countdown section (lines 257-323). We capture it there.
write_section "$OUT_DIR/specials/09-multi-venue.md" 257 323

# 10-hype-chapter-visuals.md — lines (embedded in Countdown, ~262-290ish + Hype variants section)
# The hype variants rule starts after the canonical chapter order, within countdown spec
# We include it as a sub-topic note pointing to the main countdown format file
cat > "$OUT_DIR/specials/10-hype-chapter-visuals.md" <<'HYPE'
# Hype-Chapter Visuals (v8.9.1)

> See `formats/countdown.md` for the full hype-chapter spec. This file is a cross-format summary.

**Hype-chapter visuals** are opt-in CSS modifiers (`32-hype-variants.css`) that dial back default special-edition chrome on chapters where excitement — not literary depth — is the job.

## When to use hype modifiers

Apply on:
- Countdown hype chapters: Top Attractions, Accommodation, Mood Board, Five Moments Worth the Trip, By the Numbers (when image-led)
- Field Guide: The Opening, The Unmissables

**Never apply on literary formats:** Deep Dive, Versus, Rewind, Season Review — these keep full default chrome.

## The four modifiers

1. **`.sp-chapter-gate.is-hype`** — compact gate: 60vh track (vs 110vh), 40vh hold (vs 100vh), layers solid by progress 0.08 (vs 0.20)
2. **`[data-sp-chapter].is-hype`** — re-permits coral on `.sp-number`, `.sp-number-huge`, `.sp-kicker`, `.sp-brief-kicker`, `.unmissables .sp-datum-value`, `.why-its-here`. All global lockdown elements unchanged.
3. **`.sp-ground-gallery`** — neutral slate ground (#1A1E27) for image-first chapters (Mood Board primary, optionally Field Guide Opening). NOT pitch black.
4. **`.unmissables` / `.unmissable`** — Field Guide Unmissables pattern: 6-10 full-width editorial beats, each = hero image + sensory prose + "Why It's Here" coral kicker + mono `<dl>` practical footer. Drop-cap forbidden on picks.

## Markup reminder

```html
<!-- Hype chapter gate -->
<div class="sp-chapter-gate is-hype" data-chapter-num="II" ...>...</div>

<!-- Hype chapter wrapper -->
<section data-sp-chapter data-chapter-num="2" data-chapter-title="Top Attractions"
         data-chapter-arc="The rides worth your day" class="is-hype">
```
HYPE
  written=$(( written + 1 ))
  echo "  wrote: $OUT_DIR/specials/10-hype-chapter-visuals.md (synthetic)"

# 11-readability-locks.md — brief note (Readability Lock Principle from SKILL.md CSS table, v8.10.3)
cat > "$OUT_DIR/specials/11-readability-locks.md" <<'LOCKS'
# Readability Locks (v8.10.3)

**CSS layer:** `34-readability-locks.css` (Tier 10, runs last in cascade).

Some self-painting components lose identity when nested inside `[data-sp-chapter]` because Tier 7's ground-discipline lockdown is over-aggressive. This layer re-locks each component to a fixed background+text pair regardless of the chapter ground above it.

| Component | Lock |
|---|---|
| `.sp-marginalia` | Always cream-bg + ink-text |
| `.sp-pull-break` | Always dark-bg + bone-text |
| `.sp-pullquote-huge` text | Set explicitly per chapter ground |

**Why this matters for writers:** if you use these components in the markup (which you should, per pre-flight.md), the CSS will handle contrast automatically. You do NOT need to add inline styles or ground overrides. Just use the canonical markup and the lock layer handles it.

**Markup contracts (Gate 1E):** the lockdown only works when markup matches the contract. See `global/04-markup-contracts.md` and `references/pre-flight.md` § Canonical markup snippets.
LOCKS
  written=$(( written + 1 ))
  echo "  wrote: $OUT_DIR/specials/11-readability-locks.md (synthetic)"

# 13-holiday-identity.md — v8.12 / v8.13 separate visual identity for Countdown + Field Guide
# editorial-spec.md § Holiday Identity starts at line 1030 (## Holiday Identity ...)
# v8.13 (May 2026) extended this section to end-of-file.
# and runs to end of file (line 1120). Re-check exact range if editorial-spec.md changes.
write_section "$OUT_DIR/specials/13-holiday-identity.md" 1028 1211

# 12-portrait-spread.md — portrait spread hybrid layout note
cat > "$OUT_DIR/specials/12-portrait-spread.md" <<'SPREAD'
# Portrait Spread — Hybrid Layout (v8.7.2)

**CSS:** `26-special-editorial.css`. The three-column `.sp-spread` layout adapts at ≤980px.

## Portrait behaviour

At ≤ 980px, `.sp-spread` becomes `display: flow-root; position: relative`.

- **Rail** (`.sp-rail`): `position: absolute; top:0; bottom:0; left:0; width: 60/44px` — runs full spread height as decorative chapter-side chrome.
- **Margin aside** (`.sp-margin`): reparented via the portrait-spread-reparenter IIFE in `script.js` to be first child of `.sp-spread-body`; floats right (190/128px) with `shape-outside: margin-box`. Body is `flow-root` with left padding (78/58px) to clear the rail. Prose flows around the margin and reclaims full reading width once it ends.
- **Ink grounds**: the margin paints a solid paper-tinted background so ink-on-paper text stays legible.

## Markup contract

```html
<div class="sp-spread">
  <div class="sp-rail" aria-hidden="true"></div>
  <aside class="sp-margin">
    <!-- marginalia content -->
  </aside>
  <div class="sp-spread-body">
    <!-- prose, drop cap on first <p> -->
  </div>
</div>
```

**Never stack:** portrait is the canonical read. The three-column desktop layout is a bonus, not the target.
SPREAD
  written=$(( written + 1 ))
  echo "  wrote: $OUT_DIR/specials/12-portrait-spread.md (synthetic)"

# ─────────────────────────────────────────────────────────────────────────────
# FORMATS — one file per format
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "── formats/ ──"

# weekly.md — lines 249-253 + key rules 516-550 + rotation 98-157 summary reference
write_section "$OUT_DIR/formats/weekly.md" 249 256

# deep-dive.md — lines 254-256
write_section "$OUT_DIR/formats/deep-dive.md" 254 256

# countdown.md — lines 257-323
write_section "$OUT_DIR/formats/countdown.md" 257 323

# season-review.md — lines 324-328
write_section "$OUT_DIR/formats/season-review.md" 324 328

# versus.md — lines 329-366
write_section "$OUT_DIR/formats/versus.md" 329 366

# rewind.md — lines 367-375
write_section "$OUT_DIR/formats/rewind.md" 360 375

# starter-kit.md — lines 376-384
write_section "$OUT_DIR/formats/starter-kit.md" 367 384

# blueprint.md — lines 385-394
write_section "$OUT_DIR/formats/blueprint.md" 376 394

# shortlist.md — lines 395-445
write_section "$OUT_DIR/formats/shortlist.md" 385 445

# field-guide.md — lines 395-445
write_section "$OUT_DIR/formats/field-guide.md" 395 445

# ─────────────────────────────────────────────────────────────────────────────
# TRIGGERS — auto-trigger logic
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "── triggers/ ──"

# 01-priority-1-calendar.md — synthetic (from auto-trigger logic block, lines 460-495)
# We split this by priority within the block
write_section "$OUT_DIR/triggers/01-priority-1-calendar.md" 460 473

# 02-priority-2-event.md
write_section "$OUT_DIR/triggers/02-priority-2-event.md" 474 487

# 03-priority-3-safety.md
write_section "$OUT_DIR/triggers/03-priority-3-safety.md" 488 503

# 04-guardrails.md — lines 496-514
write_section "$OUT_DIR/triggers/04-guardrails.md" 496 514

# 05-search-checklist.md — lines 159-183 (core + rotating group pointers)
write_section "$OUT_DIR/triggers/05-search-checklist.md" 159 184

# ─────────────────────────────────────────────────────────────────────────────
# README.md — reading order per role
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "── README.md ──"

cat > "$OUT_DIR/README.md" <<'README'
# references/spec/ — Sliced Editorial Spec

This directory contains role-targeted slices of `references/editorial-spec.md`.
Generated by `scripts/slice-spec.sh`. Re-run after any editorial-spec.md edit.

## Reading Order Per Role

### Researcher
Reads: context on what to find and how to source it. Does NOT need visual/markup rules.

1. `global/02-key-rules.md` — Cardinal Rule, voice, content standards, section rules
2. `global/05-image-integrity.md` — image-caption integrity, what makes a valid image
3. `triggers/05-search-checklist.md` — core search groups (always-run)
4. `triggers/01-priority-1-calendar.md` + `02-priority-2-event.md` + `03-priority-3-safety.md` — trigger logic
5. `triggers/04-guardrails.md` — what NOT to trigger
6. `formats/<format>.md` — format-specific research requirements

### Planner
Reads: structural rules, constraints, and the format contract for the issue.

1. `global/01-identity.md` — what The Signal IS
2. `global/02-key-rules.md` — Cardinal Rule and editorial standards
3. `global/04-markup-contracts.md` — banned markup alternates (chapter plan must not prescribe banned markup)
4. `global/07-accent-lockdown.md` — coral rules (plan must flag hype chapters correctly)
5. `global/08-stat-budget.md` — stat cap per issue, held-attention moment rules
6. `formats/<format>.md` — canonical chapter order, word count targets, format-specific requirements
7. `specials/01-overview.md` — if format is any special edition

### Writer (per chapter)
Reads: markup contracts, ground rules, accent rules, and their format.

1. `references/pre-flight.md` — **ALWAYS first** (12 regression triggers, canonical markup, self-audit)
2. `global/04-markup-contracts.md` — banned markup alternates (full list)
3. `global/06-ground-discipline.md` — paper/ink/gallery ground rules
4. `global/07-accent-lockdown.md` — coral lockdown rules
5. `formats/<format>.md` — their issue's format spec
6. Chapter brief from `chapter-plan.json` — their specific chapter's requirements

### Repair Subagent
Same as writer, plus the failing chapter's gate report.

1. All writer reads above
2. Gate report for the failing chapter (passed in objective)
3. `references/compliance-checklist.md` — Gate 1E markup greps (run these after repair)

## Directory Structure

```
references/spec/
├── README.md                    ← this file
├── global/
│   ├── 01-identity.md           ← Identity + The Reader (who this is for)
│   ├── 02-key-rules.md          ← Cardinal Rule, voice, content standards
│   ├── 03-visual-design.md      ← Fonts, backgrounds, output format
│   ├── 04-markup-contracts.md   ← Banned markup alternates (Gate 1E source)
│   ├── 05-image-integrity.md    ← Image-caption integrity rules (Gate 1F source)
│   ├── 06-ground-discipline.md  ← Paper/ink/gallery ground rules (v8.4)
│   ├── 07-accent-lockdown.md    ← Coral accent rules (v8.4)
│   └── 08-stat-budget.md        ← Stat cap, held-attention, chrome rules, auto-apply
├── weekly/
│   ├── 01-overview.md           ← Standard weekly: word count, page target
│   ├── 02-sections.md           ← Fixed vs rotating, anchor piece, colophon
│   ├── 03-rotating.md           ← Rotation mechanics, cadence, placement
│   ├── 04-anchor-piece.md       ← Anchor piece rotation detail
│   ├── 05-search-checklist.md   ← Core search groups
│   └── 06-image-budget.md       ← Component quick reference
├── specials/
│   ├── 01-overview.md           ← Content-first contract (non-negotiable)
│   ├── 02-cover.md              ← Authoring + component list
│   ├── 03-meanwhile.md          ← Meanwhile section rules + auto-trigger logic
│   ├── 04-chapter-gate.md       ← Chapter gate MANDATORY (v8.5)
│   ├── 05-imagery-budget.md     ← Imagery budget MANDATORY
│   ├── 06-editorial-body-kit.md ← Editorial body kit MANDATORY
│   ├── 07-signature-moments.md  ← One per format
│   ├── 08-chapter-transitions.md← Transitions + ambient
│   ├── 09-multi-venue.md        ← Multi-venue countdown rules
│   ├── 10-hype-chapter-visuals.md← Hype modifiers (v8.9.1)
│   ├── 11-readability-locks.md  ← Readability lock principle (v8.10.3)
│   ├── 12-portrait-spread.md    ← Portrait spread hybrid layout (v8.7.2)
│   └── 13-holiday-identity.md   ← Holiday identity (v8.12, Countdown + Field Guide)
├── formats/
│   ├── weekly.md                ← Standard weekly format
│   ├── deep-dive.md             ← Deep Dive format
│   ├── countdown.md             ← The Countdown format (full)
│   ├── season-review.md         ← Season Review format
│   ├── versus.md                ← Versus format (incl. holiday/destination subtype)
│   ├── rewind.md                ← The Rewind format
│   ├── starter-kit.md           ← The Starter Kit format
│   ├── blueprint.md             ← The Blueprint format
│   ├── shortlist.md             ← The Shortlist format
│   └── field-guide.md           ← The Field Guide format (full)
└── triggers/
    ├── 01-priority-1-calendar.md← Calendar-fixed triggers (P1)
    ├── 02-priority-2-event.md   ← Event-driven triggers (P2)
    ├── 03-priority-3-safety.md  ← Safety-net triggers (P3)
    ├── 04-guardrails.md         ← What NOT to trigger
    └── 05-search-checklist.md   ← Core search groups reference
```

## Source

All slices derived from `references/editorial-spec.md` (980 lines).
Re-generate with: `bash scripts/slice-spec.sh`
README

  written=$(( written + 1 ))
  echo "  wrote: $OUT_DIR/README.md"

# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "=== DONE ==="
echo "Files written:     $written"
echo "Source lines:      $TOTAL_LINES"
echo "Lines referenced:  $covered_lines (note: some ranges overlap, synthetic files not counted)"
echo ""
echo "Verify with:"
echo "  find $OUT_DIR -name '*.md' | wc -l   # should be 31"
echo "  wc -l $OUT_DIR/**/*.md               # per-file counts"

# ─────────────────────────────────────────────────────────────────────────────
# CONSOLIDATION STAGE (v8.11.0+)
# Skill library caps file count at 100. Concatenate each subdir into one .md
# file with H2 anchors, then remove the subdirs. This keeps role-targeted
# reads (via H2 anchors) while staying under the file cap.
# ─────────────────────────────────────────────────────────────────────────────

echo ""
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
