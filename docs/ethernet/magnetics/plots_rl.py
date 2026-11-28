"""Return-loss, spectrum, impedance and capacitor-range graphs for the
magnetics pages. Called from plots.py.

SPDX-License-Identifier: Apache-2.0
"""

import math

from plotkit import (INK, GREY, BLUE, ORANGE, GREEN, RED, svg, text, line,
    poly, dot, logspace, Axes)


def rl_limit(f):
    """1000BASE-T return-loss limit in dB, f in MHz."""
    return 16.0 if f <= 40 else 10 - 20 * math.log10(f / 80)


def rl_axes(ymax=60):
    a = Axes(80, 20, 520, 250, (1, 100), (0, ymax), xlog=True)
    b = a.frame([(1, "1"), (2, "2"), (5, "5"), (10, "10"), (20, "20"),
                 (40, "40"), (100, "100")],
                [(v, str(v)) for v in range(0, ymax + 1, 10)],
                "frequency (MHz)", "return loss (dB)")
    f = logspace(1, 100)
    # Forbidden region below the limit.
    pts = a.pts(f, rl_limit) + [(a.x(100), a.y(0)), (a.x(1), a.y(0))]
    b.append('<polygon points="%s" fill="#f4cccc" stroke="none"/>' % " ".join(
        f"{x:.1f},{y:.1f}" for x, y in pts))
    b.append(poly(a.pts(f, rl_limit), RED, 2.2))
    return a, b, f


def rl_mask():
    w, h = 640, 340
    a, b, f = rl_axes(30)
    b.append(text(a.x(1.1), a.y(18), "16 dB from 1 MHz to 40 MHz", size=12,
                  fill=RED))
    b.append(text(a.x(38), a.y(11.5),
                  "then 10 − 20 log10(f / 80 MHz): 8.1 dB at 100 MHz", "end",
                  12, fill=RED))
    b.append(text(a.x(3), a.y(6), "not allowed", size=12, fill=RED))
    b.append(text(a.x(3), a.y(25), "allowed", size=12, fill=GREEN))
    return svg(w, h, b)


def rl_caps():
    w, h = 640, 340
    a, b, f = rl_axes(60)

    def rl(fm, cw):
        x = 1 / (2 * math.pi * fm * 1e6 * cw / 2)
        g = x / math.sqrt(200 ** 2 + x ** 2)
        return min(-20 * math.log10(g), 60)

    cols = (RED, ORANGE, BLUE, GREEN, GREY)
    for (cw, lab), col in zip(((9.9e-9, "9.9 nF"), (16e-9, "16 nF"),
                               (33e-9, "33 nF"), (70e-9, "70 nF"),
                               (100e-9, "100 nF")), cols):
        dash = None if cw > 1e-8 else "5,3"
        b.append(poly(a.pts(f, lambda v: rl(v, cw)), col, 1.8, dash=dash))
        k = cols.index(col)
        yl = a.y(38) + 16 * k
        b.append(line(a.x(18), yl - 4, a.x(26), yl - 4, col, 1.8, dash))
        b.append(text(a.x(27), yl, f"C_w = {lab}", size=11, fill=col))
    b.append(text(a.x(98), a.y(19), "limit", "end", 12, fill=RED))
    return svg(w, h, b)


def rl_parasitic():
    w, h = 640, 340
    a, b, f = rl_axes(60)

    def rl(fm, cd):
        x = 2 * math.pi * fm * 1e6 * 100 * cd
        g = x / math.sqrt(4 + x ** 2)
        return min(-20 * math.log10(g), 60)

    b.append(poly(a.pts(f, lambda v: rl(v, 12.8e-12)), BLUE, 2.2))
    b.append(dot(a.x(40), a.y(16), BLUE))
    b.append(text(a.x(40) - 8, a.y(16) + 20, "touches the limit at 40 MHz",
                  "end", 12, fill=BLUE))
    b.append(text(a.x(2), a.y(50), "C_d = 12.8 pF across the pair", size=12,
                  fill=BLUE))
    return svg(w, h, b)


