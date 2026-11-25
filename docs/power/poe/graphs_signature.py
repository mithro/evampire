# /// script
# requires-python = ">=3.10"
# ///
"""Write the detection and classification graphs of the Power over
Ethernet pages. Run with:

    uv run docs/power/poe/graphs_signature.py

Writes:

pd-signature.svg
    The current-voltage line of a valid 25 kOhm signature and of the
    invalid signatures, over the detection range (powered-device.rst;
    IEEE 802.3 Tables 145-21 and 145-22).
detect-iv.svg
    Two-point detection of a 25 kOhm signature with a 2 V offset, and the
    edge cases (power-sourcing.rst; IEEE 802.3 145.2.6.2, Table 145-8).
detect-bands.svg
    The detection decision bands, with the powered device's valid window
    (power-sourcing.rst; IEEE 802.3 Tables 145-8, 145-9 and 145-21).
class-bands.svg
    The powered device's class signature currents against the power
    sourcing equipment's decision bands (power-sourcing.rst; IEEE 802.3
    Tables 145-13 and 145-24).
thresholds.svg
    The voltage ranges of the steps at the powered device, with the
    comparator thresholds of one controller in the gaps (pd-controller.rst;
    IEEE 802.3 Table 145-25).
hysteresis.svg
    Turn-on and turn-off of the load against input voltage for two
    controllers (powered-device.rst; IEEE 802.3 Table 145-29).

Every number comes from the page that shows the figure.

SPDX-License-Identifier: Apache-2.0
"""

from svgfig import (BAD, BAD_INK, EVP, FILL, GREY, INK, OK, OK_INK, POWER,
                    SRC_INK, Plot, dot, line, polyline, rect, svg, text,
                    write)


def pd_signature():
    p = Plot(70, 20, 440, 280, (0, 500), (0, 12))
    body = [rect(p.left, p.y(10.1), p.w, p.y(2.7) - p.y(10.1), OK, "none")]
    body.append(p.frame())
    body += p.yticks([0, 2.7, 6, 10.1, 12], "voltage at the PD input (V)",
                     fmt="{:g}")
    body += p.xticks([0, 100, 200, 300, 400, 500], "current (µA)")
    body.append(text(p.left + 6, p.y(10.1) + 14, "detection range "
                     "2.7–10.1 V", 10, fill=OK_INK))
    lines = [(24.9, 0.0, SRC_INK, None, "24.9 kΩ resistor"),
             (24.9, 1.9, SRC_INK, "6,3", "with a 1.9 V offset"),
             (12, 0.0, BAD_INK, "2,3", "< 12 kΩ: invalid"),
             (45, 0.0, BAD_INK, "2,3", "> 45 kΩ: invalid")]
    for r, off, col, dash, label in lines:
        i_end = min(500, (12 - off) / r * 1000)
        body.append(polyline(p.pts([(0, off), (i_end, off + i_end * r
                                                / 1000)]), col, 2.0, dash))
    lx = p.right + 10
    legend = [(SRC_INK, None, "24.9 kΩ"), (SRC_INK, "6,3", "24.9 kΩ with"),
              (None, None, "1.9 V offset"), (BAD_INK, "2,3", "12 kΩ and"),
              (None, None, "45 kΩ: invalid")]
    for k, (col, dash, s) in enumerate(legend):
        y = p.top + 20 + 17 * k
        if col:
            body.append(line(lx, y - 4, lx + 18, y - 4, col, 1.8, dash))
        body.append(text(lx + 22, y, s, 9))
    for k, s in enumerate(("valid: slope", "23.7–26.3 kΩ,",
                           "offset ≤ 1.9 V")):
        body.append(text(lx, p.top + 130 + 15 * k, s, 10, fill=OK_INK))
    return svg(680, int(p.bottom + 48), body, "Powered device signature")


