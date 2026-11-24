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
* reach.svg: ADC effective bits and filter taps against cable reach
  (receiver.rst, signal-processing.rst);
* energy.svg: switching energy per gate against supply (cells.rst);
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


def reach():
    fig = Fig(480, 550)
    pts_bits = [(100, 7), (50, 5.4), (30, 4.8), (10, 4.2)]
    a = Axes(fig, 62, 30, 462, 220, (0, 100), (3, 8))
    a.frame(range(0, 101, 20), range(3, 9), "Cable reach (m)", "ADC effective bits",
            grid=True)
    fig.text(62, 14, "(a) ADC effective bits needed (estimate)", size=14,
             anchor="start", weight="bold")
    line = [(L, 7 - 18.7 * (1 - L / 100) / 6.02) for L in range(0, 101)]
    a.plot(line, stroke=BLUE)
    a.plot([(L, v - 1) for L, v in line], stroke=BLUE, dash="6 4", width=1.6)
    for L, b in pts_bits:
        fig.circle(a.X(L), a.Y(b), 4, fill=BLUE)
        fig.text(a.X(L) - 6, a.Y(b) - 12, fmt(b), size=12, anchor="end")
    fig.text(a.X(60), a.Y(3.5), "dashed: about one bit fewer with an\n"
             "analogue echo canceller", size=12, fill=GREY)
    b = Axes(fig, 62, 320, 462, 490, (0, 100), (0, 1000))
    b.frame(range(0, 101, 20), range(0, 1001, 200), "Cable reach (m)",
            "Taps, at most")
    fig.text(62, 300, "(b) Filter taps needed (estimate)", size=14,
             anchor="start", weight="bold")
    echo = [(L, 2 * 5.7 * L / 8) for L in range(0, 101)]
    total = [(L, 4 * (2 * 5.7 * L / 8 + 72 + 16 + 12)) for L in range(0, 101)]
    b.plot(total, stroke=RED)
    b.plot(echo, stroke=GREEN)
    for L, e, t in ((100, 143, 972), (50, 71, 684), (30, 43, 572),
                    (10, 14, 456)):
        fig.circle(b.X(L), b.Y(t), 4, fill=RED)
        fig.circle(b.X(L), b.Y(e), 4, fill=GREEN)
        fig.text(b.X(L) - 6, b.Y(t) - 12, str(t), size=12, anchor="end")
        fig.text(b.X(L) - 6, b.Y(e) - 16, str(e), size=12, anchor="end")
    fig.text(b.X(4), b.Y(900), "total taps, 4 pairs", size=12,
             anchor="start", fill=RED)
    fig.text(b.X(4), b.Y(260), "echo taps, one pair", size=12,
             anchor="start", fill=GREEN)
    fig.save(HERE / "reach.svg")


TIMING = [  # library and corner, flip-flop ns, carry ns, stages (page)
    ("fd_sc 7T, typ 3.3 V", 1.58, 1.02, "6.3"),
    ("fd_sc 7T, slow 3.0 V", 3.23, 2.06, "2.3"),
    ("fd_sc 7T, typ 1.8 V", 4.19, 2.70, "1.4"),
    ("fd_sc 7T, slow 1.62 V", 10.58, 6.80, "0"),
    ("fd_sc 9T, typ 3.3 V", 1.20, 0.85, "8.0"),
    ("fd_sc 9T, slow 3.0 V", 2.34, 1.66, "3.4"),
    ("fd_sc 9T, slow 1.62 V", 6.78, 5.50, "0.2"),
    ("OSU 9T, typ 3.3 V", 1.40, 0.32, "21"),
]


