# /// script
# requires-python = ">=3.10"
# ///
"""Write the 1000BASE-T coding figures of 1000base-t-coding.rst:

* level-spacing.svg: three levels and five levels at the same peak
  voltage, with the decision thresholds halfway between levels and the
  noise margin of each;
* shaping-filter.svg: the example transmit filter
  y_n = 0.75 a_n + 0.25 a_(n-1) of the 802.3ab tutorial, and a short
  sequence of PAM-5 symbols with the shaped output on the 17 levels;
* trellis.svg: the level subsets X and Y, and the eight states of the
  convolutional encoder of subclause 40.3.1.3.4 over four symbol periods,
  with one surviving path;
* scrambler-100base-tx.svg and scrambler-1000base-t.svg: the scrambler
  shift registers, with the taps of their generator polynomials.

Run with:

    uv run docs/ethernet/phy-electrical/coding_graphs.py

SPDX-License-Identifier: Apache-2.0
"""

import pathlib

from svgplot import (Axes, Fig, BLUE, RED, GREEN, GREY, INK, FILL_GREY,
                     FILL_ORANGE, fmt)

HERE = pathlib.Path(__file__).parent


def level_spacing():
    fig = Fig(480, 360)
    top, bot = 50, 300

    def y(v):  # v from -1 (minus peak) to +1 (plus peak)
        return (top + bot) / 2 - v * (bot - top) / 2

    fig.line(70, top, 70, bot)
    for v in (-1, -0.5, 0, 0.5, 1):
        fig.line(65, y(v), 70, y(v))
        fig.text(60, y(v), {1: "+peak", -1: "−peak"}.get(v, fmt(v)),
                 size=13, anchor="end")
    fig.text(20, (top + bot) / 2, "Voltage (fraction of peak)", size=14,
             rotate=-90)
    cols = [
        (150, "Three levels", [-1, 0, 1], ["−1", "0", "+1"]),
        (330, "Five levels (PAM-5)", [-1, -0.5, 0, 0.5, 1],
         ["−2", "−1", "0", "+1", "+2"]),
    ]
    for x, title, levels, names in cols:
        fig.text(x + 30, 24, title, size=14, weight="bold")
        for a, b in zip(levels, levels[1:]):
            fig.line(x - 10, y((a + b) / 2), x + 70, y((a + b) / 2),
                     stroke=RED, dash="5 4", width=1.2)
        for v, n in zip(levels, names):
            fig.line(x, y(v), x + 60, y(v), stroke=BLUE, width=3)
            fig.text(x - 14, y(v), n, size=13, anchor="end", fill=BLUE)
        # Noise margin: from the 0 level up to the next threshold.
        step = levels[1] - levels[0]
        ym0, ym1 = y(0), y(step / 2)
        fig.line(x + 80, ym0, x + 80, ym1)
        fig.arrowhead(x + 80, ym0, x + 80, ym1, size=6)
        fig.arrowhead(x + 80, ym1, x + 80, ym0, size=6)
        fig.text(x + 86, (ym0 + ym1) / 2, "margin" if step == 1 else
                 "margin,\nhalf as\nlarge:\n6.0 dB\nless", size=12, anchor="start")
    fig.line(70, 326, 90, 326, stroke=BLUE, width=3)
    fig.text(96, 326, "level", size=13, anchor="start")
    fig.line(160, 326, 180, 326, stroke=RED, dash="5 4")
    fig.text(186, 326, "decision threshold, halfway between levels",
             size=13, anchor="start")
    fig.save(HERE / "level-spacing.svg")


def box(fig, x, y, w, h, label, fill=FILL_GREY):
    fig.rect(x - w / 2, y - h / 2, w, h, fill=fill, rx=5)
    fig.text(x, y, label, size=13)


def arrow(fig, x1, y1, x2, y2):
    fig.line(x1, y1, x2, y2, arrow=True)


