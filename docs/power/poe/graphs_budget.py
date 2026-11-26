# /// script
# requires-python = ">=3.10"
# ///
"""Write the budget and voltage graphs of the Power over Ethernet pages.
Run with:

    uv run docs/power/poe/graphs_budget.py

Writes:

class-methods.svg
    The allocation set first by Physical Layer classification and then
    changed by Data Link Layer classification (classification.rst).
voltages.svg
    The voltage ranges at a powered device, at power sourcing equipment and
    of a USB Power Delivery supply (translation.rst).
power-split.svg
    The input power split into conversion loss, board power and the class
    offered, for a 60 W USB contract (translation.rst).
class-board.svg
    The highest class offered against the board's own power, for USB Power
    Delivery and Power over Ethernet inputs (translation.rst).
budget-split.svg
    An 80 W output budget shared between an Ethernet output and the USB
    Type-C outputs (sharing.rst).
supply-voltages.svg
    The supply voltage of a power sourcing port against the output range,
    and a 48 V USB supply used directly (pse-sequencing.rst).

Every number comes from the page that shows the figure.

SPDX-License-Identifier: Apache-2.0
"""

from svgfig import (BAD, BAD_INK, EVP, FILL, GREY, INK, OK, OK_INK, POWER,
                    SRC_INK, Plot, line, polyline, rect, svg, text, write)

# Power of each class at the power sourcing equipment (tab-poe-classes).
PSE = {1: 4, 2: 6.7, 3: 14, 4: 30, 5: 45, 6: 60, 7: 75, 8: 90}


def class_methods():
    p = Plot(70, 40, 560, 170, (0, 10), (0, 60))
    phases = [(0, 1.6, FILL, "class events"), (1.6, 3.4, POWER, "power on"),
              (3.4, 10, EVP, "link up: LLDP frames")]
    body = []
    for a, b, fill, s in phases:
        body.append(rect(p.x(a), p.top, p.x(b) - p.x(a), p.h, fill, "none"))
        body.append(text(p.x((a + b) / 2), p.top - 8, s, 10, "middle"))
    body.append(p.frame())
    body += p.yticks([0, 25.5, 51], "allocation at the PD (W)", fmt="{:g}")
    pts = [(0, 0), (1.6, 0), (1.6, 25.5), (5.0, 25.5), (5.0, 51),
           (10, 51)]
    body.append(polyline(p.pts(pts), SRC_INK, 2.4))
    body.append(text(p.x(1.7), p.y(25.5) - 6, "Physical Layer: class 4, "
                     "25.5 W", 10))
    body.append(text(p.x(5.1), p.y(51) + 14, "Data Link Layer: raised to "
                     "51 W,", 10))
    body.append(text(p.x(5.1), p.y(51) + 27, "set in steps of 0.1 W", 10))
    body.append(text(p.left + p.w / 2, p.bottom + 18, "time (schematic)",
                     12, "middle"))
    body.append(text(10, p.bottom + 42, "Example: a class 6 powered device "
                     "given class 4 by its class events, then raised over "
                     "LLDP.", 11, fill=GREY))
    return svg(680, int(p.bottom + 54), body, "Classification methods")


def voltages():
    rows = [("powered device input", 37, 57, POWER),
            ("Type 1 PSE output", 44, 57, OK),
            ("Type 2 and 3 PSE output", 50, 57, OK),
            ("Type 4 PSE output", 52, 57, OK),
            ("USB Power Delivery", 5, 48, EVP)]
    n = len(rows)
    p = Plot(190, 20, 450, 26 * n, (0, 60), (0, n))
    body = [p.frame()]
    for k, (name, lo, hi, fill) in enumerate(rows):
        yc = p.y(n - k - 0.5)
        body.append(text(p.left - 8, yc + 4, name, 10, "end"))
        body.append(rect(p.x(lo), yc - 7, p.x(hi) - p.x(lo), 14, fill))
        body.append(text(p.x(lo) - 4, yc + 4, f"{lo:g}", 9, "end"))
    body.append(line(p.x(44), p.top, p.x(44), p.bottom, BAD_INK, 1.0, "4,3"))
    body += p.xticks([0, 10, 20, 30, 40, 50, 57], "voltage (V)", grid=False)
    body.append(text(10, p.bottom + 58, "The powered device input can be "
                     "below every PSE minimum (dashed: 44 V), so the power",
                     11, fill=GREY))
    body.append(text(10, p.bottom + 74, "always passes through a "
                     "converter.", 11, fill=GREY))
    return svg(680, int(p.bottom + 86), body, "Voltage ranges")


def power_split():
    p = Plot(40, 40, 600, 40, (0, 60), (0, 1))
    parts = [(0, 45, OK, "class 5: 45 W"),
             (45, 56.4, POWER, "board ≤ 11.4 W"),
             (56.4, 60, FILL, "loss")]
    body = []
    for a, b, fill, s in parts:
        body.append(rect(p.x(a), p.top, p.x(b) - p.x(a), p.h, fill))
        body.append(text(p.x((a + b) / 2), p.top + 25, s, 10, "middle"))
    body.append(line(p.x(56.4), p.top - 14, p.x(56.4), p.bottom, INK, 1.2))
    body.append(text(p.x(56.4), p.top - 18, "input × η = 56.4 W", 10,
                     "end"))
    body.append(text(p.x(60), p.top - 18, "60 W", 10, "end"))
    body += p.xticks([0, 10, 20, 30, 40, 45, 50, 60], "power (W)",
                     grid=False)
    return svg(680, int(p.bottom + 48), body, "Power split")


