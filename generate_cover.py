from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 2560, 1280
CORNER_RADIUS = 80
TITLE_TEXT = "antigravity-swarm"
SUBTITLE_TEXT = "ASW workflows for Antigravity CLI."
OUT_PATH = Path(__file__).with_name("cover.png")


def make_blob(size: tuple[int, int], color_rgba: tuple[int, int, int, int], cx: int, cy: int, rx: int, ry: int) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=color_rgba)
    return layer


def load_fonts() -> tuple[ImageFont.FreeTypeFont, ImageFont.FreeTypeFont]:
    try:
        return (
            ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 176, index=1),
            ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 54, index=0),
        )
    except Exception:
        return (
            ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New Bold.ttf", 176),
            ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New Bold.ttf", 54),
        )


def draw_text_layer(text: str, x: int, y: int, font: ImageFont.FreeTypeFont, color: tuple[int, int, int, int]) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((x, y), text, font=font, fill=color)
    return layer


def generate() -> Image.Image:
    base = Image.new("RGBA", (W, H), (13, 10, 10, 255))
    blobs = [
        (139, 0, 0, 200, 690, 610, 720, 500, 120),
        (204, 0, 0, 150, 1900, 210, 620, 420, 110),
        (26, 10, 46, 190, 1280, 1160, 920, 360, 90),
        (155, 18, 25, 115, 1420, 650, 540, 360, 80),
        (18, 64, 78, 70, 2150, 900, 520, 330, 90),
    ]

    canvas = base.copy()
    for r, g, b, a, cx, cy, rx, ry, blur in blobs:
        blob = make_blob((W, H), (r, g, b, a), cx, cy, rx, ry)
        canvas = Image.alpha_composite(canvas, blob.filter(ImageFilter.GaussianBlur(radius=blur)))

    canvas = canvas.filter(ImageFilter.GaussianBlur(radius=8))

    rng = np.random.default_rng(42)
    noise = rng.integers(0, 255, (H, W), dtype=np.uint8)
    grain_alpha = (noise * 0.22).astype(np.uint8)
    grain_layer = np.stack([noise, noise, noise, grain_alpha], axis=-1).astype(np.uint8)
    canvas = Image.alpha_composite(canvas, Image.fromarray(grain_layer, "RGBA"))

    font_title, font_subtitle = load_fonts()
    measure = ImageDraw.Draw(Image.new("RGBA", (W, H), (0, 0, 0, 0)))
    title_box = measure.textbbox((0, 0), TITLE_TEXT, font=font_title)
    subtitle_box = measure.textbbox((0, 0), SUBTITLE_TEXT, font=font_subtitle)
    title_w = title_box[2] - title_box[0]
    title_h = title_box[3] - title_box[1]
    subtitle_w = subtitle_box[2] - subtitle_box[0]
    subtitle_h = subtitle_box[3] - subtitle_box[1]

    gap = 48
    block_top = (H - (title_h + gap + subtitle_h)) // 2 - 30
    title_x = int((W - title_w) // 2 - title_box[0])
    title_y = int(block_top - title_box[1])
    subtitle_x = int((W - subtitle_w) // 2 - subtitle_box[0])
    subtitle_y = int(title_y + title_h + gap)

    for color, blur in [
        ((255, 80, 80, 60), 18),
        ((255, 120, 120, 90), 9),
        ((255, 180, 180, 120), 4),
    ]:
        glow = draw_text_layer(TITLE_TEXT, title_x, title_y, font_title, color)
        canvas = Image.alpha_composite(canvas, glow.filter(ImageFilter.GaussianBlur(radius=blur)))

    canvas = Image.alpha_composite(canvas, draw_text_layer(TITLE_TEXT, title_x, title_y, font_title, (255, 255, 255, 245)))
    canvas = Image.alpha_composite(
        canvas,
        draw_text_layer(SUBTITLE_TEXT, subtitle_x, subtitle_y, font_subtitle, (192, 160, 160, 210)),
    )

    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (W - 1, H - 1)], radius=CORNER_RADIUS, fill=255)
    canvas.putalpha(mask)
    return canvas.filter(ImageFilter.GaussianBlur(radius=1))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Print cover metadata without rewriting the file.")
    args = parser.parse_args()

    if args.check:
        print(f"{TITLE_TEXT} {W}x{H} -> {OUT_PATH}")
        return

    canvas = generate()
    canvas.save(OUT_PATH, "PNG", dpi=(400, 400))
    print(f"Saved: {OUT_PATH}")
    print(f"Title: {TITLE_TEXT}")
    print(f"Size: {W}x{H}")
    print(f"Mode: {canvas.mode}")


if __name__ == "__main__":
    main()