def shaping_filter():
    fig = Fig(480, 560)
    # Filter structure.
    fig.text(20, 18, "(a) Transmit shaping filter", size=14, anchor="start",
             weight="bold")
    ya, yb = 60, 140
    fig.text(30, ya, "aₙ", size=15, italic=True)
    fig.circle(70, ya, 3.5)
    fig.line(42, ya, 70, ya)
    box(fig, 170, ya, 70, 32, "× 0.75", FILL_ORANGE)
    arrow(fig, 70, ya, 135, ya)
    fig.line(70, ya, 70, yb)
    box(fig, 130, yb, 96, 34, "delay 8 ns")
    arrow(fig, 70, yb, 82, yb)
    box(fig, 250, yb, 70, 32, "× 0.25", FILL_ORANGE)
    arrow(fig, 178, yb, 215, yb)
    fig.text(196, yb - 14, "aₙ₋₁", size=13, italic=True)
    fig.add('<circle cx="330" cy="60" r="16" fill="#ffffff" stroke="#222222" '
            'stroke-width="1.2"/>')
    fig.text(330, 60, "Σ", size=16)
    arrow(fig, 205, ya, 314, ya)
    fig.line(285, yb, 330, yb)
    arrow(fig, 330, yb, 330, 76)
    arrow(fig, 346, ya, 400, ya)
    fig.text(420, ya, "yₙ", size=15, italic=True)
    fig.text(420, ya + 22, "to DAC", size=12)
    # Example sequence.
    fig.text(20, 196, "(b) PAM-5 symbols and the shaped output", size=14,
             anchor="start", weight="bold")
    a = [0, 1, -1, 2, 2, 0, -2, -1, 1, 0]
    yv = [0.75 * a[i] + 0.25 * (a[i - 1] if i else 0) for i in range(len(a))]
    ax = Axes(fig, 62, 216, 462, 476, (0, 80), (-2.2, 2.8))
    for k in range(-8, 9):
        ax.hline(k / 4, stroke="#e4e4e4" if k % 4 else "#c8c8c8", width=1)
    ax.frame(range(0, 81, 16), [-2, -1, 0, 1, 2], "Time (ns)", "Level",
             yfmt=fmt, grid=False)

    def steps(vals):
        pts = []
        for i, v in enumerate(vals):
            pts += [(8 * i, v), (8 * i + 8, v)]
        return pts

    ax.plot(steps(a), stroke=GREY, width=2, dash="6 4")
    ax.plot(steps(yv), stroke=BLUE, width=2.6)
    fig.circle(ax.X(28), ax.Y(1.25), 4, fill=RED)
    fig.line(ax.X(28), ax.Y(2.35), ax.X(28), ax.Y(1.25) - 5, stroke=RED)
    fig.text(ax.X(28), ax.Y(2.5), "+2 after −1 gives 1.25", size=13,
             fill=RED)
    fig.line(70, 528, 94, 528, stroke=GREY, width=2, dash="6 4")
    fig.text(100, 528, "symbol aₙ, five levels", size=13, anchor="start")
    fig.line(270, 528, 294, 528, stroke=BLUE, width=2.6)
    fig.text(300, 528, "output yₙ", size=13, anchor="start")
    fig.text(240, 550, "Grid lines: the 17 output levels, every 0.25",
             size=13, fill=GREY)
    fig.save(HERE / "shaping-filter.svg")


def next_state(s, u7, u6):
    """The convolutional encoder of IEEE 802.3-2022 subclause 40.3.1.3.4,
    with the state s = 4 cs[2] + 2 cs[1] + cs[0]:
    cs[1] = u6 ^ cs[0] of the last step, cs[2] = u7 ^ cs[1], cs[0] = cs[2]."""
    c2, c1, c0 = (s >> 2) & 1, (s >> 1) & 1, s & 1
    return 4 * (u7 ^ c1) + 2 * (u6 ^ c0) + c2


