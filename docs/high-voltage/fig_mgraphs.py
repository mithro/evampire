"""Draw the remaining graphs for the junctions, grading, insulator and
metal-gate pages.

cv-doping.svg      1/C^2 of the 6 V N-well model against reverse voltage.
lmin.svg           shortest length for a voltage to fall over.
oxide-silicon.svg  thickness that holds 57 V in oxide and in silicon.
gate-potential.svg potential from a Metal1 plate into the silicon.
metal-stack.svg    equivalent insulator thickness under each metal layer.
metal-vt.svg       threshold against insulator thickness.
transfer.svg       drain current against gate voltage.

Inputs are the numbers on the pages, from calc.py. figures.py calls this
module; it writes no files itself.

SPDX-License-Identifier: Apache-2.0
"""

from fig_graphs import Axes
from svgdraw import (BLUE, DEPL, GREY, INK, METAL, OXIDE, SUB, line, rect,
                     sub, svg, text)

Q, EPS_SI = 1.602e-19, 1.035e-12
GREEN = "#2e8b57"
LAYERS = ("Metal1", "Metal2", "Metal3", "Metal4", "Metal5")
T_FOX = (1.18, 2.30, 3.42, 4.54, 5.96)        # tab-hv-metal-stack, um
T_ACT = (0.87, 2.00, 3.12, 4.24, 5.65)
VT = {"lightest estimate, 1.2 × 10¹⁵ cm⁻³": (5.0, 10.0, 15.1, 20.1, 26.5),
      "from the Metal1 minimum": (8.5, 16.8, 25.1, 33.5, 44.0),
      "from the Metal1 typical": (11.0, 21.7, 32.4, 43.0, 56.5)}


def label(x, y, s, col=INK, anchor="start", size=12):
    return text(x, y, s, anchor=anchor, size=size, fill=col)


def cv_doping():
    c0, vbi, m = 1.4914e-8, 0.43905, 0.30525    # nwp_6p0, junctions page
    ax = Axes(100, 30, 500, 270, (0, 10), (0, 4e16), False, False)
    body = ax.frame([(v, str(v)) for v in range(0, 11, 2)],
                    [(k * 1e16, f"{k}" if k else "0") for k in range(5)],
                    "reverse voltage (V)", "1/C² (10¹⁶ cm⁴/F²)")
    model = lambda v: (c0 * (1 + v / vbi) ** -m) ** -2  # noqa: E731
    body.append(ax.curve(model, 0, 10, stroke=BLUE, width=2.5))
    zero = lambda v: 2 * (vbi + v) / (Q * EPS_SI * 1.2e15)  # noqa: E731
    body.append(ax.curve(zero, 0, (4e16 * Q * EPS_SI * 1.2e15 / 2) - vbi,
                         stroke=GREY, width=1.5, dash="6 4"))
    s = (model(10) - model(2)) / 8
    chord = lambda v: model(2) + s * (v - 2)  # noqa: E731
    xa, _ = ax.px(2, 0)
    xb, _ = ax.px(10, 0)
    body.append(rect(xa, ax.y0, xb - xa, ax.h, "#e2f0d9", stroke="none",
                     opacity=0.5))
    body.append(ax.curve(chord, 0, 10, stroke=DEPL, width=1.5, dash="6 4"))
    body.append(ax.curve(model, 0, 10, stroke=BLUE, width=2.5))
    x, y = ax.px(3.1, 3.4e16)
    body.append(label(x, y, "abrupt junction at 1.2 × 10¹⁵ cm⁻³,", GREY))
    body.append(label(x, y + 15, "matched at 0 V", GREY))
    x, y = ax.px(5.2, 1.35e16)
    body.append(label(x, y, "straight line through 2 V and 10 V:", DEPL))
    body.append(label(x, y + 15, "slope gives 5.3 × 10¹⁵ cm⁻³", DEPL))
    x, y = ax.px(6.5, model(6.5))
    body.append(label(x, y + 26, "model, grading 0.31", BLUE))
    x, _ = ax.px(6, 0)
    body.append(label(x, ax.y0 + 16, "fitting window", GREEN, "middle"))
    return svg(640, 360, body)


def lmin():
    ax = Axes(90, 30, 510, 250, (0, 100), (0, 4), False, False)
    body = ax.frame([(v, str(v)) for v in range(0, 101, 20)],
                    [(v, str(v)) for v in range(5)],
                    "voltage V (V)", sub("L", "min") + "(µm)")
    f = lambda v: (1.8e-35 * v ** 7) ** (1 / 6) * 1e4  # noqa: E731
    body.append(ax.curve(f, 0.5, 100, stroke=DEPL, width=2.5))
    for v, s in ((57, "57 V: 1.8 µm, 3.2 × 10⁵ V/cm"), (100, "100 V: 3.5 µm")):
        x, y = ax.px(v, f(v))
        body.append(ax.dot(v, f(v), DEPL))
        body.append(label(x - 8, y - 10, s, anchor="end"))
    return svg(640, 340, body)


