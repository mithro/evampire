"""Figures of the bidirectional pad gf180mcu_fd_io__bi_t.

Helper for figures.py: run that script, not this module.

SPDX-License-Identifier: Apache-2.0
"""

import gdskit
from layfig import DVDD, DVSS, HOT, SECONDARY, SNAP, Fig
from shapely.geometry import box

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


def pad_net():
    """The PAD net: from the bond pad to every drain that protects it."""
    f = Fig(CELL, (0, 0, 75, 285), 3.3, top=62, bottom=112)
    net = gdskit.net(CELL, "PAD")
    f.silicon(opacity=0.4)
    f.geom(net["metal2"], "padnet", opacity=0.6)
    f.geom(net["comp"], "paddrain")
    f.layer("pad", width=1.6, dash="5,3")
    x, y = f.px(37.5, 32)
    f.text(x, y - 4, "Bond pad", weight="bold")
    f.text(x, y + 14, "metal 2 to metal 5, stacked")
    top = f.oy - 34
    f.label("4 NMOS drains,\neach shared by 2 fingers", (31.5, 95),
            (f.px(0, 95)[0], top), colour=HOT, weight="bold")
    f.label("6 PMOS drains,\neach shared by 2 fingers", (24.2, 166),
            (f.px(0, 166)[0], top), colour=HOT, weight="bold")
    f.label("Metal 2 wire, 2 µm wide, to the\nsecondary protection resistors",
            (37.5, 240), (f.px(0, 240)[0], top), colour=SECONDARY,
            weight="bold")
    bot = f.oy + f.dh + 30
    f.label("Metal 2 bus over both drivers", (55, 126),
            (f.px(0, 126)[0], bot))
    f.label("Resistors", (37.5, 272), (f.px(0, 266)[0], bot),
            colour=SECONDARY)
    return f


def paths():
    """Each discharge current drawn on the drivers it flows through."""
    f = Fig(CELL, (0, 64, 75, 206), 6.4, top=84, bottom=118)
    lay = gdskit.load(CELL)
    nets = {n: gdskit.net(CELL, n)["comp"] for n in ("PAD", "DVDD", "DVSS")}
    f.layer("nwell")
    rest = lay["comp"]
    for g in nets.values():
        rest = rest.difference(g)
    f.geom(rest, "other")
    f.geom(nets["DVDD"], "dvdd", opacity=0.85)
    f.geom(nets["DVSS"], "dvss", opacity=0.85)
    f.geom(nets["PAD"], "paddrain")
    f.layer("poly", opacity=0.9)
    # Positive pulse: P+ drains into the N-well and out through its N+ ring.
    for gx, ring in ((15.4, 8.2), (59.6, 66.8)):
        f.flow([(gx, 166), (ring, 166)])
    for gx in (24.2, 33.1, 41.9, 50.8):
        f.flow([(gx, 185.5), (gx, 197.6)])
        f.flow([(gx, 146.6), (gx, 133.4)])
    # Negative pulse: from the P+ ring into the N+ drains.
    for gx, ring in ((19.78, 11.0), (55.0, 64.0)):
        f.flow([(ring, 101), (gx, 101)])
    for gx in (31.5, 43.3):
        f.flow([(gx, 118.2), (gx, 112.6)])
        f.flow([(gx, 72.8), (gx, 76.8)])
    # Snapback: from each drain to the sources on both sides of it.
    for drain in (19.78, 31.5, 43.3, 55.0):
        for side in (-1, 1):
            f.flow([(drain + side * 2.6, 88), (drain + side * 5.9, 88)],
                   colour=SNAP, width=3.0)
    top = f.oy - 56
    f.label("Negative pulse: from the P+ ring (DVSS)\ninto the N+ drains, "
            "the NMOS drain diode", (11.0, 106), (f.px(0, 96)[0] - 20, top),
            colour=HOT, weight="bold")
    f.label("Positive pulse: from the P+ drains into the N-well and\nout "
            "through its N+ ring (DVDD), the PMOS drain diode", (9.5, 170),
            (f.px(0, 170)[0], top), colour=HOT, weight="bold")
    bot = f.oy + f.dh + 30
    f.label("Above 10.7 V: snapback from each\ndrain to the sources beside "
            "it", (35.6, 88), (f.px(0, 96)[0], bot), colour=SNAP,
            weight="bold")
    f.label("N-well under the PMOS drivers", (65.2, 150),
            (f.px(0, 166)[0], bot))
    return f


def secondary():
    """The secondary protection: four resistors and two pairs of diodes."""
    f = Fig(CELL, (21.5, 264.5, 53.5, 311.5), 14, left=178, top=70,
            right=195, bottom=104)
    f.silicon()
    f.layer("sab", width=1.0, dash="4,2")
    pad, inn = gdskit.net(CELL, "PAD"), gdskit.net(CELL, "IN")
    f.geom(pad["metal2"], "padnet", opacity=0.6)
    f.geom(inn["metal2"].union(inn["metal1"]), "innet", opacity=0.4)
    y = f.px(37.5, 0)[1] + 5
    f.label("PAD, on a metal 2\nwire from the\ndrivers", (37.5, 265.4),
            (f.ox - 12, y - 17), anchor="end", colour=HOT, weight="bold",
            lead="right")
    f.label("Protected net, on\nto the gates of the\ninput buffer",
            (37.2, 310.8), (f.ox + f.dw + 12, y - 17), anchor="start",
            colour=SECONDARY, weight="bold", lead="left")
    top = f.oy - 40
    f.label("4 polysilicon resistors,\n2.5 µm × 2.8 µm each", (32.85, 272.1),
            (f.px(0, 272.1)[0] - 30, top), colour=SECONDARY, weight="bold")
    f.label("2 P+ diodes in an N-well tied\nto DVDD, 20 µm × 1 µm each",
            (28.5, 283.2), (f.px(0, 292)[0] + 30, top), colour=DVDD,
            weight="bold")
    bot = f.oy + f.dh + 30
    f.label("2 N+ diodes in the P substrate, inside an\nN-well ring, "
            "20 µm × 1 µm each", (46.5, 304.05), (f.px(0, 293)[0], bot),
            colour=DVSS, weight="bold")
    return f


FIGURES = {"gds-cell": cell, "gds-pad-net": pad_net, "gds-paths": paths,
           "gds-secondary": secondary}
