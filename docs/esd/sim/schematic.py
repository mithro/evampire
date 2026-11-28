# /// script
# requires-python = ">=3.11"
# dependencies = ["schemdraw>=0.19", "matplotlib"]
# ///
"""Draw the ESD protection inside gf180mcu_fd_io__bi_t and the supply pads.

Writes four files in docs/esd/figures: io-cell.svg, the whole schematic,
and io-cell-primary.svg, io-cell-secondary.svg and io-cell-clamp.svg,
the same schematic with one group in colour and the others in grey.
Device sizes are from the cell netlists gf180mcu_fd_io__bi_t.cdl and
gf180mcu_fd_io__dvdd.cdl of the gf180mcu_fd_io library;
gf180mcu_fd_io__dvss.cdl has the same devices.

Run with:  uv run docs/esd/sim/schematic.py

SPDX-License-Identifier: Apache-2.0
"""

import pathlib

import matplotlib

matplotlib.use("Agg")
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402
from schemdraw import logic  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parent.parent / "figures"
schemdraw.use("svg")
schemdraw.config(fontsize=17, inches_per_unit=0.42, lw=1.6, margin=1.0)

TOP = 9.0    # DVDD rail
BOT = 0.0    # DVSS rail
MID = 4.5    # pad level
FET = 20.6   # the clamp transistor's column, nearest the bond pad
RC = 25.4    # the clamp timer's column
DIODE = 30.4  # the rail diode's column

GROUPS = {"primary": "#c0392b", "secondary": "#1f4e9c", "clamp": "#e08a00"}
DIM = "#b4b4b4"   # a group that the figure does not show


def rails(d, x0, x1):
    d += elm.Line().at((x0, TOP)).to((x1, TOP)).linewidth(2.4)
    d += elm.Line().at((x0, BOT)).to((x1, BOT)).linewidth(2.4)
    d += elm.Label().at((x1 + 0.2, TOP)).label("DVDD ring", loc="right",
                                                halign="left")
    d += elm.Label().at((x1 + 0.2, BOT)).label("DVSS ring", loc="right",
                                                halign="left")


def cell_box(d, x0, x1, name):
    """A dashed boundary round the parts that one pad cell holds."""
    y0, y1 = BOT - 0.9, TOP + 1.6
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    for a, b in zip(corners, corners[1:]):
        d += (elm.Line().at(a).to(b).linestyle("--").color("#666666")
              .linewidth(1.2))
    d += elm.Label().at(((x0 + x1) / 2, y1 + 0.5)).label("inside " + name)


