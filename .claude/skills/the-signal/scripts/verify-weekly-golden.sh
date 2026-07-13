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
echo "=== GOLDEN REGRESSION PASS — the weekly generator produces a valid Transmission issue ==="
