# /// script
# requires-python = ">=3.10"
# ///
"""Write the full-speed timing figures of the timing page as SVG files:
bit-cell.svg (edge windows and sampling margin), edge-placement.svg
(transmit edges from 125 MHz and 48 MHz clocks) and eop.svg (end of
packet). Run with:

    uv run docs/usb-serial/timing_figs.py

SPDX-License-Identifier: Apache-2.0
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from svgplot import (Axes, Svg, BLUE, ORANGE, GREEN, RED, GREY, INK,  # noqa: E402
                     FILL_BLUE, FILL_ORANGE, FILL_GREEN, FILL_GREY)

HERE = pathlib.Path(__file__).parent / "timing"
TBIT = 1000 / 12            # 83.33 ns


def bit_cell():
    """One bit cell with the sender and receiver edge windows."""
    s = Svg(600, 330)
    a = Axes(s, (175, 40, 580, 260), (-25, TBIT + 25), (0, 4))
    a.frame(xticks=[0, 18.5, TBIT / 2, TBIT - 18.5, TBIT],
            xfmt=lambda v: f"{v:.2f}".rstrip("0").rstrip("."),
            xlabel="time within one bit (ns)", grid=False, yticks=[])
    rows = [(3.4, "sent TDJ1", 3.5, BLUE, FILL_BLUE),
            (2.6, "sent paired TDJ2", 4.0, BLUE, FILL_BLUE),
            (1.8, "accepted TJR1", 18.5, ORANGE, FILL_ORANGE),
            (1.0, "accepted paired TJR2", 9.0, ORANGE, FILL_ORANGE)]
    for y, name, w, col, fill in rows:
        s.text(a.x0 - 8, a.Y(y), f"{name} ± {w:g} ns", size=12,
               anchor="end", fill=col)
        for edge in (0, TBIT):
            s.rect(a.X(edge - w), a.Y(y + 0.25), a.X(edge + w) - a.X(edge - w),
                   a.Y(y - 0.25) - a.Y(y + 0.25), fill=fill, stroke=col)
    for edge in (0, TBIT):
        s.line(a.X(edge), a.y0 - 10, a.X(edge), a.y1, stroke=INK, width=1.6)
        s.text(a.X(edge), a.y0 - 18, "ideal edge", size=11)
    xm = a.X(TBIT / 2)
    s.line(xm, a.y0, xm, a.y1, stroke=GREEN, width=1.6, dash="5 3")
    s.text(xm, a.y0 - 18, "sample at 41.67", size=11, fill=GREEN)
    ym = a.Y(0.35)
    s.line(a.X(18.5), ym, xm, ym, arrow="both", width=1.1)
    s.line(xm, ym, a.X(TBIT - 18.5), ym, arrow="both", width=1.1)
    s.text(xm, ym - 12, "23.2 ns margin on each side of the sample",
           size=11)
    s.text(300, 318, "one bit time = 83.33 ns at 12 Mbit/s", size=12,
           fill=GREY)
    s.save(HERE / "bit-cell.svg")


def edge_placement():
    """Transmit edges on a 125 MHz grid and on a 48 MHz grid."""
    s = Svg(600, 345)
    a = Axes(s, (110, 30, 580, 270), (0, 3 * TBIT + 6), (0, 5))
    a.frame(xticks=[0, TBIT, 2 * TBIT, 250],
            xfmt=lambda v: f"{v:.2f}".rstrip("0").rstrip("."),
            xlabel="time (ns)", grid=False, yticks=[])

    def window(t, y, col):
        s.rect(a.X(t - 3.5), y - 17, a.X(7) - a.X(0), 34, fill=col,
               stroke="none", opacity=0.8)

    # 125 MHz ticks.
    y = a.Y(4.2)
    s.text(a.x0 - 8, y, "125 MHz", size=12, anchor="end")
    t = 0
    while t <= 3 * TBIT + 6:
        s.line(a.X(t), y - 6, a.X(t), y + 6, stroke=INK, width=1)
        t += 8
    # Bits of 10 and 11 periods, each with the window for its end edge.
    y = a.Y(3.1)
    s.text(a.x0 - 8, y, "bits from\n125 MHz", size=12, anchor="end")
    window(TBIT, y, FILL_GREEN)
    window(80 + TBIT, y, "#f4cccc")
    for t0, t1, lab, col in ((0, 80, "10 periods: 80 ns", GREEN),
                             (80, 168, "11 periods: 88 ns", RED)):
        s.rect(a.X(t0), y - 11, a.X(t1) - a.X(t0), 22, fill="#ffffff",
               stroke=col, width=1.6)
        s.text((a.X(t0) + a.X(t1)) / 2, y, lab, size=11, fill=col)
    s.text(a.X(80) - 4, a.Y(2.35), "−3.33 ns: inside", size=11, fill=GREEN,
           anchor="end")
    s.text(a.X(168) + 6, a.Y(2.35), "+4.67 ns: outside", size=11, fill=RED,
           anchor="start")
    # 48 MHz ticks and bits.
    y = a.Y(1.55)
    s.text(a.x0 - 8, y, "48 MHz", size=12, anchor="end")
    for k in range(13):
        tt = k * TBIT / 4
        s.line(a.X(tt), y - 6, a.X(tt), y + 6, stroke=INK, width=1)
    y = a.Y(0.6)
    s.text(a.x0 - 8, y, "bits from\n48 MHz", size=12, anchor="end")
    for k in range(3):
        window((k + 1) * TBIT, y, FILL_GREEN)
        s.rect(a.X(k * TBIT), y - 11, a.X(TBIT) - a.X(0), 22, fill="#ffffff",
               stroke=GREEN, width=1.6)
        s.text(a.X(k * TBIT + TBIT / 2), y, "4 periods: 83.33 ns", size=11,
               fill=GREEN)
    s.text(345, 334, "shaded: previous edge + 83.33 ns ± 3.5 ns (TDJ1)",
           size=11, fill=GREY)
    s.save(HERE / "edge-placement.svg")


def eop():
    """D+ and D- at the end of a packet, with the SE0 timing rules."""
    s = Svg(600, 330)
    x0, x1 = 110, 580
    t_end = 7.0                               # bit times shown
    a = Axes(s, (x0, 50, x1, 230), (0, t_end), (0, 4))

    def trace(y0, levels, col, name):
        pts = []
        for t, v in levels:
            yy = y0 + (0.9 if v else 0)
            if pts:
                pts.append((t, pts[-1][1]))
            pts.append((t, yy))
        pts.append((t_end, pts[-1][1]))
        s.poly(a.P(pts), stroke=col)
        s.text(x0 - 8, a.Y(y0 + 0.45), name, size=13, anchor="end", fill=col)

    # Last data bit K (D+ low, D- high), SE0 for 2 bits, J for one bit,
    # then released: the pull-up holds J (idle).
    trace(2.5, [(0, 0), (2, 0), (4, 1)], BLUE, "D+")
    trace(1.0, [(0, 1), (2, 0), (4, 0)], ORANGE, "D−")
    s.line(a.X(5), a.Y(0.6), a.X(5), 40, stroke=GREY, dash="3 3",
           width=1)
    for t0, t1, lab, fill in ((0, 2, "last bit (K)", FILL_GREY),
                              (2, 4, "SE0: 160–175 ns sent\n(TFEOPT)",
                               FILL_ORANGE),
                              (4, 5, "J, one bit", FILL_BLUE),
                              (5, 7, "released: idle", "#ffffff")):
        s.rect(a.X(t0), 8, a.X(t1) - a.X(t0), 30, fill=fill, stroke=GREY)
        s.text((a.X(t0) + a.X(t1)) / 2, 23, lab, size=11)
    s.text(a.X(1.0), a.Y(0.25), "may be stretched by hubs:\nup to 6 bit times "
           "without a change", size=11, fill=GREY)
    # Receiver rules along the bottom.
    yb = 262
    s.line(a.X(2), yb, a.X(2 + 0.98), yb, arrow="both", width=1.2)
    s.text(a.X(3.0) + 6, yb, "receiver accepts SE0 from 82 ns (TFEOPR)",
           size=11, anchor="start")
    s.text(x0, 292, "During a normal J/K change both lines may be low for up "
           "to 14 ns (TFST),", size=11, anchor="start", fill=RED)
    s.text(x0, 310, "so the SE0 filter must be longer than 14 ns and shorter "
           "than 82 ns.", size=11, anchor="start", fill=RED)
    s.line(x0, 234, x1, 234, stroke=INK, width=1)
    s.text((x0 + x1) / 2, 246, "time (bit times of 83.33 ns, schematic)",
           size=11, fill=GREY)
    s.save(HERE / "eop.svg")


if __name__ == "__main__":
    HERE.mkdir(exist_ok=True)
    bit_cell()
    edge_placement()
    eop()
