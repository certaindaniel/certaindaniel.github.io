#!/usr/bin/env python3
"""Build web-sized TinyAquarium images from its original app screenshots."""
import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "tinyaquarium" / "assets"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("screenshots_root", type=Path, help="TinyAquarium/screenshots directory")
args = parser.parse_args()

screenshots = {
    "en-US": "en-US/02.png",
    "zh-Hant": "raw/zh-Hant/02_dex.png",
    "zh-Hans": "zh-Hans/02.png",
}
for locale, source in screenshots.items():
    with Image.open(args.screenshots_root / source) as image:
        image = image.convert("RGB")
        image.thumbnail((760, 1800), Image.Resampling.LANCZOS)
        image.save(ASSETS / f"screenshot_dex.{locale}.webp", "WEBP", quality=85, method=6)

with Image.open(ASSETS / "icon.png") as source:
    for size, name in [(48, "favicon.png"), (180, "apple-touch-icon.png")]:
        image = source.convert("RGBA")
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        image.save(ASSETS / name, "PNG", optimize=True)
