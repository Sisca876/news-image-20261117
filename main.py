#!/usr/bin/env python3
"""Front page for Tuesday 17 November 2026, drawn by this program alone.

The program paints a 1024x1024 newspaper front page -- masthead, one lead
story and five smaller stories -- with a tiny 5x7 pixel font, then writes it
as a PNG. Only the Python standard library is used, there is no network, no
clock and no randomness, so every run writes identical bytes.

    MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
"""

import math
import os
import struct
import zlib

SIZE = 1024

PAL = {
    "paper": (246, 242, 232),
    "ink": (22, 30, 48),
    "navy": (26, 44, 78),
    "navy2": (48, 72, 118),
    "red": (176, 36, 28),
    "red2": (212, 88, 78),
    "sky": (184, 212, 228),
    "sky2": (138, 178, 204),
    "sea": (44, 108, 140),
    "sea2": (26, 80, 108),
    "grey": (98, 106, 118),
    "grey2": (60, 66, 78),
    "smoke": (122, 124, 128),
    "smoke2": (160, 162, 165),
    "sun": (232, 176, 72),
    "green": (44, 122, 68),
    "green2": (118, 188, 128),
    "gold": (198, 160, 38),
    "white": (255, 255, 255),
    "orange": (212, 108, 42),
    "teal": (30, 138, 128),
    "faint": (118, 116, 110),
    "body": (74, 80, 96),
}

# ------------------------------------------------------- 5x7 pixel font ---
# One glyph per character: seven rows, each row a 5-bit number, the leftmost
# pixel in the highest bit. Only the characters the page needs are listed.
GLYPHS = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1C, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1C),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0, 0x04),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    "+": (0, 0x04, 0x04, 0x0E, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '"': (0x0A, 0x0A, 0, 0, 0, 0, 0),
}

# ------------------------------------------------------------ the canvas ---
# One flat RGB buffer for the whole page; every drawing helper writes into it.
PIX = bytearray(SIZE * SIZE * 3)


def put(x, y, rgb):
    """Paint a single pixel, silently ignoring out-of-page coordinates."""
    if 0 <= x < SIZE and 0 <= y < SIZE:
        at = (y * SIZE + x) * 3
        PIX[at], PIX[at + 1], PIX[at + 2] = rgb


def box(x, y, w, h, rgb):
    """Paint a filled rectangle, clipped to the page."""
    xa, ya = max(0, x), max(0, y)
    xb, yb = min(SIZE, x + w), min(SIZE, y + h)
    for yy in range(ya, yb):
        base = (yy * SIZE + xa) * 3
        for xx in range(xa, xb):
            at = base + (xx - xa) * 3
            PIX[at], PIX[at + 1], PIX[at + 2] = rgb


def hrule(x, y, w, rgb, thick=1):
    box(x, y, w, thick, rgb)


def vrule(x, y, h, rgb, thick=1):
    box(x, y, thick, h, rgb)


def stroke(x0, y0, x1, y1, rgb, thick=1):
    """Bresenham line between two points."""
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        for a in range(thick):
            for b in range(thick):
                put(x0 + a, y0 + b, rgb)
        if x0 == x1 and y0 == y1:
            break
        twice = 2 * err
        if twice > -dy:
            err -= dy
            x0 += sx
        if twice < dx:
            err += dx
            y0 += sy


def blob(cx, cy, r, rgb, solid=True):
    """A disc; outline only when solid is False."""
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = (xx - cx) ** 2 + (yy - cy) ** 2
            if solid:
                if d <= r * r:
                    put(xx, yy, rgb)
            elif r * r - 2 * r <= d <= r * r:
                put(xx, yy, rgb)


def curve(cx, cy, r, start, stop, rgb, thick=2):
    """An arc; angles in degrees, 0 = east, clockwise (y grows downwards)."""
    span = abs(stop - start)
    steps = max(8, int(span * r / 12))
    for s in range(steps + 1):
        ang = math.radians(start + (stop - start) * s / steps)
        px = int(round(cx + r * math.cos(ang)))
        py = int(round(cy + r * math.sin(ang)))
        for a in range(thick):
            for b in range(thick):
                put(px + a, py + b, rgb)


