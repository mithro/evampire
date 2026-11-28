"""Figures of the bidirectional pad gf180mcu_fd_io__bi_t.

Helper for figures.py: run that script, not this module.

SPDX-License-Identifier: Apache-2.0
"""

from shapely.geometry import box

import gdskit
from layfig import CLAMP, DVDD, DVSS, GREY, HOT, INK, SECONDARY, SNAP, Fig

CELL = "bi_t"
# Blocks of the cell, as (x0, y0, x1, y1) in GDS micrometres, from the
# placement of the foundry's sub-cells.
PREDRIVERS = (2.0, 211.7, 73.3, 242.3)   # comp018green_out_predrv, four
BUFFERS = (3.6, 245.5, 70.4, 264.1)      # out_sigbuf_oe, _a and sigbuf_1
# in_cms_smt and in_drv, with four sigbuf cells and four small diodes.
INPUT = (3.5, 311.6, 71.8, 341.8)
PULLS = (3.8, 266.7, 18.8, 309.5)        # comp018green_in_pupd resistors
# The resistors and the two diode blocks inside comp018green_esd_cdm.
SECOND_PARTS = ((21.7, 266.7, 52.7, 277.5), (21.7, 277.9, 52.7, 293.2),
                (21.7, 293.6, 52.7, 309.9))
RINGS = ("DVDD and DVSS rings: stripes of metal 3 to 5 across the cell, "
         "beyond the bond pad; not drawn")
PADMETAL = (("#9aa5b1", "#6b7684", 0.55), "bond pad")


