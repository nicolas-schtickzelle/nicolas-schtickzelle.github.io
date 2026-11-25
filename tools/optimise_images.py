#!/usr/bin/env python3
"""
Shrink assets/img in place so the site loads fast.

The download script pulls the ORIGINAL files from Wix, some of which are several
megabytes — far larger than any browser needs. This resizes anything wider than
MAX_W pixels and re-encodes JPEGs at quality 82.

    python tools/optimise_images.py --dry-run    # report only
    python tools/optimise_images.py              # do it

Originals are left untouched if you first copy assets/img somewhere safe, or you
can simply re-run tools/download_assets.py after deleting a file to get the
original back.
"""
import argparse
import os

from PIL import Image

MAX_W = 1600
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(HERE, "assets", "img")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    before = after = 0
    for name in sorted(os.listdir(IMG)):
        path = os.path.join(IMG, name)
        if name.lower().endswith(".gif") or not os.path.isfile(path):
            continue
        size = os.path.getsize(path)
        before += size
        try:
            im = Image.open(path)
        except Exception:  # noqa: BLE001
            after += size
            continue
        if im.width <= MAX_W and size < 400_000:
            after += size
            continue
        if args.dry_run:
            print(f"  would shrink {name}  {im.width}px  {size/1e6:.1f} MB")
            after += size
            continue
        if im.width > MAX_W:
            im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
        if path.lower().endswith((".jpg", ".jpeg")):
            im.convert("RGB").save(path, quality=82, optimize=True, progressive=True)
        else:
            im.save(path, optimize=True)
        after += os.path.getsize(path)

    print(f"before {before/1e6:.1f} MB  ->  after {after/1e6:.1f} MB")


if __name__ == "__main__":
    main()
