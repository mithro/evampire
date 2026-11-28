"""Figures of the bidirectional pad gf180mcu_fd_io__bi_t.

Helper for figures.py: run that script, not this module.

SPDX-License-Identifier: Apache-2.0
"""

from shapely.geometry import box

import gdskit
from layfig import (CLAMP, DVDD, DVSS, GREY, HOT, INK, PAPER, SECONDARY,
                    SNAP, Fig)

CELL = "bi_t"
# Blocks of the cell, as (x0, y0, x1, y1) in GDS micrometres, from the
# placement of the foundry's sub-cells.
PREDRIVERS = (2.0, 211.7, 73.3, 242.3)   # comp018green_out_predrv, four
BUFFERS = (3.6, 245.5, 70.4, 264.1)      # out_sigbuf_oe, _a and sigbuf_1
SECOND = (21.7, 266.7, 52.7, 309.9)      # comp018green_esd_cdm
# The rest of comp018green_inpath_cms_smt, round the two blocks above.
INPUT = ((3.5, 311.6, 71.8, 341.8), (54.0, 266.7, 71.6, 311.6))
PULLS = (3.8, 266.7, 18.8, 309.5)        # comp018green_in_pupd resistors
# The resistors and the two diode blocks inside SECOND.
SECOND_PARTS = ((21.7, 266.7, 52.7, 277.5), (21.7, 277.9, 52.7, 293.2),
                (21.7, 293.6, 52.7, 309.9))
RINGS = ("DVDD and DVSS rings: stripes of metal 3 to 5 over the whole "
         "cell, not drawn")
PADMETAL = (("#9aa5b1", "#6b7684", 0.55), "bond pad, metal 5")


def cell(alone=True):
    """The whole cell, with the parts of the schematic in its colours.

    `alone` adds a note that the rail clamp is in another cell, for the
    figure that does not show the supply pad under this one.

    The layers are grey, so red, blue and black mean here only what they
    mean in the schematic of schematic.py, and each label is the
    schematic's own. What the schematic leaves out is named in grey.
    """
    f = Fig(CELL, (0, 0, 75, 350), 2.7, top=132, right=75, bottom=190)
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
    # The schematic's two red diodes are the drains on the PAD net.
    f.geom(gdskit.net(CELL, "PAD")["comp"], "primdrain")
    for part in SECOND_PARTS:
        f.region(part, SECONDARY, width=2.2)
    for region in INPUT:
        f.region(region, INK, opacity=0.12)
    top = f.oy - 46
    f.label("drain diode of\nNMOS drivers:\n304 µm of gate,\n8 gates of 38 µm",
            (19.78, 97), (f.px(0, 97)[0], top - 34), colour=HOT,
            weight="bold")
    f.label("drain diode of\nPMOS drivers:\n480 µm of gate,\n"
            "12 gates of 40 µm",
            (15.4, 166), (f.px(0, 166)[0], top - 34), colour=HOT,
            weight="bold")
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
    f.note((SECONDARY, SECONDARY, 0.3), "secondary", kind="tint")
    f.note((INK, INK, 0.12), "input buffer", kind="tint")
    f.note(GREY, "not in the schematic")
    f.note(INK, RINGS, kind="plain")
    f.note(*PADMETAL, kind="tint")
    f.note(INK, "metal of the PAD net beyond the bond pad: not drawn",
           kind="plain")
    f.title("gf180mcu_fd_io__bi_t, the bidirectional pad", up=114)
    if alone:
        # In the schematic's orange, where the reader looks for those parts.
        f.text(f.ox + f.dw, f.oy - 114, "rail clamp and rail diode: not in "
               "this cell, only in the supply pads", anchor="end",
               fill=CLAMP, weight="bold", halo=False)
    f.dim((75, 0), (75, 350), "350 µm", offset=78, side="below")
    f.dim((0, 350), (75, 350), "75 µm", offset=14, side="below")
    return f