def trellis():
    fig = Fig(480, 430)
    steps = 4
    x0, dx = 150, 64
    y0, dy = 60, 36
    fig.text(20, 18, "Level subsets", size=14, anchor="start", weight="bold")
    for i, lv in enumerate((2, 1, 0, -1, -2)):
        y = y0 + 6 + i * 42
        sub = "Y" if lv % 2 == 0 else "X"
        colour = BLUE if sub == "Y" else RED
        fig.line(30, y, 70, y, stroke=colour, width=3)
        fig.text(80, y, f"{fmt(lv)}: {sub}", size=13, anchor="start",
                 fill=colour)
    fig.text(62, y0 + 6 + 5 * 42, "X = {−1, +1}\nY = {−2, 0, +2}", size=12)
    fig.text(x0 + steps * dx / 2, 18, "Encoder states over four symbol "
             "periods", size=14, weight="bold")
    xs = [x0 + k * dx for k in range(steps + 1)]
    ys = [y0 + s * dy for s in range(8)]
    for k in range(steps):
        for s in range(8):
            for u in range(4):
                t = next_state(s, u >> 1, u & 1)
                fig.line(xs[k], ys[s], xs[k + 1], ys[t], stroke="#c8c8c8",
                         width=1)
    path, s = [0], 0
    for u in (2, 1, 3, 0):
        s = next_state(s, u >> 1, u & 1)
        path.append(s)
    fig.poly([(xs[k], ys[st]) for k, st in enumerate(path)], stroke=GREEN,
             width=3.4)
    for k, x in enumerate(xs):
        for s, y in enumerate(ys):
            fig.circle(x, y, 4.5, fill=INK)
        fig.text(x, ys[-1] + 26, f"n + {k}" if k else "n", size=12)
    for s, y in enumerate(ys):
        fig.text(xs[-1] + 12, y, f"state {s}", size=11, anchor="start",
                 fill=GREY)
    for k in range(steps):
        fig.text((xs[k] + xs[k + 1]) / 2, ys[-1] + 44, "8 ns", size=11,
                 fill=GREY)
    fig.text(240, 400, "Grey: every allowed transition. "
             "Green: one path that the\nViterbi decoder keeps. Each step must "
             "finish within 8 ns.", size=12)
    fig.save(HERE / "trellis.svg")


def xor_gate(fig, x, y, r=10):
    fig.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#ffffff" '
            f'stroke="{INK}" stroke-width="1.3"/>')
    fig.line(x - r, y, x + r, y, width=1.2)
    fig.line(x, y - r, x, y + r, width=1.2)


def lfsr_row(fig, y, shown, taps, title):
    """Shift register stages `shown` (None marks a gap), the exclusive-OR
    of the tap outputs fed back into stage 1, and its exclusive-OR with the
    data."""
    fig.text(20, y - 50, title, size=13, anchor="start", weight="bold")
    x, w, gap = 50, 24, 5
    xs = {}
    for s in shown:
        if s is None:
            fig.text(x + 8, y, "…", size=14)
            x += 16 + gap
            continue
        colour = FILL_ORANGE if s in taps else FILL_GREY
        fig.rect(x, y - 12, w, 24, fill=colour, rx=2)
        fig.text(x + w / 2, y, str(s), size=11)
        xs[s] = x
        x += w + gap
    xe = x
    # Shift direction arrows between visible neighbours are implied; draw
    # the input arrow to stage 1 and the feedback.
    xf = 32
    yb = y + 40
    xx = xe + 10
    xor_gate(fig, xx, yb)
    for k in taps:
        xc = xs[k] + w / 2
        fig.line(xc, y + 12, xc, yb)
        fig.line(xc, yb, xx - 10, yb) if k == min(taps) else None
    fig.line(xs[max(taps)] + w / 2, yb, xx - 10, yb)
    fig.line(xx, yb + 10, xx, yb + 28)
    fig.line(xx, yb + 28, xf, yb + 28)
    fig.line(xf, yb + 28, xf, y)
    fig.line(xf, y, xs[shown[0]], y, arrow=True)
    fig.text(xf + 8, yb + 16, "new bit", size=11, anchor="start", fill=GREY)
    # Exclusive-OR of the new bit with the data.
    yd = yb + 60
    xor_gate(fig, xx, yd)
    fig.line(xx, yb + 28, xx, yd - 10, arrow=True)
    fig.line(xx - 110, yd, xx - 10, yd, arrow=True)
    fig.text(xx - 114, yd, "bits in", size=12, anchor="end")
    fig.line(xx, yd + 10, xx, yd + 36, arrow=True)
    fig.text(xx - 8, yd + 30, "scrambled bits out", size=12, anchor="end")


def scramblers():
    fig = Fig(480, 230)
    lfsr_row(fig, 60, list(range(1, 12)), (9, 11),
             "100BASE-TX: 1 + x⁹ + x¹¹, repeats every 2047 bits")
    fig.save(HERE / "scrambler-100base-tx.svg")
    fig = Fig(480, 470)
    shown = [1, 2, None, 12, 13, 14, None, 19, 20, 21, None, 32, 33]
    lfsr_row(fig, 60, shown, (13, 33), "Master: 1 + x¹³ + x³³")
    lfsr_row(fig, 290, shown, (20, 33), "Slave: 1 + x²⁰ + x³³")
    fig.save(HERE / "scrambler-1000base-t.svg")


if __name__ == "__main__":
    level_spacing()
    shaping_filter()
    trellis()
    scramblers()
