# /// script
# requires-python = ">=3.11"
# dependencies = ["schemdraw>=0.19", "matplotlib"]
# ///
"""Draw the ESD circuit diagrams that need no simulation results.

Writes, into docs/esd/figures/:

* testers.svg      the human body model, IEC 61000-4-2 and charged device
                   model testers as circuits;
* testbench.svg    the simulated test circuit: the three foundry pads, the
                   rings and the generator;
* board-tvs.svg    a board suppressor and series resistor in front of a
                   chip pin;
* hv-clamps.svg    the two kinds of clamp for a pin that works above DVDD.

Component values are those on the ESD pages. Run with:

    uv run docs/esd/sim/circuits.py

SPDX-License-Identifier: Apache-2.0
"""

import pathlib

import matplotlib

matplotlib.use("Agg")
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parent.parent / "figures"
schemdraw.use("svg")
schemdraw.config(fontsize=15, inches_per_unit=0.4, lw=1.6, margin=0.6)

HOT = "#c0392b"      # the discharge current path
CHIP = "#1f4e9c"
CLAMP = "#e08a00"
GREY = "#666666"


def box(d, x0, y0, x1, y1, label=None, color="black", ls="-"):
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    for p, q in zip(corners, corners[1:]):
        d += elm.Line().at(p).to(q).color(color).linestyle(ls)
    if label:
        d += elm.Label().at(((x0 + x1) / 2, (y0 + y1) / 2)).label(
            label, color=color)


def extent(d, x0, x1, y):
    """An invisible line that widens the drawing's bounding box, which
    schemdraw computes from the elements and not from label text."""
    d += elm.Line().at((x0, y)).to((x1, y)).color("white").linewidth(0.1)


def note(d, x, y, text, color="black", halign="left"):
    d += elm.Label().at((x, y)).label(text, color=color, halign=halign)


def tester_loop(d, y, c_label, r_label, l_label, title, r_colour,
                title_dy=5.4):
    """Capacitor, resistor and wiring inductance, switched into a pin whose
    protection conducts to the grounded pin, with the simulation's values.
    """
    note(d, 0, y + title_dy, title, halign="left")
    d += elm.Capacitor().up().at((0.6, y)).to((0.6, y + 3)).label(
        c_label, loc="top", ofst=0.25)
    d += elm.Line().at((0.6, y + 3)).to((1.0, y + 3))
    d += elm.Resistor().right().at((1.0, y + 3)).to((3.6, y + 3)).color(
        r_colour).label(r_label, loc="top")
    d += elm.Inductor().right().at((3.6, y + 3)).to((5.4, y + 3)).label(
        l_label, loc="top")
    d += elm.Dot().at((5.6, y + 3))
    d += elm.Line().at((5.4, y + 3)).to((5.6, y + 3))
    d += elm.Switch().right().at((5.6, y + 3)).to((7.2, y + 3))
    d += elm.Line().at((7.2, y + 3)).to((8.0, y + 3))
    d += elm.Dot().at((8.0, y + 3)).label("pin", loc="right")
    box(d, 7.0, y + 0.6, 9.0, y + 2.4, "chip", color=CHIP)
    d += elm.Line().at((8.0, y + 3)).to((8.0, y + 2.4))
    d += elm.Line().at((8.0, y + 0.6)).to((8.0, y))
    d += elm.Line().at((0.6, y)).to((8.0, y))
    d += elm.Ground().at((4.3, y))