def carry_stages():
    fig = Fig(480, 440)
    x0, x1 = 150, 462
    ax = Axes(fig, x0, 20, x1, 340, (0, 11), (0, len(TIMING)))
    ax.frame(range(0, 12), [], "Time (ns)", None, grid=True)
    ax.vline(8, stroke=RED, width=2)
    fig.text(ax.X(8) + 4, 12, "8 ns", size=12, anchor="start", fill=RED)
    for i, (name, ff, carry, stages) in enumerate(TIMING):
        yc = ax.Y(len(TIMING) - i - 0.5)
        fig.text(x0 - 6, yc, name, size=12, anchor="end")
        fig.rect(ax.X(0), yc - 10, ax.X(ff) - ax.X(0), 20, fill="#9aa5b1",
                 stroke="none")
        t = ff
        while t + carry <= 8 + 1e-9:
            fig.rect(ax.X(t), yc - 10, ax.X(t + carry) - ax.X(t), 20,
                     fill=FILL_ORANGE, stroke=INK, width=0.6)
            t += carry
        if ff >= 8:
            fig.text(ax.X(min(ff, 11)) - 4, yc, "flip-flop alone > 8 ns",
                     size=11, anchor="end", fill="#ffffff")
        else:
            fig.text(ax.X(8) + 6, yc, stages, size=12, anchor="start")
    fig.rect(x0 - 130, 392, 16, 12, fill="#9aa5b1", stroke="none")
    fig.text(x0 - 108, 398, "flip-flop, clock-to-output plus setup",
             size=12, anchor="start")
    fig.rect(x0 - 130, 414, 16, 12, fill=FILL_ORANGE, stroke=INK, width=0.6)
    fig.text(x0 - 108, 420, "one full-adder carry stage; number of stages "
             "in 8 ns at right", size=12, anchor="start")
    fig.save(HERE / "carry-stages.svg")


def energy():
    fig = Fig(480, 320)
    ax = Axes(fig, 62, 20, 462, 262, (0, 4), (0, 200))
    ax.frame([0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4], range(0, 201, 50), "Supply voltage V (V)",
             "Energy per gate (fJ)")
    c = 3 * 4.70
    ax.plot([(v / 100, c * (v / 100) ** 2) for v in range(0, 377)], stroke=BLUE)
    for v, e in ((1.8, 41.6), (3.3, 154)):
        fig.circle(ax.X(v), ax.Y(e), 4.5, fill=RED)
        fig.text(ax.X(v) - 8, ax.Y(e) - 12, f"{fmt(e)} fJ at {v} V", size=12,
                 anchor="end", fill=RED)
    fig.text(ax.X(3.1), ax.Y(60), "E = 3 × 4.70 fF × V²\n(the 1.8 V point "
             "uses\n4.275 fF, so lies slightly\nbelow the curve)", size=12)
    fig.save(HERE / "energy.svg")


PARTS = [  # part, area lo, hi (mm2), power lo, hi (W)
    ("4 ADCs", 2.1, 4.1, 0.088, 0.48),
    ("4 DACs and drivers", 0.52, 0.64, 0.096, 0.15),
    ("PLL and interpolator", 0.065, 0.065, 0.004, 0.004),
    ("Signal processing, 3.3 V", 3.9, 8.1, 0.48, 1.5),
    ("Total at 3.3 V", 6.6, 12.8, 0.67, 2.2),
]


def area_power():
    fig = Fig(480, 440)
    for k, (title, lim, ticks, lo_i, hi_i, unit) in enumerate((
            ("Area (mm²)", (0, 18), range(0, 19, 3), 1, 2, "mm²"),
            ("Power (W)", (0, 3), [0, 0.5, 1, 1.5, 2, 2.5, 3], 3, 4, "W"))):
        y0 = 30 + k * 200
        ax = Axes(fig, 170, y0, 462, y0 + 140, lim, (0, len(PARTS)))
        ax.frame(ticks, [], title, None, xfmt=fmt, grid=True)
        for i, row in enumerate(PARTS):
            yc = ax.Y(len(PARTS) - i - 0.5)
            lo, hi = row[lo_i], row[hi_i]
            colour = RED if i == len(PARTS) - 1 else BLUE
            if hi > lo:
                fig.rect(ax.X(lo), yc - 7, ax.X(hi) - ax.X(lo), 14,
                         fill=colour, stroke="none")
            else:
                fig.circle(ax.X(lo), yc, 4, fill=colour)
            fig.text(164, yc, row[0], size=12, anchor="end")
            fig.text(ax.X(hi) + 6, yc, f"{fmt(lo)} to {fmt(hi)}"
                     if hi > lo else fmt(lo), size=11, anchor="start")
    fig.text(240, 430, "Bars span the range of the reference examples "
             "and assumptions", size=12, fill=GREY)
    fig.save(HERE / "area-power.svg")


if __name__ == "__main__":
    phase_steps()
    jitter()
    termination()
    reach()
    carry_stages()
    energy()
    area_power()
