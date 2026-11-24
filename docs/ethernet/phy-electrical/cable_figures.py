# /// script
# requires-python = ">=3.10"
# ///
"""Write the cable figures of the Ethernet transceiver pages:

* cable.svg: the four twisted pairs of a cable, the RJ45 contacts that
  each pair lands on (IEEE 802.3-2022 Table 40-12, MDI column), the
  100 ohm pair impedance, the up to 100 m length, and the differential
  voltage of one pair;
* impairments.svg: the four ways the cable changes the signal, one panel
  each: insertion loss and inter-symbol interference, a reflection at an
  impedance change, near-end crosstalk and far-end crosstalk;
* pulse-response.svg: a received symbol pulse sampled once per symbol
  period, with the precursor and postcursor samples that the two
  equalisers remove.

The pulse shapes are schematic, not to scale. Run with:

    uv run docs/ethernet/phy-electrical/cable_figures.py

SPDX-License-Identifier: Apache-2.0
"""

import math
import pathlib

from svgplot import (Axes, Fig, BLUE, RED, GREEN, PURPLE, GREY, INK,
                     FILL_GREY, FILL_ORANGE, FILL_BLUE, fmt)

HERE = pathlib.Path(__file__).parent
PAIRS = [("A", (1, 2), BLUE), ("B", (3, 6), RED), ("C", (4, 5), GREEN),
         ("D", (7, 8), PURPLE)]


def twisted(fig, x0, x1, yc, colour, amp=6, period=26):
    for phase in (0, math.pi):
        pts = [(x, yc + amp * math.sin(2 * math.pi * (x - x0) / period + phase))
               for x in range(int(x0), int(x1) + 1, 2)]
        fig.poly(pts, stroke=colour, width=2.2)


def cable():
    fig = Fig(480, 350)
    # RJ45 plug face with eight contacts.
    fig.rect(14, 40, 56, 230, fill=FILL_GREY, rx=6)
    fig.text(42, 26, "RJ45", size=13, weight="bold")
    cy = {c: 58 + (c - 1) * 28 for c in range(1, 9)}
    for c, y in cy.items():
        fig.rect(48, y - 6, 18, 12, fill="#d9b44a", stroke=INK, width=0.8)
        fig.text(34, y, str(c), size=13)
    fig.text(42, 290, "contact", size=12, fill=GREY)
    # Pairs inside the jacket.
    fig.rect(150, 46, 316, 224, fill="#ffffff", stroke=GREY, width=1.5,
             rx=20)
    py = {p: 78 + i * 54 for i, (p, _, _) in enumerate(PAIRS)}
    for p, (ca, cb), colour in PAIRS:
        y = py[p]
        for c, dy in ((ca, -6), (cb, 6)):
            fig.line(66, cy[c], 150, y + dy, stroke=colour, width=1.8)
        twisted(fig, 150, 290, y, colour)
        twisted(fig, 330, 440, y, colour)
        fig.text(462, y, p, size=14, weight="bold", fill=colour,
                 anchor="start")
    # Break marks: the cable continues for up to 100 m.
    for x in (300, 320):
        fig.poly([(x - 4, 50), (x + 4, 140), (x - 4, 180), (x + 4, 266)],
                 stroke=GREY, width=1.2)
    y = 18
    fig.line(150, y, 466, y, arrow=True)
    fig.arrowhead(466, y, 150, y)
    fig.rect(240, y - 9, 136, 18, fill="#ffffff", stroke="none")
    fig.text(308, y, "link up to 100 m", size=13)
    fig.text(270, 306, "Each pair: two wires twisted together, with a\n"
             "differential impedance of 100 Ω. Its signal is the\n"
             "voltage between its wires: for pair A, the voltage\n"
             "of contact 1 minus that of contact 2.", size=13)
    fig.save(HERE / "cable.svg")


def pulse(t, t0, tau, amp):
    """A smooth one-sided pulse that peaks at t0 + 2 tau."""
    x = t - t0
    if x <= 0:
        return 0.0
    return amp * (x / (2 * tau)) ** 2 * math.exp(2 - x / tau)


