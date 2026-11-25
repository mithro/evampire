# /// script
# requires-python = ">=3.10"
# ///
"""Write the timing graphs of the Power over Ethernet sequence. Run with:

    uv run docs/power/poe/graphs_sequence.py

Writes:

step-times.svg
    The shortest and longest duration of each step for Types 3 and 4,
    laid end to end against the 400 ms limit from detection to full power
    (sequence.rst; IEEE 802.3 Tables 145-14 and 145-16).
class-events.svg
    The class signature current of a class 4 and a class 8 powered device
    in five class events, and the class assigned when the power sourcing
    equipment stops after each event (sequence.rst; IEEE 802.3 Tables
    145-11, 145-24 and 145-26).
mps.svg
    The maintain power signature as pulses of current, and the removal of
    power after the current stops (sequence.rst; IEEE 802.3 Tables 145-16
    and 145-32).
action-window.svg
    A software action placed in the 6 ms to 12 ms window that ends a mark
    event (pse-sequencing.rst).

Every number comes from the page that shows the figure.

SPDX-License-Identifier: Apache-2.0
"""

import math

from svgfig import (BAD, BAD_INK, EVP, FILL, GREY, INK, OK, OK_INK, POWER,
                    SRC_INK, Plot, line, polyline, rect, svg, text, write)

# (step, shortest ms, longest ms) for a powered device of class 5 or 6
# classified with four class events (Tables 145-14 and 145-16).
STEPS = [("class event 1", 88, 105), ("mark", 6, 12),
         ("class event 2", 6, 20), ("mark", 6, 12),
         ("class event 3", 6, 20), ("mark", 6, 12),
         ("class event 4", 6, 20), ("inrush", 50, 75)]


def step_times():
    p = Plot(130, 30, 520, 300, (0, 420), (0, len(STEPS)))
    body = [p.frame()]
    body += p.xticks([0, 100, 200, 300, 400],
                     "time after the end of detection (ms)")
    lo = hi = 0.0
    for k, (name, a, b) in enumerate(STEPS):
        yc = p.y(len(STEPS) - k - 0.5)
        body.append(text(p.left - 8, yc + 4, name, 11, "end"))
        x0 = p.x(hi)
        body.append(rect(x0, yc - 8, p.x(hi + a) - x0, 16, POWER))
        body.append(rect(p.x(hi + a), yc - 8, p.x(hi + b) - p.x(hi + a), 16,
                         "#ffffff", GREY, 1.0, "3,2"))
        lab = f"{a}–{b} ms"
        body.append(text(p.x(hi + b) + 5, yc + 4, lab, 10, "start",
                         fill=GREY))
        lo += a
        hi += b
    body.append(line(p.x(400), p.top, p.x(400), p.bottom, BAD_INK, 1.6,
                     "6,3"))
    body.append(text(p.x(400) - 4, p.top + 14, "full power", 11, "end",
                     fill=BAD_INK))
    body.append(text(p.x(400) - 4, p.top + 28, "by 400 ms", 11, "end",
                     fill=BAD_INK))
    body.append(text(10, p.bottom + 58, f"Solid: shortest duration. Dashed: "
                     f"up to the longest. Total {hi:g} ms without the last mark "
                     "event,", 11, fill=GREY))
    body.append(text(10, p.bottom + 74, "whose limit is not shown. Detection "
                     "takes up to 500 ms per pair set before this.", 11,
                     fill=GREY))
    return svg(680, int(p.bottom + 86), body, "Step durations")


def class_events():
    # Schematic time axis: class events 3 units long, marks 2 units.
    p = Plot(70, 30, 470, 240, (0, 25), (0, 50))
    body = []
    bands = [(1, 4, "0"), (9, 12, "1"), (17, 20, "2"), (26, 30, "3"),
             (36, 44, "4")]
    for a, b, sig in bands:
        body.append(rect(p.left, p.y(b), p.w, p.y(a) - p.y(b), OK, "none"))
        body.append(text(p.right + 6, p.y((a + b) / 2) + 4,
                         f"signature {sig}", 10, fill=OK_INK))
    body.append(p.frame())
    body += p.yticks([0, 10, 20, 30, 40, 50], "current (mA)", grid=False)
    # Event start times: class event k occupies [5k, 5k+3).
    sig4, sig3 = 40, 28
    for curve, col, dash, label in (
            ([sig4] * 5, GREY, "6,3", "class 4"),
            ([sig4, sig4, sig3, sig3, sig3], SRC_INK, None, "class 8")):
        pts = [(0, 0)]
        for k, i in enumerate(curve):
            t0 = 5 * k
            pts += [(t0, 2 if k else 0), (t0, i), (t0 + 3, i), (t0 + 3, 2)]
        pts.append((24.5, 2))
        body.append(polyline(p.pts(pts), col, 2.2, dash))
        body.append(text(p.x(23.2), p.y(curve[-1]) - 6, label, 11, "middle",
                         "bold", col))
    for k in range(5):
        body.append(text(p.x(5 * k + 1.5), p.bottom + 16, f"{k + 1}", 11,
                         "middle"))
    body.append(text(p.x(12), p.bottom + 32, "class event (marks between at "
                     "0.25–4 mA; time not to scale)", 12, "middle"))
    # Where the power sourcing equipment may stop.
    stops = [(1, "3"), (2, "4"), (3, "4"), (4, "6"), (5, "8")]
    yb = p.bottom + 54
    body.append(text(10, yb + 14, "stops after", 11))
    body.append(text(10, yb + 30, "highest class", 11))
    for n, c in stops:
        x = p.x(5 * n - 1)
        body.append(line(x, p.top, x, p.bottom, GREY, 0.8, "2,3"))
        body.append(text(x, yb + 14, f"{n}", 11, "middle"))
        body.append(text(x, yb + 30, c, 11, "middle", "bold"))
    body.append(text(10, yb + 54, "A class 8 device gets class 4 after 2 or "
                     "3 events, 6 after 4 and 8 after 5.", 11, fill=GREY))
    return svg(680, int(yb + 66), body, "Class events")