def pad_net():
    """The PAD net: from the bond pad to every drain that protects it."""
    f = Fig(CELL, (0, 0, 75, 278), 3.3, top=132, bottom=166)
    net = gdskit.net(CELL, "PAD")
    # Grey layers: red is then the schematic's primary protection only.
    f.grey_silicon()
    f.geom(net["comp"], "primdrain")
    # Under the metal, so that its edge crosses them unbroken.
    for region in (PREDRIVERS, BUFFERS, (*PULLS[:3], 278)):
        f.box(region, colour=GREY, dash="5,4", width=1.4)
    # The metal with its small slots closed, ruled and outlined as one
    # piece from the bond pad to the far end of the wire.
    metal = net["metal2"].buffer(1.5).buffer(-1.5)
    f.geom(metal, "padwire", key=False)
    f.outline(metal, INK, width=1.3)
    f.note(("url(#wire)", INK, 1.0),
           "PAD net, metal 2: ruled, outlined in black", kind="tint")
    f.region(SECOND_PARTS[0], SECONDARY, width=2.2)
    f.layer("pad", width=1.6, dash="5,3", key=False)
    x, y = f.px(37.5, 32)
    # A plain patch under the words, clear of the ruling.
    f.over.append(f'<rect x="{x - 96:.1f}" y="{y - 46:.1f}" width="192" '
                  'height="82" fill="#ffffff" opacity="0.92"/>')
    f.text(x, y - 26, "PAD", weight="bold", size=18)
    f.text(x, y - 6, "bond pad, 60 µm opening:")
    f.text(x, y + 11, "metal 2 to 5, stacked;")
    f.text(x, y + 28, "metal 2 shown")
    top = f.oy - 68
    f.label("drain diode of NMOS\ndrivers: 304 µm of gate,\n4 drains, "
            "each between\n2 gates of 38 µm", (19.78, 95),
            (f.px(0, 95)[0], top), colour=HOT, weight="bold")
    f.label("drain diode of PMOS\ndrivers: 480 µm of gate,\n6 drains, "
            "each between\n2 gates of 40 µm", (15.4, 166),
            (f.px(0, 166)[0], top), colour=HOT, weight="bold")
    f.label("a gate", (24.47, 112), (f.px(0, 128)[0], top + 51), colour=GREY)
    f.label("metal 2 wire,\n2 µm wide, from\nPAD to the 110 Ω", (37.5, 232),
            (f.px(0, 232)[0], top + 17), weight="bold")
    f.label("pull-up and\npull-down\nresistors", (3.8, 272.1),
            (f.ox + f.dw, top + 17), anchor="end", colour=GREY,
            elbow=(f.px(0, 272.1)[0], f.oy - 12))
    bot = f.oy + f.dh + 30
    f.label("slot in the metal over an\nNMOS source; the PMOS\nsources "
            "have none", (61.0, 80), (f.px(0, 84)[0], bot), colour=GREY)
    # A point well inside the metal between the two drivers.
    join = metal.intersection(box(60, 118, 71, 134)).representative_point()
    f.label("metal 2 joining PAD to the\ndrains of both drivers",
            (join.x, join.y), (f.px(0, 152)[0], bot), weight="bold")
    f.label("pre-drivers", (73.3, 222), (f.px(0, 222)[0], bot), colour=GREY)
    f.label("output signal\nbuffers", (70.4, 252), (f.px(0, 252)[0], bot),
            colour=GREY)
    f.label("110 Ω: 4 of 440 Ω in parallel", (52.7, 272.1),
            (f.ox + f.dw, bot + 46), anchor="end", colour=SECONDARY,
            weight="bold", elbow=(f.px(0, 272.1)[0], f.oy + f.dh + 8))
    f.note((SECONDARY, SECONDARY, 0.3), "secondary", kind="tint")
    f.note(GREY, "not in the schematic")
    f.note(INK, "NMOS drains: diodes from the P-type silicon on DVSS",
           kind="plain")
    f.note(INK, "PMOS drains: diodes to the N-well on DVDD", kind="plain")
    f.note(INK, RINGS, kind="plain")
    f.note(INK, "40 µm² diodes, input buffer: further right", kind="plain")
    f.note(INK, "rail clamp and rail diode: in the supply pads",
           kind="plain")
    f.title("gf180mcu_fd_io__bi_t: the PAD net", up=114)
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
    f.geom(lay["poly"].intersection(lay["comp"]), "gate", opacity=0.45)
    f.title(title, up=118)
    f.note(DVDD, "on DVDD")
    f.note(DVSS, "on DVSS")
    return f


