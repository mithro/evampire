"""Figures of the rail clamp in the supply pads gf180mcu_fd_io__dvdd/dvss.

Helper for figures.py: run that script, not this module.

SPDX-License-Identifier: Apache-2.0
"""

from shapely.affinity import translate
from shapely.geometry import box

import figs_pad
import gdskit
from layfig import CLAMP, DVDD, DVSS, GREY, HOT, INK, SUB, Fig

CELL = "dvdd"
PITCH = 75.0   # width of a pad cell: the next cell along the ring
INVERTERS = (15.8, 195.4, 59.6, 214.6)
FET = (9.0, 71.0, 66.0, 193.0)        # the clamp transistor's four blocks
CAPS = (11.0, 216.5, 65.0, 276.0)     # eight timer capacitors
RES = (3.5, 277.5, 72.0, 298.0)       # twelve timer resistors
DIODES = (12.3, 299.8, 62.7, 325.6)   # four diode strips, DVSS to DVDD
DVDD_EDGE, DVSS_EDGE, PAD_EDGE = "#a02c7d", "#0d5045", "#7d1f14"


def clamp():
    """The whole DVDD pad, with the schematic's rail clamp in its orange.

    As in figs_pad.cell: grey layers, the schematic's own labels, and what
    the schematic leaves out named in grey.
    """
    f = Fig(CELL, (0, 0, 75, 350), 2.7, top=106, right=75, bottom=184)
    lay = gdskit.load(CELL)
    f.grey_silicon()
    f.geom(lay["metal5"].intersection(box(0, 0, 75, 66)), "metal",
           opacity=0.55, key=False)
    f.layer("pad", width=1.6, dash="5,3", key=False)
    x, y = f.px(37.5, 32)
    # Grey: the schematic has the DVDD ring, but no symbol for its pad.
    f.text(x, y - 6, "DVDD", size=18, fill=GREY)
    f.text(x, y + 14, "bond pad", fill=GREY)
    for region in (FET, INVERTERS, CAPS, RES, DIODES):
        f.region(region, CLAMP)
    top = f.oy - 34
    f.label("clamp NMOS: 4000 µm of\ngate, 80 gates of 50 µm,\n"
            "in 4 blocks", (9.0, 131), (f.px(0, 131)[0], top - 17),
            colour=CLAMP, weight="bold")
    f.label("three\ninverters", (15.8, 205), (f.px(0, 203)[0], top),
            colour=CLAMP, weight="bold")
    f.label("MOS capacitor:\n8 of 10 µm ×\n25 µm", (11.0, 246),
            (f.px(0, 246)[0], top - 17), colour=CLAMP, weight="bold")
    f.label("360 kΩ:\n12 of 30 kΩ\nin series", (3.5, 288),
            (f.px(0, 292)[0], top - 17), colour=CLAMP, weight="bold")
    bot = f.oy + f.dh + 30
    f.label("160 µm² diode\nfrom DVSS to DVDD:\n4 of 40 µm²", (62.7, 306),
            (f.px(0, 300)[0], bot), colour=CLAMP, weight="bold")
    f.label("4 supply\ncapacitors", (64, 337.8), (f.px(0, 347)[0], bot),
            colour=GREY)
    f.note((CLAMP, CLAMP, 0.3), "rail clamp and rail diode", kind="tint")
    f.note(GREY, "not in the schematic")
    f.note(*figs_pad.PADMETAL, kind="tint")
    f.note(INK, "each supply pad holds one such clamp and diode; the DVSS "
           "pad's are the same", kind="plain")
    f.note(INK, figs_pad.RINGS, kind="plain")
    f.title("gf180mcu_fd_io__dvdd, the DVDD supply pad", up=88)
    f.dim((75, 0), (75, 350), "350 µm", offset=92, side="below")
    f.dim((0, 350), (75, 350), "75 µm", offset=14, side="below")
    return f


def cells():
    """Both cells of the schematic: the bidirectional pad over a supply pad."""
    f = figs_pad.cell(alone=False)
    f.stack(clamp())
    return f


