#!/usr/bin/env bash
# check-image-diversity.sh — Phase 7.7 downstream gate.
#
# After Phase 7.6 (URL liveness) confirms every <img src> resolves, this gate
# enforces diversity across the stitched issue on BOTH axes:
#
#   WHERE the image came from (provenance)
#   - No single domain >50% of images       (RT-5 hard fail)
#   - At least 3 distinct source types      (the `types` menu in
#                                            references/image-source-types.json)
#
#   WHAT the image SHOWS (specificity)
#   - At least `min_distinct_shapes` distinct data-shows values across the issue
#   - Every data-shows value is a member of the canonical `shows` enum
#
# WHY THE SECOND AXIS EXISTS (SPEC 2026-07-26 §3.8/§3.14, defect E). Until
# 2026-07 this script measured provenance only. Issue #18 passed
# min_distinct_source_types: 3 comfortably while its Halo lead was key art with
# the logo composited in, and its Long Read was three Wikimedia images including
# a 2007 hobbyist model standing in for a 2021 result. A press kit is good
# provenance, so the safest, most-available press-kit asset — key art — scored
# full marks. The domain never tells you WHAT the picture shows.
#
# RETIRED HERE, 2026-07-26 (SPEC §3.14): the `wikimedia_max_pct` (30) and
# `wikimedia_max_count` (4) rules. A ceiling with no matching floor reads as a
# target — Commons became the thing to fill up to. They are replaced by
# `min_distinct_shapes`, a floor on the interesting shapes. Do not reinstate
# them; see `retired_thresholds` in the lookup for the history.
#
# Reads the lookup at references/image-source-types.json for the domain map,
# the `shows` enum and the thresholds. Unknown domains count toward the domain
# ratio but not toward source-type diversity — they trigger an advisory, not a
# hard fail. An unknown *shape* IS a hard fail: a typo'd data-shows value is
# invisible to every downstream budget in validate-issue.py.
#
# Catches the edge case where the research bundle passes Phase 3b but writers
# omit some images (changing the final ratio), where a new domain slips in via
# writer prose (not in the bundle), or where every plate in the issue ends up
# being the same safe shape.
#
# DIVISION OF LABOUR — read this before adding a rule here. This script is the
# ISSUE-WIDE half: distinct-shape count and enum validity. The PER-BAND shape
# budgets (at most one key_art in Pixel & Byte and never as its lead; the Long
# Read's ≥1 diagram/map/chart/artefact; the Touchline's concluded-result rule;
# the cross-issue no-repeat-lead rule) belong to validate-issue.py (SPEC §3.8),
# which owns the band structure. Editorial judgement — "is THIS the most
# specific available image of THIS thing" — stays with the human/reader pass;
# see references/compliance-checklist.md § Image specificity check.
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

lookup = json.loads(open(lookup_path).read())
thresholds = lookup["thresholds"]
domain_map = lookup["domains"]
# The `shows` enum is canonicalised in this file (SPEC §3.3). Read it; never
# hardcode the value list here, or the two drift.
shows_enum = list(lookup["shows"]["values"].keys())
info_shapes = lookup["shows"].get("information_figure_shapes", [])
last_resort = lookup["shows"].get("last_resort_shapes", [])
never_lead = lookup["shows"].get("never_lead_shapes", [])

failures = []
warnings = []

# ---------------------------------------------------------------- shape axis
# data-shows is emitted on every .plate-img by stitch_weekly.py (SPEC §3.4).
# Matched on the attribute rather than the element so a plate variant or a
# non-plate figure carrying the machine record still counts.
shapes_raw = re.findall(r'data-shows="([^"]*)"', body)
shapes = Counter(s.strip() for s in shapes_raw if s.strip())
unknown_shapes = sorted({s for s in shapes if s not in shows_enum})
valid_shapes = Counter({s: n for s, n in shapes.items() if s in shows_enum})
min_shapes = thresholds["min_distinct_shapes"]

if not shapes_raw:
    failures.append(
        "No data-shows attributes found — this issue is UNLABELLED, so its image "
        f"shapes cannot be counted and min_distinct_shapes ({min_shapes}) cannot be met. "
        "Every .plate-img carries data-shows (SPEC §3.4); the weekly stitcher emits it "
        "from the plan's image record. If this is a pre-2026-07 issue, the failure is "
        "expected and correct — the taxonomy did not exist when it shipped."
    )
elif unknown_shapes:
    failures.append(
        f"data-shows value(s) not in the canonical enum: {unknown_shapes}. "
        f"The closed set is {sorted(shows_enum)} — see the `shows` block in "
        "references/image-source-types.json. A typo'd shape is invisible to every "
        "per-band budget in validate-issue.py, so this is a hard fail, not an advisory."
    )

