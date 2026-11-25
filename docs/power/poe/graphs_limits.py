# /// script
# requires-python = ">=3.10"
# ///
"""Write the current, voltage and stress graphs of the Power over Ethernet
pages. Run with:

    uv run docs/power/poe/graphs_limits.py

Writes:

template.svg
    The upper current template of a pair set, with the current limit and
    the overload removal window (monitoring.rst; IEEE 802.3 145.2.10.8,
    145.2.10.9 and Table 145-16).
soa.svg
    The short-circuit operating point of the power sourcing switch against
    lines of constant power (monitoring.rst).
ripple.svg
    The ripple and noise limit against frequency (monitoring.rst; IEEE
    802.3 Table 145-16).
ratings.svg
    Ratings and breakdown voltages of gf180mcu devices against the cable
    voltage (hv-limits.rst).
stresses.svg
    The four stresses on the cable side by duration and voltage
    (hv-limits.rst, isolation.rst).
surge.svg
    The current of a 1500 V, 10/700 us surge into a 90 V clamp
    (hv-limits.rst).

Every number comes from the page that shows the figure.

SPDX-License-Identifier: Apache-2.0
"""

import math

from svgfig import (BAD, BAD_INK, EVP, FILL, GREY, INK, OK, OK_INK, POWER,
                    SRC_INK, Plot, dot, line, polyline, rect, svg, text,
                    write)

K = 0.025          # energy limitation constant, A^2 s


def log_ticks(p, ticks, label):
    """Log-axis ticks with text labels: ticks is [(value, text), ...]."""
    out = []
    for v, s in ticks:
        x = p.x(v)
        out.append(line(x, p.top, x, p.bottom, GREY, 0.5, "2,3"))
        out.append(line(x, p.bottom, x, p.bottom + 5))
        out.append(text(x, p.bottom + 18, s, 12, "middle"))
    out.append(text(p.left + p.w / 2, p.bottom + 36, label, 13, "middle"))
    return out


TIME_TICKS = [(1e-6, "1 µs"), (1e-5, "10 µs"), (1e-4, "100 µs"),
              (1e-3, "1 ms"), (1e-2, "10 ms"), (0.1, "100 ms"), (1, "1 s"),
              (10, "10 s")]


def template():
    p = Plot(70, 30, 560, 300, (1e-6, 10), (0.1, 100), xlog=True,
             ylog=True)
    body = [rect(p.x(1e-6), p.top, p.x(0.05) - p.x(1e-6), p.h, EVP, "none"),
            rect(p.x(0.05), p.top, p.x(10) - p.x(0.05), p.h, OK, "none"),
            rect(p.x(0.05), p.top, p.x(0.075) - p.x(0.05), p.h, BAD, "none")]
    body.append(text(p.x(3e-6), p.y(20), "hardware acts", 11, "middle"))
    body.append(text(p.x(0.7), p.top + 16, "software acts,", 11, "middle"))
    body.append(text(p.x(0.7), p.top + 30, "hardware backstop", 11,
                     "middle"))
    # Current limit held from the start of a fault for at least 6 ms
    # (Type 4) or 10 ms (Type 3) and ended by 75 ms.
    body.append(rect(p.x(1e-5), p.y(1.005), p.x(0.075) - p.x(1e-5),
                     p.y(0.4) - p.y(1.005), "#ffffff", SRC_INK, 1.0, "4,2"))
    body.append(text(p.x(1.2e-5), p.y(0.4) + 14, "current limit "
                     "0.4–1.005 A, held ≥ 6 or 10 ms, ended by 75 ms", 10,
                     fill=SRC_INK))
    body.append(p.frame())
    body += p.yticks([0.1, 0.4, 1, 10, 100], "pair set current (A)",
                     fmt="{:g}")
    body += log_ticks(p, TIME_TICKS, "time since the current rose")
    t1 = K / 1.75 ** 2
    pts = [(1e-6, 50), (1e-5, 50)]
    t = 1e-5
    while t < t1:
        pts.append((t, math.sqrt(K / t)))
        t *= 1.2
    pts += [(t1, 1.75), (0.075, 1.75)]
    body.append(polyline(p.pts(pts + [(0.075, 1.3), (4, 1.3)]),
                         INK, 2.4))
    body.append(polyline(p.pts([(0.075, 1.75), (0.075, 0.85), (10, 0.85)]),
                         GREY, 2.0, "6,3"))
    labels = [(1e-5, 50, "50 A at 10 µs", 8, -6),
              (1e-3, 5, "5 A at 1 ms: I = √(K / t)", 8, -4),
              (t1, 1.75, "1.75 A from 8.2 ms", 6, -6),
              (0.3, 1.3, "Type 4: 1.3 A to 4 s", 0, -6),
              (0.3, 0.85, "Type 3: 0.85 A", 0, 14)]
    for x, y, s, dx, dy in labels:
        body.append(dot(p.x(x), p.y(y), 3))
        body.append(text(p.x(x) + dx, p.y(y) + dy, s, 10))
    body.append(text(p.x(0.062), p.bottom - 8, "50–75 ms: overload removed",
                     10, "end", fill=BAD_INK))
    body.append(text(10, p.bottom + 58, "Type 4 also caps the power at "
                     "99.9 W averaged over up to 4 s.", 11, fill=GREY))
    return svg(680, int(p.bottom + 70), body, "Upper current template")


