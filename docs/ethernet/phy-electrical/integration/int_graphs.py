# /// script
# requires-python = ">=3.10"
# ///
"""Write the graphs of the integrated-transceiver pages, each from numbers
that its page gives:

* phase-steps.svg: one 8 ns symbol divided into 64 sampling phases of
  125 ps (clock-recovery.rst);
* jitter.svg: a Gaussian jitter distribution with sigma = 4.9 ps and its
  peak-to-peak width of 69 ps at Q = 7.03 (clock-recovery.rst);
* termination.svg: return loss against termination impedance, with the
  16 dB line and the 73 ohm to 138 ohm window (transmitter.rst);
* adc-reach.svg: ADC effective bits and echo canceller taps against cable
  reach (receiver.rst, signal-processing.rst);
* carry-stages.svg: the 8 ns period split into flip-flop time and carry
  stages for each cell library and corner (cells.rst);
* area-power.svg: the area and power ranges of one port by part
  (area-power.rst).

Run with:

    uv run docs/ethernet/phy-electrical/integration/int_graphs.py

SPDX-License-Identifier: Apache-2.0
"""

import math
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent))

from svgplot import (Axes, Fig, BLUE, RED, GREEN, GREY, INK,  # noqa: E402
                     FILL_ORANGE, FILL_BLUE, FILL_GREEN, fmt)


def sci(v):
    """A power of ten with a superscript exponent."""
    sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    e = round(math.log10(v))
    return "1" if e == 0 else "10" + str(e).translate(sup)


def phase_steps():
    fig = Fig(480, 170)
    x0, x1, y = 30, 450, 90
    fig.rect(x0, y - 30, x1 - x0, 30, fill=FILL_BLUE, stroke=INK)
    fig.text(340, y - 15, "one symbol period, 8 ns", size=13)
    step = (x1 - x0) / 64
    for k in range(65):
        h = 12 if k % 8 == 0 else 6
        fig.line(x0 + k * step, y, x0 + k * step, y + h, width=1)
    k0 = 22
    for k, c in ((k0, BLUE), (k0 + 1, RED)):
        fig.line(x0 + k * step, y - 40, x0 + k * step, y + 14, stroke=c,
                 width=2)
    fig.text(x0 + k0 * step - 4, y - 48, "sampling phase", size=12,
             anchor="end", fill=BLUE)
    fig.text(x0 + (k0 + 1) * step + 4, y - 48, "one step later", size=12,
             anchor="start", fill=RED)
    fig.text((x0 + x1) / 2, y + 34, "64 phases per symbol: steps of "
             "8 ns / 64 = 125 ps", size=13)
    fig.text((x0 + x1) / 2, y + 56, "(256 phases would give steps of "
             "31 ps)", size=12, fill=GREY)
    fig.save(HERE / "phase-steps.svg")


def jitter():
    sigma, q = 4.9, 7.03
    fig = Fig(480, 340)
    ax = Axes(fig, 72, 20, 462, 262, (-45, 45), (1e-14, 1), ylog=True)
    jpp = q * sigma
    ax.band(1e-14, 1, "#f6f6f6", -jpp, jpp)
    ax.frame(range(-40, 41, 20), [1e-14, 1e-12, 1e-9, 1e-6, 1e-3, 1],
             "Time error (ps)", "Relative probability density",
             xfmt=fmt, yfmt=sci)
    pts = []
    for i in range(-450, 451):
        t = i / 10
        p = math.exp(-0.5 * (t / sigma) ** 2) / math.sqrt(2 * math.pi)
        if p > 1e-14:
            pts.append((t, p))
    ax.plot(pts, stroke=BLUE)
    for s in (-1, 1):
        ax.vline(s * jpp, stroke=RED, width=1.6, dash="6 4")
    y = ax.Y(1e-13)
    fig.line(ax.X(-jpp), y, ax.X(jpp), y, stroke=RED, arrow=True)
    fig.arrowhead(ax.X(jpp), y, ax.X(-jpp), y, RED)
    fig.text(ax.X(0), y - 14, "Jpp = 2 × 7.03 × 4.9 ps = 69 ps", size=12,
             fill=RED)
    fig.text(ax.X(0), ax.Y(1e-6), "σ = 4.9 ps", size=12, fill=BLUE)
    fig.text(267, 326, "The 1.4 ns limit is about 20 times Jpp.",
             size=12, fill=GREY)
    fig.save(HERE / "jitter.svg")


def termination():
    fig = Fig(480, 320)
    ax = Axes(fig, 62, 20, 462, 262, (50, 200), (0, 40))
    ax.band(0, 40, "#e2efda", 73, 138)
    ax.band(0, 40, FILL_BLUE, 80, 120)
    ax.frame(range(50, 201, 25), range(0, 41, 10), "Termination impedance "
             "Z (Ω)", "Return loss (dB)")
    pts = []
    for i in range(500, 2001):
        z = i / 10
        g = abs(z - 100) / (z + 100)
        pts.append((z, min(40, -20 * math.log10(g)) if g > 0 else 40))
    ax.plot(pts, stroke=BLUE)
    ax.hline(16, stroke=RED, width=1.6, dash="6 4")
    fig.text(ax.X(185), ax.Y(17.8), "16 dB", size=12, fill=RED)
    for z in (73, 138):
        fig.circle(ax.X(z), ax.Y(16), 4, fill=RED)
        fig.text(ax.X(z) + (-5 if z < 100 else 5), ax.Y(12), f"{z} Ω",
                 size=12, anchor="end" if z < 100 else "start", fill=RED)
    fig.text(ax.X(100), ax.Y(5), "untrimmed\n80 Ω to 120 Ω", size=12)
    fig.text(ax.X(160), ax.Y(30), "window\n73 Ω to 138 Ω", size=12,
             fill=GREEN)
    fig.save(HERE / "termination.svg")


if __name__ == "__main__":
    phase_steps()
    jitter()
    termination()
