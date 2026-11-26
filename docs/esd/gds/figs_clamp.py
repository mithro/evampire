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
INVERTERS = (16.8, 196.6, 58.6, 213.4)


def clamp():
    """The whole DVDD pad: the rail clamp and its timer."""
    f = Fig(CELL, (0, 0, 75, 350), 2.7, top=62, right=20, bottom=132)
    lay = gdskit.load(CELL)
    f.silicon()
    f.geom(lay["metal5"].intersection(box(0, 0, 75, 66)), "metal",
           opacity=0.55)
    f.layer("pad", width=1.6, dash="5,3")
    x, y = f.px(37.5, 32)
    f.text(x, y - 4, "Bond pad", weight="bold")
    f.text(x, y + 14, "DVDD")
    f.box(INVERTERS, colour=CLAMP, dash="5,3", width=1.8)
    top = f.oy - 34
    f.label("Clamp transistor: 4 blocks of 20\nfingers, each finger 50 µm wide",
            (37.5, 116), (f.px(0, 131)[0], top), colour=CLAMP, weight="bold")
    f.label("Timer capacitors:\n8 of 10 µm × 25 µm", (19, 231),
            (f.px(0, 226)[0], top), colour=CLAMP, weight="bold")
    f.label("Timer resistors:\n12 of 30 kΩ", (37.5, 287.8),
            (f.px(0, 294)[0], top), colour=CLAMP, weight="bold")
    bot = f.oy + f.dh + 30
    f.label("Guard rings round the\nclamp transistor", (67.6, 110),
            (f.px(0, 122)[0], bot), also=[(65.4, 134)])
    f.label("3 inverters", (58.6, 205), (f.px(0, 205)[0], bot), colour=CLAMP,
            weight="bold")
    f.label("P+ ties to\nthe substrate", (67, 250), (f.px(0, 250)[0], bot))
    f.label("4 diodes from\nDVSS to DVDD", (58, 312.7),
            (f.px(0, 298)[0], bot))
    f.label("4 supply\ncapacitors", (64, 337.8), (f.ox + f.dw, bot),
            anchor="end")
    f.note(CLAMP, "part of the rail clamp")
    return f


def clamp_fingers():
    """A corner of the clamp transistor: no silicide block anywhere."""
    f = Fig(CELL, (8.6, 72.6, 21.4, 94.4), 40, top=64, right=20, bottom=128)
    lay = gdskit.load(CELL)
    nets = {n: gdskit.net(CELL, n)["comp"] for n in ("DVDD", "DVSS")}
    f.geom(nets["DVDD"], "dvdd", opacity=0.85)
    f.geom(nets["DVSS"], "dvss", opacity=0.85)
    f.layer("poly")
    f.geom(lay["poly"].intersection(lay["comp"]), "gate")
    f.layer("contact")
    top = f.oy - 30
    f.label("P+ guard ring, on DVSS", (9.3, 78), (f.px(0, 78)[0], top),
            colour=DVSS, weight="bold")
    f.label("Polysilicon bar joining the gates: 20 in a block, 16 shown",
            (11.8, 86), (f.px(0, 86)[0], top))
    # Diffusion strips repeat every 1.22 µm: drain, gate, source, gate.
    first, pitch = 74.92, 1.22
    bot = f.oy + f.dh + 30

    def under(text, k, gx=20.6, **kw):
        gy = first + k * pitch
        f.label(text, (gx, gy), (f.px(0, gy)[0], bot), **kw)

    under("N+ drain,\non DVDD", 0, colour=DVDD, weight="bold")
    under("N+ source,\non DVSS", 3, colour=DVSS, weight="bold")
    under("Gate", 5.5)
    under("Contacts directly beside each\ngate: no silicide block", 12,
          weight="bold")
    g0 = first + 7.5 * pitch - 0.35
    f.dim((14.4, g0), (14.4, g0 + 0.7), "gate: 0.7 µm")
    d0 = first + 10 * pitch - 0.26
    f.dim((16.6, d0), (16.6, d0 + 0.52), "drain: 0.52 µm")
    return f


def ring():
    """A positive pulse from PAD to DVSS, across two cells of the ring."""
    f = Fig("bi_t", (0, 0, 2 * PITCH, 222), 3.7, left=20, top=70, right=190,
            bottom=136)
    for cell, shift in (("bi_t", 0.0), ("dvss", PITCH)):
        for name, style in (("DVDD", "dvddrail"), ("DVSS", "dvssrail")):
            metal = gdskit.net(cell, name)["metal5"]
            f.geom(translate(metal, xoff=shift), style, opacity=0.4)
    pad = gdskit.net("bi_t", "PAD")
    f.geom(pad["metal2"].intersection(box(0, 0, 75, 201)), "padnet",
           opacity=0.7)
    f.geom(pad["comp"], "paddrain")
    lay = gdskit.load("dvss")
    fet = lay["comp"].intersection(lay["nplus"]).intersection(
        box(10, 72, 65, 192))
    f.geom(translate(fet, xoff=PITCH), "clampfet")
    x0, y0 = f.px(PITCH, 0)
    x1, _ = f.px(PITCH, 222)
    f.over.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" '
                  f'y2="{y0:.1f}" stroke="{INK}" stroke-width="1.4"/>')
    for gx, name, kind in ((37.5, "PAD", "bidirectional pad cell"),
                           (PITCH + 37.5, "DVSS", "DVSS supply pad cell")):
        x, y = f.px(gx, 32)
        f.text(x, y - 4, f"{name} bond pad", weight="bold")
        f.text(x, y + 14, kind)
    x, y = f.px(8, 95)
    f.text(x, y + 5, "NMOS drains")
    x, y = f.px(8, 166)
    f.text(x, y + 5, "PMOS drains")
    x, y = f.px(PITCH, 214)
    f.text(x - 6, y - 6, "cell boundary", anchor="end")
    # One current: along the pad's bus, down the DVDD rail, back to DVSS.
    y_rail = 181.5
    f.flow([(37.5, 64), (37.5, y_rail), (PITCH + 37.5, y_rail),
            (PITCH + 37.5, 62)], width=5.0)
    top = f.oy - 38
    f.label("1  Positive pulse: from the bond pad\nalong metal 2 to the "
            "PMOS drains", (37.5, 118), (f.px(0, 96)[0], top), colour=HOT,
            weight="bold")
    f.label("2  PMOS drain diode: P+ drain to\nN-well, onto the DVDD "
            "stripes above", (37.5, y_rail), (f.px(0, 196)[0] - 30, top),
            colour=HOT, weight="bold")
    bot = f.oy + f.dh + 30
    f.label("5  DVSS stripes to\nthe DVSS bond pad", (PITCH + 37.5, 70),
            (f.px(0, 56)[0], bot), colour=HOT, weight="bold")
    f.label("4  Clamp transistor: from the DVDD\nstripes over it to the "
            "DVSS stripes", (PITCH + 37.5, 150), (f.px(0, 128)[0], bot),
            colour=HOT, weight="bold")
    x, y = f.px(PITCH + 5, y_rail)
    f.label("3  DVDD rail into\nthe next cell", (PITCH + 5, y_rail),
            (f.ox + f.dw + 14, y), anchor="start", colour=HOT, weight="bold",
            lead="left")
    return f


FIGURES = {"gds-clamp": clamp, "gds-clamp-fingers": clamp_fingers,
           "gds-ring": ring}
