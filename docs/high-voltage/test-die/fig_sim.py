"""Draw the method figures of the predictions page.

hvt-sim-section.svg   where the two simulated sections are cut, and the
                      mesh of one.
hvt-ionisation.svg    field, ionisation coefficients and ionisation
                      integral of a one-sided abrupt junction (computed).
hvt-assumptions.svg   where the P-well lies under each assumption.

figures.py calls this module; it writes no files itself.

SPDX-License-Identifier: Apache-2.0
"""

import physics as ph
import tdkit
from tdkit import PWELL, Section, plan
from fig_graphs import Axes
from svgdraw import (ARROW, BLUE, DEPL, GREY, line, polyline, rect, svg,
                     text)

STRUCTS, MAN = tdkit.load()


def sim_section():
    w, h = 640, 560
    p = STRUCTS["NT20"]
    b = [ARROW, text(20, 24, "(a) The two sections simulated for each "
                     "structure, on NT20 in plan view", anchor="start",
                     weight="bold")]
    cx, cy, s = 150, 150, 2.6
    b += plan(p, cx, cy, s)
    far = (p["half"] + p["term"] + p["ncomp_w"] + 4) * s
    b.append(line(cx, cy, cx + far, cy, stroke=DEPL, width=2.2))
    d = far * 0.7071
    b.append(line(cx, cy, cx + d, cy - d, stroke=BLUE, width=2.2))
    b.append(text(cx + far + 8, cy - 4, "straight edge: a flat section, the",
                  anchor="start", size=12, fill=DEPL))
    b.append(text(cx + far + 8, cy + 12, "same at every point along the "
                  "side", anchor="start", size=12, fill=DEPL))
    b.append(text(cx + d + 8, cy - d - 10, "corner: the same section "
                  "rotated about the", anchor="start", size=12, fill=BLUE))
    b.append(text(cx + d + 8, cy - d + 6, "centre of the corner arc",
                  anchor="start", size=12, fill=BLUE))
    y0 = 400
    b.append(text(20, 296, "(b) The section and its mesh: fine at the "
                  "surface and at every drawn edge", anchor="start",
                  weight="bold"))
    sec = Section(p, 30, y0, 580)
    b += sec.silicon() + sec.metal(False)
    xs, x = [], sec.left
    while x < sec.right:
        near = min(abs(x - e) for e in (0, -2, -4, 20, 22))
        x += 0.25 + min(near, 4.0) * 0.22
        xs.append(x)
    for x in xs[:-1]:
        b.append(line(sec.x(x), y0, sec.x(x), y0 + sec.DEPTH,
                      stroke="#555555", width=0.4))
    y = 0.0
    while y < sec.DEPTH:
        y += 2.5 + y * 0.16
        if y < sec.DEPTH:
            b.append(line(sec.x0, y0 + y, sec.x0 + sec.wpx, y0 + y,
                          stroke="#555555", width=0.4))
    b.append(line(sec.x0, y0 - 70, sec.x0, y0 + sec.DEPTH + 8, stroke=DEPL,
                  dash="6 3", width=1.6))
    b.append(text(sec.x0 + 6, y0 - 60, "symmetry plane inside the well",
                  anchor="start", size=12, fill=DEPL))
    b.append(text(sec.x(-3), y0 - 42, "+V", size=12, weight="bold"))
    b += sec.dim(0, p["term"], "termination zone as drawn")
    return svg(w, h, b)


