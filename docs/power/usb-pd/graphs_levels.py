# /// script
# requires-python = ">=3.10"
# ///
"""Write the graphs of USB Power Delivery power levels and offers. Run with:

    uv run docs/power/usb-pd/graphs_levels.py

Writes:

power-levels.svg
    The voltage of each kind of supply, with the worst-case VBUS voltages
    (power-levels.rst; PD Tables 3.1, 4.2 to 4.4 and 4.7).
offer-currents.svg
    The maximum current of each fixed offer against the Port Present PDP
    (power-translation.rst; PD Section 3.2.4 and Table 3.2).
pdp-nesting.svg
    The three powers that describe a source port, schematic
    (two-ports.rst).

SPDX-License-Identifier: Apache-2.0
"""

from svgfig import (CABLE, CABLE_INK, FILL, GREY, INK, SNK, SNK_INK, SRC,
                    SRC_INK, Plot, line, polyline, rect, svg, text, write)


def power_levels():
    p = Plot(230, 20, 420, 250, (0, 55), (0, 6))
    rows = ["SPR fixed", "SPR PPS: 5 to 11, 16 or 21 V",
            "SPR AVS: 9 to 15 or 20 V", "EPR fixed",
            "EPR AVS: 15 to 28, 36 or 48 V"]
    body = [rect(p.x(0), p.top, p.x(24) - p.x(0), p.h, "#f7f7f7", "none")]
    body.append(p.frame())
    for k, name in enumerate(rows):
        y = p.y(5 - k)
        body.append(text(p.left - 8, y + 4, name, 12, "end"))
    def bars(k, ranges, fill):
        h = 0.55 / len(ranges)
        out = []
        for j, (a, b) in enumerate(ranges):
            yc = 5 - k + 0.275 - h * (j + 0.5)
            out.append(rect(p.x(a), p.y(yc + h / 2 - 0.03),
                            p.x(b) - p.x(a), p.y(yc - h / 2 + 0.03)
                            - p.y(yc + h / 2 - 0.03), fill))
        return out
    def dots(k, volts, col):
        out = []
        for v in volts:
            out.append(f'<circle cx="{p.x(v):.1f}" cy="{p.y(5 - k):.1f}" '
                       f'r="5" fill="{col}"/>')
            out.append(text(p.x(v), p.y(5 - k) - 9, f"{v:g}", 10, "middle"))
        return out
    body += dots(0, (5, 9, 15, 20), SRC_INK)
    body += bars(1, ((5, 11), (5, 16), (5, 21)), SRC)
    body += bars(2, ((9, 15), (9, 20)), SRC)
    body += dots(3, (28, 36, 48), SNK_INK)
    body += bars(4, ((15, 28), (15, 36), (15, 48)), SNK)
    for v in (21.5, 22.15, 24, 50.9):
        body.append(line(p.x(v), p.top, p.x(v), p.bottom, INK, 0.9, "4,3"))
    body += p.xticks([0, 10, 20, 30, 40, 50], "voltage (V)", grid=False)
    body.append(text(p.x(12), p.top + 14, "SPR: up to 100 W", 11,
                     "middle", fill=GREY))
    body.append(text(p.x(40), p.top + 14, "EPR: up to 240 W", 11,
                     "middle", fill=GREY))
    ly = p.bottom + 58
    for k, s in enumerate((
            "Dashed lines: worst-case VBUS of 21.5 V (SPR fixed and AVS), "
            "22.15 V (PPS),",
            "24 V (what an SPR sink tolerates) and 50.9 V (EPR).")):
        body.append(text(10, ly + 16 * k, s, 12))
    return svg(680, int(ly + 26), body, "USB PD power levels")


def offer_currents():
    p = Plot(60, 20, 520, 280, (0, 100), (0, 5.4))
    body = [p.frame()]
    body += p.yticks([0, 1, 2, 3, 4, 5], "maximum current (A)")
    offers = [(5, 0, 3.0, SRC_INK, None), (9, 15, 3.0, SNK_INK, None),
              (15, 27, 3.0, CABLE_INK, None), (20, 45, 3.0, INK, None)]
    for v, start, ilim, col, dash in offers:
        pts = [(x / 2, min(ilim, x / 2 / v)) for x in range(2 * start,
                                                             201)]
        if v == 20:
            pts = [(x, y) for x, y in pts if x <= 60]
        body.append(polyline(p.pts(pts), col, 2.2, dash))
        x0 = start if start else 2
        # The 9 V label sits left of its line, clear of the 19 W example.
        dx, anchor = (-4, "end") if v == 9 else (6, "start")
        body.append(text(p.x(x0) + dx, p.y(min(ilim, x0 / v)) + 16,
                         f"{v} V", 12, anchor, fill=col))
    five = [(x, min(5.0, x / 20)) for x in range(60, 101)]
    body.append(polyline(p.pts(five), INK, 2.2, "6,3"))
    body.append(text(p.x(62), p.y(4.6), "20 V with a 5 A cable", 11))
    body.append(text(p.x(62), p.y(2.7), "5, 9 and 15 V stop at 3 A; a 3 A", 11))
    body.append(text(p.x(62), p.y(2.7) + 14, "cable caps the PDP at 60 W", 11))
    for x, lab in ((8, "8"), (19, "19"), (42, "42"), (61, "61")):
        body.append(line(p.x(x), p.top, p.x(x), p.bottom, GREY, 1.0, "3,3"))
        body.append(text(p.x(x) + 3, p.top + 12, f"{lab} W", 10))
    body += p.xticks([0, 15, 27, 45, 60, 80, 100], "Port Present PDP (W)",
                     grid=False)
    body.append(text(p.left, p.bottom + 58, "Each line starts where the "
                     "offer becomes required. Grey: the worked examples.",
                     12, fill=GREY))
    return svg(680, int(p.bottom + 70), body, "Offer current against PDP")


def pdp_nesting():
    body = []
    x0, w = 160, 300
    rows = [("Port Maximum PDP", 1.0, FILL, "the most the port will ever "
             "provide"),
            ("Port Present PDP", 0.72, CABLE, "what it can provide now"),
            ("present offer", 0.5, SRC, "the power in Source_Capabilities")]
    for k, (name, frac, fill, note) in enumerate(rows):
        y = 30 + 44 * k
        body.append(rect(x0, y, w * frac, 26, fill))
        body.append(text(x0 - 8, y + 18, name, 12, "end"))
        body.append(text(x0 + w * frac + 6, y + 18, note, 11))
    xg = x0 + w * 0.35
    body.append(line(xg, 20, xg, 166, SNK_INK, 2.0, "6,3"))
    body.append(text(xg, 184, "Port Guaranteed PDP: provided on request", 11,
                     "middle", fill=SNK_INK))
    body.append(line(x0, 196, x0 + w, 196, arrow="end"))
    body.append(text(x0 + w, 214, "power (schematic, not to scale)", 11,
                     "end"))
    return svg(680, 224, body, "Port powers")


if __name__ == "__main__":
    write("power-levels.svg", power_levels())
    write("offer-currents.svg", offer_currents())
    write("pdp-nesting.svg", pdp_nesting())
