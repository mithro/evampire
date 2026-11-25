# /// script
# requires-python = ">=3.10"
# ///
"""Write the figures of the "External power stage control" page as SVG
files: PWM edge placement, fault times and the start-up timeline.

Run with:

    uv run docs/power/converters/fv_figures.py

SPDX-License-Identifier: Apache-2.0
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from svgplot import (Axes, Svg, square, BLUE, ORANGE, GREEN, RED,  # noqa: E402
                     GREY, INK, FILL_BLUE, FILL_ORANGE, FILL_GREEN, FILL_GREY)

HERE = pathlib.Path(__file__).parent


def pwm_resolution():
    """Edge placement of a counter, a delay line and dithering."""
    fs = 15
    s = Svg(480, 470)
    tr = (0, 48)
    x0, x1 = 125, 470
    ideal = 37.4
    rows = []
    ck = Axes(s, (x0, 28, x1, 52), tr, (0, 1))
    pts = []
    for k in range(6):
        pts += [(8 * k, 0), (8 * k, 1), (8 * k + 4, 1), (8 * k + 4, 0)]
    pts.append((48, 0))
    s.poly(ck.P(pts), stroke=GREY, width=1.4)
    s.text(x0 - 8, 40, "125 MHz", size=fs, anchor="end")
    for ax_y, name, edge, col in ((80, "ideal", ideal, GREEN),
                                  (135, "counter", 40, RED),
                                  (190, "counter and\ndelay line", 37, BLUE)):
        ax = Axes(s, (x0, ax_y, x1, ax_y + 26), tr, (0, 1))
        square(s, ax, [(0, edge)], 0, 1, stroke=col)
        s.text(x0 - 8, ax_y + 13, name, size=fs, anchor="end")
        rows.append((ax, edge, col))
    for ax, edge, col in rows:
        err = f"{edge - ideal:+.1f}".replace("-", "−")
        lab = "37.4 ns" if edge == ideal else f"{edge:g} ns ({err})"
        s.text(ax.X(edge) - 4, ax.y0 - 10, lab, size=fs - 1, fill=col,
               anchor="end")
    # Delay-line taps inside the clock period 32..40 ns.
    for k in range(9):
        x = rows[2][0].X(32 + k)
        s.line(x, 228, x, 238, stroke=BLUE, width=1.2)
    s.text(rows[2][0].X(36), 252, "taps 1 ns apart", size=fs - 1, fill=BLUE)
    # Dithering: two periods of 40 ns and one of 32 ns average 37.33 ns.
    s.text(x0 - 8, 318, "dithering,\nperiods\n1, 2, 3", size=fs, anchor="end")
    for y0, edge in ((280, 40), (310, 40), (340, 32)):
        ax = Axes(s, (x0, y0, x1, y0 + 22), tr, (0, 1))
        square(s, ax, [(0, edge)], 0, 1, stroke=ORANGE)
    s.text(240, 392, "40 ns, 40 ns, 32 ns: 37.33 ns on\naverage (−0.07 ns)",
           size=fs - 1, fill=ORANGE)
    for k in range(7):
        x = ck.X(8 * k)
        s.line(x, 58, x, 365, stroke="#dddddd", width=1, dash="2 3")
    s.text(240, 446, "time (ns), one 8 ns clock period\nper grid line",
           size=fs - 1, fill=GREY)
    s.save(HERE / "pwm-resolution.svg")


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
    s.text(a.X(4.15), a.Y(10.3), "turn-on threshold\n8.65 V to 9.3 V",
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


def runaway():
    """Inductor current rise with 57 V across 47 µH, against time."""
    s = Svg(560, 360)
    a = Axes(s, (80, 20, 530, 290), (1e-8, 2e-5), (0.01, 30), xlog=True,
             ylog=True)
    labels = {1e-8: "10 ns", 1e-7: "100 ns", 1e-6: "1 µs", 1e-5: "10 µs"}
    a.frame(xticks=list(labels), yticks=[0.01, 0.1, 1, 10],
            xfmt=lambda v: labels[v], yfmt=lambda v: f"{v:g}",
            xlabel="time after the current limit is passed (log scale)",
            ylabel="current rise (A, log scale)")
    rate = 57 / 47e-6
    s.poly(a.P([(1e-8, rate * 1e-8), (2e-5, rate * 2e-5)]), stroke=BLUE)
    for t, txt in ((1e-7, "0.12 A at 100 ns"), (1e-6, "1.21 A at 1 µs"),
                   (1e-5, "12.1 A at 10 µs")):
        s.add(f'<circle cx="{a.X(t):.1f}" cy="{a.Y(rate * t):.1f}" r="4" '
              f'fill="{BLUE}"/>')
        if t < 5e-6:
            s.text(a.X(t) + 8, a.Y(rate * t) + 12, txt, size=11,
                   anchor="start")
        else:
            s.text(a.X(t) - 8, a.Y(rate * t) - 12, txt, size=11,
                   anchor="end")
    s.line(a.x0, a.Y(1), a.X(0.82e-6), a.Y(1), stroke=RED, dash="5 3")
    s.line(a.X(0.82e-6), a.Y(1), a.X(0.82e-6), a.y1, stroke=RED, dash="5 3")
    s.text(a.X(0.82e-6) - 6, a.Y(0.03), "1 A margin\nreached at\n0.82 µs",
           size=11, fill=RED, anchor="end")
    s.text(a.X(1e-8) + 6, a.Y(15), "1.21 A/µs: 57 V across 47 µH", size=11,
           anchor="start", fill=BLUE)
    s.save(HERE / "runaway.svg")


FIGURES = {
    "pwm-resolution": pwm_resolution,
    "pse-template": pse_template,
    "start-timeline": start_timeline,
    "runaway": runaway,
}

if __name__ == "__main__":
    for n in sys.argv[1:] or list(FIGURES):
        FIGURES[n]()
