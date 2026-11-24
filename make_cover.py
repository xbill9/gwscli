"""Textless cover: a terminal window linked through a key to nine service tiles.

Usage: python3 make_cover.py   -> devto-cover.<hash>.jpg (1376x578), builder-cover.<hash>.jpg (1200x675)
"""
import hashlib
import io
from pathlib import Path

from PIL import Image, ImageDraw

SURFACE = (26, 26, 25)
TILE_BG = (32, 32, 31)
PAPER = (44, 44, 42)
INK_2 = (195, 194, 183)
INK_3 = (128, 127, 120)
RULE = (58, 58, 55)
BLUE = (57, 135, 229)
ORANGE = (217, 89, 38)
S = 2  # draw at 2x, then downsample


def draw(w, h):
    W, H = w * S, h * S
    img = Image.new("RGB", (W, H), SURFACE)
    d = ImageDraw.Draw(img)
    cy = H // 2

    # terminal window
    tw, th = int(W * 0.30), int(H * 0.56)
    tx, ty = int(W * 0.08), cy - th // 2
    d.rounded_rectangle((tx, ty, tx + tw, ty + th), 22 * S, fill=TILE_BG, outline=RULE, width=3 * S)
    d.rounded_rectangle((tx, ty, tx + tw, ty + 46 * S), 22 * S, fill=PAPER)
    d.rectangle((tx, ty + 24 * S, tx + tw, ty + 46 * S), fill=PAPER)
    for i, c in enumerate((ORANGE, INK_3, BLUE)):
        x = tx + 30 * S + i * 30 * S
        d.ellipse((x - 8 * S, ty + 15 * S, x + 8 * S, ty + 31 * S), fill=c)
    # prompt chevron, command bar, cursor, output lines
    px, py = tx + 34 * S, ty + 90 * S
    d.line((px, py, px + 22 * S, py + 18 * S, px, py + 36 * S), fill=BLUE, width=7 * S, joint="curve")
    d.rounded_rectangle((px + 44 * S, py + 10 * S, px + 44 * S + int(tw * 0.48), py + 26 * S), 8 * S, fill=INK_2)
    cx = px + 60 * S + int(tw * 0.48)
    d.rectangle((cx, py, cx + 14 * S, py + 36 * S), fill=ORANGE)
    for i, frac in enumerate((0.70, 0.55, 0.62, 0.40)):
        y = py + 70 * S + i * 34 * S
        if y + 14 * S > ty + th - 20 * S:
            break
        d.rounded_rectangle((px, y, px + int((tw - 68 * S) * frac), y + 14 * S), 7 * S, fill=RULE)

    # nine service tiles in a 3x3 grid
    g = int(H * 0.17)
    gap = int(g * 0.32)
    gx0 = int(W * 0.62)
    gy0 = cy - (3 * g + 2 * gap) // 2
    colours = [BLUE, ORANGE, INK_3, ORANGE, BLUE, ORANGE, INK_3, BLUE, ORANGE]
    centres = []
    for r in range(3):
        for c in range(3):
            x, y = gx0 + c * (g + gap), gy0 + r * (g + gap)
            col = colours[r * 3 + c]
            d.rounded_rectangle((x, y, x + g, y + g), 16 * S, fill=TILE_BG, outline=col, width=4 * S)
            d.rounded_rectangle((x + g // 4, y + g // 4, x + 3 * g // 4, y + 3 * g // 4), 10 * S, fill=col)
            centres.append((x, y + g // 2))

    # key between them, with links fanning to the first column of tiles
    kx, ky = int(W * 0.47), cy
    for r in range(3):
        y = gy0 + r * (g + gap) + g // 2
        d.line((kx + 70 * S, ky, gx0 - 6 * S, y), fill=RULE, width=4 * S)
    d.line((tx + tw + 6 * S, cy, kx - 34 * S, cy), fill=RULE, width=4 * S)
    d.ellipse((kx - 34 * S, ky - 34 * S, kx + 34 * S, ky + 34 * S), outline=ORANGE, width=10 * S)
    d.ellipse((kx - 12 * S, ky - 12 * S, kx + 12 * S, ky + 12 * S), fill=SURFACE)
    d.rectangle((kx + 34 * S, ky - 6 * S, kx + 84 * S, ky + 6 * S), fill=ORANGE)
    d.rectangle((kx + 58 * S, ky + 6 * S, kx + 68 * S, ky + 22 * S), fill=ORANGE)
    d.rectangle((kx + 74 * S, ky + 6 * S, kx + 84 * S, ky + 18 * S), fill=ORANGE)

    return img.resize((w, h), Image.LANCZOS)


def save(img, stem):
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=90, optimize=True)
    data = buf.getvalue()
    name = f"{stem}.{hashlib.sha256(data).hexdigest()[:8]}.jpg"
    Path(name).write_bytes(data)
    print(f"wrote {name}  {img.size[0]}x{img.size[1]}  {len(data) // 1024} KB")


if __name__ == "__main__":
    save(draw(1376, 578), "devto-cover")
    save(draw(1200, 675), "builder-cover")
