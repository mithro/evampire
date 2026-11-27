"""Figures of the bidirectional pad gf180mcu_fd_io__bi_t.

Helper for figures.py: run that script, not this module.

SPDX-License-Identifier: Apache-2.0
"""

from shapely.geometry import box

import gdskit
from layfig import DVDD, DVSS, GREY, HOT, INK, SECONDARY, SNAP, Fig

CELL = "bi_t"
# Blocks of the cell, as (x0, y0, x1, y1) in GDS micrometres, from the
# placement of the foundry's sub-cells.
PREDRIVERS = (2.0, 211.7, 73.3, 242.3)   # comp018green_out_predrv, four
BUFFERS = (3.6, 245.5, 70.4, 264.1)      # out_sigbuf_oe, _a and sigbuf_1
SECOND = (21.7, 266.7, 52.7, 309.9)      # comp018green_esd_cdm
INPUT = (3.5, 311.6, 71.8, 341.8)        # rest of comp018green_inpath_cms_smt
PULLS = (3.8, 266.7, 18.8, 309.5)        # comp018green_in_pupd resistors


NDRIVERS = (2.0, 69.0, 73.0, 124.8)      # NMOS output drivers and rings
PDRIVERS = (2.0, 125.2, 73.0, 208.0)     # PMOS output drivers and rings


def cell():
    """The whole cell, with the parts of the schematic in its colours.

    The layers are grey, so red, blue and black mean here only what they
    mean in the schematic of schematic.py, and each label is the
    schematic's own. What the schematic leaves out is named in grey.
    """
    f = Fig(CELL, (0, 0, 75, 350), 2.7, top=90, right=75, bottom=190)
    lay = gdskit.load(CELL)
    f.grey_silicon()
    f.geom(lay["metal5"].intersection(box(0, 0, 75, 66)), "metal",
           opacity=0.55, key=False)
    f.layer("pad", width=1.6, dash="5,3")
    x, y = f.px(37.5, 32)
    f.text(x, y - 10, "PAD", weight="bold", size=18)
    f.text(x, y + 10, "bond pad, 60 µm ×")
    f.text(x, y + 27, "60 µm opening")
    for region in (PREDRIVERS, BUFFERS, PULLS):
        f.box(region, colour=GREY, dash="5,4", width=1.4)
    for region in (NDRIVERS, PDRIVERS):
        f.region(region, HOT)
    f.region(SECOND, SECONDARY)
    f.region(INPUT, INK, opacity=0.12)
    top = f.oy - 46
    f.label("drain diode of\nNMOS drivers\n304 µm", (2.0, 97),
            (f.px(0, 97)[0], top - 17), colour=HOT, weight="bold")
    f.label("drain diode of\nPMOS drivers\n480 µm", (2.0, 166),
            (f.px(0, 166)[0], top - 17), colour=HOT, weight="bold")
    f.label("pre-\ndrivers", (2.0, 222), (f.px(0, 222)[0], top),
            colour=GREY)
    f.label("output signal\nbuffers", (3.6, 255), (f.px(0, 255)[0], top),
            colour=GREY)
    f.label("pull-up and\npull-down\nresistors", (3.8, 288),
            (f.px(0, 288)[0], top - 17), colour=GREY)
    f.label("input\nbuffer", (3.5, 327), (f.px(0, 327)[0], top),
            weight="bold")
    bot = f.oy + f.dh + 30
    f.label("110 Ω\n(4 × 440 Ω)", (36.0, 272.1), (f.px(0, 246)[0], bot),
            colour=SECONDARY, weight="bold")
    f.label("40 µm² diode\nto DVDD", (49.0, 285.5), (f.px(0, 291)[0], bot),
            colour=SECONDARY, weight="bold")
    f.label("40 µm² diode\nfrom DVSS", (49.0, 301.7), (f.px(0, 338)[0], bot),
            colour=SECONDARY, weight="bold")
    f.note((HOT, HOT, 0.3), "primary", kind="tint")
    f.note((SECONDARY, SECONDARY, 0.3), "secondary", kind="tint")
    f.note((INK, INK, 0.12), "input buffer", kind="tint")
    f.note(GREY, "not in the schematic")
    f.note(INK, "rail clamp: in the supply pads, not here",
           kind="plain")
    f.note(INK, "DVDD and DVSS rings: metal over the cell, not drawn",
           kind="plain")
    f.dim((75, 0), (75, 350), "350 µm", offset=78, side="below")
    f.dim((0, 350), (75, 350), "75 µm", offset=14, side="below")
    return f


