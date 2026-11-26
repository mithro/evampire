"""Figures of the rail clamp in the supply pads gf180mcu_fd_io__dvdd/dvss.

Helper for figures.py: run that script, not this module.

SPDX-License-Identifier: Apache-2.0
"""

import gdskit
from layfig import CLAMP, DVDD, DVSS, HOT, INK, Fig
from shapely.affinity import translate
from shapely.geometry import box

CELL = "dvdd"
PITCH = 75.0   # width of a pad cell: the next cell along the ring


def clamp():
    """The whole DVDD pad: the rail clamp and its timer."""
    f = Fig(CELL, (0, 0, 75, 350), 2.7, top=62, right=20, bottom=118)
    lay = gdskit.load(CELL)
    f.silicon()
    f.geom(lay["metal5"].intersection(box(0, 0, 75, 66)), "metal",
           opacity=0.55)
    f.layer("pad", width=1.6, dash="5,3")
    x, y = f.px(37.5, 32)
    f.text(x, y - 4, "Bond pad", weight="bold")
    f.text(x, y + 14, "DVDD")
    top = f.oy - 34
    f.label("Clamp transistor: 4 blocks of\n20 fingers, 50 µm each",
            (37.5, 116), (f.px(0, 131)[0], top), colour=CLAMP, weight="bold")
    f.label("Timer capacitors:\n8 of 10 µm × 25 µm", (19, 246),
            (f.px(0, 233)[0], top), colour=CLAMP, weight="bold")
    f.label("Timer resistors:\n12 of 30 kΩ", (37.5, 287.8),
            (f.px(0, 300)[0], top), colour=CLAMP, weight="bold")
    bot = f.oy + f.dh + 30
    f.label("Guard rings", (67.5, 131), (f.px(0, 131)[0], bot))
    f.label("3 inverters", (52, 209), (f.px(0, 205)[0], bot), colour=CLAMP,
            weight="bold")
    f.label("4 diodes from\nDVSS to DVDD", (57, 312.7),
            (f.px(0, 268)[0], bot))
    f.label("4 capacitors from\nDVDD to DVSS", (64, 337.8),
            (f.ox + f.dw, bot), anchor="end")
    return f


def clamp_fingers():
    """A corner of the clamp transistor: no silicide block anywhere."""
    f = Fig(CELL, (8.6, 72.6, 21.4, 94.4), 40, top=64, right=20, bottom=104)
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
    f.label("Polysilicon bar joining the 20 gates of a block", (11.8, 88.5),
            (f.px(0, 88.5)[0] - 60, top))
    # Diffusion strips repeat every 1.22 µm: drain, gate, source, gate.
    first, pitch = 74.92, 1.22
    bot = f.oy + f.dh + 30
    f.label("Drain, on DVDD", (20.6, first + 2 * pitch),
            (f.px(0, 75.5)[0], bot), colour=DVDD, weight="bold")
    f.label("Source, on DVSS", (20.6, first + 5 * pitch),
            (f.px(0, 80.2)[0], bot), colour=DVSS, weight="bold")
    f.label("Gate", (20.6, first + 7.5 * pitch),
            (f.px(0, 84.07)[0], bot))
    f.label("Contacts right beside each gate:\nno silicide block",
            (18.2, first + 10 * pitch), (f.px(0, 90)[0], bot))
    g0 = first + 3.5 * pitch - 0.35
    f.dim((15.2, g0), (15.2, g0 + 0.7), "0.7 µm")
    return f


def ring():
    """A positive pulse from PAD to DVSS, across two cells of the ring."""
    f = Fig("bi_t", (0, 0, 2 * PITCH, 350), 2.7, left=20, top=66, right=20,
            bottom=110)
    for cell, shift in (("bi_t", 0.0), ("dvss", PITCH)):
        for name, style in (("DVDD", "dvddrail"), ("DVSS", "dvssrail")):
            metal = gdskit.net(cell, name)["metal5"]
            f.geom(translate(metal, xoff=shift), style, opacity=0.45)
    pad = gdskit.net("bi_t", "PAD")
    f.geom(pad["metal2"], "padnet", opacity=0.6)
    f.geom(pad["comp"], "paddrain")
    lay = gdskit.load("dvss")
    fet = lay["comp"].intersection(lay["nplus"]).intersection(
        box(10, 72, 65, 192))
    f.geom(translate(fet, xoff=PITCH), "clampfet")
    f.box((0, 0, PITCH, 350), colour=INK, dash=None, width=1.2)
    f.box((PITCH, 0, 2 * PITCH, 350), colour=INK, dash=None, width=1.2)
    for gx, name, kind in ((37.5, "PAD", "bidirectional pad cell"),
                           (PITCH + 37.5, "DVSS", "DVSS supply pad cell")):
        x, y = f.px(gx, 32)
        f.text(x, y - 4, f"{name} bond pad", weight="bold")
        f.text(x, y + 14, kind)
    # The current: along the pad's bus, down the DVDD rail, back to DVSS.
    y_rail = 181.5
    f.flow([(37.5, 66), (37.5, y_rail - 20)])
    f.flow([(37.5, y_rail), (PITCH + 30, y_rail)])
    f.flow([(PITCH + 37.5, y_rail - 6), (PITCH + 37.5, 66)], colour=CLAMP)
    top = f.oy - 36
    f.label("1  Bond pad and metal 2 bus\nto the PMOS drains", (37.5, 100),
            (f.px(0, 96)[0], top), colour=HOT, weight="bold")
    f.label("2  PMOS drain diode\nonto the DVDD rail", (28, y_rail),
            (f.px(0, 225)[0], top), colour=HOT, weight="bold")
    bot = f.oy + f.dh + 30
    f.label("4  Clamp transistor,\nfrom DVDD to DVSS", (PITCH + 37.5, 120),
            (f.px(0, 110)[0], bot), colour=CLAMP, weight="bold")
    f.label("3  DVDD rail into\nthe next cell", (PITCH + 12, y_rail),
            (f.px(0, 225)[0], bot), colour=HOT, weight="bold")
    return f


FIGURES = {"gds-clamp": clamp, "gds-clamp-fingers": clamp_fingers,
           "gds-ring": ring}
