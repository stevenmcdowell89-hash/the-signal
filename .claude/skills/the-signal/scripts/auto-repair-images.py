#!/usr/bin/env python3
"""
auto-repair-images.py — Phase 9 programmatic image-defect repair.

Strengthens the in-pipeline repair loop so it doesn't depend on a subagent
remembering to do anything. Takes a stitched HTML + research bundle, finds
the image defects the Phase 7.6/7.7/7.8 gates catch, and substitutes
unused bundle URLs in-place. Pure Python — no subagent calls, no network.

Repairs:
  - D6 duplicates → second+ occurrences of a URL are replaced with the
    next unused bundle URL (preference: same data-venue scope, then any)
  - D7 unbundled → any DOM URL not in image_candidates is replaced with
    an unused bundle URL of matching venue scope
  - D3 page-URL (no image extension) → same as D7
  - Phase 7.6 page-URL-as-image static fails → same as D7

If the bundle is exhausted before all defects are fixed, the script
exits with a partial-repair status and a report of unfixable defects.
The orchestrator's loop budget (3 rounds in Phase 9) absorbs this:
after 3 rounds of best-effort, the pipeline publishes whatever's left.

Usage:
  python3 scripts/auto-repair-images.py <stitched-html> <bundle.json>
  [--max-uses-per-url N]  (default 1)
  [--dry-run]             (print plan, don't write)

Exit codes:
  0 — no defects, or all defects repaired
  1 — partial repair (bundle exhausted; some defects remain)
  2 — usage / missing file
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional


IMG_EXTS = (
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".svg",
    ".JPG", ".JPEG", ".PNG", ".WEBP", ".GIF", ".AVIF", ".SVG",
)


def strip_inline(html: str) -> str:
    """Strip comments, style, script blocks for DOM-only scanning."""
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    return html


def has_image_extension(url: str) -> bool:
    return url.split("?", 1)[0].split("#", 1)[0].endswith(IMG_EXTS)


def find_image_refs(raw_html: str) -> list[tuple[int, int, str, str]]:
    """Return [(start, end, url, kind), ...] for every <img src> and
    background-image:url() in the OUT-OF-STYLE/SCRIPT portion of the HTML.
    Positions are in the original raw_html so we can slice it for replacement.
    """
    # Build a mask of regions to ignore (inside <style>, <script>, comments).
    # Order matters: comments first, then style/script — and we skip pattern
    # matches whose start is already masked, so an example <script> mention
    # inside a comment doesn't fire its own (huge) script-strip region.
    mask = bytearray(len(raw_html))
    for pat in (
        r"<!--.*?-->",
        r"<style[^>]*>.*?</style>",
        r"<script[^>]*>.*?</script>",
    ):
        for m in re.finditer(pat, raw_html, flags=re.DOTALL | re.IGNORECASE):
            if mask[m.start()]:
                continue  # this opening tag is already inside an earlier masked region
            for i in range(m.start(), m.end()):
                mask[i] = 1

    refs: list[tuple[int, int, str, str]] = []

    img_re = re.compile(r'<img\b[^>]*?\bsrc\s*=\s*"([^"]+)"', re.IGNORECASE)
    for m in img_re.finditer(raw_html):
        if not mask[m.start()]:
            url = m.group(1)
            # Compute the absolute span of the URL itself (between the quotes).
            url_start = raw_html.find(url, m.start())
            url_end = url_start + len(url)
            refs.append((url_start, url_end, url, "img"))

    bg_re = re.compile(
        r"background(?:-image)?\s*:\s*[^;\"']*?url\(\s*['\"]?([^'\")]+)['\"]?\s*\)",
        re.IGNORECASE,
    )
    for m in bg_re.finditer(raw_html):
        if not mask[m.start()]:
            url = m.group(1)
            url_start = raw_html.find(url, m.start())
            url_end = url_start + len(url)
            refs.append((url_start, url_end, url, "bg"))

    refs.sort()
    return refs


def find_chapter_at(html: str, position: int) -> tuple[str | None, str | None]:
    """Return (chapter_id, data_venue) for the <section data-sp-chapter> that
    contains `position`. None if the position isn't inside any chapter
    (e.g. inside .hol-cover or .hol-masthead, which don't carry sp-chapter)."""
    # Find every section open before this position; pick the latest one whose
    # close is after this position. Naive but correct for flat chapter sections.
    best: tuple[str | None, str | None] = (None, None)
    for m in re.finditer(
        r'<section\b[^>]*\bdata-sp-chapter="([^"]+)"[^>]*>',
        html,
        re.IGNORECASE,
    ):
        if m.start() > position:
            break
        # Find matching close
        depth = 1
        pos = m.end()
        while depth > 0 and pos < len(html):
            no = html.find("<section", pos)
            nc = html.find("</section>", pos)
            if nc == -1:
                break
            if no != -1 and no < nc:
                depth += 1
                pos = no + 8
            else:
                depth -= 1
                pos = nc + 10
                if depth == 0 and pos > position:
                    venue_m = re.search(r'data-venue="([^"]+)"', m.group())
                    best = (m.group(1), venue_m.group(1).lower() if venue_m else None)
    return best


def main() -> int:
    ap = argparse.ArgumentParser(description="Programmatic image-defect repair for The Signal.")
    ap.add_argument("html_path", type=Path)
    ap.add_argument("bundle_path", type=Path)
    ap.add_argument("--max-uses-per-url", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.html_path.exists():
        print(f"ERROR: {args.html_path} not found", file=sys.stderr)
        return 2
    if not args.bundle_path.exists():
        print(f"ERROR: {args.bundle_path} not found", file=sys.stderr)
        return 2

    raw = args.html_path.read_text(encoding="utf-8")
    bundle = json.loads(args.bundle_path.read_text(encoding="utf-8"))

    # ── Index the bundle by venue ──────────────────────────────────────────
    # Each candidate's `venue` field (set by the researcher) tells us where it
    # fits. Candidates with venue="both" or no venue are usable anywhere.
    candidates_by_venue: dict[str | None, list[str]] = defaultdict(list)
    bundle_url_set: set[str] = set()
    for c in bundle.get("image_candidates", []):
        url = c.get("url_or_keyword", "").strip()
        if not url or not has_image_extension(url):
            continue
        bundle_url_set.add(url)
        venue = (c.get("venue") or "").strip().lower() or None
        if venue == "both":
            venue = None
        candidates_by_venue[venue].append(url)

    if not bundle_url_set:
        print("ABORT: bundle has no usable image_candidates.")
        return 1

    # ── Scan DOM for image refs ───────────────────────────────────────────
    refs = find_image_refs(raw)
    if not refs:
        print("OK: no image refs in DOM.")
        return 0

    counts = Counter(url for _, _, url, _ in refs)

    print(f"=== auto-repair-images.py ===")
    print(f"DOM image refs:     {len(refs)} ({len(counts)} unique URLs)")
    print(f"Bundle candidates:  {len(bundle_url_set)} unique URLs")
    print()

    # ── Identify defects ──────────────────────────────────────────────────
    # Strategy: walk refs in order. For each, classify the issue. If the URL
    # is fine, leave it alone. If it's defective, find a replacement and
    # substitute.

    # Track which bundle URLs we've already assigned (so we don't introduce
    # new duplicates).
    used: Counter[str] = Counter()
    # Pre-seed `used` with the URLs already in the DOM that we'll keep.
    # We decide what to keep below; for now compute a "keepers" pass:
    # for any URL appearing > max_uses_per_url times, the FIRST occurrences
    # up to the limit are keepers, the rest are duplicates to replace.
    keeper_indices: set[int] = set()
    seen_keep: Counter[str] = Counter()
    for i, (_, _, url, _) in enumerate(refs):
        # If URL is bundled + has extension, it's "good content"
        good_content = url in bundle_url_set and has_image_extension(url)
        if good_content and seen_keep[url] < args.max_uses_per_url:
            keeper_indices.add(i)
            seen_keep[url] += 1
            used[url] += 1

    # Anything not a keeper is a defect to repair.
    defect_indices = [i for i in range(len(refs)) if i not in keeper_indices]

    repairs: list[tuple[int, str, str, str]] = []  # (ref_index, old_url, new_url, reason)
    unfixable: list[tuple[int, str, str]] = []  # (ref_index, old_url, reason)

    def pick_replacement(venue: str | None) -> Optional[str]:
        """Pick the next bundle URL with capacity, preferring same venue.
        Returns None if every candidate is at the use limit — the caller
        marks the defect unfixable and the orchestrator's Phase 9 loop
        budget absorbs it (publish-anyway after 3 rounds)."""
        # Try venue-specific candidates first. Try any-venue candidates second.
        for pool_venue in (venue, None):
            # Iterate candidates_by_venue in original order so substitutions
            # are deterministic across re-runs.
            for url in candidates_by_venue.get(pool_venue, []):
                if used[url] < args.max_uses_per_url:
                    used[url] += 1
                    return url
        # Also try EVERY bundle URL (in case the venue match was wrong)
        for url in sorted(bundle_url_set):
            if used[url] < args.max_uses_per_url:
                used[url] += 1
                return url
        return None  # bundle exhausted — unfixable

    for i in defect_indices:
        start, end, old_url, kind = refs[i]
        ch_id, venue = find_chapter_at(raw, start)
        # Classify defect
        if old_url in bundle_url_set and seen_keep[old_url] >= args.max_uses_per_url:
            reason = f"duplicate (URL used {counts[old_url]}x, max {args.max_uses_per_url})"
        elif old_url not in bundle_url_set and has_image_extension(old_url):
            reason = "unbundled (URL not in image_candidates)"
        elif not has_image_extension(old_url):
            reason = "page-URL-as-image (no image extension)"
        else:
            reason = "other defect"
        new_url = pick_replacement(venue)
        if new_url:
            repairs.append((i, old_url, new_url, f"{reason} [chapter={ch_id or '-'}, venue={venue or '-'}]"))
        else:
            unfixable.append((i, old_url, reason))

    # ── Report + write ────────────────────────────────────────────────────
    print(f"Defects found: {len(defect_indices)}")
    print(f"  Repairable:  {len(repairs)}")
    print(f"  Unfixable:   {len(unfixable)} (bundle exhausted)")
    print()

    for i, old, new, why in repairs:
        print(f"  REPAIR [{why}]")
        print(f"    old: {old}")
        print(f"    new: {new}")
    if unfixable:
        print()
        for i, old, why in unfixable:
            print(f"  UNFIXABLE [{why}]: {old}")

    if args.dry_run:
        print("\n(--dry-run: no file written)")
        return 0 if not unfixable else 1

    # Apply repairs from end to start (so positions stay valid)
    repairs_by_index = {ri: (old, new) for ri, old, new, _ in repairs}
    out = raw
    for i in sorted(defect_indices, reverse=True):
        if i not in repairs_by_index:
            continue
        start, end, _, _ = refs[i]
        _, new = repairs_by_index[i]
        out = out[:start] + new + out[end:]

    args.html_path.write_text(out, encoding="utf-8")
    print(f"\nWrote {len(repairs)} repair(s) to {args.html_path}")
    return 0 if not unfixable else 1


if __name__ == "__main__":
    sys.exit(main())
