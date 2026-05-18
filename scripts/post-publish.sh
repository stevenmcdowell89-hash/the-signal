#!/usr/bin/env bash
# post-publish.sh — Run after generating a new issue to mirror its external
# images into /assets/cached/ and rewrite the HTML to reference the local
# copies. Makes the issue offline-safe under the service worker, and
# permanent against upstream link rot.
#
# The PWA snippet itself (manifest link, theme-color, sw registration) is
# baked into template-parts/00-head-open.html, so newly-generated issues
# already have it — no injection step needed here.
#
# Usage:
#   bash scripts/post-publish.sh issues/signal_weekly_2026-06-07.html
#
# Idempotent: safe to re-run on the same file.

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
echo "→ Done. New issue is offline-ready under the service worker."
echo "  Commit the rewritten HTML and any new files under /assets/cached/."
