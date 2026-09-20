#!/usr/bin/env python3
"""Lay a labelled pixel grid over a photo, to read off --crop numbers for cutout.py.

    grid.py photo.jpg out.png [--step 250]
"""
import argparse
from PIL import Image, ImageDraw, ImageOps

ap = argparse.ArgumentParser()
ap.add_argument('photo')
ap.add_argument('out')
ap.add_argument('--step', type=int, default=250, help='grid spacing in original pixels')
ap.add_argument('--size', type=int, default=760)
a = ap.parse_args()

im = ImageOps.exif_transpose(Image.open(a.photo)).convert('RGB')
W, H = im.size
k = a.size / max(W, H)
small = im.resize((round(W * k), round(H * k)))
d = ImageDraw.Draw(small)
for x in range(0, W, a.step):
    d.line([(x * k, 0), (x * k, small.height)], fill=(255, 0, 0))
    d.text((x * k + 2, 3), str(x), fill=(255, 0, 0))
for y in range(0, H, a.step):
    d.line([(0, y * k), (small.width, y * k)], fill=(0, 120, 255))
    d.text((2, y * k + 1), str(y), fill=(0, 80, 255))
small.save(a.out)
print(f'{a.out}  photo is {W}x{H}')
