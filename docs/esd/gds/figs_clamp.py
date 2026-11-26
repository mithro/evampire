"""Figures of the rail clamp in the supply pads gf180mcu_fd_io__dvdd/dvss.

Helper for figures.py: run that script, not this module.

SPDX-License-Identifier: Apache-2.0
"""

from shapely.affinity import translate
from shapely.geometry import box

import gdskit
from layfig import CLAMP, DVDD, DVSS, HOT, INK, Fig

CELL = "dvdd"
PITCH = 75.0   # width of a pad cell: the next cell along the ring
INVERTERS = (15.8, 195.4, 59.6, 214.6)


def clamp():
    """The whole DVDD pad: the rail clamp and its timer."""
    f = Fig(CELL, (0, 0, 75, 350), 2.7, top=62, right=75, bottom=184)
    lay = gdskit.load(CELL)
    f.silicon()
    f.geom(lay["metal5"].intersection(box(0, 0, 75, 66)), "metal",
           opacity=0.55)
    f.layer("pad", width=1.6, dash="5,3")
    x, y = f.px(37.5, 32)
    f.text(x, y - 4, "Bond pad", weight="bold")
    f.text(x, y + 14, "DVDD")
    f.box(INVERTERS, colour=CLAMP, dash="5,4", width=2.0)
    f.note(CLAMP, "the inverters", kind="box")
    top = f.oy - 34
    f.label("Clamp transistor: 4 blocks of 20\nfingers, each finger 50 µm wide",
            (37.5, 116), (f.px(0, 131)[0], top), colour=CLAMP, weight="bold")
    f.label("Timer capacitors:\n8 of 10 µm × 25 µm", (19, 231),
            (f.px(0, 226)[0], top), colour=CLAMP, weight="bold")
    f.label("Timer resistors:\n12 of 30 kΩ", (37.5, 287.8),
            (f.px(0, 288)[0], top), colour=CLAMP, weight="bold")
    f.label("4 supply\ncapacitors", (10, 337.8), (f.ox + f.dw, top),
            anchor="end")
    bot = f.oy + f.dh + 30
    f.label("Guard rings round the\nclamp transistor", (67.6, 110),
            (f.px(0, 122)[0], bot), also=[(65.4, 134)])
    f.label("3 inverters", (59.6, 205), (f.px(0, 205)[0], bot), colour=CLAMP,
            weight="bold")
    f.label("P+ ties to\nthe substrate", (67, 250), (f.px(0, 250)[0], bot))
    f.label("4 diodes from\nDVSS to DVDD", (56, 305.7),
            (f.px(0, 305.7)[0], bot))
    f.note(CLAMP, "part of the rail clamp")
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
            (11.8, 86), (f.px(0, 86)[0], top))
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
    # Dimension ticks on the fingers, named in the bare strip above them.
    band = f.px(10.55, 0)[1] + 5
    g0 = first + 8.5 * pitch - 0.35
    f.dim((13.2, g0), (13.2, g0 + 0.7), "")
    f.label("gate length: 0.7 µm", (13.2, g0 + 0.35),
            (f.px(0, g0)[0] - 70, band), weight="bold")
    d0 = first + 12 * pitch - 0.26
    f.dim((13.2, d0), (13.2, d0 + 0.52), "")
    f.label("drain strip: 0.52 µm", (13.2, d0 + 0.26),
            (f.px(0, d0)[0] + 10, band), weight="bold")
    return f


def _stack(cell, name):
    """A supply net's metal 3 to 5, with the slots in the metal closed."""
    net = gdskit.net(cell, name)
    metal = net["metal3"].union(net["metal4"]).union(net["metal5"])
    return metal.buffer(1.5).buffer(-1.5)


def ring():
    """A positive pulse from PAD to DVSS, across two cells of the ring."""
    f = Fig("bi_t", (0, 0, 2 * PITCH, 222), 3.7, left=20, top=70, right=190,
            bottom=136)
    f.wells = False
    lay = gdskit.load("dvss")
    fet = lay["comp"].intersection(lay["nplus"]).intersection(
        box(10, 72, 65, 192))
    for cell, shift in (("bi_t", 0.0), ("dvss", PITCH)):
        for name, style in (("DVDD", "dvddrail"), ("DVSS", "dvssrail")):
            f.geom(translate(_stack(cell, name), xoff=shift), style)
    # The DVSS bond pad's metal 2 runs on as six buses over the clamp
    # transistor, whose sources connect to it.
    link = gdskit.net("dvss", "DVSS")["metal2"].intersection(
        box(0, 60, 75, 200)).buffer(0.6).buffer(-0.6)
    f.geom(translate(link, xoff=PITCH), "dvsslink")
    f.geom(translate(fet, xoff=PITCH), "clampfet", opacity=0.45, key=False)
    f.note(CLAMP, "clamp transistor, under the metal", kind="outline")
    pad = gdskit.net("bi_t", "PAD")
    top_metal = pad["metal5"].union(pad["metal2"].intersection(
        box(0, 0, 75, 201))).buffer(1.5).buffer(-1.5)
    f.geom(top_metal, "padtop", opacity=0.7)
    f.geom(pad["comp"], "paddrain")
    f.outline(translate(fet.buffer(0.3).buffer(-0.3), xoff=PITCH), CLAMP,
              width=3.0)
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
    f.flow([(42.5, 64), (42.5, y_rail), (bus, y_rail), (bus, 56)],
           width=5.0)
    top = f.oy - 38
    f.label("1  Positive pulse: from the bond pad\nalong metal 2 to the "
            "PMOS drains", (42.5, 100), (f.px(0, 84)[0], top), colour=HOT,
            weight="bold")
    f.label("2  PMOS drain diode: P+ drain to N-well,\nthen up to the DVDD "
            "stripes over it", (42.5, y_rail), (f.px(0, 190)[0], top),
            colour=HOT, weight="bold")
    bot = f.oy + f.dh + 30
    f.label("5  Metal 2 buses over the clamp,\nback to the DVSS bond pad",
            (bus, 100), (f.px(0, 56)[0], bot), colour=HOT, weight="bold")
    f.label("4  Clamp transistor, 4 blocks in parallel: from the\nDVDD "
            "stripes to metal 2 of the DVSS pad", (bus, y_rail),
            (f.px(0, 158)[0], bot), colour=HOT, weight="bold")
    x, y = f.px(PITCH + 5, y_rail)
    f.label("3  DVDD rail into\nthe next cell", (PITCH + 5, y_rail),
            (f.ox + f.dw + 14, y), anchor="start", colour=HOT, weight="bold",
            lead="left")
    return f


FIGURES = {"gds-clamp": clamp, "gds-clamp-fingers": clamp_fingers,
           "gds-ring": ring}