def fillpoly(corners, rgb):
    """A filled polygon, scanline by scanline."""
    top = min(p[1] for p in corners)
    bottom = max(p[1] for p in corners)
    n = len(corners)
    for y in range(top, bottom + 1):
        hits = []
        for i in range(n):
            x0, y0 = corners[i]
            x1, y1 = corners[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                hits.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        hits.sort()
        for k in range(0, len(hits) - 1, 2):
            for x in range(int(hits[k]), int(hits[k + 1]) + 1):
                put(x, y, rgb)


# ------------------------------------------------------------------- text --
def _step(scale):
    # One glyph cell: five pixels plus a one-pixel gap, times the scale.
    return 6 * scale


def str_w(text, scale):
    text = text.upper()
    return len(text) * _step(scale) - scale if text else 0


def put_text(x, y, text, scale, rgb):
    """Draw text left-aligned; returns the x just past the last glyph."""
    cx = x
    for ch in text.upper():
        rows = GLYPHS.get(ch)
        if rows:
            for r in range(7):
                bits = rows[r]
                for col in range(5):
                    if bits >> (4 - col) & 1:
                        box(cx + col * scale, y + r * scale, scale, scale, rgb)
        cx += _step(scale)
    return cx


def put_centre(x, y, w, text, scale, rgb):
    put_text(x + (w - str_w(text, scale)) // 2, y, text, scale, rgb)


def split_lines(text, scale, max_w):
    """Greedy word wrap into lines that fit max_w pixels."""
    lines, cur = [], ""
    for word in text.upper().split(" "):
        trial = word if not cur else cur + " " + word
        if str_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def put_para(x, y, text, scale, rgb, max_w, gap=4):
    """Draw a wrapped paragraph; returns the y just past its last line."""
    yy = y
    for ln in split_lines(text, scale, max_w):
        put_text(x, yy, ln, scale, rgb)
        yy += 7 * scale + gap
    return yy


# -------------------------------------------------------------- the pictures
def pic_bridge(x, y, w, h):
    """The Kerch bridge to Crimea: two standing spans, the middle span
    dropped into the strait, smoke rising where the road arch broke."""
    box(x, y, w, h, PAL["sky"])
    blob(x + w - 64, y + 40, 24, PAL["sun"])
    blob(x + w - 64, y + 40, 17, (240, 198, 110))
    box(x, y + h - 104, w, 12, (118, 148, 138))  # far shore
    box(x, y + h - 92, w, 92, PAL["sea"])
    hrule(x, y + h - 92, w, PAL["sea2"], 4)
    for wy in (y + h - 68, y + h - 44, y + h - 20):
        for wx in range(x + 10, x + w - 10, 44):
            hrule(wx, wy, 24, PAL["sea2"], 2)
    deck = y + h - 146
    box(x + 8, deck, 148, 13, PAL["grey2"])       # left span
    box(x + w - 156, deck, 148, 13, PAL["grey2"])  # right span
    box(x + 32, deck - 58, 9, 58, PAL["grey2"])    # pylons
    box(x + w - 41, deck - 58, 9, 58, PAL["grey2"])
    curve(x + 156, deck + 13, 58, 200, 340, PAL["grey"], 5)
    curve(x + w - 156, deck + 13, 58, 200, 340, PAL["grey"], 5)
    # the fallen middle span, sliding down into the water
    fillpoly([(x + 164, deck + 1), (x + 192, deck + 1),
              (x + 222, deck + 76), (x + 194, deck + 76)], PAL["grey2"])
    fillpoly([(x + 164, deck + 1), (x + 172, deck + 13),
              (x + 202, deck + 76), (x + 194, deck + 76)], PAL["grey"])
    vrule(x + 58, deck + 13, 64, PAL["grey2"], 6)
    vrule(x + w - 64, deck + 13, 64, PAL["grey2"], 6)
    blob(x + w // 2 - 16, deck - 34, 15, PAL["smoke"])
    blob(x + w // 2 + 10, deck - 50, 19, PAL["smoke2"])
    blob(x + w // 2 + 32, deck - 26, 11, PAL["smoke"])
    blob(x + w // 2 - 36, deck - 56, 11, PAL["smoke2"])


def pic_radar(x, y, w, h):
    """A radar dish sweeping while three drones are shot down above it."""
    cx, cy = x + w // 2, y + h // 2 + 10
    for dx, dy in ((-56, -30), (46, -36), (6, -42)):
        stroke(cx + dx - 7, cy + dy, cx + dx + 7, cy + dy, PAL["ink"], 2)
        stroke(cx + dx, cy + dy - 7, cx + dx, cy + dy + 7, PAL["ink"], 2)
    curve(cx, cy - 4, 30, 180, 360, PAL["navy"], 4)
    hrule(cx - 30, cy - 4, 60, PAL["navy"], 4)
    stroke(cx, cy - 4, cx + 24, cy - 26, PAL["red"], 3)
    vrule(cx, cy - 4, 26, PAL["navy"], 6)
    fillpoly([(cx - 24, cy + 22), (cx + 24, cy + 22), (cx + 7, cy + 2),
              (cx - 7, cy + 2)], PAL["navy"])
    hrule(x + 14, cy + 22, w - 28, PAL["navy"], 3)


def pic_summit(x, y, w, h):
    """Three flag poles -- China, the United States, Russia -- for the
    three-way summit in Shenzhen."""
    base = y + h - 22
    step = (w - 36) // 3
    for i, kind in enumerate(("china", "usa", "russia")):
        px = x + 22 + i * step
        vrule(px, y + 16, base - y - 16, PAL["ink"], 3)
        fx, fy, fw, fh = px + 3, y + 16, 32, 20
        if kind == "china":
            box(fx, fy, fw, fh, PAL["red"])
            blob(fx + 9, fy + 10, 3, PAL["gold"])
            for sx, sy in ((20, 5), (24, 9), (24, 13), (20, 16)):
                put(fx + sx, fy + sy, PAL["gold"])
        elif kind == "usa":
            for s in range(7):
                box(fx, fy + s * 3, fw, 2 if s % 2 == 0 else 1,
                    PAL["red2"] if s % 2 == 0 else PAL["white"])
            box(fx, fy, 14, 10, PAL["navy"])
        else:
            box(fx, fy, fw, fh, PAL["ink"])
            box(fx + 1, fy + 1, fw - 2, 5, PAL["white"])
            box(fx + 1, fy + 7, fw - 2, 6, PAL["navy2"])
            box(fx + 1, fy + 14, fw - 2, 5, PAL["red"])
        put_text(px - 1, base + 5, ("CN", "US", "RU")[i], 2, PAL["ink"])
    hrule(x + 12, base, w - 24, PAL["ink"], 3)


def pic_chip(x, y, w, h):
    """A chip with a red line falling away from it: chip stocks sliding."""
    cx, cy = x + w // 2 - 12, y + h // 2 + 4
    box(cx - 26, cy - 26, 52, 52, PAL["navy"])
    box(cx - 17, cy - 17, 34, 34, PAL["navy2"])
    box(cx - 9, cy - 9, 18, 18, PAL["green"])
    for i in range(5):
        box(cx - 26 + i * 10, cy - 35, 5, 9, PAL["grey2"])
        box(cx - 26 + i * 10, cy + 26, 5, 9, PAL["grey2"])
        box(cx - 35, cy - 26 + i * 10, 9, 5, PAL["grey2"])
        box(cx + 26, cy - 26 + i * 10, 9, 5, PAL["grey2"])
    stroke(cx + 18, cy - 26, cx + 38, cy - 8, PAL["red"], 4)
    stroke(cx + 38, cy - 8, cx + 58, cy + 12, PAL["red"], 4)
    stroke(cx + 58, cy + 12, cx + 48, cy + 12, PAL["red"], 4)
    stroke(cx + 58, cy + 12, cx + 58, cy + 2, PAL["red"], 4)


def pic_jets(x, y, w, h):
    """Two fighter jets climbing over Japan, contrails behind them."""
    box(x, y, w, h, PAL["sky"])
    blob(x + w - 52, y + 26, 18, PAL["sun"])
    stroke(x + 18, y + h - 30, x + w // 2 - 30, y + 34, PAL["white"], 3)
    stroke(x + 30, y + h - 18, x + w // 2 - 10, y + 52, PAL["white"], 2)
    for jx, jy in ((x + w // 2 - 6, y + 30), (x + w // 2 + 64, y + 52)):
        fillpoly([(jx, jy - 6), (jx + 34, jy + 2), (jx, jy + 8)], PAL["grey2"])
        fillpoly([(jx + 8, jy - 2), (jx + 18, jy - 16), (jx + 24, jy - 2)],
                 PAL["grey2"])
        fillpoly([(jx + 8, jy + 4), (jx + 16, jy + 16), (jx + 22, jy + 4)],
                 PAL["grey2"])
        fillpoly([(jx - 8, jy), (jx + 2, jy - 4), (jx + 2, jy + 4)], PAL["navy"])


def pic_knesset(x, y, w, h):
    """A parliament building under a dome, with a ballot box marked 66 --
    the votes that installed the new speaker."""
    bx, by = x + w // 2 - 78, y + h - 46
    box(bx - 8, by + 26, 172, 6, PAL["grey2"])
    box(bx - 4, by + 20, 164, 6, PAL["grey"])
    for i in range(5):
        vrule(bx + 8 + i * 34, by - 6, 26, PAL["navy"], 5)
    box(bx, by - 12, 156, 8, PAL["navy"])
    curve(bx + 78, by - 12, 34, 180, 360, PAL["navy2"], 5)
    vrule(bx + 78, by - 52, 8, PAL["navy2"], 4)
    blob(bx + 78, by - 54, 3, PAL["gold"])
    box(x + w - 66, y + h - 34, 34, 26, PAL["red"])
    box(x + w - 62, y + h - 40, 26, 6, PAL["red2"])
    put_text(x + w - 58, y + h - 26, "66", 2, PAL["white"])


# ------------------------------------------------------------ the layout ---
def card(x, y, w, h, kicker, tint, headline, body, picture, pic_h=72):
    """One story panel: coloured kicker strip, small picture, headline,
    then body text."""
    box(x, y, w, h, PAL["white"])
    hrule(x, y, w, PAL["ink"], 2)
    hrule(x, y + h - 2, w, PAL["ink"], 2)
    vrule(x, y, h, PAL["ink"], 2)
    vrule(x + w - 2, y, h, PAL["ink"], 2)
    box(x + 2, y + 2, w - 4, 26, tint)
    put_text(x + 12, y + 8, kicker, 2, PAL["white"])
    pad = 14
    picture(x + pad, y + 34, w - 2 * pad, pic_h)
    ty = y + 34 + pic_h + 6
    put_para(x + pad, ty, headline, 3, PAL["ink"], w - 2 * pad, gap=3)
    head_lines = len(split_lines(headline, 3, w - 2 * pad))
    by = ty + head_lines * (21 + 3) + 6
    put_para(x + pad, by, body, 2, PAL["body"], w - 2 * pad, gap=3)


def compose():
    """Lay out the whole front page."""
    box(0, 0, SIZE, SIZE, PAL["paper"])
    m = 24
    cw = SIZE - 2 * m  # 976

    # masthead
    put_centre(m, 28, cw, "THE WORLD IN ONE DAY", 6, PAL["navy"])
    put_centre(m, 82, cw, "TUESDAY - 17 NOVEMBER 2026", 3, PAL["red"])
    hrule(m, 120, cw, PAL["ink"], 3)
    hrule(m, 126, cw, PAL["ink"], 1)

    # lead story: picture left, words right
    ly, lh = 140, 310
    box(m, ly, cw, lh, PAL["white"])
    hrule(m, ly, cw, PAL["ink"], 2)
    hrule(m, ly + lh - 2, cw, PAL["ink"], 2)
    vrule(m, ly, lh, PAL["ink"], 2)
    vrule(m + cw - 2, ly, lh, PAL["ink"], 2)
    pic_bridge(m + 14, ly + 14, 414, lh - 28)
    vrule(m + 442, ly + 14, lh - 28, PAL["ink"], 2)
    tx = m + 464
    tw = cw - 464 - 14
    box(tx, ly + 16, tw, 26, PAL["red"])
    put_text(tx + 10, ly + 22, "WAR IN EUROPE - TOP STORY", 2, PAL["white"])
    put_para(tx, ly + 56, "CRIMEA BRIDGE HIT AGAIN", 4, PAL["ink"], tw, gap=4)
    put_para(tx, ly + 56 + 2 * 32 + 10,
             "UKRAINE STRIKES THE 19-KM LINK TO CRIMEA FOR A SECOND DAY. "
             "ZELENSKYY HAILS AN 'UNPRECEDENTED OPERATION' AS RUSSIA "
             "HITS KYIV'S BRIDGES IN REPLY.", 2, PAL["body"], tw, gap=4)
    put_text(tx, ly + lh - 42, "SECOND DAY IN A ROW", 2, PAL["red"])
    put_text(tx, ly + lh - 24, "TRAFFIC SUSPENDED", 2, PAL["red"])

    # first row: three stories side by side
    ry, rh = 466, 250
    pw = (cw - 2 * 16) // 3
    card(m, ry, pw, rh, "GULF TENSIONS", PAL["navy"],
         "IRAN DRONES TARGET US RADAR",
         "IRAN FIRES DRONES AT A US RADAR IN BAHRAIN. BAHRAIN AND THE US "
         "SAY ALL WERE SHOT DOWN.", pic_radar)
    card(m + pw + 16, ry, pw, rh, "ASIA SUMMIT", PAL["navy"],
         "XI, TRUMP, PUTIN TO MEET",
         "XI, TRUMP AND PUTIN WILL MEET IN SHENZHEN ON THURSDAY, CHINA "
         "CONFIRMS.", pic_summit)
    card(m + 2 * (pw + 16), ry, pw, rh, "MARKETS", PAL["navy"],
         "CHIP STOCKS KEEP SLIDING",
         "SHARES TUMBLE AS THE US TIGHTENS AI CHIP EXPORT CURBS. NVIDIA "
         "REPORTS AFTER THE BELL.", pic_chip)

    # second row: two wider stories
    ry2, rh2 = 732, 228
    pw2 = (cw - 16) // 2
    card(m, ry2, pw2, rh2, "ASIA SECURITY", PAL["teal"],
         "JETS SCRAMBLED OVER JAPAN",
         "JAPAN LAUNCHES FIGHTERS AFTER SUSPECTED RUSSIAN JETS ENTER ITS "
         "AIRSPACE.", pic_jets, pic_h=96)
    card(m + pw2 + 16, ry2, pw2, rh2, "ISRAEL", PAL["green"],
         "KNESSET PICKS NEW SPEAKER",
         "EISENKOT'S BLOC INSTALLS MATAN KAHANA, OUSTING A NETANYAHU ALLY "
         "AFTER THE DEADLOCKED VOTE.", pic_knesset, pic_h=96)

    # footer: when the news was first reported, and from whom
    put_centre(m, 978, cw,
               "FIRST REPORTED 17 NOV 2026 - SOURCES: REUTERS, AP, AL JAZEERA, JUST SECURITY",
               2, PAL["faint"])


# ------------------------------------------------------------- PNG output --
def _chunk(kind, payload):
    head = struct.pack(">I", len(payload)) + kind + payload
    return head + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def to_png():
    rows = bytearray()
    for y in range(SIZE):
        rows.append(0)  # no filter on any scanline
        rows += PIX[y * SIZE * 3:(y + 1) * SIZE * 3]
    header = struct.pack(">IIBBBBB", SIZE, SIZE, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", header)
            + _chunk(b"IDAT", zlib.compress(bytes(rows), 9))
            + _chunk(b"IEND", b""))


def main():
    compose()
    dest = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(dest, exist_ok=True)
    with open(os.path.join(dest, "entry.png"), "wb") as fh:
        fh.write(to_png())


if __name__ == "__main__":
    main()
