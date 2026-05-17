#!/usr/bin/env bash
# check-release-dates.sh
# Pre-publish release-date sanity check for The Signal issues.
# Extracts every claim of a date adjacent to a media name (TV / film / game / book / album)
# and prints them for the agent to verify against the locked-date register and web search.
#
# Usage: bash scripts/check-release-dates.sh <html-file>
#
# Output is written to /tmp/signal-date-claims.txt — a list of "claim contexts" the agent
# should walk through and search-verify before publishing. The script does NOT make verdicts;
# it surfaces the claims so the agent can do the checking.

set -euo pipefail

if [[ $# -lt 1 || ! -f "$1" ]]; then
  echo "usage: $0 <html-file>" >&2
  exit 2
fi

FILE="$1"
OUT="/tmp/signal-date-claims.txt"

{
  echo "=== Release-date claim extraction ==="
  echo "File: $FILE"
  echo "Generated: $(date -Iseconds)"
  echo ""
  echo "Walk each line below. For each:"
  echo "  1. Identify the media name (TV / film / game / book / album)"
  echo "  2. Check it against the locked-date register in references/compliance-checklist.md (1B)"
  echo "  3. If not in the register and dated, search-verify (e.g. 'X release date')"
  echo "  4. If the date is wrong or the item already aired, fix or cut before publishing"
  echo ""
  echo "--- Locked tripwire entries (auto-flag if matched) ---"
  grep -niE "andor|tales of the (jedi|empire|underworld)|skeleton crew|the acolyte|maul: shadow lord|mandalorian and grogu" "$FILE" | head -40 || echo "(none found)"
  echo ""
  echo "--- Lines with absolute dates (DD Month YYYY / Month DD YYYY) near media context ---"
  grep -niE "(19|20)[0-9]{2}.*(season|series|episode|finale|premiere|drops|releases|launches|hits|cinemas|disney\\+|netflix|apple tv|hbo|paramount|prime video)" "$FILE" | head -60 || echo "(none found)"
  echo ""
  echo "--- Lines with relative time + media context (HIGH RISK) ---"
  grep -niE "(last (week|month|year|spring|summer|autumn|winter|january|february|march|april|may|june|july|august|september|october|november|december))|(this (week|month|year|spring|summer|autumn|winter|january|february|march|april|may|june|july|august|september|october|november|december))|(next (week|month|year|spring|summer|autumn|winter|january|february|march|april|may|june|july|august|september|october|november|december))|(coming (soon|next|this))" "$FILE" | grep -iE "season|series|episode|finale|premiere|drops|releases|launches|hits|cinemas|disney\\+|netflix|apple tv|hbo|paramount|prime video|switch|playstation|xbox|steam" | head -40 || echo "(none found)"
  echo ""
  echo "--- Lines mentioning specific upcoming-feeling phrases ---"
  grep -niE "is (coming|due|set to (drop|release|launch|premiere|land|hit))|will (drop|release|launch|premiere|land|hit)|(arrives|drops|premieres|releases|launches) (on|in|this)" "$FILE" | head -40 || echo "(none found)"
  echo ""
  echo "=== End ==="
  echo ""
  echo "Verification protocol (mandatory before publish):"
  echo "  - Every line above must either: (a) match a locked-register entry with the right date, or"
  echo "    (b) have been web-search-verified for the current year, or (c) be cut from the issue."
  echo "  - 'Coming next month' without a year is automatically suspect — the agent has fabricated"
  echo "    upcoming Star Wars releases three times in past issues. Default to skepticism."
} > "$OUT"

# Echo summary to stderr / stdout for the agent
HIT_COUNT=$(grep -cE "^[0-9]+:" "$OUT" || true)
echo "Release-date claims surfaced for review: ~$HIT_COUNT lines"
echo "Full report: $OUT"
echo ""
echo "Next step: read $OUT, walk each claim, verify against locked register or web search, fix or cut failures."
