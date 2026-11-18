#!/usr/bin/env python3
"""news-image-20261117 entry: draws a one-page newspaper front page summing
up the world news of Tuesday 17 November 2026 and writes it to entry.png.

Pure Python 3 standard library (os, struct, zlib, math). No network, no
randomness, no clock: the same input always produces the same bytes. The
image is drawn pixel by pixel with a small built-in 5x7 bitmap font, then
encoded as PNG.
Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   (or writes /output/entry.png)
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette ---
PAPER = (246, 242, 232)
INK = (22, 30, 48)
NAVY = (26, 44, 78)
NAVY2 = (48, 72, 118)
RED = (176, 36, 28)
RED2 = (212, 88, 78)
SKY = (184, 212, 228)
SKY2 = (138, 178, 204)
SEA = (44, 108, 140)
SEA2 = (26, 80, 108)
GREY = (98, 106, 118)
GREY2 = (60, 66, 78)
SMOKE = (122, 124, 128)
SMOKE2 = (160, 162, 165)
SUN = (232, 176, 72)
GREEN = (44, 122, 68)
GREEN2 = (118, 188, 128)
GOLD = (198, 160, 38)
WHITE = (255, 255, 255)
CREAM = (236, 229, 212)
ORANGE = (212, 108, 42)
TEAL = (30, 138, 128)
FAINT = (118, 116, 110)

# ------------------------------------------------------------- 5x7 font -----
# Each glyph: 7 rows of 5 pixels, '#' = on. Text is uppercased before
# drawing; characters not in the table draw as a blank.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}

# ------------------------------------------------------------------ canvas --
buf = bytearray(W * H * 3)


def _set(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = c


def rect(x, y, w, h, c):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            buf[i], buf[i + 1], buf[i + 2] = c


def hline(x, y, w, c, t=1):
    rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    rect(x, y, t, h, c)


def seg(x0, y0, x1, y1, c, t=1):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        for a in range(t):
            for b in range(t):
                _set(x0 + a, y0 + b, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def disc(cx, cy, r, c, filled=True):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = (xx - cx) ** 2 + (yy - cy) ** 2
            if filled:
                if d <= r * r:
                    _set(xx, yy, c)
            elif r * r - 2 * r <= d <= r * r:
                _set(xx, yy, c)


def arc(cx, cy, r, a0, a1, c, t=2):
    # Angles in degrees, 0 = east, going clockwise (screen coords, y down).
    steps = max(8, int(abs(a1 - a0) * r / 12))
    for s in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * s / steps)
        x = int(round(cx + r * math.cos(a)))
        y = int(round(cy + r * math.sin(a)))
        for dx in range(t):
            for dy in range(t):
                _set(x + dx, y + dy, c)


def poly(points, c):
    # Filled polygon via scanline fill.
    ys = [p[1] for p in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                _set(x, y, c)


# -------------------------------------------------------------------- text --
def _cw(scale):
    return 5 * scale + scale  # glyph width + 1 unit gap


def text_w(s, scale):
    s = s.upper()
    if not s:
        return 0
    return len(s) * _cw(scale) - scale


def draw_text(x, y, s, scale, color):
    s = s.upper()
    cx = x
    for ch in s:
        g = FONT.get(ch)
        if g:
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == '1':
                        rect(cx + col * scale, y + r * scale, scale, scale, color)
        cx += _cw(scale)
    return cx


def draw_center(x, y, w, s, scale, color):
    draw_text(x + (w - text_w(s, scale)) // 2, y, s, scale, color)


def wrap(s, scale, max_w):
    """Greedy word wrap; returns a list of lines."""
    words = s.upper().split(' ')
    lines, cur = [], ''
    for word in words:
        cand = word if not cur else cur + ' ' + word
        if text_w(cand, scale) <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, s, scale, color, max_w, gap=4):
    lines = wrap(s, scale, max_w)
    yy = y
    for ln in lines:
        draw_text(x, yy, ln, scale, color)
        yy += 7 * scale + gap
    return yy


# ----------------------------------------------------------------- scenes --
def scene_bridge(x, y, w, h):
    """Lead illustration: the Kerch bridge to Crimea, its road arch broken
    and dropped into the strait, smoke rising from the gap."""
    rect(x, y, w, h, SKY)
    disc(x + w - 64, y + 40, 24, SUN)
    disc(x + w - 64, y + 40, 17, (240, 198, 110))
    # far shore
    rect(x, y + h - 104, w, 12, (118, 148, 138))
    # sea
    rect(x, y + h - 92, w, 92, SEA)
    rect(x, y + h - 92, w, 4, SEA2)
    for wy in (y + h - 68, y + h - 44, y + h - 20):
        for wx in range(x + 10, x + w - 10, 44):
            hline(wx, wy, 24, SEA2, 2)
    deck = y + h - 146
    # two standing spans, one gap in the middle
    rect(x + 8, deck, 148, 13, GREY2)
    rect(x + w - 156, deck, 148, 13, GREY2)
    # pylons
    rect(x + 32, deck - 58, 9, 58, GREY2)
    rect(x + w - 41, deck - 58, 9, 58, GREY2)
    # arch stubs curving down into the gap
    arc(x + 156, deck + 13, 58, 200, 340, GREY, 5)
    arc(x + w - 156, deck + 13, 58, 200, 340, GREY, 5)
    # collapsed span: a slab sliding down into the water
    poly([(x + 164, deck + 1), (x + 192, deck + 1),
          (x + 222, deck + 76), (x + 194, deck + 76)], GREY2)
    poly([(x + 164, deck + 1), (x + 172, deck + 13),
          (x + 202, deck + 76), (x + 194, deck + 76)], GREY)
    # legs standing in the water
    vline(x + 58, deck + 13, 64, GREY2, 6)
    vline(x + w - 64, deck + 13, 64, GREY2, 6)
    # smoke over the gap, rising clear of the arch stubs
    disc(x + w // 2 - 16, deck - 34, 15, SMOKE)
    disc(x + w // 2 + 10, deck - 50, 19, SMOKE2)
    disc(x + w // 2 + 32, deck - 26, 11, SMOKE)
    disc(x + w // 2 - 36, deck - 56, 11, SMOKE2)


def scene_radar(x, y, w, h):
    """Gulf story: a radar dish sweeping while drones are shot down above."""
    cx, cy = x + w // 2, y + h // 2 + 10
    # intercepted drones as small crosses in the sky
    for dx, dy in ((-56, -30), (46, -36), (6, -42)):
        seg(cx + dx - 7, cy + dy, cx + dx + 7, cy + dy, INK, 2)
        seg(cx + dx, cy + dy - 7, cx + dx, cy + dy + 7, INK, 2)
    # dish
    arc(cx, cy - 4, 30, 180, 360, NAVY, 4)
    hline(cx - 30, cy - 4, 60, NAVY, 4)
    seg(cx, cy - 4, cx + 24, cy - 26, RED, 3)
    # mast and base
    vline(cx, cy - 4, 26, NAVY, 6)
    poly([(cx - 24, cy + 22), (cx + 24, cy + 22), (cx + 7, cy + 2),
          (cx - 7, cy + 2)], NAVY)
    hline(x + 14, cy + 22, w - 28, NAVY, 3)


def scene_summit(x, y, w, h):
    """Asia summit: three flag poles for China, the US and Russia."""
    base = y + h - 22
    # (flag colours, label) left to right: China, United States, Russia
    flags = [
        ('CN', RED, 'china'),
        ('US', NAVY, 'usa'),
        ('RU', WHITE, 'russia'),
    ]
    step = (w - 36) // 3
    for i, (label, col, kind) in enumerate(flags):
        px = x + 22 + i * step
        vline(px, y + 16, base - y - 16, INK, 3)
        fx, fy, fw, fh = px + 3, y + 16, 32, 20
        if kind == 'china':
            rect(fx, fy, fw, fh, RED)
            disc(fx + 9, fy + 10, 3, GOLD)
            _set(fx + 20, fy + 5, GOLD)
            _set(fx + 24, fy + 9, GOLD)
            _set(fx + 24, fy + 13, GOLD)
            _set(fx + 20, fy + 16, GOLD)
        elif kind == 'usa':
            for s in range(7):
                rect(fx, fy + s * 3, fw, 2 if s % 2 == 0 else 1,
                     RED2 if s % 2 == 0 else WHITE)
            rect(fx, fy, 14, 10, NAVY)
        else:
            rect(fx, fy, fw, fh, INK)
            rect(fx + 1, fy + 1, fw - 2, 5, WHITE)
            rect(fx + 1, fy + 7, fw - 2, 6, NAVY2)
            rect(fx + 1, fy + 14, fw - 2, 5, RED)
        draw_text(px - 1, base + 5, label, 2, INK)
    hline(x + 12, base, w - 24, INK, 3)


def scene_chip_down(x, y, w, h):
    """Markets story: a chip with a falling red chart line."""
    cx, cy = x + w // 2 - 12, y + h // 2 + 4
    rect(cx - 26, cy - 26, 52, 52, NAVY)
    rect(cx - 17, cy - 17, 34, 34, NAVY2)
    rect(cx - 9, cy - 9, 18, 18, GREEN)
    for i in range(5):
        rect(cx - 26 + i * 10, cy - 35, 5, 9, GREY2)
        rect(cx - 26 + i * 10, cy + 26, 5, 9, GREY2)
        rect(cx - 35, cy - 26 + i * 10, 9, 5, GREY2)
        rect(cx + 26, cy - 26 + i * 10, 9, 5, GREY2)
    # falling line, left to right, with a small arrowhead at the end
    seg(cx + 18, cy - 26, cx + 38, cy - 8, RED, 4)
    seg(cx + 38, cy - 8, cx + 58, cy + 12, RED, 4)
    seg(cx + 58, cy + 12, cx + 48, cy + 12, RED, 4)
    seg(cx + 58, cy + 12, cx + 58, cy + 2, RED, 4)


def scene_jets(x, y, w, h):
    """Japan story: two fighter jets climbing, one trailing a contrail."""
    rect(x, y, w, h, SKY)
    disc(x + w - 52, y + 26, 18, SUN)
    # contrails
    seg(x + 18, y + h - 30, x + w // 2 - 30, y + 34, WHITE, 3)
    seg(x + 30, y + h - 18, x + w // 2 - 10, y + 52, WHITE, 2)
    for jx, jy, s in ((x + w // 2 - 6, y + 30, 1), (x + w // 2 + 64, y + 52, 1)):
        # fuselage, swept wings, tail
        poly([(jx, jy - 6), (jx + 34, jy + 2), (jx, jy + 8)], GREY2)
        poly([(jx + 8, jy - 2), (jx + 18, jy - 16), (jx + 24, jy - 2)], GREY2)
        poly([(jx + 8, jy + 4), (jx + 16, jy + 16), (jx + 22, jy + 4)], GREY2)
        poly([(jx - 8, jy), (jx + 2, jy - 4), (jx + 2, jy + 4)], NAVY)


def scene_knesset(x, y, w, h):
    """Israel story: a parliament building with a dome and a ballot box."""
    bx, by = x + w // 2 - 78, y + h - 46
    # steps and columns
    rect(bx - 8, by + 26, 172, 6, GREY2)
    rect(bx - 4, by + 20, 164, 6, GREY)
    for i in range(5):
        vline(bx + 8 + i * 34, by - 6, 26, NAVY, 5)
    rect(bx, by - 12, 156, 8, NAVY)
    # dome
    arc(bx + 78, by - 12, 34, 180, 360, NAVY2, 5)
    vline(bx + 78, by - 52, 8, NAVY2, 4)
    disc(bx + 78, by - 54, 3, GOLD)
    # ballot box in front
    rect(x + w - 66, y + h - 34, 34, 26, RED)
    rect(x + w - 62, y + h - 40, 26, 6, RED2)
    draw_text(x + w - 58, y + h - 26, '66', 2, WHITE)


# ------------------------------------------------------------------ layout --
def frame(x, y, w, h):
    rect(x, y, w, h, WHITE)
    hline(x, y, w, INK, 2)
    hline(x, y + h - 2, w, INK, 2)
    vline(x, y, h, INK, 2)
    vline(x + w - 2, y, h, INK, 2)


def panel(x, y, w, h, kicker, kcolor, headline, body, draw_fn, ih=72):
    frame(x, y, w, h)
    rect(x + 2, y + 2, w - 4, 26, kcolor)
    draw_text(x + 12, y + 8, kicker, 2, WHITE)
    pad = 14
    draw_fn(x + pad, y + 34, w - 2 * pad, ih)
    ty = y + 34 + ih + 6
    draw_para(x + pad, ty, headline, 3, INK, w - 2 * pad, gap=3)
    n_head = len(wrap(headline, 3, w - 2 * pad))
    by = ty + n_head * (21 + 3) + 6
    draw_para(x + pad, by, body, 2, (74, 80, 96), w - 2 * pad, gap=3)


def build():
    rect(0, 0, W, H, PAPER)
    m = 24
    cw = W - 2 * m  # 976

    # masthead
    draw_center(m, 28, cw, 'THE WORLD IN ONE DAY', 6, NAVY)
    draw_center(m, 82, cw, 'TUESDAY - 17 NOVEMBER 2026', 3, RED)
    hline(m, 120, cw, INK, 3)
    hline(m, 126, cw, INK, 1)

    # lead story
    ly, lh = 140, 310
    frame(m, ly, cw, lh)
    scene_bridge(m + 14, ly + 14, 414, lh - 28)
    vline(m + 442, ly + 14, lh - 28, INK, 2)
    tx = m + 464
    tw = cw - 464 - 14
    rect(tx, ly + 16, tw, 26, RED)
    draw_text(tx + 10, ly + 22, 'WAR IN EUROPE - TOP STORY', 2, WHITE)
    draw_para(tx, ly + 56, 'CRIMEA BRIDGE HIT AGAIN', 4, INK, tw, gap=4)
    draw_para(tx, ly + 56 + 2 * 32 + 10,
              "UKRAINE STRIKES THE 19-KM LINK TO CRIMEA FOR A SECOND DAY. "
              "ZELENSKYY HAILS AN 'UNPRECEDENTED OPERATION' AS RUSSIA "
              "HITS KYIV'S BRIDGES IN REPLY.", 2, (74, 80, 96), tw, gap=4)
    draw_text(tx, ly + lh - 42, 'SECOND DAY IN A ROW', 2, RED)
    draw_text(tx, ly + lh - 24, 'TRAFFIC SUSPENDED', 2, RED)

    # row 1: three panels
    ry, rh = 466, 250
    pw = (cw - 2 * 16) // 3
    panel(m, ry, pw, rh, 'GULF TENSIONS', NAVY, 'IRAN DRONES TARGET US RADAR',
          'IRAN FIRES DRONES AT A US RADAR IN BAHRAIN. BAHRAIN AND THE US '
          'SAY ALL WERE SHOT DOWN.', scene_radar)
    panel(m + pw + 16, ry, pw, rh, 'ASIA SUMMIT', NAVY, 'XI, TRUMP, PUTIN TO MEET',
          'XI, TRUMP AND PUTIN WILL MEET IN SHENZHEN ON THURSDAY, CHINA '
          'CONFIRMS.', scene_summit)
    panel(m + 2 * (pw + 16), ry, pw, rh, 'MARKETS', NAVY, 'CHIP STOCKS KEEP SLIDING',
          'SHARES TUMBLE AS THE US TIGHTENS AI CHIP EXPORT CURBS. NVIDIA '
          'REPORTS AFTER THE BELL.', scene_chip_down)

    # row 2: two wide panels
    ry2, rh2 = 732, 228
    pw2 = (cw - 16) // 2
    panel(m, ry2, pw2, rh2, 'ASIA SECURITY', TEAL, 'JETS SCRAMBLED OVER JAPAN',
          "JAPAN LAUNCHES FIGHTERS AFTER SUSPECTED RUSSIAN JETS ENTER ITS "
          'AIRSPACE.', scene_jets, ih=96)
    panel(m + pw2 + 16, ry2, pw2, rh2, 'ISRAEL', GREEN, 'KNESSET PICKS NEW SPEAKER',
          "EISENKOT'S BLOC INSTALLS MATAN KAHANA, OUSTING A NETANYAHU ALLY "
          'AFTER THE DEADLOCKED VOTE.', scene_knesset, ih=96)

    # footer
    draw_center(m, 978, cw,
                'FIRST REPORTED 17 NOV 2026 - SOURCES: REUTERS, AP, AL JAZEERA, JUST SECURITY',
                2, FAINT)


# ---------------------------------------------------------------- PNG out ---
def chunk(typ, data):
    c = struct.pack('>I', len(data)) + typ + data
    return c + struct.pack('>I', zlib.crc32(typ + data) & 0xFFFFFFFF)


def encode_png():
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += buf[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + chunk(b'IEND', b''))


def main():
    build()
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR') or '/output'
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'entry.png'), 'wb') as f:
        f.write(encode_png())


if __name__ == '__main__':
    main()
