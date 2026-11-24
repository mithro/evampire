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


def bode():
    """Schematic loop gain: magnitude and phase against frequency."""
    import cmath
    import math
    fc, fp = 25e3, 25e3 / math.tan(math.radians(35))  # 55 degree margin

    def loop(f):
        s = 1j * f
        return 1 / (s / fc) / (1 + s / fp) * abs(1 + 1j * fc / fp)

    fs = [10 ** (2 + k * 0.01) for k in range(401)]       # 100 Hz to 1 MHz
    mag = [20 * math.log10(abs(loop(f))) for f in fs]
    ph = [math.degrees(cmath.phase(loop(f))) for f in fs]
    s = Svg(560, 470)
    am = Axes(s, (80, 20, 530, 200), (1e2, 1e6), (-40, 60), xlog=True)
    ap = Axes(s, (80, 250, 530, 400), (1e2, 1e6), (-180, 0), xlog=True)
    for ax in (am, ap):
        s.rect(ax.X(12.5e3), ax.y0, ax.X(50e3) - ax.X(12.5e3), ax.y1 - ax.y0,
               fill=FILL_GREEN, stroke="none")
        s.line(ax.X(250e3), ax.y0, ax.X(250e3), ax.y1, stroke=GREY,
               dash="4 3")
    ticks = [1e2, 1e3, 1e4, 1e5, 1e6]
    lab = {1e2: "100 Hz", 1e3: "1 kHz", 1e4: "10 kHz", 1e5: "100 kHz",
           1e6: "1 MHz"}
    am.frame(xticks=ticks, yticks=[-40, -20, 0, 20, 40, 60],
             ylabel="loop gain (dB)", xfmt=lambda v: lab[v])
    ap.frame(xticks=ticks, yticks=[-180, -135, -90, -45, 0],
             ylabel="phase (°)", xfmt=lambda v: lab[v],
             xlabel="frequency (log scale)")
    s.line(am.X(1e2), am.Y(0), am.X(1e6), am.Y(0), stroke=INK, width=1.4)
    s.poly(am.P([(f, m) for f, m in zip(fs, mag) if m >= -40]), stroke=BLUE)
    s.poly(ap.P(list(zip(fs, ph))), stroke=BLUE)
    # Crossover and phase margin.
    for ax in (am, ap):
        s.line(ax.X(fc), ax.y0, ax.X(fc), ax.y1, stroke=ORANGE, width=1.2,
               dash="2 2")
    s.add(f'<circle cx="{am.X(fc):.1f}" cy="{am.Y(0):.1f}" r="4" '
          f'fill="{ORANGE}"/>')
    s.text(am.X(fc) - 8, am.Y(0) + 14, "crossover: gain = 1 (0 dB)", size=12,
           anchor="end", fill=ORANGE)
    x = ap.X(fc) - 10
    s.line(x, ap.Y(-180), x, ap.Y(-125), arrow="both", width=1.2)
    s.text(x - 6, ap.Y(-158), "phase margin 55°", size=12, anchor="end")
    s.text((am.X(12.5e3) + am.X(50e3)) / 2, am.y0 + 12, "fsw/20 to fsw/5",
           size=11, fill=GREEN)
    s.text(am.X(250e3) + 4, am.Y(45), "fsw\n250 kHz", size=11,
           anchor="start", fill=GREY)
    s.text(ap.X(600), ap.Y(-120), "a phase of −180° at crossover\nwould oscillate", size=12, fill=RED)
    s.save(HERE / "bode.svg")


