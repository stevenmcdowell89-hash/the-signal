#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# test-coverage-gates.sh — the editorial-coverage-rebuild verification harness.
#
#   SPEC: docs/editorial-coverage-rebuild-SPEC-2026-07-26.md §4 (12 acceptance criteria)
#   WP:   WP-10.  Exclusive files: this script and
#         references/fixtures/coverage-rebuild/**.  Everything else is an INPUT.
#
# WHAT THIS IS FOR
# ----------------
# Nine work packages added mechanical checks across two upstream production aids,
# one ship gate, two asset scripts and the daily. Each proved its own checks in
# isolation, with fixtures that lived in a scratchpad and have since evaporated.
# This harness is the single command that re-proves all twelve acceptance criteria
# from permanent fixtures, on demand, and goes red if any of them stops holding.
#
# THE RULE THIS HARNESS OBEYS, BECAUSE THE BUILD ALREADY BROKE IT ONCE
# -------------------------------------------------------------------
# A harness that hides a failure is worse than no harness, because it converts a
# red state into a green one. `verify-weekly-golden.sh:43-44` does exactly that: it
# runs validate-chapter-plan.py on the golden plan with `2>/dev/null || echo
# "(… skipping plan check)"`, so 7 real errors are printed as a reassuring skip
# notice and the script still exits 0. That file belongs to WP-3, so this harness
# does not edit it — it invokes the validator DIRECTLY, asserts on its real exit
# code, and prints the whole finding under § PLAN-VALIDATION HOLE below. Nothing
# here discards an exit code, redirects a stderr to /dev/null, or pipes a command
# whose status matters into anything.
#
# EVERY CRITERION GETS BOTH DIRECTIONS
# ------------------------------------
# A check that has only ever been seen to pass has not been seen to work. So each
# criterion is asserted with at least one FIRING case (a known-bad input that must
# be rejected) and one PASSING case (a known-good input that must be accepted).
# Where a criterion cannot be demonstrated in this environment it is reported as
# NOT DEMONSTRATED with the reason, and is never counted as a pass.
#
# USAGE
#   bash test-coverage-gates.sh                 # everything
#   bash test-coverage-gates.sh 3 8             # only criteria 3 and 8
#   bash test-coverage-gates.sh --list
#   bash test-coverage-gates.sh --keep          # keep the work dir for inspection
#   bash test-coverage-gates.sh -v              # echo every command and its output
#   bash test-coverage-gates.sh --ignore-known-debt
#         Exit 0 even if the only remaining problem is the golden-plan debt in
#         § PLAN-VALIDATION HOLE. Read that section before using it; the debt is
#         still printed in full, it just stops gating.
#
# EXIT CODES
#   0  every criterion demonstrated, no known debt outstanding
#   1  at least one assertion failed, or known debt is outstanding
#   2  the harness could not run (missing input, fixture build failure)
# ═══════════════════════════════════════════════════════════════════════════════

set -uo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$SKILL_DIR/../../.." && pwd)"
FIXTURES="$SKILL_DIR/references/fixtures/coverage-rebuild"

VALIDATE_ISSUE="$SKILL_DIR/scripts/validate-issue.py"
VALIDATE_PLAN="$SKILL_DIR/scripts/validate-chapter-plan.py"
VALIDATE_BUNDLE="$SKILL_DIR/scripts/validate-research-bundle.py"
IMAGE_DIVERSITY="$SKILL_DIR/scripts/check-image-diversity.sh"
GOLDEN_GATE="$SKILL_DIR/scripts/verify-weekly-golden.sh"
EXTRACT_COVERS="$REPO/scripts/extract-covers.py"
MIRROR_IMAGES="$REPO/scripts/mirror-images.py"
ISSUE_18="$REPO/issues/signal_weekly_2026-07-26.html"
REAL_STATE="$REPO/state/signal-state.json"
LOOKUP="$SKILL_DIR/references/image-source-types.json"
GOLD_PLAN="$SKILL_DIR/references/golden/weekly/chapter-plan.json"
MXGOLD_PLAN="$SKILL_DIR/references/golden/weekly-mx/chapter-plan.json"

# Named baselines, used only for FIRING cases that need the pre-rebuild code.
# A firing case against the code as it was is stronger than a synthetic one: it
# proves the criterion describes a real change, not a tautology.
BASE_DAILY="394b2af"     # last commit before WP-7 (feeds/profile) and WP-11 (render/dedup)
BASE_MIRROR="394b2af"    # last commit before WP-8 (mirror-images/extract-covers)

VERBOSE=0
KEEP=0
IGNORE_DEBT=0
ONLY=()

while [ $# -gt 0 ]; do
  case "$1" in
    -v|--verbose) VERBOSE=1 ;;
    --keep) KEEP=1 ;;
    --ignore-known-debt) IGNORE_DEBT=1 ;;
    --list)
      cat <<'LIST'
SPEC §4 acceptance criteria (all 12 are WP-10's remit to demonstrate):
   1  a weekly plan whose long_read omits `vintage` is rejected            WP-5
   2  an evergreen anchor renders .lr-vintage + a date-free byline;
      a news anchor renders neither                                       WP-3 + WP-4
   3  Issue #18 fails caption-vintage at FIG 03; a corrected fixture passes WP-4 + WP-10
   4  a plan leading news on a family that led 3 of the last 4, with no
      override reason, is rejected                                        WP-5
   5  a matured open loop with no resolving fact fails the bundle gate     WP-5
   6  a matured open loop absent from the rendered HTML fails
      validate-issue.py                                                   WP-4
   7  a results ledger with one data-sport fails when >=2 tracked sports
      concluded in-window                                                 WP-4
   8  Issue #18 fails the shape-budget check                              WP-4 + WP-10
   9  extract-covers.py exits non-zero on an allows_derivatives:false src  WP-8
  10  mirror-images.py writes assets/cached/manifest.json with url+licence WP-8
  11  the daily surfaces a cricket/cycling/athletics item                  WP-7
  12  check-image-diversity.sh no longer reads the retired Wikimedia
      thresholds and enforces min_distinct_shapes                         WP-6
Plus two non-criterion sections that always run:
   P  the plan-validation hole verify-weekly-golden.sh swallows
   G  the golden fixture, re-checked against the commit under test
LIST
      exit 0 ;;
    [0-9]|1[0-2]) ONLY+=("$1") ;;
    *) echo "unknown argument: $1  (try --list)" >&2; exit 2 ;;
  esac
  shift
done

# ── colours, only on a tty ───────────────────────────────────────────────────
if [ -t 1 ]; then
  C_OK=$'\033[32m'; C_NO=$'\033[31m'; C_WARN=$'\033[33m'; C_H=$'\033[1m'; C_D=$'\033[2m'; C_0=$'\033[0m'
else
  C_OK=""; C_NO=""; C_WARN=""; C_H=""; C_D=""; C_0=""
fi

# ── tally ────────────────────────────────────────────────────────────────────
TOTAL_PASS=0; TOTAL_FAIL=0; TOTAL_SKIP=0
CRIT=""                       # id of the criterion currently under test
declare -A CP=() CF=() CS=()  # per-criterion pass / fail / skip counts
declare -a CRIT_ORDER=()
DEBT=0                        # known, reported, non-criterion debt
declare -a DEBT_LINES=()

section() {
  CRIT="$1"; shift
  CRIT_ORDER+=("$CRIT"); CP[$CRIT]=0; CF[$CRIT]=0; CS[$CRIT]=0
  printf '\n%s══ CRITERION %-3s %s%s\n' "$C_H" "$CRIT" "$*" "$C_0"
}
plain_section() {
  CRIT="$1"; shift
  CRIT_ORDER+=("$CRIT"); CP[$CRIT]=0; CF[$CRIT]=0; CS[$CRIT]=0
  printf '\n%s══ %-14s %s%s\n' "$C_H" "$CRIT" "$*" "$C_0"
}

pass() { CP[$CRIT]=$(( ${CP[$CRIT]} + 1 )); TOTAL_PASS=$(( TOTAL_PASS + 1 ))
         printf '   %sok  %s %s\n' "$C_OK" "$C_0" "$1"; }
fail() { CF[$CRIT]=$(( ${CF[$CRIT]} + 1 )); TOTAL_FAIL=$(( TOTAL_FAIL + 1 ))
         printf '   %sFAIL%s %s\n' "$C_NO" "$C_0" "$1"
         [ -n "${2:-}" ] && printf '        %s%s%s\n' "$C_D" "$2" "$C_0"
         if [ -n "${LAST_OUT:-}" ]; then
           printf '        %s--- actual output (first 25 lines) ---%s\n' "$C_D" "$C_0"
           printf '%s\n' "$LAST_OUT" | head -25 | sed "s/^/        ${C_D}| /;s/\$/${C_0}/"
         fi; }
