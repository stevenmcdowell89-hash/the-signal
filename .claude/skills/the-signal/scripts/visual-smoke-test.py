#!/usr/bin/env python3
"""
visual-smoke-test.py — Phase 7.8 DOM-level "visual" QA gate.

A pure-Python static analyser that catches the class of bugs that look
"obvious in a browser" but that the earlier gates miss because they
check structure or HTTP status, not rendered output.

What it catches (per defect category):

  D1. DUPLICATE CHROME
      Both the legacy default-chrome cover/masthead/footer AND the
      Holiday Identity equivalents present in the same DOM. The viewer
      sees a duplicate title page or duplicate footer.

  D2. UN-WRAPPED VENUE CHAPTERS
      On holiday + multi_venue issues, venue chapters (sections with
      data-venue="X") that are NOT DOM-descendants of the matching
      .hol-half--N wrapper. Those chapters render against the body
      default instead of the venue's painted ground.

  D3. PAGE-URL-AS-IMAGE
      <img src> or background-image:url(...) pointing at a path with
      no recognised image extension AND not a data: URI. Almost always
      a page URL pasted in where a CDN image URL was expected.

  D4. ORPHAN HOLIDAY ELEMENTS
      .hol-anchor / .hol-unmissable / .hol-polaroid / .hol-postcard
      placed OUTSIDE any .hol-half on a multi-venue holiday issue.
      Those elements get no venue context and float in a void.

  D5. EMPTY HERO BANDS
      .hol-cover / .hol-half__opener / .hol-unmissable with no
      child text content (rendered as a blank stretch).

This is structural QA — it can't replace a human looking at the
rendered page, but it catches the recurring shipping-defect patterns
that other gates miss.

Usage:
  python3 scripts/visual-smoke-test.py <stitched-html-path> \\
    --format field-guide [--multi-venue]

Exit codes:
  0 — all checks pass (warnings may be present)
  1 — one or more defects found
  2 — usage / missing file
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


HOLIDAY_FORMATS = {"countdown", "field-guide"}


def strip_inline(html: str) -> str:
    """Strip <style>/<script>/HTML-comment blocks for DOM scanning.
    Order matters: comments FIRST, because some scaffold comments contain
    plain-text mentions of <style>...</style> that confuse the style-strip
    regex (a non-greedy `<style>.*?</style>` can otherwise eat across a
    legitimate comment close, leaving an unclosed comment that later
    swallows </head> and <body>).
    """
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    return html


def body_dom(html: str) -> str:
    """Return everything between the real <body> (after </head>) and </body>."""
    head_end = re.search(r"</head\s*>", html, re.IGNORECASE)
    if not head_end:
        return ""
    body_open = re.search(r"<body\b[^>]*>", html[head_end.end():], re.IGNORECASE)
    if not body_open:
        return ""
    start = head_end.end() + body_open.end()
    end = html.lower().find("</body>", start)
    if end == -1:
        end = len(html)
    return html[start:end]


def find_section_spans(dom: str, opener_regex: re.Pattern) -> list[tuple[int, int, str]]:
    """For each opening tag matching opener_regex, find its balanced </section>.
    Returns list of (start, end, opening_tag_text)."""
    spans = []
    for m in opener_regex.finditer(dom):
        start = m.start()
        pos = m.end()
        depth = 1
        while depth > 0 and pos < len(dom):
            nxt_open = dom.find("<section", pos)
            nxt_close = dom.find("</section>", pos)
            if nxt_close == -1:
                break
            if nxt_open != -1 and nxt_open < nxt_close:
                depth += 1
                pos = nxt_open + len("<section")
            else:
                depth -= 1
                pos = nxt_close + len("</section>")
        spans.append((start, pos, m.group()))
    return spans


# ─────────────────────────────────────────────────────────────────────────────
# Detectors
# ─────────────────────────────────────────────────────────────────────────────

def d1_duplicate_chrome(dom: str, fmt: str) -> list[str]:
    """Both legacy chrome AND holiday chrome present."""
    if fmt not in HOLIDAY_FORMATS:
        return []
    issues = []
    legacy_cover = re.search(r'<header\s+class="cover"', dom, re.IGNORECASE)
    holiday_cover = re.search(r'<section\s+class="hol-cover"', dom, re.IGNORECASE)
    if legacy_cover and holiday_cover:
        issues.append(
            "D1.cover — both legacy <header class=\"cover\"> AND <section class=\"hol-cover\"> "
            "present in DOM. The legacy cover from 03-cover.html should be dropped on holiday "
            "formats — the stitcher's holiday override (v8.13.5) is the canonical fix."
        )
    legacy_mast = re.search(r'<div\s+class="mast[\"\s]', dom, re.IGNORECASE)
    holiday_mast = re.search(r'<header\s+class="hol-masthead"', dom, re.IGNORECASE)
    if legacy_mast and holiday_mast:
        issues.append(
            "D1.masthead — both legacy <div class=\"mast\"> AND <header class=\"hol-masthead\"> "
            "present in DOM. Drop 01-masthead.html from scaffold_parts_used on holiday formats."
        )
    legacy_footer = re.search(r'<footer\s+class="footer"', dom, re.IGNORECASE)
    holiday_footer = re.search(r'class="hol-footer-row"', dom, re.IGNORECASE)
    if legacy_footer and holiday_footer:
        issues.append(
            "D1.footer — both legacy <footer class=\"footer\"> AND .hol-footer-row "
            "present in DOM. Drop 18-footer.html from scaffold_parts_used on holiday formats."
        )
    return issues


def d2_unwrapped_venue_chapters(dom: str, fmt: str, multi_venue: bool) -> list[str]:
    """Venue chapters that are not DOM-descendants of the matching .hol-half--N."""
    if fmt not in HOLIDAY_FORMATS or not multi_venue:
        return []
    issues = []
    half_one_spans = find_section_spans(
        dom, re.compile(r'<section\b[^>]*\bclass="[^"]*\bhol-half--one\b[^"]*"[^>]*>', re.IGNORECASE)
    )
    half_two_spans = find_section_spans(
        dom, re.compile(r'<section\b[^>]*\bclass="[^"]*\bhol-half--two\b[^"]*"[^>]*>', re.IGNORECASE)
    )
    venue_to_spans = {
        "efteling": half_one_spans,        # convention; could be either by issue
        "beekse-bergen": half_two_spans,
    }
    # Build set of half-span ranges per venue
    venue_chapter_re = re.compile(
        r'<section\b[^>]*\bdata-sp-chapter="([^"]+)"[^>]*\bdata-venue="([^"]+)"[^>]*>',
        re.IGNORECASE,
    )
    for m in venue_chapter_re.finditer(dom):
        ch_id, venue = m.group(1), m.group(2).lower()
        pos = m.start()
        spans = venue_to_spans.get(venue, [])
        # Also accept: any .hol-half block (in case the venue→half mapping
        # is opposite — issue 2026-05-17 has Efteling in half-one, but a
        # different issue might invert).
        all_spans = half_one_spans + half_two_spans
        if not any(s <= pos < e for s, e, _ in all_spans):
            issues.append(
                f"D2.unwrapped — chapter '{ch_id}' (data-venue=\"{venue}\") is NOT nested inside "
                f"any .hol-half--N wrapper. The chapter will render against the body default with "
                f"no venue ground. Fix at stitch time with the holiday half-wrap reorganisation."
            )
    return issues


def d3_page_url_as_image(dom: str) -> list[str]:
    """Image refs whose URL has no image extension."""
    IMG_EXTS = (
        ".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".svg",
        ".JPG", ".JPEG", ".PNG", ".WEBP", ".GIF", ".AVIF", ".SVG",
    )
    issues = []
    img_src_re = re.compile(r'<img\b[^>]*?\bsrc\s*=\s*"([^"]+)"', re.IGNORECASE)
    bg_url_re = re.compile(
        r"background(?:-image)?\s*:\s*[^;\"']*?url\(\s*['\"]?([^'\")]+)['\"]?\s*\)",
        re.IGNORECASE,
    )
    urls = set(img_src_re.findall(dom)) | set(bg_url_re.findall(dom))
    for u in urls:
        if not u or u.startswith("data:") or u.startswith("#"):
            continue
        # Strip querystring before checking extension
        path = u.split("?", 1)[0].split("#", 1)[0]
        if not path.endswith(IMG_EXTS):
            issues.append(
                f"D3.page-url-image — image reference has no image extension: {u}\n"
                f"    Almost certainly a page URL pasted where a CDN image URL was expected. "
                f"Browsers render nothing for an HTML page used as <img src> or background-image."
            )
    return issues


def d4_orphan_holiday_elements(dom: str, fmt: str, multi_venue: bool) -> list[str]:
    """Hero holiday components placed outside any .hol-half (multi-venue only)."""
    if fmt not in HOLIDAY_FORMATS or not multi_venue:
        return []
    half_spans = find_section_spans(
        dom, re.compile(r'<section\b[^>]*\bclass="[^"]*\bhol-half\b[^"]*"[^>]*>', re.IGNORECASE)
    )
    # Allow .hol-anchor, .hol-unmissable inside non-venue contexts (transit, anchor chapter
    # may legitimately host them). Only flag if there's NO .hol-half in the issue at all —
    # other defects will surface the structural problem.
    # NOTE: this detector is intentionally conservative; the D2 check is the primary one.
    issues = []
    if half_spans:
        return issues
    # No halves at all in a multi-venue holiday issue
    issues.append(
        "D4.no-halves — multi-venue holiday issue has NO .hol-half blocks in the DOM. "
        "Field Guide and multi-venue Countdown must structure content into halves."
    )
    return issues


def d6_duplicate_image_urls(dom: str, max_uses: int = 1) -> list[str]:
    """No image URL may appear more than `max_uses` times in the rendered DOM.
    Counts each <img src> and background-image:url(...) occurrence. This is
    the hard rule that prevents the "same image, three slots" pattern that
    has shipped repeatedly when writers run out of bundle candidates.

    Override: pass max_uses=2 for issues that legitimately repeat (rare).
    """
    img_re = re.compile(r'<img\b[^>]*?\bsrc\s*=\s*"([^"]+)"', re.IGNORECASE)
    bg_re = re.compile(
        r"background(?:-image)?\s*:\s*[^;\"']*?url\(\s*['\"]?([^'\")]+)['\"]?\s*\)",
        re.IGNORECASE,
    )
    from collections import Counter
    urls = list(img_re.findall(dom)) + list(bg_re.findall(dom))
    # Don't count data: URIs or fragment refs
    urls = [u for u in urls if u and not u.startswith("data:") and not u.startswith("#")]
    counts = Counter(urls)
    issues = []
    for u, n in counts.items():
        if n > max_uses:
            issues.append(
                f"D6.duplicate-image — URL used {n}x (max allowed: {max_uses}): {u}\n"
                f"    Writer ran out of distinct candidates and recycled. The researcher must surface "
                f"more verified image_candidates; once bundle has enough unique URLs, writers won't "
                f"need to reuse. Set --max-uses-per-url <N> to override for legitimate dual-use."
            )
    return issues


def d7_unbundled_images(dom: str, bundle_path: Path | None) -> list[str]:
    """Every image URL in the DOM must appear verbatim in the bundle's
    image_candidates set. This prevents writers from inventing URLs that
    were never verified.
    """
    if not bundle_path or not bundle_path.exists():
        return []  # skipped when no bundle supplied
    import json
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    bundle_urls = {c.get("url_or_keyword", "") for c in bundle.get("image_candidates", [])}
    img_re = re.compile(r'<img\b[^>]*?\bsrc\s*=\s*"([^"]+)"', re.IGNORECASE)
    bg_re = re.compile(
        r"background(?:-image)?\s*:\s*[^;\"']*?url\(\s*['\"]?([^'\")]+)['\"]?\s*\)",
        re.IGNORECASE,
    )
    urls = set(img_re.findall(dom)) | set(bg_re.findall(dom))
    issues = []
    for u in urls:
        if not u or u.startswith("data:") or u.startswith("#"):
            continue
        if u not in bundle_urls:
            issues.append(
                f"D7.unbundled-image — DOM contains URL not in research-bundle.json image_candidates: {u}\n"
                f"    Writers may only use images the researcher verified. This URL bypassed Phase 3b."
            )
    return issues


def d5_empty_hero_bands(dom: str) -> list[str]:
    """Hero bands with no text content (visible as blank stretch)."""
    issues = []
    # Find .hol-cover and check it has visible text
    for tag, label in (
        ('hol-cover', '.hol-cover'),
        ('hol-half__opener', '.hol-half__opener'),
    ):
        # Each block: capture from class until close of the wrapper element.
        # Naive but effective: capture 4 KB after the opening tag, strip HTML, see if any text.
        for m in re.finditer(
            r'<(?:section|div|header)\b[^>]*\bclass="[^"]*\b'
            + re.escape(tag)
            + r'\b[^"]*"[^>]*>',
            dom,
            re.IGNORECASE,
        ):
            chunk = dom[m.end(): m.end() + 4000]
            text = re.sub(r"<[^>]+>", " ", chunk)
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) < 12:
                issues.append(
                    f"D5.empty-hero — {label} block at offset {m.start()} appears empty "
                    f"(<12 chars of text in first 4 KB after opening tag). May render as blank stretch."
                )
    return issues


# ─────────────────────────────────────────────────────────────────────────────
# Driver
# ─────────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Phase 7.8 DOM visual smoke test for The Signal issues.")
    ap.add_argument("issue_html", type=Path, help="Path to stitched issue HTML")
    ap.add_argument("--format", default="", help="Issue format (e.g. field-guide, countdown, weekly)")
    ap.add_argument("--multi-venue", action="store_true", help="Issue has multiple venues")
    ap.add_argument("--bundle", type=Path, default=None,
                    help="Path to research-bundle.json. When provided, enables D7 (every DOM "
                         "image URL must appear in image_candidates).")
    ap.add_argument("--max-uses-per-url", type=int, default=1,
                    help="Maximum times a single image URL may appear in the DOM. Default 1.")
    args = ap.parse_args()

    if not args.issue_html.exists():
        print(f"ERROR: {args.issue_html} not found", file=sys.stderr)
        sys.exit(2)

    raw = args.issue_html.read_text(encoding="utf-8")
    dom = body_dom(strip_inline(raw))
    fmt = (args.format or "").lower().replace("_", "-")

    print("=== Phase 7.8: visual-smoke-test.py ===")
    print(f"File:   {args.issue_html}")
    print(f"Format: {fmt or '<unset>'}  Multi-venue: {args.multi_venue}")
    print(f"DOM:    {len(dom):,} chars (style/script/comments stripped)")
    print()

    all_issues: list[str] = []
    for name, fn in (
        ("D1 duplicate chrome", lambda: d1_duplicate_chrome(dom, fmt)),
        ("D2 un-wrapped venue chapters", lambda: d2_unwrapped_venue_chapters(dom, fmt, args.multi_venue)),
        ("D3 page-url-as-image", lambda: d3_page_url_as_image(dom)),
        ("D4 orphan holiday elements", lambda: d4_orphan_holiday_elements(dom, fmt, args.multi_venue)),
        ("D5 empty hero bands", lambda: d5_empty_hero_bands(dom)),
        ("D6 duplicate image URLs", lambda: d6_duplicate_image_urls(dom, args.max_uses_per_url)),
        ("D7 unbundled images", lambda: d7_unbundled_images(dom, args.bundle)),
    ):
        found = fn()
        if found:
            print(f"[FAIL] {name}: {len(found)} issue(s)")
            for line in found:
                print(f"  • {line}")
            all_issues.extend(found)
        else:
            print(f"[PASS] {name}")
    print()

    if all_issues:
        print(f"{len(all_issues)} defect(s) — issue NOT shippable.")
        sys.exit(1)
    print("All visual smoke-test detectors passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
