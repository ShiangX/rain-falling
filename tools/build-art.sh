#!/bin/sh
# Rebuild the sprites from the original photos in art/source.
# Re-run this after re-cropping, or copy the pattern for a new drawing.
set -e
cd "$(dirname "$0")/.."
PY=${PY:-/tmp/rfvenv/bin/python}

$PY tools/cutout.py art/source/rain-cat.jpg art/rain.png \
    --crop 420 1400 2350 2990 --ink 0.26 --size 560

$PY tools/cutout.py art/source/fish.jpg art/item-1.png \
    --crop 1120 1940 1990 2690 --ink 0.15 --size 560

$PY tools/cutout.py art/source/cocoa.jpg art/item-2.png \
    --crop 600 1260 2120 2700 --ink 0.20 --close 7 --size 560 \
    --erase 600 1250 1150 1560 --erase 600 1560 725 2700
