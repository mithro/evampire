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


# The resistors and the two diode blocks inside SECOND.
SECOND_PARTS = ((21.7, 266.7, 52.7, 277.5), (21.7, 277.9, 52.7, 293.2),
                (21.7, 293.6, 52.7, 309.9))
NDRIVERS = (2.0, 69.0, 73.0, 124.8)      # NMOS output drivers and rings
PDRIVERS = (2.0, 125.2, 73.0, 208.0)     # PMOS output drivers and rings


def cell():
    """The whole cell, with the parts of the schematic in its colours.

    The layers are grey, so red, blue and black mean here only what they
    mean in the schematic of schematic.py, and each label is the
    schematic's own. What the schematic leaves out is named in grey.
    """
    f = Fig(CELL, (0, 0, 75, 350), 2.7, top=116, right=75, bottom=190)
    lay = gdskit.load(CELL)
    f.grey_silicon()
    f.geom(lay["metal5"].intersection(box(0, 0, 75, 66)), "metal",
           opacity=0.55, key=False)
    f.layer("pad", width=1.6, dash="5,3", key=False)
    x, y = f.px(37.5, 32)
    f.text(x, y - 10, "PAD", weight="bold", size=18)
    f.text(x, y + 10, "bond pad, 60 µm ×")
    f.text(x, y + 27, "60 µm opening")
    for region in (PREDRIVERS, BUFFERS, PULLS):
        f.box(region, colour=GREY, dash="5,4", width=1.4)
    for region in (NDRIVERS, PDRIVERS):
        f.region(region, HOT)
    for part in SECOND_PARTS:
        f.region(part, SECONDARY, width=2.2)
    f.region(INPUT, INK, opacity=0.12)
    top = f.oy - 46
    f.label("drain diode of\nNMOS drivers\n304 µm", (2.0, 97),
            (f.px(0, 97)[0], top - 17), colour=HOT, weight="bold")
    f.label("drain diode of\nPMOS drivers\n480 µm", (2.0, 166),
            (f.px(0, 166)[0], top - 17), colour=HOT, weight="bold")
    f.label("pre-\ndrivers", (2.0, 222), (f.px(0, 222)[0], top),
            colour=GREY)
    f.label("output signal\nbuffers", (3.6, 255), (f.px(0, 251)[0], top),
            colour=GREY)
    f.label("pull-up and\npull-down\nresistors", (3.8, 288),
            (f.px(0, 291)[0], top - 17), colour=GREY)
    f.label("input\nbuffer", (3.5, 327), (f.px(0, 327)[0], top),
            weight="bold")
    bot = f.oy + f.dh + 30
    # Each leader drops straight out of the cell before it turns.
    for text, gy, at in (("110 Ω: 4 of\n440 Ω in parallel", 272.1, 240),
                         ("40 µm² diode\nto DVDD", 285.5, 291),
                         ("40 µm² diode\nfrom DVSS", 301.7, 338)):
        f.label(text, (52.7, gy), (f.px(0, at)[0], bot), colour=SECONDARY,
                weight="bold", elbow=f.px(76.5, gy))
    f.note((HOT, HOT, 0.3), "primary", kind="tint")
    f.note((SECONDARY, SECONDARY, 0.3), "secondary", kind="tint")
    f.note((INK, INK, 0.12), "input buffer", kind="tint")
    f.note(GREY, "not in the schematic")
    f.note(INK, "rail clamp: in the supply pads, not here",
           kind="plain")
    f.note(INK, "DVDD and DVSS rings: metal over the cell, not drawn",
           kind="plain")
    f.title("gf180mcu_fd_io__bi_t, the bidirectional pad", up=98)
    f.dim((75, 0), (75, 350), "350 µm", offset=78, side="below")
    f.dim((0, 350), (75, 350), "75 µm", offset=14, side="below")
    return f


