"""Small helpers that write SVG graphs and drawings with the standard library.

The figure scripts on the Ethernet transceiver pages import this module. It
draws dark lines and text on a white background, in the light colours of
the other figures on the site.

SPDX-License-Identifier: Apache-2.0
"""

import math
from xml.sax.saxutils import escape

FONT = "Helvetica, Arial, sans-serif"
INK = "#222222"
GREY = "#777777"
GRID = "#e4e4e4"
BLUE = "#1f4e79"
RED = "#c0392b"
GREEN = "#2e7d32"
ORANGE = "#d35400"
PURPLE = "#6a3d9a"
FILL_BLUE = "#dbe8f5"
FILL_GREEN = "#e2efda"
FILL_ORANGE = "#fbe5d6"
FILL_GREY = "#f2f2f2"


class Fig:
    """An SVG canvas of a fixed size in px."""

    def __init__(self, width, height):
        self.w, self.h = width, height
        self.parts = [f'<rect width="{width}" height="{height}" fill="#ffffff"/>']

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, size=14, anchor="middle", weight="normal",
             fill=INK, rotate=0, italic=False):
        """Text centred vertically on y; a newline starts another line."""
        lines = s.split("\n")
        style = ' font-style="italic"' if italic else ""
        rot = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate else ""
        for i, line in enumerate(lines):
            dy = (i - (len(lines) - 1) / 2) * (size + 2)
            self.add(f'<text x="{x:.1f}" y="{y + dy:.1f}" font-size="{size}" '
                     f'text-anchor="{anchor}" font-weight="{weight}" '
                     f'fill="{fill}" dominant-baseline="middle"{style}{rot}>'
                     f'{escape(line)}</text>')

    def line(self, x1, y1, x2, y2, stroke=INK, width=1.2, dash=None,
             arrow=False):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
                 f'y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width}"{d}/>')
        if arrow:
            self.arrowhead(x1, y1, x2, y2, stroke)

    def arrowhead(self, x1, y1, x2, y2, fill=INK, size=8):
        a = math.atan2(y2 - y1, x2 - x1)
        pts = [(x2, y2)]
        for s in (+1, -1):
            pts.append((x2 - size * math.cos(a + s * 0.4),
                        y2 - size * math.sin(a + s * 0.4)))
        self.add('<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
                 + f'" fill="{fill}"/>')

    def poly(self, pts, stroke=BLUE, width=2.2, fill="none", dash=None,
             closed=False):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        tag = "polygon" if closed else "polyline"
        self.add(f'<{tag} points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
                 + f'" fill="{fill}" stroke="{stroke}" stroke-width="{width}" '
                 f'stroke-linejoin="round"{d}/>')

    def rect(self, x, y, w, h, fill=FILL_GREY, stroke=INK, width=1.0, rx=0,
             dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
                 f'height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{width}"{d}/>')

    def circle(self, x, y, r, fill=INK, stroke="none"):
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" '
                 f'stroke="{stroke}"/>')

    def save(self, path):
        body = "\n".join(self.parts)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" '
                    f'height="{self.h}" viewBox="0 0 {self.w} {self.h}" '
                    f'font-family="{FONT}">\n{body}\n</svg>\n')


class Axes:
    """A plot area on a Fig, mapping data values to px."""

    def __init__(self, fig, x0, y0, x1, y1, xlim, ylim, xlog=False,
                 ylog=False):
        self.f = fig
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.xlim, self.ylim = xlim, ylim
        self.xlog, self.ylog = xlog, ylog

    def _frac(self, v, lim, log):
        if log:
            return (math.log10(v) - math.log10(lim[0])) / (
                math.log10(lim[1]) - math.log10(lim[0]))
        return (v - lim[0]) / (lim[1] - lim[0])

    def X(self, v):
        return self.x0 + self._frac(v, self.xlim, self.xlog) * (self.x1 - self.x0)

    def Y(self, v):
        return self.y1 - self._frac(v, self.ylim, self.ylog) * (self.y1 - self.y0)

    def pts(self, data):
        return [(self.X(x), self.Y(y)) for x, y in data]

    def frame(self, xticks, yticks, xlabel, ylabel, xfmt=str, yfmt=str,
              grid=True, size=13):
        f = self.f
        if grid:
            for t in xticks:
                f.line(self.X(t), self.y0, self.X(t), self.y1, GRID, 1)
            for t in yticks:
                f.line(self.x0, self.Y(t), self.x1, self.Y(t), GRID, 1)
        f.rect(self.x0, self.y0, self.x1 - self.x0, self.y1 - self.y0,
               fill="none", stroke=INK, width=1.2)
        for t in xticks:
            f.line(self.X(t), self.y1, self.X(t), self.y1 + 5)
            f.text(self.X(t), self.y1 + 15, xfmt(t), size=size)
        for t in yticks:
            f.line(self.x0 - 5, self.Y(t), self.x0, self.Y(t))
            f.text(self.x0 - 8, self.Y(t), yfmt(t), size=size, anchor="end")
        if xlabel:
            f.text((self.x0 + self.x1) / 2, self.y1 + 36, xlabel, size=14)
        if ylabel:
            yc = (self.y0 + self.y1) / 2
            f.text(self.x0 - 48, yc, ylabel, size=14, rotate=-90)

    def plot(self, data, **kw):
        self.f.poly(self.pts(data), **kw)

    def hline(self, y, **kw):
        self.f.line(self.x0, self.Y(y), self.x1, self.Y(y), **kw)

    def vline(self, x, **kw):
        self.f.line(self.X(x), self.y0, self.X(x), self.y1, **kw)

    def band(self, ylo, yhi, fill, xlo=None, xhi=None):
        xa = self.x0 if xlo is None else self.X(xlo)
        xb = self.x1 if xhi is None else self.X(xhi)
        self.f.rect(xa, self.Y(yhi), xb - xa, self.Y(ylo) - self.Y(yhi),
                    fill=fill, stroke="none")


def fmt(v):
    """Number without a trailing .0, with a real minus sign."""
    s = f"{v:g}"
    return s.replace("-", "−")
