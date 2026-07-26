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

PLAN_RC=0

# ── plan validation, surfaced rather than swallowed (WP-3c, 2026-07-26) ───────
# Both goldens' chapter-plan.json files are validated by the upstream production
# aid (scripts/validate-chapter-plan.py, SPEC §3.1/§3.6), and a failure reaches
# this script's exit code.
#
# It did not, until now. The legacy call sent the validator's report to
# /dev/null, then neutralised its status with an `|| echo` whose message told the
# reader the check had been passed over for a benign reason — so the script
# printed PASS over a plan that was failing with 7 errors, and `set -e` never saw
# it. The mx golden's plan was not checked at all: 21 errors that nobody had ever
# looked for. See EVIDENCE/WP-10.md § 6 for the measurements and WP-3c.md for the
# repair. A harness that hides a failure is worse than no harness, because it
# converts red into green.
#
# Both plans are validated even when the first one fails (status accumulated in
# PLAN_RC, checked at the end) rather than aborting on the first non-zero: the
# whole point of the second call is that its errors were never seen, so stopping
# short of it would reintroduce the same blind spot in a new shape.
validate_plan() {
  local label="$1" plan="$2" rc=0
  echo "--- validate the $label golden plan against the skeleton ---"
  python3 "$SKILL_DIR/scripts/validate-chapter-plan.py" "$plan" || rc=$?
  if [ "$rc" -eq 0 ]; then
    echo "  plan OK — validate-chapter-plan.py exit 0"
  else
    echo "  PLAN VALIDATION FAILED (exit $rc): $plan"
    echo "  Not skipped, not swallowed — this fails the golden regression."
    PLAN_RC=1
  fi
}

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
validate_plan "legacy" "$GOLD/chapter-plan.json"

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
  validate_plan "mx" "$MXGOLD/chapter-plan.json"
  echo ""
fi

if [ "$PLAN_RC" -ne 0 ]; then
  echo "=== GOLDEN REGRESSION FAIL — a golden chapter plan does not satisfy the plan"
  echo "    contract (SPEC §3.1/§3.6). The report above says which fields and why. ==="
  exit 1
fi

echo "=== GOLDEN REGRESSION PASS — the weekly generator produces a valid Transmission issue ==="
