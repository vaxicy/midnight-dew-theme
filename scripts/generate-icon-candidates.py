# -*- coding: utf-8 -*-
"""Generate new logo/icon candidates (F-J) for the Midnight Dew VS Code theme.

Pure PIL drawing: shapes are rendered at 2048px and downsampled to 512 / 128.
Palette comes from the theme files (light + dark variants).
"""

import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFont

SS = 2048
SIZES = (512, 128)
DROP_RATIO = 1.78  # apex height / radius
DROP_SHOULDER = -18.0  # tangent point, degrees above the circle equator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "store-assets", "icon-candidates")

VIOLET_LIGHT = (183, 156, 240)
VIOLET = (155, 125, 221)
VIOLET_DEEP = (125, 85, 211)
VIOLET_DARK = (106, 68, 190)
NIGHT = (26, 20, 28)
DAWN = (248, 241, 250)

CANDIDATES = [
    ("candidate-f-ripple-dew", "F \u00b7 Ripple Dew"),
    ("candidate-g-facet-dew", "G \u00b7 Facet Dew"),
    ("candidate-h-dual-split", "H \u00b7 Dual Split"),
    ("candidate-i-star-trail", "I \u00b7 Star Trail"),
    ("candidate-j-pixel-dew", "J \u00b7 Pixel Dew"),
]


# ---------------------------------------------------------------- helpers


def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(round(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def quad(p0, p1, p2, t):
    u = 1.0 - t
    return (
        u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
        u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
    )


def drop_points(cx, cy, r, h_ratio=DROP_RATIO, shoulder_deg=DROP_SHOULDER, steps=140):
    """Teardrop: round bottom, tapering smoothly to a point on top."""
    sh = math.radians(shoulder_deg)
    height = r * h_ratio
    apex = (cx, cy - height)
    right = (cx + r * math.cos(sh), cy + r * math.sin(sh))
    left = (cx - r * math.cos(sh), cy + r * math.sin(sh))

    pts = []
    a0, a1 = sh, math.pi - sh
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * i / steps
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))

    # continue along the circle tangent so the shoulder stays smooth
    k = 0.55 * math.dist(left, apex)
    tan_l = (-math.sin(math.pi - sh), math.cos(math.pi - sh))
    ctrl_l = (left[0] + tan_l[0] * k, left[1] + tan_l[1] * k)
    for i in range(1, steps + 1):
        pts.append(quad(left, ctrl_l, apex, i / steps))

    tan_r = (math.sin(sh), -math.cos(sh))
    ctrl_r = (right[0] + tan_r[0] * k, right[1] + tan_r[1] * k)
    for i in range(1, steps + 1):
        pts.append(quad(apex, ctrl_r, right, i / steps))
    return pts


def vgrad(size, top, bottom, y0, y1):
    """Vertical gradient image, transparent outside [y0, y1]."""
    h = max(2, int(round(y1 - y0)))
    strip = Image.new("RGB", (4, 160))
    px = strip.load()
    for j in range(160):
        col = mix(top, bottom, j / 159.0)
        for i in range(4):
            px[i, j] = col
    strip = strip.resize((size, h), Image.LANCZOS)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    img.paste(strip, (0, int(round(y0))))
    return img


def clipped(layer, mask):
    out = layer.copy()
    out.putalpha(ImageChops.multiply(out.getchannel("A"), mask))
    return out


def band(size, y0, y1):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rectangle([0, max(0, int(y0)), size, int(y1)], fill=255)
    return m


def drop_mask(cx, cy, r, h_ratio=DROP_RATIO, shoulder_deg=DROP_SHOULDER):
    mask = Image.new("L", (SS, SS), 0)
    ImageDraw.Draw(mask).polygon(drop_points(cx, cy, r, h_ratio, shoulder_deg), fill=255)
    return mask


def four_point_star(draw, cx, cy, s, fill):
    k = s * 0.2
    draw.polygon(
        [
            (cx, cy - s),
            (cx + k, cy - k),
            (cx + s, cy),
            (cx + k, cy + k),
            (cx, cy + s),
            (cx - k, cy + k),
            (cx - s, cy),
            (cx - k, cy - k),
        ],
        fill=fill,
    )


