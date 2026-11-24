# /// script
# requires-python = ">=3.10"
# ///
"""Write the signal graphs of the 10BASE-T and 100BASE-TX pages:

* 10base-t-levels.svg: the 10BASE-T and 10BASE-Te peak bands of IEEE
  802.3-2022 subclause 14.3.1.2.1 on a Manchester waveform, and the 300 mV
  idle threshold of 14.3.1.3.2;
* link-pulses.svg: link test pulses every 16 ms +/- 8 ms (14.2.1.1), the
  link_loss time of 50 ms to 150 ms (14.2.1.7), and one pulse enlarged
  with its peak band of 585 mV to 3.1 V;
* 100base-tx-edges.svg: single-pole edges with 10 % to 90 % rise times of
  3 ns and 5 ns against the 0.95 V to 1.05 V peak band;
* baseline-wander.svg: three-level symbols after a coupling that blocks
  DC, whose zero level drifts during a run that does not average to zero,
  and the same symbols after the zero level is restored.

Edge shapes, noise and pulse shapes are schematic: the pages give limits,
not shapes. Run with:

    uv run docs/ethernet/phy-electrical/signal_graphs.py

SPDX-License-Identifier: Apache-2.0
"""

import math
import pathlib
import random

from svgplot import (Axes, Fig, BLUE, RED, GREY, INK, FILL_ORANGE,
                     FILL_BLUE, fmt)

HERE = pathlib.Path(__file__).parent


