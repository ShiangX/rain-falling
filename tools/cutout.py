#!/usr/bin/env python3
"""Turn a photo of a drawing on paper into a game sprite with a clear background.

    cutout.py photo.jpg out.png --crop X0 Y0 X1 Y1

Keeps the largest blob of ink in the crop, so other drawings on the same page
and stray lines from a neighbouring doodle get dropped. Fills the inside of that
blob so white paper within the outline stays white instead of going see-through.
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter, ImageOps
from scipy import ndimage


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('photo')
    ap.add_argument('out')
    ap.add_argument('--crop', nargs=4, type=int, metavar=('X0', 'Y0', 'X1', 'Y1'))
    ap.add_argument('--erase', nargs=4, type=int, action='append', default=[],
                    metavar=('X0', 'Y0', 'X1', 'Y1'),
                    help='blank a box before picking the drawing, in the same photo '
                         'pixels as --crop; repeatable, for a neighbour that overlaps')
    ap.add_argument('--size', type=int, default=560, help='max side of the finished sprite')
    ap.add_argument('--ink', type=float, default=0.20, help='0-1, lower catches fainter pencil')
    ap.add_argument('--close', type=int, default=9, help='radius that bridges gaps in an outline')
    ap.add_argument('--punch', type=float, default=1.45, help='contrast boost on the lines')
    ap.add_argument('--sat', type=float, default=1.5)
    ap.add_argument('--white', type=float, default=0.86, help='above this the paper goes flat white')
    args = ap.parse_args()

    img = ImageOps.exif_transpose(Image.open(args.photo)).convert('RGB')
    ox, oy = (args.crop[0], args.crop[1]) if args.crop else (0, 0)
    if args.crop:
        img = img.crop(tuple(args.crop))
    scale = min(1.0, args.size / max(img.size))
    if scale < 1.0:
        img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)

    rgb = np.asarray(img).astype(np.float32)
    lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
    chroma = rgb.max(2) - rgb.min(2)

    # estimate the lit paper behind every pixel, so a shadow across the page
    # isn't mistaken for pencil
    win = max(9, int(min(img.size) * 0.07)) | 1
    paper = ndimage.maximum_filter(lum, size=win)
    paper = ndimage.gaussian_filter(paper, sigma=win / 3.0)
    paper = np.maximum(paper, 40.0)
    darkness = np.clip((paper - lum) / (paper * 0.42), 0, 1)
    colour = np.clip((chroma - 12) / 45.0, 0, 1)
    ink = np.maximum(darkness, colour)

    for bx0, by0, bx1, by1 in args.erase:
        x0e, x1e = round((bx0 - ox) * scale), round((bx1 - ox) * scale)
        y0e, y1e = round((by0 - oy) * scale), round((by1 - oy) * scale)
        ink[max(0, y0e):max(0, y1e), max(0, x0e):max(0, x1e)] = 0.0

    # the drawing we want is the biggest connected run of ink in the crop
    binary = ink > args.ink
    labels, count = ndimage.label(binary, structure=np.ones((3, 3), int))
    if count == 0:
        raise SystemExit('no ink found; try a lower --ink')
    sizes = ndimage.sum(binary, labels, range(1, count + 1))
    shape = labels == (int(np.argmax(sizes)) + 1)

    shape = ndimage.binary_closing(shape, structure=disk(args.close))
    shape = ndimage.binary_fill_holes(shape)
    shape = ndimage.binary_opening(shape, structure=disk(2))

    ys, xs = np.nonzero(shape)
    if len(xs) == 0:
        raise SystemExit('nothing survived the cleanup; try a larger --close')
    pad = 6
    y0, y1 = max(0, ys.min() - pad), min(shape.shape[0], ys.max() + 1 + pad)
    x0, x1 = max(0, xs.min() - pad), min(shape.shape[1], xs.max() + 1 + pad)
    rgb, shape, paper = rgb[y0:y1, x0:x1], shape[y0:y1, x0:x1], paper[y0:y1, x0:x1]

    # lift the paper to white and push the pencil darker so it reads when small
    black = max(np.percentile(rgb, 1), 10.0)
    out = np.clip((rgb - black) / np.maximum(paper - black, 1.0)[..., None], 0, 1)
    out = np.clip(0.5 + (out - 0.5) * args.punch, 0, 1)
    grey = (out @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    out = np.clip(grey + (out - grey) * args.sat, 0, 1)

    # snap the near-white paper to flat white: it kills the photo speckle and
    # roughly halves the PNG, and the paper is meant to be white anyway
    plain = (out @ np.array([0.299, 0.587, 0.114], np.float32)) > args.white
    plain &= (out.max(2) - out.min(2)) < 0.07
    out[plain] = 1.0

    alpha = Image.fromarray((shape * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.1))
    sprite = Image.fromarray((out * 255).astype(np.uint8)).convert('RGBA')
    sprite.putalpha(alpha)
    sprite.save(args.out, optimize=True)
    print(f'{args.out}  {sprite.width}x{sprite.height}  ink pixels {int(shape.sum())}')


if __name__ == '__main__':
    main()