def detect_iv():
    p = Plot(70, 20, 440, 280, (0, 400), (0, 11))
    body = [rect(p.left, p.y(10), p.w, p.y(2.8) - p.y(10), OK, "none")]
    body.append(p.frame())
    body += p.yticks([0, 2.8, 6, 8.75, 10], "port voltage (V)", fmt="{:g}")
    body += p.xticks([0, 100, 160, 270, 400], "forced current (µA)")
    body.append(text(p.left + 6, p.y(10) + 14, "test window 2.8–10 V", 10,
                     fill=OK_INK))
    cases = [(25, 2.0, SRC_INK, None), (25, 0.0, GREY, "6,3"),
             (26.5, 2.0, INK, "2,3"), (19, 0.0, INK, "2,3")]
    for r, off, col, dash in cases:
        i_end = min(400, (11 - off) / r * 1000)
        body.append(polyline(p.pts([(0, off), (i_end, off + i_end * r
                                                / 1000)]), col, 1.8, dash))
    for i, v in ((160, 6.0), (270, 8.75)):
        body.append(dot(p.x(i), p.y(v), 4, SRC_INK))
        body.append(line(p.x(i), p.y(v), p.x(i), p.bottom, GREY, 0.6, "2,2"))
        body.append(line(p.left, p.y(v), p.x(i), p.y(v), GREY, 0.6, "2,2"))
    body.append(line(p.x(160), p.y(6.0), p.x(270), p.y(6.0), SRC_INK, 1.0))
    body.append(line(p.x(270), p.y(6.0), p.x(270), p.y(8.75), SRC_INK, 1.0))
    body.append(text(p.x(215), p.y(6.0) + 14, "110 µA", 10, "middle",
                     fill=SRC_INK))
    body.append(text(p.x(270) + 6, p.y(7.4), "2.75 V", 10, fill=SRC_INK))
    body.append(dot(p.x(270), p.y(9.155), 3.5, INK))
    body.append(dot(p.x(160), p.y(3.04), 3.5, INK))
    body.append(text(p.x(270) - 8, p.y(9.155) - 2, "9.2 V", 10, "end"))
    body.append(text(p.x(160) + 8, p.y(3.04) + 14, "3.0 V", 10))
    lx = p.right + 10
    legend = [(SRC_INK, None, "25 kΩ + 2 V offset"),
              (GREY, "6,3", "25 kΩ, no offset"),
              (INK, "2,3", "edges: 26.5 kΩ + 2 V"),
              (None, None, "and 19 kΩ")]
    for k, (col, dash, s) in enumerate(legend):
        y = p.top + 20 + 18 * k
        if col:
            body.append(line(lx, y - 4, lx + 18, y - 4, col, 1.8, dash))
        body.append(text(lx + 22, y, s, 9))
    body.append(text(p.left, p.bottom + 58, "Both 25 kΩ lines give "
                     "2.75 V / 110 µA = 25 kΩ: the offset cancels.", 11,
                     fill=GREY))
    return svg(680, int(p.bottom + 70), body, "Two-point detection")


def detect_bands():
    p = Plot(40, 64, 600, 30, (0, 40), (0, 1))
    body = []
    bands = [(0, 15, BAD, "reject"), (15, 19, FILL, "either"),
             (19, 26.5, OK, "accept"), (26.5, 33, FILL, "either"),
             (33, 40, BAD, "reject")]
    for a, b, fill, lab in bands:
        body.append(rect(p.x(a), p.top, p.x(b) - p.x(a), p.h, fill))
        body.append(text(p.x((a + b) / 2), p.top + 20, lab, 10, "middle"))
    body.append(text(p.left, p.top - 30, "power sourcing equipment decision",
                     11, weight="bold"))
    y2 = p.bottom + 34
    body.append(text(p.left, y2 - 8, "powered device valid window", 11,
                     weight="bold"))
    body.append(rect(p.x(23.7), y2, p.x(26.3) - p.x(23.7), 20, SRC_INK,
                     "none"))
    body.append(text(p.x(23.7) - 4, y2 + 15, "23.7", 10, "end"))
    body.append(text(p.x(26.3) + 4, y2 + 15, "26.3 kΩ", 10))
    # Thresholds with equal relative error at both edges.
    for lo, hi in ((15, 19), (26.5, 33)):
        t = 2 / (1 / lo + 1 / hi)
        body.append(line(p.x(t), p.top - 4, p.x(t), p.bottom + 4, INK, 2.0))
    body.append(text(p.x(29.4), p.top - 8, "threshold, ± 11 %", 10,
                     "middle"))
    body.append(text(p.x(16.8), p.top - 8, "± 12 %", 10, "middle"))
    ax = y2 + 40
    body.append(line(p.left, ax, p.right, ax))
    for v in (0, 15, 19, 26.5, 33, 40):
        body.append(line(p.x(v), ax, p.x(v), ax + 5))
        body.append(text(p.x(v), ax + 18, f"{v:g}", 11, "middle"))
    body.append(text(p.left + p.w / 2, ax + 36, "signature resistance (kΩ)",
                     12, "middle"))
    return svg(680, int(ax + 46), body, "Detection decision")


