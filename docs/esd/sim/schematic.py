# /// script
# requires-python = ">=3.11"
# dependencies = ["schemdraw>=0.19", "matplotlib"]
# ///
"""Draw the ESD protection inside gf180mcu_fd_io__bi_t and the supply pads.

Device sizes are from the cell netlists gf180mcu_fd_io__bi_t.cdl and
gf180mcu_fd_io__dvdd.cdl of the gf180mcu_fd_io library.

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

PRIMARY = "#c0392b"
SECONDARY = "#1f4e9c"
CLAMP = "#e08a00"


def rails(d, x0, x1):
    d += elm.Line().at((x0, TOP)).to((x1, TOP)).linewidth(2.4)
    d += elm.Line().at((x0, BOT)).to((x1, BOT)).linewidth(2.4)
    d += elm.Label().at((x1 + 0.2, TOP)).label("DVDD ring", loc="right",
                                                halign="left")
    d += elm.Label().at((x1 + 0.2, BOT)).label("DVSS ring", loc="right",
                                                halign="left")


def main():
    with schemdraw.Drawing(show=False) as d:
        rails(d, 1.5, 25.5)

        # Bond pad.
        corners = [(0, MID - 0.6), (1.2, MID - 0.6), (1.2, MID + 0.6),
                   (0, MID + 0.6), (0, MID - 0.6)]
        for a, b in zip(corners, corners[1:]):
            d += elm.Line().at(a).to(b).linewidth(2.0)
        d += elm.Label().at((0.6, MID + 1.2)).label("PAD")
        d += elm.Line().at((1.2, MID)).to((3.5, MID))
        d += elm.Dot().at((3.5, MID))

        # Primary protection: the output drivers' drain diodes.
        d += elm.Line().at((3.5, MID)).to((3.5, MID + 0.8))
        d += (elm.Diode().up().at((3.5, MID + 0.8)).to((3.5, TOP))
              .color(PRIMARY).label("drain diode of\nPMOS drivers\n480 µm",
                                     loc="bottom", ofst=0.25))
        d += elm.Line().at((3.5, MID)).to((3.5, MID - 0.8))
        d += (elm.Diode().up().at((3.5, BOT)).to((3.5, MID - 0.8))
              .color(PRIMARY).label("drain diode of\nNMOS drivers\n304 µm",
                                     loc="bottom", ofst=0.25))
        d += elm.Dot().at((3.5, TOP))
        d += elm.Dot().at((3.5, BOT))

        # Secondary protection.
        d += elm.Line().at((3.5, MID)).to((5.5, MID))
        d += (elm.Resistor().right().at((5.5, MID)).to((8.5, MID))
              .color(SECONDARY)
              .label("110 Ω\n(4 × 440 Ω)", loc="top", ofst=0.3))
        d += elm.Line().at((8.5, MID)).to((10.5, MID))
        d += elm.Dot().at((10.5, MID))
        d += (elm.Diode().up().at((10.5, MID)).to((10.5, TOP))
              .color(SECONDARY).label("40 µm²", loc="bottom", ofst=0.2))
        d += (elm.Diode().up().at((10.5, BOT)).to((10.5, MID))
              .color(SECONDARY).label("40 µm²", loc="bottom", ofst=0.2))
        d += elm.Dot().at((10.5, TOP))
        d += elm.Dot().at((10.5, BOT))
        d += elm.Line().at((10.5, MID)).to((12.5, MID))
        d += (logic.Not().right().at((12.5, MID)).anchor("in1")
              .label("input\nbuffer", loc="bottom", ofst=0.4))

        # Rail clamp, in each DVDD and DVSS pad cell.
        d += elm.Line().at((17.0, TOP)).to((17.0, TOP - 0.5))
        d += (elm.Resistor().down().at((17.0, TOP - 0.5)).to((17.0, MID))
              .color(CLAMP).label("360 kΩ", loc="top"))
        d += elm.Dot().at((17.0, MID))
        d += (elm.Capacitor().down().at((17.0, MID)).to((17.0, BOT))
              .color(CLAMP).label("MOS\ncapacitor", loc="top"))
        d += elm.Dot().at((17.0, TOP))
        d += elm.Dot().at((17.0, BOT))
        d += elm.Line().at((17.0, MID)).to((18.0, MID)).color(CLAMP)
        inv = d.add(logic.Not().right().at((18.0, MID)).anchor("in1")
                    .color(CLAMP)
                    .label("three\ninverters", loc="bottom", ofst=0.4))
        d += elm.Line().at(inv.out).to((22.0, MID)).color(CLAMP)
        fet = d.add(elm.NFet().anchor("gate").at((22.0, MID)).reverse()
                    .color(CLAMP))
        d += elm.Line().at(fet.drain).to((fet.drain[0], TOP))
        d += elm.Line().at(fet.source).to((fet.source[0], BOT))
        d += elm.Label().at((fet.drain[0] + 0.4, MID + 0.9)).label(
            "clamp NMOS\n4000 µm", halign="left", color=CLAMP)
        d += elm.Dot().at((fet.drain[0], TOP))
        d += elm.Dot().at((fet.source[0], BOT))

        # Group labels.
        d += elm.Label().at((3.5, TOP + 1.0)).label("primary",
                                                      color=PRIMARY)
        d += elm.Label().at((10.5, TOP + 1.0)).label("secondary",
                                                       color=SECONDARY)
        d += elm.Label().at((20.0, TOP + 1.0)).label(
            "rail clamp (in the DVDD and DVSS pads)", color=CLAMP)
        d += elm.Label().at((8.0, TOP + 1.9)).label(
            "inside gf180mcu_fd_io__bi_t")

        OUT.mkdir(exist_ok=True)
        d.save(str(OUT / "io-cell.svg"))


if __name__ == "__main__":
    main()
