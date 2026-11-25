"""Shared SVG helpers for the Power over Ethernet figure scripts.

The graph and drawing scripts in this folder import this module. It uses
the standard library only and writes plain SVG in the style of the USB
Power Delivery graphs: black ink on white, Helvetica, grey keep-out fills,
and the colours of the Graphviz figures in this folder (far-end equipment
orange, power circuits yellow, evampire and the bus blue).

SPDX-License-Identifier: Apache-2.0
"""

import math
import pathlib

HERE = pathlib.Path(__file__).parent

INK = "#000000"
GREY = "#7f7f7f"
FILL = "#d9d9d9"
SRC = "#fbe5d6"        # source side, as in the Graphviz figures
SRC_INK = "#c55a11"
SNK = "#e2f0d9"        # sink side
SNK_INK = "#548235"
CABLE = "#dbe8f5"      # cable and neutral blue
CABLE_INK = "#2e75b6"
FONT = 'font-family="Helvetica, Arial, sans-serif"'
# Text is drawn this much larger than the size passed, so that a 680 px
# figure stays readable when the page scales it down on a narrow screen.
FONT_SCALE = 1.25


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=13, anchor="start", weight="normal", fill=INK,
         italic=False, rotate=None):
    st = ' font-style="italic"' if italic else ""
    rot = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" {FONT} '
            f'font-size="{size * FONT_SCALE:.1f}" '
            f'text-anchor="{anchor}" font-weight="{weight}" '
            f'fill="{fill}"{st}{rot}>{esc(s)}</text>')


