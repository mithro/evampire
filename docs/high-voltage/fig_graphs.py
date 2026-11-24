"""Draw the breakdown graphs for the junctions page.

doping-breakdown.svg  flat-junction breakdown voltage and depletion width
                      against the doping of the lightly doped side.
edge-breakdown.svg    breakdown of cylindrical and spherical edges against
                      their radius, at 1e15 cm^-3.

The equations are those of calc.py sections 1 and 3 (Baliga; Baliga and
Ghandhi), repeated here because calc.py prints as it runs. figures.py
calls this module; it writes no files itself.

SPDX-License-Identifier: Apache-2.0
"""

import math

from svgdraw import (BLUE, DEPL, GREY, INK, polyline, rect, sub, svg, text,
                     line)

SHADE = "#e2f0d9"


def bv_planar(n):
    return 5.34e13 * n ** -0.75


def w_planar_um(n):
    return 2.67e10 * n ** -0.875 * 1e4


def ratio_cyl(x):
    return (0.5 * (x ** 2 + 2 * x ** (6 / 7))
            * math.log(1 + 2 * x ** (-8 / 7)) - x ** (6 / 7))


def ratio_sph(x):
    return (x ** 2 + 2.14 * x ** (6 / 7)
            - (x ** 3 + 3 * x ** (13 / 7)) ** (2 / 3))


class Axes:
    """A plot area with linear or logarithmic axes."""

    def __init__(self, x0, y0, w, h, xr, yr, xlog, ylog):
        self.x0, self.y0, self.w, self.h = x0, y0, w, h
        self.xr, self.yr, self.xlog, self.ylog = xr, yr, xlog, ylog

    @staticmethod
    def _f(v, r, log):
        if log:
            return (math.log10(v) - math.log10(r[0])) / (
                math.log10(r[1]) - math.log10(r[0]))
        return (v - r[0]) / (r[1] - r[0])

    def px(self, x, y):
        return (self.x0 + self.w * self._f(x, self.xr, self.xlog),
                self.y0 + self.h * (1 - self._f(y, self.yr, self.ylog)))

    def frame(self, xticks, yticks, xlabel, ylabel):
        b = [rect(self.x0, self.y0, self.w, self.h, "none")]
        for v, s in xticks:
            x, _ = self.px(v, self.yr[0])
            b.append(line(x, self.y0, x, self.y0 + self.h, stroke="#dddddd",
                          width=1))
            b.append(text(x, self.y0 + self.h + 17, s, size=12))
        for v, s in yticks:
            _, y = self.px(self.xr[0], v)
            b.append(line(self.x0, y, self.x0 + self.w, y, stroke="#dddddd",
                          width=1))
            b.append(text(self.x0 - 6, y + 4, s, anchor="end", size=12))
        b.append(text(self.x0 + self.w / 2, self.y0 + self.h + 38, xlabel,
                      size=13))
        b.append(text(self.x0 - 50, self.y0 + self.h / 2, ylabel, size=13,
                      rotate=-90))
        return b

    def curve(self, f, lo, hi, n=80, **kw):
        pts = []
        for k in range(n + 1):
            if self.xlog:
                v = 10 ** (math.log10(lo) + (math.log10(hi) - math.log10(lo))
                           * k / n)
            else:
                v = lo + (hi - lo) * k / n
            pts.append(self.px(v, f(v)))
        return polyline(pts, **kw)

    def dot(self, x, y, colour):
        px, py = self.px(x, y)
        return (f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{colour}" '
                f'stroke="{INK}" stroke-width="0.8"/>')


EXP = {14: "10¹⁴", 15: "10¹⁵", 16: "10¹⁶", 17: "10¹⁷"}
TABLE = ((1e14, 1690, 150), (1e15, 300, 20), (1e16, 53, 2.7), (1e17, 9, 0.36))