def class_bands():
    p = Plot(40, 40, 600, 30, (0, 56), (0, 1))
    body = []
    pd = [(1, 4, "0"), (9, 12, "1"), (17, 20, "2"), (26, 30, "3"),
          (36, 44, "4")]
    body.append(text(p.left, p.top - 8, "powered device draws "
                     "(class signature)", 11, weight="bold"))
    for a, b, s in pd:
        body.append(rect(p.x(a), p.top, p.x(b) - p.x(a), p.h, SRC_INK,
                         "none"))
        body.append(text(p.x((a + b) / 2), p.top + 20, s, 11, "middle",
                         "bold", "#ffffff"))
    y2 = p.bottom + 40
    body.append(text(p.left, y2 - 8, "power sourcing equipment decides", 11,
                     weight="bold"))
    pse = [(0, 5, OK, "0"), (5, 8, FILL, ""), (8, 13, OK, "1"),
           (13, 16, FILL, ""), (16, 21, OK, "2"), (21, 25, FILL, ""),
           (25, 31, OK, "3"), (31, 35, FILL, ""), (35, 45, OK, "4"),
           (45, 51, FILL, "4 or\ninvalid"), (51, 56, BAD, "")]
    for a, b, fill, s in pse:
        body.append(rect(p.x(a), y2, p.x(b) - p.x(a), 30, fill))
        if s and "\n" not in s:
            body.append(text(p.x((a + b) / 2), y2 + 20, s, 11, "middle"))
    body.append(text(p.x(48), y2 + 14, "4 or", 9, "middle"))
    body.append(text(p.x(48), y2 + 25, "invalid", 9, "middle"))
    body.append(text(p.x(53.5), y2 + 20, "end", 9, "middle",
                     fill=BAD_INK))
    ax = y2 + 44
    body.append(line(p.left, ax, p.right, ax))
    for v in (0, 5, 8, 13, 16, 21, 25, 31, 35, 45, 51):
        body.append(line(p.x(v), ax, p.x(v), ax + 5))
        body.append(text(p.x(v), ax + 18, f"{v}", 10, "middle"))
    body.append(text(p.left + p.w / 2, ax + 36, "class event current (mA)",
                     12, "middle"))
    body.append(text(p.left, ax + 58, "Grey: either neighbouring signature "
                     "allowed. The narrowest grey gaps are 3 mA wide.", 11,
                     fill=GREY))
    return svg(680, int(ax + 70), body, "Class decision")


