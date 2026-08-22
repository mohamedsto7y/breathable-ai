"""Simplified two-stroke wind mark, drawn for legibility at 16px."""
import math
from PIL import Image, ImageDraw

SS = 16  # supersample


def _round_polyline(draw, pts, w, fill):
    r = w / 2.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        draw.line([x0, y0, x1, y1], fill=fill, width=max(1, int(round(w))))
    for x, y in pts:
        draw.ellipse([x - r, y - r, x + r, y + r], fill=fill)


def _hook(cx, cy, r, steps=24):
    """Right half-circle, 12 o'clock -> 6 o'clock (screen coords, y down)."""
    return [
        (cx + r * math.sin(math.pi * i / steps), cy - r * math.cos(math.pi * i / steps))
        for i in range(steps + 1)
    ]


def mark_mask(size):
    """Alpha mask of the simplified mark, laid out on a 16-unit grid."""
    c = size * SS
    u = c / 16.0
    img = Image.new("L", (c, c), 0)
    d = ImageDraw.Draw(img)
    w = 1.8 * u

    top = [(3.4 * u, 5.8 * u), (9.8 * u, 5.8 * u)]
    top = _hook(9.8 * u, 4.1 * u, 1.7 * u)[::-1] + top[::-1]
    _round_polyline(d, top, w, 255)

    bot = [(3.4 * u, 10.2 * u), (8.4 * u, 10.2 * u)]
    bot = bot + _hook(8.4 * u, 11.9 * u, 1.7 * u)
    _round_polyline(d, bot, w, 255)

    return img
