#!/usr/bin/env python3
"""
Sum up 19 November 2026's world news in one image.

Pure Python 3 standard library only (zlib + struct for the PNG encoder).
Running this program writes a 1024x1024 PNG newspaper front page to
/output/entry.png (falling back to ./entry.png if /output is not writable).
"""
import math
import os
import struct
import zlib

W = H = 1024

# --------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph: 7 rows of 5 pixels ('#' = on).
# --------------------------------------------------------------------------
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '$': ("..#..", ".####", "##.#.", ".###.", ".#.##", "####.", "..#.."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
}


# --------------------------------------------------------------------------
# Canvas + minimal PNG writer (RGB, filter 0, zlib-compressed IDAT).
# --------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def save(self, path):
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)
            raw += self.px[y * stride:(y + 1) * stride]

        def chunk(tag, data):
            c = struct.pack(">I", len(data)) + tag + data
            return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0))
        png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        png += chunk(b"IEND", b"")
        with open(path, "wb") as f:
            f.write(png)


# --------------------------------------------------------------------------
# Drawing primitives.
# --------------------------------------------------------------------------
def fill_rect(cv, x, y, w, h, color):
    for yy in range(int(y), int(y + h)):
        for xx in range(int(x), int(x + w)):
            cv.set(xx, yy, color)


def rect_outline(cv, x, y, w, h, color, t=2):
    fill_rect(cv, x, y, w, t, color)
    fill_rect(cv, x, y + h - t, w, t, color)
    fill_rect(cv, x, y, t, h, color)
    fill_rect(cv, x + w - t, y, t, h, color)