def smooth_levels(levels, period, rise, t_end, step=1.0):
    """A waveform holding each level for `period`, with raised-cosine
    transitions of length `rise` centred on each boundary."""
    pts = []
    t = 0.0
    while t <= t_end:
        i = min(int(t // period), len(levels) - 1)
        v = levels[i]
        tb = (i + 1) * period
        tp = i * period
        if i + 1 < len(levels) and t > tb - rise / 2:
            x = (t - (tb - rise / 2)) / rise
            v = levels[i] + (levels[i + 1] - levels[i]) * (1 - math.cos(math.pi * x)) / 2
        elif i > 0 and t < tp + rise / 2:
            x = (t - (tp - rise / 2)) / rise
            v = levels[i - 1] + (levels[i] - levels[i - 1]) * (1 - math.cos(math.pi * x)) / 2
        pts.append((t, v))
        t += step
    return pts


def manchester(bits, amp):
    """Half-bit levels: a 1 goes low to high, a 0 high to low."""
    out = []
    for b in bits:
        out += [-amp, amp] if b else [amp, -amp]
    return out


def ten_base_t_levels():
    fig = Fig(480, 580)
    # (a) Transmitted waveform and the peak bands.
    a = Axes(fig, 62, 56, 462, 266, (0, 500), (-3.2, 3.2))
    for s in (+1, -1):
        a.band(2.2 * s if s > 0 else -2.8, 2.8 if s > 0 else -2.2, FILL_ORANGE)
        a.band(1.54 if s > 0 else -1.96, 1.96 if s > 0 else -1.54, FILL_BLUE)
    a.frame(range(0, 501, 100), [-3, -2, -1, 0, 1, 2, 3], "Time (ns)",
            "Differential voltage (V)", yfmt=fmt)
    wave = smooth_levels(manchester([1, 0, 1, 1, 0], 2.5), 50, 14, 500)
    a.plot(wave, stroke=BLUE)
    fig.text(62, 14, "(a) Transmitter, into 100 Ω", size=14, anchor="start",
             weight="bold")
    for i, (fill, label) in enumerate(((FILL_ORANGE, "10BASE-T peak, 2.2 V to 2.8 V"),
                                      (FILL_BLUE, "10BASE-Te peak, 1.54 V to 1.96 V"))):
        x = 62 + i * 205
        fig.rect(x, 34, 18, 12, fill=fill, stroke="none")
        fig.text(x + 23, 40, label, size=12, anchor="start")
    # (b) Idle receiver: noise below the threshold, then a signal above it.
    b = Axes(fig, 62, 356, 462, 520, (0, 500), (-1.2, 1.4))
    b.band(-0.3, 0.3, "#f6f6f6")
    b.frame(range(0, 501, 100), [-1, -0.3, 0, 0.3, 1], "Time (ns)",
            "Differential voltage (V)", yfmt=fmt)
    for v in (0.3, -0.3):
        b.hline(v, stroke=RED, width=1.4, dash="6 4")
    rnd = random.Random(4)
    noise = []
    for t in range(0, 251, 4):
        noise.append((t, 0.17 * math.sin(t / 7.0) * rnd.uniform(0.3, 1.0)
                      + rnd.uniform(-0.06, 0.06)))
    b.plot(noise, stroke=GREY, width=1.6)
    sig = smooth_levels([0] + manchester([1, 0, 1], 0.9)[:-1], 50, 18, 250)
    b.plot([(t + 250, v) for t, v in sig], stroke=BLUE)
    fig.text(62, 340, "(b) Idle receiver, after the 15 MHz filter",
             size=14, anchor="start", weight="bold")
    fig.text(b.X(125), b.Y(0.75), "below 300 mV:\nignored", size=13)
    fig.text(b.X(400), b.Y(1.17), "above 300 mV: accepted", size=13)
    fig.save(HERE / "10base-t-levels.svg")


def link_pulses():
    fig = Fig(480, 500)
    a = Axes(fig, 62, 40, 462, 200, (0, 240), (0, 3.5))
    a.band(0, 3.5, FILL_ORANGE, 114, 214)
    a.frame(range(0, 241, 40), [0, 1, 2, 3], "Time (ms)",
            "Voltage (V)", yfmt=fmt, grid=False)
    for t in (16, 40, 64):
        fig.line(a.X(t), a.Y(0), a.X(t), a.Y(2.5), stroke=BLUE, width=2.4)
    fig.text(62, 20, "(a) Pulses on a silent line, then a lost link",
             size=14, anchor="start", weight="bold")
    y = a.Y(2.9)
    fig.line(a.X(16), y, a.X(40), y, arrow=True)
    fig.arrowhead(a.X(40), y, a.X(16), y)
    fig.text(a.X(28), a.Y(3.25), "8 ms to 24 ms", size=12)
    fig.text(a.X(89), a.Y(1.6), "no pulse", size=13)
    fig.text(a.X(164), a.Y(2.4), "link_loss:\nfailed between\n50 ms and 150 ms\n"
             "after the last pulse", size=12)
    # (b) One pulse enlarged.
    b = Axes(fig, 62, 290, 462, 440, (-100, 300), (0, 3.5))
    b.band(0.585, 3.1, FILL_BLUE)
    b.frame(range(-100, 301, 100), [0, 0.585, 2, 3.1], "Time (ns)",
            "Voltage (V)", xfmt=fmt, yfmt=fmt)
    pulse = [(t, 2.5 * math.sin(math.pi * t / 100) ** 2 if 0 <= t <= 100 else 0)
             for t in range(-100, 301, 2)]
    b.plot(pulse, stroke=BLUE)
    fig.text(62, 270, "(b) One link test pulse", size=14, anchor="start",
             weight="bold")
    fig.text(b.X(200), b.Y(2.2), "peak between\n585 mV and 3.1 V", size=13)
    yb = b.Y(0.3)
    fig.line(b.X(0), yb, b.X(100), yb, arrow=True)
    fig.arrowhead(b.X(100), yb, b.X(0), yb)
    fig.text(b.X(100) + 8, yb, "about 100 ns", size=12, anchor="start")
    fig.save(HERE / "link-pulses.svg")


def edges_100base_tx():
    fig = Fig(480, 330)
    ax = Axes(fig, 62, 12, 462, 262, (-2, 12), (0, 1.2))
    ax.band(0.95, 1.05, FILL_ORANGE)
    ax.frame(range(-2, 13, 2), [0, 0.1, 0.5, 0.9, 1.0, 1.2], "Time (ns)",
             "Differential voltage (V)", xfmt=fmt, yfmt=fmt)
    for v in (0.1, 0.9):
        ax.hline(v, stroke=GREY, width=1, dash="4 3")
    for tr, colour, ylab in ((3, BLUE, 0.62), (5, RED, 0.38)):
        tau = tr / 2.2
        ax.plot([(t / 10, 0 if t < 0 else 1 - math.exp(-t / 10 / tau))
                 for t in range(-20, 121)], stroke=colour)
        t10, t90 = 0.105 * tau, 2.303 * tau
        for t, v in ((t10, 0.1), (t90, 0.9)):
            fig.circle(ax.X(t), ax.Y(v), 3.5, fill=colour)
        fig.text(ax.X(t90) + 6, ax.Y(ylab), f"10 % to 90 %\nin {tr} ns",
                 size=13, anchor="start", fill=colour)
    fig.text(ax.X(7.5), ax.Y(1.12), "peak 0.95 V to 1.05 V", size=13)
    fig.save(HERE / "100base-tx-edges.svg")


def baseline_wander():
    """Symbols through a coupling that blocks DC (a first-order high-pass),
    before and after a slow loop restores the zero level. Schematic."""
    rnd = random.Random(7)
    sym = [rnd.choice((-1, 0, 1)) for _ in range(12)]
    sym += [1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1]
    sym += [rnd.choice((-1, 0, 1)) for _ in range(16)]
    period, tau = 8.0, 60.0
    x, base, wander = [], 0.0, []
    for i, s in enumerate(sym):
        for k in range(8):
            t = i * period + k
            base += (s - base) / tau
            x.append((t, s))
            wander.append((t, -base))
    fig = Fig(480, 490)
    t_end = len(sym) * period
    for row, (title, y0) in enumerate((("(a) After the coupling: the zero "
                                        "level drifts", 30),
                                       ("(b) After baseline restoration", 260))):
        ax = Axes(fig, 62, y0 + 20, 462, y0 + 160, (0, t_end), (-2, 1.6))
        ax.frame(range(0, int(t_end) + 1, 64), [-2, -1, 0, 1], "Time (ns)"
                 if row else None, "Level", yfmt=fmt)
        fig.text(62, y0, title, size=14, anchor="start", weight="bold")
        ax.band(-2, 1.6, "#fbe5d6", 12 * period, 32 * period)
        if row == 0:
            ax.plot([(t, v + w) for (t, v), (_, w) in zip(x, wander)],
                    stroke=BLUE, width=1.8)
            ax.plot(wander, stroke=RED, width=1.6, dash="6 4")
            fig.text(ax.X(23 * period), ax.Y(-1.1), "zero level", size=12,
                     fill=RED)
        else:
            ax.plot(x, stroke=BLUE, width=1.8)
            ax.hline(0, stroke=RED, width=1.6, dash="6 4")
    fig.text(240, 478, "Shaded: a run of symbols that does not average "
             "to zero", size=12, fill=GREY)
    fig.save(HERE / "baseline-wander.svg")


if __name__ == "__main__":
    ten_base_t_levels()
    link_pulses()
    edges_100base_tx()
    baseline_wander()