def soa():
    p = Plot(70, 20, 470, 260, (1, 100), (0.1, 10), xlog=True, ylog=True)
    body = [p.frame()]
    body += p.yticks([0.1, 1, 10], "switch current (A)", fmt="{:g}")
    body += p.xticks([1, 10, 57, 100], "voltage across the switch (V)",
                     fmt="{:g}")
    for pw, dash in ((57, None),):
        pts = [(v, pw / v) for v in (1, 2, 5, 10, 20, 50, 100)
               if 0.1 <= pw / v <= 10]
        v0 = max(1, pw / 10)
        v1 = min(100, pw / 0.1)
        pts = [(v0, pw / v0)] + [q for q in pts if v0 < q[0] < v1] + \
              [(v1, pw / v1)]
        body.append(polyline(p.pts(pts), GREY if dash else SRC_INK, 1.6,
                             dash))
    body.append(text(p.x(8), p.y(57 / 8) + 16, "57 W", 10, fill=SRC_INK))
    body.append(dot(p.x(57), p.y(1.0), 5, BAD_INK))
    body.append(text(p.x(57) - 8, p.y(1.0) + 18, "short at the current "
                     "limit:", 10, "end", fill=BAD_INK))
    body.append(text(p.x(57) - 8, p.y(1.0) + 32, "57 V, 1.0 A for 75 ms, "
                     "4.3 J", 10, "end", fill=BAD_INK))
    for k, s in enumerate(("The switch's", "safe operating", "area for 75 ms",
                           "must contain", "this point.")):
        body.append(text(p.right + 10, p.top + 20 + 15 * k, s, 10))
    return svg(680, int(p.bottom + 48), body, "Switch operating point")


def ripple():
    p = Plot(70, 20, 540, 200, (10, 1e6), (0, 0.6), xlog=True)
    steps = [(10, 500, 0.5), (500, 150e3, 0.2), (150e3, 500e3, 0.15),
             (500e3, 1e6, 0.1)]
    body = []
    for a, b, v in steps:
        body.append(rect(p.x(a), p.y(0.6), p.x(b) - p.x(a), p.y(v)
                         - p.y(0.6), BAD, "none"))
        if v > 0.15:
            body.append(text(p.x(math.sqrt(a * b)), p.y(v) - 6,
                             f"{v:g} Vpp", 10, "middle"))
        else:
            body.append(text(p.x(b) - 4, p.y(v) + (30 if v == 0.1 else 16),
                             f"{v:g} Vpp", 10, "end"))
    body.append(p.frame())
    pts = []
    for a, b, v in steps:
        pts += [(a, v), (b, v)]
    body.append(polyline(p.pts(pts), INK, 2.2))
    body += p.yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
                     "ripple and noise (Vpp)", fmt="{:g}")
    body += log_ticks(p, [(10, "10 Hz"), (100, "100 Hz"), (1e3, "1 kHz"),
                          (1e4, "10 kHz"), (1e5, "100 kHz"),
                          (1e6, "1 MHz")], "frequency")
    body.append(text(p.x(3e3), p.y(0.35), "not allowed", 11, "middle",
                     fill=BAD_INK))
    return svg(680, int(p.bottom + 48), body, "Ripple and noise limit")


def ratings():
    rows = [("3.3 V transistors", 3.63, [("gate oxide", 7, 8.8)]),
            ("5 V transistors", 5.5, []),
            ("6 V transistors", 6.6, [("gate oxide", 12, 16),
                                      ("N+ to p-well", 8.5, 11),
                                      ("P+ to n-well", 8.5, 10.5)]),
            ("n-well to substrate", None, [("", 10, 14)]),
            ("10 V LDMOS", 10, [("drain to source", 13.2, 14.5)]),
            ("vertical PNP", None, [("collector to emitter", 10, 15)]),
            ("MIM 1 fF/µm²", 20, [("", 20, 40)]),
            ("MIM 1.5, 2 fF/µm²", None, [("", 10, 24)])]
    n = sum(max(1, len(r[2])) for r in rows)
    p = Plot(200, 30, 440, 18 * n + 10, (0, 100), (0, n))
    body = [p.frame()]
    k = 0
    for name, rating, bds in rows:
        rh = max(1, len(bds))
        y0 = p.y(n - k)
        body.append(text(p.left - 8, y0 + 13, name, 10, "end"))
        if rating:
            body.append(rect(p.left, y0 + 3, p.x(rating) - p.left, 8, OK,
                             OK_INK, 0.8))
        for j, (bname, lo, typ) in enumerate(bds):
            yy = y0 + 18 * j + 12
            body.append(rect(p.left, yy, p.x(lo) - p.left, 5, POWER, INK,
                             0.6))
            body.append(rect(p.x(lo), yy, p.x(typ) - p.x(lo), 5, FILL, INK,
                             0.6))
            if bname:
                body.append(text(p.x(typ) + 4, yy + 6, bname, 9, fill=GREY))
        body.append(line(p.left, p.y(n - k - rh), p.right,
                         p.y(n - k - rh), GREY, 0.4))
        k += rh
    for v, s, col in ((57, "57 V cable", BAD_INK), (95, "95 V suppressor limit",
                                                    SRC_INK)):
        body.append(line(p.x(v), p.top - 4, p.x(v), p.bottom, col, 1.6,
                         "6,3"))
        body.append(text(p.x(v), p.top - 8, s, 10, "middle", fill=col))
    body += p.xticks([0, 20, 40, 57, 80, 100], "voltage (V)", grid=False)
    legend = [(OK, "rating"), (POWER, "breakdown, minimum"),
              (FILL, "breakdown, up to typical")]
    for j, (fill, s) in enumerate(legend):
        x = 10 + 200 * j
        body.append(rect(x, p.bottom + 50, 16, 9, fill, INK, 0.6))
        body.append(text(x + 22, p.bottom + 59, s, 11))
    return svg(680, int(p.bottom + 70), body, "Device limits")


