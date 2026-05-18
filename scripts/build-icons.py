#!/usr/bin/env python3
"""
Generate PWA icons for The Signal.

Produces:
  assets/icons/icon-192.png         (192x192, app icon)
  assets/icons/icon-512.png         (512x512, app icon)
  assets/icons/icon-maskable.png    (512x512 with safe-area padding for Android adaptive icons)
  assets/icons/apple-touch-icon.png (180x180, iOS home screen)
  assets/icons/favicon-32.png       (32x32, browser tab)

Design: indigo background (#1A1A2E) with a serif "S" in coral-to-orange
gradient (#E94560 → #FF6B35) — mirrors the archive masthead.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
ICON_DIR = REPO_ROOT / "assets" / "icons"

BG = "#1A1A2E"
GRAD_TOP = (233, 69, 96)     # #E94560
GRAD_BOT = (255, 107, 53)    # #FF6B35
RING = (245, 236, 214, 200)  # cream-ish hint ring

SERIF_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def gradient_text_mask(text: str, size: int, font_size: int) -> Image.Image:
    """Render text in a vertical coral→orange gradient on a transparent layer."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    font = ImageFont.truetype(SERIF_FONT, font_size)

    # First render the text in white to get the alpha mask
    mask = Image.new("L", (size, size), 0)
    mdraw = ImageDraw.Draw(mask)
    bbox = mdraw.textbbox((0, 0), text, font=font, anchor="mm")
    cx, cy = size // 2, size // 2
    # Visually centre — serifs throw centroid slightly off, nudge up a touch
    mdraw.text((cx, cy - int(font_size * 0.04)), text, font=font, fill=255, anchor="mm")

    # Build the gradient
    grad = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grad)
    for y in range(size):
        t = y / max(1, size - 1)
        r = int(GRAD_TOP[0] + (GRAD_BOT[0] - GRAD_TOP[0]) * t)
        g = int(GRAD_TOP[1] + (GRAD_BOT[1] - GRAD_TOP[1]) * t)
        b = int(GRAD_TOP[2] + (GRAD_BOT[2] - GRAD_TOP[2]) * t)
        gdraw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    grad.putalpha(mask)
    img = Image.alpha_composite(img, grad)
    return img


def make_icon(size: int, *, maskable: bool = False, output: Path) -> None:
    """Compose background + ring + gradient S into a square icon."""
    img = Image.new("RGB", (size, size), BG)
    draw = ImageDraw.Draw(img)

    # Maskable safe area: keep all content inside the central 80%
    inset = int(size * 0.10) if maskable else int(size * 0.04)

    # Thin ring at the safe edge for a magazine-cover feel
    ring_inset = inset + int(size * 0.02)
    ring_width = max(1, size // 96)
    draw.rounded_rectangle(
        (ring_inset, ring_inset, size - ring_inset, size - ring_inset),
        radius=int(size * 0.06),
        outline=RING,
        width=ring_width,
    )

    # The "S"
    font_size = int(size * (0.55 if maskable else 0.66))
    s_layer = gradient_text_mask("S", size, font_size)
    img = Image.alpha_composite(img.convert("RGBA"), s_layer)
    img.convert("RGB").save(output, "PNG", optimize=True)


def main() -> None:
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    targets = [
        (192, ICON_DIR / "icon-192.png", False),
        (512, ICON_DIR / "icon-512.png", False),
        (512, ICON_DIR / "icon-maskable.png", True),
        (180, ICON_DIR / "apple-touch-icon.png", False),
        (32, ICON_DIR / "favicon-32.png", False),
    ]
    for size, path, maskable in targets:
        make_icon(size, maskable=maskable, output=path)
        print(f"  wrote {path.relative_to(REPO_ROOT)} ({size}x{size}{'  maskable' if maskable else ''})")


if __name__ == "__main__":
    main()
