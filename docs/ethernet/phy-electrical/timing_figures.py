# /// script
# requires-python = ">=3.10"
# ///
"""Write the slot-timing figures of the 100BASE-TX and 1000BASE-T coding
pages, drawn large enough to read on a narrow screen:

* 4b5b-timing.svg: one 4-bit group at 100 Mbit/s and its 5-bit code word
  at 125 MBd, both 40 ns long;
* nyquist.svg: the fastest PAM-5 symbol pattern, alternating every 8 ns
  and repeating every 16 ns, 62.5 MHz;
* frame-delimiters.svg: the code groups around a frame on the wire.

Run with:

    uv run docs/ethernet/phy-electrical/timing_figures.py

SPDX-License-Identifier: Apache-2.0
"""

import pathlib

from svgplot import Fig, INK, GREY, BLUE, FILL_BLUE, FILL_ORANGE, FILL_GREY

HERE = pathlib.Path(__file__).parent
X0, X1 = 110, 466        # time axis, px


def slots(fig, y, t_total, cells, h=28):
    """A row of boxes: cells are (start, length, label, fill) in time
    units of 0..t_total."""
    for start, length, label, fill in cells:
        xa = X0 + start / t_total * (X1 - X0)
        xb = X0 + (start + length) / t_total * (X1 - X0)
        dash = "4 3" if fill is None else None
        fig.rect(xa, y - h / 2, xb - xa, h, fill=fill or "#ffffff", dash=dash)
        if label:
            fig.text((xa + xb) / 2, y, label, size=12)


def axis(fig, y, t_total, ticks, unit):
    fig.line(X0, y, X1, y)
    for t in ticks:
        x = X0 + t / t_total * (X1 - X0)
        fig.line(x, y, x, y + 5)
        fig.text(x, y + 15, f"{t:g}", size=12)
    fig.text((X0 + X1) / 2, y + 34, unit, size=13)


def four_b_five_b():
    fig = Fig(480, 220)
    rows = [("data bits", [(k * 10, 10, f"{k + 1}", FILL_BLUE) for k in range(4)]),
            ("4-bit group", [(0, 40, "4 data bits", FILL_BLUE)]),
            ("code word", [(0, 40, "5-bit code word", FILL_ORANGE)]),
            ("code bits", [(k * 8, 8, f"{k + 1}", FILL_ORANGE) for k in range(5)])]
    for i, (name, cells) in enumerate(rows):
        y = 24 + i * 38
        fig.text(X0 - 8, y, name, size=13, anchor="end")
        slots(fig, y, 40, cells)
    axis(fig, 168, 40, [0, 10, 20, 30, 40], "Time (ns)")
    fig.save(HERE / "4b5b-timing.svg")


def nyquist():
    fig = Fig(480, 200)
    n = 8
    levels = ["+2", "−2"] * (n // 2)
    fig.text(X0 - 8, 30, "symbol", size=13, anchor="end")
    slots(fig, 30, 64, [(8 * k, 8, levels[k], FILL_GREY) for k in range(n)])
    fig.text(X0 - 8, 80, "line", size=13, anchor="end")
    pts = []
    for k in range(n):
        y = 64 if k % 2 == 0 else 96
        pts += [(X0 + 8 * k / 64 * (X1 - X0), y),
                (X0 + 8 * (k + 1) / 64 * (X1 - X0), y)]
    fig.poly(pts, stroke=BLUE, width=2.4)
    xa = X0 + 16 / 64 * (X1 - X0)
    xb = X0 + 32 / 64 * (X1 - X0)
    yb = 118
    fig.line(xa, yb, xb, yb, arrow=True)
    fig.arrowhead(xb, yb, xa, yb)
    fig.text((xa + xb) / 2, yb + 14, "one period: 16 ns, 62.5 MHz", size=12)
    axis(fig, 146, 64, range(0, 65, 8), "Time (ns)")
    fig.save(HERE / "nyquist.svg")


def frame_delimiters():
    fig = Fig(480, 200)
    groups = [("idle", 2, FILL_GREY), ("SSD", 2, FILL_ORANGE),
              ("data", 3, FILL_BLUE), ("CSReset", 2, FILL_ORANGE),
              ("ESD", 2, FILL_ORANGE), ("idle", 2, FILL_GREY)]
    total = sum(g[1] for g in groups)
    cells, levels, t = [], [], 0
    for name, length, fill in groups:
        cells.append((t, length, name, fill))
        if name == "idle":
            levels.append((t, length, "−2, 0, +2", FILL_GREY))
        elif name == "data":
            levels.append((t, length, "all five", FILL_BLUE))
        else:
            levels.append((t, length, "", None))
        t += length
    fig.text(X0 - 8, 30, "code groups", size=13, anchor="end")
    slots(fig, 30, total, cells)
    fig.text(X0 - 8, 72, "levels", size=13, anchor="end")
    slots(fig, 72, total, levels)
    axis(fig, 104, total * 8, range(0, total * 8 + 1, 16), "Time (ns), one "
         "code group per 8 ns")
    fig.text(240, 180, "Dashed: levels not listed on these pages", size=12,
             fill=GREY)
    fig.save(HERE / "frame-delimiters.svg")


if __name__ == "__main__":
    four_b_five_b()
    nyquist()
    frame_delimiters()
