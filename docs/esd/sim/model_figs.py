# /// script
# requires-python = ">=3.11"
# dependencies = ["schemdraw>=0.19", "matplotlib"]
# ///
"""Draw the circuit diagrams of the simulation's model changes and of the
scaled pad.

Writes, into docs/esd/figures/:

* added-esd.svg   the pad with the parts the simulation adds for an ESD
                  event highlighted;
* sab-model.svg   the replacement for a silicide-blocked transistor, and
                  the split of a wide transistor;
* scaled-pad.svg  the pad with dedicated diodes and more supply pads.

Run with:  uv run docs/esd/sim/model_figs.py

SPDX-License-Identifier: Apache-2.0
"""

import schemdraw
import schemdraw.elements as elm

from circuits import CHIP, CLAMP, GREY, OUT, box, extent, note

ADD = "#2e8b57"


def rails(d, x0, x1):
    for y, name in ((6, "DVDD"), (0, "DVSS")):
        d += elm.Line().at((x0, y)).to((x1, y)).linewidth(2.4)
        note(d, x1 + 0.2, y, name)


def added_esd():
    with schemdraw.Drawing(show=False) as d:
        rails(d, 1.5, 13.4)
        d += elm.Dot(open=True).at((0, 3)).label("PAD", loc="left")
        d += elm.Line().at((0, 3)).to((12.2, 3))
        # Output transistors, from the foundry netlist.
        for y0, y1, name in ((3.6, 5.4, "PMOS\ndrivers"),
                             (0.6, 2.4, "NMOS\ndrivers")):
            box(d, 1.2, y0, 3.8, y1, name, color=CHIP)
        for a, b in (((2.5, 3), (2.5, 3.6)), ((2.5, 5.4), (2.5, 6)),
                     ((2.5, 3), (2.5, 2.4)), ((2.5, 0.6), (2.5, 0))):
            d += elm.Line().at(a).to(b).color(CHIP)
        # Added drain diodes, scaled by width, with the fitted resistance.
        d += (elm.Diode().up().at((5.0, 3)).to((5.0, 6)).color(ADD)
              .label("drain diode\n480 µm", loc="bottom", ofst=0.2))
        d += (elm.Diode().up().at((5.0, 0)).to((5.0, 3)).color(ADD)
              .label("drain diode\n304 µm", loc="bottom", ofst=0.2))
        # Added avalanche and snapback branches.
        d += (elm.SourceI().down().at((9.4, 6)).to((9.4, 3)).color(ADD)
              .label("PMOS\navalanche\nabove 9.7 V", loc="bottom", ofst=0.2))
        d += (elm.SourceI().down().at((12.2, 3)).to((12.2, 0)).color(ADD)
              .label("NMOS\nsnapback,\nlatched\nabove 10.7 V", loc="bottom",
                     ofst=0.2))
        for p in ((5.0, 6), (5.0, 3), (5.0, 0), (9.4, 6), (9.4, 3),
                  (12.2, 0)):
            d += elm.Dot().at(p)
        note(d, 0.2, 7.2, "blue: from the foundry netlist; green: added",
             color=GREY)
        extent(d, -1.4, 16.4, -0.6)
        d.save(str(OUT / "added-esd.svg"))