def add_drop(base, cx, cy, r, top, bottom, highlight=True, h_ratio=DROP_RATIO):
    mask = drop_mask(cx, cy, r, h_ratio)
    grad = vgrad(SS, top, bottom, cy - r * h_ratio, cy + r)
    base.alpha_composite(clipped(grad, mask))
    if highlight:
        hl = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
        hx, hy = cx - r * 0.36, cy - r * 0.34
        rr = r * 0.25
        ImageDraw.Draw(hl).ellipse(
            [hx - rr, hy - rr * 1.3, hx + rr, hy + rr * 1.3], fill=(255, 255, 255, 95)
        )
        base.alpha_composite(clipped(hl, mask))


def empty():
    return Image.new("RGBA", (SS, SS), (0, 0, 0, 0))


# ------------------------------------------------------------- candidates


def candidate_ripple_dew():
    """Droplet above spreading water ripples."""
    img = empty()
    cx, cy, r = 1024, 1030, 295

    ring = empty()
    d = ImageDraw.Draw(ring)
    origin_y = cy + r
    for rad, width, alpha in ((375, 36, 185), (525, 26, 122)):
        d.arc(
            [cx - rad, origin_y - rad, cx + rad, origin_y + rad],
            start=8,
            end=172,
            fill=VIOLET + (alpha,),
            width=width,
        )
    img.alpha_composite(ring)

    add_drop(img, cx, cy, r, VIOLET_LIGHT, VIOLET_DEEP)
    return img


def candidate_facet_dew():
    """Geometric faceted crystal droplet."""
    cx, cy, r = 1024, 1120, 330
    height = r * DROP_RATIO
    sh = math.radians(DROP_SHOULDER)
    apex = (cx, cy - height)
    left = (cx - r * math.cos(sh), cy + r * math.sin(sh))
    right = (cx + r * math.cos(sh), cy + r * math.sin(sh))
    bottom = (cx, cy + r)

    mask = drop_mask(cx, cy, r)
    img = empty()
    img.alpha_composite(clipped(Image.new("RGBA", (SS, SS), VIOLET_DEEP + (255,)), mask))

    facets = empty()
    d = ImageDraw.Draw(facets)
    d.polygon([apex, left, bottom], fill=(201, 181, 249, 255))
    d.polygon([apex, right, bottom], fill=(99, 62, 184, 255))
    d.polygon([apex, left, (cx - r * 0.42, cy + r * 0.02)], fill=(232, 223, 255, 140))
    blade = [
        (cx, cy - height * 0.86),
        (cx + r * 0.11, cy - height * 0.46),
        (cx + r * 0.05, cy + r * 0.30),
        (cx - r * 0.05, cy + r * 0.30),
        (cx - r * 0.11, cy - height * 0.46),
    ]
    d.polygon(blade, fill=(238, 231, 255, 210))
    img.alpha_composite(clipped(facets, mask))
    return img


def candidate_dual_split():
    """Droplet split in two: dark midnight on top, bright dew below."""
    cx, cy, r = 1024, 1120, 330
    height = r * DROP_RATIO
    apex_y = cy - height
    split = apex_y + (height + r) / 2.0
    mask = drop_mask(cx, cy, r)

    img = empty()
    upper = vgrad(SS, (94, 70, 138), (46, 33, 74), apex_y, split)
    lower = vgrad(SS, VIOLET_LIGHT, VIOLET_DEEP, split, cy + r)
    img.alpha_composite(clipped(upper, ImageChops.multiply(mask, band(SS, 0, split))))
    img.alpha_composite(clipped(lower, ImageChops.multiply(mask, band(SS, split, SS))))

    seam = empty()
    ImageDraw.Draw(seam).rectangle(
        [cx - r - 12, split - 7, cx + r + 12, split + 7], fill=(246, 243, 255, 238)
    )
    img.alpha_composite(clipped(seam, mask))

    decor = empty()
    d = ImageDraw.Draw(decor)
    four_point_star(d, cx - r * 0.40, split - height * 0.30, 60, (255, 255, 255, 226))
    four_point_star(d, cx + r * 0.34, split - height * 0.10, 33, (255, 255, 255, 172))
    d.ellipse(
        [cx + r * 0.44 - 28, split + r * 0.50 - 28, cx + r * 0.44 + 28, split + r * 0.50 + 28],
        fill=(62, 45, 92, 240),
    )
    img.alpha_composite(clipped(decor, mask))
    return img


