"""Shared SVG helpers, colours and the Axes class for the magnetics
graphs.

SPDX-License-Identifier: Apache-2.0
"""

import math

INK = "#222222"
GREY = "#7f7f7f"
LIGHT = "#d9d9d9"
BLUE = "#1f4e79"
ORANGE = "#c55a11"
GREEN = "#548235"
RED = "#c00000"
FONT = 'font-family="Helvetica, Arial, sans-serif"'


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" '
            f'height="{h}" viewBox="0 0 {w} {h}" {FONT} font-size="13">\n'
            f'<rect width="{w}" height="{h}" fill="white"/>\n'
            + "\n".join(body) + "\n</svg>\n")


def text(x, y, s, anchor="start", size=13, weight="normal", fill=INK,
         rotate=None):
    r = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}"{r}>'
            f'{s}</text>')


def line(x1, y1, x2, y2, stroke=INK, width=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{width}"{d}/>')


def poly(pts, stroke, width=2.0, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{width}"{d}/>')


def dot(x, y, fill=INK, r=3.5):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"/>'


class Axes:
    """A plot area with linear or log axes, ticks and labels."""

    def __init__(self, left, top, width, height, xr, yr, xlog=False,
                 ylog=False):
        self.l, self.t, self.w, self.h = left, top, width, height
        self.xr, self.yr, self.xlog, self.ylog = xr, yr, xlog, ylog

    def _f(self, v, r, log):
        if log:
            return (math.log10(v) - math.log10(r[0])) / (
                math.log10(r[1]) - math.log10(r[0]))
        return (v - r[0]) / (r[1] - r[0])

    def x(self, v):
        return self.l + self._f(v, self.xr, self.xlog) * self.w

    def y(self, v):
        return self.t + self.h - self._f(v, self.yr, self.ylog) * self.h

    def pts(self, xs, f):
        return [(self.x(v), self.y(f(v))) for v in xs]

    def frame(self, xticks, yticks, xlabel, ylabel, grid=True):
        out = []
        b = self.t + self.h
        for v, lab in xticks:
            if grid:
                out.append(line(self.x(v), self.t, self.x(v), b, LIGHT))
            out.append(line(self.x(v), b, self.x(v), b + 5))
            out.append(text(self.x(v), b + 19, lab, "middle", 12))
        for v, lab in yticks:
            if grid:
                out.append(line(self.l, self.y(v), self.l + self.w,
                                self.y(v), LIGHT))
            out.append(line(self.l - 5, self.y(v), self.l, self.y(v)))
            out.append(text(self.l - 8, self.y(v) + 4, lab, "end", 12))
        out.append(f'<rect x="{self.l}" y="{self.t}" width="{self.w}" '
                   f'height="{self.h}" fill="none" stroke="{INK}"/>')
        out.append(text(self.l + self.w / 2, b + 38, xlabel, "middle"))
        out.append(text(self.l - 46, self.t + self.h / 2, ylabel, "middle",
                        rotate=-90))
        return out


def logspace(a, b, n=300):
    la, lb = math.log10(a), math.log10(b)
    return [10 ** (la + (lb - la) * k / n) for k in range(n + 1)]


def linspace(a, b, n=300):
    return [a + (b - a) * k / n for k in range(n + 1)]
