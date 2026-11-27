# badge_display.py -- multi-mode RGB display for the Shattered Shard badge
# Panel (from firmware): GPIO17, 18x7, column-major, 126 pixels.
# Button: BOOT (GPIO0) cycles modes. Deploy as main.py to run on boot.

import random
import time

import neopixel
from machine import Pin

# ----------------- panel config (confirmed from firmware) -----------------
DATA_PIN = 17
W, H     = 18, 7
N        = W * H
COL_MAJOR = True     # firmware: "column-major"
SERP      = False    # confirmed: text read correctly with no zig-zag
BRIGHT    = 0.20     # 0..1  (20% -- comfortable and easy on the battery)
BTN_PIN   = 0        # BOOT button (the non-EN one)

np  = neopixel.NeoPixel(Pin(DATA_PIN), N)
btn = Pin(BTN_PIN, Pin.IN, Pin.PULL_UP)

# ----------------- framebuffer helpers -----------------
def _i(x, y):
    if x < 0 or x >= W or y < 0 or y >= H:
        return -1
    if COL_MAJOR:
        yy = (H - 1 - y) if (SERP and (x & 1)) else y
        return x * H + yy
    xx = (W - 1 - x) if (SERP and (y & 1)) else x
    return y * W + xx

def clear():
    for i in range(N):
        np[i] = (0, 0, 0)

def px(x, y, c):
    j = _i(x, y)
    if j >= 0:
        np[j] = (int(c[0] * BRIGHT), int(c[1] * BRIGHT), int(c[2] * BRIGHT))

def show():
    np.write()

def hsv(h, s, v):
    h = h % 1.0
    i = int(h * 6); f = h * 6 - i
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    r, g, b = [(v, t, p), (q, v, p), (p, v, t),
               (p, q, v), (t, p, v), (v, p, q)][i % 6]
    return (int(r * 255), int(g * 255), int(b * 255))

# ----------------- 5x7 font (classic glcd, column-major, bit0=top) -----------------
FONT = {
 ' ':[0,0,0,0,0],
 'A':[0x7E,0x11,0x11,0x11,0x7E],'B':[0x7F,0x49,0x49,0x49,0x36],'C':[0x3E,0x41,0x41,0x41,0x22],
 'D':[0x7F,0x41,0x41,0x22,0x1C],'E':[0x7F,0x49,0x49,0x49,0x41],'F':[0x7F,0x09,0x09,0x09,0x01],
 'G':[0x3E,0x41,0x49,0x49,0x7A],'H':[0x7F,0x08,0x08,0x08,0x7F],'I':[0x00,0x41,0x7F,0x41,0x00],
 'J':[0x20,0x40,0x41,0x3F,0x01],'K':[0x7F,0x08,0x14,0x22,0x41],'L':[0x7F,0x40,0x40,0x40,0x40],
 'M':[0x7F,0x02,0x0C,0x02,0x7F],'N':[0x7F,0x04,0x08,0x10,0x7F],'O':[0x3E,0x41,0x41,0x41,0x3E],
 'P':[0x7F,0x09,0x09,0x09,0x06],'Q':[0x3E,0x41,0x51,0x21,0x5E],'R':[0x7F,0x09,0x19,0x29,0x46],
 'S':[0x46,0x49,0x49,0x49,0x31],'T':[0x01,0x01,0x7F,0x01,0x01],'U':[0x3F,0x40,0x40,0x40,0x3F],
 'V':[0x1F,0x20,0x40,0x20,0x1F],'W':[0x7F,0x20,0x18,0x20,0x7F],'X':[0x63,0x14,0x08,0x14,0x63],
 'Y':[0x03,0x04,0x78,0x04,0x03],'Z':[0x61,0x51,0x49,0x45,0x43],
 '0':[0x3E,0x51,0x49,0x45,0x3E],'1':[0x00,0x42,0x7F,0x40,0x00],'2':[0x42,0x61,0x51,0x49,0x46],
 '3':[0x21,0x41,0x45,0x4B,0x31],'4':[0x18,0x14,0x12,0x7F,0x10],'5':[0x27,0x45,0x45,0x45,0x39],
 '6':[0x3C,0x4A,0x49,0x49,0x30],'7':[0x01,0x71,0x09,0x05,0x03],'8':[0x36,0x49,0x49,0x49,0x36],
 '9':[0x06,0x49,0x49,0x29,0x1E],'!':[0x00,0x00,0x5F,0x00,0x00],'.':[0x00,0x60,0x60,0x00,0x00],
 'a':[0x20,0x54,0x54,0x54,0x78],'c':[0x38,0x44,0x44,0x44,0x20],'d':[0x38,0x44,0x44,0x48,0x7F],
 'e':[0x38,0x54,0x54,0x54,0x18],'f':[0x08,0x7E,0x09,0x01,0x02],'i':[0x00,0x44,0x7D,0x40,0x00],
 'o':[0x38,0x44,0x44,0x44,0x38],'x':[0x44,0x28,0x10,0x28,0x44],
 'b':[0x7F,0x48,0x44,0x44,0x38],'h':[0x7F,0x08,0x04,0x04,0x78],'l':[0x00,0x41,0x7F,0x40,0x00],
 'n':[0x7C,0x08,0x04,0x04,0x78],'r':[0x7C,0x08,0x04,0x04,0x08],'w':[0x3C,0x40,0x30,0x40,0x3C],
 'y':[0x0C,0x50,0x50,0x50,0x3C],'k':[0x7F,0x10,0x28,0x44,0x00],
 # arrow glyphs for the konami code
 '^':[0x04,0x02,0x7F,0x02,0x04],'v':[0x10,0x20,0x7F,0x20,0x10],
 '<':[0x08,0x1C,0x2A,0x08,0x08],'>':[0x08,0x08,0x2A,0x1C,0x08],
}

