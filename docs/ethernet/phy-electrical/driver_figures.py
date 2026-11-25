# /// script
# requires-python = ">=3.10"
# ///
"""Write line-drivers.svg: simplified schematics of a current-mode and a
voltage-mode gigabit line driver, each connected to the transceiver-side
winding of a transformer, as described on line-drivers.rst. Component
values other than the 0.1 uF centre-tap capacitor are not given on the
page, so none are drawn. Run with:

    uv run docs/ethernet/phy-electrical/driver_figures.py

SPDX-License-Identifier: Apache-2.0
"""

import math
import pathlib

from svgplot import Fig, INK, GREY, BLUE, RED, FILL_ORANGE, FILL_GREY

HERE = pathlib.Path(__file__).parent


def resistor_v(f, x, y1, y2, label=None, side=1):
    """A vertical zigzag resistor between y1 and y2."""
    lead = (y2 - y1) * 0.25
    pts = [(x, y1), (x, y1 + lead)]
    n = 6
    h = (y2 - y1 - 2 * lead) / n
    for i in range(n):
        pts.append((x + (5 if i % 2 == 0 else -5), y1 + lead + (i + 0.5) * h))
    pts += [(x, y2 - lead), (x, y2)]
    f.poly(pts, stroke=INK, width=1.4)
    if label:
        f.text(x + side * 9, (y1 + y2) / 2, label, size=11,
               anchor="start" if side > 0 else "end")


def coil_h(f, x1, x2, y, loops=6):
    """A horizontal winding drawn as bumps above the line y."""
    w = (x2 - x1) / loops
    d = f"M{x1:.1f},{y:.1f} "
    for i in range(loops):
        d += f"a{w / 2:.1f},{w / 2:.1f} 0 0 1 {w:.1f},0 "
    f.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.6"/>')


def ground(f, x, y):
    f.line(x, y, x, y + 6)
    for i, w in enumerate((10, 6, 2)):
        f.line(x - w, y + 6 + 3 * i, x + w, y + 6 + 3 * i, width=1.4)


def current_source(f, x, y, r=9):
    f.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffffff" stroke="{INK}" '
          'stroke-width="1.4"/>')
    f.line(x, y + r - 3, x, y - r + 3, width=1.3, arrow=False)
    f.arrowhead(x, y + 2, x, y + r - 2, INK, size=5)


def winding(f, xl, xr, y, tap_label):
    coil_h(f, xl, xr, y)
    f.text((xl + xr) / 2, y - 34, tap_label, size=11, fill=GREY)
    f.text((xl + xr) / 2, y + 14, "winding, transceiver side", size=11,
           fill=GREY)


def current_mode(f, x0):
    xl, xr, xm = x0 + 50, x0 + 190, x0 + 120
    yr, yw = 60, 120
    f.text(x0 + 120, 18, "Current-mode driver", size=14, weight="bold")
    f.line(x0 + 20, yr, x0 + 220, yr, width=2)
    f.text(x0 + 20, yr - 10, "analogue supply", size=11, anchor="start")
    f.line(xm, yr, xm, yw - 10)
    f.circle(xm, yr, 3)
    winding(f, xl, xr, yw, "")
    f.text(xm + 6, yw - 30, "centre tap", size=11, anchor="start", fill=GREY)
    # Wires down to the driver; termination resistors from each wire to the
    # supply.
    for x, xt, s in ((xl, x0 + 26, "+"), (xr, x0 + 214, "−")):
        f.line(x, yw, x, 246 if s == "+" else 256)
        f.line(x, 170, xt, 170)
        f.circle(x, 170, 3)
        resistor_v(f, xt, yr, 170)
        f.circle(xt, yr, 3)
        f.text(x + (8 if s == "+" else -8), 190, f"wire {s}", size=11,
               anchor="start" if s == "+" else "end")
    f.text(x0 + 120, 175, "termination", size=11, fill=GREY)
    # Segmented current cells: each steers its current to one wire. The
    # left leg of each switch goes to wire +, the right leg to wire −.
    cells = [x0 + 80, x0 + 160]
    f.line(xl, 246, cells[1] - 18, 246)
    f.line(cells[0] + 18, 256, xr, 256)
    for xc in cells:
        f.line(xc - 18, 246, xc - 18, 270)
        f.line(xc + 18, 256, xc + 18, 270)
        f.circle(xc - 18, 246, 2.5)
        f.circle(xc + 18, 256, 2.5)
        f.rect(xc - 30, 270, 60, 30, fill=FILL_ORANGE, rx=4)
        f.text(xc, 285, "switch", size=11)
        f.line(xc, 300, xc, 313)
        current_source(f, xc, 322)
        ground(f, xc, 331)
    f.text(x0 + 120, 322, "…", size=16)
    f.text(x0 + 120, 368, "segmented cells, each steering\nits current to "
           "one wire or the other", size=11)


def voltage_mode(f, x0):
    xl, xr, xm = x0 + 50, x0 + 190, x0 + 120
    yw = 120
    f.text(x0 + 120, 18, "Voltage-mode driver", size=14, weight="bold")
    winding(f, xl, xr, yw, "")
    f.text(xm + 6, yw - 30, "centre tap", size=11, anchor="start", fill=GREY)
    # Centre tap to ground through a capacitor.
    f.line(xm, yw - 10, xm, 76)
    f.line(xm - 12, 76, xm + 12, 76, width=2)
    f.line(xm - 12, 70, xm + 12, 70, width=2)
    f.line(xm, 70, xm, 58)
    f.line(xm, 58, xm + 40, 58)
    ground(f, xm + 40, 58)
    f.text(xm - 16, 73, "0.1 µF", size=11, anchor="end")
    # Source resistors, which are also the termination.
    for x, s in ((xl, "+"), (xr, "−")):
        f.line(x, yw, x, 160)
        resistor_v(f, x, 160, 220)
        f.text(x + (8 if s == "+" else -8), 150, f"wire {s}", size=11,
               anchor="start" if s == "+" else "end")
    f.text(x0 + 120, 190, "source resistance\n= termination", size=11,
           fill=GREY)
    # Differential amplifier fed from a DAC.
    f.line(xl, 220, xl, 246)
    f.line(xr, 220, xr, 246)
    f.rect(xl - 14, 246, xr - xl + 28, 46, fill=FILL_ORANGE, rx=4)
    f.text(xm, 262, "differential amplifier", size=11)
    f.text(xm, 278, "input below, outputs above", size=10, fill=GREY)
    f.line(xm, 320, xm, 292, arrow=True)
    f.rect(xm - 34, 320, 68, 26, fill=FILL_GREY, rx=4)
    f.text(xm, 333, "DAC", size=12)
    f.text(x0 + 120, 372, "linear amplifier with a low output\n"
           "impedance; it sets its own common-mode\nvoltage, so no DC "
           "flows through the tap", size=11)


def main():
    f = Fig(480, 430)
    current_mode(f, 0)
    voltage_mode(f, 240)
    f.line(240, 30, 240, 390, stroke="#cccccc")
    f.text(240, 412, "Both: 17 shaped levels, peak distortion below 10 mV "
           "in test mode 4,\nabout 7 bits of linearity", size=12)
    f.save(HERE / "line-drivers.svg")


if __name__ == "__main__":
    main()
