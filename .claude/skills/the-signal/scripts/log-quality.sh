#!/usr/bin/env bash
# log-quality.sh — append one editorial-quality score to the quality log.
#
# Scored at Phase 8.5 by a dedicated scorer agent (NOT the orchestrator,
# NOT the writer) against references/quality-rubric.md. This is the
# pipeline's only QUALITY signal — every other gate measures compliance.
#
# Usage:
#   bash scripts/log-quality.sh '<scorer-json>'      # JSON as $1
#   echo '<scorer-json>' | bash scripts/log-quality.sh   # JSON on stdin
#
# The scorer emits a JSON object with: issue_id, issue_file, title, format,
# date, writer_model, scorer_model, scores{voice,density,length,structure,
# opening,throughline,novelty,visual}, weakest, note. (throughline is null for
# parallel formats; novelty added v8.27; length + visual added v8.43 —
# `overall` is the mean of all numeric scores, so new dimensions are averaged
# in automatically and old rows without them stay valid.)
#
# This script injects `ts`, computes `overall` (mean of non-null scores,
# 1 dp), appends one line to the quality log, and regenerates quality.html.
#
# Default log path: /tmp/the-signal/state/quality-log.jsonl (committed to
# the repo alongside cost-log.jsonl). Override via SIGNAL_QUALITY_LOG.
#
# Never blocks the pipeline — logging failures are non-fatal.
#
# Read with: bash scripts/quality-summary.sh

set +e  # never block the pipeline on logging errors

LOG_FILE="${SIGNAL_QUALITY_LOG:-/tmp/the-signal/state/quality-log.jsonl}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Read the scorer JSON from $1 or stdin.
if [ "$#" -ge 1 ] && [ -n "$1" ]; then
  PAYLOAD="$1"
else
  PAYLOAD="$(cat)"
fi

mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null

python3 - "$LOG_FILE" "$PAYLOAD" <<'PY'
import sys, json, datetime

log_file, payload = sys.argv[1], sys.argv[2]
try:
    obj = json.loads(payload)
except Exception as e:
    sys.stderr.write(f"log-quality: payload is not valid JSON ({e}); not logging.\n")
    sys.exit(0)  # non-fatal

scores = obj.get("scores", {})
vals = [v for v in scores.values() if isinstance(v, (int, float))]
obj["overall"] = round(sum(vals) / len(vals), 1) if vals else None
obj.setdefault("ts", datetime.datetime.now(datetime.timezone.utc)
               .strftime("%Y-%m-%dT%H:%M:%SZ"))

# Stable key order for readability.
order = ["ts", "issue_id", "issue_file", "title", "format", "date",
         "writer_model", "scorer_model", "scores", "overall",
         "weakest", "note", "backfill"]
row = {k: obj[k] for k in order if k in obj}
for k, v in obj.items():  # keep any extra keys
    row.setdefault(k, v)

try:
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
except Exception as e:
    sys.stderr.write(f"log-quality: could not write log ({e}).\n")
    sys.exit(0)

print(f"✓ logged quality score for {row.get('issue_id','?')}: "
      f"overall {row.get('overall','?')} (weakest: {row.get('weakest','?')})")
PY

# Regenerate the public page from the full log (best-effort).
if [ -f "$SCRIPT_DIR/render-quality-page.py" ]; then
  python3 "$SCRIPT_DIR/render-quality-page.py" 2>/dev/null \
    && echo "✓ regenerated quality.html"
fi

exit 0
