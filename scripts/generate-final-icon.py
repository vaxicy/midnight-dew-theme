# -*- coding: utf-8 -*-
"""Export the chosen Midnight Dew logo (candidate F - Ripple Dew) with a
transparent background, at the sizes the extension / store needs."""

import importlib.util
import os

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "scripts", "generate-icon-candidates.py")
OUT_DIR = os.path.join(ROOT, "store-assets", "icon")
SIZES = (1024, 512, 256, 128)


def load_candidate_module(path):
    spec = importlib.util.spec_from_file_location("icon_candidates", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def report(path, img):
    alpha = img.getchannel("A")
    px = alpha.load()
    w, h = img.size
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    hist = alpha.histogram()
    total = w * h
    transparent = hist[0] / total
    semi = sum(hist[1:255]) / total
    opaque = hist[255] / total
    print(
        f"{os.path.relpath(path, ROOT)} {w}x{h} corners={corners} "
        f"transparent={transparent:.1%} semi={semi:.1%} opaque={opaque:.1%}"
    )


def transparency_check(art):
    """Side-by-side check: checkerboard / dark / light background."""
    tile = 360
    pad = 24
    art512 = art.resize((300, 300), Image.LANCZOS)
    canvas = Image.new("RGB", (tile * 3 + pad * 4, tile + pad * 2), (18, 15, 20))

    checker = Image.new("RGB", (tile, tile), (255, 255, 255))
    dc = ImageDraw.Draw(checker)
    step = 30
    for j in range(0, tile, step):
        for i in range(0, tile, step):
            if (i // step + j // step) % 2:
                dc.rectangle([i, j, i + step - 1, j + step - 1], fill=(204, 204, 204))

    tiles = [
        checker,
        Image.new("RGB", (tile, tile), (26, 20, 28)),
        Image.new("RGB", (tile, tile), (248, 241, 250)),
    ]
    for i, board in enumerate(tiles):
        board.paste(art512, ((tile - 300) // 2, (tile - 300) // 2), art512)
        canvas.paste(board, (pad + i * (tile + pad), pad))
    path = os.path.join(OUT_DIR, "icon-transparency-check.png")
    canvas.save(path)
    print("saved", os.path.relpath(path, ROOT))


def main():
    module = load_candidate_module(SRC)
    art = module.candidate_ripple_dew()

    os.makedirs(OUT_DIR, exist_ok=True)
    for size in SIZES:
        img = art.resize((size, size), Image.LANCZOS)
        path = os.path.join(OUT_DIR, f"midnight-dew-icon-{size}.png")
        img.save(path)
        report(path, img)

    root_icon = os.path.join(ROOT, "icon.png")
    img = art.resize((128, 128), Image.LANCZOS)
    img.save(root_icon)
    report(root_icon, img)

    transparency_check(art)


if __name__ == "__main__":
    main()