def paths():
    """The discharge currents on the drivers, one panel per polarity."""
    diode = "current through a drain diode"
    snap = "second path: NMOS snapback"
    a = _drivers((0, 64, 75, 206),
                 "(a) Positive, PAD to DVSS and PAD to DVDD")
    # P+ drains into the N-well and out through its N+ ring.
    for gx, ring in ((15.4, 8.6), (59.6, 66.4)):
        a.flow([(gx, 166), (ring, 166)], key=diode)
    for gx in (24.2, 33.1, 41.9, 50.8):
        a.flow([(gx, 185.5), (gx, 196.6)], key=diode)
        a.flow([(gx, 146.6), (gx, 134.6)], key=diode)
    # Snapback: from each NMOS drain to the sources on both sides of it.
    # Neighbouring drains' arrows are staggered, so no two tips meet.
    for k, drain in enumerate((19.78, 31.5, 43.3, 55.0)):
        mid = 99 if k % 2 == 0 else 111
        for side in (-1, 1):
            # The pair is offset too, so it does not read as one arrow
            # with two heads.
            gy = mid + side * 2.4
            a.flow([(drain + side * 0.4, gy), (drain + side * 5.2, gy)],
                   colour=SNAP, width=3.2, key=snap)
    x, y = a.px(7.3, 65.5)
    a.text(x, y + 5, "NMOS output drivers", anchor="start", weight="bold")
    x, y = a.px(3.4, 146)
    a.text(x, y + 5, "PMOS output drivers", weight="bold")
    top = a.oy - 56
    a.label("output NMOS, the same drains as the NMOS\ndrain diode: snaps "
            "back above 10.7 V\n(Positive, PAD to DVSS), from each drain\n"
            "to the sources beside it, on DVSS", (22.6, 101.4),
            (a.px(0, 97)[0], top - 17), colour=SNAP, weight="bold")
    a.label("PMOS drain: from the P+ drains, on PAD, into\nthe N-well and "
            "out through its N+ guard ring\non DVDD. To DVSS, on through "
            "the rail clamp", (24.2, 189),
            (a.px(0, 170)[0], top), colour=HOT, weight="bold")
    bot = a.oy + a.dh + 30
    a.label("N-well, seen between the\ndrains and its guard ring", (65.2, 150),
            (a.px(0, 132)[0], bot))
    a.label("N+ guard ring,\non DVDD", (67.3, 180), (a.px(0, 166)[0], bot),
            colour=DVDD, weight="bold")
    a.label("outer P+ guard\nring, on DVSS", (72.0, 200), (a.ox + a.dw, bot),
            anchor="end", colour=GREY)

    b = _drivers((0, 64, 75, 125),
                 "(b) Negative, PAD to DVSS and PAD\nto DVDD: "
                 "the NMOS drivers of (a)")
    # From the P+ ring into the N+ drains.
    for gx, ring in ((19.78, 11.0), (55.0, 64.0)):
        b.flow([(ring, 101), (gx, 101)], key=diode)
    for gx in (31.5, 43.3):
        b.flow([(gx, 118.2), (gx, 108.5)], key=diode)
        b.flow([(gx, 72.4), (gx, 81.0)], key=diode)
    top = b.oy - 56
    b.label("NMOS drain: from the P+ guard ring on\nDVSS into the N+ drains, "
            "on PAD. From\nDVDD, first through the rail clamp to DVSS",
            (15.5, 101), (b.px(0, 93)[0], top), colour=HOT, weight="bold")
    bot = b.oy + b.dh + 30
    b.label("P+ guard ring,\non DVSS", (64.3, 80), (b.ox, bot),
            anchor="start", colour=DVSS, weight="bold")
    b.label("outer N+ guard\nring, on DVDD", (70.5, 110),
            (b.px(0, 108)[0], bot), colour=GREY)
    a.attach(b)
    a.note(GREY, "not in the paths diagram")
    a.note(INK, "output NMOS and NMOS drain diode: the same drains",
           kind="plain")
    a.note(INK, "PMOS drains avalanche above 9.7 V (Negative, PAD to DVDD): "
           "second path, not drawn", kind="plain")
    a.note(INK, "rail clamp: in the supply pads, not here", kind="plain")
    return a


