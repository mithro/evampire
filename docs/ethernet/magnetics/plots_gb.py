"""Gigabit-risk graphs for the magnetics pages: wander (PAM-5 levels and
the baseline-wander band) and echo-tail (the low-frequency tail of the
echo against the canceller span). Called from plots.py. Values are those
quoted on gigabit-risk.rst.

SPDX-License-Identifier: Apache-2.0
"""

import math
import random

from plotkit import (INK, GREY, BLUE, ORANGE, GREEN, RED, svg, text, line,
                     poly, dot, Axes)


def wander():
    """Symbols on the five PAM-5 levels with a baseline that drifts with an
    r.m.s. size of 0.071 level steps (C_w = 16 nF), against the decision
    thresholds at half steps."""
    w, h = 640, 340
    n = 120
    a = Axes(80, 20, 520, 250, (0, n), (-2.6, 2.6))
    b = a.frame([(v, str(v)) for v in range(0, n + 1, 20)],
                [(v, f"{v:+d}" if v else "0") for v in range(-2, 3)],
                "symbol number", "received level (level steps)",
                grid=False)
    for v in (-1.5, -0.5, 0.5, 1.5):
        b.append(line(a.l, a.y(v), a.l + a.w, a.y(v), RED, 0.9, "5,4"))
    rng = random.Random(1)
    # A slow drift with an r.m.s. value of 0.071, drawn to scale.
    drift = [0.071 * math.sqrt(2) * math.sin(2 * math.pi * k / 90 + 0.6)
             for k in range(n + 1)]
    for v in range(-2, 3):
        b.append(f'<rect x="{a.l}" y="{a.y(v + 0.071):.1f}" width="{a.w}" '
                 f'height="{a.y(v - 0.071) - a.y(v + 0.071):.1f}" '
                 'fill="#dbe8f5" stroke="none"/>')
        b.append(line(a.l, a.y(v), a.l + a.w, a.y(v), GREY, 0.6))
    for k in range(n):
        lv = rng.choice((-2, -1, 0, 1, 2))
        b.append(dot(a.x(k + 0.5), a.y(lv + drift[k]), BLUE, 2.2))
    b.append(poly(a.pts(range(n + 1), lambda k: drift[int(k)]), ORANGE, 1.6))
    b.append(text(a.x(2), a.y(-2.45), "red dashed: decision thresholds at "
                  "half steps; blue bands: ±0.071 steps of wander", size=11,
                  fill=GREY))
    return svg(w, h, b)


def echo_tail():
    """h_k = (T/tau) exp(-kT/tau) for the four capacitor values, against
    the 120-symbol span of the echo canceller."""
    w, h = 640, 340
    kmax = 1500
    a = Axes(80, 20, 520, 250, (0, kmax), (0, 5.5))
    b = a.frame([(v, str(v)) for v in range(0, kmax + 1, 250)],
                [(v, f"{v:g}") for v in range(0, 6)],
                "symbols after the transmitted symbol",
                "tail, per symbol (× 0.001)")
    b.append(f'<rect x="{a.x(0):.1f}" y="{a.t}" width="'
             f'{a.x(120) - a.x(0):.1f}" height="{a.h}" fill="#e2efda"/>')
    b.append(text(a.x(125), a.y(5.2), "echo canceller span: 120 symbols",
                  size=11, fill=GREEN))
    for r, col in ((200, RED), (412, ORANGE), (875, BLUE), (1250, GREY)):
        ks = range(0, kmax + 1, 5)
        b.append(poly(a.pts(ks, lambda k: 1000 / r * math.exp(-k / r)), col,
                      2.0))
    # Legend in the empty upper right.
    for k, (col, lab) in enumerate(((RED, "C_w = 16 nF: τ/T = 200"),
                                    (ORANGE, "33 nF: τ/T = 412"),
                                    (BLUE, "70 nF: τ/T = 875"),
                                    (GREY, "100 nF: τ/T = 1250"))):
        y = a.y(4.4 - 0.45 * k)
        b.append(line(a.x(850), y - 4, a.x(950), y - 4, col, 2))
        b.append(text(a.x(970), y, lab, size=11, fill=col))
    return svg(w, h, b)
