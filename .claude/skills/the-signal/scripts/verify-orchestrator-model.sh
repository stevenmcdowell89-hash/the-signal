#!/bin/bash
# verify-orchestrator-model.sh — Phase 0 hard-gate
#
# Called by the orchestrator as its FIRST tool call when a Signal pipeline
# run starts. Exits non-zero (and prints to stderr) if the orchestrator's
# model is below the Opus 4.7 1M-context FLOOR, blocking the pipeline
# before any real work happens. A newer Opus 1M (4.8+) passes — the gate
# stops a downgrade, it does not forbid an upgrade.
#
# Why this exists: the 24 May 2026 Sunday run was scheduled with the
# routine's model preference set to Opus 4.7 1M, but the Claude Code on
# the Web harness selected Opus 4.6 anyway. The 4.6 context window
# overflowed during Phase 5 writer fan-out (16 writers × ~3-5 min each
# of accumulated context), compaction fired mid-pipeline, live state
# was lost, the issue shipped with multiple defects.
#
# Usage:
#   bash scripts/verify-orchestrator-model.sh "<model-id-from-system-prompt>"
#
# The orchestrator reads its exact model identifier from its own system
# prompt under "Environment" → "The exact model ID is …" and passes it
# verbatim as the single argument.
#
# Exit codes:
#   0  — model is allowed
#   1  — model is not allowed; abort the pipeline

set -euo pipefail

# Allowlist, not a single pin. The gate is a FLOOR — it exists to stop a
# *downgrade* (e.g. the harness silently falling back to Opus 4.6 or a
# Sonnet tier), not to forbid a stronger model. When Anthropic ships a
# newer Opus 1M, append its identifier here — never remove the floor.
ALLOWED=(
  "claude-opus-4-7[1m]"
  "claude-opus-4-8[1m]"
)
ALLOWED_DISPLAY="Opus 4.7 1M or newer (one of: ${ALLOWED[*]})"

if [ "$#" -ne 1 ]; then
  echo "verify-orchestrator-model.sh: usage: $0 <model-id>" >&2
  echo "  The orchestrator must pass its exact model identifier from its" >&2
  echo "  system prompt (Environment → 'The exact model ID is …')." >&2
  exit 1
fi

OBSERVED="$1"

# Trim quotes / whitespace defensively
OBSERVED="${OBSERVED#\"}"
OBSERVED="${OBSERVED%\"}"
OBSERVED="${OBSERVED#\'}"
OBSERVED="${OBSERVED%\'}"
OBSERVED="$(echo "$OBSERVED" | xargs)"

for m in "${ALLOWED[@]}"; do
  if [ "$OBSERVED" = "$m" ]; then
    echo "✓ Orchestrator model verified: $OBSERVED"
    exit 0
  fi
done

cat >&2 <<EOF

═══════════════════════════════════════════════════════════════════════
ORCHESTRATOR MODEL CHECK FAILED — PIPELINE ABORTING
═══════════════════════════════════════════════════════════════════════

The Signal pipeline requires the orchestrator to run at or above the
Opus 4.7 1M-context floor. Accepted identifiers:

    $ALLOWED_DISPLAY

The orchestrator reported:

    $OBSERVED

This is the May 24 2026 failure mode. Lower-tier models cannot reliably
hold full pipeline state through the 16-chapter Phase 5 writer fan-out;
context compaction mid-run will corrupt live state and the issue will
ship with structural defects.

The Claude Code routine that triggered this run was almost certainly
configured for Opus 4.7 1M — the harness ignored the preference. This
is a harness-layer issue, not something this repo can fix from inside.

Action: do not retry from here. Re-trigger the routine from Claude Code
on the Web (or its CLI equivalent). If the harness keeps falling back
to a lower-tier model, the model-pref is not being honoured and the
routine config needs investigation.

═══════════════════════════════════════════════════════════════════════
EOF

exit 1