def thresholds():
    p = Plot(40, 40, 600, 150, (0, 60), (0, 3))
    body = []
    for a, b in ((2.81, 6.9), (10.1, 14.5)):
        body.append(rect(p.x(a), p.y(3), p.x(b) - p.x(a), p.y(0) - p.y(3),
                         "#f2f2f2", GREY, 0.8, "3,2"))
        body.append(text(p.x((a + b) / 2), p.y(3) - 6, "gap", 10, "middle",
                         fill=GREY))
    body.append(text(p.right, p.top - 22, "ranges at the powered device",
                     11, "end", "bold"))
    rows = [(2.5, "detection", 2.7, 10.1, EVP), (2.5, "class", 14.5, 20.5,
                                                OK),
            (2.5, "turn on", 30, 42, POWER), (2.5, "operating", 42.5, 57,
                                              FILL),
            (1.6, "mark", 6.9, 10.1, EVP), (1.6, "reset", 0, 2.81, BAD)]
    for r, name, a, b, fill in rows:
        yc = p.y(r)
        body.append(rect(p.x(a), yc - 11, p.x(b) - p.x(a), 22, fill))
        body.append(text(p.x((a + b) / 2), yc + 4, name, 10, "middle"))
    yt = p.y(0.6)
    body.append(text(p.right, yt - 26, "TPS2372 thresholds (typical)", 11,
                     "end", "bold"))
    for rise, fall in ((12.5, 10.9), (22, 21.22), (38.1, 32.0)):
        body.append(line(p.x(rise), yt - 14, p.x(rise), yt + 2, INK, 2.0))
        body.append(line(p.x(fall), yt - 2, p.x(fall), yt + 14, INK, 2.0,
                         "3,2"))
        body.append(text(p.x(rise), yt - 18, f"{rise:g}↑", 10, "middle"))
        body.append(text(p.x(fall), yt + 26, f"{fall:.1f}↓", 10, "middle"))
    body.append(line(p.x(3.9), yt - 2, p.x(3.9), yt + 14, INK, 2.0, "3,2"))
    body.append(text(p.x(3.9), yt + 26, "3.9↓", 10, "middle"))
    body += p.xticks([0, 10, 20, 30, 40, 50, 60],
                     "voltage at the powered device input (V)", grid=False)
    body.append(text(p.left, p.bottom + 58, "↑ rising threshold (solid); "
                     "↓ falling threshold (dashed), lower by the hysteresis.",
                     11, fill=GREY))
    return svg(680, int(p.bottom + 70), body, "Comparator thresholds")


def hysteresis():
    p = Plot(80, 50, 540, 160, (25, 45), (0, 1))
    body = [rect(p.x(30), p.top, p.x(42) - p.x(30), p.h, POWER, "none")]
    body.append(p.frame())
    body.append(text(p.x(36), p.top - 8, "turn-on allowed 30–42 V", 10,
                     "middle"))
    for k, (col, dash, s) in enumerate(((SRC_INK, None, "TPS2372"),
                                        (INK, "6,3", "LT4275"))):
        x = p.left + 130 * k
        body.append(line(x, 18, x + 24, 18, col, 2.0, dash))
        body.append(text(x + 30, 22, s, 11, fill=col))
    for (on, off, col, dash, lift, yon, yoff, aoff) in (
            (38.1, 32, SRC_INK, None, 0.0, 0.3, 0.72, "start"),
            (35, 31, INK, "6,3", 0.06, 0.42, 0.58, "end")):
        lo, hi = 0.1 + lift, 0.9 - lift
        body.append(polyline(p.pts([(25, lo), (on, lo), (on, hi),
                                    (45, hi)]), col, 2.0, dash))
        body.append(polyline(p.pts([(off, hi), (off, lo)]), col, 2.0, dash))
        body.append(line(p.x(on) - 30, p.y(lo) - 6, p.x(on) - 8,
                         p.y(lo) - 6, col, 1.0, arrow="end"))
        body.append(line(p.x(off) + 30, p.y(hi) + 6, p.x(off) + 8,
                         p.y(hi) + 6, col, 1.0, arrow="end"))
        body.append(text(p.x(on) + 5, p.y(yon), f"on {on:g} V", 10,
                         fill=col))
        dx = 5 if aoff == "start" else -5
        body.append(text(p.x(off) + dx, p.y(yoff), f"off {off:g} V", 10,
                         aoff, fill=col))
    for v, s in ((0.1, "off"), (0.9, "on")):
        body.append(text(p.left - 8, p.y(v) + 4, s, 11, "end"))
    body.append(text(14, p.top + p.h / 2, "load switch", 12, "middle",
                     rotate=-90))
    body += p.xticks([25, 30, 35, 40, 45], "input voltage (V)", grid=False)
    return svg(680, int(p.bottom + 48), body, "Turn-on hysteresis")


if __name__ == "__main__":
    write("pd-signature.svg", pd_signature())
    write("detect-iv.svg", detect_iv())
    write("detect-bands.svg", detect_bands())
    write("class-bands.svg", class_bands())
    write("thresholds.svg", thresholds())
    write("hysteresis.svg", hysteresis())
