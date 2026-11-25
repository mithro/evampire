# /// script
# requires-python = ">=3.10"
# ///
"""Write the waveform figures of the control page as SVG files. Most are
schematic: the shapes follow the text, not a simulation.

Run with:

    uv run docs/power/converters/control_waves.py

SPDX-License-Identifier: Apache-2.0
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from svgplot import (Axes, Svg, square, BLUE, ORANGE, GREEN, RED,  # noqa: E402
                     GREY, INK, FILL_BLUE, FILL_ORANGE, FILL_GREEN, FILL_GREY)

HERE = pathlib.Path(__file__).parent


def pwm():
    """Analogue PWM (ramp and control voltage) and digital PWM (counter)."""
    s = Svg(560, 560)
    n = 3
    s.text(280, 14, "(a) Analogue: a ramp compared with a control voltage",
           size=13, weight="bold")
    a = Axes(s, (110, 35, 540, 165), (0, n), (0, 1.1))
    a.frame(yticks=[], grid=False)
    pts = []
    for k in range(n):
        pts += [(k, 0.05), (k + 1, 1.0), (k + 1, 0.05)]
    s.poly(a.P(pts[:-1]), stroke=GREY, width=1.6)
    for vc, col, name in ((0.35, ORANGE, "Vc low"), (0.75, GREEN, "Vc high")):
        s.line(a.X(0), a.Y(vc), a.X(n), a.Y(vc), stroke=col, dash="6 4",
               width=1.6)
        s.text(a.X(0) - 8, a.Y(vc), name, size=12, anchor="end", fill=col)
    s.text(a.X(0) - 8, a.Y(0.98), "ramp", size=12, anchor="end", fill=GREY)
    for i, (vc, col, name) in enumerate(((0.35, ORANGE, "gate, Vc low"),
                                          (0.75, GREEN, "gate, Vc high"))):
        g = Axes(s, (110, 185 + i * 45, 540, 215 + i * 45), (0, n), (0, 1))
        d = (vc - 0.05) / 0.95
        square(s, g, [(k, k + d) for k in range(n)], 0, 1, stroke=col)
        s.text(102, (g.y0 + g.y1) / 2, name, size=12, anchor="end", fill=col)
    s.text(325, 290, "on at the start of each period, off where the ramp "
           "crosses Vc", size=12, fill=GREY)

    s.text(280, 325, "(b) Digital: a counter compared with a register",
           size=13, weight="bold")
    steps = 8
    cmp_v = 3
    c = Axes(s, (110, 345, 540, 465), (0, n), (0, steps))
    c.frame(yticks=[0, 4, 8], ylabel="", grid=False)
    pts = []
    for k in range(n):
        for j in range(steps):
            t0 = k + j / steps
            pts += [(t0, j), (t0 + 1 / steps, j)]
    s.poly(c.P(pts), stroke=GREY, width=1.6)
    s.line(c.X(0), c.Y(cmp_v), c.X(n), c.Y(cmp_v), stroke=ORANGE, dash="6 4",
           width=1.6)
    s.text(c.X(0) - 30, c.Y(cmp_v), "compare\nregister", size=12,
           anchor="end", fill=ORANGE)
    s.text(c.X(0) - 30, c.Y(6.5), "counter", size=12, anchor="end",
           fill=GREY)
    g = Axes(s, (110, 485, 540, 515), (0, n), (0, 1))
    square(s, g, [(k, k + cmp_v / steps) for k in range(n)], 0, 1)
    s.text(102, 500, "gate", size=12, anchor="end", fill=BLUE)
    for k in range(n + 1):
        for y0, y1 in ((30, 305), (340, 520)):
            s.line(c.X(k), y0, c.X(k), y1, stroke="#cccccc", width=1,
                   dash="2 3")
    s.text(325, 540, "time: three switching periods; gate on while "
           "counter < register", size=12, fill=GREY)
    s.save(HERE / "pwm.svg")


def peak_current(m1, m2, ma, ic, i0, periods):
    """Event simulation of peak current-mode control over whole periods.

    The current rises at m1 from the clock edge until it reaches the
    control level ic less the compensation ramp ma*t, then falls at m2.
    Times and currents are in units of the period and of the ramp.
    Returns the polyline points and the list of on times.
    """
    pts = [(0.0, i0)]
    i = i0
    ons = []
    for k in range(periods):
        # i + m1*t = ic - ma*t  ->  t = (ic - i) / (m1 + ma)
        t_on = min(max((ic - i) / (m1 + ma), 0.0), 1.0)
        i_pk = i + m1 * t_on
        i_end = i_pk - m2 * (1 - t_on)
        pts += [(k + t_on, i_pk), (k + 1, i_end)]
        ons.append(t_on)
        i = i_end
    return pts, ons


def subharmonic():
    """Peak current-mode control above D = 0.5, without and with slope
    compensation (schematic units)."""
    s = Svg(560, 450)
    m1, m2 = 1.0, 1.5          # rising and falling slopes, D = 0.6
    d = m2 / (m1 + m2)
    periods = 6
    for row, (ma, title) in enumerate(((0.0, "(a) No slope compensation: "
                                        "the disturbance grows"),
                                       (0.75, "(b) Compensation ramp of half "
                                        "the down-slope: it decays"))):
        top = 20 + row * 205
        a = Axes(s, (60, top + 15, 540, top + 150), (0, periods),
                 (-0.05, 1.6))
        a.frame(xticks=range(periods + 1), yticks=[], grid=True,
                xlabel="time (switching periods)" if row else "",
                ylabel="iL", size=13)
        s.text(300, top, title, size=13, weight="bold")
        ic = 1.0 + ma * d       # level that gives the same steady state
        i_ss = 1.0 - m1 * d     # steady valley current
        pts, _ = peak_current(m1, m2, ma, ic, i_ss + 0.03, periods)
        ref, _ = peak_current(m1, m2, ma, ic, i_ss, periods)
        s.poly(a.P(ref), stroke=GREY, width=1.2, dash="4 3")
        s.poly(a.P(pts), stroke=BLUE)
        # Control level, falling with the compensation ramp.
        lvl = []
        for k in range(periods):
            lvl += [(k, ic), (k + 1, ic - ma), (k + 1, ic)]
        s.poly(a.P(lvl[:-1]), stroke=ORANGE, width=1.4, dash="6 4")
    s.text(300, 438, "blue: disturbed current; grey dashed: steady state; "
           "orange: turn-off level", size=12, fill=GREY)
    s.save(HERE / "subharmonic.svg")


def rhp_step():
    """Boost response to a step increase of duty cycle: the output first
    falls, then rises as the inductor current grows. Schematic shapes; the
    dip is exaggerated so that it is visible."""
    import math
    t_step, t_end = 1.0, 10.0
    ts = [t_step + k * 0.02 for k in range(int((t_end - t_step) / 0.02) + 1)]

    def cur(t):
        return 1 - math.exp(-(t - t_step) / 2.5)

    def vout(t):
        x = t - t_step
        return 0.9 * (1 - math.exp(-x / 2.5)) ** 2 - 0.25 * (x / 0.6) * \
            math.exp(1 - x / 0.6)

    s = Svg(560, 400)
    s.text(300, 14, "Step increase of the boost duty cycle at time t0",
           size=13, weight="bold")
    g = Axes(s, (90, 40, 540, 80), (0, t_end), (0, 1))
    s.poly(g.P([(0, 0.1), (t_step, 0.1), (t_step, 0.9), (t_end, 0.9)]))
    s.text(82, 60, "duty\ncycle D", size=12, anchor="end")
    a = Axes(s, (90, 105, 540, 215), (0, t_end), (-0.1, 1.1))
    a.frame(yticks=[], grid=False)
    s.poly(a.P([(0, 0)] + [(t, cur(t)) for t in ts]), stroke=GREEN)
    s.text(82, 160, "inductor\ncurrent", size=12, anchor="end", fill=GREEN)
    b = Axes(s, (90, 240, 540, 350), (0, t_end), (-0.4, 1.0))
    b.frame(yticks=[], grid=False, xlabel="time (schematic)")
    s.poly(b.P([(0, 0)] + [(t, vout(t)) for t in ts]), stroke=BLUE)
    s.line(b.X(0), b.Y(0), b.X(t_end), b.Y(0), stroke=GREY, dash="3 3",
           width=1)
    s.text(82, 295, "output\nvoltage", size=12, anchor="end", fill=BLUE)
    s.text(b.X(2.0) + 8, b.Y(-0.25), "first falls", size=12, anchor="start",
           fill=RED)
    s.text(b.X(6.8), b.Y(0.45), "then rises as the\ncurrent grows",
           size=12, fill=BLUE)
    for ax in (g, a, b):
        s.line(ax.X(t_step), ax.y0, ax.X(t_step), ax.y1, stroke=GREY,
               dash="3 3", width=1)
    s.text(g.X(t_step), 375, "t0", size=12, fill=GREY)
    s.save(HERE / "rhp-step.svg")


def hysteretic():
    """Hysteretic control and pulse-frequency modulation (schematic)."""
    s = Svg(600, 330)
    s.text(300, 14, "(a) Hysteretic: the switch turns on at the lower "
           "threshold and off at the upper", size=12, weight="bold")
    a = Axes(s, (110, 30, 580, 120), (0, 10), (0, 1))
    hi_, lo_ = 0.8, 0.3
    pts, gate, v, t, on = [], [], lo_, 0.0, True
    # Light load first (slow fall), then heavy load (fast fall).
    while t < 10:
        fall = 0.12 if t < 5 else 0.35
        if on:
            dt = (hi_ - v) / 0.5
            gate.append((t, t + dt))
            v, t, on = hi_, t + dt, False
        else:
            dt = (v - lo_) / fall
            v, t, on = lo_, t + dt, True
        pts.append((min(t, 10), v))
    s.poly(a.P([(0, lo_)] + pts), stroke=BLUE)
    for y, lab in ((hi_, "upper"), (lo_, "lower")):
        s.line(a.x0, a.Y(y), a.x1, a.Y(y), stroke=GREY, dash="4 3", width=1)
        s.text(a.x0 - 6, a.Y(y), lab, size=11, anchor="end", fill=GREY)
    g = Axes(s, (110, 130, 580, 150), (0, 10), (0, 1))
    square(s, g, [(t0, min(t1, 10)) for t0, t1 in gate if t0 < 10], 0, 1)
    s.text(102, 140, "switch", size=11, anchor="end")
    s.text(a.X(2.5), 165, "light load: slow", size=11, fill=GREY)
    s.text(a.X(7.5), 165, "heavy load: fast", size=11, fill=GREY)
    s.text(102, 75, "output\nvoltage", size=11, anchor="end", fill=BLUE)
    s.text(300, 195, "(b) Pulse-frequency modulation: fixed pulses only as "
           "often as the load needs", size=12, weight="bold")
    p = Axes(s, (110, 220, 580, 260), (0, 10), (0, 1))
    bursts = [0.5, 0.8, 1.1, 4.5, 4.8, 5.1, 8.5, 8.8, 9.1]
    square(s, p, [(b, b + 0.15) for b in bursts], 0, 1)
    s.text(102, 240, "switch", size=11, anchor="end")
    s.text(p.X(2.8), 280, "no switching while the output\ncapacitor "
           "holds the light load", size=11, fill=GREY)
    s.line(110, 305, 580, 305, stroke=INK, width=1)
    s.text(345, 320, "time (schematic)", size=11, fill=GREY)
    s.save(HERE / "hysteretic.svg")


def soft_start():
    """Start-up without and with soft start (schematic)."""
    import math
    s = Svg(600, 330)
    for col, (title, soft) in enumerate((("Without soft start", False),
                                         ("With soft start", True))):
        x0 = 75 + col * 270
        s.text(x0 + 120, 14, title, size=12, weight="bold")
        av = Axes(s, (x0, 30, x0 + 240, 140), (0, 10), (0, 1.3))
        ai = Axes(s, (x0, 170, x0 + 240, 280), (0, 10), (0, 1.3))
        av.frame(yticks=[], grid=False)
        ai.frame(yticks=[], grid=False, xlabel="time (schematic)")
        s.line(av.x0, av.Y(1), av.x1, av.Y(1), stroke=GREY, dash="4 3",
               width=1)
        s.line(ai.x0, ai.Y(1.1), ai.x1, ai.Y(1.1), stroke=RED, dash="4 3",
               width=1)
        s.text(ai.x1, ai.Y(1.1) - 8, "current limit", size=10, fill=RED,
               anchor="end")
        ts = [k * 0.05 for k in range(201)]
        if soft:
            v = [(t, min(t / 6, 1) - 0.02 * math.sin(min(t / 6, 1) * 3)) for t in ts]
            i = [(t, 0.45 if t < 6 else 0.3 + 0.15 * math.exp(-(t - 6)))
                 for t in ts]
            s.text(av.X(7.2), av.Y(0.55), "reference ramps;\noutput follows",
                   size=10, fill=GREY)
            s.text(ai.X(3), ai.Y(0.65), "stays below the limit", size=10,
                   fill=GREY)
        else:
            v = [(t, 1 + 0.25 * math.exp(-(t - 2) / 1.2) * math.cos((t - 2) * 2)
                  if t > 2 else 1.25 * t / 2)
                 for t in ts]
            i = [(t, 1.1 if t < 2 else 0.3 + 0.8 * math.exp(-(t - 2) * 1.5))
                 for t in ts]
            s.text(av.X(6), av.Y(1.22), "overshoot", size=10, fill=RED)
            s.text(ai.X(0.3), ai.Y(1.24), "runs at the limit", size=10,
                   fill=RED, anchor="start")
        s.poly(av.P(v), stroke=BLUE)
        s.poly(ai.P(i), stroke=ORANGE)
    s.text(67, 85, "output\nvoltage", size=11, anchor="end", fill=BLUE)
    s.text(67, 225, "inductor\ncurrent", size=11, anchor="end", fill=ORANGE)
    s.save(HERE / "soft-start.svg")


def current_limit():
    """Cycle-by-cycle current limit and hiccup mode (schematic)."""
    s = Svg(600, 320)
    s.text(300, 14, "(a) Cycle-by-cycle: the on time ends when the current "
           "reaches the limit", size=12, weight="bold")
    a = Axes(s, (90, 30, 580, 130), (0, 6), (0, 1.2))
    a.frame(yticks=[], grid=False)
    s.line(a.x0, a.Y(1), a.x1, a.Y(1), stroke=RED, dash="4 3", width=1.2)
    s.text(a.x1, a.Y(1) - 8, "limit", size=10, fill=RED, anchor="end")
    pts, i = [], 0.55
    for k in range(6):
        d_nom = 0.45
        rise = 0.6 if k < 2 else 1.6           # overload from period 2
        t_on = min(d_nom, (1 - i) / rise)
        pts += [(k, i), (k + t_on, i + rise * t_on)]
        i = i + rise * t_on - 0.4 * (1 - t_on)
    pts.append((6, i))
    s.poly(a.P(pts), stroke=BLUE)
    s.text(82, 80, "inductor\ncurrent", size=11, anchor="end")
    s.text(a.X(1), a.Y(0.15), "normal", size=10, fill=GREY)
    s.text(a.X(4), a.Y(0.15), "overload: pulses cut short", size=10,
           fill=GREY)
    s.text(300, 170, "(b) Hiccup: a sustained overload stops switching, "
           "then retries", size=12, weight="bold")
    h = Axes(s, (90, 190, 580, 260), (0, 10), (0, 1))
    h.frame(yticks=[], grid=False, xlabel="time (schematic)")
    for b0 in (0.3, 4.8, 9.3):
        for k in range(8):
            t0 = b0 + k * 0.08
            s.line(h.X(t0), h.Y(0), h.X(t0), h.Y(0.9), stroke=BLUE, width=1.2)
    s.text(h.X(2.6), h.Y(0.45), "off", size=11, fill=GREY)
    s.text(h.X(7.1), h.Y(0.45), "off", size=11, fill=GREY)
    s.text(82, 225, "switching", size=11, anchor="end")
    s.text(h.X(0.6), h.Y(1.0) - 6, "burst", size=10, fill=BLUE)
    s.text(h.X(5.1), h.Y(1.0) - 6, "retry", size=10, fill=BLUE)
    s.save(HERE / "current-limit.svg")


def dead_time():
    """Gate signals with dead time and the switch node (schematic)."""
    s = Svg(600, 300)
    tr = (0, 10)
    g1 = Axes(s, (120, 20, 580, 50), tr, (0, 1))
    g2 = Axes(s, (120, 80, 580, 110), tr, (0, 1))
    sw = Axes(s, (120, 140, 580, 230), tr, (-0.15, 1))
    square(s, g1, [(0, 4)], 0, 1)
    square(s, g2, [(5, 10)], 0, 1)
    for t0, t1 in ((4, 5),):
        for ax in (g1, g2, sw):
            s.rect(ax.X(t0), ax.y0 - 5, ax.X(t1) - ax.X(t0),
                   ax.y1 - ax.y0 + 10, fill=FILL_ORANGE, stroke="none",
                   opacity=0.7)
    s.poly(g1.P([(0, 0), (0, 1), (4, 1), (4, 0), (10, 0)]), stroke=BLUE)
    s.poly(g2.P([(0, 0), (5, 0), (5, 1), (10, 1)]), stroke=BLUE)
    s.poly(sw.P([(0, 1), (4, 1), (4.3, -0.12), (5, -0.12), (5.1, 0),
                 (10, 0)]), stroke=BLUE)
    s.line(sw.x0, sw.Y(0), sw.x1, sw.Y(0), stroke=GREY, dash="3 3", width=1)
    for ax, name in ((g1, "high-side\ngate"), (g2, "low-side\ngate"),
                     (sw, "switch\nnode")):
        s.text(112, (ax.y0 + ax.y1) / 2, name, size=11, anchor="end")
    s.text(sw.X(5.4), sw.Y(0.35), "dead time: the body diode\nof the "
           "low-side switch conducts,\nnode one diode drop below ground",
           size=10, fill=ORANGE, anchor="start")
    s.text(sw.X(2), sw.Y(1) - 8, "Vin", size=11)
    s.text(345, 290, "both gates high together would short the input to "
           "ground (shoot-through)", size=11, fill=RED)
    s.save(HERE / "dead-time.svg")


FIGURES = {
    "pwm": pwm,
    "subharmonic": subharmonic,
    "rhp-step": rhp_step,
    "hysteretic": hysteretic,
    "soft-start": soft_start,
    "current-limit": current_limit,
    "dead-time": dead_time,
}

if __name__ == "__main__":
    for n in sys.argv[1:] or list(FIGURES):
        FIGURES[n]()