def testers():
    with schemdraw.Drawing(show=False) as d:
        tester_loop(d, 10.6, "100 pF", "1500 Ω", "5 µH",
                    "Human body model, 2 kV", HOT)
        note(d, 2.3, 12.5, "≈ 1990 V across it", color=HOT,
             halign="center")
        note(d, 9.4, 12.1, "≈ 10 V on the pin,\n1.33 A at 2 kV", color=CHIP)
        tester_loop(d, 2.6, "150 pF", "330 Ω", "2 µH",
                    "IEC 61000-4-2, through a metal tip", "black",
                    title_dy=6.4)
        # The fast branch that forms the IEC first peak, fitted.
        y = 2.6
        d += elm.Line().at((-0.8, y)).to((0.6, y))
        d += elm.Capacitor().up().at((-0.8, y)).to((-0.8, y + 4.4)).label(
            "6 pF", loc="top", ofst=0.25)
        d += elm.Resistor().right().at((-0.8, y + 4.4)).to((1.8, y + 4.4)
                                                           ).label("200 Ω")
        d += elm.Inductor().right().at((1.8, y + 4.4)).to((3.6, y + 4.4)
                                                          ).label("120 nH")
        d += elm.Line().at((3.6, y + 4.4)).to((5.6, y + 4.4))
        d += elm.Line().at((5.6, y + 4.4)).to((5.6, y + 3))
        note(d, 6.0, y + 4.9, "fast branch, fitted\nto the first peak",
             color=GREY)
        note(d, 9.4, y + 1.6, "first peak 3.75 A\nper kV, 30 A at 8 kV",
             color=CHIP)
        note(d, 0.3, 1.5, "contact discharge: the tip touches the pin "
             "first", color=GREY)
        note(d, 0.3, 0.7, "air discharge: a spark jumps as the tip "
             "approaches", color=GREY)
        # Charged device model: the chip is the capacitor.
        y = -4.4
        note(d, 0, y + 3.6, "Charged device model", halign="left")
        box(d, -0.2, y + 1.2, 4.0, y + 2.6, "charged chip", color=CHIP)
        d += elm.Line().at((4.0, y + 1.9)).to((4.8, y + 1.9))
        d += elm.Switch().right().at((4.8, y + 1.9)).to((6.8, y + 1.9)).label(
            "pin touches", loc="top")
        d += elm.Line().at((6.8, y + 1.9)).to((7.6, y + 1.9)).color(HOT)
        d += elm.Ground().at((7.6, y + 1.9))
        d += elm.Capacitor().down().at((1.9, y + 1.2)).to((1.9, y - 0.6)
                                                          ).linestyle("--")
        d += elm.Ground().at((1.9, y - 0.6))
        note(d, 2.3, y + 0.3, "capacitance to\nits surroundings",
             color=GREY)
        note(d, 8.3, y + 1.9, "under 1 ns,\ntens of amperes", color=CHIP)
        extent(d, -1.2, 14.6, y - 1.0)
        OUT.mkdir(exist_ok=True)
        d.save(str(OUT / "testers.svg"))


def clamp_cell(d, x, name):
    """A supply pad cell holding a rail clamp between the two rings."""
    box(d, x - 1.5, 0.6, x + 1.5, 5.4, color=CLAMP)
    note(d, x, 6.8, name, color=CLAMP, halign="center")
    d += elm.Line().at((x, 6)).to((x, 4.2))
    d += elm.Line().at((x, 0)).to((x, 1.8))
    box(d, x - 1.1, 1.8, x + 1.1, 4.2, "rail\nclamp", color=CLAMP)
    d += elm.Dot().at((x, 6))
    d += elm.Dot().at((x, 0))


def testbench():
    with schemdraw.Drawing(show=False, fontsize=18) as d:
        # The DVDD and DVSS rings, with their resistance.
        for y, name in ((6, "DVDD"), (0, "DVSS")):
            d += elm.Line().at((1.4, y)).to((7.0, y)).linewidth(2.4)
            d += (elm.Resistor().right().at((7.0, y)).to((9.0, y))
                  .label("0 or 1 Ω", loc="top" if y else "bottom"))
            d += elm.Line().at((9.0, y)).to((17.4, y)).linewidth(2.4)
            note(d, 17.6, y, name)
        # The bidirectional pad cell.
        box(d, 1.4, 0.6, 6.6, 5.4, color=CHIP)
        note(d, 4.0, 6.8, "bi_t pad", color=CHIP, halign="center")
        note(d, 4.0, 3.3, "drivers, drain\ndiodes, input\nprotection",
             color=CHIP, halign="center")
        note(d, 4.0, 1.4, "A, OE: low", color=GREY, halign="center")
        d += elm.Line().at((4.0, 5.4)).to((4.0, 6))
        d += elm.Line().at((4.0, 0.6)).to((4.0, 0))
        d += elm.Dot().at((4.0, 6))
        d += elm.Dot().at((4.0, 0))
        clamp_cell(d, 11.4, "DVDD pad")
        clamp_cell(d, 15.4, "DVSS pad")
        # The generator into PAD, returning to the grounded DVSS.
        d += elm.Line().at((1.4, 3.0)).to((0.6, 3.0)).color(HOT)
        d += elm.Dot(open=True).at((0.6, 3.0)).label("PAD", loc="top")
        box(d, -4.4, 1.6, -0.4, 4.4, "HBM or IEC\ngenerator")
        d += elm.Line().at((-0.4, 3.0)).to((0.6, 3.0)).color(HOT)
        d += elm.Line().at((-2.4, 1.6)).to((-2.4, -1.2))
        d += elm.Line().at((-2.4, -1.2)).to((15.4, -1.2))
        d += elm.Line().at((15.4, 0)).to((15.4, -1.2))
        d += elm.Ground().at((6.0, -1.2))
        note(d, 6.4, -2.0, "tester ground on the DVSS pad", color=GREY)
        note(d, 6.4, -3.0, "DVDD floats", color=GREY)
        extent(d, -4.4, 19.4, -3.4)
        OUT.mkdir(exist_ok=True)
        d.save(str(OUT / "testbench.svg"))


