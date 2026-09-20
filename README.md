# Rain Falling

A catching game for Rain, starring her drawings. One HTML file, no install,
no internet needed.

**Play it: https://shiangx.github.io/rain-falling/**

## Play it

Open the link above on any phone, tablet or laptop, or double-click
`index.html` to run it offline. Press Play. Move the winged cat with your finger
or the mouse and catch the fish. There is no way to lose. Every 10 catches bumps
the level: fish fall faster and the sky changes color.

## The art

Rain drew both of them. The originals are in `art/source/`, the cut-out sprites
the game loads are:

    art/rain.png      the winged cat, the player
    art/item-1.png    the fish in the party hat, the thing that falls

Slots `item-2.png` through `item-5.png` are empty. Only slots that have a real
drawing ever fall, so the game drops fish and nothing else until more are added.

## Adding a drawing

Fastest way, no tools: press **Use our drawings** on the start screen and drop a
photo onto a square. The paper gets cut away on the spot. That lasts until the
page reloads, which is fine for showing her.

To keep it, cut the sprite properly and save it into `art/`:

    /tmp/rfvenv/bin/python tools/cutout.py art/source/whatever.jpg art/item-2.png \
        --crop 1120 1940 1990 2690

`--crop` is a box in the original photo's pixels, which matters because these
pages have several drawings on them. To find the numbers, lay a grid over the
photo and read them off:

    /tmp/rfvenv/bin/python tools/grid.py art/source/whatever.jpg /tmp/grid.png

`tools/build-art.sh` re-runs every cutout with the crops already worked out, so
edit that file rather than retyping the commands.

The cutout keeps the largest connected blob of ink in the crop and drops the
rest, which is how the pencil oval around the cat and the "Hi" speech bubble
above the fish got left behind. Two knobs when it goes wrong:

- `--ink` (default 0.20) — lower catches fainter pencil, higher ignores a light
  background scribble. The fish needed 0.15, the cat needed 0.26.
- `--close` (default 9) — larger bridges bigger gaps in an outline, which keeps
  the inside of the drawing solid instead of see-through.

It needs numpy, Pillow and scipy. They live in a throwaway virtualenv:

    python3 -m venv /tmp/rfvenv && /tmp/rfvenv/bin/pip install pillow numpy scipy

## Changing the game

Everything is in `index.html`. The parts worth touching:

- `SLOTS` — the art slots and their emoji stand-ins. Add rows for more things to catch.
- `SKIES` — the sky gradient per level.
- `spawn()` — fall speed. `3.4 - (level-1)*0.22` is seconds from top to bottom.
- `update()` — `Math.max(0.42, 1.1 - level*0.07)` is the gap between drops in seconds.
- `catchItem()` — scoring, the level-up threshold, and the cheer messages.