def pad_net():
    """The PAD net: from the bond pad to every drain that protects it."""
    f = Fig(CELL, (0, 0, 75, 285), 3.3, top=62, bottom=120)
    lay = gdskit.load(CELL)
    net = gdskit.net(CELL, "PAD")
    f.silicon(opacity=0.45)
    # The drivers' gates at full strength: every drain lies between two.
    f.geom(lay["poly"].intersection(box(5, 70, 70, 190)), "poly", key=False)
    f.geom(net["metal2"], "padnet", opacity=0.7)
    f.geom(net["comp"], "paddrain")
    f.geom(lay["resistor"].intersection(box(*SECOND)), "resistor", width=1.2)
    f.layer("pad", width=1.6, dash="5,3")
    x, y = f.px(37.5, 32)
    f.text(x, y - 16, "Bond pad", weight="bold")
    f.text(x, y + 2, "metal 2 to 5, stacked;")
    f.text(x, y + 19, "metal 2 shown, slotted")
    top = f.oy - 34
    f.label("4 NMOS drains,\neach between 2 gates", (19.78, 95),
            (f.px(0, 95)[0], top), colour=HOT, weight="bold")
    f.label("6 PMOS drains,\neach between 2 gates", (15.4, 166),
            (f.px(0, 166)[0], top), colour=HOT, weight="bold")
    f.label("Metal 2 wire, 2 µm wide", (37.5, 232), (f.px(0, 232)[0], top + 17),
            colour=HOT, weight="bold")
    bot = f.oy + f.dh + 30
    f.label("Gate\n(polysilicon)", (59.68, 104), (f.px(0, 100)[0], bot))
    f.label("Metal 2 joining the drains\nof both drivers", (62, 126),
            (f.px(0, 150)[0], bot), colour=HOT, weight="bold")
    f.label("4 secondary protection\nresistors", (45.2, 272.1),
            (f.px(0, 258)[0], bot), colour=SECONDARY, weight="bold")
    f.note(HOT, "on the PAD net")
    f.note(SECONDARY, "secondary protection")
    return f


def paths():
    """Each discharge current drawn on the drivers it flows through."""
    f = Fig(CELL, (0, 64, 75, 206), 6.4, top=84, bottom=146)
    lay = gdskit.load(CELL)
    nets = {n: gdskit.net(CELL, n)["comp"] for n in ("PAD", "DVDD", "DVSS")}
    f.layer("nwell")
    rest = lay["comp"]
    for g in nets.values():
        rest = rest.difference(g)
    f.geom(rest, "other", opacity=0.6)
    f.geom(nets["DVDD"], "dvdd", opacity=0.7)
    f.geom(nets["DVSS"], "dvss", opacity=0.7)
    f.geom(nets["PAD"], "paddrain")
    # Pale gates, so the purple snapback arrows stand out against them.
    f.layer("poly", opacity=0.45)
    f.geom(lay["poly"].intersection(lay["comp"]), "gate", opacity=0.45)
    diode = "discharge current through a drain diode"
    # Positive pulse: P+ drains into the N-well and out through its N+ ring.
    for gx, ring in ((15.4, 8.6), (59.6, 66.4)):
        f.flow([(gx, 166), (ring, 166)], key=diode)
    for gx in (24.2, 33.1, 41.9, 50.8):
        f.flow([(gx, 185.5), (gx, 196.6)], key=diode)
        f.flow([(gx, 146.6), (gx, 134.6)], key=diode)
    # Negative pulse: from the P+ ring into the N+ drains.
    for gx, ring in ((19.78, 11.0), (55.0, 64.0)):
        f.flow([(ring, 101), (gx, 101)], key=diode)
    for gx in (31.5, 43.3):
        f.flow([(gx, 118.2), (gx, 108.5)], key=diode)
        f.flow([(gx, 72.4), (gx, 81.0)], key=diode)
    # Snapback: from each drain to the sources on both sides of it.
    for drain in (19.78, 31.5, 43.3, 55.0):
        for side in (-1, 1):
            f.flow([(drain + side * 0.9, 90 + side * 5),
                    (drain + side * 5.86, 90 + side * 5)],
                   colour=SNAP, width=5.0,
                   key="discharge current in snapback")
    x, y = f.px(7.3, 84)
    f.text(x, y + 5, "NMOS output drivers", weight="bold")
    x, y = f.px(3.4, 146)
    f.text(x, y + 5, "PMOS output drivers", weight="bold")
    top = f.oy - 56
    f.label("Negative pulse: NMOS drain diode, from the\nP+ guard ring on DVSS "
            "into the N+ drains", (15.5, 101), (f.px(0, 104)[0], top),
            colour=HOT, weight="bold")
    f.label("Positive pulse: PMOS drain diode, from the P+ drains\ninto "
            "the N-well and out through its N+ guard ring on DVDD", (24.2, 189),
            (f.px(0, 170)[0], top), colour=HOT, weight="bold")
    bot = f.oy + f.dh + 30
    f.label("P+ guard ring,\non DVSS", (64.3, 80), (f.ox, bot), anchor="start",
            colour=DVSS, weight="bold")
    f.label("Positive pulse above 10.7 V:\nsnapback from each NMOS drain\n"
            "to the sources beside it, on DVSS", (56.6, 95),
            (f.px(0, 110)[0], bot), colour=SNAP, weight="bold",
            elbow=(f.px(0, 86)[0], f.oy + f.dh + 12))
    f.label("N-well, seen between the\ndrains and its guard ring", (65.2, 150),
            (f.px(0, 166)[0], bot))
    f.label("N+ guard ring,\non DVDD", (67.3, 188), (f.ox + f.dw, bot),
            anchor="end", colour=DVDD, weight="bold")
    f.note(DVDD, "on DVDD")
    f.note(DVSS, "on DVSS")
    return f


