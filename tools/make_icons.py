"""Regenerate Breathable AI icons from icons/source-glyph-512.png.

The source art is a black-on-transparent wind glyph, which disappears on
Chrome's dark toolbar. This composites it white on a teal rounded square and
renders each size from its own supersampled master, thickening the strokes at
small sizes so they survive the downsample.

Usage:  python tools/make_icons.py
"""
from pathlib import Path
from PIL import Image, ImageDraw

from _mark16 import mark_mask

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "icons" / "source-glyph-512.png"
OUT = ROOT / "icons"

TOP, BOTTOM = (36, 172, 128), (23, 133, 95)  # teal gradient
RADIUS = 0.22                                 # corner radius, fraction of size
SS = 8                                        # supersample factor

# The full three-stroke glyph cannot resolve at 16px, so that size uses a
# purpose-drawn two-stroke mark instead (see tools/_mark16.py).
# size -> glyph width as a fraction of the canvas
PLAN = {32: 0.82, 48: 0.78, 128: 0.74, 512: 0.74}


def rounded_gradient(size, radius):
    grad = Image.new("RGB", (1, size))
    for y in range(size):
        t = y / max(size - 1, 1)
        grad.putpixel((0, y), tuple(round(a + (b - a) * t) for a, b in zip(TOP, BOTTOM)))
    grad = grad.resize((size, size))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    tile.paste(grad, (0, 0), mask)
    return tile


def _glyph_mask(canvas, glyph_frac):
    mask = Image.open(SRC).convert("RGBA").split()[3]
    mask = mask.crop(mask.getbbox())
    gw = int(canvas * glyph_frac)
    gh = round(mask.height * gw / mask.width)
    mask = mask.resize((gw, gh), Image.LANCZOS)
    full = Image.new("L", (canvas, canvas), 0)
    full.paste(mask, ((canvas - gw) // 2, (canvas - gh) // 2))
    return full


def render(size, glyph_frac=None):
    if glyph_frac is None:               # 16px: simplified mark, its own scale
        mask = mark_mask(size)
        canvas = mask.width
    else:
        canvas = size * SS
        mask = _glyph_mask(canvas, glyph_frac)

    tile = rounded_gradient(canvas, int(canvas * RADIUS))
    glyph = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    glyph.paste((255, 255, 255, 255), (0, 0), mask)
    return Image.alpha_composite(tile, glyph).resize((size, size), Image.LANCZOS)


if __name__ == "__main__":
    for size, frac in [(16, None), *PLAN.items()]:
        path = OUT / f"icon{size}.png"
        render(size, frac).save(path, optimize=True)
        print(f"{path.name}: {size}x{size}  {path.stat().st_size} bytes")
