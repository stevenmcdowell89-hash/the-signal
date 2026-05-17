#!/usr/bin/env bash
# log-call.sh — append one line per subagent call to the cost log.
#
# Usage:
#   bash scripts/log-call.sh <role> <model> <issue_id> [chapter_id] [retry_count] [outcome]
#
# Args:
#   role          researcher | planner | writer | repair
#   model         the model identifier actually used (e.g. sonnet, opus, haiku)
#   issue_id      slug for the issue (e.g. weekly-2026-05-03 or countdown-efteling)
#   chapter_id    optional — chapter slug for writer/repair calls; "-" otherwise
#   retry_count   optional integer — 0 for first call, 1+ for retries; defaults 0
#   outcome       optional — "ok" | "validator_fail" | "gate_fail" | "escalated"; defaults "ok"
#
# Output: one JSON line appended to the cost log with timestamp. Default path
# is /tmp/the-signal/state/cost-log.jsonl (committed to the repo alongside
# signal-state.json so usage history survives session reclaim). Override the
# path via the SIGNAL_COST_LOG environment variable.
#
# Never errors out — failures are silent so the pipeline isn't blocked by logging.
#
# Read with: bash scripts/cost-summary.sh [--since YYYY-MM-DD]

set +e  # never block the pipeline on logging errors

LOG_FILE="${SIGNAL_COST_LOG:-/tmp/the-signal/state/cost-log.jsonl}"
mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null

ROLE="${1:-unknown}"
MODEL="${2:-unknown}"
ISSUE_ID="${3:-unknown}"
CHAPTER_ID="${4:--}"
RETRY="${5:-0}"
OUTCOME="${6:-ok}"

TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# JSON-escape any user-supplied strings (basic — replace " and \)
esc() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }

cat >> "$LOG_FILE" <<JSON
{"ts":"$(esc "$TS")","role":"$(esc "$ROLE")","model":"$(esc "$MODEL")","issue_id":"$(esc "$ISSUE_ID")","chapter_id":"$(esc "$CHAPTER_ID")","retry":$RETRY,"outcome":"$(esc "$OUTCOME")"}
JSON

exit 0