def text_cols(s):
    cols = []
    for ch in s:
        g = FONT.get(ch) or FONT.get(ch.lower()) or FONT.get(ch.upper()) or FONT[' ']
        cols += g + [0]          # 1px gap
    return cols

# ----------------- button (debounced, edge-triggered) -----------------
_last = 1
_last_t = 0
def pressed():
    """True once per physical press (falling edge, 200ms debounce)."""
    global _last, _last_t
    v = btn.value()
    now = time.ticks_ms()
    hit = False
    if _last == 1 and v == 0 and time.ticks_diff(now, _last_t) > 200:
        hit = True; _last_t = now
    _last = v
    return hit

# ----------------- MODES (generators; yield frame delay in ms) -----------------
def m_scroll(text="CodexMafia", speed=55):
    cols = text_cols(text)
    hue = 0.0
    while True:
        for xoff in range(-W, len(cols)):
            clear()
            for sx in range(W):
                src = sx + xoff
                if 0 <= src < len(cols) and cols[src]:
                    col = hsv((hue + src * 0.03) % 1.0, 1.0, 1.0)
                    for row in range(7):
                        if cols[src] & (1 << row):
                            px(sx, row, col)
            hue = (hue + 0.012) % 1.0
            yield speed

def m_konami(speed=70):
    seq = "^^vv<><>BA"
    cols = text_cols(seq)
    while True:
        # scroll the sequence in cyan/magenta
        for xoff in range(-W, len(cols)):
            clear()
            for sx in range(W):
                src = sx + xoff
                if 0 <= src < len(cols) and cols[src]:
                    c = (0, 255, 180) if src < 8 * 6 else (255, 60, 255)
                    for row in range(7):
                        if cols[src] & (1 << row):
                            px(sx, row, c)
            yield speed
        # payoff: rainbow flash burst
        for f in range(24):
            for x in range(W):
                for y in range(H):
                    px(x, y, hsv((x + y) / 20.0 + f / 12.0, 1.0, 1.0))
            yield 45

def m_snake():
    while True:
        snake = [(W // 2, H // 2)]
        food = (random.randint(0, W - 1), random.randint(0, H - 1))
        alive = True
        hue0 = 0.0
        while alive:
            hx, hy = snake[0]
            # greedy AI: choose a safe move that reduces distance to food
            best = None; bestd = 1e9
            for nd in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = hx + nd[0], hy + nd[1]
                if nx < 0 or nx >= W or ny < 0 or ny >= H: continue
                if (nx, ny) in snake[:-1]: continue
                dist = abs(nx - food[0]) + abs(ny - food[1])
                if dist < bestd:
                    bestd = dist; best = nd; bhead = (nx, ny)
            if best is None:            # trapped -> die
                for _ in range(6):
                    for i, (x, y) in enumerate(snake):
                        px(x, y, (120, 0, 0))
                    yield 90; clear(); yield 90
                alive = False; continue
            nh = bhead
            snake.insert(0, nh)
            if nh == food:
                food = (random.randint(0, W - 1), random.randint(0, H - 1))
                while food in snake:
                    food = (random.randint(0, W - 1), random.randint(0, H - 1))
            else:
                snake.pop()
            clear()
            px(food[0], food[1], (255, 0, 0))
            for i, (x, y) in enumerate(snake):
                if i == 0:
                    px(x, y, (255, 255, 255))          # bright white head
                else:
                    px(x, y, hsv(hue0 + i / 9.0, 1.0, 1.0))  # rainbow tail
            hue0 = (hue0 + 0.04) % 1.0
            yield 120

def m_matrix():
    drops = [random.randint(-H, 0) for _ in range(W)]
    spd = [random.choice((1, 1, 2)) for _ in range(W)]
    trail = [[0] * H for _ in range(W)]
    while True:
        clear()
        for x in range(W):
            drops[x] += spd[x]
            if drops[x] > H + 4:
                drops[x] = random.randint(-H, -1); spd[x] = random.choice((1, 1, 2))
            for y in range(H):
                if y == drops[x]:
                    trail[x][y] = 255
                px(x, y, (0, trail[x][y], 0))
                if trail[x][y] > 0:
                    trail[x][y] = max(0, trail[x][y] - 60)
            hy = drops[x]
            if 0 <= hy < H:
                px(x, hy, (180, 255, 180))
        yield 70

def m_plasma():
    import math
    t = 0.0
    while True:
        clear()
        for x in range(W):
            for y in range(H):
                v = (math.sin(x / 2.0 + t) + math.sin(y / 1.5 + t) +
                     math.sin((x + y) / 2.0 + t)) / 3.0
                px(x, y, hsv((v + 1) / 2.0, 1.0, 1.0))
        t += 0.15
        yield 45

MODES = [
    ("w00k", lambda: m_scroll("w00k")),
    ("Konami",     m_konami),
    ("Snake",      m_snake),
    ("Matrix",     m_matrix),
    ("Plasma",     m_plasma),
]

def run():
    mi = 0
    gen = MODES[mi][1]()
    print("mode:", MODES[mi][0], "(press BOOT to cycle)")
    while True:
        delay = next(gen)
        show()
        # poll button across the frame delay so switching feels instant
        end = time.ticks_add(time.ticks_ms(), delay)
        while time.ticks_diff(end, time.ticks_ms()) > 0:
            if pressed():
                mi = (mi + 1) % len(MODES)
                gen = MODES[mi][1]()
                print("mode:", MODES[mi][0])
                break
            time.sleep_ms(5)

if __name__ == "__main__":
    run()
