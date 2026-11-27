# snake_rainbow.py  --  rainbow snake crawling across a WS2812 (NeoPixel) matrix
# MicroPython (ESP32-S3).  A snake starts at START_LEN and moves one cell per tick.
# It wraps at the panel edges. A food cell is placed on a random free cell. When
# the head reaches it, the snake grows by one. When the board is full (or the
# snake has no legal move), it resets to START_LEN. Each segment has a hue offset,
# so the body looks like it cycles through the rainbow.
#
# ---- PANEL CONFIG (same as scroll_handle.py) ------------------------------------
DATA_PIN   = 17      # confirmed from firmware: "LED panel: GPIO17"
WIDTH      = 18      # confirmed: 18 columns
HEIGHT     = 7       # confirmed: 7 rows
SERPENTINE = False   # flip to True if odd columns look upside-down
COL_MAJOR  = True    # confirmed: firmware says "column-major"
BRIGHT     = 0.20    # 0..1 master brightness (WS2812 are BLINDING at full)
# ---- TUNABLES -------------------------------------------------------------------
SPEED_MS      = 80   # ms per tick (lower = faster)
START_LEN     = 3    # snake length at start and after a reset
TURN_PCT      = 20   # % chance per tick to turn instead of going straight
HUE_STEP      = 0.04 # hue offset between neighbouring segments
HUE_SPEED     = 0.01 # how far the whole rainbow shifts per tick
# --------------------------------------------------------------------------------

import time

import neopixel
import urandom
from machine import Pin

np = neopixel.NeoPixel(Pin(DATA_PIN), WIDTH * HEIGHT)

def _idx(x, y):
    """Map (x,y) -> LED index, honoring wiring layout."""
    if COL_MAJOR:
        yy = (HEIGHT - 1 - y) if (SERPENTINE and (x & 1)) else y
        return x * HEIGHT + yy
    xx = (WIDTH - 1 - x) if (SERPENTINE and (y & 1)) else x
    return y * WIDTH + xx

def _hsv(h, s, v):
    """h,s,v in 0..1 -> (r,g,b) 0..255."""
    i = int(h * 6) % 6
    f = h * 6 - int(h * 6)
    p, q, t = v*(1-s), v*(1-s*f), v*(1-s*(1-f))
    r, g, b = [(v,t,p),(q,v,p),(p,v,t),(p,q,v),(t,p,v),(v,p,q)][i]
    return (int(r*255), int(g*255), int(b*255))

def _wrap(x, y):
    # Wrap at the edges so the snake crawls off one side and re-enters the other.
    return (x % WIDTH, y % HEIGHT)

def _random_free(occupied):
    """Pick a random cell that the snake does not occupy, or None if the board is full."""
    free = [(x, y) for x in range(WIDTH) for y in range(HEIGHT) if (x, y) not in occupied]
    if not free:
        return None
    return free[urandom.randint(0, len(free) - 1)]

def _choose_move(body, dx, dy):
    """Return (next_cell, new_dx, new_dy) or None if no legal move exists."""
    hx, hy = body[0]
    # Block every body cell, including the tail. Entering a tail cell that is about
    # to vacate would be legal, but blocking it keeps the growth logic simple.
    blocked = set(body)
    straight = (dx, dy)
    back = (-dx, -dy)
    perp = [(dy, dx), (-dy, -dx)]
    if urandom.randint(1, 100) <= TURN_PCT:
        # Turn sideways with a random tie-break between the two perpendiculars.
        if urandom.randint(0, 1):
            perp.reverse()
        order = perp + [straight, back]
    else:
        order = [straight] + perp + [back]
    for ddx, ddy in order:
        nx, ny = _wrap(hx + ddx, hy + ddy)
        if (nx, ny) not in blocked:
            return (nx, ny), ddx, ddy
    return None

def _render(body, food, phase):
    for i in range(len(np)):
        np[i] = (0, 0, 0)
    if food is not None:
        # Food is a dim white dot so it reads differently from the rainbow body.
        np[_idx(food[0], food[1])] = _hsv(0.0, 0.0, BRIGHT * 0.5)
    for i, (x, y) in enumerate(body):
        r, g, b = _hsv((phase + i * HUE_STEP) % 1.0, 1.0, BRIGHT)
        np[_idx(x, y)] = (r, g, b)
    np.write()

def _reset():
    """Start a fresh snake near the centre heading right, with food placed on a free cell."""
    cx, cy = WIDTH // 2, HEIGHT // 2
    body = [(cx - i, cy) for i in range(START_LEN)]
    food = _random_free(set(body))
    return body, food, 1, 0

def run(frames=0):
    """Run the snake. frames=0 -> forever. Ctrl-C to stop."""
    body, food, dx, dy = _reset()
    phase = 0.0
    n = 0
    try:
        while frames == 0 or n < frames:
            move = _choose_move(body, dx, dy)
            if move is None:
                body, food, dx, dy = _reset()
            else:
                (nx, ny), dx, dy = move
                body.insert(0, (nx, ny))
                if (nx, ny) == food:
                    # Ate the food: keep the tail, so the snake grows by one.
                    food = _random_free(set(body))
                else:
                    body.pop()
                # Board full: the snake filled every cell, so there is no food spot left.
                if food is None:
                    body, food, dx, dy = _reset()
            _render(body, food, phase)
            phase = (phase + HUE_SPEED) % 1.0
            n += 1
            time.sleep_ms(SPEED_MS)
    except KeyboardInterrupt:
        for i in range(len(np)):
            np[i] = (0, 0, 0)
        np.write()

if __name__ == "__main__":
    run()