def oxide_silicon():
    """Bars to scale: thickness that holds 57 V."""
    rows = (("oxide at 10 MV/cm", 57, OXIDE), ("oxide at 6 MV/cm", 95, OXIDE),
            ("oxide at 4 MV/cm", 142, OXIDE),
            ("silicon, an ideal even fall", 1800, SUB))
    body = [text(20, 24, "Thickness that holds 57 V, to scale", anchor="start",
                 size=14, weight="bold")]
    x0, scale = 200, 360 / 1800
    for k, (name, nm, col) in enumerate(rows):
        y = 50 + k * 44
        body.append(text(x0 - 8, y + 19, name, anchor="end", size=12))
        body.append(rect(x0, y, max(nm * scale, 1.5), 28, col))
        s = f"{nm} nm" if nm < 1000 else "1.8 µm"
        body.append(text(x0 + nm * scale + 8, y + 19, s, anchor="start",
                         size=12))
    body.append(text(320, 250, "oxide's critical field is 20 to 33 times "
                     "silicon's", size=13))
    return svg(640, 270, body)


def gate_potential():
    ax = Axes(90, 30, 500, 260, (0, 2.0), (0, 60), False, False)
    t = T_FOX[0]
    xa, _ = ax.px(0, 0)
    xb, _ = ax.px(t, 0)
    xc, _ = ax.px(2.0, 0)
    body = [rect(xa, ax.y0, xb - xa, ax.h, OXIDE, stroke="none"),
            rect(xb, ax.y0, xc - xb, ax.h, SUB, stroke="none")]
    body += ax.frame([(v, f"{v:g}") for v in (0, 0.5, 1, 1.5, 2)],
                     [(v, str(v)) for v in range(0, 61, 10)],
                     "depth below the Metal1 plate (µm)", "potential (V)")
    ws, psi = 0.4, 0.7
    for vg, col in ((57, DEPL), (11, BLUE)):
        pts = [ax.px(0, vg), ax.px(t, psi)]
        for k in range(11):
            d = ws * k / 10
            pts.append(ax.px(t + d, psi * (1 - d / ws) ** 2))
        pts.append(ax.px(2.0, 0))
        body.append('<polyline points="' + " ".join(
            f"{x:.1f},{y:.1f}" for x, y in pts) + f'" stroke="{col}" '
            'stroke-width="2.5" fill="none"/>')
        x, y = ax.px(0.05, vg)
        body.append(label(x, y + 18 if vg > 30 else y - 6,
                          f"gate at {vg} V", col))
    x, y = ax.px(0.85, 50)
    body.append(label(x, y, "insulator, 1.18 µm", INK, "middle"))
    x, y = ax.px(1.6, 30)
    body.append(label(x, y, "silicon", INK, "middle"))
    body.append(label(x, y + 16, "surface below", INK, "middle"))
    body.append(label(x, y + 32, "1 V in both", INK, "middle"))
    return svg(640, 340, body)


def metal_stack():
    ax = Axes(120, 30, 440, 300, (0, 2), (0, 6.5), False, False)
    body = ax.frame([], [(v, str(v)) for v in range(7)], "",
                    "equivalent oxide thickness (µm)")
    for c, (name, ts) in enumerate((("over field oxide", T_FOX),
                                    ("over active", T_ACT))):
        xa, _ = ax.px(c + 0.2, 0)
        xb, _ = ax.px(c + 0.8, 0)
        _, ytop = ax.px(0, 6.3)
        body.append(rect(xa, ytop, xb - xa, ax.y0 + ax.h - ytop, OXIDE))
        for lay, tt in zip(LAYERS, ts):
            _, y = ax.px(0, tt)
            body.append(rect(xa + 8, y - 4, xb - xa - 16, 8, METAL))
            body.append(text(xb + 6, y + 4, f"{tt}", anchor="start",
                             size=11))
            if c == 0:
                body.append(text(xa - 8, y + 4, lay, anchor="end", size=11))
        body.append(text((xa + xb) / 2, ax.y0 + ax.h + 20, name, size=13))
    return svg(640, 380, body)