def board_tvs():
    with schemdraw.Drawing(show=False) as d:
        d += elm.Arrow().right().at((-1.6, 3)).to((0, 3)).color(HOT)
        note(d, -1.7, 3.7, "IEC discharge", color=HOT)
        d += elm.Dot(open=True).at((0, 3)).label("connector", loc="bottom")
        d += elm.Line().at((0, 3)).to((2.5, 3)).color(HOT)
        d += elm.Dot().at((2.5, 3))
        d += (elm.DiodeTVS().down().at((2.5, 3)).to((2.5, 0)).color(HOT)
              .label("suppressor:\n14 V at 5 A\n(datasheet)",
                     loc="bottom", ofst=0.3))
        d += elm.Ground().at((2.5, 0))
        d += (elm.Resistor().right().at((2.5, 3)).to((6.5, 3))
              .label("$R_{series}$ = 10 Ω", loc="top"))
        d += elm.Line().at((6.5, 3)).to((8.0, 3))
        d += elm.Dot().at((8.0, 3)).label("chip pin", loc="top")
        box(d, 7.2, 0.6, 8.8, 2.4, "chip", color=CHIP)
        d += elm.Line().at((8.0, 3)).to((8.0, 2.4))
        d += elm.Line().at((8.0, 0.6)).to((8.0, 0))
        d += elm.Ground().at((8.0, 0))
        note(d, 9.2, 1.5, "protection holds\nthe pin near 4 V", color=CHIP)
        note(d, 0.4, 0.9, "most of\nthe current", color=HOT,
             halign="center")
        note(d, 4.5, -1.3, "$I_{chip}$ ≈ ($V_{TVS}$ − $V_{pin}$) / "
             "$R_{series}$ = (14 V − 4 V) / 10 Ω = 1 A", halign="center")
        extent(d, -4.2, 15.4, -1.8)
        OUT.mkdir(exist_ok=True)
        d.save(str(OUT / "board-tvs.svg"))


def snapback_stack(d, x):
    note(d, x + 1.6, 7.6, "stack of snapback devices", halign="center")
    d += elm.Dot(open=True).at((x, 7.0)).label("pin", loc="left")
    d += elm.Line().at((x, 7.0)).to((x + 1.6, 7.0))
    y = 7.0
    for k in range(3):
        fet = d.add(elm.NFet().anchor("drain").at((x + 1.6, y)).reverse()
                    .color(CLAMP))
        d += elm.Line().at(fet.gate).to((fet.gate[0] - 0.5, fet.gate[1]))
        d += elm.Line().at((fet.gate[0] - 0.5, fet.gate[1])).to(
            (fet.gate[0] - 0.5, fet.source[1]))
        d += elm.Line().at((fet.gate[0] - 0.5, fet.source[1])).to(fet.source)
        y = fet.source[1]
    d += elm.Ground().at((x + 1.6, y))
    note(d, x + 2.4, 4.8, "trigger voltages\nadd", color=CLAMP)
    note(d, x + 2.4, 3.2, "each in its own\nisolated well", color=GREY)


def drift_clamp(d, x):
    note(d, x + 2.4, 7.6, "drift-region transistor and timer",
         halign="center")
    d += elm.Dot(open=True).at((x, 7.0)).label("pin", loc="left")
    d += elm.Line().at((x, 7.0)).to((x + 4.4, 7.0))
    d += elm.Dot().at((x + 0.8, 7.0))
    d += elm.Resistor().down().at((x + 0.8, 7.0)).to((x + 0.8, 4.2)).label(
        "R", loc="bottom")
    d += elm.Dot().at((x + 0.8, 4.2))
    d += elm.Capacitor().down().at((x + 0.8, 4.2)).to((x + 0.8, 2.0)).label(
        "C", loc="bottom")
    d += elm.Ground().at((x + 0.8, 2.0))
    d += elm.Line().at((x + 0.8, 4.2)).to((x + 1.4, 4.2))
    box(d, x + 1.4, 3.2, x + 3.2, 5.2, "invert-\ning\ndriver")
    d += elm.Line().at((x + 3.2, 4.2)).to((x + 3.4, 4.2))
    fet = d.add(elm.NFet().anchor("gate").at((x + 3.4, 4.2)).reverse()
                .color(CLAMP))
    d += elm.Line().at(fet.drain).to((fet.drain[0], 7.0))
    d += elm.Line().at((x + 4.4, 7.0)).to((fet.drain[0], 7.0))
    d += elm.Ground().at(fet.source)
    note(d, fet.drain[0] + 0.4, 5.2, "long, lightly\ndoped drift region",
         color=CLAMP)


def hv_clamps():
    with schemdraw.Drawing(show=False) as d:
        snapback_stack(d, 0)
        drift_clamp(d, 8.2)
        extent(d, -2.6, 18.6, 1.0)
        OUT.mkdir(exist_ok=True)
        d.save(str(OUT / "hv-clamps.svg"))


def main():
    testers()
    testbench()
    board_tvs()
    hv_clamps()


if __name__ == "__main__":
    main()
