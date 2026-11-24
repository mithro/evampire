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
            box(d, 1.6, y0, 3.4, y1, name, color=CHIP)
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
    with schemdraw.Drawing(show=False) as d:
        note(d, 0, 9.4, "Silicide-blocked transistor", halign="left")
        d += elm.Dot(open=True).at((1.5, 8.6)).label("drain", loc="left")
        d += (elm.Resistor().down().at((1.5, 8.6)).to((1.5, 6.6)).color(ADD)
              .label("blocked drain:\n60 Ω/sq N+,\n185 Ω/sq P+",
                     loc="bottom", ofst=0.2))
        fet = d.add(elm.NFet().right().anchor("drain").at((1.5, 6.6))
                    .reverse().color(CHIP))
        d += elm.Line().at(fet.gate).to((fet.gate[0] - 0.8, fet.gate[1]))
        note(d, fet.gate[0] - 0.9, fet.gate[1] + 0.45, "gate",
             halign="right")
        note(d, 4.9, fet.gate[1] + 0.1, "core 6 V transistor:\ntiny "
             "junction areas,\nlower junction\ncurrent limit", color=CHIP)
        d += (elm.Resistor().down().at(fet.source)
              .to((fet.source[0], fet.source[1] - 2.0)).color(ADD)
              .label("blocked source", loc="bottom", ofst=0.2))
        d += elm.Dot(open=True).at((fet.source[0], fet.source[1] - 2.0)).label(
            "source", loc="left")
        # A 4000 um clamp as 40 transistors of 100 um.
        x0 = 11.0
        note(d, x0 - 0.4, 9.4, "A 4000 µm transistor", halign="left")
        d += elm.Line().at((x0, 8.0)).to((x0 + 5.0, 8.0))
        d += elm.Line().at((x0, 3.0)).to((x0 + 5.0, 3.0))
        for k, x in enumerate((x0 + 0.6, x0 + 2.0, x0 + 4.4)):
            f = d.add(elm.NFet().right().anchor("drain").at((x, 8.0))
                      .reverse())
            d += elm.Line().at(f.source).to((x, 3.0))
        note(d, x0 + 3.2, 5.5, "…", halign="center")
        note(d, x0 + 2.5, 2.2, "40 transistors of 100 µm in parallel",
             halign="center")
        extent(d, -1.6, 18.4, 1.6)
        d.save(str(OUT / "sab-model.svg"))


def scaled_pad():
    with schemdraw.Drawing(show=False) as d:
        rails(d, 1.0, 18.6)
        box(d, 1.0, 0.6, 8.4, 5.4, color=CHIP)
        note(d, 7.4, 4.8, "bi_t pad", color=CHIP, halign="center")
        d += elm.Dot(open=True).at((-0.6, 3)).label("PAD", loc="left")
        d += elm.Line().at((-0.6, 3)).to((5.6, 3))
        for x, lab in ((2.4, "drain\ndiodes"),
                       (5.6, "dedicated,\n1×, 2× or 4×")):
            col = CHIP if x < 3 else ADD
            d += elm.Diode().up().at((x, 3)).to((x, 6)).color(col)
            d += elm.Diode().up().at((x, 0)).to((x, 3)).color(col)
            note(d, x + 0.25, 2.3, lab, color=col)
            d += elm.Dot().at((x, 3)).color(col)
        for k, x in enumerate((10.2, 12.6, 16.6)):
            box(d, x - 0.9, 1.6, x + 0.9, 4.4, "rail\nclamp", color=CLAMP)
            d += elm.Line().at((x, 6)).to((x, 4.4)).color(CLAMP)
            d += elm.Line().at((x, 1.6)).to((x, 0)).color(CLAMP)
        note(d, 14.6, 3.0, "…", halign="center")
        note(d, 13.4, -0.9, "1 or 4 DVDD pads and as many DVSS pads,\n"
             "each with its rail clamp", color=CLAMP, halign="center")
        extent(d, -2.0, 20.4, -2.0)
        d.save(str(OUT / "scaled-pad.svg"))


def main():
    OUT.mkdir(exist_ok=True)
    added_esd()
    sab_model()
    scaled_pad()


if __name__ == "__main__":
    main()
