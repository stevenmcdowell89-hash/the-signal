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

WP-8 / SPEC §3.10 — licence gate
--------------------------------
Cropping and resizing produce a *derivative work*. Any NoDerivatives licence
(CC BY-ND, CC BY-NC-ND, …) forbids distributing one. This script therefore
reads `assets/cached/manifest.json` and refuses to derive a cover from a
source whose `licence.allows_derivatives` is `false`, exiting non-zero and
naming the file and the licence.

Three licence states, three behaviours:

  allows_derivatives  behaviour
  ------------------  --------------------------------------------------------
  true                derive normally
  false               REFUSE. Never write, never touch an existing cover.
                      Run exits non-zero.
  null / no entry     UNKNOWN. Warn loudly and proceed by default; refuse
                      under --strict-licence.

Why unknown proceeds by default: 438 assets were cached before the manifest
existed and their provenance is unrecoverable, and `licence` only starts
arriving once the research bundle is wired through (WP-1 §3.2 contract, WP-5
enforcement, WP-9 wiring). Hard-failing on unknown today would refuse every
cover in the archive and every new issue as well — a gate that blocks
everything is switched off within a week, and it would add no signal, because
"unknown" is not evidence of an ND licence. So the default fails safe on
*known* prohibition and stays loud about the gap; `--strict-licence` escalates
unknown to refusal and is the intended setting once licences are populated.

This is forward-looking. Issue #18's cover source is credited CC BY-NC-ND and
its existing cover is a live violation, but SPEC §1 rule 3 freezes #18: the
cover is not re-cropped, regenerated or deleted (see FROZEN_SLUGS).

Usage:
    python3 scripts/extract-covers.py                       # all issues
    python3 scripts/extract-covers.py path/to/x.html        # specific files
    python3 scripts/extract-covers.py --force               # regenerate all
    python3 scripts/extract-covers.py --strict-licence      # unknown => refuse
    python3 scripts/extract-covers.py --nd-fallback contain # see below
    python3 scripts/extract-covers.py --manifest PATH       # alternate manifest
"""

import argparse
import json
import re
import sys
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
ISSUES_DIR = REPO_ROOT / "issues"
CACHED_DIR = REPO_ROOT / "assets" / "cached"
COVERS_DIR = REPO_ROOT / "assets" / "covers"
MANIFEST_PATH = CACHED_DIR / "manifest.json"

THUMB_W = 800
THUMB_H = 533  # 3:2 landscape, magazine-friendly
JPEG_QUALITY = 82

# SPEC §1 rule 3: Issue #18 is the evidence exhibit and the regression fixture.
# Its cover stays exactly as published even under --force.
FROZEN_SLUGS = frozenset({"signal_weekly_2026-07-26"})

# Exit code when a source's licence forbids the derivative.
EXIT_LICENCE_REFUSED = 2

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
    # WP-6 mx-compat: new-system covers — <section class="mx-cover ..."> ... </section>
    re.compile(
        r'<section\s+class="[^"]*\bmx-cover\b[^"]*"[^>]*>(.*?)</section>',
        re.IGNORECASE | re.DOTALL,
    ),
]

# WP-6 mx-compat: scan the DOM only. The unified bundle inlines CSS whose
# comments contain example markup (e.g. `<img src="/assets/cached/img.jpg">`
# in core/10-ephemera.css) — scanning raw HTML made the fallback matcher pick
# those up as "covers". Strip comments/<style>/<script> before matching.
def _dom_only(html: str) -> str:
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    html = re.sub(r"<style\b[^>]*>.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<script\b[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    return html

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
    html = _dom_only(html)
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


# ---------------------------------------------------------------------------
# WP-8 / SPEC §3.10 — licence gate
# ---------------------------------------------------------------------------

def load_manifest(path: Path) -> dict:
    """Read the provenance manifest. Absent is fine (first run) — everything is
    then simply unknown. Corrupt is not fine: it would silently downgrade every
    known `false` to `unknown` and let a refusal through."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        sys.exit(
            f"FATAL: {path} is not valid JSON ({exc}). Cannot verify image "
            "licences, so refusing to derive any cover."
        )
    if not isinstance(data, dict):
        sys.exit(f"FATAL: {path} must be a JSON object keyed by asset hash.")
    return data


def licence_for(manifest: dict, cover_path: str) -> tuple[bool | None, dict]:
    """(allows_derivatives, licence_record) for a /assets/cached/<hash>.<ext>
    reference. `None` means unknown — no entry, or an entry that has not been
    given a licence yet."""
    asset_hash = Path(cover_path).stem
    entry = manifest.get(asset_hash) or {}
    licence = entry.get("licence") or {}
    allows = licence.get("allows_derivatives")
    return (allows if isinstance(allows, bool) else None), licence


def describe_licence(licence: dict) -> str:
    code = licence.get("code") or "UNKNOWN"
    holder = licence.get("holder") or "UNKNOWN"
    url = licence.get("url")
    text = f"{code} (holder: {holder})"
    if url and url != "UNKNOWN":
        text += f" <{url}>"
    return text


def make_thumb(src_path: Path, out_path: Path, mode: str = "crop") -> None:
    """mode="crop": smart-crop to 3:2, then resize (creates a derivative).
    mode="contain": no crop — the whole frame is scaled to fit and letterboxed
    onto a 3:2 canvas. See --nd-fallback."""
    if mode == "contain":
        return make_thumb_contain(src_path, out_path)
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


