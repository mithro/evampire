# /// script
# requires-python = ">=3.10"
# ///
"""Write the graphs for the CC protection page. Run with:

    uv run docs/power/usb-pd/graphs_protection.py

Writes:

cc-ringing.svg
    An illustrative step response of a lightly damped RLC circuit: a 20 V
    VBUS short ringing on a CC pin (cc-protection.rst).
esd-short.svg
    Current against time for an HBM test, an IEC 61000-4-2 test and a VBUS
    short, on logarithmic axes (cc-protection.rst).

SPDX-License-Identifier: Apache-2.0
"""

import math

from svgfig import (CABLE_INK, GREY, INK, SNK_INK, SRC_INK, Plot, line,
                    polyline, svg, text, write)


def cc_ringing():
    """Underdamped second-order step response, damping ratio 0.03, time in
    periods of the ringing. Illustrative only."""
    p = Plot(60, 20, 420, 300, (0, 4), (0, 55))
    zeta, step = 0.03, 20.0
    wd = 2 * math.pi
    wn = wd / math.sqrt(1 - zeta ** 2)
    pts = [(-0.0, 0.0)]
    for k in range(0, 801):
        t = 4 * k / 800
        v = step * (1 - math.exp(-zeta * wn * t) * (
            math.cos(wd * t) + zeta / math.sqrt(1 - zeta ** 2)
            * math.sin(wd * t)))
        pts.append((t, v))
    body = [p.frame()]
    body += p.yticks([0, 10, 20, 30, 40, 50], "CC voltage (V)")
    for v, lab, col in ((50.9, "50.9 V: EPR worst case", GREY),
                        (44, "44 V: reported for a 20 V port", GREY),
                        (22.15, "22.15 V: SPR with PPS", GREY),
                        (5.5, "5.5 V: highest VCONN", SNK_INK),
                        (2.9, "2.9 V: lowest allowed clamp", SNK_INK)):
        body.append(line(p.left, p.y(v), p.right, p.y(v), col, 1.0, "6,3"))
        dy = 10 if v == 2.9 else (-2 if v == 5.5 else 4)
        body.append(text(p.right + 6, p.y(v) + dy, lab, 11,
                         fill=col if col != GREY else INK))
    body.append(polyline(p.pts(pts), SRC_INK, 2.0))
    peak = max(v for _, v in pts)
    body.append(text(p.x(0.55), p.y(peak) - 6, f"about twice the step "
                     f"({peak:.0f} V here)", 11))
    body += p.xticks([0, 1, 2, 3, 4], "time (periods of the ringing)",
                     grid=False)
    body.append(text(p.left, p.bottom + 58, "Illustrative: a 20 V step into "
                     "a lightly damped RLC circuit, damping ratio 0.03.",
                     12, fill=GREY))
    return svg(680, int(p.bottom + 70), body, "CC ringing after a short")


def esd_short():
    """Current against time, log-log: two ESD tests drawn as single
    exponentials from their peak, and a 3 A short for 1 s."""
    p = Plot(70, 20, 580, 300, (1e-9, 3), (0.01, 100), xlog=True, ylog=True)
    body = [p.frame()]
    for k in range(-9, 1):
        x = p.x(10.0 ** k)
        body.append(line(x, p.top, x, p.bottom, GREY, 0.5, "2,3"))
    labels = {-9: "1 ns", -8: "10 ns", -7: "100 ns", -6: "1 µs",
              -5: "10 µs", -4: "100 µs", -3: "1 ms", -2: "10 ms",
              -1: "100 ms", 0: "1 s"}
    for k, s in labels.items():
        x = p.x(10.0 ** k)
        body.append(line(x, p.bottom, x, p.bottom + 5))
        body.append(text(x, p.bottom + 18, s, 10, "middle"))
    body.append(text(p.left + p.w / 2, p.bottom + 36, "time (s, "
                     "logarithmic)", 13, "middle"))
    for v in (0.01, 0.1, 1, 10, 100):
        y = p.y(v)
        body.append(line(p.left, y, p.right, y, GREY, 0.5, "2,3"))
        body.append(line(p.left - 5, y, p.left, y))
        body.append(text(p.left - 8, y + 4, f"{v:g}", 12, "end"))
    body.append(text(14, p.top + p.h / 2, "current (A)", 13, "middle",
                     rotate=-90))

    def expo(i0, tau):
        out = []
        for k in range(0, 200):
            t = 10 ** (-9 + 9.4 * k / 199)
            i = i0 * math.exp(-t / tau)
            if i < 0.01:
                break
            out.append((t, i))
        return out
    hbm = expo(2000 / 1500, 150e-9)
    iec = expo(30.0, 50e-9)
    short = [(1e-9, 3.0), (1.0, 3.0), (1.0, 0.01)]
    body.append(polyline(p.pts(hbm), CABLE_INK, 2.2))
    body.append(polyline(p.pts(iec), INK, 2.2, "6,3"))
    body.append(polyline(p.pts(short), SRC_INK, 2.6))
    body.append(text(p.x(2e-9), p.y(0.04), "HBM 2 kV: 1.33 A, τ 150 ns",
                     11, fill=CABLE_INK))
    body.append(text(p.x(2e-9), p.y(30) - 8, "IEC 8 kV: 30 A, τ 50 ns", 11))
    body.append(text(p.x(1e-5), p.y(3) - 8, "VBUS short: 3 A until the "
                     "cable is pulled, 1 s here", 11, fill=SRC_INK))
    body.append(text(p.left, p.bottom + 58, "ESD currents drawn as single "
                     "exponentials from their peak.", 12, fill=GREY))
    return svg(680, int(p.bottom + 70), body, "ESD tests and a VBUS short")


if __name__ == "__main__":
    write("cc-ringing.svg", cc_ringing())
    write("esd-short.svg", esd_short())