def pad_net():
    """The PAD net: from the bond pad to every drain that protects it."""
    f = Fig(CELL, (0, 0, 75, 285), 3.3, top=102, bottom=120)
    net = gdskit.net(CELL, "PAD")
    # Grey layers: red is then the schematic's primary protection only.
    f.grey_silicon()
    f.geom(net["comp"], "primdrain")
    f.geom(net["metal2"], "padwire", opacity=0.3, key=False)
    f.note(("#444444", INK, 0.3), "PAD net, metal 2, outlined in black",
           kind="tint")
    # A firm edge, so the wire can be followed across the cell.
    f.outline(net["metal2"].intersection(box(0, 66, 75, 285)), INK, width=1.1)
    f.region(SECOND_PARTS[0], SECONDARY, width=2.2)
    f.layer("pad", width=1.6, dash="5,3", key=False)
    x, y = f.px(37.5, 32)
    f.text(x, y - 26, "PAD", weight="bold", size=18)
    f.text(x, y - 6, "bond pad:")
    f.text(x, y + 11, "metal 2 to 5, stacked;")
    f.text(x, y + 28, "metal 2 shown, slotted")
    top = f.oy - 51
    f.label("drain diode of NMOS drivers\n304 µm: 4 drains of 38 µm,\na gate on each side", (19.78, 95),
            (f.px(0, 88)[0], top), colour=HOT, weight="bold")
    f.label("drain diode of PMOS drivers\n480 µm: 6 drains of 40 µm,\na gate on each side", (15.4, 166),
            (f.px(0, 170)[0], top), colour=HOT, weight="bold")
    f.label("metal 2 wire, 2 µm wide,\nfrom PAD to the 110 Ω", (37.5, 232),
            (f.px(0, 240)[0], top + 17), weight="bold")
    bot = f.oy + f.dh + 30
    f.label("metal 2 joining PAD to the\ndrains of both drivers", (62, 126),
            (f.px(0, 150)[0], bot), weight="bold")
    f.label("110 Ω: 4 of\n440 Ω in parallel", (52.7, 272.1),
            (f.px(0, 262)[0], bot), colour=SECONDARY, weight="bold")
    f.note((SECONDARY, SECONDARY, 0.3), "secondary", kind="tint")
    f.note(INK, "NMOS drains: diodes from the P substrate on DVSS",
           kind="plain")
    f.note(INK, "PMOS drains: diodes to the N-well on DVDD", kind="plain")
    f.note(INK, "DVDD and DVSS rings: not drawn", kind="plain")
    f.note(INK, "40 µm² diodes, input buffer: further right", kind="plain")
    f.note(INK, "rail clamp: in the supply pads, not here", kind="plain")
    f.title("gf180mcu_fd_io__bi_t: the PAD net", up=84)
    return f



def _drivers(window, title):
    """The output drivers with each diffusion in the colour of its net."""
    f = Fig(CELL, window, 5.4, top=136, bottom=150)
    lay = gdskit.load(CELL)
    nets = {n: gdskit.net(CELL, n)["comp"] for n in ("PAD", "DVDD", "DVSS")}
    f.layer("nwell")
    rest = lay["comp"]
    for g in nets.values():
        rest = rest.difference(g)
    f.geom(rest, "other")
    f.geom(nets["DVDD"], "dvdd", opacity=0.7)
    f.geom(nets["DVSS"], "dvss", opacity=0.7)
    f.geom(nets["PAD"], "paddrain")
    # Pale gates, so the arrows stand out against them.
    f.geom(lay["poly"], "gate", opacity=0.45)
    f.title(title, up=118)
    f.note(DVDD, "on DVDD")
    f.note(DVSS, "on DVSS")
    return f


def paths():
    """The discharge currents on the drivers, one panel per polarity."""
    diode = "current through a drain diode"
    a = _drivers((0, 64, 75, 128), "(a) Negative, PAD to DVSS\nand PAD to DVDD")
    # From the P+ ring into the N+ drains.
    for gx, ring in ((19.78, 11.0), (55.0, 64.0)):
        a.flow([(ring, 101), (gx, 101)], key=diode)
    for gx in (31.5, 43.3):
        a.flow([(gx, 118.2), (gx, 108.5)], key=diode)
        a.flow([(gx, 72.4), (gx, 81.0)], key=diode)
    x, y = a.px(7.3, 84)
    a.text(x, y + 5, "NMOS output drivers", weight="bold")
    top = a.oy - 56
    a.label("NMOS drain: from the P+ guard\nring on DVSS into the N+ drains",
            (15.5, 101), (a.px(0, 96)[0], top + 17), colour=HOT,
            weight="bold")
    bot = a.oy + a.dh + 30
    a.label("P+ guard ring,\non DVSS", (64.3, 80), (a.ox, bot),
            anchor="start", colour=DVSS, weight="bold")
    a.label("outer N+ guard\nring, on DVDD", (70.5, 110),
            (a.px(0, 112)[0], bot), colour=DVDD, weight="bold")

    b = _drivers((0, 64, 75, 206), "(b) Positive, PAD to DVSS and PAD to DVDD")
    # P+ drains into the N-well and out through its N+ ring.
    for gx, ring in ((15.4, 8.6), (59.6, 66.4)):
        b.flow([(gx, 166), (ring, 166)], key=diode)
    for gx in (24.2, 33.1, 41.9, 50.8):
        b.flow([(gx, 185.5), (gx, 196.6)], key=diode)
        b.flow([(gx, 146.6), (gx, 134.6)], key=diode)
    # Snapback: from each NMOS drain to the sources on both sides of it.
    for drain in (19.78, 31.5, 43.3, 55.0):
        for side in (-1, 1):
            b.flow([(drain + side * 0.9, 90 + side * 5),
                    (drain + side * 5.86, 90 + side * 5)],
                   colour=SNAP, width=5.0,
                   key="snapback (dashed in the schematic)")
    x, y = b.px(7.3, 84)
    b.text(x, y + 5, "NMOS output drivers", weight="bold")
    x, y = b.px(3.4, 146)
    b.text(x, y + 5, "PMOS output drivers", weight="bold")
    top = b.oy - 56
    b.label("output NMOS snaps back above\n10.7 V (Positive, PAD to DVSS):\n"
            "from each drain to the sources\nbeside it, on DVSS", (20.7, 95),
            (b.px(0, 92)[0], top - 17), colour=SNAP, weight="bold")
    b.label("PMOS drain: from the P+ drains into the\nN-well and out through "
            "its N+ guard ring\non DVDD", (24.2, 189),
            (b.px(0, 168)[0], top), colour=HOT, weight="bold")
    bot = b.oy + b.dh + 30
    b.label("N-well, seen between the\ndrains and its guard ring", (65.2, 150),
            (b.px(0, 132)[0], bot))
    b.label("N+ guard ring,\non DVDD", (67.3, 180), (b.px(0, 166)[0], bot),
            colour=DVDD, weight="bold")
    b.label("outer P+ guard\nring, on DVSS", (72.0, 200), (b.ox + b.dw, bot),
            anchor="end", colour=DVSS, weight="bold")
    a.attach(b)
    a.note(INK, "PMOS avalanche above 9.7 V: not drawn", kind="plain")
    a.note(INK, "rail clamp: in the supply pads, not here", kind="plain")
    return a