def impairments():
    fig = Fig(480, 640)
    # (a) Insertion loss and inter-symbol interference.
    fig.text(10, 14, "(a) Insertion loss", size=14, anchor="start",
             weight="bold")
    ax = Axes(fig, 62, 34, 466, 184, (0, 64), (0, 1.1))
    for k in range(8, 64, 8):
        ax.vline(k, stroke="#e4e4e4", width=1)
    ax.frame([0, 16, 32, 48, 64], [0, 0.5, 1],
             "Time (ns), symbol slots of 8 ns", "Voltage", xfmt=fmt,
             yfmt=fmt, grid=False, size=12)
    sent = [(0, 0), (8, 0), (8, 1), (16, 1), (16, 0), (64, 0)]
    ax.plot(sent, stroke=GREY, width=2, dash="6 4")
    rx = [(t / 4, pulse(t / 4, 10, 4, 0.42)) for t in range(0, 257)]
    tail = [(t, v) for t, v in rx if t >= 24]
    fig.poly(ax.pts([(24, 0)] + tail + [(64, 0)]), stroke="none",
             fill=FILL_ORANGE, closed=True)
    ax.plot(rx, stroke=BLUE)
    fig.text(ax.X(17), ax.Y(0.9), "sent", size=12, anchor="start", fill=GREY)
    fig.text(ax.X(27), ax.Y(0.62), "arrives smaller and wider", size=12,
             anchor="start", fill=BLUE)
    fig.text(ax.X(47), ax.Y(0.36), "shaded tail over later\nsymbols: "
             "inter-symbol\ninterference", size=12)
    # (b) Return loss: reflection at an impedance change.
    y0 = 250
    fig.text(10, y0, "(b) Return loss", size=14, anchor="start",
             weight="bold")
    yl = y0 + 50
    fig.rect(14, yl - 18, 70, 36, fill=FILL_ORANGE, rx=5)
    fig.text(49, yl, "sender", size=12)
    fig.line(84, yl, 466, yl, stroke=INK, width=3)
    fig.rect(273, yl - 15, 14, 30, fill=FILL_BLUE)
    fig.text(296, yl - 24, "connector: impedance change", size=12,
             anchor="start")
    fig.line(100, yl - 12, 266, yl - 12, stroke=BLUE, width=2.6, arrow=True)
    fig.text(180, yl - 26, "incident signal", size=12, fill=BLUE)
    fig.line(266, yl + 12, 100, yl + 12, stroke=RED, width=1.2, arrow=True)
    fig.text(180, yl + 26, "reflection, weaker by the return loss", size=12,
             fill=RED)
    # (c) and (d): one end of the cable on the left, pairs A and B.
    for y0, title, near in ((350, "(c) Near-end crosstalk", True),
                            (470, "(d) Far-end crosstalk", False)):
        fig.text(10, y0, title, size=14, anchor="start", weight="bold")
        ya, yb = y0 + 34, y0 + 80
        xl, xr = 14, 466
        for yy, p in ((ya, "A"), (yb, "B")):
            fig.line(xl + 50, yy, xr - (50 if not near else 0), yy,
                     stroke=INK, width=2.2)
            fig.text(xl + 64, yy - 10, f"pair {p}", size=12, fill=GREY,
                     anchor="start")
        fig.rect(xl, ya - 13, 50, 26, fill=FILL_BLUE, rx=4)
        fig.text(xl + 25, ya, "RX", size=12)
        tx_x = xl if near else xr - 50
        fig.rect(tx_x, yb - 13, 50, 26, fill=FILL_ORANGE, rx=4)
        fig.text(tx_x + 25, yb, "TX", size=12)
        if near:
            fig.line(xl + 150, yb - 4, xl + 150, ya + 4, stroke=RED,
                     width=3.5, arrow=True)
            fig.text(xl + 162, (ya + yb) / 2, "strong: the disturbing "
                     "transmitter is at\nthe receiver's end", size=12,
                     anchor="start", fill=RED)
        else:
            fig.line(xr - 100, yb - 4, xr - 100, ya + 4, stroke=RED,
                     width=1.2, arrow=True)
            fig.line(xr - 104, ya + 6, xl + 56, ya + 6, stroke=RED,
                     width=1.2, dash="4 3", arrow=True)
            fig.text(xl + 150, (ya + yb) / 2 + 4, "weaker: it crosses the "
                     "whole cable", size=12, anchor="start", fill=RED)
            fig.text(xr - 25, yb + 22, "far end", size=12, fill=GREY)
        if near:
            fig.text(xr - 4, yb + 18, "to the far end", size=12, fill=GREY,
                     anchor="end")
    fig.text(240, 612, "Losses are in dB: 6 dB halves a voltage, and "
             "20 dB divides it by 10.", size=12)
    fig.save(HERE / "impairments.svg")


def pulse_response():
    fig = Fig(480, 330)
    ax = Axes(fig, 62, 20, 462, 262, (-3, 9), (-0.1, 1.1))

    def h(t):
        tail = 0.1 * (1 - math.exp(-t / 0.5)) * math.exp(-t / 4) if t > 0 else 0
        return pulse(t, -1.2, 0.6, 1.0) + tail

    ax.band(-0.1, 1.1, FILL_BLUE, -3, -0.5)
    ax.band(-0.1, 1.1, FILL_ORANGE, 0.5, 9)
    ax.frame(range(-3, 10), [0, 0.5, 1], "Time (symbol periods of 8 ns)",
             "Amplitude", xfmt=fmt, yfmt=fmt)
    ax.hline(0, stroke=GREY, width=1)
    ax.plot([(t / 20, h(t / 20)) for t in range(-60, 181)], stroke=BLUE)
    for n in range(-2, 9):
        v = h(n)
        c = RED if n == 0 else INK
        fig.line(ax.X(n), ax.Y(0), ax.X(n), ax.Y(v), stroke=c, width=1.6)
        fig.circle(ax.X(n), ax.Y(v), 4, fill=c)
    fig.text(ax.X(-1.75), ax.Y(0.72), "precursor:\nfeed-forward\nequaliser",
             size=12)
    fig.text(ax.X(-0.2), ax.Y(1.04), "cursor", size=12, anchor="end",
             fill=RED)
    fig.text(ax.X(5), ax.Y(0.6), "postcursor tail:\ndecision-feedback\n"
             "equaliser", size=12)
    fig.save(HERE / "pulse-response.svg")


if __name__ == "__main__":
    cable()
    impairments()
    pulse_response()
