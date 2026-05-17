#!/usr/bin/env bash
# check-image-diversity.sh — Phase 7.7 downstream gate.
#
# After Phase 7.6 (URL liveness) confirms every <img src> resolves, this gate
# enforces source-type diversity across the stitched issue:
#
#   - No single domain >50% of images       (RT-5 hard fail)
#   - Wikimedia ≤30% AND ≤4 entries          (the lower of the two wins)
#   - At least 3 distinct source types       (from the 5-type menu in
#                                             references/spec/global.md
#                                             image-integrity)
#
# Reads the lookup at references/image-source-types.json to classify domains.
# Unknown domains count toward the domain ratio but not toward source-type
# diversity — they trigger an advisory, not a hard fail.
#
# Catches the edge case where the research bundle passes Phase 3b but
# writers omit some images (changing the final ratio) or where a new domain
# slips in via writer prose (not in the bundle).
#
# Usage:
#   bash scripts/check-image-diversity.sh path/to/stitched.html
#
# Exit codes:
#   0 — PASS
#   1 — FAIL
#   2 — usage / missing file

set -euo pipefail

FILE="${1:-}"
if [[ -z "$FILE" || ! -f "$FILE" ]]; then
  echo "Usage: $0 path/to/stitched.html" >&2
  exit 2
fi

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOOKUP="${SKILL_DIR}/references/image-source-types.json"
if [[ ! -f "$LOOKUP" ]]; then
  echo "ERROR: lookup table not found at $LOOKUP" >&2
  exit 2
fi

python3 - "$FILE" "$LOOKUP" <<'PYEOF'
import json
import re
import sys
from collections import Counter
from urllib.parse import urlparse

html_path, lookup_path = sys.argv[1], sys.argv[2]
html = open(html_path).read()
body = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL)
body = re.sub(r'<!--.*?-->', '', body, flags=re.DOTALL)
imgs = re.findall(r'<img[^>]+src="([^"]+)"', body)
bgs  = re.findall(r"background-image\s*:\s*url\('?\"?([^'\")]+)", body)
urls = [u for u in (imgs + bgs) if u.startswith(("http://", "https://"))]

if not urls:
    print("No external image URLs found — skipping diversity check.")
    sys.exit(0)

lookup = json.loads(open(lookup_path).read())
thresholds = lookup["thresholds"]
domain_map = lookup["domains"]

# Classify
def classify(url):
    netloc = urlparse(url).netloc.lower()
    if netloc in domain_map:
        return netloc, domain_map[netloc]
    stripped = netloc.removeprefix("www.")
    if stripped in domain_map:
        return netloc, domain_map[stripped]
    if netloc in lookup.get("ambiguous_domains", {}):
        return netloc, "ambiguous"
    return netloc, "unknown"

records = [classify(u) for u in urls]
total = len(records)
domains = Counter(d for d, _ in records)
types_full = Counter(t for _, t in records)
types_counted = Counter(t for _, t in records if t not in ("unknown", "ambiguous"))

# Apply rules
failures = []
warnings = []

# Rule 1: single-domain cap
for d, n in domains.most_common():
    pct = 100 * n / total
    if pct > thresholds["single_domain_max_pct"]:
        failures.append(
            f"RT-5 hard fail: {d} = {n}/{total} ({pct:.1f}%) > "
            f"{thresholds['single_domain_max_pct']}% cap."
        )

# Rule 2: Wikimedia cap
wm = sum(n for d, n in domains.items() if domain_map.get(d) == "wikimedia")
wm_pct = 100 * wm / total if total else 0
if wm > thresholds["wikimedia_max_count"]:
    failures.append(
        f"Wikimedia entries: {wm} > {thresholds['wikimedia_max_count']} cap. "
        "Wikimedia is a supplement — see image-integrity § Researcher contract."
    )
if wm_pct > thresholds["wikimedia_max_pct"]:
    failures.append(
        f"Wikimedia ratio: {wm}/{total} = {wm_pct:.1f}% > "
        f"{thresholds['wikimedia_max_pct']}% cap."
    )

# Rule 3: min source-type diversity
if len(types_counted) < thresholds["min_distinct_source_types"]:
    failures.append(
        f"Source-type diversity: {len(types_counted)} types ({sorted(types_counted)}) "
        f"< minimum of {thresholds['min_distinct_source_types']}. "
        f"Menu: {sorted(lookup['types'].keys())}."
    )

# Unknown / ambiguous → warning, not fail
if "unknown" in types_full:
    unknown_domains = sorted({d for d, t in records if t == "unknown"})
    warnings.append(
        f"unknown domain(s) seen: {unknown_domains}. "
        "Add to references/image-source-types.json if recurring."
    )
if "ambiguous" in types_full:
    amb_domains = sorted({d for d, t in records if t == "ambiguous"})
    warnings.append(
        f"ambiguous domain(s) seen: {amb_domains}. "
        "Stitched HTML cannot carry the source_type annotation that resolves these — "
        "next time, set source_type explicitly in research-bundle image_candidates."
    )

# Report
print("=== Phase 7.7: check-image-diversity.sh ===")
print(f"Total images: {total}")
print(f"Distinct domains: {len(domains)}")
print()
print("By domain:")
for d, n in domains.most_common():
    t = domain_map.get(d, "(unknown)")
    print(f"  {n:2}/{total}  ({100*n/total:4.1f}%)  {d:45}  → {t}")
print()
print(f"By source type: {dict(types_full)}")
print()

if warnings:
    print("Warnings:")
    for w in warnings:
        print(f"  {w}")
    print()

if failures:
    print("FAIL — rule violations:")
    for f in failures:
        print(f"  {f}")
    print()
    print("Remediation:")
    print("  • For RT-5 / Wikimedia caps: swap entries to under-represented source types.")
    print("    See references/spec/global.md image-integrity for the 5-type menu.")
    print("  • For source-type diversity: extend research to additional source types.")
    print("    Researcher should re-run with the failure report as input.")
    sys.exit(1)

print("PASS — image source diversity within thresholds.")
sys.exit(0)
PYEOF
