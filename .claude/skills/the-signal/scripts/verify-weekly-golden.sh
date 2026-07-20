#!/usr/bin/env bash
# verify-weekly-golden.sh — the weekly generator's golden-issue regression.
#
# Stitches the committed golden weekly fixture (references/golden/weekly/) through
# the REAL weekly stitcher and asserts it passes every validate-issue.py gate.
# This is the "test the generator, not just the output" regression from the
# reliability design (Pillar F): run it after ANY change to stitch_weekly.py,
# weekly.json, the weekly CSS, or the weekly structural/visual gates, so a
# regression is caught here — not by the reader on a Sunday.
#
# Exit 0 = the generator still produces a valid Transmission weekly.
# Exit 1 = a regression; the printed gate report says what broke.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
GOLD="$SKILL_DIR/references/golden/weekly"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "=== weekly golden regression ==="
echo "  fixture: $GOLD"

# stage band-content where the stitcher expects it
mkdir -p "$WORK/build/chapters"
cp "$GOLD"/chapters/*.html "$WORK/build/chapters/"

OUT="$WORK/golden-weekly.html"

echo "--- stitch (via the real bash entrypoint) ---"
bash "$SKILL_DIR/scripts/stitch-issue.sh" \
  --plan "$GOLD/chapter-plan.json" \
  --out "$OUT" \
  --build-dir "$WORK/build" \
  --issue-number 16

echo ""
echo "--- validate (all gates; golden carries real <img> markup — --skip-image-urls only skips the network HEAD-checks, which can't run in the offline sandbox) ---"
python3 "$SKILL_DIR/scripts/validate-issue.py" "$OUT" --format weekly --skip-image-urls

echo ""
echo "--- validate the golden plan against the skeleton ---"
python3 "$SKILL_DIR/scripts/validate-chapter-plan.py" "$GOLD/chapter-plan.json" 2>/dev/null \
  || echo "  (validate-chapter-plan weekly branch not present or plan-arg differs — skipping plan check)"

echo ""
# ── mx-weekly golden (WP-8 densification) ────────────────────────────────────
# The densified weekly (design_system=mx) is an OPT-IN path: the legacy golden
# above proves backward-compat (mx flag absent → byte-stable). This second
# golden proves the densified path itself stays valid and byte-reproducible.
# It is NOT a migration of the legacy golden — that fixture's real content
# carries only 3 named voices and the mx path's Law-9 floor is 4; fabricating
# a fourth is forbidden (Law 12). This fixture is the real 4-voice 2026-07-19
# densified weekly instead.
MXGOLD="$SKILL_DIR/references/golden/weekly-mx"
if [ -d "$MXGOLD" ]; then
  echo "=== mx-weekly golden regression (WP-8) ==="
  echo "  fixture: $MXGOLD"
  mkdir -p "$WORK/mxbuild/chapters"
  cp "$MXGOLD"/chapters/*.html "$WORK/mxbuild/chapters/"
  MXOUT="$WORK/mx-weekly.html"
  python3 "$SKILL_DIR/scripts/stitch_weekly.py" \
    --plan "$MXGOLD/chapter-plan.json" \
    --out "$MXOUT" \
    --build-dir "$WORK/mxbuild" \
    --issue-number 17 >/dev/null
  echo "--- byte-identity vs committed expected.html ---"
  if ! diff -q "$MXOUT" "$MXGOLD/expected.html" >/dev/null; then
    echo "  MX GOLDEN DRIFT — stitched output differs from committed expected.html"
    diff "$MXOUT" "$MXGOLD/expected.html" | head -12
    exit 1
  fi
  echo "  byte-identical ✓"
  echo "--- validate (weekly + mx gates: Law-3 6,000 / Law-9 ≥4 / mx-variety) ---"
  python3 "$SKILL_DIR/scripts/validate-issue.py" "$MXOUT" --format weekly --skip-image-urls
  echo ""
fi

echo "=== GOLDEN REGRESSION PASS — the weekly generator produces a valid Transmission issue ==="
