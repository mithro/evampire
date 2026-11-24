# /// script
# requires-python = ">=3.10"
# ///
"""Draw the graphs for the magnetics pages as SVG files.

Usage: uv run docs/ethernet/magnetics/plots.py

Writes, next to this script:

- cm-dm.svg: the two wires of a pair, their difference and their average;
- balance.svg: the impedance-balance limit of 1000BASE-T;
- impulses.svg: the 1.2/50 us and 10/700 us isolation impulses;
- droop.svg: the fraction of a constant level left against time;
- events.svg: peak voltage against time scale of each event at the port;
- cm-divider.svg: the share of a cable common-mode voltage that reaches
  the chip through coupling capacitors;
- rl-mask.svg, rl-caps.svg, rl-parasitic.svg: the 1000BASE-T return-loss
  limit, alone, with coupling capacitors and with parasitic capacitance;
- psd.svg: the power spectrum of the symbol stream and the corners;
- zc.svg: impedance of the 1000 pF termination capacitor;
- cw-range.svg: the lower limits on the coupling capacitor.

Every value is one quoted on the page that shows the graph.

SPDX-License-Identifier: Apache-2.0
"""

import math
import pathlib

HERE = pathlib.Path(__file__).parent

INK = "#222222"
GREY = "#7f7f7f"
LIGHT = "#d9d9d9"
BLUE = "#1f4e79"
ORANGE = "#c55a11"
GREEN = "#548235"
RED = "#c00000"
FONT = 'font-family="Helvetica, Arial, sans-serif"'


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" '
            f'height="{h}" viewBox="0 0 {w} {h}" {FONT} font-size="13">\n'
            f'<rect width="{w}" height="{h}" fill="white"/>\n'
            + "\n".join(body) + "\n</svg>\n")


def text(x, y, s, anchor="start", size=13, weight="normal", fill=INK,
         rotate=None):
    r = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}"{r}>'
            f'{s}</text>')


