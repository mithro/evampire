# /// script
# requires-python = ">=3.10"
# ///
"""Write the power and current graphs of the Power over Ethernet pages.
Run with:

    uv run docs/power/poe/graphs_power.py

Writes:

peak-power.svg
    A class 4 powered device drawing above its class power, up to the peak
    power, for a limited time (types-classes.rst; IEEE 802.3 145.3.8.4).
pd-voltage.svg
    The voltage at the powered device against its power, from the cable
    model, with the class 8 operating point (types-classes.rst).
inrush-pd.svg
    The input capacitor charging at a constant current after turn-on, with
    the time limits (powered-device.rst, pd-controller.rst).
inrush-pse.svg
    The lowest and highest inrush current of power sourcing equipment
    against port voltage (power-sourcing.rst; IEEE 802.3 145.2.10.7 and
    Table 145-16).
startup-power.svg
    The power available to the powered device at each step, on a log scale
    (startup.rst).

Every number comes from the page that shows the figure.

SPDX-License-Identifier: Apache-2.0
"""

import math

from svgfig import (BAD, BAD_INK, EVP, FILL, GREY, INK, OK, OK_INK, POWER,
                    SRC_INK, Plot, dot, line, polyline, rect, svg, text,
                    write)


def peak_power():
    p = Plot(70, 30, 560, 200, (0, 1000), (20, 30))
    body = [rect(p.left, p.y(30), p.w, p.y(28.3) - p.y(30), BAD, "none"),
            rect(p.left, p.y(28.3), p.w, p.y(25.5) - p.y(28.3), POWER,
                 "none")]
    body.append(p.frame())
    body += p.yticks([20, 25.5, 28.3, 30], "PD power (W)", fmt="{:g}")
    body += p.xticks([0, 200, 400, 600, 800, 1000],
                     "time in a 1 s window (ms)", grid=False)
    pts = [(0, 23), (300, 23), (300, 28), (350, 28), (350, 23), (1000, 23)]
    body.append(polyline(p.pts(pts), SRC_INK, 2.2))
    body.append(line(p.x(300), p.y(29.2), p.x(350), p.y(29.2), INK, 1.0,
                     arrow="both"))
    body.append(text(p.x(360), p.y(29.2) + 4, "≤ 50 ms at a time, and "
                     "≤ 5 % of any 1 s window", 10))
    body.append(text(p.x(990), p.y(25.5) - 5, "class 4 power 25.5 W", 10,
                     "end"))
    body.append(text(p.x(990), p.y(28.3) - 5, "peak 28.3 W", 10, "end"))
    body.append(text(p.x(990), p.y(29.6) + 2, "not allowed", 10, "end",
                     fill=BAD_INK))
    return svg(680, int(p.bottom + 48), body, "Peak power")


def pd_voltage():
    p = Plot(70, 20, 470, 280, (0, 120), (0, 60))
    body = [p.frame()]
    body += p.yticks([0, 10, 20, 26, 41.2, 50, 60],
                     "voltage at the PD (V)", fmt="{:g}")
    body += p.xticks([0, 20, 40, 60, 71.3, 100, 120], "PD power (W)",
                     fmt="{:g}")
    cases = [(52, 6.25, SRC_INK, None, "52 V, 6.25 Ω"),
             (50, 6.25, INK, "6,3", "50 V, 6.25 Ω"),
             (50, 12.5, GREY, "2,3", "50 V, 12.5 Ω")]
    for v, r, col, dash, lab in cases:
        pmax = v * v / (4 * r)
        n = 60
        up = [(pmax * k / n, (v + math.sqrt(max(0, v * v - 4 * r * pmax *
                                                      k / n))) / 2)
              for k in range(n + 1)]
        lo = [(pmax * k / n, (v - math.sqrt(max(0, v * v - 4 * r * pmax *
                                                      k / n))) / 2)
              for k in range(n, -1, -1)]
        body.append(polyline(p.pts(up), col, 2.0, dash))
        body.append(polyline(p.pts(lo), col, 1.2, "1,3"))
        body.append(dot(p.x(pmax), p.y(v / 2), 3.5, col))
    body.append(dot(p.x(71.3), p.y(41.2), 5, SRC_INK))
    body.append(text(p.x(71.3) + 8, p.y(41.2) - 6, "class 8: 71.3 W at "
                     "41.2 V", 10, fill=SRC_INK))

    lx = p.right + 10
    for k, (v, r, col, dash, lab) in enumerate(cases):
        y = p.top + 20 + 18 * k
        body.append(line(lx, y - 4, lx + 18, y - 4, col, 2.0, dash))
        body.append(text(lx + 22, y, lab, 9))
    for k, s in enumerate(("solid: higher root,", "the operating point;",
                           "dotted: lower root;", "dots: D = 0, where",
                           "the roots meet;", "52 V: 108 W at 26 V")):
        body.append(text(lx, p.top + 90 + 14 * k, s, 9, fill=GREY))
    return svg(680, int(p.bottom + 48), body, "Voltage at the PD")