def secondary():
    """The secondary protection: four resistors and two pairs of diodes."""
    f = Fig(CELL, (21.5, 264.5, 53.5, 311.5), 14, left=178, top=126,
            right=195, bottom=130)
    lay = gdskit.load(CELL)
    # Grey layers: blue is then the schematic's secondary protection only.
    f.grey_silicon(named=True)
    pad, inn = gdskit.net(CELL, "PAD"), gdskit.net(CELL, "IN")
    # Blue is the schematic's three parts; its wires are black, so the
    # metal is too. The parts are drawn over the metal that covers them.
    f.geom(pad["metal2"], "padwire", opacity=0.3, key=False)
    f.note(("#444444", INK, 0.3), "PAD net, metal 2", kind="tint")
    f.outline(pad["metal2"], INK, width=1.1)
    metal = inn["metal2"].union(inn["metal1"])
    f.geom(metal, "padwire", opacity=0.22, key=False)
    f.outline(metal, INK, width=1.0)
    bodies = lay["poly"].intersection(lay["resistor"]).intersection(
        box(*SECOND))
    f.geom(bodies, "secpart", opacity=0.85)
    f.geom(inn["comp"].intersection(lay["pplus"]), "secpart", opacity=0.85)
    f.geom(inn["comp"].intersection(lay["nplus"]), "secpart", opacity=0.85)
    f.layer("sab", width=1.0)
    y = f.px(37.5, 0)[1] + 5
    f.label("PAD, on a metal 2\nwire from the\ndrivers", (37.5, 265.4),
            (f.ox - 12, y - 17), anchor="end", weight="bold", lead="right")
    f.label("to the input\nbuffer",
            (37.2, 310.8), (f.ox + f.dw + 12, y - 8), anchor="start",
            weight="bold", lead="left")
    top = f.oy - 40
    f.label("110 Ω: 4 of 440 Ω in parallel,\npolysilicon, each 2.5 µm wide\n"
            "and 2.8 µm long under the\nsilicide block",
            (32.85, 272.1), (f.ox + 60, top - 34), colour=SECONDARY,
            weight="bold")
    f.label("N+ guard ring,\non DVDD", (26.05, 283), (f.px(0, 283)[0], top))
    f.label("also to the pull\nresistors", (22.3, 292.9),
            (f.px(0, 292.9)[0], top), colour=GREY)
    f.label("P+ guard ring,\non DVSS", (26.05, 302), (f.px(0, 302)[0], top))
    bot = f.oy + f.dh + 30
    f.label("40 µm² diode to DVDD: 2 P+ strips of\n20 µm × 1 µm in an N-well held on\n"
            "DVDD by the N+ guard ring round them", (46.5, 283.2), (f.px(0, 278)[0], bot),
            colour=SECONDARY, weight="bold", also=[(46.5, 287.87)])
    f.label("40 µm² diode from DVSS: 2 N+ strips of\n20 µm × 1 µm in substrate held on\n"
            "DVSS by the P+ guard ring round them", (46.5, 304.05), (f.px(0, 304)[0], bot),
            colour=SECONDARY, weight="bold", also=[(46.5, 299.38)])
    f.note(("#444444", INK, 0.22),
           "wire after the 110 Ω: metal, with openings", kind="tint")
    f.note(INK, "the diode strips lie under the metal", kind="plain")
    f.note(GREY, "not in the schematic")
    f.note(INK, "DVDD and DVSS rings: not drawn", kind="plain")
    f.note(INK, "primary: to the left, not here", kind="plain")
    f.note(INK, "rail clamp: in the supply pads", kind="plain")
    f.title("gf180mcu_fd_io__bi_t: the secondary protection", up=108)
    return f


FIGURES = {"gds-cell": cell, "gds-pad-net": pad_net, "gds-paths": paths,
           "gds-secondary": secondary}
