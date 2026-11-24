# /// script
# requires-python = ">=3.10"
# ///
"""Write the converter graphs as SVG files.

Each function draws one graph from the numbers quoted on the converter
pages. Run with:

    uv run docs/power/converters/graphs.py

SPDX-License-Identifier: Apache-2.0
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from svgplot import (Axes, Svg, BLUE, ORANGE, GREEN, RED, GREY, INK,  # noqa: E402
                     FILL_BLUE, FILL_ORANGE, FILL_GREEN, FILL_GREY)

HERE = pathlib.Path(__file__).parent


def boost_gain():
    """Boost voltage gain 1/(1-D) against D, with tab-conv-boost-duty."""
    s = Svg(560, 400)
    a = Axes(s, (75, 20, 530, 340), (0, 1), (0, 12))
    # LM5155 maximum duty-cycle ranges.
    for lo, hi, label in ((0.80, 0.90, "80–90 %"), (0.90, 0.96, "90–96 %")):
        s.rect(a.X(lo), a.Y(12), a.X(hi) - a.X(lo), a.Y(0) - a.Y(12),
               fill=FILL_ORANGE if lo < 0.85 else FILL_GREY, stroke="none")
        s.text((a.X(lo) + a.X(hi)) / 2, a.Y(0.6), label, size=11,
               fill=ORANGE if lo < 0.85 else GREY, rotate=-90)
    s.text(a.X(0.79), a.Y(8.6), "LM5155 maximum\nduty-cycle settings",
           size=12, anchor="end", fill=ORANGE)
    a.frame(xticks=[0, 0.2, 0.4, 0.6, 0.8, 1.0], yticks=[0, 2, 4, 6, 8, 10, 12],
            xlabel="duty cycle D", ylabel="voltage gain Vout / Vin",
            xfmt=lambda v: f"{v:.1f}")
    pts = []
    d = 0.0
    while d <= 1 - 1 / 12 + 1e-9:
        pts.append((d, 1 / (1 - d)))
        d += 0.005
    pts.append((1 - 1 / 12, 12))
    s.poly(a.P(pts), stroke=BLUE)
    points = [(5, 0.907, 10.80), (9, 0.833, 6.00), (15, 0.722, 3.60),
              (20, 0.630, 2.70), (28, 0.481, 1.93), (36, 0.333, 1.50),
              (48, 0.111, 1.12)]
    for vin, dd, g in points:
        x, y = a.X(dd), a.Y(g)
        s.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{ORANGE}"/>')
        if vin == 5:
            s.text(x - 8, y, f"{vin} V in: D = {dd}, ×{g:.2f}", size=12,
                   anchor="end")
        else:
            s.text(x - 6, y - 12, f"{vin} V", size=12, anchor="end")
    s.text(a.X(0.3), a.Y(4.5), "points: fixed USB voltages\nraised to 54 V",
           size=12, fill=GREY)
    s.save(HERE / "boost-gain.svg")


FIGURES = {
    "boost-gain": boost_gain,
}

if __name__ == "__main__":
    for n in sys.argv[1:] or list(FIGURES):
        FIGURES[n]()
