# Rain Falling

A drawing game for Rain. Everything you see on screen, she drew. One HTML file,
no install, no internet needed.

**Play it: https://shiangx.github.io/rain-falling/**

## The two games

**Catch** — things fall, you catch them. Score is how many you caught.

**Dodge** — things fall, you get out of the way. Score is how many seconds you
lasted. Getting hit sends you tumbling through a full spin and makes you safe
for a moment. It costs no lives, because the spin is the fun part.

Neither game can be lost.

## One player or two

The home screen toggles between them.

    Player 1    arrow keys, or drag with a finger
    Player 2    A and S

In two-player games each seat picks its own drawing and keeps its own score,
shown with a numbered badge over the character and a matching dot in the
corner. The two seats can never hold the same drawing, because you would not be
able to tell which one is yours; taking the other seat's pick swaps them.

A falling drawing that both players are touching goes to whichever one is
closer, not to whoever the code happens to check first.

In Dodge each player scores a point for every second they are flying clean, so
the better dodger wins rather than whoever simply stayed on screen longest.

## The drawings

Every drawing sits in one library and can take either job. Nothing is a player
by nature and nothing is a falling thing by nature, the two pick screens decide:

- **Who plays** — pick one to be, or one per seat in a two-player game.
- **What falls** — tick as many as you want dropping out of the sky.

Choices are remembered between visits. Current library:

    art/cat.png       the winged cat
    art/fish.png      the fish in the party hat
    art/cocoa.png     the Free Hot Coco For All sign
    art/jet.png       the jet

Originals are in `art/source/`.

## Adding a drawing

Fastest way, no tools: open **Who plays** or **What falls** and drop a photo
onto any square. That drawing's picture is replaced on the spot, the paper gets
cut away, and it lasts until the page reloads.

To keep it, add an entry to `ART` in `index.html`, then cut the sprite properly:

    /tmp/rfvenv/bin/python tools/cutout.py art/source/whatever.jpg art/whatever.png \
        --crop 1120 1940 1990 2690

`--crop` is a box in the original photo's pixels, which matters because these
pages usually hold several drawings. To find the numbers, lay a grid over the
photo and read them off:

    /tmp/rfvenv/bin/python tools/grid.py art/source/whatever.jpg /tmp/grid.png

`tools/build-art.sh` re-runs every cutout with the crops already worked out, so
edit that file rather than retyping commands.

The cutout keeps the largest connected blob of ink in the crop and drops the
rest, which is how the pencil oval around the cat and the "Hi" speech bubble
above the fish got left behind. Three knobs when it goes wrong:

- `--ink` (default 0.20) — lower catches fainter pencil, higher ignores a light
  background scribble. The fish needed 0.15, the cat needed 0.26.
- `--close` (default 9) — larger bridges bigger gaps in an outline, which keeps
  the inside of the drawing solid instead of see-through.
- `--erase X0 Y0 X1 Y1` — blank a box before the drawing is picked, for a
  neighbour sitting too close to crop away. Repeatable.

It needs numpy, Pillow and scipy, in a throwaway virtualenv:

    python3 -m venv /tmp/rfvenv && /tmp/rfvenv/bin/pip install pillow numpy scipy

## Changing the game

Everything is in `index.html`:

- `ART` — the drawing library. `fallScale` and `playScale` size a drawing
  against the others; a busy drawing with writing in it needs more room than a
  bold simple shape. Cocoa falls at 1.7.
- `SKIES` — the sky gradient per level.
- `SEATS` — the two seats: badge, colour, and which keys they answer to.
- `KEY_MAP` — which key moves which seat.
- `SPIN_TIME` and `SAFE_TIME` — how long the tumble lasts, and how long you
  can't be hit again after one. `KEY_SPEED` is screens per second while a key
  is held.
- `spawn()` — fall speed. `3.4 - (level-1)*0.22` is seconds from top to bottom.
- `update()` — the gap between drops, and how fast each mode levels up. Dodge
  ramps slower than catch on purpose.
- `catchItem()` and `hitItem()` — scoring, the cheers, and what a hit does.