def clamp_fingers():
    """A corner of the clamp transistor: no silicide block anywhere."""
    f = Fig(CELL, (8.6, 72.6, 21.4, 94.4), 40, top=64, right=20, bottom=128)
    lay = gdskit.load(CELL)
    nets = {n: gdskit.net(CELL, n)["comp"] for n in ("DVDD", "DVSS")}
    f.geom(nets["DVDD"], "dvdd", opacity=0.7)
    f.geom(nets["DVSS"], "dvss", opacity=0.7)
    f.layer("poly")
    f.geom(lay["poly"].intersection(lay["comp"]), "gate")
    f.note(DVDD, "on DVDD")
    f.note(DVSS, "on DVSS")
    f.layer("contact")
    top = f.oy - 30
    f.label("P+ guard ring, on DVSS", (9.3, 76.5), (f.px(0, 76.5)[0], top),
            colour=DVSS, weight="bold")
    f.label("Polysilicon bar joining the gates of a block (16 of its 20 "
            "fingers shown)", (11.8, 80.5), (f.px(0, 86)[0], top))
    # The 0.52 µm strips repeat every 1.22 µm: drain, gate, source, gate.
    first, pitch = 74.88, 1.22
    bot = f.oy + f.dh + 30

    def under(text, k, gx=20.6, **kw):
        gy = first + k * pitch
        f.label(text, (gx, gy), (f.px(0, gy)[0], bot), **kw)

    under("N+ drain,\non DVDD", 2, colour=DVDD, weight="bold")
    under("N+ source,\non DVSS", 5, colour=DVSS, weight="bold")
    under("Gate", 7.5)
    gap = first + 12 * pitch + 0.185   # between a contact and the gate
    # (0.11 µm contact half-width plus half of the 0.15 µm gap)
    f.label("Contacts 0.15 µm from each gate:\nno silicide block",
            (20.9, gap), (f.px(0, gap)[0], bot), weight="bold")
    # Dimensions in the bare strip above the fingers, with extension
    # lines down to the two edges each one measures.
    for k, size, text in ((9.5, 0.7, "gate length: 0.7 µm"),
                          (14, 0.52, "drain strip: 0.52 µm")):
        lo = first + k * pitch - size / 2
        for gy in (lo, lo + size):
            f.line((10.75, gy), (13.6, gy))
        f.dim((10.95, lo), (10.95, lo + size), text)
    return f


def _stack(cell, name):
    """A supply net's metal 3 to 5, with the slots in the metal closed."""
    net = gdskit.net(cell, name)
    metal = net["metal3"].union(net["metal4"]).union(net["metal5"])
    return metal.buffer(1.5).buffer(-1.5)