def psd():
    w, h = 640, 340
    T = 8e-9
    a = Axes(80, 20, 520, 250, (1e4, 2.5e8), (-40, 5), xlog=True)
    b = a.frame([(1e4, "10 kHz"), (1e5, "100 kHz"), (1e6, "1 MHz"),
                 (1e7, "10 MHz"), (1e8, "100 MHz")],
                [(v, str(v)) for v in range(-40, 1, 10)],
                "frequency", "power spectrum relative to DC (dB)")

    def db(v):
        x = math.pi * v * T
        sc = 1.0 if x == 0 else (math.sin(x) / x) ** 2
        return max(10 * math.log10(max(sc, 1e-6)), -40)

    fc = 99.5e3
    fl = logspace(1e4, fc, 50)
    pts = a.pts(fl, db) + [(a.x(fc), a.y(-40)), (a.x(1e4), a.y(-40))]
    b.append('<polygon points="%s" fill="#f8cbad" stroke="none"/>' % " ".join(
        f"{x:.1f},{y:.1f}" for x, y in pts))
    b.append(poly(a.pts(logspace(1e4, 2.5e8, 600), db), BLUE, 2.0))
    for fcx, lab in ((99.5e3, "99.5 kHz (16 nF)"), (48.2e3, "48.2 kHz"),
                     (22.7e3, "22.7 kHz"), (15.9e3, "15.9 kHz")):
        b.append(line(a.x(fcx), a.y(5), a.x(fcx), a.y(-40), GREY, 0.8,
                      "4,3"))
    b.append(text(a.x(99.5e3) + 6, a.y(-20), "below 99.5 kHz:", size=12,
                  fill=ORANGE))
    b.append(text(a.x(99.5e3) + 6, a.y(-20) + 15, "0.16 % of the power",
                  size=12, fill=ORANGE))
    b.append(text(a.x(1.1e5), a.y(-33), "dashed: corners at 15.9, 22.7,",
                  size=11, fill=GREY))
    b.append(text(a.x(1.1e5), a.y(-33) + 14, "48.2 and 99.5 kHz", size=11,
                  fill=GREY))
    b.append(text(a.x(2e6), a.y(-5), "T sinc²(fT), T = 8 ns", size=12,
                  fill=BLUE))
    return svg(w, h, b)


def zc():
    w, h = 640, 330
    C = 1e-9
    a = Axes(80, 20, 520, 240, (10, 1e8), (0.1, 1e8), xlog=True, ylog=True)
    b = a.frame([(10, "10 Hz"), (1e3, "1 kHz"), (1e5, "100 kHz"),
                 (1e7, "10 MHz")],
                [(1, "1"), (100, "100"), (1e4, "10 k"), (1e6, "1 M")],
                "frequency", "|Z_C| (Ω)")
    f = logspace(10, 1e8)
    b.append(poly(a.pts(f, lambda v: 1 / (2 * math.pi * v * C)), BLUE, 2.2))
    for v, lab, dx, dy in ((50, "3.2 MΩ at 50 Hz: nearly open", 10, -2),
                           (30e6, "5.3 Ω at 30 MHz", -10, 34)):
        z = 1 / (2 * math.pi * v * C)
        b.append(dot(a.x(v), a.y(z), RED))
        b.append(text(a.x(v) + dx, a.y(z) + dy, lab,
                      "start" if dx > 0 else "end", 12, fill=RED))
    b.append(text(a.x(1e5), a.y(3e6), "C = 1000 pF", size=12, fill=BLUE))
    return svg(w, h, b)


def cw_range():
    w, h = 640, 200
    a = Axes(40, 60, 560, 0.001, (5, 150), (0, 1), xlog=True)
    b = []
    y = 100
    b.append(f'<rect x="{a.x(33):.1f}" y="{y - 22}" '
             f'width="{a.x(100) - a.x(33):.1f}" height="44" '
             'fill="#e2efda" stroke="none"/>')
    b.append(text((a.x(33) + a.x(100)) / 2, y + 40,
                  "working range, 33 nF to 100 nF", "middle", 12,
                  fill=GREEN))
    b.append(line(a.x(5), y, a.x(150), y, INK, 1.5))
    for v in (5, 10, 20, 50, 100, 150):
        b.append(line(a.x(v), y, a.x(v), y + 6))
        b.append(text(a.x(v), y + 20, f"{v:g}", "middle", 11))
    b.append(text(a.x(150), y + 60, "C_w per wire (nF, log scale)", "end",
                  12))
    marks = ((9.9, "return loss", -1), (16, "droop", 1),
             (24, "PoE 100BASE-TX τ", -1), (30.4, "phase", 1),
             (70, "like magnetics", -1))
    for v, lab, up in marks:
        b.append(line(a.x(v), y - 12, a.x(v), y + 12, RED, 2))
        b.append(text(a.x(v), y - 18 if up < 0 else y - 34, f"{lab}, {v:g}",
                      "middle", 11, fill=RED))
    return svg(w, h, b)
