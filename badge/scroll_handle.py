# scroll_handle.py  --  rainbow scrolling player handle for a WS2812 (NeoPixel) matrix
# MicroPython (ESP32-S3).  Scrolls the player's handle across the panel with an
# animated rainbow so every column cycles hue over time.
#
# Where the handle comes from: the badge web UI (/profile) saves it to NVS
# namespace "spellbook", key "handle". NAMESPACE and KEY below must match the
# firmware's NVS key exactly. If no handle is set, DEFAULT_TEXT is scrolled
# instead. (The firmware itself shows the Wi-Fi SSID in that case.)
#
# Font note: FONT only covers the glyphs the original text needed. Characters
# without a glyph render as blank columns.
#
# ---- CONFIGURE THESE FOUR THINGS FOR YOUR PANEL --------------------------------
DATA_PIN   = 17      # confirmed from firmware: "LED panel: GPIO17"
WIDTH      = 18      # confirmed: 18 columns
HEIGHT     = 7       # confirmed: 7 rows (perfect for the 5x7 font)
SERPENTINE = False   # unknown yet; flip to True if odd columns look upside-down
COL_MAJOR  = True    # confirmed: firmware says "column-major"
BRIGHT     = 0.20    # 0..1 master brightness (WS2812 are BLINDING at full)
SPEED_MS   = 55      # ms per scroll step (lower = faster)
# --------------------------------------------------------------------------------

import time

import esp32
import neopixel
from machine import Pin

# Must match the firmware's NVS write from the /profile page.
NVS_NAMESPACE = "spellbook"
NVS_KEY = "handle"
MAX_HANDLE = 24          # the firmware's /profile form caps the handle at 24 chars
NVS_BUF_BYTES = 64       # MicroPython has no blob size probe, so read into a bigger buffer
DEFAULT_TEXT = "APPRENTICE"

# 5x7 font, column-major: each glyph = 5 columns, each column a 7-bit value
# (bit0 = top row, bit6 = bottom row). Hand-built glyphs; see the font note above.
FONT = {
    'C': [0x3E,0x41,0x41,0x41,0x22],
    'M': [0x7F,0x02,0x0C,0x02,0x7F],
    'a': [0x20,0x54,0x54,0x54,0x78],
    'd': [0x38,0x44,0x44,0x48,0x7F],
    'e': [0x38,0x54,0x54,0x54,0x18],
    'f': [0x08,0x7E,0x09,0x01,0x02],
    'i': [0x00,0x44,0x7D,0x40,0x00],
    'o': [0x38,0x44,0x44,0x44,0x38],
    'x': [0x44,0x28,0x10,0x28,0x44],
    ' ': [0x00,0x00,0x00,0x00,0x00],
}

np = neopixel.NeoPixel(Pin(DATA_PIN), WIDTH * HEIGHT)

def _idx(x, y):
    """Map (x,y) -> LED index, honoring wiring layout."""
    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
        return -1
    if COL_MAJOR:
        col = x
        yy = (HEIGHT - 1 - y) if (SERPENTINE and (col & 1)) else y
        return col * HEIGHT + yy
    else:
        row = y
        xx = (WIDTH - 1 - x) if (SERPENTINE and (row & 1)) else x
        return row * WIDTH + xx

def _hsv(h, s, v):
    """h,s,v in 0..1 -> (r,g,b) 0..255."""
    i = int(h * 6) % 6
    f = h * 6 - int(h * 6)
    p, q, t = v*(1-s), v*(1-s*f), v*(1-s*(1-f))
    r, g, b = [(v,t,p),(q,v,p),(p,v,t),(p,q,v),(t,p,v),(v,p,q)][i]
    return (int(r*255), int(g*255), int(b*255))

def _render(cols, xoff, hue):
    """Draw the virtual glyph-column buffer `cols` at horizontal offset xoff."""
    for i in range(len(np)):
        np[i] = (0, 0, 0)
    ytop = (HEIGHT - 7) // 2  # vertically center the 7-row font
    for sx in range(WIDTH):
        src = sx + xoff
        if 0 <= src < len(cols):
            colbits = cols[src]
            if colbits:
                # per-column hue shift => moving rainbow
                r, g, b = _hsv(((hue + src * 0.03) % 1.0), 1.0, BRIGHT)
                for row in range(7):
                    if colbits & (1 << row):
                        j = _idx(sx, ytop + row)
                        if j >= 0:
                            np[j] = (r, g, b)
    np.write()

def _build_columns(text):
    cols = []
    for ch in text:
        glyph = FONT.get(ch, FONT.get(ch.lower(), FONT[' ']))
        cols.extend(glyph)
        cols.append(0x00)  # 1px gap between letters
    return cols

def read_handle():
    """Return the stored handle, or DEFAULT_TEXT if it is missing or empty.

    esp32.NVS.get_blob raises OSError when the key is absent or the buffer is too
    small, so both cases fall back to DEFAULT_TEXT. Only printable ASCII is kept,
    because the /profile form allows ASCII only.
    """
    try:
        nvs = esp32.NVS(NVS_NAMESPACE)
        buf = bytearray(NVS_BUF_BYTES)
        n = nvs.get_blob(NVS_KEY, buf)
    except OSError:
        return DEFAULT_TEXT
    raw = bytes(buf[:n]).rstrip(b"\x00")
    text = "".join(chr(b) for b in raw if 32 <= b < 127)[:MAX_HANDLE].strip()
    return text or DEFAULT_TEXT

def scroll(text=None, loops=0):
    """Scroll the handle (or `text` if given). loops=0 -> forever. Ctrl-C to stop."""
    cols = _build_columns(text if text is not None else read_handle())
    hue = 0.0
    n = 0
    try:
        while loops == 0 or n < loops:
            for xoff in range(-WIDTH, len(cols)):
                _render(cols, xoff, hue)
                hue = (hue + 0.01) % 1.0
                time.sleep_ms(SPEED_MS)
            n += 1
    except KeyboardInterrupt:
        for i in range(len(np)):
            np[i] = (0, 0, 0)
        np.write()

# ---- helpers to discover unknown hardware --------------------------------------
def find_pin(candidates=(48,38,39,40,41,42,45,46,47,21,18,17,16,8,9,10,7,6,5,4)):
    """Light a few LEDs on each candidate pin so you can see which one is the panel.
    Watch the badge; note the pin that makes LEDs turn on."""
    for g in candidates:
        try:
            t = neopixel.NeoPixel(Pin(g), 64)
            for i in range(64):
                t[i] = (0, 20, 0) if i < 8 else (0, 0, 0)
            t.write()
            print("pin", g, "-> pulsed green (look now)")
            time.sleep_ms(1200)
            for i in range(64):
                t[i] = (0, 0, 0)
            t.write()
        except Exception as e:  # noqa: BLE001 -- probing unknown pins, any failure is fine
            print("pin", g, "err", e)

def count_leds(pin=None, n=256):
    """Light LEDs 0..n-1 one color so you can count how many your panel has."""
    p = pin if pin is not None else DATA_PIN
    t = neopixel.NeoPixel(Pin(p), n)
    for i in range(n):
        t[i] = (8, 0, 8)
    t.write()
    print("lit", n, "LEDs on pin", p, "- count the ones that are ON")

if __name__ == "__main__":
    scroll(loops=6)