def mps():
    pulse, gap = 75, 250
    starts = [0, pulse + gap, 2 * (pulse + gap)]
    stop = starts[-1] + pulse
    p = Plot(70, 30, 560, 130, (-50, 1850), (0, 20))
    body = [rect(p.left, p.y(10), p.w, p.bottom - p.y(10), FILL, "none")]
    body.append(p.frame())
    body += p.yticks([0, 10, 20], "PD current (mA)", grid=False)
    pts = [(-50, 0)]
    for s in starts:
        pts += [(s, 0), (s, 14), (s + pulse, 14), (s + pulse, 0)]
    pts.append((1850, 0))
    body.append(polyline(p.pts(pts), SRC_INK, 2.2))
    body.append(text(p.x(1800), p.y(10) + 14, "below 10 mA", 10, "end",
                     fill=GREY))
    body.append(text(p.x(37), p.y(14) - 5, "≥ 75 ms", 10, "middle"))
    body.append(line(p.x(pulse), p.y(17), p.x(pulse + gap), p.y(17), INK,
                     1.0, arrow="both"))
    body.append(text(p.x(pulse + gap / 2), p.y(17) - 5, "gap ≤ 250 ms", 10,
                     "middle"))
    body.append(text(p.x(stop) + 6, p.y(16), "current stops", 10))
    # Port voltage below.
    q = Plot(70, 200, 560, 130, (-50, 1850), (0, 60))
    body.append(q.frame())
    body += q.yticks([0, 20, 40, 54], "port voltage (V)", fmt="{:g}",
                     grid=False)
    off = stop + 360
    body.append(rect(q.x(stop + 320), q.top, q.x(stop + 400)
                     - q.x(stop + 320), q.h, BAD, "none"))
    body.append(q.frame())
    tau = 500 / math.log(54 / 2.8) * 0.8
    vpts = [(-50, 54), (off, 54)]
    t = off
    while t < 1850:
        t += 10
        vpts.append((t, 54 * math.exp(-(t - off) / tau)))
    body.append(polyline(q.pts(vpts), INK, 2.2))
    body.append(line(q.left, q.y(2.8), q.right, q.y(2.8), GREY, 0.8, "3,3"))
    body.append(text(q.x(stop + 360), q.top - 6, "removed 320–400 ms after "
                     "the current stops", 10, "middle", fill=BAD_INK))
    body.append(text(q.right - 4, q.y(2.8) - 4, "2.8 V", 10, "end",
                     fill=GREY))
    body.append(line(q.x(off), q.y(46), q.x(off + 500), q.y(46), INK, 1.0,
                     arrow="both"))
    body.append(text(q.x(off + 250) + 30, q.y(46) - 5, "below 2.8 V within 500 ms",
                     10, "middle"))
    body += q.xticks([0, 400, 800, 1200, 1600], "time (ms)", grid=False)
    body.append(text(10, q.bottom + 58, "Pulse height and the fall are "
                     "schematic. After a long first class event: pulses ≥ 7 ms,",
                     11, fill=GREY))
    body.append(text(10, q.bottom + 74, "gaps ≤ 310 ms. Classes 5 to 8: "
                     "16 mA instead of 10 mA.", 11, fill=GREY))
    return svg(680, int(q.bottom + 86), body, "Maintain power signature")


def action_window():
    p = Plot(40, 40, 600, 60, (0, 14), (0, 1))
    body = [rect(p.x(6), p.top, p.x(12) - p.x(6), p.h, OK, "none"),
            rect(p.x(8), p.top, p.x(10) - p.x(8), p.h, EVP, "none")]
    body.append(p.frame())
    body.append(line(p.x(9), p.top - 6, p.x(9), p.bottom + 6, INK, 2.0))
    body.append(text(p.x(9), p.top - 10, "action aimed at 9 ms", 11,
                     "middle", "bold"))
    body.append(text(p.x(9) + 4, p.y(0.2), "± 1 ms", 10, "start"))
    for a, b in ((6, 8), (10, 12)):
        body.append(text(p.x((a + b) / 2), p.y(0.45), "2 ms margin", 10,
                         "middle", fill=OK_INK))
    body.append(text(p.x(3), p.y(0.45), "too early", 10, "middle",
                     fill=BAD_INK))
    body.append(text(p.x(13), p.y(0.45), "too late", 10, "middle",
                     fill=BAD_INK))
    body += p.xticks([0, 2, 4, 6, 8, 10, 12, 14],
                     "time since the mark event started (ms)", grid=False)
    return svg(680, int(p.bottom + 48), body, "Action window")


if __name__ == "__main__":
    write("step-times.svg", step_times())
    write("class-events.svg", class_events())
    write("mps.svg", mps())
    write("action-window.svg", action_window())
