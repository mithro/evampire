# /// script
# requires-python = ">=3.11"
# dependencies = ["schemdraw>=0.19", "matplotlib"]
# ///
"""Draw the four discharge paths through the bidirectional pad.

Writes docs/esd/figures/paths.svg: one simplified copy of the pad's
protection per discharge mode, with the current's path drawn thick. A
dashed path is the one that also conducts once the pad passes the voltage
named beside it. The paths are those of the table tab-esd-paths on
docs/esd/io-cells.rst. Run with:

    uv run docs/esd/sim/paths.py

SPDX-License-Identifier: Apache-2.0
"""

import schemdraw.elements as elm

import schemdraw
from circuits import GREY, HOT, OUT, box, extent, note

SECOND = "#8e44ad"   # snapback and avalanche, as in sections.py
# Each mode: title, the rail the tester grounds, the polarity at PAD, the
# parts on the main path and the parts on the high-voltage second path.
MODES = [
    ("Positive, PAD to DVSS", "DVSS", "+",
     {"dp", "dvdd.b", "dvdd.c", "clamp", "dvss.c", "dvss.b", "dvss.a"},
     {"nmos", "pad.b"}, "NMOS snaps back\nabove 10.7 V"),
    ("Negative, PAD to DVSS", "DVSS", "−", {"dvss.a", "dn"}, set(), None),
    ("Positive, PAD to DVDD", "DVDD", "+", {"dp", "dvdd.a"}, set(), None),
    ("Negative, PAD to DVDD", "DVDD", "−",
     {"dvdd.a", "dvdd.b", "dvdd.c", "clamp", "dvss.c", "dvss.b", "dn"},
     {"dp"}, "PMOS drain\navalanches\nabove 9.7 V"),
]
XS = {"a": (0.6, 1.5), "b": (1.5, 3.5), "c": (3.5, 7.2)}


def style(el, part, main, second):
    if part in main:
        return el.color(HOT).linewidth(3.2)
    if part in second:
        return el.color(SECOND).linewidth(3.2).linestyle("--")
    return el.color("#999999")


def panel(d, ox, oy, mode):
    title, ground, sign, main, second, note2 = mode
    note(d, ox + 0.2, oy + 7.4, title, halign="left")
    for name, y in (("dvdd", 6.0), ("dvss", 0.0)):
        for seg, (x0, x1) in XS.items():
            d += style(elm.Line().at((ox + x0, oy + y)).to((ox + x1, oy + y)),
                       f"{name}.{seg}", main, second)
        d += elm.Line().at((ox + 7.2, oy + y)).to((ox + 8.6, oy + y)).color(
            "#999999")
        note(d, ox + 8.8, oy + y, name.upper(), halign="left")
    # PAD and its wires.
    d += elm.Dot(open=True).at((ox + 0.6, oy + 3)).label(
        f"PAD {sign}", loc="left")
    d += elm.Line().at((ox + 0.6, oy + 3)).to((ox + 1.5, oy + 3)).color(
        HOT).linewidth(3.2)
    d += style(elm.Line().at((ox + 1.5, oy + 3)).to((ox + 3.5, oy + 3)),
               "pad.b", main, second)
    # Drain diodes of the output drivers.
    d += style(elm.Diode().up().at((ox + 1.5, oy + 3)).to((ox + 1.5, oy + 6)),
               "dp", main, second)
    d += style(elm.Diode().up().at((ox + 1.5, oy)).to((ox + 1.5, oy + 3)),
               "dn", main, second)
    note(d, ox + 1.1, oy + 4.5, "PMOS\ndrain", halign="right")
    note(d, ox + 1.1, oy + 1.5, "NMOS\ndrain", halign="right")
    # Output NMOS, which snaps back from PAD to DVSS.
    for y0, y1 in ((3.0, 2.3), (1.0, 0.0)):
        d += style(elm.Line().at((ox + 3.5, oy + y0)).to((ox + 3.5, oy + y1)),
                   "nmos", main, second)
    box(d, ox + 2.3, oy + 0.8, ox + 4.7, oy + 2.3, "output\nNMOS",
        color=SECOND if "nmos" in second else "#999999",
        ls="--" if "nmos" in second else "-")
    # Rail clamp.
    for y0, y1 in ((6.0, 4.0), (2.0, 0.0)):
        d += style(elm.Line().at((ox + 7.2, oy + y0)).to((ox + 7.2, oy + y1)),
                   "clamp", main, second)
    box(d, ox + 6.0, oy + 2.0, ox + 8.4, oy + 4.0, "rail\nclamp",
        color=HOT if "clamp" in main else "#999999")
    # The tester's ground on one rail; the other floats.
    gy = 6.0 if ground == "DVDD" else 0.0
    d += elm.Ground().at((ox + 0.6, oy + gy))
    if note2:
        note(d, ox + 2.0, oy + 4.6 if "PMOS" in note2 else oy - 1.0, note2,
             color=SECOND, halign="left")


def main():
    with schemdraw.Drawing(show=False, fontsize=18) as d:
        for k, mode in enumerate(MODES):
            panel(d, (k % 2) * 13.0, -(k // 2) * 10.4, mode)
        extent(d, -1.8, 24.6, -11.6)
        note(d, 0.2, -12.0, "thick red: the main path; dashed orange: a "
             "second path\nat higher voltage", color=GREY, halign="left")
        OUT.mkdir(exist_ok=True)
        d.save(str(OUT / "paths.svg"))


if __name__ == "__main__":
    main()
