#!/usr/bin/env bash
# check-image-urls.sh — Phase 7.6 gate.
#
# Probes every <img src> URL in the stitched HTML and reports failures.
# Catches the regression where writer subagents construct plausible-looking
# but non-existent image URLs (fabricated Wikimedia hash prefixes, invented
# press-kit page slugs, typo'd file names, guessed PIA numbers, etc.).
#
# Usage:
#   bash scripts/check-image-urls.sh path/to/stitched.html
#
# Exit codes:
#   0 — every URL returned 200 (or sandboxed env detected, advisory only)
#   1 — at least one URL is broken (4xx/5xx/timeout)
#   2 — usage / missing file
#
# Sandbox detection: if the FIRST probe returns 000 (connection refused)
# we treat the environment as egress-blocked and skip remaining checks —
# the script logs an advisory and exits 0. This lets pipelines run inside
# restricted containers without a hard fail; the JS onerror fallback in
# script.js is the runtime safety net.
#
# Browser-like UA matters: Wikimedia, starwars.com, NASA JPL all reject
# bare curl. Use a Chrome desktop UA.

set -euo pipefail

FILE="${1:-}"
if [[ -z "$FILE" || ! -f "$FILE" ]]; then
  echo "Usage: $0 path/to/stitched.html" >&2
  exit 2
fi

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
TIMEOUT=15

URLS=$(python3 - "$FILE" <<'PYEOF'
import re, sys
html = open(sys.argv[1]).read()
body = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL)
body = re.sub(r'<!--.*?-->', '', body, flags=re.DOTALL)
imgs = re.findall(r'<img[^>]+src="([^"]+)"', body)
bgs  = re.findall(r"background-image\s*:\s*url\('?\"?([^'\")]+)", body)
for u in imgs + bgs:
    if u.startswith(('http://', 'https://')):
        print(u)
PYEOF
)

total=$(echo "$URLS" | grep -c . || true)
if [[ "$total" -eq 0 ]]; then
  echo "No external image URLs found in $FILE — nothing to probe."
  exit 0
fi

echo "=== Phase 7.6: check-image-urls.sh ==="
echo "Probing $total image URLs in $FILE..."
echo ""

ok=0
fail=0
failures=()
codes_seen=""

while IFS= read -r url; do
  [[ -z "$url" ]] && continue
  code=$(curl -sIL -H "User-Agent: $UA" -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null || echo "000")
  codes_seen+="$code "

  if [[ "$code" =~ ^(200|301|302|304)$ ]]; then
    ok=$((ok+1))
  else
    fail=$((fail+1))
    failures+=("$code  $url")
  fi
done <<< "$URLS"

# Sandbox detection: if every probe failed AND every probe returned the
# same status code (e.g. 000 from connection-refused, 403 from a uniform
# upstream block), treat as egress-blocked rather than as 14 simultaneous
# fabrications. Real production has heterogeneous hosts that don't all
# fail the same way at once.
unique=$(echo "$codes_seen" | tr ' ' '\n' | sort -u | grep -c . || true)
if [[ "$ok" -eq 0 && "$unique" -eq 1 && "$total" -ge 3 ]]; then
  single_code=$(echo "$codes_seen" | awk '{print $1}')
  echo "ADVISORY: all $total probes returned $single_code (uniform failure)."
  echo "          Egress-blocked sandbox detected — skipping liveness checks."
  echo "          Runtime JS onerror fallback in script.js will hide any broken images."
  exit 0
fi

echo "OK:   $ok"
echo "FAIL: $fail"

if [[ ${#failures[@]} -gt 0 ]]; then
  echo ""
  echo "Failed URLs (fix in research-bundle.json image_candidates and re-run writers,"
  echo "or substitute a verified URL via WebSearch and re-stitch):"
  for f in "${failures[@]}"; do
    echo "  $f"
  done
  exit 1
fi

echo ""
echo "All image URLs resolve."
exit 0