def line(x1, y1, x2, y2, stroke=INK, width=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{width}"{d}/>')


def poly(pts, stroke, width=2.0, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{width}"{d}/>')


def dot(x, y, fill=INK, r=3.5):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"/>'


class Axes:
    """A plot area with linear or log axes, ticks and labels."""

    def __init__(self, left, top, width, height, xr, yr, xlog=False,
                 ylog=False):
        self.l, self.t, self.w, self.h = left, top, width, height
        self.xr, self.yr, self.xlog, self.ylog = xr, yr, xlog, ylog

    def _f(self, v, r, log):
        if log:
            return (math.log10(v) - math.log10(r[0])) / (
                math.log10(r[1]) - math.log10(r[0]))
        return (v - r[0]) / (r[1] - r[0])

    def x(self, v):
        return self.l + self._f(v, self.xr, self.xlog) * self.w

    def y(self, v):
        return self.t + self.h - self._f(v, self.yr, self.ylog) * self.h

    def pts(self, xs, f):
        return [(self.x(v), self.y(f(v))) for v in xs]

    def frame(self, xticks, yticks, xlabel, ylabel, grid=True):
        out = []
        b = self.t + self.h
        for v, lab in xticks:
            if grid:
                out.append(line(self.x(v), self.t, self.x(v), b, LIGHT))
            out.append(line(self.x(v), b, self.x(v), b + 5))
            out.append(text(self.x(v), b + 19, lab, "middle", 12))
        for v, lab in yticks:
            if grid:
                out.append(line(self.l, self.y(v), self.l + self.w,
                                self.y(v), LIGHT))
            out.append(line(self.l - 5, self.y(v), self.l, self.y(v)))
            out.append(text(self.l - 8, self.y(v) + 4, lab, "end", 12))
        out.append(f'<rect x="{self.l}" y="{self.t}" width="{self.w}" '
                   f'height="{self.h}" fill="none" stroke="{INK}"/>')
        out.append(text(self.l + self.w / 2, b + 38, xlabel, "middle"))
        out.append(text(self.l - 46, self.t + self.h / 2, ylabel, "middle",
                        rotate=-90))
        return out


def logspace(a, b, n=300):
    la, lb = math.log10(a), math.log10(b)
    return [10 ** (la + (lb - la) * k / n) for k in range(n + 1)]


def linspace(a, b, n=300):
    return [a + (b - a) * k / n for k in range(n + 1)]


# ---------------------------------------------------------------------------

def cm_dm():
    """Schematic: two wires = common mode +/- half the data."""
    w, h = 640, 400

    def data(t):
        bits = [1, -1, -1, 1, -1, 1, 1, -1]
        return 0.5 * bits[min(int(t), len(bits) - 1)]

    def cm(t):
        return 0.6 * math.sin(2 * math.pi * t / 6.5)

    ts = linspace(0, 8, 800)
    b = []
    a1 = Axes(80, 26, 540, 150, (0, 8), (-1.3, 1.3))
    b += a1.frame([], [(0, "0")], "", "voltage (schematic)", grid=False)
    b.append(poly(a1.pts(ts, lambda t: cm(t) + data(t)), BLUE))
    b.append(poly(a1.pts(ts, lambda t: cm(t) - data(t)), ORANGE))
    b.append(text(a1.l, a1.t - 8, "Each wire against ground", size=12,
                  weight="bold"))
    b.append(text(a1.x(8) - 6, a1.y(0.55), "wire −", "end", 12,
                  fill=ORANGE))
    b.append(text(a1.x(8) - 6, a1.y(-0.35), "wire +", "end", 12, fill=BLUE))

    a2 = Axes(80, 222, 540, 130, (0, 8), (-1.3, 1.3))
    b += a2.frame([], [(0, "0")], "time (schematic)", "voltage (schematic)",
                  grid=False)
    b.append(poly(a2.pts(ts, lambda t: 2 * data(t)), INK, 2.2))
    b.append(poly(a2.pts(ts, cm), GREEN, 2.0, dash="6,4"))
    b.append(text(a2.l, a2.t - 8,
                  "Difference and average of the two wires", size=12,
                  weight="bold"))
    b.append(text(a2.x(8) - 6, a2.y(1.1), "difference: the data", "end",
                  12))
    b.append(text(a2.x(8) - 6, a2.y(-1.15),
                  "average: the interference", "end", 12, fill=GREEN))
    return svg(w, h, b)


def balance():
    w, h = 640, 330
    a = Axes(80, 20, 520, 240, (1, 100), (20, 70), xlog=True)
    b = a.frame([(1, "1"), (2, "2"), (5, "5"), (10, "10"), (20, "20"),
                 (50, "50"), (100, "100")],
                [(v, str(v)) for v in range(20, 71, 10)],
                "frequency (MHz)", "impedance balance (dB)")
    f = logspace(1, 100)
    lim = lambda v: 34 - 19.2 * math.log10(v / 50)
    # Allowed region above the limit.
    pts = a.pts(f, lim) + [(a.x(100), a.y(70)), (a.x(1), a.y(70))]
    b.append('<polygon points="%s" fill="#e2efda" stroke="none"/>' % " ".join(
        f"{x:.1f},{y:.1f}" for x, y in pts))
    b.append(poly(a.pts(f, lim), INK, 2.2))
    b.append(text(a.x(3), a.y(64), "required: above the line", size=12,
                  fill=GREEN))
    for v, s, dx in ((1, "66.6 dB at 1 MHz", 8), (100, "28.2 dB at 100 MHz",
                                                    -8)):
        b.append(dot(a.x(v), a.y(lim(v))))
        b.append(text(a.x(v) + dx, a.y(lim(v) - (10 if v == 1 else 2.5)), s,
                      "start" if dx > 0 else "end", 12))
    b.append(text(a.x(1.5), a.y(23),
                  "34 − 19.2 log10(f / 50 MHz)", size=12))
    return svg(w, h, b)


def impulses():
    """Double-exponential impulses with the stated front and half time."""
    w, h = 640, 330

    def shape(t1, t2):
        # exp(-t/a) - exp(-t/b), normalised to a peak of 1. For the
        # 1.2/50 us impulse a = 68.2 us and b = 0.405 us give the stated
        # front and half-value times; the same ratios are used for 10/700.
        a, bb = t2 / 0.733, t1 / 2.96
        ts = linspace(0, 1000, 4000)
        v = [math.exp(-t / a) - math.exp(-t / bb) for t in ts]
        peak = max(v)
        return ts, [x / peak for x in v]

    a = Axes(80, 20, 520, 240, (0, 1000), (0, 2.6))
    b = a.frame([(v, str(v)) for v in range(0, 1001, 200)],
                [(v, f"{v:g}") for v in (0, 0.5, 1, 1.5, 2, 2.5)],
                "time (µs)", "voltage (kV)")
    for t1, t2, pk, col, lab, lx, ly in ((1.2, 50, 2.4, BLUE,
                                       "1.2/50 µs, 2400 V: port without "
                                       "Power over Ethernet", 20, 2.3),
                                      (10, 700, 1.5, ORANGE,
                                       "10/700 µs, 1500 V: port with Power "
                                       "over Ethernet", 250, 1.38)):
        ts, v = shape(t1, t2)
        b.append(poly([(a.x(t), a.y(pk * x)) for t, x in zip(ts, v)], col,
                      2.2))
        b.append(text(a.x(lx), a.y(ly), lab, size=12, fill=col))
    b.append(line(a.x(0), a.y(2.121), a.x(1000), a.y(2.121), RED, 1.4,
                  dash="6,4"))
    b.append(text(a.x(990), a.y(2.121) - 6,
                  "peak of the 1500 V rms test: 2121 V", "end", 12,
                  fill=RED))
    return svg(w, h, b)


def droop():
    w, h = 640, 340
    a = Axes(80, 20, 520, 250, (0, 2.0), (0, 100))
    b = a.frame([(v, f"{v:g}") for v in (0, 0.5, 1.0, 1.5, 2.0)],
                [(v, str(v)) for v in range(0, 101, 20)],
                "time after the start of a constant level (µs)",
                "voltage remaining (%)")
    ts = linspace(0, 2.0)
    for tau, col, lab, y in ((1.6, ORANGE, "τ = 1.6 µs (80 µH, the minimum)",
                              18),
                             (7.0, BLUE, "τ = 7.0 µs (350 µH)", 86)):
        b.append(poly(a.pts(ts, lambda t: 100 * math.exp(-t / tau)), col,
                      2.2))
        b.append(text(a.x(1.98), a.y(y), lab, "end", 12, fill=col))
    b.append(line(a.x(0.5), a.t, a.x(0.5), a.t + a.h, RED, 1.4, "6,4"))
    b.append(line(a.l, a.y(73.1), a.l + a.w, a.y(73.1), RED, 1.4, "6,4"))
    b.append(text(a.x(0.52), a.y(3), "500 ns", size=12, fill=RED))
    b.append(text(a.x(1.98), a.y(66), "73.1 % must remain", "end", 12,
                  fill=RED))
    b.append(dot(a.x(0.5), a.y(100 * math.exp(-0.5 / 7.0)), BLUE))
    b.append(text(a.x(0.5) + 8, a.y(93) - 6, "93 %", size=12, fill=BLUE))
    b.append(dot(a.x(0.5), a.y(100 * math.exp(-0.5 / 1.6)), ORANGE))
    return svg(w, h, b)


def events():
    w, h = 640, 380
    a = Axes(80, 20, 530, 280, (1e-9, 100), (0, 9), xlog=True)
    xt = [(1e-9, "1 ns"), (1e-7, "100 ns"), (1e-5, "10 µs"),
          (1e-3, "1 ms"), (1e-1, "100 ms"), (10, "10 s")]
    b = a.frame(xt, [(v, str(v)) for v in range(0, 10)],
                "time scale of the event (log scale)", "peak voltage (kV)")
    ev = [  # (time s, kV, label, dx, dy, anchor, colour)
        (1e-7, 8, "system-level discharge, 8 kV, about 100 ns", 8, 4,
         "start", RED),
        (6e-7, 5, "charged cable, up to 5 kV, over 600 ns", 60, 4,
         "start", RED),
        (50e-6, 4, "surge, 4 kV, 1.2/50 µs", 8, 4, "start", RED),
        (50e-9, 2, "fast transient, 2 kV, 5/50 ns", -4, -12, "start", RED),
        (200e-9, 2, "human-body model, 2 kV, about 200 ns", 8, 30, "start",
         BLUE),
        (50e-6, 2.4, "isolation impulse, 2.4 kV, 50 µs", 8, 18, "start",
         GREY),
        (60, 2.25, "isolation tests, 2.1 kV and 2.25 kV, 60 s", 0, -14,
         "end", GREY),
    ]
    for t, v, lab, dx, dy, anc, col in ev:
        b.append(dot(a.x(t), a.y(v), col, 4.5))
        b.append(text(a.x(t) + dx, a.y(v) + dy, lab, anc, 12, fill=col))
    b.append(dot(a.x(60), a.y(2.121), GREY, 4.5))
    # Arrow on the charged cable: longer than 600 ns.
    b.append(line(a.x(6e-7), a.y(5), a.x(6e-6), a.y(5), RED, 1.4, "4,3"))
    return svg(w, h, b)


def cm_divider():
    w, h = 640, 330
    cw, r = 33e-9, 1e3
    a = Axes(80, 20, 520, 240, (10, 1e7), (0.001, 1), xlog=True, ylog=True)
    b = a.frame([(10, "10 Hz"), (100, "100 Hz"), (1e3, "1 kHz"),
                 (1e4, "10 kHz"), (1e5, "100 kHz"), (1e6, "1 MHz"),
                 (1e7, "10 MHz")],
                [(0.001, "0.001"), (0.01, "0.01"), (0.1, "0.1"), (1, "1")],
                "frequency of the common-mode voltage", "V_chip / V_cable")
    f = logspace(10, 1e7)

    def ratio(v):
        x = 1 / (2 * math.pi * v * 2 * cw)
        return 1 / math.sqrt(1 + (x / r) ** 2)

    b.append(poly(a.pts(f, ratio), BLUE, 2.2))
    b.append(dot(a.x(50), a.y(ratio(50)), RED))
    b.append(text(a.x(50) + 10, a.y(ratio(50)) + 5,
                  "50 Hz: 0.021 (about 2 %)", size=12, fill=RED))
    b.append(text(a.x(3e3), a.y(0.6),
                  "signal frequencies: almost all of it", size=12))
    b.append(text(a.x(12), a.y(0.0016), "C_w = 33 nF per wire, R_cm = 1 kΩ",
                  size=12, fill=GREY))
    return svg(w, h, b)


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
    b.append(text(a.x(98), a.y(10.5),
                  "10 − 20 log10(f / 80 MHz), 8.1 dB at 100 MHz", "end",
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
    a = Axes(80, 20, 520, 240, (10, 1e8), (1, 1e7), xlog=True, ylog=True)
    b = a.frame([(10, "10 Hz"), (1e3, "1 kHz"), (1e5, "100 kHz"),
                 (1e7, "10 MHz")],
                [(1, "1"), (100, "100"), (1e4, "10 k"), (1e6, "1 M")],
                "frequency", "|Z_C| (Ω)")
    f = logspace(10, 1e8)
    b.append(poly(a.pts(f, lambda v: 1 / (2 * math.pi * v * C)), BLUE, 2.2))
    for v, lab, dx, dy in ((50, "3.2 MΩ at 50 Hz: nearly open", 10, -2),
                           (30e6, "5.3 Ω at 30 MHz", -10, 20)):
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


if __name__ == "__main__":
    for name, fn in (("cm-dm", cm_dm), ("balance", balance),
                     ("impulses", impulses), ("droop", droop),
                     ("events", events), ("cm-divider", cm_divider),
                     ("rl-mask", rl_mask), ("rl-caps", rl_caps),
                     ("rl-parasitic", rl_parasitic), ("psd", psd),
                     ("zc", zc), ("cw-range", cw_range)):
        (HERE / f"{name}.svg").write_text(fn())
