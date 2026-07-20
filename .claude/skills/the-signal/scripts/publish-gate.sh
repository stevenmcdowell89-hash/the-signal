#!/usr/bin/env bash
# publish-gate.sh — the MECHANICAL publish receipt (reliability design, Pillar F).
#
# Publish is earned, not assumed. This runs the ship-quality gates on the FINAL
# stitched issue, writes a machine-readable build-receipt.json, and exits 0 ONLY
# if every hard gate is green. The publish step (post-publish / CI) must run this
# and honour its exit code — so a broken issue cannot ship even if the
# orchestrator's prompt-honour is bypassed (the failure that shipped the Rewind
# despite a failing image gate — handoff §8c).
#
# Usage:
#   bash scripts/publish-gate.sh <stitched-html> --format <fmt> [--issue-id ID]
#         [--skip-image-urls] [--receipt PATH]
#
# Exit 0 = all hard gates green → safe to publish. Non-zero = DO NOT PUBLISH.

set -uo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
HTML=""
FMT=""
ISSUE_ID=""
SKIP_IMG=""
RECEIPT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --format)         FMT="$2"; shift 2 ;;
    --issue-id)       ISSUE_ID="$2"; shift 2 ;;
    --skip-image-urls) SKIP_IMG="--skip-image-urls"; shift ;;
    --receipt)        RECEIPT="$2"; shift 2 ;;
    -*)               echo "Unknown arg: $1"; exit 2 ;;
    *)                HTML="$1"; shift ;;
  esac
done

if [[ -z "$HTML" || -z "$FMT" ]]; then
  echo "Usage: publish-gate.sh <stitched-html> --format <fmt> [--issue-id ID] [--skip-image-urls] [--receipt PATH]"
  exit 2
fi
if [[ ! -f "$HTML" ]]; then
  echo "ERROR: issue file not found: $HTML"
  exit 2
fi
[[ -z "$RECEIPT" ]] && RECEIPT="$(dirname "$HTML")/build-receipt.json"
[[ -z "$ISSUE_ID" ]] && ISSUE_ID="$(basename "$HTML" .html)"

echo "=== publish-gate: $ISSUE_ID ($FMT) ==="

# --- run the gates, capturing each exit code ---
declare -a NAMES EXITS

run_gate() {          # name  command...
  local name="$1"; shift
  echo "--- gate: $name ---"
  if "$@"; then local rc=0; else local rc=$?; fi
  NAMES+=("$name"); EXITS+=("$rc")
  echo "    → exit $rc"
}

# Gate: structural + markup + visual-consistency + images (validate-issue.py)
# Runs non-strict deliberately: strictness is no longer load-bearing for
# imagelessness — the word floor (length-floor) and image-presence floor
# (image-floor) are hard FAILs that fire regardless of --strict or
# --skip-image-urls, so a thin/imageless issue goes red on its own.
run_gate "validate-issue" python3 "$SKILL_DIR/scripts/validate-issue.py" "$HTML" --format "$FMT" $SKIP_IMG

# Gate: image-source diversity (only meaningful when the issue carries <img>)
if grep -q '<img ' "$HTML"; then
  run_gate "image-diversity" bash "$SKILL_DIR/scripts/check-image-diversity.sh" "$HTML"
else
  echo "--- gate: image-diversity — no <img> in issue (CSS-placeholder plates), skipped ---"
fi

# ── WP-6: rendered gates for NEW-SYSTEM (data-mx) issues ──────────────────────
# A data-mx issue additionally runs the WP-0 measurement harness
# (tools/measure-issue.mjs: one run, both viewports + reduced-motion passes)
# and hard-fails on Law-2 floors/distribution, words-per-screen caps, Law-3
# measured body copy, Law-10 craft flags (chrome overlap / h-scroll / table
# truncation) and the Law-5 motion census per tier incl. reduced-motion==0.
# Detection keys off the REAL <body> tag (after </head>), same as
# validate-issue.py's is_new_system. Legacy issues never enter this block.
IS_MX=$(python3 - "$HTML" <<'PY'
import re, sys
html = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
he = re.search(r"</head\s*>", html, re.I)
tail = html[he.end():] if he else html
m = re.search(r"<body\b[^>]*>", tail, re.I)
print("yes" if (m and re.search(r"\bdata-mx\b", m.group(0))) else "no")
PY
)
if [[ "$IS_MX" == "yes" ]]; then
  REPO_ROOT="$(cd "$SKILL_DIR/../../.." && pwd)"
  METRICS_DIR="${MX_METRICS_DIR:-$(dirname "$HTML")/$(basename "$HTML" .html)-metrics}"
  mkdir -p "$METRICS_DIR"
  echo "--- data-mx issue: running WP-0 rendered gates (measure-issue.mjs → $METRICS_DIR) ---"
  run_gate "rendered-measure" node "$REPO_ROOT/tools/measure-issue.mjs" "$HTML" --out "$METRICS_DIR"
  if [[ -f "$METRICS_DIR/metrics.json" ]]; then
    run_gate "rendered-metrics" python3 "$SKILL_DIR/scripts/check-rendered-metrics.py" \
      "$METRICS_DIR/metrics.json" --format "$FMT" --html "$HTML"
  else
    echo "--- gate: rendered-metrics — metrics.json missing (measure failed) ---"
    NAMES+=("rendered-metrics"); EXITS+=(1)
  fi
else
  echo "--- rendered gates: legacy (non-mx) issue — skipped, pipeline unchanged ---"
fi

# --- compute verdict + write receipt ---
VERDICT="green"
for rc in "${EXITS[@]}"; do [[ "$rc" -ne 0 ]] && VERDICT="red"; done

python3 - "$RECEIPT" "$ISSUE_ID" "$FMT" "$HTML" "$VERDICT" "${NAMES[*]}" "${EXITS[*]}" <<'PY'
import json, sys
receipt, issue_id, fmt, html, verdict, names, exits = sys.argv[1:8]
names = names.split() if names else []
exits = [int(x) for x in exits.split()] if exits else []
gates = [{"name": n, "exit": e, "status": "pass" if e == 0 else "FAIL"}
         for n, e in zip(names, exits)]
data = {
    "issue_id": issue_id, "format": fmt, "issue_file": html,
    "verdict": verdict, "gates": gates,
    "publishable": verdict == "green",
    "note": "Machine-checkable ship receipt. The publish step must refuse to "
            "publish unless verdict=='green'. Reliability design Pillar F.",
}
with open(receipt, "w") as f:
    json.dump(data, f, indent=2)
print(f"receipt → {receipt}: verdict={verdict}")
PY

echo ""
if [[ "$VERDICT" == "green" ]]; then
  echo "=== PUBLISH-GATE GREEN — safe to publish $ISSUE_ID ==="
  exit 0
else
  echo "=== PUBLISH-GATE RED — DO NOT PUBLISH $ISSUE_ID (see receipt: $RECEIPT) ==="
  exit 1
fi
