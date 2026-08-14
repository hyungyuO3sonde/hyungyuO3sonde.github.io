#!/usr/bin/env python3
"""Prepare photos in assets/img/ for the web.

For every image found:
  - applies the EXIF rotation, then strips all EXIF (including GPS location)
  - shrinks it so the long side is at most MAX_LONG_SIDE px
  - saves it as a lowercase .jpg (GitHub Pages URLs are case-sensitive)

Safe to run repeatedly: images that are already small and EXIF-free are skipped.
Originals are only removed once the new file has been written successfully.
"""

import os
import sys
from PIL import Image, ImageOps

IMG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "assets", "img")

# long side in pixels, per filename
MAX_LONG_SIDE = {
    "profile.jpg":   900,   # header portrait
    "marathon.jpg": 1800,   # full-width banner
}
DEFAULT_LONG_SIDE = 1200    # gallery thumbnails
QUALITY = 82

SOURCE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".tif", ".tiff", ".webp"}


def target_name(filename):
    return os.path.splitext(filename)[0].lower() + ".jpg"


def process(path):
    filename = os.path.basename(path)
    dst_name = target_name(filename)
    dst = os.path.join(IMG_DIR, dst_name)
    limit = MAX_LONG_SIDE.get(dst_name, DEFAULT_LONG_SIDE)

    try:
        im = Image.open(path)
    except Exception as exc:                       # not an image after all
        print(f"  skip  {filename}: cannot open ({exc})")
        return False

    has_exif = len(im.getexif()) > 0
    w, h = im.size
    renaming = filename != dst_name

    if not has_exif and max(w, h) <= limit and not renaming:
        print(f"  ok    {filename} ({w}x{h}) — already optimized")
        return False

    im = ImageOps.exif_transpose(im).convert("RGB")
    w, h = im.size
    scale = min(1.0, limit / max(w, h))
    if scale < 1.0:
        im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)

    before = os.path.getsize(path)
    tmp = os.path.join(IMG_DIR, ".__optimize_tmp.jpg")
    im.save(tmp, "JPEG", quality=QUALITY, optimize=True, progressive=True)

    # NOTE: macOS filesystems are case-insensitive, so "agu23.JPG" and "agu23.jpg"
    # are the same file. Remove the source BEFORE moving the temp file into place —
    # doing it the other way round deletes the freshly written result.
    os.remove(path)
    os.replace(tmp, dst)

    after = os.path.getsize(dst)
    arrow = f"{filename} -> {dst_name}" if renaming else dst_name
    print(f"  done  {arrow}  {w}x{h} -> {im.size[0]}x{im.size[1]}, "
          f"{before/1e6:.1f}MB -> {after/1e3:.0f}KB")
    return True


def main():
    if not os.path.isdir(IMG_DIR):
        sys.exit(f"no image folder at {IMG_DIR}")

    changed = 0
    for filename in sorted(os.listdir(IMG_DIR)):
        if filename.startswith(".") or filename == "README.md":
            continue
        if os.path.splitext(filename)[1].lower() not in SOURCE_EXTS:
            continue
        if process(os.path.join(IMG_DIR, filename)):
            changed += 1

    print(f"\n{changed} image(s) updated.")


if __name__ == "__main__":
    main()
