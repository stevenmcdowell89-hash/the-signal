#!/usr/bin/env python3
"""
validate-research-bundle.py — Phase 3b upstream gate.

Validates research-bundle.json's image_candidates BEFORE the planner spawns,
catching the two failure modes that propagated through the 17 May test issue:

  1. Fabricated URLs   — image_candidates entries with `url_or_keyword`
                         containing a keyword ("Wikimedia: Starmer") instead
                         of a verified URL. Forces writers to invent URLs.

  2. Mono-sourcing     — too many entries from one domain (typically Wikimedia
                         Special:FilePath because it verifies easily). Fails
                         RT-5 (single-domain >50%) and the tighter 30%
                         Wikimedia cap.

Reads the lookup table at references/image-source-types.json to classify
domains. Domains not in the lookup are flagged as "unknown" — counted toward
domain-ratio thresholds but not toward source-type diversity.

Usage:
  python3 scripts/validate-research-bundle.py /tmp/signal-build/research-bundle.json

Exit codes:
  0 — PASS
  1 — FAIL (one or more rules violated; report printed)
  2 — usage / missing file
"""
import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


def load_lookup(skill_dir: Path) -> dict:
    p = skill_dir / "references" / "image-source-types.json"
    if not p.exists():
        print(f"ERROR: lookup table not found at {p}", file=sys.stderr)
        sys.exit(2)
    return json.loads(p.read_text())


def classify_domain(url: str, lookup: dict, explicit_type: str | None = None) -> str:
    """Return source_type for a URL. explicit_type wins; otherwise lookup by domain."""
    if explicit_type and explicit_type in lookup["types"]:
        return explicit_type
    netloc = urlparse(url).netloc.lower()
    # Strip leading www. — but only as a fallback; some keys include www.
    if netloc in lookup["domains"]:
        return lookup["domains"][netloc]
    stripped = netloc.removeprefix("www.")
    if stripped in lookup["domains"]:
        return lookup["domains"][stripped]
    # Flickr-style ambiguous host: needs explicit annotation
    if netloc in lookup.get("ambiguous_domains", {}):
        return "ambiguous"
    return "unknown"


def main():
    if len(sys.argv) < 2:
        print("Usage: validate-research-bundle.py <research-bundle.json>", file=sys.stderr)
        sys.exit(2)

    bundle_path = Path(sys.argv[1])
    if not bundle_path.exists():
        print(f"ERROR: {bundle_path} not found", file=sys.stderr)
        sys.exit(2)

    skill_dir = Path(__file__).resolve().parent.parent
    lookup = load_lookup(skill_dir)
    thresholds = lookup["thresholds"]

    bundle = json.loads(bundle_path.read_text())
    candidates = bundle.get("image_candidates", [])

    if not candidates:
        print("ADVISORY: research-bundle.json has no image_candidates — skipping image-source validation.")
        sys.exit(0)

    failures = []
    warnings = []

    # Per-entry validation
    valid_entries = []
    for i, c in enumerate(candidates):
        url = c.get("url_or_keyword", "")
        explicit_type = c.get("source_type")
        ctx = c.get("context", f"entry[{i}]")

        if not url:
            warnings.append(f"  entry[{i}] ({ctx}): no url_or_keyword — will be skipped by writers")
            continue

        if not url.startswith(("http://", "https://")):
            failures.append(
                f"  entry[{i}] ({ctx}): url_or_keyword is not a URL: {url!r}\n"
                f"    Researcher must supply a direct, verified URL — keywords force writers to guess. See RT-16."
            )
            continue

        stype = classify_domain(url, lookup, explicit_type)
        if stype == "ambiguous":
            failures.append(
                f"  entry[{i}] ({ctx}): {urlparse(url).netloc} requires explicit source_type field.\n"
                f"    See ambiguous_domains in image-source-types.json. URL: {url}"
            )
            continue
        if stype == "unknown":
            warnings.append(
                f"  entry[{i}] ({ctx}): domain {urlparse(url).netloc} not in lookup — classified as 'unknown'.\n"
                f"    Add to references/image-source-types.json domains map if this is a real recurring source."
            )

        valid_entries.append((url, stype, ctx))

    # Aggregate validation
    if valid_entries:
        domains = Counter(urlparse(u).netloc for u, _, _ in valid_entries)
        types = Counter(t for _, t, _ in valid_entries if t not in ("unknown", "ambiguous"))
        total = len(valid_entries)

        # Rule 1: single-domain cap (RT-5 hard)
        for d, n in domains.items():
            pct = 100 * n / total
            if pct > thresholds["single_domain_max_pct"]:
                failures.append(
                    f"  RT-5 hard fail: {d} provides {n}/{total} images ({pct:.1f}%). "
                    f"Cap is {thresholds['single_domain_max_pct']}%."
                )

        # Rule 2: Wikimedia cap (lower of pct or count)
        wm = sum(n for d, n in domains.items()
                 if lookup["domains"].get(d) == "wikimedia")
        wm_pct = 100 * wm / total if total else 0
        if wm > thresholds["wikimedia_max_count"]:
            failures.append(
                f"  Wikimedia entries: {wm} > cap of {thresholds['wikimedia_max_count']}. "
                f"Wikimedia is a supplement — pull more from press kits / government / archive / news CDNs."
            )
        if wm_pct > thresholds["wikimedia_max_pct"]:
            failures.append(
                f"  Wikimedia ratio: {wm}/{total} = {wm_pct:.1f}% > cap of {thresholds['wikimedia_max_pct']}%."
            )

        # Rule 3: minimum distinct source types
        if len(types) < thresholds["min_distinct_source_types"]:
            failures.append(
                f"  Source-type diversity: {len(types)} types represented ({sorted(types)}) "
                f"< minimum of {thresholds['min_distinct_source_types']}.\n"
                f"    The 5-type menu: {sorted(lookup['types'].keys())}."
            )

    # Report
    print("=== Phase 3b: validate-research-bundle.py ===")
    print(f"image_candidates entries: {len(candidates)}")
    print(f"valid URL entries:        {len(valid_entries)}")
    if valid_entries:
        types_repr = Counter(t for _, t, _ in valid_entries)
        print(f"by source type:           {dict(types_repr)}")
    print()

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(w)
        print()

    if failures:
        print("FAIL — rule violations:")
        for f in failures:
            print(f)
        print()
        print("Re-spawn the researcher with this report so the bundle can be corrected before Phase 4 (planner).")
        sys.exit(1)

    print("PASS — research bundle image_candidates comply with image-integrity rules.")
    sys.exit(0)


if __name__ == "__main__":
    main()
