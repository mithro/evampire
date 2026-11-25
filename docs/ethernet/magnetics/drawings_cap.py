"""On-chip capacitor drawing for the magnetics pages: cap-area (series
devices and the two kinds of on-chip capacitor). Called from
drawings.py. Values are those quoted on coupling-capacitors.rst.

SPDX-License-Identifier: Apache-2.0
"""

import math

from drawings import (INK, GREY, RED, OXIDE, METAL, svg, text, line, rect)


def cap_area():
    w, h = 660, 330
    b = [text(165, 22, "N devices in series", weight="bold"),
         text(495, 22, "Two kinds of on-chip capacitor", weight="bold")]
    # Left: N = 1, 2, 3; each device N times larger, area N squared.
    unit = 22
    y = 50
    for n in (1, 2, 3):
        side = unit * math.sqrt(n)
        x = 20
        for k in range(n):
            b.append(rect(x, y, side, side, "#fff2cc"))
            if k < n - 1:
                b.append(line(x + side, y + side / 2, x + side + 8,
                              y + side / 2))
            x += side + 8
        b.append(text(x + 4, y + side / 2 + 4,
                      f"N = {n}: area {n * n}×", anchor="start", size=12))
        y += side + 22
    b.append(text(20, y + 8, "each device N times larger,", anchor="start",
                  size=11, fill=GREY))
    b.append(text(20, y + 22, "so the area grows as N²", anchor="start",
                  size=11, fill=GREY))
    b.append(line(330, 10, 330, h - 10, GREY, 0.8))
    # Right: oxide stack with a MIM capacitor and a whole-stack capacitor.
    x0, x1, top, bot = 350, 640, 60, 250
    b.append(rect(x0, top, x1 - x0, bot - top, OXIDE))
    for k, yy in enumerate((240, 195, 150, 105, 66)):
        b.append(text(x1 + 4, yy + 4, f"M{k + 1}", anchor="start", size=10,
                      fill=GREY))
    # MIM: two plates close together just under the top metal.
    b.append(rect(370, 92, 100, 8, METAL))
    b.append(rect(370, 104, 100, 8, METAL))
    b.append(text(420, 84, "MIM capacitor", size=11))
    b.append(text(420, 132, "thin insulator:", size=10))
    b.append(text(420, 145, "2.0 fF/µm², 6.6 V", size=10))
    b.append(text(420, 158, "16 nF in 8.0 mm²", size=10))
    # Whole stack: plates on M1 and M5.
    b.append(rect(500, 58, 120, 8, METAL))
    b.append(rect(500, 236, 120, 8, METAL))
    b.append(line(612, 70, 612, 232, RED, 1.2))
    b.append(text(553, 130, "whole stack,", size=10, fill=RED))
    b.append(text(553, 143, "about 5 µm:", size=10, fill=RED))
    b.append(text(553, 156, "0.0069 fF/µm²", size=10, fill=RED))
    b.append(text(553, 169, "16 nF in", size=10, fill=RED))
    b.append(text(553, 182, "about 2300 mm²", size=10, fill=RED))
    b.append(text(495, 275, "schematic, not to scale", size=11, fill=GREY))
    return svg(w, h, b)