def secondary():
    """The secondary protection: four resistors and two pairs of diodes."""
    f = Fig(CELL, (21.5, 264.5, 53.5, 311.5), 14, left=178, top=126,
            right=195, bottom=130)
    lay = gdskit.load(CELL)
    # Grey layers: blue is then the schematic's secondary protection only.
    f.grey_silicon(named=True)
    # The only polysilicon left grey is at the two ends of each resistor.
    f.notes = [(k, c, t + ": the resistors' ends" if "polysilicon" in t else t)
               for k, c, t in f.notes]
    pad, inn = gdskit.net(CELL, "PAD"), gdskit.net(CELL, "IN")
    # Blue is the schematic's three parts; its wires are black, so the
    # metal is too. The parts are drawn over the metal that covers them.
    f.geom(pad["metal2"], "padwire", key=False)
    f.note(("url(#wire)", INK, 1.0), "PAD net, metal 2", kind="tint")
    f.outline(pad["metal2"], INK, width=1.1)
    metal = inn["metal2"].union(inn["metal1"])
    f.geom(metal, "nextwire", key=False)
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
            (31.2, 272.1), (f.ox + 60, top - 34), colour=SECONDARY,
            weight="bold")
    # One outline round the four, for the label's one leader.
    f.box((31.2, 270.3, 43.8, 273.9), colour=SECONDARY, dash="1,0",
          width=2.0)
    f.label("N+ guard ring,\non DVDD", (26.05, 283), (f.px(0, 283)[0], top))
    f.label("also to pull-up,\npull-down resistors", (22.3, 292.9),
            (f.px(0, 292.9)[0], top), colour=GREY)
    f.label("P+ guard ring,\non DVSS", (26.05, 302), (f.px(0, 302)[0], top))
    # The rings that the schematic has no symbol for, in grey.
    y = f.px(28, 0)[1] + 5
    f.label("N+ ring in an N-well,\non DVDD, round the\nresistors",
            (28, 268.0), (f.ox - 12, y - 17), anchor="end", colour=GREY,
            lead="right")
    y = f.px(47, 0)[1] + 5
    # Their targets lie beside the metal, where the ring shows.
    f.label("outer P+ ring, on\nDVSS, round the\ndiode to DVDD",
            (50.9, 279.2), (f.ox - 12, y - 17), anchor="end", colour=GREY,
            lead="right")
    f.label("outer N+ ring in\nan N-well, on DVDD,\nround the diode\n"
            "from DVSS", (50.9, 307.8), (f.ox + f.dw + 12, y - 25),
            anchor="start", colour=GREY, lead="left")
    bot = f.oy + f.dh + 30
    f.label("40 µm² diode to DVDD: 2 P+ strips of\n20 µm × 1 µm in an "
            "N-well held on\nDVDD by the N+ guard ring round them",
            (46.5, 283.2), (f.px(0, 278)[0], bot), colour=SECONDARY,
            weight="bold", also=[(46.5, 287.87)])
    f.label("40 µm² diode from DVSS: 2 N+ strips of\n20 µm × 1 µm in "
            "P-type silicon held on\nDVSS by the P+ guard ring round them",
            (46.5, 304.05), (f.px(0, 304)[0], bot), colour=SECONDARY,
            weight="bold", also=[(46.5, 299.38)])
    f.note(("url(#wire2)", INK, 1.0),
           "protected net, after the 110 Ω: metal 1 and 2, with openings",
           kind="tint")
    f.note((PAPER, "#808080", 1.0), "P-type silicon, no N-well", kind="tint")
    f.note(INK, "the blue strips are drawn over the metal that covers them",
           kind="plain")
    f.note(INK, "contacts and vias: not drawn", kind="plain")
    f.note(GREY, "not in the schematic")
    f.note(INK, RINGS, kind="plain")
    f.note(INK, "primary: nearer the pad, left of this view", kind="plain")
    f.note(INK, "rail clamp and rail diode: in the supply pads",
           kind="plain")
    f.title("gf180mcu_fd_io__bi_t: the secondary protection", up=108)
    return f


FIGURES = {"gds-cell": cell, "gds-pad-net": pad_net, "gds-paths": paths,
           "gds-secondary": secondary}