def ranges():
    """Voltage ranges at each kind of port (tab-conv-overlap)."""
    rows = [
        ("Powered device input", 37, 57, BLUE),
        ("Power sourcing equipment\noutput, Type 1", 44, 57, ORANGE),
        ("Power sourcing equipment\noutput, Types 2 and 3", 50, 57, ORANGE),
        ("Power sourcing equipment\noutput, Type 4", 52, 57, ORANGE),
        ("USB standard power range", 5, 21.5, GREEN),
        ("USB extended power range,\n48 V fixed supply", 45.6, 50.9, GREEN),
        ("USB extended power range,\nadjustable", 15, 50.9, GREEN),
    ]
    h = 42
    top = 40
    s = Svg(600, top + h * len(rows) + 60)
    a = Axes(s, (215, top, 580, top + h * len(rows)), (0, 60), (0, 1))
    # Overlap 1: the shared Power over Ethernet band.
    s.rect(a.X(44), a.y0, a.X(57) - a.X(44), a.y1 - a.y0, fill=FILL_GREY,
           stroke="none")
    a.frame(xticks=range(0, 61, 10), xlabel="voltage (V)", grid=True)
    fills = {BLUE: FILL_BLUE, ORANGE: FILL_ORANGE, GREEN: FILL_GREEN}
    for i, (name, lo, hi, col) in enumerate(rows):
        yc = top + h * i + h / 2
        s.rect(a.X(lo), yc - 11, a.X(hi) - a.X(lo), 22, fill=fills[col],
               stroke=col, width=1.5)
        s.text(a.x0 - 8, yc, name, size=12, anchor="end")
        s.text(a.X(lo) - 4, yc, f"{lo:g}", size=11, anchor="end", fill=GREY)
        s.text(a.X(hi) + 4, yc, f"{hi:g}", size=11, anchor="start", fill=GREY)

    def mark(n, x, y):
        s.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="#ffffff" '
              f'stroke="{INK}" stroke-width="1.2"/>')
        s.text(x, y + 1, str(n), size=12, weight="bold")

    mark(1, a.X(50.5), top - 14)
    s.text(a.X(44) - 14, top - 14, "shared band 44–57 V", size=11,
           anchor="end", fill=GREY)
    y48 = top + h * 5 + h / 2
    mark(2, a.X(45.6) - 40, y48)
    yad = top + h * 6 + h / 2
    mark(3, a.X(50.9) + 46, yad)
    ysp = top + h * 4 + h / 2
    mark(4, a.X(30), ysp)
    s.text(a.X(30) + 14, ysp, "below every Power\nover Ethernet voltage",
           size=11, anchor="start", fill=GREY)
    s.save(HERE / "ranges.svg")


def pse_template():
    """Times a power sourcing equipment port must meet in current limit."""
    s = Svg(600, 440)
    a = Axes(s, (80, 30, 570, 300), (1e-6, 1), (0.5, 100), xlog=True,
             ylog=True)
    s.rect(a.X(50e-3), a.y0, a.X(75e-3) - a.X(50e-3), a.y1 - a.y0,
           fill=FILL_ORANGE, stroke="none")
    labels = {1e-6: "1 µs", 1e-5: "10 µs", 1e-4: "100 µs", 1e-3: "1 ms",
              1e-2: "10 ms", 1e-1: "100 ms", 1: "1 s"}
    a.frame(xticks=list(labels), yticks=[0.5, 1, 2, 5, 10, 20, 50, 100],
            xfmt=lambda v: labels[v], yfmt=lambda v: f"{v:g}",
            ylabel="current (A, log scale)", xlabel="time (log scale)")
    s.poly(a.P([(1e-6, 50), (1e-5, 50)]), stroke=RED)
    s.poly(a.P([(1e-5, 50), (8.2e-3, 1.75)]), stroke=RED, dash="6 4",
           width=1.6)
    s.poly(a.P([(8.2e-3, 1.75), (75e-3, 1.75)]), stroke=RED)
    for x, y in ((1e-5, 50), (8.2e-3, 1.75)):
        s.add(f'<circle cx="{a.X(x):.1f}" cy="{a.Y(y):.1f}" r="4" '
              f'fill="{RED}"/>')
    s.text(a.X(1e-5) + 8, a.Y(50) - 12, "50 A up to 10 µs", size=12,
           anchor="start", fill=RED)
    s.text(a.X(8.2e-3) - 8, a.Y(1.75) + 14, "1.75 A by 8.2 ms", size=12,
           anchor="end", fill=RED)
    s.text(a.X(3e-4), a.Y(12), "shape between these\npoints: see the source",
           size=11, fill=GREY, anchor="start")
    s.text(a.X(1e-5), a.Y(1.0), "port current must stay below the red line",
           size=12, anchor="start")
    s.text((a.X(50e-3) + a.X(75e-3)) / 2, a.y0 + 22, "overload:\nremove\n50–75 ms",
           size=11, fill=ORANGE)
    # Hold and removal times in current limit, one row per type.
    for yb, typ, hold in ((370, "Type 3", 10e-3), (395, "Type 4", 6e-3)):
        s.text(a.x0 - 8, yb, typ, size=11, anchor="end")
        s.line(a.X(1e-6), yb, a.X(hold), yb, stroke=GREEN, width=5)
        s.line(a.X(hold), yb, a.X(75e-3), yb, stroke=GREY, width=1.5)
        s.line(a.X(75e-3), yb - 8, a.X(75e-3), yb + 8, stroke=RED, width=2.5)
        s.text(a.X(hold) - 4, yb - 11, f"{hold * 1e3:g} ms", size=11,
               anchor="end", fill=GREEN)
    s.text(a.X(75e-3) + 6, 382, "power removed\nby 75 ms", size=11,
           anchor="start", fill=RED)
    s.text(a.x0, 425, "In current limit, from the start of the fault, power "
           "must stay on (green), then be removed by 75 ms.", size=11,
           anchor="start", fill=GREY)
    s.save(HERE / "pse-template.svg")