def make_thumb_contain(src_path: Path, out_path: Path) -> None:
    """Non-cropping variant: proportional scale to fit, letterboxed onto the
    3:2 canvas the archive grid expects. Nothing is cut off.

    Honest caveat — this is NOT an automatic ND-compliance escape hatch. A pure
    proportional resize is defensible as a technical format change, but
    compositing the work onto a larger canvas of a different aspect ratio is
    itself an edit, and CC's NoDerivatives term is not settled on it. That is
    why the default remains a hard refusal and this path must be asked for
    per run with --nd-fallback contain.
    """
    with Image.open(src_path) as im:
        im = im.convert("RGB")
        sw, sh = im.size
        scale = min(THUMB_W / sw, THUMB_H / sh)
        new_size = (max(1, round(sw * scale)), max(1, round(sh * scale)))
        fitted = im.resize(new_size, Image.LANCZOS)
        canvas = Image.new("RGB", (THUMB_W, THUMB_H), (26, 26, 46))  # --ink
        canvas.paste(
            fitted,
            ((THUMB_W - new_size[0]) // 2, (THUMB_H - new_size[1]) // 2),
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(
            out_path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True
        )


def slug_for(html_path: Path) -> str:
    return html_path.stem  # filename without .html


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="HTML files (default: all /issues/*.html)")
    ap.add_argument("--force", action="store_true", help="Regenerate even if cover exists")
    ap.add_argument(
        "--manifest",
        default=str(MANIFEST_PATH),
        help="Provenance manifest to read licences from "
             "(default: assets/cached/manifest.json)",
    )
    ap.add_argument(
        "--strict-licence",
        action="store_true",
        help="Treat unknown/missing licence as a refusal, not a warning.",
    )
    ap.add_argument(
        "--nd-fallback",
        choices=("refuse", "contain"),
        default="refuse",
        help="What to do with a NoDerivatives source. 'refuse' (default) "
             "declines and exits non-zero. 'contain' letterboxes the whole "
             "frame instead of cropping — read make_thumb_contain() first, it "
             "is not an automatic ND-compliance guarantee.",
    )
    args = ap.parse_args()

    targets = (
        [Path(f).resolve() for f in args.files]
        if args.files
        else sorted(ISSUES_DIR.glob("*.html"))
    )

    manifest_path = Path(args.manifest).resolve()
    manifest = load_manifest(manifest_path)
    if not manifest:
        print(
            f"  · no provenance manifest at {manifest_path} — every licence is "
            "unknown. Run scripts/mirror-images.py --manifest-only to create it."
        )

    stats = {
        "made": 0,
        "skipped": 0,
        "no_cover": 0,
        "missing_src": 0,
        "frozen": 0,
        "refused": 0,
        "unknown_licence": 0,
    }
    refusals: list[str] = []

    for html_path in targets:
        slug = slug_for(html_path)
        out_path = COVERS_DIR / f"{slug}.jpg"

        if out_path.exists() and not args.force:
            stats["skipped"] += 1
            continue

        # SPEC §1 rule 3 — frozen issues keep the cover they shipped with.
        if slug in FROZEN_SLUGS and out_path.exists():
            stats["frozen"] += 1
            print(f"  = {slug}.jpg — frozen issue (SPEC §1 rule 3), left as published")
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

        # --- licence gate (SPEC §3.10) -----------------------------------
        allows_derivatives, licence = licence_for(manifest, cover_path)
        mode = "crop"

        if allows_derivatives is False:
            if args.nd_fallback == "contain":
                mode = "contain"
                print(
                    f"  ~ {slug}.jpg — {src.name} is NoDerivatives "
                    f"[{describe_licence(licence)}]; using the non-cropping "
                    "contain path because --nd-fallback contain was given."
                )
            else:
                stats["refused"] += 1
                message = (
                    f"REFUSED: {html_path.name} — will not crop/resize "
                    f"{src.name} ({cover_path}). Its licence forbids "
                    f"derivative works: {describe_licence(licence)}. "
                    "A cover thumbnail is a derivative. Use an image whose "
                    "licence allows derivatives, or re-run with "
                    "--nd-fallback contain after reading its caveat."
                )
                refusals.append(message)
                print(f"  ✗ {message}", file=sys.stderr)
                continue
        elif allows_derivatives is None:
            stats["unknown_licence"] += 1
            note = (
                f"{html_path.name} — no licence on record for {src.name} "
                f"({cover_path}); provenance unknown, cannot confirm that a "
                "derivative is permitted."
            )
            if args.strict_licence:
                stats["refused"] += 1
                message = f"REFUSED (--strict-licence): {note}"
                refusals.append(message)
                print(f"  ✗ {message}", file=sys.stderr)
                continue
            print(f"  ⚠ {note} Proceeding — pass --strict-licence to refuse.")

        try:
            make_thumb(src, out_path, mode=mode)
            stats["made"] += 1
            print(f"  ✓ {slug}.jpg ← {src.name}" + (" (contain)" if mode == "contain" else ""))
        except Exception as e:
            print(f"  ! {html_path.name} — thumbnail failed: {e}", file=sys.stderr)

    print(
        f"\nDone. Made: {stats['made']}, skipped: {stats['skipped']}, "
        f"frozen: {stats['frozen']}, no cover: {stats['no_cover']}, "
        f"missing src: {stats['missing_src']}, "
        f"unknown licence: {stats['unknown_licence']}, "
        f"refused: {stats['refused']}."
    )

    if refusals:
        print(
            f"\n{len(refusals)} cover(s) refused on licence grounds:", file=sys.stderr
        )
        for message in refusals:
            print(f"  - {message}", file=sys.stderr)
        sys.exit(EXIT_LICENCE_REFUSED)


if __name__ == "__main__":
    main()
