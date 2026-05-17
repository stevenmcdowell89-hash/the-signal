#!/usr/bin/env bash
# cost-summary.sh — summarise the cost log so we can see actual cost shape per issue.
#
# Reads the cost log (default /tmp/the-signal/state/cost-log.jsonl; override
# via SIGNAL_COST_LOG) and prints:
#   - Calls per issue, broken down by role and model
#   - Retry rate per role (validator failures, gate failures, escalations)
#   - Aggregate counts across all issues
#
# Usage:
#   bash scripts/cost-summary.sh                  # summarise everything
#   bash scripts/cost-summary.sh --issue weekly-2026-05-03    # one issue
#   bash scripts/cost-summary.sh --since 2026-05-01           # date floor
#
# Pure stdlib — uses python3 with json + collections only.

set -e

LOG_FILE="${SIGNAL_COST_LOG:-/tmp/the-signal/state/cost-log.jsonl}"

if [ ! -f "$LOG_FILE" ]; then
  echo "No cost log yet at $LOG_FILE."
  echo "It will appear after the first pipeline run logs a subagent call."
  exit 0
fi

FILTER_ISSUE=""
FILTER_SINCE=""

while [ $# -gt 0 ]; do
  case "$1" in
    --issue)  FILTER_ISSUE="$2"; shift 2 ;;
    --since)  FILTER_SINCE="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

python3 - "$LOG_FILE" "$FILTER_ISSUE" "$FILTER_SINCE" <<'PY'
import json, sys
from collections import defaultdict, Counter

log_file, filter_issue, filter_since = sys.argv[1], sys.argv[2], sys.argv[3]

rows = []
with open(log_file) as f:
    for line in f:
        line = line.strip()
        if not line: continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if filter_issue and r.get("issue_id") != filter_issue:
            continue
        if filter_since and r.get("ts", "")[:10] < filter_since:
            continue
        rows.append(r)

if not rows:
    print("No matching rows in cost log.")
    sys.exit(0)

# Per-issue breakdown
by_issue = defaultdict(list)
for r in rows:
    by_issue[r["issue_id"]].append(r)

print("=" * 68)
print(f"Signal cost log summary — {len(rows)} calls across {len(by_issue)} issues")
print("=" * 68)

for issue_id in sorted(by_issue.keys()):
    issue_rows = by_issue[issue_id]
    print()
    print(f"📰 {issue_id}  ({len(issue_rows)} calls)")
    print("-" * 68)

    by_role = defaultdict(list)
    for r in issue_rows:
        by_role[r["role"]].append(r)

    for role in ["researcher", "planner", "writer", "repair"]:
        if role not in by_role: continue
        role_rows = by_role[role]
        models = Counter(r["model"] for r in role_rows)
        retries = sum(1 for r in role_rows if r.get("retry", 0) > 0)
        bad_outcomes = Counter(r["outcome"] for r in role_rows if r["outcome"] != "ok")

        model_str = ", ".join(f"{m}×{n}" for m, n in models.most_common())
        line = f"  {role:11s} {len(role_rows):2d} calls  ({model_str})"
        if retries:
            line += f"  retries: {retries}"
        if bad_outcomes:
            line += f"  outcomes: {dict(bad_outcomes)}"
        print(line)

# Aggregate across all issues
print()
print("=" * 68)
print("Aggregate across all issues")
print("=" * 68)
agg_role_model = Counter((r["role"], r["model"]) for r in rows)
for (role, model), n in sorted(agg_role_model.items(), key=lambda x: (-x[1], x[0])):
    print(f"  {role:11s} {model:24s} {n:4d} calls")

print()
escalations = [r for r in rows if r["outcome"] == "escalated"]
gate_fails  = [r for r in rows if r["outcome"] == "gate_fail"]
val_fails   = [r for r in rows if r["outcome"] == "validator_fail"]
print(f"  validator failures: {len(val_fails)}")
print(f"  gate failures:      {len(gate_fails)}")
print(f"  escalations:        {len(escalations)}")
PY
