# /// script
# requires-python = ">=3.10"
# ///
"""Write the cable graphs of the Ethernet transceiver pages:

* channel-limits.svg: the 1000BASE-T insertion loss, NEXT loss and ELFEXT
  loss limits of IEEE 802.3-2022 subclauses 40.7.2.1, 40.7.3.1.1,
  40.7.3.2.1 and 40.7.3.2.2, as quoted on 1000base-t-echo.rst, with the
  near-end crosstalk margin shaded;
* return-loss.svg: the 1000BASE-T return loss limit of subclause 40.8.3.1,
  as quoted on integration/requirements.rst.

Run with:

    uv run docs/ethernet/phy-electrical/channel_graphs.py

SPDX-License-Identifier: Apache-2.0
"""

import math
import pathlib

from svgplot import (Axes, Fig, BLUE, RED, GREEN, ORANGE, GREY, INK,
                     FILL_ORANGE, FILL_BLUE)

HERE = pathlib.Path(__file__).parent
FREQS = [1 * 10 ** (i / 100) for i in range(201)]   # 1 MHz to 100 MHz


def il(f):
    return 2.1 * f ** 0.529 + 0.4 / f


def next_loss(f):
    return 27.1 - 16.8 * math.log10(f / 100)


def elfext(f):
    return 17 - 20 * math.log10(f / 100)


def pselfext(f):
    return 14.4 - 20 * math.log10(f / 100)


def channel_limits():
    fig = Fig(480, 700)
    fig.text(10, 14, "(a) Wanted signal and near-end crosstalk", size=14,
             anchor="start", weight="bold")
    ax = Axes(fig, 62, 32, 462, 352, (1, 100), (0, 70), xlog=True)
    # Near-end crosstalk margin: the gap between the NEXT and IL curves.
    top = ax.pts([(f, next_loss(f)) for f in FREQS])
    bot = ax.pts([(f, il(f)) for f in reversed(FREQS)])
    fig.poly(top + bot, stroke="none", fill=FILL_ORANGE, closed=True)
    ax.frame([1, 2, 5, 10, 31.25, 62.5, 100], range(0, 71, 10),
             "Frequency (MHz, log scale)", "Loss (dB)",
             xfmt=lambda v: f"{v:g}")
    for f in (31.25, 62.5):
        ax.vline(f, stroke=GREY, width=1, dash="4 3")
    ax.plot([(f, next_loss(f)) for f in FREQS], stroke=RED)
    ax.plot([(f, il(f)) for f in FREQS], stroke=BLUE)
    # Margin bars at 62.5 MHz and 100 MHz.
    for f in (62.5, 100):
        fig.line(ax.X(f), ax.Y(il(f)), ax.X(f), ax.Y(next_loss(f)),
                 stroke=INK, width=1.6)
    # Points from the table on the page.
    for f, v in ((10, 7.1), (62.5, 18.7), (100, 24.0)):
        fig.circle(ax.X(f), ax.Y(v), 3, fill=BLUE)
    for f, v in ((10, 43.9), (62.5, 30.5), (100, 27.1)):
        fig.circle(ax.X(f), ax.Y(v), 3, fill=RED)
    x = ax.X(1.12)
    fig.text(x, ax.Y(65), "NEXT loss, at least", size=13, anchor="start",
             fill=RED)
    fig.text(x, ax.Y(30), "Shaded: margin M of the wanted signal\n"
             "over NEXT, 11.8 dB at 62.5 MHz\nand 3.1 dB at 100 MHz",
             size=13, anchor="start")
    fig.text(x, ax.Y(7.5), "Insertion loss, at most", size=13,
             anchor="start", fill=BLUE)
    # (b) ELFEXT, already relative to the received signal.
    fig.text(10, 420, "(b) Far-end crosstalk against the received signal",
             size=14, anchor="start", weight="bold")
    bx = Axes(fig, 62, 438, 462, 638, (1, 100), (0, 70), xlog=True)
    bx.frame([1, 2, 5, 10, 31.25, 62.5, 100], range(0, 71, 10),
             "Frequency (MHz, log scale)", "ELFEXT loss (dB)",
             xfmt=lambda v: f"{v:g}")
    bx.plot([(f, elfext(f)) for f in FREQS], stroke=GREEN)
    bx.plot([(f, pselfext(f)) for f in FREQS], stroke=GREEN, dash="6 4")
    for f, v in ((10, 37.0), (62.5, 21.1), (100, 17.0)):
        fig.circle(bx.X(f), bx.Y(v), 3, fill=GREEN)
    fig.text(bx.X(1.12), bx.Y(12), "ELFEXT loss, at least: one pair (solid)\n"
             "and power sum of three (dashed)", size=13, anchor="start",
             fill=GREEN)
    fig.save(HERE / "channel-limits.svg")


def return_loss():
    fig = Fig(480, 320)
    ax = Axes(fig, 62, 12, 462, 262, (1, 100), (0, 25), xlog=True)

    def limit(f):
        return 16 if f <= 40 else 10 - 20 * math.log10(f / 80)

    pts = [(f, limit(f)) for f in FREQS]
    fig.poly(ax.pts(pts) + [(ax.X(100), ax.Y(0)), (ax.X(1), ax.Y(0))],
             stroke="none", fill=FILL_ORANGE, closed=True)
    ax.frame([1, 2, 5, 10, 20, 40, 100], range(0, 26, 5),
             "Frequency (MHz, log scale)", "Return loss (dB)")
    ax.plot(pts, stroke=BLUE)
    fig.circle(ax.X(100), ax.Y(limit(100)), 3.5, fill=BLUE)
    fig.text(ax.X(100) - 6, ax.Y(limit(100)) + 18, "8.1 dB at 100 MHz",
             size=13, anchor="end")
    fig.text(ax.X(1.1), ax.Y(19), "at least 16 dB, 1 MHz to 40 MHz",
             size=13, anchor="start")
    fig.text(ax.X(100) - 4, ax.Y(23), "10 − 20 log₁₀(f/80),\nf in MHz", size=13,
             anchor="end")
    fig.text(ax.X(6), ax.Y(8), "not allowed", size=14, fill="#8a4a1a")
    fig.save(HERE / "integration" / "return-loss.svg")


if __name__ == "__main__":
    channel_limits()
    return_loss()