def line(cv, x0, y0, x1, y1, color, t=1):
    """Thick line: stamp a small filled disc along a Bresenham path."""
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err, x, y = dx - dy, x0, y0
    while True:
        if t <= 1:
            cv.set(x, y, color)
        else:
            fill_circle(cv, x, y, t // 2, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def fill_circle(cv, cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(max(0, r * r - dy * dy)))
        fill_rect(cv, cx - dx, cy + dy, 2 * dx + 1, 1, color)


def circle_outline(cv, cx, cy, r, color, t=2):
    steps = max(24, int(2 * math.pi * r))
    for i in range(steps + 1):
        a = 2 * math.pi * i / steps
        fill_circle(cv, int(cx + r * math.cos(a)), int(cy + r * math.sin(a)), t // 2, color)


def fill_polygon(cv, pts, color):
    ys = [p[1] for p in pts]
    for y in range(min(ys), max(ys) + 1):
        nodes = []
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                nodes.append(int(x0 + (y - y0) * (x1 - x0) / (y1 - y0)))
        nodes.sort()
        for i in range(0, len(nodes) - 1, 2):
            fill_rect(cv, nodes[i], y, nodes[i + 1] - nodes[i] + 1, 1, color)


def dashed_bezier(cv, p0, p1, p2, color):
    """Dashed quadratic bezier from p0 (control p1) to p2: the signal path."""
    steps = 90
    for i in range(steps + 1):
        if (i // 5) % 2 == 0:
            t = i / steps
            x = int((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0])
            y = int((1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1])
            fill_circle(cv, x, y, 2, color)


# --------------------------------------------------------------------------
# Text.
# --------------------------------------------------------------------------
def text_width(s, scale, bold=False):
    if not s:
        return 0
    w = len(s) * 6 * scale - scale
    return w + (max(1, scale // 3) if bold else 0)


def draw_text(cv, x, y, s, scale, color, bold=False):
    extra = max(1, scale // 3)
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[' '])
        for ry, row in enumerate(glyph):
            for rx, c in enumerate(row):
                if c == '#':
                    fill_rect(cv, x + rx * scale, y + ry * scale, scale, scale, color)
                    if bold:
                        fill_rect(cv, x + rx * scale + extra, y + ry * scale, scale, scale, color)
        x += 6 * scale
    return x


def center_text(cv, cx, y, s, scale, color, bold=False):
    draw_text(cv, cx - text_width(s, scale, bold) // 2, y, s, scale, color, bold)


# --------------------------------------------------------------------------
# Palette.
# --------------------------------------------------------------------------
PAPER = (246, 241, 227)
CARD = (253, 251, 244)
INK = (26, 26, 32)
GRAY = (96, 94, 88)
NAVY = (18, 22, 56)
GOLD = (240, 198, 92)
WHITE = (255, 255, 255)


# --------------------------------------------------------------------------
# Icons. Each paints inside the zone (ix, iy, iw=448, ih=140).
# --------------------------------------------------------------------------
def icon_courthouse(cv, ix, iy):
    cx, gy = ix + 224, iy + 132          # building centre x, ground line y
    stone, stone_d = (216, 211, 198), (168, 163, 148)
    fill_rect(cv, cx - 132, gy - 10, 264, 10, stone_d)        # steps
    fill_rect(cv, cx - 116, gy - 22, 232, 12, stone)
    for off in (-102, -36, 36, 102):                          # columns
        fill_rect(cv, cx + off - 9, gy - 86, 18, 64, stone)
        rect_outline(cv, cx + off - 9, gy - 86, 18, 64, INK, 2)
    fill_rect(cv, cx - 126, gy - 104, 252, 18, stone)         # entablature
    rect_outline(cv, cx - 126, gy - 104, 252, 18, INK, 2)
    fill_polygon(cv, [(cx - 136, gy - 104), (cx + 136, gy - 104), (cx, gy - 132)], stone)
    line(cv, cx - 136, gy - 104, cx, gy - 132, INK, 3)
    line(cv, cx + 136, gy - 104, cx, gy - 132, INK, 3)
    fill_circle(cv, cx, gy - 112, 6, GOLD)
    fill_rect(cv, cx - 132, gy - 10, 264, 3, INK)


def icon_flags(cv, ix, iy):
    cx, cy = ix + 224, iy + 78
    fill_circle(cv, cx, cy, 56, (198, 219, 240))              # pale globe
    circle_outline(cv, cx, cy, 56, (120, 150, 190), 2)
    poles = [ix + 84, ix + 196, ix + 308]
    for px in poles:
        line(cv, px, iy + 14, px, iy + 134, INK, 4)
        fill_circle(cv, px, iy + 11, 4, GOLD)
    fill_rect(cv, ix + 60, iy + 134, 328, 3, INK)
    fw, fh = 86, 54
    # United States: stripes + blue canton
    x, y = poles[0], iy + 16
    fill_rect(cv, x, y, fw, fh, WHITE)
    for i in range(0, 7, 2):
        fill_rect(cv, x, y + i * 8, fw, 8, (178, 34, 52))
    fill_rect(cv, x, y, 38, 28, (38, 48, 110))
    for r in range(3):
        for c in range(4):
            fill_circle(cv, x + 6 + c * 9, y + 6 + r * 9, 1, WHITE)
    rect_outline(cv, x, y, fw, fh, INK, 2)
    # China: red field, gold stars
    x = poles[1]
    fill_rect(cv, x, y, fw, fh, (206, 32, 40))
    fill_circle(cv, x + 14, y + 14, 5, GOLD)
    for dx, dy in ((26, 6), (29, 14), (29, 23), (25, 30)):
        fill_circle(cv, x + dx, y + dy, 2, GOLD)
    rect_outline(cv, x, y, fw, fh, INK, 2)
    # Russia: white / blue / red bands
    x = poles[2]
    fill_rect(cv, x, y, fw, 18, WHITE)
    fill_rect(cv, x, y + 18, fw, 18, (30, 70, 160))
    fill_rect(cv, x, y + 36, fw, 18, (200, 40, 45))
    rect_outline(cv, x, y, fw, fh, INK, 2)


def icon_voyager(cv, ix, iy):
    fill_rect(cv, ix, iy, 448, 140, (8, 10, 28))
    seed = 12345                                              # deterministic stars
    for _ in range(70):
        seed = (1103515245 * seed + 12345) % (2 ** 31)
        sx = ix + seed % 448
        seed = (1103515245 * seed + 12345) % (2 ** 31)
        sy = iy + seed % 140
        fill_circle(cv, sx, sy, 1 if seed % 3 else 2, (230, 232, 255))
    ex, ey = ix + 54, iy + 102                                # Earth
    dx, dy = ix + 322, iy + 54                                # probe + dish
    dashed_bezier(cv, (ex + 12, ey - 14), (ix + 180, iy - 6), (dx - 26, dy + 12), GOLD)
    fill_circle(cv, ex, ey, 17, (62, 112, 222))
    fill_circle(cv, ex - 6, ey - 5, 6, (80, 190, 100))
    fill_circle(cv, ex + 7, ey + 6, 5, (80, 190, 100))
    line(cv, dx - 6, dy + 30, ix + 238, iy + 128, (170, 170, 180), 4)   # boom
    fill_rect(cv, ix + 224, iy + 122, 20, 10, (170, 170, 180))
    line(cv, dx + 8, dy + 32, ix + 396, iy + 108, (170, 170, 180), 4)   # RTG arm
    fill_rect(cv, ix + 388, iy + 100, 30, 12, (120, 120, 130))
    fill_circle(cv, dx, dy, 31, (228, 228, 232))
    circle_outline(cv, dx, dy, 31, INK, 2)
    circle_outline(cv, dx, dy, 20, (150, 150, 160), 2)
    line(cv, dx, dy, dx + 16, dy - 16, INK, 3)
    fill_circle(cv, dx + 17, dy - 17, 4, INK)
    fill_rect(cv, dx - 13, dy + 28, 26, 17, (202, 162, 62))   # bus
    rect_outline(cv, dx - 13, dy + 28, 26, 17, INK, 2)
    line(cv, dx + 20, dy - 24, dx + 44, dy - 44, (200, 200, 208), 3)    # whip antenna
    fill_circle(cv, dx + 45, dy - 45, 3, (200, 200, 208))
    draw_text(cv, ix + 292, iy + 116, "1 LIGHT-DAY", 2, (255, 220, 120), bold=True)


def icon_vice_city(cv, ix, iy):
    bands = [(255, 176, 84), (253, 150, 84), (248, 122, 96),
             (232, 94, 116), (206, 72, 128), (176, 58, 128)]
    for i, col in enumerate(bands):
        fill_rect(cv, ix, iy + i * 24, 448, 24, col)
    fill_circle(cv, ix + 336, iy + 48, 24, (255, 232, 150))   # sun
    dark = (32, 20, 44)
    bx = ix                                                 # skyline
    for bw, bh in ((48, 52), (36, 74), (54, 44), (32, 88), (50, 58),
                   (38, 70), (58, 48), (34, 80), (50, 56), (40, 66)):
        fill_rect(cv, bx, iy + 140 - bh, bw, bh, dark)
        for wy in range(iy + 140 - bh + 8, iy + 132, 12):   # lit windows
            for wx in range(bx + 6, bx + bw - 6, 11):
                if (wx * 7 + wy * 13) % 5 == 0:
                    fill_rect(cv, wx, wy, 4, 5, (255, 214, 110))
        bx += bw
    fill_rect(cv, ix, iy + 136, 448, 4, dark)

    def palm(px, base, top, lean):
        pts = []
        for i in range(21):                                 # curved trunk
            t = i / 20
            pts.append((int(px + lean * t * t), int(base + (top - base) * t)))
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            line(cv, x0, y0, x1, y1, dark, 6)
        tx, ty = pts[-1]
        fill_circle(cv, tx - 5, ty + 3, 4, dark)            # coconuts
        fill_circle(cv, tx + 5, ty + 3, 4, dark)
        for d in (-1, -0.5, 0, 0.5, 1):                     # arcing fronds
            for i in range(13):
                t0, t1 = i / 12, (i + 1) / 12
                line(cv, int(tx + d * 46 * t0), int(ty - 20 * t0 + 40 * t0 * t0),
                     int(tx + d * 46 * t1), int(ty - 20 * t1 + 40 * t1 * t1), dark, 4)

    palm(ix + 58, iy + 140, iy + 40, 24)
    palm(ix + 152, iy + 140, iy + 62, -18)
    fill_circle(cv, ix + 398, iy + 34, 23, (18, 16, 30))    # VI badge
    circle_outline(cv, ix + 398, iy + 34, 23, WHITE, 2)
    draw_text(cv, ix + 398 - text_width("VI", 3, True) // 2, iy + 34 - 10, "VI", 3, WHITE, bold=True)


# --------------------------------------------------------------------------
# Page assembly.
# --------------------------------------------------------------------------
PANELS = [
    ("WORLD COURT - THE HAGUE", (31, 58, 110), icon_courthouse,
     ["UN COURT: MYANMAR", "GUILTY OF GENOCIDE"],
     "FIRST-EVER STATE GENOCIDE VERDICT"),
    ("SUMMIT - SHENZHEN", (150, 30, 36), icon_flags,
     ["US, CHINA & RUSSIA", "SIGN PEACE DECLARATION"],
     "FIRST TRILATERAL SUMMIT OF ITS KIND"),
    ("SPACE - DEEP SPACE", (24, 24, 54), icon_voyager,
     ["VOYAGER 1 NOW ONE", "LIGHT-DAY AWAY"],
     "ITS SIGNALS TAKE 24 HOURS TO ARRIVE"),
    ("GAMES - VICE CITY", (176, 52, 110), icon_vice_city,
     ["GTA VI LAUNCHES AFTER", "13-YEAR WAIT"],
     "RECORD $1.1 BILLION IN PRE-ORDERS"),
]


def panel(cv, px, py, cat, color, icon, headline, sub):
    fill_rect(cv, px, py, 476, 329, CARD)
    rect_outline(cv, px, py, 476, 329, INK, 3)
    fill_rect(cv, px, py, 476, 42, color)
    draw_text(cv, px + 16, py + 12, cat, 2, WHITE, bold=True)
    icon(cv, px + 14, py + 54)
    hy = py + 210
    for ln in headline:
        draw_text(cv, px + 16, hy, ln, 3, INK, bold=True)
        hy += 32
    fill_rect(cv, px + 16, hy + 1, 60, 3, GOLD)   # gold rule above the standfirst
    draw_text(cv, px + 16, hy + 10, sub, 2, GRAY)


def main():
    cv = Canvas(W, H, PAPER)
    rect_outline(cv, 12, 12, W - 24, H - 24, INK, 3)
    # Masthead
    fill_rect(cv, 28, 34, W - 56, 3, INK)
    fill_rect(cv, 28, 41, W - 56, 1, INK)
    center_text(cv, 512, 50, "ALL THE DAY'S NEWS - ON ONE PAGE", 2, GRAY)
    center_text(cv, 512, 76, "WORLD NEWS", 11, INK, bold=True)
    fill_rect(cv, 28, 166, W - 56, 2, INK)
    fill_rect(cv, 28, 172, W - 56, 5, INK)
    # Date band: the date, unmistakable
    fill_rect(cv, 28, 190, W - 56, 100, NAVY)
    center_text(cv, 512, 204, "19 NOVEMBER 2026", 8, WHITE, bold=True)
    center_text(cv, 512, 268, "T H U R S D A Y", 2, GOLD)
    tw = text_width("T H U R S D A Y", 2)          # gold rules flanking the weekday
    fill_rect(cv, 512 - tw // 2 - 92, 274, 64, 3, GOLD)
    fill_rect(cv, 512 + tw // 2 + 28, 274, 64, 3, GOLD)
    # Dateline strip: where the day's four stories happened
    center_text(cv, 512, 292, "THE HAGUE - SHENZHEN - DEEP SPACE - VICE CITY", 2, GRAY)
    # Panels, 2 x 2
    pos = [(28, 308), (520, 308), (28, 653), (520, 653)]
    for (px, py), args in zip(pos, PANELS):
        panel(cv, px, py, *args)
    center_text(cv, 512, 992, "FOUR STORIES THAT DEFINED THE DAY", 2, GRAY)
    # Write to /output/entry.png, else ./entry.png
    try:
        os.makedirs("/output", exist_ok=True)
        out = "/output/entry.png"
        cv.save(out)
    except OSError:
        out = "entry.png"
        cv.save(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