def draw(path, show=None):
    """The schematic, with only the group `show` in colour if one is given."""
    primary, secondary, clamp = (
        colour if show in (None, group) else DIM
        for group, colour in GROUPS.items())
    with schemdraw.Drawing(show=False) as d:
        rails(d, 1.5, 35.4)

        # Bond pad.
        corners = [(0, MID - 0.6), (1.2, MID - 0.6), (1.2, MID + 0.6),
                   (0, MID + 0.6), (0, MID - 0.6)]
        for a, b in zip(corners, corners[1:]):
            d += elm.Line().at(a).to(b).linewidth(2.0)
        d += elm.Label().at((0.6, MID + 1.2)).label("PAD")
        d += elm.Line().at((1.2, MID)).to((3.5, MID))
        d += elm.Dot().at((3.5, MID))

        # Primary protection: the output drivers' drain diodes.
        d += elm.Line().at((3.5, MID)).to((3.5, MID + 0.8)).color(primary)
        d += (elm.Diode().up().at((3.5, MID + 0.8)).to((3.5, TOP))
              .color(primary)
              .label("drain diode of\nPMOS drivers:\n480 µm of gate",
                     loc="bottom", ofst=0.25))
        d += elm.Line().at((3.5, MID)).to((3.5, MID - 0.8)).color(primary)
        d += (elm.Diode().up().at((3.5, BOT)).to((3.5, MID - 0.8))
              .color(primary)
              .label("drain diode of\nNMOS drivers:\n304 µm of gate",
                     loc="bottom", ofst=0.25))
        d += elm.Dot().at((3.5, TOP))
        d += elm.Dot().at((3.5, BOT))

        # Secondary protection.
        d += elm.Line().at((3.5, MID)).to((5.5, MID))
        d += (elm.Resistor().right().at((5.5, MID)).to((8.5, MID))
              .color(secondary)
              .label("110 Ω: 4 of\n440 Ω in parallel", loc="top", ofst=0.3))
        d += elm.Line().at((8.5, MID)).to((10.5, MID))
        d += elm.Dot().at((10.5, MID))
        d += (elm.Diode().up().at((10.5, MID)).to((10.5, TOP))
              .color(secondary).label("40 µm²", loc="bottom", ofst=0.2))
        d += (elm.Diode().up().at((10.5, BOT)).to((10.5, MID))
              .color(secondary).label("40 µm²", loc="bottom", ofst=0.2))
        d += elm.Dot().at((10.5, TOP))
        d += elm.Dot().at((10.5, BOT))
        d += elm.Line().at((10.5, MID)).to((12.5, MID))
        d += (logic.Buf().right().at((12.5, MID)).anchor("in1")
              .label("input\nbuffer", loc="bottom", ofst=0.4))

        # Rail clamp, in each DVDD and DVSS pad cell, in the order of the
        # layout: the transistor nearest the bond pad, then the inverters
        # and the timer.
        fet = d.add(elm.NFet().anchor("gate").at((FET + 1.0, MID))
                    .color(clamp))
        d += elm.Line().at(fet.drain).to((fet.drain[0], TOP)).color(clamp)
        d += elm.Line().at(fet.source).to((fet.source[0], BOT)).color(clamp)
        d += elm.Label().at((fet.drain[0] - 0.4, MID + 1.3)).label(
            "clamp NMOS:\n4000 µm\nof gate", halign="right", color=clamp)
        d += elm.Dot().at((fet.drain[0], TOP))
        d += elm.Dot().at((fet.source[0], BOT))
        inv = d.add(logic.Not().left().at((RC - 1.0, MID)).anchor("in1")
                    .color(clamp)
                    .label("three\ninverters", loc="bottom", ofst=0.4))
        d += elm.Line().at(inv.out).to((FET + 1.0, MID)).color(clamp)
        d += elm.Line().at((RC, MID)).to((RC - 1.0, MID)).color(clamp)
        d += elm.Line().at((RC, TOP)).to((RC, TOP - 0.5)).color(clamp)
        d += (elm.Resistor().down().at((RC, TOP - 0.5)).to((RC, MID))
              .color(clamp).label("360 kΩ", loc="bottom"))
        d += elm.Dot().at((RC, MID))
        d += (elm.Capacitor().down().at((RC, MID)).to((RC, BOT))
              .color(clamp).label("MOS\ncapacitor", loc="bottom"))
        d += elm.Dot().at((RC, TOP))
        d += elm.Dot().at((RC, BOT))

        # Rail diode, four parts, in each DVDD and DVSS pad cell.
        d += (elm.Diode().up().at((DIODE, BOT)).to((DIODE, TOP))
              .color(clamp).label("160 µm²:\n4 of 40 µm²", loc="bottom",
                                   ofst=0.2))
        d += elm.Dot().at((DIODE, TOP))
        d += elm.Dot().at((DIODE, BOT))

        # Group labels.
        d += elm.Label().at((3.5, TOP + 1.0)).label("primary", color=primary)
        d += elm.Label().at((10.5, TOP + 1.0)).label("secondary",
                                                       color=secondary)
        d += elm.Label().at((RC, TOP + 1.0)).label(
            "rail clamp and rail diode", color=clamp)
        # The rings run through every cell; each box is one cell's parts.
        cell_box(d, -0.5, 15.2, "gf180mcu_fd_io__bi_t")
        cell_box(d, 15.6, 34.8, "each of gf180mcu_fd_io__dvdd and "
                 "gf180mcu_fd_io__dvss")
        d.save(str(path))


def main():
    OUT.mkdir(exist_ok=True)
    draw(OUT / "io-cell.svg")
    for group in GROUPS:
        draw(OUT / f"io-cell-{group}.svg", show=group)


if __name__ == "__main__":
    main()