def highest(pin, board):
    c = 0
    for k, v in PSE.items():
        if v <= pin - board:
            c = k
    return c


def step_curve(p, pin):
    pts = []
    b = 0.0
    while b <= 40:
        pts.append((b, highest(pin, b)))
        b += 0.05
    out = []
    prev = None
    for x, y in pts:
        if prev is not None and y != prev[1]:
            out.append((x, prev[1]))
        out.append((x, y))
        prev = (x, y)
    return p.pts(out)


def class_board():
    body = []
    panels = (("USB Power Delivery in (η = 0.94)", 20,
               [(27, "27 W"), (45, "45 W"), (60, "60 W"), (100, "100 W")],
               0.94),
              ("Ethernet in (η = 0.85)", 300,
               [(25.5, "class 4"), (51, "class 6"), (71.3, "class 8")],
               0.85))
    cols = [GREY, OK_INK, SRC_INK, INK]
    for title, y0, inputs, eta in panels:
        p = Plot(70, y0 + 20, 440, 200, (0, 40), (0, 8.6))
        body.append(text(p.left, y0 + 10, title, 12, weight="bold"))
        body.append(p.frame())
        body += p.yticks([2, 4, 6, 8], "highest class", fmt="{:g}")
        body.append(text(p.left - 8, p.y(0) + 4, "none", 12, "end"))
        body += p.xticks([0, 10, 20, 30, 40], "board power (W)",
                         grid=False)
        for k, (pin, lab) in enumerate(inputs):
            col = cols[k % len(cols)]
            body.append(polyline(step_curve(p, pin * eta), col, 2.0))
            y = p.top + 16 + 16 * k
            body.append(line(p.right + 10, y - 4, p.right + 28, y - 4, col,
                             2.0))
            body.append(text(p.right + 32, y, lab, 10))
    return svg(680, 560, body, "Class against board power")


def budget_split():
    p = Plot(40, 30, 600, 40, (0, 80), (0, 1))
    parts = [(0, 45, OK, "Ethernet, class 5: 45 W"),
             (45, 80, EVP, "USB Type-C ports together: 35 W")]
    body = []
    for a, b, fill, s in parts:
        body.append(rect(p.x(a), p.top, p.x(b) - p.x(a), p.h, fill))
        body.append(text(p.x((a + b) / 2), p.top + 25, s, 10, "middle"))
    body.append(text(p.x(80), p.top - 8, "output budget 80 W", 10, "end"))
    body += p.xticks([0, 20, 40, 45, 60, 80], "power offered (W)",
                     grid=False)
    return svg(680, int(p.bottom + 48), body, "Budget split")


def supply_voltages():
    rows = [("Type 1 output range", 44, 57, OK),
            ("Types 2 to 4 output range", 50, 57, OK),
            ("supply near 54 V", 54, 54, SRC_INK),
            ("48 V USB supply", 45.1, 50.9, EVP)]
    n = len(rows)
    p = Plot(190, 20, 450, 28 * n, (40, 60), (0, n))
    body = [p.frame()]
    for k, (name, lo, hi, fill) in enumerate(rows):
        yc = p.y(n - k - 0.5)
        body.append(text(p.left - 8, yc + 4, name, 10, "end"))
        if lo == hi:
            body.append(line(p.x(lo), yc - 9, p.x(lo), yc + 9, fill, 3.0))
        else:
            body.append(rect(p.x(lo), yc - 7, p.x(hi) - p.x(lo), 14, fill))
    yu = p.y(0.5)
    body.append(line(p.x(48), yu - 7, p.x(48), yu + 7, INK, 1.2))
    body.append(text(p.x(50.9) + 4, yu + 4, "50.9", 9))
    body.append(line(p.x(43.2), yu - 10, p.x(43.2), yu + 10, BAD_INK, 2.0))
    body.append(text(p.x(43.2) - 4, yu + 4, "43.2 at a peak", 9, "end",
                     fill=BAD_INK))
    body.append(text(p.x(45.1) + 4, yu + 4, "45.1", 9))
    for v in (44, 50, 52):
        body.append(line(p.x(v), p.top, p.x(v), p.bottom, GREY, 0.8, "3,3"))
    body += p.xticks([40, 44, 45.1, 50, 52, 54, 57, 60], "voltage (V)",
                     grid=False)
    body.append(text(10, p.bottom + 58, "48 V ± 5 % plus 0.5 V in "
                     "transitions (tick at 48 V): as low as 45.1 V, so it",
                     11, fill=GREY))
    body.append(text(10, p.bottom + 74, "cannot be relied on to reach "
                     "50 V. The switch and cable drop more.", 11,
                     fill=GREY))
    return svg(680, int(p.bottom + 86), body, "Supply voltages")


if __name__ == "__main__":
    write("class-methods.svg", class_methods())
    write("voltages.svg", voltages())
    write("power-split.svg", power_split())
    write("class-board.svg", class_board())
    write("budget-split.svg", budget_split())
    write("supply-voltages.svg", supply_voltages())