if valid_shapes and len(valid_shapes) < min_shapes:
    failures.append(
        f"Shape diversity: {len(valid_shapes)} distinct shape(s) "
        f"({sorted(valid_shapes)}) < minimum of {min_shapes}. "
        "This is the defect-E floor: an issue where every picture is the same safe "
        "shape (all key art, all portraits, all Commons artefacts) tells the reader "
        "nothing the headlines didn't. Reach up the hierarchy — "
        f"information figures {info_shapes} and photographs of the actual thing "
        "happening are the fix. "
        f"{last_resort} are the last resort, and {never_lead} may never be a lead figure."
    )

# ------------------------------------------------------------ provenance axis
if not urls:
    warnings.append(
        "No external image URLs found — the provenance rules (single-domain cap, "
        "source-type diversity) are skipped for this file. The shape rules above "
        "still apply."
    )
    records = []
    total = 0
    domains = Counter()
    types_full = Counter()
    types_counted = Counter()
else:
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
    # F-17 (2026-07 WP-0): 'restricted' (Getty/Shutterstock licensed stock) is a
    # quarantine type — it draws a warning below and never counts toward the
    # source-type diversity minimum, exactly like unknown/ambiguous.
    types_counted = Counter(t for _, t in records if t not in ("unknown", "ambiguous", "restricted"))

    # Rule 1: single-domain cap
    for d, n in domains.most_common():
        pct = 100 * n / total
        if pct > thresholds["single_domain_max_pct"]:
            failures.append(
                f"RT-5 hard fail: {d} = {n}/{total} ({pct:.1f}%) > "
                f"{thresholds['single_domain_max_pct']}% cap."
            )

    # Rule 2: min source-type diversity
    if len(types_counted) < thresholds["min_distinct_source_types"]:
        failures.append(
            f"Source-type diversity: {len(types_counted)} types ({sorted(types_counted)}) "
            f"< minimum of {thresholds['min_distinct_source_types']}. "
            f"Menu: {sorted(t for t in lookup['types'] if t != 'restricted')} "
            f"('restricted' is a quarantine type and never counts)."
        )

    # Restricted (F-17): Getty/Shutterstock licensed stock — warn loudly. These
    # were mislabeled press_kit until 2026-07; preview/watermarked stock URLs are
    # not cleared for publication and must be replaced before ship.
    if "restricted" in types_full:
        restricted_domains = sorted({d for d, t in records if t == "restricted"})
        warnings.append(
            f"RESTRICTED source(s) in use (licensed stock — Getty Images/Shutterstock): {restricted_domains}. "
            "These are NOT press kits (F-17), and they are not the Getty MUSEUM's Open Content "
            "programme either. Replace with a cleared source; "
            "restricted images are excluded from source-type diversity counting."
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

# ------------------------------------------------------------------- report
print("=== Phase 7.7: check-image-diversity.sh ===")
print(f"Total images: {total}")
print(f"Distinct domains: {len(domains)}")
print(f"Labelled figures (data-shows): {sum(shapes.values())}")
print(f"Distinct shapes: {len(valid_shapes)} (floor {min_shapes})")
print()
if domains:
    print("By domain:")
    for d, n in domains.most_common():
        t = domain_map.get(d, "(unknown)")
        print(f"  {n:2}/{total}  ({100*n/total:4.1f}%)  {d:45}  → {t}")
    print()
    print(f"By source type: {dict(types_full)}")
    print()
print(f"By shape (what the pictures SHOW): {dict(shapes)}")
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
    print("  • RT-5 / source-type diversity: extend research to under-represented source")
    print("    types — the `types` menu in references/image-source-types.json now includes")
    print("    open_access_journal (the paper's own figures) alongside archive/government.")
    print("  • Shape diversity: this is not a sourcing problem, it is a SHAPE problem, and")
    print("    swapping domains will not fix it. Ask what each picture SHOWS. For a game,")
    print("    Steam's appdetails API returns a screenshots[] array per app id")
    print("    (shared.fastly.steamstatic.com, already whitelisted) — real gameplay instead")
    print("    of key art. For a science piece, take the paper's own figure. For a place or")
    print("    a route, a map. See references/compliance-checklist.md § Image specificity")
    print("    check for the full information-gained hierarchy.")
    sys.exit(1)

print("PASS — image diversity within thresholds on both axes (provenance + shape).")
sys.exit(0)
PYEOF