def sab_model():
    with schemdraw.Drawing(show=False, fontsize=17) as d:
        note(d, 0, 9.6, "Silicide-blocked transistor", halign="left")
        d += elm.Dot(open=True).at((1.5, 8.6)).label("drain", loc="left")
        d += (elm.Resistor().down().at((1.5, 8.6)).to((1.5, 6.6)).color(ADD)
              .label("blocked drain:\n60 Ω/sq N+,\n185 Ω/sq P+",
                     loc="bottom", ofst=0.2))
        fet = d.add(elm.NFet().right().anchor("drain").at((1.5, 6.6))
                    .reverse().color(CHIP))
        d += elm.Line().at(fet.gate).to((fet.gate[0] - 0.8, fet.gate[1]))
        note(d, fet.gate[0] - 0.9, fet.gate[1] + 0.45, "gate",
             halign="right")
        d += (elm.Resistor().down().at(fet.source)
              .to((fet.source[0], fet.source[1] - 2.0)).color(ADD)
              .label("blocked source", loc="bottom", ofst=0.2))
        d += elm.Dot(open=True).at((fet.source[0], fet.source[1] - 2.0)).label(
            "source", loc="left")
        note(d, -1.4, fet.source[1] - 3.4, "blue: core 6 V transistor,\n"
             "tiny junction areas, lower\njunction current limit",
             color=CHIP)
        # A 4000 um clamp as 40 transistors of 100 um, gates tied.
        x0 = 9.0
        note(d, x0 - 0.4, 9.6, "A 4000 µm transistor", halign="left")
        d += elm.Line().at((x0, 8.0)).to((x0 + 5.6, 8.0))
        d += elm.Line().at((x0, 3.0)).to((x0 + 5.6, 3.0))
        gates = []
        for x in (x0 + 1.2, x0 + 2.8, x0 + 5.2):
            f = d.add(elm.NFet().right().anchor("drain").at((x, 8.0))
                      .reverse())
            d += elm.Line().at(f.source).to((x, 3.0))
            d += elm.Line().at(f.gate).to((f.gate[0], 4.0))
            gates.append(f.gate[0])
        d += elm.Line().at((gates[0] - 0.8, 4.0)).to((gates[-1], 4.0))
        # Under the free end of the gate wire, clear of the source wires.
        note(d, gates[0] - 0.8, 3.5, "gates", halign="left")
        note(d, x0 + 4.0, 5.6, "…", halign="center")
        note(d, x0 + 2.8, 2.2, "40 transistors of 100 µm\nin parallel",
             halign="center")
        extent(d, -1.6, 16.4, 0.6)
        d.save(str(OUT / "sab-model.svg"))


def scaled_pad():
    with schemdraw.Drawing(show=False) as d:
        rails(d, 1.0, 19.6)
        box(d, 1.0, 0.6, 10.0, 5.4, color=CHIP)
        note(d, 1.3, 6.6, "bi_t pad", color=CHIP)
        d += elm.Dot(open=True).at((-0.6, 3)).label("PAD", loc="left")
        d += elm.Line().at((-0.6, 3)).to((8.2, 3))
        for x, lab in ((2.6, "drain diodes"),
                       (5.4, "dedicated:\n0×, 1× or 3× the\ndrivers' width")):
            col = CHIP if x < 3 else ADD
            d += elm.Diode().up().at((x, 3)).to((x, 6)).color(col)
            d += elm.Diode().up().at((x, 0)).to((x, 3)).color(col)
            note(d, x - 1.0 if x < 3 else x + 0.4, -0.8 if x < 3 else -1.8,
                 lab, color=col, halign="center")
            d += elm.Dot().at((x, 3)).color(col)
        # The output NMOS, which snaps back from PAD to DVSS.
        d += elm.Line().at((8.2, 3)).to((8.2, 2.4))
        box(d, 7.0, 0.9, 9.4, 2.4, "output\nNMOS", color=CHIP)
        d += elm.Line().at((8.2, 0.9)).to((8.2, 0))
        note(d, 7.7, 4.2, "snaps back\nabove 10.7 V", color=CHIP,
             halign="center")
        for x in (11.8, 14.4, 18.2):
            box(d, x - 1.1, 1.6, x + 1.1, 4.4, "rail\nclamp", color=CLAMP)
            d += elm.Line().at((x, 6)).to((x, 4.4)).color(CLAMP)
            d += elm.Line().at((x, 1.6)).to((x, 0)).color(CLAMP)
        note(d, 16.3, 3.0, "…", halign="center")
        note(d, 15.0, -1.1, "1 or 4 DVDD pads and as many\nDVSS pads, "
             "each with its rail clamp", color=CLAMP, halign="center")
        extent(d, -2.0, 21.4, -3.0)
        d.save(str(OUT / "scaled-pad.svg"))


def main():
    OUT.mkdir(exist_ok=True)
    added_esd()
    sab_model()
    scaled_pad()


if __name__ == "__main__":
    main()
