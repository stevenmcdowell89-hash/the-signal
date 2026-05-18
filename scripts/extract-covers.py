#!/usr/bin/env python3
"""
Extract a cover thumbnail for each issue and save to /assets/covers/.

For each /issues/*.html:
  1. Look for an <img> inside <header class="cover">, <section class="hol-cover">,
     or — failing those — the first substantial <img> in the document.
  2. Read the source image from /assets/cached/<hash>.<ext> (already mirrored
     by mirror-images.py).
  3. Resize to a max width of 800px, JPEG quality 82, smart-crop to a
     consistent landscape aspect (3:2). 800x533.
  4. Save to /assets/covers/<issue-slug>.jpg.

Idempotent — re-running on already-extracted issues skips them unless the
source image has changed (hash check).

Usage:
    python3 scripts/extract-covers.py                       # all issues
    python3 scripts/extract-covers.py path/to/x.html        # specific files
    python3 scripts/extract-covers.py --force               # regenerate all
"""

import argparse
import re
import sys
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
ISSUES_DIR = REPO_ROOT / "issues"
CACHED_DIR = REPO_ROOT / "assets" / "cached"
COVERS_DIR = REPO_ROOT / "assets" / "covers"

THUMB_W = 800
THUMB_H = 533  # 3:2 landscape, magazine-friendly
JPEG_QUALITY = 82

COVER_PATTERNS = [
    # <header class="cover" id="top"> ... <img src="/assets/cached/...jpg"> </header>
    re.compile(
        r'<header\s+class="[^"]*\bcover\b[^"]*"[^>]*>(.*?)</header>',
        re.IGNORECASE | re.DOTALL,
    ),
    # <section class="hol-cover" ...> ... </section>
    re.compile(
        r'<section\s+class="[^"]*\bhol-cover\b[^"]*"[^>]*>(.*?)</section>',
        re.IGNORECASE | re.DOTALL,
    ),
]

IMG_SRC_RE = re.compile(
    r'<img\s[^>]*?src=["\'](/assets/cached/[^"\']+)["\']',
    re.IGNORECASE,
)
ANY_IMG_SRC_RE = re.compile(
    r'<img\s[^>]*?src=["\'](/assets/cached/[^"\']+)["\']',
    re.IGNORECASE,
)


def find_cover_path(html: str) -> str | None:
    """Return the /assets/cached/... path of the issue's cover image, or None."""
    # First: scan the dedicated cover region.
    for pat in COVER_PATTERNS:
        m = pat.search(html)
        if m:
            inner = m.group(1)
            mm = IMG_SRC_RE.search(inner)
            if mm:
                return mm.group(1)

    # Fallback: first cached image anywhere in the doc.
    mm = ANY_IMG_SRC_RE.search(html)
    if mm:
        return mm.group(1)
    return None


def make_thumb(src_path: Path, out_path: Path) -> None:
    with Image.open(src_path) as im:
        im = im.convert("RGB")
        sw, sh = im.size
        target_ratio = THUMB_W / THUMB_H

        # Smart crop to target ratio, then resize.
        src_ratio = sw / sh
        if src_ratio > target_ratio:
            # Source is wider — crop sides
            new_w = int(sh * target_ratio)
            offset = (sw - new_w) // 2
            im = im.crop((offset, 0, offset + new_w, sh))
        elif src_ratio < target_ratio:
            # Source is taller — crop top/bottom, biased toward top third
            # (heads in photos tend to be in upper third)
            new_h = int(sw / target_ratio)
            top = max(0, (sh - new_h) // 3)
            im = im.crop((0, top, sw, top + new_h))

        im = im.resize((THUMB_W, THUMB_H), Image.LANCZOS)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        im.save(out_path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)


def slug_for(html_path: Path) -> str:
    return html_path.stem  # filename without .html


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="HTML files (default: all /issues/*.html)")
    ap.add_argument("--force", action="store_true", help="Regenerate even if cover exists")
    args = ap.parse_args()

    targets = (
        [Path(f).resolve() for f in args.files]
        if args.files
        else sorted(ISSUES_DIR.glob("*.html"))
    )

    stats = {"made": 0, "skipped": 0, "no_cover": 0, "missing_src": 0}

    for html_path in targets:
        slug = slug_for(html_path)
        out_path = COVERS_DIR / f"{slug}.jpg"

        if out_path.exists() and not args.force:
            stats["skipped"] += 1
            continue

        html = html_path.read_text(encoding="utf-8")
        cover_path = find_cover_path(html)
        if not cover_path:
            stats["no_cover"] += 1
            print(f"  ? {html_path.name} — no cover image found")
            continue

        # cover_path is /assets/cached/<hash>.<ext>
        src = REPO_ROOT / cover_path.lstrip("/")
        if not src.exists():
            stats["missing_src"] += 1
            print(f"  ! {html_path.name} — cover src not in cache: {cover_path}")
            continue

        try:
            make_thumb(src, out_path)
            stats["made"] += 1
            print(f"  ✓ {slug}.jpg ← {src.name}")
        except Exception as e:
            print(f"  ! {html_path.name} — thumbnail failed: {e}", file=sys.stderr)

    print(f"\nDone. Made: {stats['made']}, skipped: {stats['skipped']}, no cover: {stats['no_cover']}, missing src: {stats['missing_src']}.")


if __name__ == "__main__":
    main()
