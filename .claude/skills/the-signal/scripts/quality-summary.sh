#!/usr/bin/env bash
# quality-summary.sh — terminal view of the editorial-quality log.
#
# Mirror of cost-summary.sh, pointed at the quality signal instead of cost.
# Prints overall trend, the average-by-writer-model comparison (the headline
# question this whole system exists to answer), and weakest-dimension
# frequency so you can see where the *spec* — not the model — should change.
#
# Usage:
#   bash scripts/quality-summary.sh [--since YYYY-MM-DD]
#
# Log path: SIGNAL_QUALITY_LOG, else state/quality-log.jsonl at the repo root.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
LOG_FILE="${SIGNAL_QUALITY_LOG:-$REPO_ROOT/state/quality-log.jsonl}"

SINCE=""
if [ "${1:-}" = "--since" ] && [ -n "${2:-}" ]; then SINCE="$2"; fi

python3 - "$LOG_FILE" "$SINCE" <<'PY'
import sys, json, statistics
from collections import defaultdict, Counter

log_file, since = sys.argv[1], sys.argv[2]
rows = []
try:
    with open(log_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if since and (r.get("date") or "") < since:
                continue
            rows.append(r)
except FileNotFoundError:
    print(f"No quality log at {log_file} yet.")
    sys.exit(0)

if not rows:
    print("No quality scores logged yet.")
    sys.exit(0)

# Full dimension list (v8.43). Older rows lack the newer keys (novelty v8.27,
# length/visual v8.43); the per-dimension loop below skips missing keys, so
# old and new rows coexist — n varies per dimension.
DIMS = ["voice", "density", "length", "structure", "opening", "throughline",
        "novelty", "visual"]
overalls = [r["overall"] for r in rows if isinstance(r.get("overall"), (int, float))]

print(f"\nThe Signal — editorial quality  ({len(rows)} issue(s)"
      + (f", since {since}" if since else "") + ")")
print("=" * 64)
if overalls:
    print(f"  Average overall : {statistics.mean(overalls):.2f}"
          f"   (min {min(overalls):g}, max {max(overalls):g})")

print("\n  Average overall by writer model:")
by_writer = defaultdict(list)
for r in rows:
    o = r.get("overall")
    if isinstance(o, (int, float)):
        by_writer[r.get("writer_model", "?")].append(o)
for m, v in sorted(by_writer.items()):
    print(f"    {m:<10} {statistics.mean(v):.2f}  (n={len(v)})")
if len(by_writer) < 2:
    print("    (only one writer model so far — the comparison goes live once"
          "\n     issues written by a second model are scored)")

print("\n  Average by dimension:")
for d in DIMS:
    vals = [r["scores"][d] for r in rows
            if isinstance(r.get("scores", {}).get(d), (int, float))]
    if vals:
        print(f"    {d:<12} {statistics.mean(vals):.2f}  (n={len(vals)})")

print("\n  Weakest dimension frequency:")
for k, n in Counter(r.get("weakest") for r in rows if r.get("weakest")).most_common():
    print(f"    {k:<12} ×{n}")

bf = sum(1 for r in rows if r.get("backfill"))
if bf:
    print(f"\n  ({bf} of {len(rows)} are backfilled / self-scored — indicative only.)")
print()
PY