def inrush_pd():
    t_ch = 100e-6 * 57 / 0.140 * 1000           # 41 ms
    p = Plot(70, 30, 560, 120, (0, 100), (0, 60))
    body = [p.frame()]
    body += p.yticks([0, 30, 57], "capacitor (V)", fmt="{:g}")
    body.append(polyline(p.pts([(0, 0), (t_ch, 57), (100, 57)]), SRC_INK,
                         2.2))
    body.append(text(p.x(t_ch) + 6, p.y(57) + 14, f"charged at "
                     f"{t_ch:.0f} ms", 10))
    q = Plot(70, 190, 560, 140, (0, 100), (0, 1.1))
    body.append(rect(q.x(50), q.top, q.x(80) - q.x(50), q.y(0.4) - q.top,
                     BAD, "none"))
    body.append(q.frame())
    body += q.yticks([0, 0.14, 0.4, 1.0], "current (A)", fmt="{:g}")
    body.append(polyline(q.pts([(0, 0.14), (t_ch, 0.14), (t_ch, 0.0),
                                (100, 0.0)]), SRC_INK, 2.2))
    body.append(text(q.x(3), q.y(0.14) - 6, "charging at the 140 mA limit",
                     10))
    body.append(text(q.x(49), q.y(0.7), "50–80 ms: PD draws less", 10,
                     "end", fill=BAD_INK))
    body.append(text(q.x(49), q.y(0.7) + 14, "than 0.4 A (0.8 A,", 10, "end",
                     fill=BAD_INK))
    body.append(text(q.x(49), q.y(0.7) + 28, "classes 7 and 8)", 10, "end",
                     fill=BAD_INK))
    for t, s in ((50, "PSE inrush ends: 50 ms at the earliest"),
                 (80, "80 ms: class power")):
        for pl in (p, q):
            body.append(line(pl.x(t), pl.top, pl.x(t), pl.bottom, GREY, 1.0,
                             "4,3"))
        body.append(text(p.x(t) + 4, p.y(20 if t == 50 else 38), s, 10))
    body += q.xticks([0, 20, 41, 50, 80, 100], "time after turn-on (ms)",
                     grid=False)
    body.append(text(10, q.bottom + 58, "Example: 100 µF charged to 57 V "
                     "from empty. The load stays off until the capacitor",
                     11, fill=GREY))
    body.append(text(10, q.bottom + 74, "is charged; the converter then "
                     "starts (not drawn).", 11, fill=GREY))
    return svg(680, int(q.bottom + 86), body, "Powered device inrush")


def inrush_pse():
    p = Plot(80, 20, 460, 240, (0, 57), (0.001, 2), ylog=True)
    body = [p.frame()]
    body += p.yticks([0.001, 0.005, 0.01, 0.06, 0.1, 0.4, 0.9],
                     "inrush current (A)", fmt="{:g}")
    body += p.xticks([0, 10, 20, 30, 40, 50, 57], "port voltage (V)",
                     grid=False)
    lo = [(0, 0.005), (10, 0.005), (10, 0.06), (30, 0.06), (30, 0.4),
          (57, 0.4)]
    body.append(polyline(p.pts(lo), SRC_INK, 2.2))
    body.append(polyline(p.pts([(30, 0.4), (30, 0.8), (57, 0.8)]), SRC_INK,
                         1.6, "6,3"))
    body.append(polyline(p.pts([(0, 0.45), (57, 0.45)]), INK, 1.4, "2,3"))
    body.append(polyline(p.pts([(0, 0.9), (57, 0.9)]), INK, 1.4, "2,3"))
    labels = [(1, 0.005, "≥ 5 mA"), (11, 0.06, "≥ 60 mA"),
              (31, 0.4, "≥ 0.4 A")]
    for v, i, s in labels:
        body.append(text(p.x(v), p.y(i) - 5, s, 10))
    lx = p.right + 10
    notes = [(SRC_INK, None, "lowest the PSE"), (None, None, "must supply"),
             (SRC_INK, "6,3", "classes 7, 8:"), (None, None, "0.8 A"),
             (INK, "2,3", "highest: 0.45 A"), (None, None, "(classes 1–4),"),
             (None, None, "0.9 A (5–8)")]
    for k, (col, dash, s) in enumerate(notes):
        y = p.top + 20 + 16 * k
        if col:
            body.append(line(lx, y - 4, lx + 18, y - 4, col, 2.0, dash))
        body.append(text(lx + 22, y, s, 9))
    return svg(680, int(p.bottom + 48), body, "Power sourcing inrush")


def startup_power():
    rows = [("detection, offset current", 0.032, 0.12),
            ("detection, signature", 0.28, 4.3),
            ("mark event", 1.7, 40),
            ("class event, signature 0", 14.5, 82),
            ("class event, signature 1", 131, 246),
            ("class event, signature 2", 247, 410),
            ("class event, signature 3", 377, 615),
            ("class event, signature 4", 522, 902)]
    n = len(rows)
    p = Plot(190, 20, 440, 22 * n, (0.01, 1000), (0, n), xlog=True)
    body = [p.frame()]
    for k, (name, lo, hi) in enumerate(rows):
        yc = p.y(n - k - 0.5)
        body.append(text(p.left - 8, yc + 4, name, 10, "end"))
        body.append(rect(p.x(lo), yc - 6, p.x(hi) - p.x(lo), 12, POWER))
        body.append(text(p.x(hi) + 5, yc + 4, f"{lo:g}–{hi:g}", 9,
                         fill=GREY))
    body += p.xticks([0.01, 0.1, 1, 10, 100, 1000], "power (mW)",
                     fmt="{:g}")
    body.append(text(10, p.bottom + 58, "Reset: 0 mW. Each bar runs from "
                     "the lowest voltage and current of the step to the "
                     "highest.", 11, fill=GREY))
    return svg(680, int(p.bottom + 70), body, "Power at each step")


if __name__ == "__main__":
    write("peak-power.svg", peak_power())
    write("pd-voltage.svg", pd_voltage())
    write("inrush-pd.svg", inrush_pd())
    write("inrush-pse.svg", inrush_pse())
    write("startup-power.svg", startup_power())