def metal_vt():
    ax = Axes(90, 30, 500, 300, (0, 6.5), (0, 62), False, False)
    body = ax.frame([(v, str(v)) for v in range(7)],
                    [(v, str(v)) for v in range(0, 61, 10)],
                    "equivalent insulator thickness over field oxide (µm)",
                    "threshold (V)")
    # Shift by 1e11 cm^-2 of fixed charge: 5.5 V on Metal1, in proportion.
    typ = VT["from the Metal1 typical"]
    pts_hi = [ax.px(t, v + 5.5 * t / T_FOX[0]) for t, v in zip(T_FOX, typ)]
    pts_lo = [ax.px(t, v - 5.5 * t / T_FOX[0]) for t, v in zip(T_FOX, typ)]
    poly = pts_hi + pts_lo[::-1]
    body.append('<polygon points="' + " ".join(
        f"{x:.1f},{min(max(y, ax.y0), ax.y0 + ax.h):.1f}" for x, y in poly)
        + '" fill="#f6d5d1" fill-opacity="0.6" stroke="none"/>')
    _, y57 = ax.px(0, 57)
    body.append(line(ax.x0, y57, ax.x0 + ax.w, y57, stroke=GREY, dash="6 4"))
    body.append(label(ax.x0 + 6, y57 - 6, "sensed node, 57 V", GREY))
    for (name, vs), col in zip(VT.items(), (GREEN, BLUE, DEPL)):
        body.append('<polyline points="' + " ".join(
            f"{x:.1f},{y:.1f}" for x, y in (ax.px(t, v) for t, v in
                                            zip(T_FOX, vs)))
            + f'" stroke="{col}" stroke-width="2" fill="none"/>')
        for t, v in zip(T_FOX, vs):
            body.append(ax.dot(t, v, col))
    for lay, t in zip(LAYERS, T_FOX):
        x, _ = ax.px(t, 0)
        body.append(text(x, ax.y0 + ax.h - 6, lay, size=10, fill=GREY))
    ys = 52
    for (name, _), col in zip(VT.items(), (GREEN, BLUE, DEPL)):
        x, y = ax.px(0.15, 0)
        _, yy = ax.px(0, ys)
        body.append(label(x, yy, name, col))
        ys -= 4.5
    xm, ylo = ax.px(T_FOX[0], 8.5)
    _, yhi = ax.px(T_FOX[0], 11)
    body.append(line(xm, ylo, xm, yhi, stroke=INK, width=4))
    x, yy = ax.px(0.15, 36)
    body.append(label(x, yy, "measured Metal1: 8.5 V minimum,", INK))
    body.append(label(x, yy + 15, "11 V typical", INK))
    x, yy = ax.px(3.9, 14)
    body.append(label(x, yy, "shaded: ±10¹¹ cm⁻² of fixed charge", DEPL))
    return svg(640, 390, body)


def transfer():
    body = []
    caps = {"Metal1": (2.93e-9, 11.0, DEPL), "Metal3": (1.009e-9, 32.4, BLUE),
            "Metal5": (5.80e-10, 56.5, GREEN)}
    ax = Axes(90, 40, 500, 230, (0, 60), (0, 600), False, False)
    body.append(text(20, 24, "(a) Above threshold, W/L = 10, "
                     + sub("V", "DS") + "= 1 V", anchor="start", size=14,
                     weight="bold"))
    body += ax.frame([(v, str(v)) for v in range(0, 61, 10)],
                     [(v, str(v)) for v in range(0, 601, 100)],
                     "gate voltage " + sub("V", "G") + "(V)",
                     "drain current (µA)")
    for name, (c, vt, col) in caps.items():
        def f(v, c=c, vt=vt):
            return max(0.0, 10 * 400 * c * (v - 0.5 - vt) * 1e6)
        body.append(ax.curve(f, vt + 0.5, 60, stroke=col, width=2.5))
        body.append(ax.dot(57, f(57), col))
        x, y = ax.px(57, f(57))
        if f(57) > 1:
            body.append(label(x - 8, y - 8, f"{name}: {f(57):.0f} µA at 57 V",
                              col, "end"))
        else:
            xl, yl = ax.px(57, 160)
            body.append(line(xl, yl + 4, x, y - 5, stroke=col, width=1))
            body.append(label(xl - 4, yl, f"{name}: at threshold at 57 V",
                              col, "end"))
    ax2 = Axes(90, 380, 500, 200, (-5, 0), (1e-4, 1), False, True)
    body.append(text(20, 360, "(b) Below threshold", anchor="start", size=14,
                     weight="bold"))
    body += ax2.frame([(v, str(v)) for v in range(-5, 1)],
                      [(1e-4, "10⁻⁴"), (1e-2, "10⁻²"), (1, "1")],
                      sub("V", "G") + "− " + sub("V", "T") + "(V)",
                      "current ÷ current at threshold")
    for name, sl, col in (("Metal1, 550 mV per decade", 0.55, DEPL),
                          ("Metal5, 2.6 V per decade", 2.6, GREEN)):
        lo = max(-5, -4 * sl)
        body.append(ax2.curve(lambda v, sl=sl: 10 ** (v / sl), lo, 0,
                              stroke=col, width=2.5))
        if sl < 1:
            x, y = ax2.px(-1.9, 1e-3)
            body.append(label(x, y, name, col, "end"))
        else:
            x, y = ax2.px(-0.2, 10 ** (-0.2 / sl))
            body.append(label(ax2.x0 + ax2.w - 6, y - 10, name, col, "end"))
    return svg(640, 640, body)


FIGURES = {"cv-doping.svg": cv_doping, "lmin.svg": lmin,
           "oxide-silicon.svg": oxide_silicon,
           "gate-potential.svg": gate_potential,
           "metal-stack.svg": metal_stack, "metal-vt.svg": metal_vt,
           "transfer.svg": transfer}
