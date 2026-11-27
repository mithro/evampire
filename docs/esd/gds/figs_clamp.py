"""Figures of the rail clamp in the supply pads gf180mcu_fd_io__dvdd/dvss.

Helper for figures.py: run that script, not this module.

SPDX-License-Identifier: Apache-2.0
"""

from shapely.affinity import translate
from shapely.geometry import box

import gdskit
from layfig import CLAMP, DVDD, DVSS, GREY, HOT, INK, Fig

CELL = "dvdd"
PITCH = 75.0   # width of a pad cell: the next cell along the ring
INVERTERS = (15.8, 195.4, 59.6, 214.6)


FET = (9.0, 71.0, 66.0, 193.0)        # the clamp transistor's four blocks
CAPS = (11.0, 216.5, 65.0, 276.0)     # eight timer capacitors
RES = (3.5, 277.5, 72.0, 298.0)       # twelve timer resistors


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
    f.text(x, y - 6, "DVDD", weight="bold", size=18)
    f.text(x, y + 14, "bond pad")
    for region in (FET, INVERTERS, CAPS, RES):
        f.region(region, CLAMP)
    top = f.oy - 34
    f.label("clamp NMOS 4000 µm:\n4 blocks of 20 fingers,\n"
            "each 50 µm wide", (9.0, 131), (f.px(0, 131)[0], top - 17),
            colour=CLAMP, weight="bold")
    f.label("three\ninverters", (15.8, 205), (f.px(0, 203)[0], top),
            colour=CLAMP, weight="bold")
    f.label("MOS capacitor:\n8 of 10 µm ×\n25 µm", (11.0, 246),
            (f.px(0, 246)[0], top - 17), colour=CLAMP, weight="bold")
    f.label("360 kΩ:\n12 of 30 kΩ\nin series", (3.5, 288),
            (f.px(0, 292)[0], top - 17), colour=CLAMP, weight="bold")
    bot = f.oy + f.dh + 30
    f.label("4 diodes from\nDVSS to DVDD", (56, 305.7),
            (f.px(0, 300)[0], bot), colour=GREY)
    f.label("4 supply\ncapacitors", (64, 337.8), (f.px(0, 337.8)[0], bot),
            colour=GREY)
    f.note((CLAMP, CLAMP, 0.3), "rail clamp", kind="tint")
    f.note(GREY, "not in the schematic")
    f.note(INK, "the DVSS pad holds the same rail clamp", kind="plain")
    f.note(INK, "DVDD and DVSS rings: metal over the cell, not drawn",
           kind="plain")
    f.title("gf180mcu_fd_io__dvdd, the DVDD supply pad", up=88)
    f.dim((75, 0), (75, 350), "350 µm", offset=92, side="below")
    f.dim((0, 350), (75, 350), "75 µm", offset=14, side="below")
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
    f.layer("sab", width=1.0)   # draws nothing: no silicide block here
    f.note(DVDD, "on DVDD")
    f.note(DVSS, "on DVSS")
    f.layer("contact")
    top = f.oy - 30
    f.label("P+ guard ring, on DVSS", (9.3, 76.5), (f.px(0, 76.5)[0], top),
            colour=DVSS, weight="bold")
    f.label("Polysilicon bar joining the gates of a block (16 of its 20 fingers shown)",
            (11.8, 80.5), (f.px(0, 86)[0], top))
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
            bottom=136)
    f.wells = False
    lay = gdskit.load("dvss")
    fet = lay["comp"].intersection(lay["nplus"]).intersection(
        box(10, 72, 65, 192))
    for cell, shift in (("bi_t", 0.0), ("dvss", PITCH)):
        for name, style in (("DVDD", "dvddrail"), ("DVSS", "dvssrail")):
            f.geom(translate(_stack(cell, name), xoff=shift), style)
    # Metal 2 lies under the stripes, so it is drawn in outline: no fill
    # then hides the stripe that the current runs along. The DVSS bond
    # pad's metal 2 runs on as six buses over the clamp transistor, whose
    # sources connect to it.
    link = gdskit.net("dvss", "DVSS")["metal2"].intersection(
        box(0, 60, 75, 200)).buffer(0.6).buffer(-0.6)
    f.outline(translate(link, xoff=PITCH), "#0d5045", width=1.6)
    f.note("#0d5045", "DVSS pad's metal 2, under the stripes", kind="outline")
    pad = gdskit.net("bi_t", "PAD")
    f.geom(pad["metal5"].buffer(1.5).buffer(-1.5), "padtop", opacity=0.6)
    bus = pad["metal2"].intersection(box(0, 60, 75, 201)).buffer(
        1.5).buffer(-1.5)
    f.outline(bus, "#7d1f14", width=1.6)
    f.note("#7d1f14", "PAD net's metal 2, under the stripes", kind="outline")
    f.geom(pad["comp"], "paddrain")
    f.outline(translate(fet.buffer(0.3).buffer(-0.3), xoff=PITCH), CLAMP,
              width=3.0)
    f.note(CLAMP, "rail clamp's NMOS, under the metal", kind="outline")
    f.note(INK, "the output NMOS's snapback path is not drawn", kind="plain")
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
    f.text(x, y + 5, "NMOS drains")
    x, y = f.px(69.5, 166)
    f.text(x, y + 5, "PMOS drains")
    x, y = f.px(PITCH, 0)
    f.text(x + 6, y - 6, "Cell boundary", anchor="start")
    # The current: along the pad's metal, down the DVDD rail, through the
    # clamp transistor, and back along a metal 2 bus of the DVSS pad.
    y_rail, bus = 181.5, PITCH + 44.3
    route = [(43.3, 64), (43.3, y_rail), (bus, y_rail), (bus, 56)]
    f.flow(route, width=5.0)
    # A head part-way along the first two runs; the last has the end's.
    for (ax, ay), (bx, by) in list(zip(route, route[1:]))[:2]:
        f.flow([(ax, ay), (ax + 0.62 * (bx - ax), ay + 0.62 * (by - ay))],
               width=5.0)
    top = f.oy - 38
    f.label("1  PAD +: along metal 2, over the\nNMOS drains, to the "
            "PMOS drains", (43.3, 122), (f.px(0, 84)[0], top), colour=HOT,
            leader=INK, weight="bold")
    f.label("2  PMOS drain: P+ drain to N-well,\nthen to the DVDD "
            "stripes, metal 3 to 5", (43.3, y_rail), (f.px(0, 190)[0], top),
            colour=HOT, leader=INK, weight="bold")
    bot = f.oy + f.dh + 30
    f.label("5  Metal 2 buses over the rail\nclamp, back to the DVSS bond pad",
            (bus, 66), (f.px(0, 40)[0], bot), colour=HOT, leader=INK,
            weight="bold")
    f.label("4  Rail clamp: all 4 blocks of its NMOS conduct,\nfrom the "
            "DVDD stripes to the metal 2 buses", (bus + 7, 177),
            (f.px(0, 150)[0], bot), colour=HOT, leader=INK, weight="bold",
            also=[(bus + 7, 146), (bus + 7, 116), (bus + 7, 86)])
    x, y = f.px(PITCH + 5, y_rail)
    f.label("3  Along the DVDD rail\ninto the DVSS supply\npad cell", (PITCH + 5, y_rail),
            (f.ox + f.dw + 14, y), anchor="start", colour=HOT, leader=INK, weight="bold",
            lead="left")
    return f


FIGURES = {"gds-clamp": clamp, "gds-clamp-fingers": clamp_fingers,
           "gds-ring": ring}