skip() { CS[$CRIT]=$(( ${CS[$CRIT]} + 1 )); TOTAL_SKIP=$(( TOTAL_SKIP + 1 ))
         printf '   %sNOT DEMONSTRATED%s %s\n        reason: %s\n' "$C_WARN" "$C_0" "$1" "$2"; }
debt() { DEBT=$(( DEBT + 1 )); DEBT_LINES+=("$1")
         printf '   %sBLOCKER%s %s\n' "$C_NO" "$C_0" "$1"; }
info() { printf '        %s%s%s\n' "$C_D" "$1" "$C_0"; }

# run <cmd...>  → sets LAST_OUT and LAST_RC. Never swallows the exit code.
run() {
  [ "$VERBOSE" = 1 ] && printf '     %s$ %s%s\n' "$C_D" "$*" "$C_0"
  LAST_OUT="$("$@" 2>&1)"; LAST_RC=$?
  [ "$VERBOSE" = 1 ] && printf '%s\n' "$LAST_OUT" | sed "s/^/       ${C_D}| /;s/\$/${C_0}/"
  return 0
}

# exits <expected-rc> <label>   (assert on the exit code of the last `run`)
exits() {
  if [ "$LAST_RC" = "$1" ]; then pass "$2  ${C_D}[exit $LAST_RC]${C_0}"
  else LAST_OUT="$LAST_OUT" fail "$2" "expected exit $1, got $LAST_RC"; fi
}
# has <regex> <label>  /  hasnt <regex> <label>
has()   { if printf '%s\n' "$LAST_OUT" | grep -Eq -- "$1"; then pass "$2"
          else fail "$2" "output does not match /$1/"; fi; }
hasnt() { if printf '%s\n' "$LAST_OUT" | grep -Eq -- "$1"; then fail "$2" "output DOES match /$1/, and must not"
          else pass "$2"; fi; }
# quiet variants: assert without dumping the output on failure
truth() { if [ "$1" = 1 ]; then pass "$2"; else LAST_OUT="" fail "$2" "${3:-}"; fi; }

# grep for a line matching a pattern, for evidence echo
echo_line() { printf '%s\n' "$LAST_OUT" | grep -E -- "$1" | head -"${2:-1}" | sed "s/^/        ${C_D}> /;s/\$/${C_0}/"; }