def doping_breakdown():
    w, h = 640, 560
    body = []
    xt = [(10 ** k, s) for k, s in EXP.items()]
    for k, (title, f, yr, yt, ylab, col) in enumerate((
            ("(a) Breakdown voltage of a flat junction", bv_planar, (5, 3000),
             [(10, "10"), (100, "100"), (1000, "1000")],
             sub("V", "B") + "(V)", DEPL),
            ("(b) Depletion width at breakdown", w_planar_um, (0.2, 300),
             [(1, "1"), (10, "10"), (100, "100")],
             sub("W", "B") + "(µm)", BLUE))):
        ax = Axes(90, 40 + k * 270, 520, 190, (1e14, 1e17), yr, True, True)
        body.append(text(20, 26 + k * 270, title, anchor="start", size=14,
                         weight="bold"))
        # The gf180mcu substrate estimate.
        xa, _ = ax.px(1.2e15, yr[1])
        xb, _ = ax.px(5.3e15, yr[1])
        body.append(rect(xa, ax.y0, xb - xa, ax.h, SHADE, stroke="none"))
        body += ax.frame(xt, yt, "doping of the lightly doped side, N "
                         "(cm⁻³)", ylab)
        body.append(text((xa + xb) / 2, ax.y0 + 16, "gf180mcu",
                         size=11))
        body.append(text((xa + xb) / 2, ax.y0 + 30, "estimate",
                         size=11))
        body.append(ax.curve(f, 1e14, 1e17, stroke=col, width=2.2))
        for n, vb, wb in TABLE:
            body.append(ax.dot(n, vb if k == 0 else wb, col))
        if k == 0:
            for v, s, dy, anc in ((57, "57 V, the most on an Ethernet "
                                   "cable", -6, "start"),
                                  (14, "published N-well breakdown, 14 V "
                                   "typical", 16, "start")):
                _, y = ax.px(1e14, v)
                body.append(line(ax.x0, y, ax.x0 + ax.w, y, stroke=GREY,
                                 dash="6 4", width=1.3))
                xt_ = ax.x0 + ax.w - 6 if anc == "end" else ax.x0 + 6
                body.append(text(xt_, y + dy, s, anchor=anc, size=12,
                                 fill=GREY))
            body.append(text(xb + 6, ax.px(1e14, 200)[1], "about 90 V to "
                             "270 V", anchor="start", size=12))
    return svg(w, h, body)


def edge_breakdown():
    w, h = 640, 380
    n = 1e15
    bv, wb = bv_planar(n), w_planar_um(n)
    ax = Axes(90, 30, 520, 290, (0.2, 3.2), (0, 330), False, False)
    body = ax.frame([(x, f"{x:g}") for x in (0.5, 1, 1.5, 2, 2.5, 3)],
                    [(v, str(v)) for v in (0, 50, 100, 150, 200, 250, 300)],
                    "radius of the edge (µm)", "breakdown voltage (V)")
    for v, s, col in ((bv, "flat bottom, 300 V", INK),
                      (14, "published N-well breakdown, 14 V typical",
                       GREY)):
        _, y = ax.px(0.2, v)
        body.append(line(ax.x0, y, ax.x0 + ax.w, y, stroke=col, dash="6 4",
                         width=1.3))
        body.append(text(ax.x0 + ax.w - 6, y - 6, s, anchor="end", size=12,
                         fill=col))
    for f, col, name, rows in (
            (ratio_cyl, DEPL, "straight side (cylinder)",
             ((0.5, 50), (1, 74), (2, 103), (3, 123))),
            (ratio_sph, BLUE, "corner (sphere)",
             ((0.5, 21), (1, 35), (2, 56), (3, 72)))):
        body.append(ax.curve(lambda r: bv * f(r / wb), 0.2, 3.2, stroke=col,
                             width=2.2))
        for r, v in rows:
            body.append(ax.dot(r, v, col))
        x, y = ax.px(3.2, bv * f(3.2 / wb))
        body.append(text(x - 4, y - 10, name, anchor="end", size=13,
                         fill=col))
    body.append(text(ax.x0 + 8, ax.y0 + 54, "substrate doped at 10¹⁵ cm⁻³",
                     anchor="start", size=12))
    return svg(w, h, body)


FIGURES = {"doping-breakdown.svg": doping_breakdown,
           "edge-breakdown.svg": edge_breakdown}