def ionisation():
    n = 1e16
    bv = ph.breakdown_abrupt(n)
    wd = ph.depletion_width(n, bv)
    emax = ph.Q * n * wd / ph.EPS
    w, h = 640, 770
    b = []
    um = wd * 1e4
    ax = Axes(90, 50, 520, 150, (0, 3.5), (0, 5), False, False)
    b.append(text(20, 30, f"(a) Field at breakdown, {bv:.0f} V: a triangle "
                  f"{um:.2f} µm wide", anchor="start", weight="bold"))
    b += ax.frame([(v, str(v)) for v in (0, 1, 2, 3)],
                  [(v, str(v)) for v in (0, 1, 2, 3, 4, 5)],
                  "distance from the P-side edge of the depletion region "
                  "(µm)", "E (10⁵ V/cm)")
    b.append(polyline([ax.px(0, 0), ax.px(um, emax / 1e5), ax.px(um, 0)],
                      stroke=DEPL, width=2.4))
    b.append(text(*ax.px(um + 0.04, emax / 1e5 - 0.3), "junction",
                  anchor="start", size=12))
    ax2 = Axes(90, 300, 520, 150, (0, 3.5), (0, 4), False, False)
    b.append(text(20, 280, "(b) Ionisation coefficients along the same "
                  "line", anchor="start", weight="bold"))
    b += ax2.frame([(v, str(v)) for v in (0, 1, 2, 3)],
                   [(v, str(v)) for v in (0, 1, 2, 3, 4)],
                   "distance (µm)", "α (per µm)")
    for f, col, name, yy in ((ph.alpha_n, DEPL, "electrons, αₙ", 3.3),
                             (ph.alpha_p, BLUE, "holes, αₚ", 0.6)):
        b.append(ax2.curve(lambda x, f=f: f(ph.Q * n * x * 1e-4 / ph.EPS)
                           * 1e-4, 0.001, um, n=120, stroke=col, width=2.4))
        b.append(text(*ax2.px(um + 0.04, yy), name, anchor="start", size=12,
                      fill=col))
    ax3 = Axes(90, 550, 520, 150, (0, 70), (0, 1.4), False, False)
    b.append(text(20, 530, "(c) Ionisation integral against reverse "
                  "voltage", anchor="start", weight="bold"))
    b += ax3.frame([(v, str(v)) for v in range(0, 71, 10)],
                   [(v, f"{v:g}") for v in (0, 0.5, 1.0)],
                   "reverse voltage (V)", "integral")
    b.append(ax3.curve(lambda v: ph.integral_abrupt(n, v, 600), 1, 70,
                       n=70, stroke=DEPL, width=2.4))
    _, y1 = ax3.px(0, 1)
    b.append(line(ax3.x0, y1, ax3.x0 + ax3.w, y1, stroke=GREY, dash="6 4",
                  width=1.2))
    b.append(text(ax3.x0 + 8, y1 - 6, "breakdown: the integral reaches 1",
                  anchor="start", size=12))
    b.append(ax3.dot(bv, 1.0, DEPL))
    b.append(text(*ax3.px(bv - 1.5, 1.12), f"{bv:.0f} V", anchor="end",
                  size=12, weight="bold"))
    b.append(text(w - 30, 754, "one-sided abrupt junction, 10¹⁶ cm⁻³",
                  anchor="end", size=12, fill=GREY))
    return svg(w, h, b)


def assumptions():
    rows = [("NT20", "assumption A: generated P-well up to the well edge",
             [(0, 25, "generated P-well")]),
            ("NA2", "assumption A with NAT: P-well in the strip beside "
             "the well", [(0, 2, ""), (19.5, 25, "")]),
            ("NA2", "assumption An: as A, but no P-well in the strip",
             [(19.5, 25, "")]),
            ("DAo1", "assumption A: NAT overlaps the deep N-well, so no "
             "strip exists", [(19.5, 25, "")]),
            ("NT20", "assumption B: no P-well unless the layout draws one",
             [])]
    w, h = 640, 60 + 205 * len(rows)
    b = [ARROW, text(20, 24, "Where the P-well lies under each assumption",
                     anchor="start", weight="bold")]
    for k, (name, caption, spans) in enumerate(rows):
        y0 = 110 + k * 205
        p = STRUCTS[name]
        sec = Section(p, 30, y0, 580)
        b.append(text(30, y0 - 54, f"{name}, {caption}", anchor="start"))
        b += sec.silicon(spans) + sec.nat() + sec.metal(False)
    b.append(rect(30, h - 22, 16, 12, PWELL))
    b.append(text(52, h - 11, "P-well that the foundry generates",
                  anchor="start", size=12))
    return svg(w, h, b)


FIGURES = {"hvt-sim-section.svg": sim_section,
           "hvt-ionisation.svg": ionisation,
           "hvt-assumptions.svg": assumptions}
