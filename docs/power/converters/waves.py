# /// script
# requires-python = ">=3.10"
# ///
"""Write the buck and boost waveform figures as SVG files, from the worked
examples on the buck and boost pages.

Run with:

    uv run docs/power/converters/waves.py

SPDX-License-Identifier: Apache-2.0
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from svgplot import (Axes, Svg, square, BLUE, ORANGE, GREEN, RED,  # noqa: E402
                     GREY, INK, FILL_BLUE, FILL_ORANGE, FILL_GREEN, FILL_GREY)

HERE = pathlib.Path(__file__).parent

# Buck worked example (buck.rst).
VIN, VOUT, L_UH, FSW_KHZ = 48.0, 12.0, 47.0, 250.0
T_US = 1000.0 / FSW_KHZ            # 4 µs
D = VOUT / VIN                     # 0.25
IOUT = 25.5 / 12.0                 # 2.125 A
RISE = (VIN - VOUT) / L_UH         # A/µs while S1 is on
FALL = VOUT / L_UH                 # A/µs while S2 is on
RIPPLE = RISE * D * T_US           # 0.766 A


def buck_balance():
    """Inductor voltage and current of the buck example: volt-second balance."""
    s = Svg(640, 400)
    t_end = 2 * T_US
    # Inductor voltage.
    av = Axes(s, (110, 30, 560, 170), (0, t_end), (-20, 45))
    av.frame(xticks=[0, 1, 2, 3, 4, 5, 6, 7, 8], yticks=[-12, 0, 36],
             ylabel="vL (V)", grid=False)
    s.line(av.X(0), av.Y(0), av.X(t_end), av.Y(0), stroke=GREY, dash="3 3")
    pts = []
    for k in range(2):
        t0 = k * T_US
        pts += [(t0, 36), (t0 + D * T_US, 36), (t0 + D * T_US, -12),
                (t0 + T_US, -12)]
    for k in range(2):
        t0 = k * T_US
        s.poly(av.P([(t0, 0), (t0, 36), (t0 + D * T_US, 36),
                     (t0 + D * T_US, 0)]), stroke="none", fill=FILL_ORANGE,
               close=True)
        s.poly(av.P([(t0 + D * T_US, 0), (t0 + D * T_US, -12),
                     (t0 + T_US, -12), (t0 + T_US, 0)]), stroke="none",
               fill=FILL_BLUE, close=True)
    s.poly(av.P(pts), stroke=BLUE)
    s.text(av.X(0.5), av.Y(18), "+36 V\n× 1 µs", size=12)
    s.text(av.X(2.5), av.Y(-6), "−12 V × 3 µs", size=12)
    s.text(av.X(6.5), av.Y(22), "equal areas:\n36 V·µs each", size=12,
           fill=ORANGE)
    # Inductor current.
    ai = Axes(s, (110, 215, 560, 340), (0, t_end), (1.5, 2.7))
    ai.frame(xticks=[0, 1, 2, 3, 4, 5, 6, 7, 8], yticks=[1.742, 2.125, 2.508],
             xlabel="time (µs), 250 kHz, period 4 µs", ylabel="iL (A)",
             grid=False, yfmt=lambda v: f"{v:.3f}")
    lo, hi = IOUT - RIPPLE / 2, IOUT + RIPPLE / 2
    pts = []
    for k in range(2):
        t0 = k * T_US
        pts += [(t0, lo), (t0 + D * T_US, hi)]
    pts.append((t_end, lo))
    s.poly(ai.P(pts), stroke=BLUE)
    s.line(ai.X(0), ai.Y(IOUT), ai.X(t_end), ai.Y(IOUT), stroke=GREY,
           dash="5 4")
    s.text(ai.X(3.3), ai.Y(IOUT) - 9, "average = Iout", size=12,
           fill=GREY)
    s.line(ai.X(5), ai.Y(hi), ai.X(8) + 16, ai.Y(hi), stroke=GREY, width=1,
           dash="2 3")
    x = ai.X(8) + 12
    s.line(x, ai.Y(lo), x, ai.Y(hi), arrow="both", width=1)
    s.text(x + 6, ai.Y(IOUT), "ΔiL =\n0.766 A", size=12, anchor="start")
    s.text(av.X(0.5), 22, "S1 on", size=12, fill=GREY)
    s.text(av.X(2.5), 22, "S2 on", size=12, fill=GREY)
    s.save(HERE / "buck-balance.svg")


def conduction_modes():
    """Inductor current in the four cases of the buck example."""
    s = Svg(560, 470)
    yr = (-0.8, 2.75)
    panels = [
        ("(a) continuous, Iout = 2.125 A", 10, IOUT, "ccm"),
        ("(b) boundary, Iout = 0.383 A", 290, RIPPLE / 2, "ccm"),
        ("(c) discontinuous, diode as S2", 10, None, "dcm"),
        ("(d) synchronous S2 left on", 290, 0.17, "ccm"),
    ]
    for i, (title, x0, avg, kind) in enumerate(panels):
        top = 30 if i < 2 else 255
        a = Axes(s, (x0 + 55, top + 20, x0 + 255, top + 160), (0, 8), yr)
        a.frame(xticks=[0, 4, 8], yticks=[0, 1, 2],
                xlabel="time (µs)" if i >= 2 else "",
                ylabel="iL (A)" if x0 == 10 else "", grid=True)
        s.text(x0 + 145, top + 5, title, size=13, weight="bold")
        s.line(a.X(0), a.Y(0), a.X(8), a.Y(0), stroke=INK, width=1.2)
        if kind == "ccm":
            lo, hi = avg - RIPPLE / 2, avg + RIPPLE / 2
            pts = []
            for k in range(2):
                pts += [(k * T_US, lo), (k * T_US + D * T_US, hi)]
            pts.append((8, lo))
            if lo < 0:
                # Shade the parts of each period with negative current.
                t_up = -lo / RISE
                polys = [[(0, 0), (0, lo), (t_up, 0)]]
                for k in range(2):
                    tz = k * T_US + D * T_US + hi / FALL
                    te = (k + 1) * T_US
                    if te + t_up <= 8:
                        polys.append([(tz, 0), (te, lo), (te + t_up, 0)])
                    else:
                        polys.append([(tz, 0), (te, lo), (te, 0)])
                for poly in polys:
                    s.poly(a.P(poly), stroke="none", fill=FILL_ORANGE,
                           close=True)
                s.text(a.X(4.6), a.Y(-0.55), "negative: flows back",
                       size=12, fill=ORANGE)
            s.poly(a.P(pts), stroke=BLUE)
            s.line(a.X(0), a.Y(avg), a.X(8), a.Y(avg), stroke=GREY,
                   dash="5 4", width=1)
        else:
            # Same slopes, shorter on time: the current reaches zero and
            # stays there until the next period (schematic load).
            peak = 0.5
            t_on = peak / RISE
            t_off = peak / FALL
            pts = []
            for k in range(2):
                t0 = k * T_US
                pts += [(t0, 0), (t0 + t_on, peak), (t0 + t_on + t_off, 0)]
            pts.append((8, 0))
            s.poly(a.P(pts), stroke=BLUE)
            t0 = t_on + t_off
            s.rect(a.X(t0), a.Y(0.35), a.X(T_US) - a.X(t0), a.Y(0) - a.Y(0.35),
                   fill=FILL_GREEN, stroke="none")
            s.text((a.X(t0) + a.X(T_US)) / 2, a.Y(0.6), "iL = 0,\nvL = 0",
                   size=11, fill=GREEN)
    s.save(HERE / "conduction-modes.svg")


def boost_waves():
    """Boost example: gates, switch node, inductor and S2 current."""
    d, t_per = 0.630, 4.0
    iin, rip = 1.5, 0.504
    s = Svg(600, 470)
    rows = [("S1 gate", 30), ("S2 gate", 85), ("switch node", 140),
            ("inductor\ncurrent", 230), ("S2 current", 345)]
    tr = (0, 2 * t_per)
    a1 = Axes(s, (120, 30, 520, 60), tr, (0, 1))
    a2 = Axes(s, (120, 85, 520, 115), tr, (0, 1))
    av = Axes(s, (120, 140, 520, 200), tr, (0, 60))
    ai = Axes(s, (120, 225, 520, 315), tr, (1.1, 1.9))
    a5 = Axes(s, (120, 340, 520, 420), tr, (0, 1.9))
    on = [(k * t_per, (k + d) * t_per) for k in range(2)]
    off = [((k + d) * t_per, (k + 1) * t_per) for k in range(2)]
    square(s, a1, on, 0, 1)
    square(s, a2, off, 0, 1)
    pts = [(0, 0)]
    for t0, t1 in off:
        pts += [(t0, 0), (t0, 54), (t1, 54), (t1, 0)]
    s.poly(av.P(pts), stroke=BLUE)
    s.text(av.X((d + 0.5 * (1 - d)) * t_per), av.Y(54) - 9, "54 V", size=11)
    lo, hi = iin - rip / 2, iin + rip / 2
    pts = []
    for k in range(2):
        pts += [(k * t_per, lo), ((k + d) * t_per, hi)]
    pts.append((2 * t_per, lo))
    s.poly(ai.P(pts), stroke=BLUE)
    s.line(ai.X(0), ai.Y(iin), ai.X(2 * t_per), ai.Y(iin), stroke=GREY,
           dash="5 4", width=1)
    for v in (lo, iin, hi):
        s.text(ai.x1 + 6, ai.Y(v), f"{v:.3f} A", size=11, anchor="start")
    pts = [(0, 0)]
    for t0, t1 in off:
        pts += [(t0, 0), (t0, hi), (t1, lo), (t1, 0)]
    pts.append((2 * t_per, 0))
    s.poly(a5.P(pts), stroke=ORANGE)
    s.line(a5.X(0), a5.Y(0.556), a5.X(2 * t_per), a5.Y(0.556), stroke=GREY,
           dash="5 4", width=1)
    s.text(a5.X(1.0), a5.Y(0.556) - 9, "average 0.556 A = output current",
           size=11, fill=GREY, anchor="start")
    for name, y in rows:
        s.text(112, y + 15, name, size=12, anchor="end")
    s.line(120, 445, 520, 445, stroke=INK, width=1)
    for k in range(3):
        s.line(a1.X(k * t_per), 441, a1.X(k * t_per), 449, stroke=INK)
        s.text(a1.X(k * t_per), 460, f"{k * 4} µs", size=11)
    s.text(a1.X(d * t_per / 2), 22, "D·T = 2.52 µs", size=11)
    s.save(HERE / "boost-waves.svg")


def cap_ripple():
    """Output capacitor current and voltage ripple of the buck example."""
    c_uf = 22.0
    s = Svg(600, 395)
    t_end = 2 * T_US
    ai = Axes(s, (110, 30, 520, 160), (0, t_end), (-0.5, 0.5))
    ai.frame(xticks=range(9), yticks=[-0.383, 0, 0.383], ylabel="iC (A)",
             grid=False, yfmt=lambda v: f"{v:+.3f}".replace("-", "−")
             if v else "0")
    pts, vs = [], []
    v, dt, t = 0.0, 0.01, 0.0
    while t <= t_end + 1e-9:
        ph = t % T_US
        i = (-RIPPLE / 2 + RISE * ph if ph < D * T_US
             else RIPPLE / 2 - FALL * (ph - D * T_US))
        pts.append((t, i))
        vs.append((t, v))
        v += i * dt / c_uf * 1e3          # mV, with t in µs and C in µF
        t += dt
    s.line(ai.X(0), ai.Y(0), ai.X(t_end), ai.Y(0), stroke=GREY, dash="3 3",
           width=1)
    s.poly(ai.P(pts), stroke=BLUE)
    mean = sum(x for _, x in vs) / len(vs)
    vs = [(t, x - mean) for t, x in vs]
    lo, hi = min(x for _, x in vs), max(x for _, x in vs)
    av = Axes(s, (110, 200, 520, 320), (0, t_end), (-12, 12))
    av.frame(xticks=range(9), yticks=[round(lo, 1), 0, round(hi, 1)],
             ylabel="ripple (mV)", grid=False,
             xlabel="time (µs), 250 kHz, 22 µF",
             yfmt=lambda x: f"{x:+.1f}".replace("-", "−") if x else "0")
    s.poly(av.P(vs), stroke=ORANGE)
    x = av.X(t_end) + 12
    s.line(x, av.Y(lo), x, av.Y(hi), arrow="both", width=1)
    s.text(x + 6, av.Y(0), f"{hi - lo:.1f} mV\npeak to\npeak", size=11,
           anchor="start")
    s.text(ai.X(t_end) + 8, ai.Y(0), "iL − Iout", size=11, anchor="start",
           fill=BLUE)
    s.text(300, 382, "the voltage rises while iC is positive and falls "
           "while it is negative", size=11, fill=GREY)
    s.save(HERE / "cap-ripple.svg")


FIGURES = {
    "buck-balance": buck_balance,
    "conduction-modes": conduction_modes,
    "boost-waves": boost_waves,
    "cap-ripple": cap_ripple,
}

if __name__ == "__main__":
    for n in sys.argv[1:] or list(FIGURES):
        FIGURES[n]()
