#!/bin/bash
# SessionStart hook — Claude Code on the Web only.
#
# Installs the Python packages the publish pipeline needs:
#   - Pillow   → scripts/extract-covers.py, scripts/build-icons.py
#   - requests → scripts/mirror-images.py
#
# Skill scripts (validate-issue.py, etc.) use only Python stdlib, so they
# need no extra packages.
#
# Runs synchronously so dependencies are guaranteed in place before the
# pipeline starts. ~10–20s on first run; faster on warm container reuse.
set -euo pipefail

# Skip on local machines — the user already has these installed there.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

python3 -m pip install \
  --quiet \
  --disable-pip-version-check \
  --no-input \
  Pillow requests