def candidate_star_trail():
    """Droplet with a constellation trail above it."""
    img = empty()
    cx, cy, r = 1024, 1340, 300

    trail = empty()
    d = ImageDraw.Draw(trail)
    stars = [(500, 720), (690, 585), (890, 650), (1070, 495), (1300, 570)]
    for a, b in zip(stars, stars[1:]):
        d.line([a, b], fill=VIOLET + (130,), width=10)
    for i, (sx, sy) in enumerate(stars):
        size = (44, 33, 37, 48, 33)[i]
        four_point_star(d, sx, sy, size * 1.24, VIOLET_DEEP + (255,))
        four_point_star(d, sx, sy, size, (255, 255, 255, 238))
    img.alpha_composite(trail)

    add_drop(img, cx, cy, r, VIOLET_LIGHT, VIOLET_DEEP)
    return img


def candidate_pixel_dew():
    """Droplet built from a pixel grid."""
    n = 20
    cell = 90
    margin = (SS - n * cell) // 2
    cx, cy, r = 1024, 1100, 420
    ratio = 1.45
    height = r * ratio
    mask = drop_mask(cx, cy, r, ratio)
    px = mask.load()
    y_top = cy - height

    img = empty()
    d = ImageDraw.Draw(img)
    gap = 5
    for j in range(n):
        for i in range(n):
            x0 = margin + i * cell
            y0 = margin + j * cell
            sx = int(x0 + cell / 2)
            sy = int(y0 + cell / 2)
            if not (0 <= sx < SS and 0 <= sy < SS) or px[sx, sy] <= 128:
                continue
            col = mix((202, 184, 249), (117, 77, 202), (sy - y_top) / (height + r))
            d.rectangle(
                [x0 + gap, y0 + gap, x0 + cell - gap, y0 + cell - gap], fill=col + (255,)
            )
    return img


GENERATORS = {
    "candidate-f-ripple-dew": candidate_ripple_dew,
    "candidate-g-facet-dew": candidate_facet_dew,
    "candidate-h-dual-split": candidate_dual_split,
    "candidate-i-star-trail": candidate_star_trail,
    "candidate-j-pixel-dew": candidate_pixel_dew,
}


# ------------------------------------------------------------- rendering


def load_font(size):
    for name in ("msyh.ttc", "segoeui.ttf", "arial.ttf"):
        path = os.path.join("C:\\Windows\\Fonts", name)
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def build_preview(icons, labels):
    font = load_font(46)
    title_font = load_font(56)
    small_font = load_font(30)
    cell_w, cell_h = 640, 980
    pad = 44
    cols = len(icons)
    width = cols * cell_w + pad * 2
    top = pad + 96
    height = top + 2 * cell_h + pad * 2

    canvas = Image.new("RGB", (width, height), (11, 9, 13))
    dc = ImageDraw.Draw(canvas)
    dc.text(
        (pad, pad + 30),
        "Midnight Dew - new icon candidates",
        font=title_font,
        fill=(236, 231, 240),
    )

    for row, bg in enumerate((NIGHT, DAWN)):
        for i, icon in enumerate(icons):
            x = pad + i * cell_w
            y = top + row * (cell_h + pad)
            tile = Image.new("RGB", (cell_w, cell_h), bg)
            art = icon.resize((512, 512), Image.LANCZOS)
            tile.paste(art, ((cell_w - 512) // 2, 46), art)
            dt = ImageDraw.Draw(tile)
            fg = (245, 243, 246) if row == 0 else (43, 37, 45)
            dt.text((cell_w // 2, 660), labels[i], font=font, fill=fg, anchor="mm")

            small = icon.resize((128, 128), Image.LANCZOS)
            tinier = icon.resize((64, 64), Image.LANCZOS)
            base_y = 740
            dt.text(
                (cell_w // 2 - 150, base_y + 168), "128 px", font=small_font, fill=fg, anchor="mm"
            )
            dt.text(
                (cell_w // 2 + 120, base_y + 168), "64 px", font=small_font, fill=fg, anchor="mm"
            )
            tile.paste(small, (cell_w // 2 - 150 - 64, base_y), small)
            tile.paste(tinier, (cell_w // 2 + 120 - 32, base_y + 32), tinier)
            canvas.paste(tile, (x, y))
    return canvas


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    icons = []
    labels = []
    for stem, label in CANDIDATES:
        art = GENERATORS[stem]()
        icons.append(art)
        labels.append(label)
        for size in SIZES:
            out = art.resize((size, size), Image.LANCZOS)
            suffix = "" if size == 512 else "-128"
            path = os.path.join(OUT_DIR, f"{stem}{suffix}.png")
            out.save(path)
            print("saved", path)
    preview = build_preview(icons, labels)
    preview_path = os.path.join(OUT_DIR, "preview-f-j.png")
    preview.save(preview_path)
    print("saved", preview_path, preview.size)


if __name__ == "__main__":
    main()
