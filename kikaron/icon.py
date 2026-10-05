#!/usr/bin/env python3
"""Kikaron Multipass icon tooling (Pillow).

  icon.py concept-a OUT.png
      Render the placeholder "Concept A" icon at 1024x1024, opaque: a dark
      navy square (iOS rounds the corners), a white ring with a dot in the
      centre and four small circles around it - orange top, blue right,
      brown bottom, pale left.

  icon.py derive ICON.png
      From a 1024x1024 icon, write every image asset the app needs (see
      TARGETS below): the opaque app icons, the monochrome share-sheet icon
      and the template wordmark logos. Deterministic for a given input,
      Pillow version and system font.
"""
import json
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAVY = (0x1F, 0x24, 0x33)
WHITE = (255, 255, 255)
DOTS = [  # (dx, dy, colour)
    (0, -1, (0xFF, 0x7A, 0x2F)),  # top: orange
    (1, 0, (0x38, 0xB6, 0xFF)),   # right: blue
    (0, 1, (0x8A, 0x6A, 0x45)),   # bottom: brown
    (-1, 0, (0xCF, 0xE9, 0xF5)),  # left: pale
]
PRODUCT_NAME = os.environ.get("PRODUCT_NAME", "Multipass")


def concept_a(out):
    ss = 4  # supersample for smooth edges
    n = 1024 * ss
    im = Image.new("RGB", (n, n), NAVY)
    d = ImageDraw.Draw(im)
    c = n / 2

    def disc(cx, cy, r, fill):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)

    ring_r, ring_w = 235 * ss, 58 * ss
    disc(c, c, ring_r, WHITE)
    disc(c, c, ring_r - ring_w, NAVY)
    disc(c, c, 78 * ss, WHITE)
    orbit, small = 345 * ss, 60 * ss
    for dx, dy, col in DOTS:
        disc(c + dx * orbit, c + dy * orbit, small, col)
    im = im.resize((1024, 1024), Image.Resampling.LANCZOS)
    im.save(out, "PNG", optimize=False)


def load_icon(path):
    im = Image.open(path)
    if im.size != (1024, 1024):
        sys.exit(f"icon must be 1024x1024, got {im.size}")
    return im.convert("RGB")  # App Store icons must be opaque: drop alpha


def glyph_mask(icon):
    """Alpha mask of everything that differs from the icon's background
    (sampled at the corners), so any flat-background icon yields a glyph."""
    bg = icon.getpixel((4, 4))
    diff = ImageChops.difference(icon, Image.new("RGB", icon.size, bg)).convert("L")
    return diff.point(lambda v: 255 if v > 40 else int(v * 255 / 40))


def solid(mask, colour=(0, 0, 0)):
    out = Image.new("RGBA", mask.size, colour + (0,))
    out.putalpha(mask)
    return out


def font(px):
    path = "/System/Library/Fonts/Avenir Next.ttc"
    for i in range(16):
        try:
            f = ImageFont.truetype(path, px, index=i)
        except OSError:
            break
        if f.getname()[1] in ("Demi Bold", "DemiBold"):
            return f
    return ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", px, index=1)


def wordmark(mask, w3=846, h3=132):
    """A template logo the size of upstream's (282x44 pt): glyph + name."""
    ss = 2
    W, H = w3 * ss, h3 * ss
    canvas = Image.new("L", (W, H), 0)
    bbox = mask.getbbox() or (0, 0, 1024, 1024)
    g = mask.crop(bbox)
    gh = H
    g = g.resize((round(g.width * gh / g.height), gh), Image.Resampling.LANCZOS)
    canvas.paste(g, (0, 0))
    f = font(int(H * 0.72))
    d = ImageDraw.Draw(canvas)
    tb = d.textbbox((0, 0), PRODUCT_NAME, font=f)
    x = g.width + int(H * 0.28)
    y = (H - (tb[3] - tb[1])) // 2 - tb[1]
    d.text((x, y), PRODUCT_NAME, font=f, fill=255)
    used = canvas.getbbox()
    if used and used[2] > W:
        canvas = canvas.crop((0, 0, used[2], H))
    canvas = canvas.resize((w3, h3), Image.Resampling.LANCZOS)
    return solid(canvas)


def save(im, rel):
    path = os.path.join(ROOT, rel)
    im.save(path, "PNG", optimize=False)


def write_appiconset(rel_dir, filename, image):
    full = os.path.join(ROOT, rel_dir)
    for f in os.listdir(full):
        if f.endswith(".png"):
            os.remove(os.path.join(full, f))
    save(image, os.path.join(rel_dir, filename))
    contents = {
        "images": [{"filename": filename, "idiom": "universal", "platform": "ios", "size": "1024x1024"}],
        "info": {"author": "xcode", "version": 1},
    }
    with open(os.path.join(full, "Contents.json"), "w") as fh:
        json.dump(contents, fh, indent=2)
        fh.write("\n")


APP_ICONSETS = [
    "Bitwarden/Application/Support/Assets.xcassets/AppIcon.appiconset",
    "Bitwarden/Application/Support/Assets.xcassets/AppIcon-Beta.appiconset",
    "Bitwarden/Application/Support/Assets.xcassets/AppIcon-Dev.appiconset",
]
MONO_ICONSETS = [
    "BitwardenActionExtension/Application/Support/Assets.xcassets/AppIcon.appiconset",
    "BitwardenActionExtension/Application/Support/Assets.xcassets/AppIcon-Beta.appiconset",
    "BitwardenActionExtension/Application/Support/Assets.xcassets/AppIcon-Dev.appiconset",
]
LOGO_IMAGESETS = [
    "Bitwarden/Application/Support/Assets.xcassets/logoBitwarden.imageset",
    "BitwardenShared/UI/Platform/Application/Support/Images.xcassets/logo.imageset",
]


def derive(icon_path):
    icon = load_icon(icon_path)
    for d in APP_ICONSETS:
        write_appiconset(d, "Icon-1024.png", icon)
    mask = glyph_mask(icon)
    mono = solid(mask)
    for d in MONO_ICONSETS:
        if os.path.isdir(os.path.join(ROOT, d)):
            write_appiconset(d, "AppIcon-Monochrome.png", mono)
    logo3 = wordmark(mask)
    for d in LOGO_IMAGESETS:
        save(logo3, os.path.join(d, "logo@3x.png"))
        save(logo3.resize((564, 88), Image.Resampling.LANCZOS), os.path.join(d, "logo@2x.png"))
        save(logo3.resize((282, 44), Image.Resampling.LANCZOS), os.path.join(d, "logo.png"))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "concept-a":
        concept_a(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "derive":
        derive(sys.argv[2])
    else:
        sys.exit(__doc__)