def ring():
    """A positive pulse from PAD to DVSS, across two cells of the ring."""
    f = Fig("bi_t", (0, 0, 2 * PITCH, 222), 3.7, left=20, top=104, right=215,
            bottom=180)
    f.wells = False   # no silicon is drawn, so the ground is plain
    f.body[0] = f.body[0].replace(SUB, "#ffffff")
    lay = gdskit.load("dvss")
    fet = lay["comp"].intersection(lay["nplus"]).intersection(
        box(10, 72, 65, 192))
    for cell, shift in (("bi_t", 0.0), ("dvss", PITCH)):
        for name, style in (("DVDD", "dvddrail"), ("DVSS", "dvssrail")):
            f.geom(translate(_stack(cell, name), xoff=shift), style)
    # Metal 2 lies under the stripes, so it is drawn as an edge with a
    # light tint inside: the tint shows which side is metal and hides no
    # stripe. The DVSS bond pad's metal 2 runs on as six buses over the
    # clamp transistor, whose sources connect to it.
    tint = 0.12
    link = gdskit.net("dvss", "DVSS")["metal2"].intersection(
        box(0, 60, 75, 200)).buffer(0.6).buffer(-0.6)
    f.outline(translate(link, xoff=PITCH), DVSS_EDGE, width=1.6, tint=tint)
    f.note((DVSS_EDGE, DVSS_EDGE, tint),
           "DVSS pad's metal 2, under the stripes", kind="tint")
    # Five metal 2 strips join the clamp's drains to the DVDD stripes.
    feed = gdskit.net("dvss", "DVDD")["metal2"].intersection(
        box(0, 60, 75, 200))
    f.outline(translate(feed, xoff=PITCH), DVDD_EDGE, width=1.6, tint=0.45)
    f.note((DVDD_EDGE, DVDD_EDGE, 0.45),
           "DVDD metal 2: 5 strips, under the stripes", kind="tint")
    pad = gdskit.net("bi_t", "PAD")
    f.geom(pad["metal5"].buffer(1.5).buffer(-1.5), "padtop", opacity=0.6)
    bus = pad["metal2"].intersection(box(0, 60, 75, 201)).buffer(
        1.5).buffer(-1.5)
    f.outline(bus, PAD_EDGE, width=1.6, tint=tint)
    f.note((PAD_EDGE, PAD_EDGE, tint),
           "PAD net's metal 2, under the stripes", kind="tint")
    # The NMOS drains carry none of this current, so they are grey.
    f.geom(pad["comp"].intersection(box(0, 120, 75, 222)), "paddrain")
    # Drawn over the metal, so that they show through its tint.
    f.outline(pad["comp"].intersection(box(0, 0, 75, 120)), "#555555",
              width=1.2, tint=0.3)
    f.note(("#555555", "#555555", 0.3), "drain of the output NMOS, on the "
           "PAD net: no current on the main path", kind="tint")
    f.outline(translate(fet.buffer(0.3).buffer(-0.3), xoff=PITCH), CLAMP,
              width=3.0)
    f.note(CLAMP, "rail clamp's NMOS, under the metal", kind="outline")
    f.note(INK, "the second path, the output NMOS's snapback: not drawn",
           kind="plain")
    f.note(INK, "the other three discharges of the paths diagram: not drawn",
           kind="plain")
    f.note(INK, "metal 2 is tinted, so colours blend where it lies under "
           "a stripe", kind="plain")
    f.note(INK, "rounded gaps over the NMOS drains: slots in the PAD net's "
           "metal 2", kind="plain")
    f.title("Positive, PAD to DVSS: the main path, across two cells", up=84)
    x0, y0 = f.px(PITCH, 0)
    x1, _ = f.px(PITCH, 222)
    f.over.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" '
                  f'y2="{y0:.1f}" stroke="{INK}" stroke-width="1.4"/>')
    for gx, name, kind in ((37.5, "PAD", "bidirectional pad cell"),
                           (PITCH + 37.5, "DVSS", "DVSS supply pad cell")):
        x, y = f.px(gx, 32)
        f.text(x, y - 4, f"{name} bond pad", weight="bold")
        f.text(x, y + 14, kind)
    x, y = f.px(66.5, 95)
    f.label("drains of the output NMOS", (55.0, 95), (x, y + 5))
    x, y = f.px(69.5, 166)
    f.text(x, y + 5, "PMOS drains")
    x, y = f.px(PITCH, 0)
    f.text(x + 6, y - 6, "boundary between the two cells", anchor="start")
    # The current: along the pad's metal, down the DVDD rail, along a
    # DVDD metal 2 strip, across each block of the clamp transistor, and
    # back along the DVSS metal 2 beside the strip. The strip's own run
    # has no head: the current leaves it at each block.
    y_rail, strip, bus = 181.5, PITCH + 37.5, PITCH + 44.3
    route = [(43.3, 56), (43.3, y_rail), (strip, y_rail), (strip, 86)]
    f.flow(route, width=5.0, head=False)
    for gy in (176, 146, 116, 86):
        f.flow([(strip - 0.7, gy), (bus - 0.3, gy)], width=4.2)
    f.flow([(bus, 176), (bus, 56)], width=5.0)
    # A head part-way along the first two runs; the last has the end's.
    for (ax, ay), (bx, by) in list(zip(route, route[1:]))[:2]:
        f.flow([(ax, ay), (ax + 0.62 * (bx - ax), ay + 0.62 * (by - ay))],
               width=5.0)
    top = f.oy - 38
    f.label("1  PAD +: along metal 2, over the\nNMOS drains, to the "
            "PMOS drains", (43.3, 122), (f.px(0, 84)[0], top), colour=HOT,
            leader=INK, weight="bold")
    f.label("2  PMOS drain: P+ drain to N-well, out through\nits N+ "
            "guard ring to the DVDD stripes, metal 3 to 5",
            (43.3, y_rail), (f.px(0, 190)[0], top), colour=HOT, leader=INK,
            weight="bold")
    bot = f.oy + f.dh + 30
    f.label("5  DVSS metal 2 over the rail\nclamp, back to the DVSS bond pad",
            (bus, 66), (f.px(0, 40)[0], bot + 46), colour=HOT, leader=INK,
            weight="bold")
    f.label("4  Rail clamp: along the five DVDD metal 2 strips (the "
            "current is drawn on\none), then across the NMOS of each orange "
            "block to the DVSS metal 2", (strip, 131),
            (f.px(0, 150)[0], bot), colour=HOT, leader=INK, weight="bold")
    x, y = f.px(PITCH + 5, y_rail)
    f.label("3  Along the DVDD stripes\ninto the DVSS supply\npad cell",
            (PITCH + 5, y_rail), (f.ox + f.dw + 14, y), anchor="start",
            colour=HOT, leader=INK, weight="bold", lead="left")
    return f


FIGURES = {"gds-clamp": clamp, "gds-cells": cells,
           "gds-clamp-fingers": clamp_fingers,
           "gds-ring": ring}