def cell(alone=True):
    """The whole cell, with the parts of the schematic in its colours.

    `alone` adds a note that the rail clamp is in another cell, for the
    figure that does not show the supply pad under this one.

    The layers are grey, so red, blue and black mean here only what they
    mean in the schematic of schematic.py, and each label is the
    schematic's own. What the schematic leaves out is named in grey.
    """
    f = Fig(CELL, (0, 0, 75, 350), 2.7, top=132, right=75, bottom=284)
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
    f.region(INPUT, INK, opacity=0.12)
    top = f.oy - 46
    f.label("drain diode of\nNMOS drivers:\n304 µm of gate,\non 4 drains",
            (19.78, 97), (f.px(0, 97)[0], top - 34), colour=HOT,
            weight="bold")
    f.label("drain diode of\nPMOS drivers:\n480 µm of gate,\non 6 drains",
            (15.4, 166), (f.px(0, 166)[0], top - 34), colour=HOT,
            weight="bold")
    f.label("pre-\ndrivers", (2.0, 222), (f.px(0, 222)[0], top),
            colour=GREY)
    f.label("output signal\nbuffers", (3.6, 255), (f.px(0, 251)[0], top),
            colour=GREY)
    f.label("pull-up and\npull-down\nresistors", (3.8, 288),
            (f.px(0, 291)[0], top - 17), colour=GREY)
    f.label("input buffer\nand logic", (3.5, 327), (f.px(0, 327)[0], top),
            weight="bold")
    bot = f.oy + f.dh + 30
    # Each leader drops straight out of the cell before it turns.
    for text, gy, at, drop in (
            ("110 Ω: 4 of\n440 Ω in parallel", 272.1, 228, 0),
            ("40 µm² diode to\nDVDD: 2 strips of\n20 µm × 1 µm", 285.5, 286,
             0),
            ("40 µm² diode from\nDVSS: 2 strips of\n20 µm × 1 µm", 301.7, 338,
             70)):
        f.label(text, (52.7, gy), (f.px(0, at)[0], bot + drop),
                colour=SECONDARY, weight="bold", elbow=f.px(76.5, gy))
    f.note((SECONDARY, SECONDARY, 0.3), "secondary", kind="tint")
    f.note((INK, INK, 0.12), "input buffer and logic", kind="tint")
    f.note(*PADMETAL, kind="tint")
    f.note(GREY, "not in the schematic")
    f.note(INK, RINGS, kind="plain")
    f.note(INK, "metal of the PAD net beyond the bond pad: not drawn",
           kind="plain")
    f.title("gf180mcu_fd_io__bi_t, the bidirectional pad", up=114)
    if alone:
        # In the schematic's orange, where the reader looks for those parts.
        f.text(f.ox + f.dw, f.oy - 114, "rail clamp and its diode: not in "
               "this cell, only in the supply pads", anchor="end",
               fill=CLAMP, weight="bold", halo=False)
    f.dim((75, 0), (75, 350), "350 µm", offset=172, side="below")
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
    for region in (PREDRIVERS, BUFFERS, (*PULLS[:3], 278), SECOND_PARTS[0]):
        f.box(region, colour=GREY, dash="5,4", width=1.4)
    # The metal beyond the bond pad, as the layout has it: ruled, with
    # every edge outlined, so each gap in it is an outlined, unruled shape.
    # The bond pad itself is a plain tint: its metal has fine slots that
    # a ruling would not show truly.
    lay = gdskit.load(CELL)
    f.geom(lay["metal5"].intersection(box(0, 0, 75, 66)), "metal",
           opacity=0.55, key=False)
    f.note(*PADMETAL, kind="tint")
    metal = net["metal2"].intersection(box(0, 65.2, 75, 278))
    f.geom(metal, "padwire", width=0, key=False)
    f.outline(metal, INK, width=1.1)
    f.note(("url(#wire)", INK, 1.0), "PAD net, metal 2 beyond the bond pad: "
           "ruled; an unruled shape inside it is a gap", kind="tint")
    f.layer("pad", width=1.6, dash="5,3", key=False)
    x, y = f.px(37.5, 32)
    f.text(x, y - 18, "PAD", weight="bold", size=18)
    f.text(x, y + 2, "bond pad, 60 µm opening:")
    f.text(x, y + 19, "metal 2 to 5, stacked")
    top = f.oy - 68
    f.label("drain diode of NMOS\ndrivers: 304 µm of gate,\n4 drains, "
            "each between\n2 gates of 38 µm", (19.78, 95),
            (f.px(0, 95)[0], top), colour=HOT, weight="bold")
    f.label("drain diode of PMOS\ndrivers: 480 µm of gate,\n6 drains, "
            "each between\n2 gates of 40 µm", (15.4, 166),
            (f.px(0, 166)[0], top), colour=HOT, weight="bold")
    f.label("metal 2 wire,\n2 µm wide, on\nto the secondary\nprotection",
            (37.5, 209.4), (f.px(0, 218.5)[0], top), weight="bold")
    f.label("pull-up and\npull-down\nresistors", (3.8, 272.1),
            (f.ox + f.dw, top + 17), anchor="end", colour=GREY,
            elbow=(f.px(0, 272.1)[0], f.oy - 12))
    bot = f.oy + f.dh + 30
    # Inside the gap over the source between the last two NMOS drains.
    f.label("gap in the metal 2 over a\nsource: one of ten, five in\n"
            "each driver", (49.1, 104), (f.px(0, 88)[0], bot), colour=GREY)
    # A point well inside the metal between the two drivers.
    join = metal.intersection(box(63, 118, 70, 124)).representative_point()
    f.label("metal 2 joining PAD to the\ndrains of both drivers",
            (join.x, join.y), (f.px(0, 152)[0], bot), weight="bold")
    f.label("pre-drivers", (73.3, 222), (f.px(0, 222)[0], bot), colour=GREY)
    f.label("output signal\nbuffers", (70.4, 250), (f.px(0, 250)[0], bot),
            colour=GREY)
    f.label("110 Ω of the secondary\nprotection", (52.7, 272.1),
            (f.px(0, 254)[0], bot + 46), colour=GREY,
            elbow=(f.px(0, 272.1)[0], f.oy + f.dh + 8))
    f.note(GREY, "not in the schematic's primary protection")
    f.note(INK, "NMOS drains: diodes from the P-type silicon, on DVSS "
           "through the P+ ring round them", kind="plain")
    f.note(INK, "PMOS drains: diodes to the N-well, on DVDD through the N+ "
           "ring round them", kind="plain")
    f.note(INK, RINGS, kind="plain")
    f.note(INK, "40 µm² diodes, input buffer: further right", kind="plain")
    f.note(INK, "rail clamp and its diode: in the supply pads", kind="plain")
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
    for drain in (19.78, 31.5, 43.3, 55.0):
        for side in (-1, 1):
            # The two arrows of a drain are offset along it, so that they
            # do not read as one arrow with two heads, and no two tips
            # meet on a shared source.
            gy = 96 + side * 2.6
            a.flow([(drain + side * 0.4, gy), (drain + side * 5.2, gy)],
                   colour=SNAP, width=3.2, key=snap)
    x, y = a.px(7.3, 65.5)
    a.text(x, y + 5, "NMOS output drivers", anchor="start", weight="bold")
    x, y = a.px(72.2, 66)
    a.text(x, y + 5, "rings round the NMOS: named in (b)", anchor="start",
           fill=GREY)
    x, y = a.px(3.4, 146)
    a.text(x, y + 5, "PMOS output drivers", weight="bold")
    top = a.oy - 56
    a.label("output NMOS, the same drains as the NMOS\ndrain diode: snaps "
            "back above 10.7 V\n(Positive, PAD to DVSS), from each drain\n"
            "to the sources beside it, on DVSS", (22.6, 98.6),
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
    a.note(INK, "PMOS drains of (a) avalanche above 9.7 V (Negative, PAD to "
           "DVDD): second path, not drawn", kind="plain")
    a.note(INK, "rail clamp: in the supply pads, not here", kind="plain")
    a.note(INK, "bond pad and metal: not drawn", kind="plain")
    return a


def secondary():
    """The secondary protection: four resistors and two diodes."""
    f = Fig(CELL, (21.5, 264.5, 53.5, 311.5), 14, left=178, top=126,
            right=195, bottom=130)
    # The cross-section's colours: wells and diffusions then differ by
    # hue, also under the ruled metal. The schematic's three parts have a
    # blue outline.
    f.silicon()
    f.layer("sab", width=1.0)
    pad, inn = gdskit.net(CELL, "PAD"), gdskit.net(CELL, "IN")
    f.geom(pad["metal2"], "padwire", width=0, key=False)
    f.outline(pad["metal2"], INK, width=1.1)
    f.note(("url(#wire)", INK, 1.0), "PAD net, metal 2", kind="tint")
    metal = inn["metal2"].union(inn["metal1"])
    f.geom(metal, "nextwire", width=0, key=False)
    f.outline(metal, INK, width=0.8)
    f.box((31.2, 270.3, 43.8, 273.9), colour=SECONDARY, dash="1,0",
          width=2.6)
    f.outline(inn["comp"].buffer(0.3), SECONDARY, width=2.6)
    f.note(SECONDARY, "secondary: the four resistors, the four diode strips",
           kind="outline")
    y = f.px(37.5, 0)[1] + 5
    f.label("PAD, on a metal 2\nwire from the\ndrivers", (37.5, 265.4),
            (f.ox - 12, y - 17), anchor="end", weight="bold", lead="right")
    f.label("to the input\nbuffer",
            (37.2, 310.8), (f.ox + f.dw + 12, y - 8), anchor="start",
            weight="bold", lead="left")
    top = f.oy - 40
    f.label("110 Ω: 4 of 440 Ω in parallel,\npolysilicon, each 2.5 µm wide\n"
            "and 2.8 µm long, left to right,\nunder the silicide block",
            (31.2, 272.1), (f.ox + 44, top - 34), colour=SECONDARY,
            weight="bold")
    f.label("N+ guard ring,\non DVDD: the diode's\nDVDD end", (26.05, 283),
            (f.px(0, 282.6)[0], top - 17))
    f.label("also to\npull-up, pull-down\nresistors", (22.3, 292.9),
            (f.px(0, 292.9)[0], top - 17), colour=GREY)
    f.label("P+ guard ring,\non DVSS: the diode's\nDVSS end", (26.05, 302),
            (f.px(0, 303)[0], top - 17))
    # The rings that the schematic has no symbol for, in grey. Their
    # targets lie beside the metal, where the ring shows.
    y = f.px(28, 0)[1] + 5
    f.label("N+ ring in an N-well,\non DVDD, round the\nresistors",
            (28, 268.0), (f.ox - 12, y - 17), anchor="end", colour=GREY,
            lead="right")
    y = f.px(51, 0)[1] + 5
    f.label("outer P+ ring, on\nDVSS, round the\ndiode to DVDD",
            (50.9, 279.2), (f.ox - 12, y - 17), anchor="end", colour=GREY,
            lead="right", elbow=(f.px(50.9, 266.5)))
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
    f.note(("url(#wire2)", INK, 1.0), "protected net, after the 110 Ω: "
           "metal 1 and 2; an unruled shape inside it is an opening",
           kind="tint")
    f.note(INK, "the four strips are the only diffusion on the protected "
           "net; contacts and vias are not drawn", kind="plain")
    f.note(GREY, "not in the schematic")
    f.note(INK, RINGS, kind="plain")
    f.note(INK, "primary: nearer the pad, left of this view", kind="plain")
    f.note(INK, "rail clamp and its diode: in the supply pads", kind="plain")
    f.title("gf180mcu_fd_io__bi_t: the secondary protection", up=108)
    return f


FIGURES = {"gds-cell": cell, "gds-pad-net": pad_net, "gds-paths": paths,
           "gds-secondary": secondary}
