#!/usr/bin/env bash
# post-publish.sh — Runs after the generation pipeline writes a new issue
# into /issues/. Two side effects:
#
#   1. Mirror every external image referenced by the new HTML into
#      /assets/cached/<hash>.<ext> and rewrite the HTML to reference the
#      local copies. Makes the issue offline-safe and permanent.
#
#   2. Generate a cover thumbnail at /assets/covers/<slug>.jpg so the
#      archive page renders the issue with a visible cover.
#
# The PWA snippet, reading-progress tracker, and standard chrome are all
# baked into template-parts/, so no injection step is needed here.
#
# Usage:
#   bash scripts/post-publish.sh issues/signal_weekly_2026-06-07.html
#
# Idempotent on all sides — re-running is safe.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <issue.html> [<issue.html> ...]" >&2
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "→ Mirroring external images..."
python3 scripts/mirror-images.py "$@"

echo
echo "→ Generating cover thumbnail(s)..."
python3 scripts/extract-covers.py "$@"

echo
echo "→ Done. Commit the rewritten HTML, any new files under /assets/cached/,"
echo "  and the cover under /assets/covers/."