def secondary():
    """The secondary protection: four resistors and two pairs of diodes."""
    f = Fig(CELL, (21.5, 264.5, 53.5, 311.5), 14, left=178, top=70,
            right=195, bottom=130)
    lay = gdskit.load(CELL)
    f.silicon()
    f.layer("sab", width=1.0)
    pad, inn = gdskit.net(CELL, "PAD"), gdskit.net(CELL, "IN")
    f.geom(pad["metal2"], "padnet", opacity=0.7)
    metal = inn["metal2"].union(inn["metal1"])
    f.geom(metal, "innet", opacity=0.3, key=False)
    f.outline(metal, "#12305f", width=2.0)
    # Outline the diode strips, which the metal covers.
    f.outline(inn["comp"].intersection(lay["pplus"]), INK, width=2.0,
              dash="5,4")
    f.outline(inn["comp"].intersection(lay["nplus"]), INK, width=2.0,
              dash="5,4")
    y = f.px(37.5, 0)[1] + 5
    f.label("PAD, on a metal 2\nwire from the\ndrivers", (37.5, 265.4),
            (f.ox - 12, y - 17), anchor="end", colour=HOT, weight="bold",
            lead="right")
    f.label("Protected net, on\nto the gates of the\ninput buffer",
            (37.2, 310.8), (f.ox + f.dw + 12, y - 17), anchor="start",
            colour=SECONDARY, weight="bold", lead="left")
    top = f.oy - 40
    f.label("4 polysilicon resistors of 440 Ω in parallel, 110 Ω in all:\n"
            "each 2.5 µm wide and 2.8 µm long under the silicide block",
            (32.85, 272.1),
            (f.px(0, 272.1)[0] - 40, top), colour=SECONDARY, weight="bold")
    f.label("Protected net, also to the\npull-up and pull-down resistors",
            (22.3, 292.9), (f.px(0, 292.9)[0] + 70, top), colour=SECONDARY,
            weight="bold")
    bot = f.oy + f.dh + 30
    f.label("Diode to DVDD, 40 µm²: 2 P+ strips of\n20 µm × 1 µm in an N-well held on\n"
            "DVDD by the N+ ring round them", (46.5, 283.2), (f.px(0, 278)[0], bot),
            colour=SECONDARY, weight="bold", also=[(46.5, 287.87)])
    f.label("Diode from DVSS, 40 µm²: 2 N+ strips of\n20 µm × 1 µm in substrate held on\n"
            "DVSS by the P+ ring round them", (46.5, 304.05), (f.px(0, 304)[0], bot),
            colour=SECONDARY, weight="bold", also=[(46.5, 299.38)])
    f.note((SECONDARY, "#12305f", 0.3),
           "protected net, metal 1 and 2, with openings", kind="tint")
    f.note(INK, "diode strip, under metal", kind="box")
    f.note(INK, "metal is translucent: layers under it look darker",
           kind="plain")
    f.note(HOT, "on the PAD net")
    f.note(SECONDARY, "on the protected net")

    return f


FIGURES = {"gds-cell": cell, "gds-pad-net": pad_net, "gds-paths": paths,
           "gds-secondary": secondary}