def line(x1, y1, x2, y2, stroke=INK, width=1.0, dash=None, arrow=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = ""
    if arrow in ("end", "both"):
        m += ' marker-end="url(#arr)"'
    if arrow in ("start", "both"):
        m += ' marker-start="url(#arr)"'
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{width}"{d}{m}/>')


def rect(x, y, w, h, fill="none", stroke=INK, width=1.0, dash=None, rx=0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{width}"{d}/>')


def polyline(pts, stroke=INK, width=2.0, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{width}"{d}/>')


def polygon(pts, fill=FILL, stroke=INK, width=1.0):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{width}"/>')


ARROW = ('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
         'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>')


def svg(width, height, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">\n'
            f'<title>{esc(title)}</title>\n{ARROW}\n'
            f'<rect width="{width}" height="{height}" fill="#ffffff"/>\n'
            + "\n".join(body) + "\n</svg>\n")


def write(name, content):
    path = HERE / name
    path.write_text(content)
    print(f"wrote {path}")


class Plot:
    """A rectangular plot area mapping data (x, y) to pixels.

    xlog and ylog select logarithmic axes (base 10)."""

    def __init__(self, left, top, width, height, xr, yr, xlog=False,
                 ylog=False):
        self.left, self.top, self.w, self.h = left, top, width, height
        self.x0, self.x1 = xr
        self.y0, self.y1 = yr
        self.xlog, self.ylog = xlog, ylog

    @property
    def right(self):
        return self.left + self.w

    @property
    def bottom(self):
        return self.top + self.h

    def x(self, v):
        if self.xlog:
            a, b, v = math.log10(self.x0), math.log10(self.x1), math.log10(v)
        else:
            a, b = self.x0, self.x1
        return self.left + (v - a) / (b - a) * self.w

    def y(self, v):
        if self.ylog:
            a, b, v = math.log10(self.y0), math.log10(self.y1), math.log10(v)
        else:
            a, b = self.y0, self.y1
        return self.top + (b - v) / (b - a) * self.h

    def pts(self, data):
        return [(self.x(a), self.y(b)) for a, b in data]

    def frame(self):
        return rect(self.left, self.top, self.w, self.h, width=1.0)

    def xticks(self, ticks, label, fmt="{:g}", size=12, grid=True):
        out = []
        for t in ticks:
            x = self.x(t)
            if grid:
                out.append(line(x, self.top, x, self.bottom, GREY, 0.5,
                                "2,3"))
            out.append(line(x, self.bottom, x, self.bottom + 5))
            s = t if isinstance(t, str) else fmt.format(t)
            out.append(text(x, self.bottom + 18, s, size, "middle"))
        out.append(text(self.left + self.w / 2, self.bottom + 36, label, 13,
                        "middle"))
        return out

    def yticks(self, ticks, label, fmt="{:g}", size=12, grid=True):
        out = []
        for t in ticks:
            y = self.y(t)
            if grid:
                out.append(line(self.left, y, self.right, y, GREY, 0.5,
                                "2,3"))
            out.append(line(self.left - 5, y, self.left, y))
            out.append(text(self.left - 8, y + 4, fmt.format(t), size,
                            "end"))
        out.append(text(14, self.top + self.h / 2, label, 13, "middle",
                        rotate=-90))
        return out


# Colours of the Power over Ethernet Graphviz figures.
FAR = "#fbe5d6"        # far-end equipment
POWER = "#fff2cc"      # power circuits on the board
EVP = "#dbe8f5"        # evampire and the power bus
OK = "#e2f0d9"         # accepted or valid bands
OK_INK = "#548235"
BAD = "#f4cccc"        # rejected or invalid bands
BAD_INK = "#c00000"


def lines(x, y, s, size=12, anchor="start", fill=INK, gap=1.25,
          weight="normal"):
    """Several lines of text, one per newline, the first at y."""
    return [text(x, y + k * size * FONT_SCALE * gap, part, size, anchor,
                 weight, fill) for k, part in enumerate(s.split("\n"))]


def box(x, y, w, h, label, fill=POWER, size=12, rx=6, stroke=INK,
        dash=None):
    """A rounded box with centred, possibly multi-line, text."""
    out = [rect(x, y, w, h, fill, stroke, 1.0, dash, rx)]
    parts = label.split("\n")
    step = size * FONT_SCALE * 1.2
    y0 = y + h / 2 - step * (len(parts) - 1) / 2 + size * FONT_SCALE * 0.35
    for k, part in enumerate(parts):
        out.append(text(x + w / 2, y0 + k * step, part, size, "middle"))
    return out


def dot(x, y, r=3.0, fill=INK):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"/>'


def resistor(x1, y1, x2, y2, stroke=INK, n=6, amp=5.0, lead=0.25):
    """A zigzag resistor between two points, with straight leads."""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    a, b = lead * length, (1 - lead) * length
    pts = [(x1, y1), (x1 + ux * a, y1 + uy * a)]
    for k in range(1, 2 * n):
        t = a + (b - a) * k / (2 * n)
        s = amp if k % 2 else -amp
        pts.append((x1 + ux * t + px * s, y1 + uy * t + py * s))
    pts += [(x1 + ux * b, y1 + uy * b), (x2, y2)]
    return polyline(pts, stroke, 1.4)


def diode(x, y, direction="up", size=9.0, stroke=INK, fill=INK):
    """A diode symbol centred at (x, y), conducting towards direction."""
    s = size
    if direction == "up":
        tri = [(x - s, y + s * 0.8), (x + s, y + s * 0.8), (x, y - s * 0.8)]
        bar = (x - s, y - s * 0.8, x + s, y - s * 0.8)
    elif direction == "down":
        tri = [(x - s, y - s * 0.8), (x + s, y - s * 0.8), (x, y + s * 0.8)]
        bar = (x - s, y + s * 0.8, x + s, y + s * 0.8)
    elif direction == "right":
        tri = [(x - s * 0.8, y - s), (x - s * 0.8, y + s), (x + s * 0.8, y)]
        bar = (x + s * 0.8, y - s, x + s * 0.8, y + s)
    else:
        tri = [(x + s * 0.8, y - s), (x + s * 0.8, y + s), (x - s * 0.8, y)]
        bar = (x - s * 0.8, y - s, x - s * 0.8, y + s)
    return [polygon(tri, fill, stroke, 1.0), line(*bar, stroke, 1.6)]


def coil(x, y1, y2, side="right", turns=4, stroke=INK):
    """A vertical winding from y1 to y2, bulging to one side."""
    h = (y2 - y1) / turns
    sweep = 1 if side == "right" else 0
    d = f"M{x:.1f},{y1:.1f} "
    for k in range(turns):
        d += f"A{h / 2:.1f},{h / 2:.1f} 0 0 {sweep} {x:.1f},{y1 + h * (k + 1):.1f} "
    return (f'<path d="{d}" fill="none" stroke="{stroke}" '
            f'stroke-width="1.4"/>')


def capacitor(x, y, horizontal=False, w=10.0, gap=4.0, stroke=INK):
    """Capacitor plates centred at (x, y); leads join at the plate centres."""
    if horizontal:
        return [line(x - gap, y - w, x - gap, y + w, stroke, 1.8),
                line(x + gap, y - w, x + gap, y + w, stroke, 1.8)]
    return [line(x - w, y - gap, x + w, y - gap, stroke, 1.8),
            line(x - w, y + gap, x + w, y + gap, stroke, 1.8)]


def wire(pts, stroke=INK, width=1.4, dash=None):
    return polyline(pts, stroke, width, dash)
