"""Regenerate the owned raster fixtures; requires Pillow (not a test dependency).

Run this script explicitly when changing fixtures. Normal tests consume the
versioned images and require no Pillow installation. The SVG is authored directly.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUTPUT = Path(__file__).parent / "images"
SIZE = (640, 260)
COLORS = ("#4051b5", "#009688", "#ff9800", "#9c27b0")


def canvas(title: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", SIZE, "#f0f4f8")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=22)
    draw.text((24, 16), title, fill="#172b4d", font=font)
    return image, draw


def generate() -> None:
    OUTPUT.mkdir(exist_ok=True)
    image, draw = canvas("PNG: build stages")
    for index, label in enumerate(("Source", "XML", "Markdown", "HTML")):
        left = 24 + index * 152
        draw.rounded_rectangle((left, 80, left + 138, 168), radius=12, fill=COLORS[index])
        draw.text((left + 12, 112), label, fill="white", font=ImageFont.load_default(size=18))
    image.save(OUTPUT / "stages.png", optimize=False)

    image, draw = canvas("JPEG: illustrative signal")
    points = [(x, 150 - int(55 * math.sin(x / 43))) for x in range(24, 616)]
    draw.line(points, fill=COLORS[0], width=5)
    image.save(OUTPUT / "signal.jpg", quality=90)

    image, draw = canvas("JPEG extension: illustrative bars")
    for index in range(8):
        x = 26 + index * 74
        height = 30 + (index * 31) % 130
        draw.rectangle((x, 220 - height, x + 48, 220), fill=COLORS[index % 4])
    image.save(OUTPUT / "bars.jpeg", quality=90)

    frames = []
    for active in range(4):
        image, draw = canvas("GIF: animated build progress")
        for index in range(4):
            x = 24 + index * 152
            draw.rounded_rectangle(
                (x, 90, x + 138, 170), radius=12, fill=COLORS[index] if index <= active else "#cfd8e3"
            )
            draw.text((x + 52, 114), str(index + 1), fill="white", font=ImageFont.load_default(size=24))
        frames.append(image)
    frames[0].save(OUTPUT / "progress.gif", save_all=True, append_images=frames[1:], duration=650, loop=0)

    image, draw = canvas("BMP: pixel grid")
    for y in range(7):
        for x in range(20):
            color = COLORS[(x // 3 + y // 2) % 4]
            draw.rectangle((24 + x * 29, 68 + y * 23, 50 + x * 29, 88 + y * 23), fill=color)
    image.save(OUTPUT / "pixels.bmp")

    image, draw = canvas("WebP: illustrative heatmap")
    for y in range(6):
        for x in range(18):
            value = (x * 13 + y * 29) % 200
            color = (40 + value // 4, 100 + value // 2, 220 - value // 3)
            draw.rounded_rectangle((24 + x * 33, 68 + y * 27, 54 + x * 33, 92 + y * 27), radius=3, fill=color)
    image.save(OUTPUT / "coverage.webp", lossless=True)


if __name__ == "__main__":
    generate()