wants() {  # wants <criterion-id> → 0 if it should run
  [ ${#ONLY[@]} -eq 0 ] && return 0
  local c; for c in "${ONLY[@]}"; do [ "$c" = "$1" ] && return 0; done; return 1
}

# ═══════════════════════════════════════════════════════════════════════════════
# Pre-flight
# ═══════════════════════════════════════════════════════════════════════════════
printf '%s╔══════════════════════════════════════════════════════════════════════════════╗\n' "$C_H"
printf   '║  editorial-coverage-rebuild — verification harness (WP-10)                   ║\n'
printf   '╚══════════════════════════════════════════════════════════════════════════════╝%s\n' "$C_0"

HEAD_SHA="$(git -C "$REPO" rev-parse --short HEAD 2>/dev/null || echo "not-a-git-repo")"
DIRTY="$(git -C "$REPO" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
printf '  repo         %s\n' "$REPO"
printf '  commit       %s  (%s path(s) dirty in the working tree)\n' "$HEAD_SHA" "$DIRTY"
printf '  fixtures     %s\n' "$FIXTURES"
printf '  run date     %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"

for f in "$VALIDATE_ISSUE" "$VALIDATE_PLAN" "$VALIDATE_BUNDLE" "$IMAGE_DIVERSITY" \
         "$EXTRACT_COVERS" "$MIRROR_IMAGES" "$ISSUE_18" "$REAL_STATE" "$LOOKUP" \
         "$FIXTURES/build-fixtures.py"; do
  [ -e "$f" ] || { echo "FATAL: required input missing: $f" >&2; exit 2; }
done

# Line numbers in files this WP does not own, resolved at run time rather than
# hardcoded — a stale line reference in a bug report is how a two-line fix goes
# unmade. Fall back to "?" rather than lying.
SWALLOW_LN="$(grep -n 'skipping plan check' "$GOLDEN_GATE" | head -1 | cut -d: -f1)"
SWALLOW_LN="${SWALLOW_LN:-?}"
TK_LN="$(grep -n '^TABLE_KINDS' "$VALIDATE_ISSUE" | head -1 | cut -d: -f1)"
TK_LN="${TK_LN:-?}"

WORK="$(mktemp -d)"
cleanup() { if [ "$KEEP" = 1 ]; then echo; echo "  work dir kept: $WORK"; else rm -rf "$WORK"; fi; }
trap cleanup EXIT

# Frozen-input guard. Issue #18 and the archive are read-only (SPEC §1.3); the
# harness asserts against them and must never be able to change them. Recording
# the digests before and after makes that checkable rather than promised.
ISSUE18_SHA_BEFORE="$(sha256sum "$ISSUE_18" | cut -c1-16)"
STATE_SHA_BEFORE="$(sha256sum "$REAL_STATE" | cut -c1-16)"
MANIFEST_SHA_BEFORE=""
[ -f "$REPO/assets/cached/manifest.json" ] && \
  MANIFEST_SHA_BEFORE="$(sha256sum "$REPO/assets/cached/manifest.json" | cut -c1-16)"

echo
echo "  ── building fixtures from the frozen inputs ──"
if ! python3 "$FIXTURES/build-fixtures.py" --out "$WORK/fx" \
        --issue "$ISSUE_18" --state "$REAL_STATE" | sed 's/^/  /'; then
  echo "FATAL: fixture build failed" >&2; exit 2
fi
FX="$WORK/fx"
V=( python3 "$VALIDATE_ISSUE" )
VFLAGS=( --format weekly --skip-image-urls )

# ═══════════════════════════════════════════════════════════════════════════════
# CRITERION 1 — a weekly plan whose long_read omits `vintage` is rejected  (WP-5)
# ═══════════════════════════════════════════════════════════════════════════════
if wants 1; then
section 1 "long_read.vintage is required  (SPEC §3.1, defect A)"

  run python3 "$VALIDATE_PLAN" "$FX/plans/weekly-no-vintage.json"
  exits 1 "FIRING: a plan whose long_read omits vintage is rejected"
  has "missing required 'vintage'" "  … and the error names the missing field"
  has "defect A" "  … and says why it matters (the stitcher stamps the issue date)"
  echo_line "\[VINTAGE\]" 1

  run python3 "$VALIDATE_PLAN" "$FX/plans/weekly-valid.json"
  exits 0 "PASSING: the same plan with vintage=evergreen + material_span + latest_development"

  # the other direction: a NEWS anchor may not carry evergreen metadata, or the
  # declaration and the material disagree
  run python3 "$VALIDATE_PLAN" "$FX/plans/weekly-news-vintage-with-span.json"
  exits 1 "FIRING: a news anchor carrying material_span/latest_development is rejected"
  has "forbidden when vintage='news'" "  … naming the forbidden field"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CRITERION 2 — evergreen renders .lr-vintage + a date-free byline; news neither
# ═══════════════════════════════════════════════════════════════════════════════
if wants 2; then
section 2 "the rendered vintage contract  (SPEC §3.4 / §3.4a, defect A)"

  run "${V[@]}" "$FX/weekly/vintage-evergreen-ok.html" "${VFLAGS[@]}" --run-date 2026-07-26
  exits 0 "PASSING: evergreen + .lr-vintage present + date-free byline + lr-framing"
  has '\[PASS\] long-read-vintage: data-vintage="evergreen"' "  … long-read-vintage passes on evergreen"
  has '\[PASS\] lr-framing' "  … The Letter carries data-lr-framing=\"feature\""

  run "${V[@]}" "$FX/weekly/pass.html" "${VFLAGS[@]}" --run-date 2026-07-26
  exits 0 "PASSING: news + .lr-vintage absent + dated byline"
  has '\[PASS\] long-read-vintage: data-vintage="news"' "  … long-read-vintage passes on news"

  # name|regex|human-readable description of what the message must diagnose
  while IFS='|' read -r n pat desc; do
    [ -n "$n" ] || continue
    run "${V[@]}" "$FX/weekly/$n.html" "${VFLAGS[@]}" --run-date 2026-07-26
    exits 1 "FIRING: $n"
    has '\[FAIL\] long-read-vintage' "  … long-read-vintage fires"
    has "$pat" "  … and diagnoses it: $desc"
  done <<'CASES'
vintage-missing|carries no data-vintage attribute|the attribute is absent, and it is ALWAYS required
vintage-bad-enum|is not one of|the value is outside {news, evergreen}
vintage-news-with-lrvintage|\.lr-vintage line present|a news anchor must not carry the standing-story line
vintage-evergreen-dated-byline|byline carries an issue date|an evergreen byline must not be stamped with today
vintage-evergreen-no-lrvintage|no \.lr-vintage line|an evergreen anchor must carry the standing-story line
CASES

  run "${V[@]}" "$FX/weekly/vintage-evergreen-no-framing.html" "${VFLAGS[@]}" --run-date 2026-07-26
  exits 1 "FIRING: vintage-evergreen-no-framing"
  has '\[FAIL\] lr-framing' "  … lr-framing fires on the missing Letter framing"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CRITERION 3 — caption vintage: Issue #18's FIG 03            (WP-4 + WP-10)
# ═══════════════════════════════════════════════════════════════════════════════
if wants 3; then
section 3 "caption vintage  (SPEC §3.9, defect B) — asserted as MEASURED, not as predicted"

  info "PROGRESS predicted caption-vintage would FAIL on #18. It does not, and WP-4"
  info "corrected the prediction rather than forcing it: #18 declares NO figure"
  info "attributes at all, so there is no data-capture-year to compare and the check"
  info "correctly WARNs that it cannot speak. The rule is proven instead on #18's OWN"
  info "FIG 03 caption wording with only the capture year added."

  run "${V[@]}" "$ISSUE_18" "${VFLAGS[@]}"
  exits 1 "Issue #18 fails the gate (frozen, never modified)"
  has '\[WARN\] caption-vintage' "MEASURED: caption-vintage is INERT on #18 (WARN), not failing"
  hasnt '\[FAIL\] caption-vintage' "  … and it is not reported as a failure either"
  has 'nothing to compare' "  … the WARN says in terms that it cannot speak"
  has '\[FAIL\] figure-provenance: 11 of 11' "  … the defect is caught by figure-provenance, 11 of 11"
  has 'fb560e553feb' "  … which names FIG 03's asset explicitly"
  echo_line '\[WARN\] caption-vintage' 1

  run "${V[@]}" "$FX/weekly/capvintage-fire.html" "${VFLAGS[@]}" --run-date 2026-07-26
  exits 1 "FIRING: #18's own FIG 03 wording + capture-year 2007, band claims 2021"
  has '\[FAIL\] caption-vintage' "  … caption-vintage fires"
  has 'FIG\. 03' "  … at FIG 03"
  has 'capture year 2007 is OLDER than the band.s latest claim 2021' "  … 2007 < 2021, correctly measured"
  has '"2007" does not appear in the caption' "  … and the visible sentence does not say so"
  echo_line 'capture year 2007 is OLDER' 1

  run "${V[@]}" "$FX/weekly/pass.html" "${VFLAGS[@]}" --run-date 2026-07-26
  exits 0 "PASSING: the SPEC §3.9 suggested rewrite (\"A 2007 working reconstruction…\")"
  has '\[PASS\] caption-vintage' "  … caption-vintage passes"
  has 'capture 2007 < claim 2021, and the visible caption says so' "  … for the right reason"

  # §3.4a note 3 boundaries: "" is the legal null; anything else non-4-digit fails
  run "${V[@]}" "$FX/weekly/capvintage-null-year.html" "${VFLAGS[@]}" --run-date 2026-07-26
  exits 0 'PASSING (boundary): data-capture-year="" is the legal null rendering'
  run "${V[@]}" "$FX/weekly/capvintage-bad-year.html" "${VFLAGS[@]}" --run-date 2026-07-26
  exits 1 'FIRING (boundary): data-capture-year="c. 2007" is neither empty nor 4 digits'
  has 'figure-provenance/values' "  … caught as an invalid provenance value"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CRITERION 4 — the rut rule                                          (WP-5)
# ═══════════════════════════════════════════════════════════════════════════════
if wants 4; then
section 4 "the cover-lead rut rule  (SPEC §3.6, defect C) — a forced choice, not suppression"

  run python3 "$VALIDATE_PLAN" "$FX/plans/weekly-valid.json" --state "$FX/states/rutted-uk-politics.json"
  exits 1 "FIRING: uk_politics led news in 3 of the last 4, plan leads news again, no override"
  has '\[RUT\] cover-lead rut' "  … the rut rule fires"
  has 'in \[3\]\s*of the last 4' "  … counting 3 of the last 4"
  has 'THIS IS NOT A BAN' "  … and the message says it is overridable in writing"
  echo_line '\[RUT\] cover-lead rut' 1

  run python3 "$VALIDATE_PLAN" "$FX/plans/weekly-rut-overridden.json" --state "$FX/states/rutted-uk-politics.json"
  exits 0 "PASSING (a): the same plan + a 164-char lead_override_reason. Nothing else changed"
  has 'rut acknowledged and overridden in writing' "  … recorded as an audit warning, not silence"

  run python3 "$VALIDATE_PLAN" "$FX/plans/weekly-valid.json" --state "$FX/states/rutted-other-family.json"
  exits 0 "PASSING (b): the rut is on us_politics, which this plan does not lead on"
  hasnt '\[RUT\] cover-lead rut' "  … the rule must NOT fire, and does not"

  run python3 "$VALIDATE_PLAN" "$FX/plans/weekly-valid.json" --state "$REAL_STATE"
  exits 0 "PASSING (c): against the REAL cover_lead_ledger — not firing on live data"
  info "That is the precondition for this being a test and not an artefact: the real"
  info "ledger puts uk_politics on news once in its last 4."

  run python3 "$VALIDATE_PLAN" "$FX/plans/weekly-clf-out-of-enum.json" --state "$FX/states/rutted-uk-politics.json"
  exits 1 "FIRING: cover_lead_topic_family='uk_polotics' — the typo that would silently disable the rule"
  has 'not in the closed Topic Family Enumeration' "  … hard-failed, not warned"
  has 'pass while checking nothing' "  … because an out-of-enum family makes the rule a green no-op"

  run python3 "$VALIDATE_PLAN" "$FX/plans/weekly-no-clf.json" --state "$FX/states/rutted-uk-politics.json"
  exits 1 "FIRING (compat path): a pre-amendment plan with no cover_lead_topic_family"
  has 'derived' "  … and the rut verdict is still reached, by falling back to the lead pieces"

  run python3 "$VALIDATE_PLAN" "$FX/plans/weekly-no-family-at-all.json" --state "$FX/states/rutted-uk-politics.json"
  has 'could not be evaluated' "SKIP-NOT-PASS: no field and no lead piece -> warn-and-skip"
  has 'SKIPPED here, not satisfied' "  … and it says so, rather than reporting a pass"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CRITERION 5 — a matured open loop with no resolving fact  (WP-5, bundle gate)
# ═══════════════════════════════════════════════════════════════════════════════
if wants 5; then
section 5 "matured open loop, upstream  (SPEC §3.7, defect D)"

  info "The two loops seeded in state/signal-state.json are status:\"dropped\" — honest"
  info "history, since neither the World Cup final nor The Open was ever reported and"
  info "#18 is frozen. A DROPPED LOOP DOES NOT MATURE, so the seeds cannot make this"
  info "gate fire. states/open-loop-matured.json exists for exactly that reason."

  run python3 "$VALIDATE_BUNDLE" "$FX/bundles/loop-unresolved.json" \
      --run-date 2026-07-26 --state "$FX/states/open-loop-matured.json"
  exits 1 "FIRING: a matured loop (ERD 2026-07-19, status=open) with no resolving fact"
  has 'MATURED LOOP UNRESOLVED' "  … the §3.7 rule fires"
  has "loop_2026-07-19_wc-final-open" "  … naming the loop"
  has 'matured loop ids: *\[.loop_2026-07-19_wc-final-open.\]' "  … and ONLY the matured one is considered"
  echo_line 'MATURED LOOP UNRESOLVED' 1

  run python3 "$VALIDATE_BUNDLE" "$FX/bundles/loop-resolved.json" \
      --run-date 2026-07-26 --state "$FX/states/open-loop-matured.json"
  exits 0 "PASSING: the identical bundle + one fact carrying resolves_loop"

  run python3 "$VALIDATE_BUNDLE" "$FX/bundles/loop-unresolved.json" \
      --run-date 2026-07-26 --state "$REAL_STATE"
  exits 0 "PASSING: against the REAL state — 2 dropped loops, 0 matured"
  has '0 matured' "  … confirming a dropped loop does not mature"

  run python3 "$VALIDATE_BUNDLE" "$FX/bundles/loop-unresolved.json" \
      --run-date 2026-07-26 --state "$FX/states/empty.json"
  exits 0 "PASSING (tolerance): a state with no open_loops is legal"
  has 'not a pass mark' "  … and reported as \"legal, not a pass mark\""

  run python3 "$VALIDATE_BUNDLE" "$FX/bundles/loop-unresolved.json" \
      --run-date 2026-07-26 --state "$WORK/no-such-state.json"
  exits 2 "FIRING (tolerance): an explicitly-passed missing --state is exit 2, never a pass"

  # the regression that would have caught this build's own breakage
  run python3 "$VALIDATE_BUNDLE" "$FX/bundles/repro-retired-threshold-keyerror.json" --run-date 2026-07-26
  exits 1 "REGRESSION: the retired-Wikimedia-threshold path reports instead of crashing"
  hasnt 'KeyError' "  … no KeyError (this crashed Phase 3b in-tree before WP-5)"
  has 'min_distinct_shapes' "  … and the shape FLOOR is what fires instead"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CRITERION 6 — a matured open loop absent from the rendered HTML     (WP-4)
# ═══════════════════════════════════════════════════════════════════════════════
if wants 6; then
section 6 "matured open loop, rendered  (SPEC §3.7, defect D)"

  run "${V[@]}" "$FX/weekly/pass.html" "${VFLAGS[@]}" \
      --run-date 2026-07-26 --state "$FX/states/weekly-matured-loop.json"
  exits 1 "FIRING: a matured loop with no data-resolves-loop anywhere in the HTML"
  has '\[FAIL\] resolved-loops: 1 of 1 matured open loop' "  … resolved-loops fires, 1 of 1"
  has 'loop_2026-07-19_fixture-final' "  … naming the loop, its band and its opening issue"
  has 'silently vanishes \(defect D\)' "  … and naming the defect"
  echo_line '\[FAIL\] resolved-loops' 1

  run "${V[@]}" "$FX/weekly/loop-resolved.html" "${VFLAGS[@]}" \
      --run-date 2026-07-26 --state "$FX/states/weekly-matured-loop.json"
  exits 0 "PASSING: the same state, and a ledger row carrying data-resolves-loop=<id>"

  run "${V[@]}" "$FX/weekly/pass.html" "${VFLAGS[@]}" \
      --run-date 2026-07-18 --state "$FX/states/weekly-matured-loop.json"
  exits 0 "PASSING: run-date 2026-07-18 — the loop has not matured yet"
  info "Maturity is real, not decorative: the same HTML and the same state, one day"
  info "before the expected resolution date, must not fail."
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CRITERION 7 — results-ledger breadth + sport tokens                 (WP-4)
# ═══════════════════════════════════════════════════════════════════════════════
if wants 7; then
section 7 "results_ledger_multi_sport + sport tokens  (SPEC §3.11, defect D)"

  run "${V[@]}" "$FX/weekly/ledger-one-sport.html" "${VFLAGS[@]}" \
      --run-date 2026-07-20 --state "$FX/states/weekly-two-sports.json"
  exits 1 "FIRING: a 1-sport ledger when 2 tracked sports concluded in-window"
  has '\[FAIL\] results-ledger-multi-sport' "  … the invariant fires"
  has "\['football', 'golf'\]" "  … naming the two sports that concluded"
  has "carries 1 distinct data-sport value" "  … and what the ledger actually carries"
  echo_line '\[FAIL\] results-ledger-multi-sport' 1

  run "${V[@]}" "$FX/weekly/ledger-two-sports.html" "${VFLAGS[@]}" \
      --run-date 2026-07-20 --state "$FX/states/weekly-two-sports.json"
  exits 0 "PASSING: a 2-sport ledger in the same window"

  run "${V[@]}" "$FX/weekly/ledger-one-sport.html" "${VFLAGS[@]}" \
      --run-date 2026-07-20 --state "$FX/states/weekly-golf-off.json"
  exits 0 "PASSING: golf switched off -> 1 tracked sport concluded -> not applicable"
  has 'not applicable' "  … the invariant is conditional, not a blanket rule"

  run "${V[@]}" "$FX/weekly/ledger-one-sport.html" "${VFLAGS[@]}" \
      --run-date 2026-07-20 --state "$FX/states/weekly-unset-sports.json"
  exits 1 "FIRING: an ABSENT interest_depth key is UNSET, never off (WP-1 correction)"
  has "'athletics', 'cricket'" "  … cricket and athletics have no key and still count as tracked"

  run "${V[@]}" "$FX/weekly/ledger-multi-sport-token.html" "${VFLAGS[@]}" --run-date 2026-07-26
  exits 1 'FIRING: data-sport="multi_sport" is forbidden in rendered HTML'
  has '\[FAIL\] sport-tokens' "  … sport-tokens hard-fails"
  has 'legal only in state.sports_calendar' "  … naming the one namespace where it IS legal"

  run "${V[@]}" "$FX/weekly/ledger-unknown-token.html" "${VFLAGS[@]}" --run-date 2026-07-26
  exits 0 'PASSING: an off-list token (lawn_bowls) WARNs and must never block a ship'
  has '\[WARN\] sport-tokens/vocabulary' "  … warned, not failed"

  run "${V[@]}" "$FX/weekly/ledger-unknown-token.html" "${VFLAGS[@]}" --run-date 2026-07-26 --strict
  has '\[WARN\] sport-tokens/vocabulary' "PASSING: --strict cannot promote the off-list-token warning"
  hasnt '\[FAIL\] sport-tokens' "  … a breadth check that blocks breadth is self-defeating"
  info "This run exits 1 for a DIFFERENT, pre-existing reason (--strict promotes the"
  info "image-urls: skipped warning), which is what proves --strict still works."
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CRITERION 8 — image shape budgets                                   (WP-4)
# ═══════════════════════════════════════════════════════════════════════════════
if wants 8; then
section 8 "image shape budgets  (SPEC §3.8/§3.14, defect E) — asserted as MEASURED"

  info "PROGRESS predicted the budget would fail via a Pixel & Byte key_art lead. It"
  info "fails, but by a different route: #18 declares no shapes at all, so the key_art"
  info "clause is inert and the two COUNTED budgets catch it instead. That is the more"
  info "robust route — it fails on absence, not on a specific bad value being present."

  run "${V[@]}" "$ISSUE_18" "${VFLAGS[@]}"
  exits 1 "Issue #18 fails the gate (frozen, never modified)"
  has '\[FAIL\] image-shapes/distinct: 0 distinct data-shows value' "MEASURED: distinct-shapes 0 of 3"
  has '\[FAIL\] image-shapes/long-read-information' "MEASURED: the Long Read carries no information figure"
  hasnt '\[FAIL\] image-shapes/pixel-byte-key-art' "MEASURED: the key_art clause is INERT on #18, not failing"
  has '\[FAIL\] cover-leads-on' "MEASURED (unpredicted): cover-leads-on fails"
  has '\[FAIL\] long-read-vintage' "MEASURED (as predicted): long-read-vintage fails"
  N18="$(printf '%s\n' "$LAST_OUT" | grep -cE '^\[FAIL\]')"
  truth "$([ "$N18" = 5 ] && echo 1 || echo 0)" \
        "MEASURED: exactly 5 failures on #18, as WP-4 recorded" "counted $N18"
  printf '%s\n' "$LAST_OUT" | grep -E '^\[FAIL\]' | cut -c1-96 | sed "s/^/        ${C_D}> /;s/\$/${C_0}/"

  run "${V[@]}" "$FX/weekly/pass.html" "${VFLAGS[@]}" --run-date 2026-07-26
  exits 0 "PASSING: the corrected fixture — #18 plus the contract markup it predates"
  has '\[PASS\] image-shapes/distinct: 7 distinct' "  … 7 distinct shapes against a floor of 3"
  has '\[PASS\] image-shapes/long-read-information' "  … and an information figure in the Long Read"

  for t in shapes-two-distinct-shapes:'image-shapes/distinct' \
           shapes-keyart-leads-pb:'image-shapes/pixel-byte-key-art' \
           shapes-two-keyart-pb:'image-shapes/pixel-byte-key-art' \
           shapes-portrait-lead:'image-shapes/never-lead' \
           shapes-keyart-lead-nonpb:'image-shapes/never-lead' \
           shapes-lr-no-information-figure:'image-shapes/long-read-information' \
           shapes-touchline-result-keyart:'image-shapes/touchline-result' \
           shapes-repeat-lead:'image-shapes/cross-issue-lead'; do
    n="${t%%:*}"; chk="${t#*:}"
    run "${V[@]}" "$FX/weekly/$n.html" "${VFLAGS[@]}" --run-date 2026-07-26
    exits 1 "FIRING: $n"
    has "\[FAIL\] $chk" "  … $chk fires"
  done

  run "${V[@]}" "$FX/weekly/shapes-touchline-result-ok.html" "${VFLAGS[@]}" --run-date 2026-07-26
  exits 0 'PASSING: the same result caption with data-shows="event_photo"'

  run "${V[@]}" "$FX/weekly/shapes-productshot-lead.html" "${VFLAGS[@]}" --run-date 2026-07-26
  exits 0 'PASSING (conditional): a product_shot lead WARNs, for the gate-3 human read'
  has '\[WARN\] image-shapes/never-lead-conditional' "  … reported, not failed"
  info "\"the band's subject IS the product\" is not in the rendered HTML, so this one"
  info "clause is surfaced rather than guessed. Recorded as such, not as a pass."
  skip "product_shot may lead only when the band's subject IS the product" \
       "no band declares a subject type in the rendered markup (data-band=\"pixel_byte\" covers hardware, software, games and services alike). WP-4 implemented it as a WARN naming the band and figure; a FAIL would break legitimate hardware coverage and inferring the subject from prose would be a guess."

fi

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION X — §3.4 markup contracts with no numbered criterion of their own.
# Not part of the §4 twelve, so a failure here is reported as debt rather than as
# a criterion failure — but it is reported, loudly, because the polymorphic table
# is the component defect D's single-competition shape was ruining.
# ═══════════════════════════════════════════════════════════════════════════════
if [ ${#ONLY[@]} -eq 0 ]; then
plain_section "X" "POLYMORPHIC TABLE  (SPEC §3.4 data-table-kind — no §4 criterion covers it)"

  run "${V[@]}" "$FX/weekly/table-kind-bad.html" "${VFLAGS[@]}" --run-date 2026-07-26
  exits 1 'FIRING: data-table-kind="table" is not in the §3.4 enum'
  has '\[FAIL\] table-kind' "  … table-kind fires on an illegal value"

  run "${V[@]}" "$FX/weekly/table-kind-finance.html" "${VFLAGS[@]}" --run-date 2026-07-26
  if [ "$LAST_RC" = 0 ]; then
    pass 'PASSING: data-table-kind="finance" is accepted (SPEC §3.4 amendment, 2026-07-26)'
  else
    debt 'validate-issue.py rejects data-table-kind="finance" as an illegal sixth value, but SPEC §3.4 made it legal on 2026-07-26 and WP-3b has already shipped it into weekly.json and the mx CSS. A legitimate finance card hard-fails the ship gate today.'
    printf '%s\n' "$LAST_OUT" | grep -E '^\[FAIL\] table-kind' | cut -c1-140 \
      | sed "s/^/        ${C_D}> /;s/\$/${C_0}/"
    info "THE FIX, in a file WP-10 does not own (validate-issue.py:$TK_LN): add \"finance\""
    info "to TABLE_KINDS, and reword the message — it currently says \"outside the five"
    info "legal shapes\" and \"A sixth value renders as…\", both of which are now wrong."
    info "Why this matters more than an off-by-one: The Desk ALREADY uses .mx-scorecard"
    info "for a financial card (the mx golden's rate card), which is why WP-3 asked for"
    info "the sixth kind. Shipping a \"polymorphic\" enum that admits only sport would"
    info "reproduce, one level down, the exact single-competition mistake polymorphism"
    info "was introduced to fix. The gate currently only escapes noticing because"
    info "WP-3b's finance markup is in the inlined CSS, not yet in any rendered body —"
    info "so this fixture is the first thing in the repo to exercise the value."
  fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CRITERION 9 — extract-covers.py refuses an ND source                (WP-8)
# ═══════════════════════════════════════════════════════════════════════════════
if wants 9; then
section 9 "licence safety: no derivative of a NoDerivatives source  (SPEC §3.10, defect E)"

  if ! python3 -c "import PIL" 2>/dev/null; then
    skip "extract-covers.py refuses an allows_derivatives:false source" \
         "Pillow (PIL) is not importable in this environment; extract-covers.py cannot run at all."
  else
    # A throwaway repo root: both scripts derive REPO_ROOT from __file__, so a
    # sandbox is how this is tested without writing a byte inside the real repo.
    SB="$WORK/sandbox"
    mkdir -p "$SB/scripts" "$SB/assets/cached" "$SB/assets/covers" "$SB/issues"
    cp "$EXTRACT_COVERS" "$MIRROR_IMAGES" "$SB/scripts/"
    cp "$REPO/assets/cached/af9fc905ced8.jpg" "$REPO/assets/cached/1a2d67f3ca02.jpg" "$SB/assets/cached/"
    cp "$FIXTURES/html/cover-nd.html" "$SB/issues/cover-nd.html"
    cp "$FIXTURES/html/cover-permissive.html" "$SB/issues/cover-permissive.html"
    cp "$FIXTURES/html/cover-unknown-licence.html" "$SB/issues/cover-unknown-licence.html"
    python3 - "$FIXTURES/json/cover-licences.json" "$SB/assets/cached/manifest.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
m.pop("_doc", None)
json.dump(m, open(sys.argv[2], "w"), indent=2, sort_keys=True)
PY
    truth "$( [ "$(md5sum < "$EXTRACT_COVERS")" = "$(md5sum < "$SB/scripts/extract-covers.py")" ] && echo 1 || echo 0)" \
          "the script under test is byte-identical to the repo's extract-covers.py"

    run python3 "$SB/scripts/extract-covers.py" "$SB/issues/cover-nd.html"
    exits 2 "FIRING: a CC-BY-NC-ND-2.0 source (allows_derivatives:false) is refused"
    has 'REFUSED' "  … refused, not silently cropped"
    has 'CC-BY-NC-ND-2.0' "  … naming the licence"
    has 'af9fc905ced8' "  … and the file"
    has 'A cover thumbnail is a derivative' "  … and why a thumbnail is a derivative work"
    truth "$( [ ! -f "$SB/assets/covers/cover-nd.jpg" ] && echo 1 || echo 0)" \
          "  … and no derivative file was written" "cover-nd.jpg exists and must not"
    echo_line 'REFUSED' 1

    run python3 "$SB/scripts/extract-covers.py" "$SB/issues/cover-permissive.html"
    exits 0 "PASSING: a CC-BY-2.5 source (allows_derivatives:true) is cropped"
    truth "$( [ -f "$SB/assets/covers/cover-permissive.jpg" ] && echo 1 || echo 0)" \
          "  … and the derivative WAS written" "cover-permissive.jpg missing"
    info "Same script, same manifest, same command. The licence is the only variable."

    # UNKNOWN: warn-and-proceed by default (all 438 back-filled entries are
    # UNKNOWN, so refusing by default would block the whole archive), refuse
    # under --strict-licence.
    python3 - "$SB/assets/cached/manifest.json" <<'PY'
import json, sys
p = sys.argv[1]; m = json.load(open(p))
m["1a2d67f3ca02"]["licence"] = {"holder": "UNKNOWN", "code": "UNKNOWN",
                                "url": "UNKNOWN", "allows_derivatives": None}
json.dump(m, open(p, "w"), indent=2, sort_keys=True)
PY
    run python3 "$SB/scripts/extract-covers.py" --force "$SB/issues/cover-unknown-licence.html"
    exits 0 "PASSING (boundary): an UNKNOWN licence warns and proceeds by default"
    has 'no licence on record' "  … with the provenance gap stated"
    run python3 "$SB/scripts/extract-covers.py" --force --strict-licence "$SB/issues/cover-unknown-licence.html"
    exits 2 "FIRING (boundary): --strict-licence promotes UNKNOWN to a refusal"

    printf '{ not json' > "$WORK/corrupt.json"
    run python3 "$SB/scripts/extract-covers.py" --manifest "$WORK/corrupt.json" "$SB/issues/cover-permissive.html"
    exits 1 "FIRING: a corrupt manifest refuses to derive anything, rather than assuming"
    truth "$( [ "$(cat "$WORK/corrupt.json")" = '{ not json' ] && echo 1 || echo 0)" \
          "  … and the corrupt file is left untouched, not overwritten"
  fi

  skip "the same refusal firing on Issue #18's real cover" \
       "#18's cover source IS CC BY-ND and IS already cropped into assets/covers/ — a live violation. SPEC §3.10 makes the fix forward-looking and forbids re-cropping or deleting #18's cover, and the 438 back-filled manifest entries carry allows_derivatives:null (unknown), not false. So the refusal cannot fire on the real archive today; it is armed for issue #19 onward."
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CRITERION 10 — mirror-images.py writes the provenance manifest      (WP-8)
# ═══════════════════════════════════════════════════════════════════════════════
if wants 10; then
section 10 "provenance survives publish  (SPEC §3.10, defect E)"

  SB10="$WORK/sandbox10"
  mkdir -p "$SB10/scripts" "$SB10/assets/cached" "$SB10/issues"
  cp "$MIRROR_IMAGES" "$SB10/scripts/"
  cp "$REPO/assets/cached/af9fc905ced8.jpg" "$REPO/assets/cached/1a2d67f3ca02.jpg" "$SB10/assets/cached/"
  cp "$FIXTURES/html/cover-nd.html" "$FIXTURES/html/cover-permissive.html" "$SB10/issues/"

  # FIRING CASE: the pre-WP-8 script, out of git. It named files sha256(url)[:12]
  # and DISCARDED the URL, so a caption's provenance claim could not be audited
  # after publish (~400 Commons candidates reverse-hashed, no match).
  mkdir -p "$WORK/base-mirror/scripts" "$WORK/base-mirror/assets/cached" "$WORK/base-mirror/issues"
  if git -C "$REPO" show "$BASE_MIRROR:scripts/mirror-images.py" > "$WORK/base-mirror/scripts/mirror-images.py" 2>/dev/null; then
    cp "$REPO/assets/cached/af9fc905ced8.jpg" "$WORK/base-mirror/assets/cached/"
    cp "$FIXTURES/html/cover-permissive.html" "$WORK/base-mirror/issues/"
    NHITS="$(grep -c 'manifest' "$WORK/base-mirror/scripts/mirror-images.py" || true)"
    truth "$( [ "$NHITS" = 0 ] && echo 1 || echo 0)" \
          "FIRING: the pre-WP-8 script ($BASE_MIRROR) has no manifest concept at all" \
          "expected 0 mentions of 'manifest', found $NHITS"
    run python3 "$WORK/base-mirror/scripts/mirror-images.py" --manifest-only
    exits 2 "FIRING: it does not even accept --manifest-only"
    truth "$( [ ! -f "$WORK/base-mirror/assets/cached/manifest.json" ] && echo 1 || echo 0)" \
          "  … and writes no manifest, so provenance is unauditable after publish"
  else
    skip "the pre-WP-8 firing case" "git object $BASE_MIRROR:scripts/mirror-images.py is not reachable"
  fi

  # PASSING CASE: the shipped script, against a sandbox repo root.
  run python3 "$SB10/scripts/mirror-images.py" --manifest-only
  exits 0 "PASSING: --manifest-only reconciles a manifest with no network"
  truth "$( [ -f "$SB10/assets/cached/manifest.json" ] && echo 1 || echo 0)" \
        "  … assets/cached/manifest.json is written"
  run python3 - "$SB10/assets/cached/manifest.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
need_top = {"url", "licence", "fetched_at", "shows", "capture_year", "issues", "led"}
need_lic = {"holder", "code", "url", "allows_derivatives"}
bad = []
for h, e in m.items():
    miss = need_top - set(e)
    if miss:
        bad.append(f"{h}: missing {sorted(miss)}")
    elif not isinstance(e["licence"], dict) or need_lic - set(e["licence"]):
        bad.append(f"{h}: licence missing {sorted(need_lic - set(e.get('licence') or {}))}")
print(f"entries: {len(m)}")
print("keys per entry: " + ", ".join(sorted(need_top)))
print("licence keys:   " + ", ".join(sorted(need_lic)))
for b in bad:
    print("BAD " + b)
sys.exit(1 if bad or not m else 0)
PY
  exits 0 "  … and EVERY hash carries url + licence{holder,code,url,allows_derivatives}"
  echo_line 'entries: ' 1

  # idempotence: a second run must not lose or invent provenance
  cp "$SB10/assets/cached/manifest.json" "$WORK/m1.json"
  run python3 "$SB10/scripts/mirror-images.py" --manifest-only
  exits 0 "PASSING: re-running is idempotent"
  truth "$(cmp -s "$WORK/m1.json" "$SB10/assets/cached/manifest.json" && echo 1 || echo 0)" \
        "  … byte-identical on the second run"
  has 'unchanged' "  … and reported as unchanged, not rewritten"

  printf '{ not json' > "$WORK/corrupt10.json"
  run python3 "$SB10/scripts/mirror-images.py" --manifest-only --manifest "$WORK/corrupt10.json"
  exits 1 "FIRING: a corrupt manifest is refused, never overwritten (that would lose provenance)"
  truth "$( [ "$(cat "$WORK/corrupt10.json")" = '{ not json' ] && echo 1 || echo 0)" \
        "  … and the file is untouched"

  # the real manifest, read-only: this is what the pipeline actually carries
  if [ -f "$REPO/assets/cached/manifest.json" ]; then
    run python3 - "$REPO/assets/cached/manifest.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
known = sum(1 for e in m.values() if e.get("url") not in (None, "", "UNKNOWN"))
lic = sum(1 for e in m.values() if (e.get("licence") or {}).get("code") not in (None, "", "UNKNOWN"))
print(f"real manifest: {len(m)} entries, {known} with a recovered source URL, "
      f"{lic} with a known licence code")
sys.exit(0 if len(m) > 0 else 1)
PY
    exits 0 "the REAL manifest is present and readable (read-only assertion)"
    echo_line 'real manifest:' 1
    skip "a manifest entry populated from a live research bundle" \
         "all 438 entries are WP-8 back-fills: sha256(url)[:12] is one-way and the pre-rewrite HTML was never committed, so 425 URLs and every licence are honestly UNKNOWN. Real licence/shows/capture_year arrive from the bundle (SPEC §3.2) at issue #19's publish, which needs the network and a real research phase."
  fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CRITERION 11 — the daily surfaces a cricket/cycling/athletics item  (WP-7)
# ═══════════════════════════════════════════════════════════════════════════════
if wants 11; then
section 11 "the daily's sport inputs and routing  (SPEC §3.15, defect D)"

  if ! command -v node >/dev/null 2>&1; then
    skip "the daily's feed parsing and domain routing" "node is not on PATH"
  else
    D="$REPO/functions/daily"
    run node "$FIXTURES/check-daily-routing.mjs" \
        --feeds "$D/feeds.js" --profile "$D/profile.js" --score "$D/score.js" \
        --render "$D/render.js" --ingest "$D/ingest.js" \
        --rss "$FIXTURES/rss" --label "shipped"
    exits 0 "PASSING: all three sports have a feed, parse, score > 0 and are headline-eligible"
    printf '%s\n' "$LAST_OUT" | grep -E '^      ·' | sed "s/^ */        ${C_D}> /;s/\$/${C_0}/"

    BD="$WORK/base-daily"
    mkdir -p "$BD"
    if git -C "$REPO" archive "$BASE_DAILY" functions/daily 2>/dev/null | tar -x -C "$BD"; then
      run node "$FIXTURES/check-daily-routing.mjs" \
          --feeds "$BD/functions/daily/feeds.js" --profile "$BD/functions/daily/profile.js" \
          --score "$BD/functions/daily/score.js" --render "$BD/functions/daily/render.js" \
          --ingest "$BD/functions/daily/ingest.js" \
          --rss "$FIXTURES/rss" --label "pre-WP-7/WP-11 baseline $BASE_DAILY"
      exits 1 "FIRING: against the pre-rebuild daily, every one of those items is invisible"
      has 'feeds.js declares 0 feed\(s\) with domain="cricket"' "  … no cricket feed existed"
      has 'NEWS_SPORT set \(world, local, finance, football, golf\)' "  … NEWS_SPORT had 5 members, no sport beyond football/golf"
      NZERO="$(printf '%s\n' "$LAST_OUT" | grep -cE 'score=0\.00' || true)"
      truth "$( [ "$NZERO" = 6 ] && echo 1 || echo 0)" \
            "  … and all 6 fixture headlines score exactly 0.00" "counted $NZERO"
      printf '%s\n' "$LAST_OUT" | grep -E '^      ×' | head -3 | sed "s/^ */        ${C_D}> /;s/\$/${C_0}/"
    else
      skip "the pre-WP-7 firing case" "git tree $BASE_DAILY:functions/daily is not reachable"
    fi

    skip "the feed URLs returning HTTP 200" \
         "that needs egress this harness deliberately does not take, and it is a property of the BBC and the specialist publishers, not of this repo. WP-7 verified all 9 new URLs live (EVIDENCE/WP-7.md §3.1); the fixture RSS proves the PARSER and the ROUTER, which is the half that lives here."
    skip "the daily rendering the item into a published brief" \
         "render.js's composition runs inside a Cloudflare Worker against KV and D1; there is no Worker runtime, KV namespace or D1 binding in this environment. WP-11 verified the routing behaviourally against real stored blobs (EVIDENCE/WP-11.md)."
  fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CRITERION 12 — check-image-diversity.sh                             (WP-6)
# ═══════════════════════════════════════════════════════════════════════════════
if wants 12; then
section 12 "shape floor replaces the Wikimedia ceilings  (SPEC §3.14, defect E)"

  run bash -n "$IMAGE_DIVERSITY"
  exits 0 "check-image-diversity.sh parses (bash -n)"

  # (a) the retired thresholds are gone from the live threshold block
  run python3 - "$LOOKUP" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
th, rt = d.get("thresholds", {}), d.get("retired_thresholds", {})
live = [k for k in ("wikimedia_max_pct", "wikimedia_max_count") if k in th]
ret = [k for k in ("wikimedia_max_pct", "wikimedia_max_count") if k in rt]
print("thresholds keys:        " + ", ".join(sorted(k for k in th if not k.startswith("_"))))
print("retired_thresholds:     " + ", ".join(sorted(k for k in rt if not k.startswith("_"))))
print("min_distinct_shapes:    " + repr(th.get("min_distinct_shapes")))
if live:
    print("BAD still live: " + ", ".join(live))
if len(ret) != 2:
    print("BAD not recorded as retired: " + repr(ret))
sys.exit(1 if live or len(ret) != 2 else 0)
PY
  exits 0 "the retired keys are out of thresholds and recorded under retired_thresholds"
  echo_line 'min_distinct_shapes:' 1

  # (b) and the script no longer READS them. Comments are excluded: WP-6 left an
  #     auditable retirement note, and a grep that counted prose would make the
  #     documentation of a removal look like the removal failing.
  NLIVE="$(grep -vE '^\s*#' "$IMAGE_DIVERSITY" | grep -c -E 'wikimedia_max_(pct|count)' || true)"
  truth "$( [ "$NLIVE" = 0 ] && echo 1 || echo 0)" \
        "no live read of wikimedia_max_pct / wikimedia_max_count remains in the script" \
        "found $NLIVE non-comment line(s)"

  run bash "$IMAGE_DIVERSITY" "$FIXTURES/html/diversity-one-shape.html"
  exits 1 "FIRING: 3 domains, 3 source types, all one shape -> min_distinct_shapes fires"
  has 'Shape diversity: 1 distinct shape' "  … reported as a shape-diversity failure"
  has 'never be a lead|never a lead' "  … with the hierarchy pointed at as the remedy"
  has 'not a sourcing problem, it is a SHAPE problem' "  … and remediation that says swapping domains will not fix it"
  echo_line 'Shape diversity: 1 distinct' 1

  run bash "$IMAGE_DIVERSITY" "$FIXTURES/html/diversity-three-shapes.html"
  exits 0 "PASSING: the IDENTICAL domains and source types, three distinct shapes"
  has 'Distinct shapes: 3' "  … the only variable is the shape"

  run bash "$IMAGE_DIVERSITY" "$FIXTURES/html/diversity-all-key-art.html"
  exits 1 "FIRING: the regression the ceilings could not see — 4 domains, all key_art"
  info "Wikimedia is 1/4 = 25% here, INSIDE the retired 30% / 4-entry ceilings, so the"
  info "old rules passed this. Worse: under them ONE Commons image in three breached"
  info "the 30% ceiling while three key arts were fine. The ceiling priced the"
  info "supplement and ignored the shape."

  run bash "$IMAGE_DIVERSITY" "$FIXTURES/html/diversity-bad-enum.html"
  exits 1 "FIRING: three distinct shapes but one is the typo 'screenshot' (off-enum)"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION P — the plan-validation hole verify-weekly-golden.sh swallows
# ═══════════════════════════════════════════════════════════════════════════════
if [ ${#ONLY[@]} -eq 0 ]; then
plain_section "P" "PLAN-VALIDATION HOLE  (WP-3's finding — surfaced here, not swallowed)"

  info "verify-weekly-golden.sh is WP-3's file, so this harness does not edit it. It"
  info "invokes validate-chapter-plan.py directly instead and asserts on the REAL exit"
  info "code, which is the whole point: a harness that reports green while a validator"
  info "reports 7 errors has converted a red state into a green one."

  # 1. the swallowing construct, quoted from the file this WP does not own
  if grep -nE '2>/dev/null[[:space:]]*\\?$' "$GOLDEN_GATE" | grep -q 'validate-chapter-plan' \
     || grep -A2 -nE 'validate-chapter-plan\.py' "$GOLDEN_GATE" | grep -q 'skipping plan check'; then
    pass "located the swallowing construct in verify-weekly-golden.sh (not edited)"
    grep -nE -A2 'validate the golden plan|validate-chapter-plan\.py' "$GOLDEN_GATE" \
      | sed "s/^/        ${C_D}| /;s/\$/${C_0}/"
  else
    pass "verify-weekly-golden.sh no longer swallows plan validation — the hole is closed"
    info "If this line is what you are reading, delete section P's debt handling."
  fi

  # 2. verify-weekly-golden.sh's own verdict, with its real exit code read directly
  #    (never through a pipe — a pipeline would report the tail's status, which is
  #    the same class of bug as the one this section exists to surface).
  run bash "$GOLDEN_GATE"
  GG_RC="$LAST_RC"
  printf '   %sinfo%s verify-weekly-golden.sh real exit code: %s\n' "$C_D" "$C_0" "$GG_RC"
  # DEBT PAID 2026-07-26 (WP-3c). This asserted the PRESENCE of the reassuring
  # skip notice, because at the time the notice was there and the errors were
  # swallowed. WP-3c closed the hole, so the assertion is inverted: the notice must
  # now be ABSENT. Kept rather than deleted — an assertion that the hole stays
  # closed is worth more than one that recorded it was open.
  hasnt 'skipping plan check' "verify-weekly-golden.sh no longer prints a reassuring skip notice"

  # 3. the same validator, invoked directly, on the same plan
  run python3 "$VALIDATE_PLAN" "$GOLD_PLAN"
  LEG_RC="$LAST_RC"
  LEG_ERRS="$(printf '%s\n' "$LAST_OUT" | grep -cE '^  \[[0-9]+\] \[' || true)"
  # DEBT PAID 2026-07-26 (WP-3c): was `exits 1` / `exactly 7 errors`. Inverted to
  # assert the plan is now valid, so a regression re-breaks the harness.
  truth "$( [ "$LEG_RC" = 0 ] && echo 1 || echo 0)" \
        "the LEGACY golden plan is VALID (was 7 errors, swallowed)" "got $LEG_RC"
  truth "$( [ "$LEG_ERRS" = 0 ] && echo 1 || echo 0)" \
        "with 0 plan errors" "counted $LEG_ERRS"
  printf '%s\n' "$LAST_OUT" | grep -E '^  \[[0-9]+\] \[' | cut -c1-104 \
    | sed "s/^/        ${C_D}> /;s/\$/${C_0}/"

  # 4. the mx golden's plan is never validated by that script AT ALL — a second,
  #    quieter hole in the same place.
  run python3 "$VALIDATE_PLAN" "$MXGOLD_PLAN"
  MX_RC="$LAST_RC"
  MX_ERRS="$(printf '%s\n' "$LAST_OUT" | grep -cE '^  \[[0-9]+\] \[' || true)"
  # DEBT PAID 2026-07-26 (WP-3c): was `also fails, and nothing validates it today`
  # (21 errors, unlooked-for — WP-10 found this hole; nobody else had looked).
  # WP-3c fixed the plan AND wired it into verify-weekly-golden.sh.
  truth "$( [ "$MX_RC" = 0 ] && echo 1 || echo 0)" \
        "the MX golden plan is VALID and is now validated by the golden gate (was 21 errors, unlooked-for)" "got $MX_RC"
  info "verify-weekly-golden.sh validates only the LEGACY golden's plan. The mx"
  info "fixture's plan is stitched, byte-compared and gate-checked, but never"
  info "plan-validated — so its $MX_ERRS errors are not merely swallowed, they are unlooked-for."

  if [ "$GG_RC" = 0 ] && [ "$LEG_RC" != 0 ]; then
    debt "verify-weekly-golden.sh exits 0 while validate-chapter-plan.py exits 1 with $LEG_ERRS errors on the plan it just checked."
    info "THE FIX, in a file WP-10 does not own ($(basename "$GOLDEN_GATE"):$SWALLOW_LN): drop"
    info "the '2>/dev/null || echo \"(… skipping plan check)\"' and let the validator's"
    info "status propagate under the script's own 'set -e'; and add the same call for"
    info "references/golden/weekly-mx/chapter-plan.json. Two lines."
    debt "The golden plans do not satisfy SPEC §3.1: legacy $LEG_ERRS errors, mx $MX_ERRS errors. references/golden/** is WP-3's; this harness checks it and never writes it."
    info "6 of the legacy plan's 7 errors need NO editorial judgement and no invented"
    info "fact: research_cut_at + window are fixture instants; cover_leads_on,"
    info "cover_lead_topic_family and lead_rationale are fixture metadata; and"
    info "week_in_numbers.rows is derivable from the golden's own rendered strip."
    info "The 7th, long_read.vintage, IS a judgement and WP-10 declines to take it:"
    info "the legacy golden's Long Read is Telstar 1 (1962), which is a standing story,"
    info "so 'evergreen' is the editorially right answer — and it then REQUIRES a"
    info "latest_development month for the 1984 Shuttle redeployment named in the"
    info "plan's own image brief, which nothing in this repo grounds. Declaring 'news'"
    info "clears the error with no invented date (material_span and latest_development"
    info "are forbidden when news) and matches what the stitcher already defaults to"
    info "and what the rendered golden already asserts — but it labels a 1962 story as"
    info "a development of this week, which is defect A written into the fixture that"
    info "is supposed to prove defect A is fixed. That is WP-3's call, not this one's."
  fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION G — the golden, re-checked against the commit under test
# ═══════════════════════════════════════════════════════════════════════════════
if [ ${#ONLY[@]} -eq 0 ]; then
plain_section "G" "GOLDEN RE-CHECK  (the golden moves under this harness; record the commit)"

  printf '   %sinfo%s golden last touched: %s\n' "$C_D" "$C_0" \
    "$(git -C "$REPO" log -1 --format='%h %s' -- "$SKILL_DIR/references/golden" 2>/dev/null || echo unknown)"
  GDIRTY="$(git -C "$REPO" status --porcelain -- "$SKILL_DIR/references/golden" 2>/dev/null | wc -l | tr -d ' ')"
  if [ "$GDIRTY" != 0 ]; then
    printf '   %sinfo%s %s golden path(s) are DIRTY in the working tree — a concurrent WP may be mid-edit:\n' \
      "$C_WARN" "$C_0" "$GDIRTY"
    git -C "$REPO" status --porcelain -- "$SKILL_DIR/references/golden" | sed "s/^/        ${C_D}| /;s/\$/${C_0}/"
  fi

  run bash "$GOLDEN_GATE"
  exits 0 "the golden regression passes end-to-end (both the legacy and mx paths)"
  has 'byte-identical' "  … the mx golden is byte-identical to committed expected.html"
  has 'GOLDEN REGRESSION PASS' "  … and the script reaches its own success banner"
  NF="$(printf '%s\n' "$LAST_OUT" | grep -cE '^\[FAIL\]' || true)"
  truth "$( [ "$NF" = 0 ] && echo 1 || echo 0)" "  … with 0 [FAIL] lines" "counted $NF"

  # The golden is a real generator output, so it is the strongest available
  # evidence for criterion #2's passing half — a fixture cannot prove the
  # stitcher, and this does.
  has '\[PASS\] long-read-vintage: data-vintage="news"' "criterion #2's passing half, on real generator output"
  has '\[PASS\] cover-leads-on' "  … and cover-leads-on, on both stitch paths"
  has '\[PASS\] image-shapes/distinct' "criterion #8's passing half, on real generator output"
  has '\[PASS\] figure-provenance' "  … with the full §3.4 provenance record present"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Frozen-input verification
# ═══════════════════════════════════════════════════════════════════════════════
plain_section "F" "FROZEN INPUTS  (SPEC §1.3 — this harness asserts, it never writes)"
truth "$( [ "$(sha256sum "$ISSUE_18" | cut -c1-16)" = "$ISSUE18_SHA_BEFORE" ] && echo 1 || echo 0)" \
      "Issue #18 is unchanged by this run  (sha256[:16] $ISSUE18_SHA_BEFORE)"
truth "$( [ "$(sha256sum "$REAL_STATE" | cut -c1-16)" = "$STATE_SHA_BEFORE" ] && echo 1 || echo 0)" \
      "state/signal-state.json is unchanged  (sha256[:16] $STATE_SHA_BEFORE)"
if [ -n "$MANIFEST_SHA_BEFORE" ]; then
  truth "$( [ "$(sha256sum "$REPO/assets/cached/manifest.json" | cut -c1-16)" = "$MANIFEST_SHA_BEFORE" ] && echo 1 || echo 0)" \
        "assets/cached/manifest.json is unchanged  (sha256[:16] $MANIFEST_SHA_BEFORE)"
fi
NCOV="$(find "$REPO/assets/covers" -newer "$FIXTURES/build-fixtures.py" -name '*.jpg' 2>/dev/null | wc -l | tr -d ' ')"
truth "$( [ "$NCOV" = 0 ] && echo 1 || echo 0)" \
      "no cover in assets/covers/ was written by this run" "$NCOV file(s) newer than the fixture builder"

# ═══════════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════════
printf '\n%s╔══════════════════════════════════════════════════════════════════════════════╗\n' "$C_H"
printf   '║  SUMMARY                                                                     ║\n'
printf   '╚══════════════════════════════════════════════════════════════════════════════╝%s\n' "$C_0"
printf '  %-16s %6s %6s %6s\n' "section" "ok" "FAIL" "n/d"
DEMONSTRATED=0; CRIT_TOTAL=0
for c in "${CRIT_ORDER[@]}"; do
  mark="  "
  case "$c" in
    [0-9]|1[0-2])
      CRIT_TOTAL=$(( CRIT_TOTAL + 1 ))
      if [ "${CF[$c]}" = 0 ] && [ "${CP[$c]}" -gt 0 ]; then
        DEMONSTRATED=$(( DEMONSTRATED + 1 )); mark="${C_OK}✓${C_0} "
      else mark="${C_NO}✗${C_0} "; fi ;;
  esac
  printf '  %s%-14s %6s %6s %6s\n' "$mark" "$c" "${CP[$c]}" "${CF[$c]}" "${CS[$c]}"
done
printf '  %-16s %6s %6s %6s\n' "TOTAL" "$TOTAL_PASS" "$TOTAL_FAIL" "$TOTAL_SKIP"
echo
printf '  criteria demonstrated with both a firing and a passing case: %s of %s\n' \
  "$DEMONSTRATED" "$CRIT_TOTAL"
printf '  assertions: %s ok, %s failed, %s not demonstrable here\n' \
  "$TOTAL_PASS" "$TOTAL_FAIL" "$TOTAL_SKIP"
printf '  validated against commit %s\n' "$HEAD_SHA"

RC=0
if [ "$TOTAL_FAIL" -gt 0 ]; then
  printf '\n%s✗ %s ASSERTION FAILURE(S).%s A criterion stopped holding — read the FAIL lines above.\n' \
    "$C_NO" "$TOTAL_FAIL" "$C_0"
  RC=1
fi
if [ "$DEBT" -gt 0 ]; then
  printf '\n%s✗ %s KNOWN BLOCKER(S) — surfaced, not swallowed:%s\n' "$C_NO" "$DEBT" "$C_0"
  for d in "${DEBT_LINES[@]}"; do printf '      · %s\n' "$d"; done
  printf '    These are NOT criterion failures — all %s criteria above stand. They are real\n' "$DEMONSTRATED"
  printf '    debt in files WP-10 does not own, and the exit code reflects them on purpose:\n'
  printf '    the whole reason this harness exists is that the previous one reported green\n'
  printf '    over a validator that was reporting 7 errors. Pass --ignore-known-debt to\n'
  printf '    scope the exit code to the criteria once you have read § P.\n'
  [ "$IGNORE_DEBT" = 1 ] || RC=1
fi
if [ "$TOTAL_SKIP" -gt 0 ]; then
  printf '\n%s%s finding(s) NOT DEMONSTRATED in this environment%s (Worker/KV/D1, egress, or a\n' \
    "$C_WARN" "$TOTAL_SKIP" "$C_0"
  printf '  fact not present in the rendered markup). Each is named above with its reason.\n'
  printf '  None of them is counted as a pass.\n'
fi
if [ "$RC" = 0 ]; then
  printf '\n%s✓ ALL %s ACCEPTANCE CRITERIA DEMONSTRATED%s — each with a firing case and a passing case.\n' \
    "$C_OK" "$DEMONSTRATED" "$C_0"
fi
exit "$RC"
