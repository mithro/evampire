"""Figures of the bidirectional pad gf180mcu_fd_io__bi_t.

Helper for figures.py: run that script, not this module.

SPDX-License-Identifier: Apache-2.0
"""

import gdskit
from shapely.geometry import box
import layfig
from layfig import CLAMP, DVDD, DVSS, HOT, INK, SECONDARY, Fig

CELL = "bi_t"
# Regions of the cell, as (x0, y0, x1, y1) in GDS micrometres.
NMOS = (9.8, 71.8, 65.2, 119.1)       # inside the inner guard ring
PMOS = (6.5, 131.8, 68.5, 199.3)      # the drivers' N-well
SECOND = (22.3, 266.7, 57.3, 309.9)   # resistors and both diode pairs


def cell():
    """The whole cell: where each part of the protection sits."""
    f = Fig(CELL, (0, 0, 75, 350), 2.7, top=58, right=75, bottom=150)
    lay = gdskit.load(CELL)
    f.silicon()
    f.geom(lay["metal5"].intersection(
        box(0, 0, 75, 66)), "metal", opacity=0.55)
    f.layer("pad", width=1.6, dash="5,3")
    x, y = f.px(37.5, 32)
    f.text(x, y - 4, "Bond pad", weight="bold")
    f.text(x, y + 14, "60 µm × 60 µm opening")
    top = f.oy - 30
    f.label("NMOS output drivers", (30, 95), (f.px(0, 95)[0], top),
            colour=HOT, weight="bold")
    f.label("PMOS output drivers", (30, 166), (f.px(0, 166)[0], top),
            colour=HOT, weight="bold")
    f.label("Pre-drivers", (20, 226), (f.px(0, 232)[0], top))
    f.label("Input buffer and logic", (20, 322), (f.px(0, 318)[0], top))
    bot = f.oy + f.dh + 30
    f.label("Guard rings", (70.2, 88), (f.px(0, 88)[0], bot))
    f.label("N-well of the PMOS drivers", (67.5, 150),
            (f.px(0, 166)[0], bot))
    f.label("Secondary protection:\nresistors and diodes", (45, 288),
            (f.px(0, 283)[0], bot), colour=SECONDARY, weight="bold")
    f.box(SECOND, colour=SECONDARY)
    f.dim((75, 0), (75, 350), "350 µm", offset=78, side="below")
    f.dim((0, 350), (75, 350), "75 µm", offset=14, side="below")
    return f


FIGURES = {"gds-cell": cell}
