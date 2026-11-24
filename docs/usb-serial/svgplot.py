"""Small helpers for writing the USB serial graphs and timing figures as SVG.

Used by the figure scripts in this folder (a copy of the converter
pages' svgplot.py, so that each topic stands alone). Only the standard library is
needed. The colours follow the existing figures of the site: light fills,
dark ink, and one strong colour per trace.

SPDX-License-Identifier: Apache-2.0
"""

import math
import pathlib

INK = "#222222"
GREY = "#777777"
GRID = "#e4e4e4"
BLUE = "#1f4e79"       # main trace
ORANGE = "#c55a11"     # second trace, highlights
GREEN = "#38761d"      # third trace
RED = "#c0392b"        # limits, faults
FILL_BLUE = "#dbe8f5"
FILL_ORANGE = "#fbe5d6"
FILL_GREEN = "#e2f0d9"
FILL_GREY = "#ececec"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


class Svg:
    """An SVG drawing in pixel coordinates, origin at the top left."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.body = []

    def add(self, s):
        self.body.append(s)

    def rect(self, x, y, w, h, fill="none", stroke=INK, width=1.0, dash=None,
             rx=0, opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' fill-opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
                 f'height="{h:.1f}" rx="{rx}" fill="{fill}"{o} '
                 f'stroke="{stroke}" stroke-width="{width}"{d}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, width=1.2, dash=None,
             arrow=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = ""
        if arrow in ("end", "both"):
            m += ' marker-end="url(#arrow)"'
        if arrow in ("start", "both"):
            m += ' marker-start="url(#arrow)"'
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
                 f'y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width}"'
                 f'{d}{m}/>')

    def poly(self, pts, stroke=BLUE, width=2.0, dash=None, fill="none",
             opacity=None, close=False):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' fill-opacity="{opacity}"' if opacity is not None else ""
        tag = "polygon" if close else "polyline"
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.add(f'<{tag} points="{p}" fill="{fill}"{o} stroke="{stroke}" '
                 f'stroke-width="{width}" stroke-linejoin="round"{d}/>')

    def text(self, x, y, s, size=13, anchor="middle", weight="normal",
             fill=INK, rotate=None, italic=False):
        lines = str(s).split("\n")
        rot = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate else ""
        st = ' font-style="italic"' if italic else ""
        for i, ln in enumerate(lines):
            dy = (i - (len(lines) - 1) / 2) * (size + 2)
            self.add(f'<text x="{x:.1f}" y="{y + dy:.1f}" font-size="{size}" '
                     f'text-anchor="{anchor}" font-weight="{weight}" '
                     f'fill="{fill}" dominant-baseline="middle"{st}{rot}>'
                     f'{esc(ln)}</text>')

    def save(self, path):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" '
                f'height="{self.h}" viewBox="0 0 {self.w} {self.h}" '
                'font-family="Helvetica, Arial, sans-serif">\n'
                '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" '
                'refY="5" markerWidth="7" markerHeight="7" '
                'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
                f'fill="{INK}"/></marker></defs>\n'
                f'<rect width="{self.w}" height="{self.h}" fill="#ffffff"/>\n')
        pathlib.Path(path).write_text(head + "\n".join(self.body) + "\n</svg>\n",
                                      encoding="utf-8")
        print(f"wrote {path}")


class Axes:
    """Maps data values into a pixel box of an Svg."""

    def __init__(self, svg, box, xr, yr, xlog=False, ylog=False):
        self.s = svg
        self.x0, self.y0, self.x1, self.y1 = box   # left, top, right, bottom
        self.xr, self.yr = xr, yr
        self.xlog, self.ylog = xlog, ylog

    def _f(self, v, r, log):
        if log:
            return (math.log10(v) - math.log10(r[0])) / (
                math.log10(r[1]) - math.log10(r[0]))
        return (v - r[0]) / (r[1] - r[0])

    def X(self, v):
        return self.x0 + (self.x1 - self.x0) * self._f(v, self.xr, self.xlog)

    def Y(self, v):
        return self.y1 - (self.y1 - self.y0) * self._f(v, self.yr, self.ylog)

    def P(self, pts):
        return [(self.X(x), self.Y(y)) for x, y in pts]

    def frame(self, xticks=(), yticks=(), xlabel="", ylabel="", grid=True,
              xfmt=str, yfmt=str, size=13):
        s = self.s
        for v in xticks:
            x = self.X(v)
            if grid:
                s.line(x, self.y0, x, self.y1, stroke=GRID, width=1)
            s.line(x, self.y1, x, self.y1 + 5)
            s.text(x, self.y1 + 16, xfmt(v), size=size - 1)
        for v in yticks:
            y = self.Y(v)
            if grid:
                s.line(self.x0, y, self.x1, y, stroke=GRID, width=1)
            s.line(self.x0 - 5, y, self.x0, y)
            s.text(self.x0 - 8, y, yfmt(v), size=size - 1, anchor="end")
        s.line(self.x0, self.y1, self.x1, self.y1)
        s.line(self.x0, self.y0, self.x0, self.y1)
        if xlabel:
            s.text((self.x0 + self.x1) / 2, self.y1 + 38, xlabel, size=size)
        if ylabel:
            yc = (self.y0 + self.y1) / 2
            s.text(self.x0 - 48, yc, ylabel, size=size, rotate=-90)
