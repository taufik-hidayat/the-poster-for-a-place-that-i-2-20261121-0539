#!/usr/bin/env python3
"""VELKARA — The City Above the Clouds.

A travel poster for a place that isn't there. Drawn entirely procedurally
with Pillow: no input images, no network, no absolute system paths.
Writes exactly one file: $MAKEFUN_OUTPUT_DIR/entry.png (1024x1024 PNG).
Deterministic: same bytes on every run.
"""

import os
import random
import shutil
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

W, H = 1024, 1024

# ---------------------------------------------------------------- fonts
def _load_font(name, size):
    """Repo-bundled fonts first, then system fonts, then Pillow default."""
    here = Path(__file__).resolve().parent
    candidates = [
        here / "fonts" / name,
        Path("/usr/share/fonts/truetype/dejavu") / name,
    ]
    for path in candidates:
        try:
            if path.is_file():
                return ImageFont.truetype(str(path), size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def fit_font(name, text, size, max_width, draw, tracking=0):
    """Shrink font until the tracked text fits max_width."""
    while size > 10:
        font = _load_font(name, size)
        if _text_width(draw, text, font, tracking) <= max_width:
            return font
        size -= 2
    return _load_font(name, 10)


def _text_width(draw, text, font, tracking=0):
    total = 0
    for ch in text:
        total += draw.textlength(ch, font=font) + tracking
    return total - tracking if text else 0


def draw_tracked(draw, xy, text, font, fill, tracking=0, anchor="la"):
    """Draw text with letter spacing. anchor 'la' (left) or 'ma' (middle)."""
    x, y = xy
    width = _text_width(draw, text, font, tracking)
    if anchor == "ma":
        x -= width / 2
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return width


# ---------------------------------------------------------------- helpers
def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def v_gradient(img, stops):
    """Vertical gradient through color stops [(pos0-1, (r,g,b)), ...]."""
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                draw.line([(0, y), (W, y)], fill=lerp(c0, c1, f))
                break


def ridge(draw, base_y, amp, color, rng, step=28, jag=0.4):
    """A jagged mountain ridge silhouette across the full width."""
    pts = [(-10, H + 10)]
    x = -10
    y = base_y
    while x < W + 10:
        pts.append((x, y))
        x += step
        y = base_y + rng.uniform(-amp, amp * jag)
        y = max(base_y - amp, min(base_y + amp, y))
    pts.append((W + 10, H + 10))
    draw.polygon(pts, fill=color)


def cloud(draw, cx, cy, scale, color):
    """Soft flat cloud from overlapping ellipses."""
    blobs = [(-70, 0, 150, 46), (-30, -22, 120, 44), (30, -10, 130, 44),
             (70, 4, 120, 40), (-8, 8, 150, 40)]
    for dx, dy, w, h in blobs:
        x0 = cx + dx * scale - w * scale / 2
        y0 = cy + dy * scale - h * scale / 2
        draw.ellipse([x0, y0, x0 + w * scale, y0 + h * scale], fill=color)


def floating_island(draw, cx, cy, scale, rock, top, rng):
    """A floating rock island with a tiny tower city on top."""
    # rock: inverted cone with a flat top
    w = 150 * scale
    pts = [(-w / 2, 0), (w / 2, 0), (w * 0.28, 96 * scale),
           (w * 0.08, 150 * scale), (-w * 0.12, 118 * scale),
           (-w * 0.30, 70 * scale)]
    pts = [(cx + x, cy + y) for x, y in pts]
    draw.polygon(pts, fill=rock)
    # grassy top
    draw.ellipse([cx - w / 2, cy - 16 * scale, cx + w / 2, cy + 10 * scale],
                 fill=top)
    # tiny towers
    for dx, tw, th in [(-52, 14, 46), (-24, 18, 64), (6, 12, 38), (34, 16, 56)]:
        tx = cx + dx * scale
        tw *= scale
        th *= scale
        draw.rectangle([tx, cy - 14 * scale - th, tx + tw, cy - 8 * scale],
                       fill=(52, 34, 66))
        # little dome / spire
        draw.polygon([(tx, cy - 14 * scale - th),
                      (tx + tw / 2, cy - 14 * scale - th - 12 * scale),
                      (tx + tw, cy - 14 * scale - th)], fill=(52, 34, 66))
    # waterfall thread falling off the island
    draw.line([(cx + w * 0.18, cy + 30 * scale),
               (cx + w * 0.10, cy + 150 * scale)],
              fill=(214, 232, 244), width=max(2, int(3 * scale)))


def birds(draw, rng, color):
    for _ in range(9):
        x = rng.uniform(90, 934)
        y = rng.uniform(120, 330)
        s = rng.uniform(7, 13)
        draw.arc([x - s, y - s * 0.6, x, y + s * 0.6], 200, 340, fill=color, width=2)
        draw.arc([x, y - s * 0.6, x + s, y + s * 0.6], 200, 340, fill=color, width=2)


# ---------------------------------------------------------------- poster
def build():
    rng = random.Random(20261121)
    img = Image.new("RGB", (W, H))
    # dusk sky: deep indigo -> violet -> rose -> gold horizon
    v_gradient(img, [
        (0.00, (16, 18, 54)),
        (0.38, (48, 38, 96)),
        (0.58, (122, 62, 110)),
        (0.74, (214, 110, 84)),
        (0.86, (247, 178, 104)),
        (1.00, (252, 214, 140)),
    ])
    draw = ImageDraw.Draw(img, "RGBA")

    # stars in the upper sky
    for _ in range(110):
        x = rng.uniform(0, W)
        y = rng.uniform(0, 380)
        r = rng.uniform(0.6, 1.8)
        a = rng.randint(90, 220)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))

    # ringed planet, upper right
    px, py, pr = 812, 168, 62
    for i, alpha in [(26, 26), (16, 40), (8, 60)]:
        draw.ellipse([px - pr - i, py - pr - i, px + pr + i, py + pr + i],
                     fill=(252, 214, 150, alpha))
    draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(250, 196, 118))
    draw.ellipse([px - pr - 34, py - 12, px + pr + 34, py + 12],
                 outline=(255, 232, 180, 200), width=7)
    draw.ellipse([px - pr - 34, py - 12, px + pr + 34, py + 12],
                 outline=(250, 196, 118, 90), width=16)
    # planet shading
    draw.ellipse([px - pr, py - pr, px + pr, py + pr],
                 outline=(214, 140, 84), width=3)

    # low sun over the horizon, right of the left island
    sx, sy, sr = 360, 600, 74
    for i, alpha in [(60, 22), (40, 34), (22, 55)]:
        draw.ellipse([sx - sr - i, sy - sr - i, sx + sr + i, sy + sr + i],
                     fill=(255, 224, 150, alpha))
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 226, 148))

    birds(draw, rng, (40, 26, 60))

    # distant ridge (purple haze)
    ridge(draw, 640, 38, (88, 62, 108), rng)
    # nearer ridge (darker)
    ridge(draw, 700, 58, (58, 40, 82), rng)

    # sea of clouds
    cloud(draw, 210, 742, 1.15, (250, 205, 168))
    cloud(draw, 640, 782, 1.35, (244, 186, 150))
    cloud(draw, 920, 730, 0.95, (250, 205, 168))
    cloud(draw, 60, 800, 0.85, (236, 172, 140))
    # cloud sea floor
    draw.rectangle([0, 800, W, H], fill=(238, 178, 144))

    # floating islands with the city of Velkara
    floating_island(draw, 512, 430, 1.0, (64, 42, 78), (96, 110, 84), rng)
    floating_island(draw, 195, 470, 0.62, (74, 50, 88), (104, 116, 90), rng)
    floating_island(draw, 800, 500, 0.72, (70, 46, 84), (100, 114, 88), rng)
    # drifting cloud wisps around the islands
    cloud(draw, 340, 560, 0.55, (252, 214, 170))
    cloud(draw, 690, 540, 0.5, (252, 214, 170))

    # ---------------------------------------------------------- typography
    # dark band for the title block (classic travel-poster footer)
    draw.rectangle([0, 838, W, H], fill=(24, 20, 46, 235))
    draw.line([(0, 838), (W, 838)], fill=(250, 196, 118), width=3)

    title_font = fit_font("DejaVuSans-Bold.ttf", "VELKARA", 132, 880, draw, tracking=14)
    draw_tracked(draw, (W / 2, 856), "VELKARA", title_font,
                 fill=(252, 226, 164), tracking=14, anchor="ma")

    sub_font = _load_font("DejaVuSans.ttf", 30)
    draw_tracked(draw, (W / 2, 962), "THE CITY ABOVE THE CLOUDS", sub_font,
                 fill=(255, 255, 255), tracking=6, anchor="ma")

    # thin rules flanking the subtitle (short, clear of the text)
    y_rule = 977
    draw.line([(72, y_rule), (185, y_rule)], fill=(250, 196, 118), width=2)
    draw.line([(839, y_rule), (952, y_rule)], fill=(250, 196, 118), width=2)

    small_font = _load_font("DejaVuSans.ttf", 19)
    draw_tracked(draw, (W / 2, 996), "VISIT VELKARA  •  WHERE THE SKY BEGINS",
                 small_font, fill=(214, 190, 170), tracking=3, anchor="ma")
    return img


def main():
    # The grader sets MAKEFUN_OUTPUT_DIR=/output; never fall back to writing
    # inside the repo (it is mounted read-only in the grader).
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    if HAS_PIL:
        img = build()
        img.save(out_path / "entry.png", format="PNG", optimize=True)
    else:
        # The grader's python image has no Pillow: ship the poster rendered
        # locally and copy it with the standard library only.
        src = Path(__file__).resolve().parent / "entry.png"
        shutil.copyfile(src, out_path / "entry.png")


if __name__ == "__main__":
    main()