def start_timeline():
    """Hold-capacitor voltage through a powered-device start-up."""
    s = Svg(600, 330)
    a = Axes(s, (70, 30, 570, 250), (0, 10), (0, 11))
    s.rect(a.x0, a.Y(9.3), a.x1 - a.x0, a.Y(8.65) - a.Y(9.3), fill=FILL_ORANGE,
           stroke="none")
    a.frame(yticks=[0, 3, 6, 9], ylabel="hold capacitor voltage (V)",
            xlabel="time (schematic, not to scale)", grid=False)
    s.text(a.x0 + 6, a.Y(9.3) - 9, "turn-on threshold 8.65 V to 9.3 V",
           size=11, anchor="start", fill=ORANGE)
    pts = [(0, 0), (1.5, 0), (4.0, 9.0), (7.5, 6.0), (8.0, 6.2),
           (8.4, 10.0), (10, 10.0)]
    s.poly(a.P(pts), stroke=BLUE)
    phases = [(0, 1.5, "inrush:\nconverter\nheld off"),
              (1.5, 4.0, "current source\ncharges Chold"),
              (4.0, 7.5, "source off; converter\nstarts, 800 µs\nsoft start"),
              (7.5, 10, "winding or\noutput takes\nover")]
    for t0, t1, lab in phases:
        s.line(a.X(t1), a.y0, a.X(t1), a.y1, stroke=GREY, dash="3 3", width=1)
        xc = a.X(3.15) if t0 == 1.5 else (a.X(t0) + a.X(t1)) / 2
        s.text(xc, a.Y(1.3), lab, size=11, fill=INK)
    x = a.X(7.5) + 10
    s.line(x, a.Y(9.0), x, a.Y(6.0), arrow="both", width=1.1)
    s.line(a.X(4.0), a.Y(9.0), x + 4, a.Y(9.0), stroke=GREY, width=1,
           dash="2 2")
    s.text(a.X(5.75), a.Y(4.3), "droop smaller than the\n3.3 V to 3.7 V "
           "hysteresis", size=11, fill=RED)
    s.save(HERE / "start-timeline.svg")


FIGURES = {
    "boost-gain": boost_gain,
    "bode": bode,
    "ranges": ranges,
    "pse-template": pse_template,
    "start-timeline": start_timeline,
}

if __name__ == "__main__":
    for n in sys.argv[1:] or list(FIGURES):
        FIGURES[n]()