def stresses():
    p = Plot(80, 30, 520, 260, (1e-8, 1e4), (10, 1e4), xlog=True, ylog=True)
    body = [p.frame()]
    body += p.yticks([10, 100, 1000, 10000], "voltage (V)", fmt="{:g}")
    body += log_ticks(p, [(1e-8, "10 ns"), (1e-6, "1 µs"),
                          (1e-4, "100 µs"), (1e-2, "10 ms"), (1, "1 s"),
                          (100, "100 s"), (1e4, "10⁴ s")], "duration")
    items = [(150e-9, 2000, "HBM ESD: 2 kV on 100 pF,", "τ 150 ns, 0.2 mJ",
              OK_INK, "clamp"),
             (462e-6, 1500, "surge: 1500 V, 40 Ω,", "τ 462 µs, 1.5 J in clamp",
              OK_INK, "clamp"),
             (60, 2250, "isolation: 1500 Vrms or 2250 V DC",
              "for 60 s, or ten 1500 V impulses", BAD_INK, "block"),
             (3e3, 57, "continuous: 57 V", "while powered", BAD_INK,
              "block")]
    for x, v, s1, s2, col, act in items:
        body.append(dot(p.x(x), p.y(v), 6, col))
        anchor = "end" if x > 1 else "start"
        dx = -10 if x > 1 else 10
        if x == 462e-6:
            v = 600
        if x == 60:
            v = 6500
        body.append(text(p.x(x) + dx, p.y(v) - 4, s1, 10, anchor))
        body.append(text(p.x(x) + dx, p.y(v) + 10, s2, 10, anchor))
        body.append(text(p.x(x) + dx, p.y(v) + 24, act, 10, anchor, "bold",
                         col))
    body.append(line(p.x(462e-6), p.y(1500), p.x(462e-6), p.y(90), GREY,
                     1.0, "3,3", "end"))
    body.append(text(p.x(462e-6) + 6, p.y(90) + 4, "90 V at the clamp", 10,
                     fill=GREY))
    return svg(680, int(p.bottom + 48), body, "Stresses on the cable side")


def surge():
    tau, tf = 462.0, 1.6          # µs; tf sets a front of about 5 µs
    p = Plot(70, 20, 560, 220, (0, 1500), (0, 40))
    body = [p.frame()]
    body += p.yticks([0, 10, 17.5, 30, 35, 40], "clamp current (A)",
                     fmt="{:g}")
    body += p.xticks([0, 320, 500, 1000, 1500], "time (µs)", fmt="{:g}")

    def raw(t):
        return math.exp(-t / tau) - math.exp(-t / tf)
    peak = max(raw(t / 10) for t in range(1, 400))
    pts = [(t, 35 * raw(t) / peak) for t in
           [0, 1, 2, 3, 4, 5, 6, 8, 10, 15, 20] + list(range(30, 1501, 10))]
    body.append(polyline(p.pts(pts), SRC_INK, 2.2))
    body.append(line(p.x(320), p.y(17.5), p.x(320), p.bottom, GREY, 0.8,
                     "3,3"))
    body.append(text(p.x(330), p.y(17.5) - 6, "half value at 320 µs", 10))
    body.append(text(p.x(20), p.y(35) - 6, "35 A peak after a 5 µs front",
                     10))
    body.append(text(p.x(700), p.y(30), "1500 V generator, 40 Ω, into a "
                     "90 V clamp:", 10))
    body.append(text(p.x(700), p.y(30) + 14, "about 1.5 J in the clamp", 10))
    return svg(680, int(p.bottom + 48), body, "Surge current")


if __name__ == "__main__":
    write("template.svg", template())
    write("soa.svg", soa())
    write("ripple.svg", ripple())
    write("ratings.svg", ratings())
    write("stresses.svg", stresses())
    write("surge.svg", surge())
