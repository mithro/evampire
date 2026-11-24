"""Draw the metal-gate level-shifter schematic for the metal-gate page.

level-shift.svg shows a floating circuit passing a logic signal down to
ground-referenced circuits through two metal-gate NMOS transistors. Each
transistor is drawn as its plate over the insulator over the channel, so
the reader sees where the floating voltage is held.

figures.py calls this module; it writes no files itself.

SPDX-License-Identifier: Apache-2.0
"""

from svgdraw import (ARROW, BLUE, GREY, INK, METAL, OXIDE, SUB, line,
                     polyline, rect, sub, svg, text)

GND = 330


def transistor(x, mirror):
    """A metal-gate NMOS between x and x + 110: plate, insulator, channel.
    Returns the drawing and the (source, drain) x positions."""
    b = [rect(x, 138, 110, 10, METAL),
         rect(x, 148, 110, 40, OXIDE),
         rect(x, 188, 110, 14, SUB)]
    b.append(line(x, 196, x + 110, 196, stroke=BLUE, width=4))
    b.append(text(x + 55, 172, "insulator", size=12))
    if mirror:
        b.append(text(x + 116, 147, "Metal1 plate", anchor="start", size=12))
    else:
        b.append(text(x - 6, 147, "Metal1 plate", anchor="end", size=12))
    src, drn = (x + 110, x) if mirror else (x, x + 110)
    for px in (src, drn):
        b.append(f'<circle cx="{px}" cy="196" r="3.5" fill="{INK}"/>')
    return b, src, drn


def ground(x):
    return [line(x, GND, x, GND + 8, width=1.5),
            line(x - 10, GND + 8, x + 10, GND + 8, width=2),
            line(x - 6, GND + 12, x + 6, GND + 12, width=1.5)]


def level_shift():
    w, h = 640, 440
    body = [ARROW]
    # The floating circuit and its two outputs.
    body.append(rect(130, 20, 380, 56, "#fde9d3", rx=6))
    body.append(text(320, 42, "floating circuit, 15 V to 40 V above ground",
                     size=14, weight="bold"))
    body.append(text(320, 62, "drives a signal and its complement, "
                     "5 V apart", size=13))
    t1, s1, d1 = transistor(150, False)
    t2, s2, d2 = transistor(380, True)
    body += t1 + t2
    for xg, name in ((205, "signal"), (435, "complement")):
        body.append(line(xg, 76, xg, 138, width=1.5))
        body.append(text(xg + 6, 110, name, anchor="start", size=12))
    # Sources to ground, drains to the ground-referenced comparator.
    body.append(polyline([(s1, 196), (s1 - 30, 196), (s1 - 30, GND)],
                         width=1.5))
    body.append(polyline([(s2, 196), (s2 + 30, 196), (s2 + 30, GND)],
                         width=1.5))
    body += ground(s1 - 30) + ground(s2 + 30)
    body.append(text(s1 - 36, 260, "source", anchor="end", size=12))
    body.append(text(s1 - 36, 276, "0 V", anchor="end", size=12))
    body.append(text(s2 + 36, 260, "source", anchor="start", size=12))
    body.append(text(s2 + 36, 276, "0 V", anchor="start", size=12))
    body.append(polyline([(d1, 196), (d1, 262), (270, 262)], width=1.5))
    body.append(polyline([(d2, 196), (d2, 262), (370, 262)], width=1.5))
    body.append(line(d1, 246, d1, 214, marker=True, width=1.2))
    body.append(line(d2, 246, d2, 214, marker=True, width=1.2))
    body.append(text(d1 - 6, 236, sub("I", "1"), anchor="end", size=13))
    body.append(text(d2 + 8, 236, sub("I", "2"), anchor="start", size=13))
    body.append(rect(270, 236, 100, 52, "#e2f0d9", rx=6))
    body.append(text(320, 256, "comparator", size=12, weight="bold"))
    body.append(text(320, 274, "drains at 1 V", size=12))
    body.append(line(320, 288, 320, 318, marker=True, width=1.5))
    body.append(text(328, 314, "logic out, ground referenced",
                     anchor="start", size=12))
    # What the circuit gives.
    body.append(text(320, 376, sub("I", "1") + "− " + sub("I", "2")
                     + "= (W/L) " + sub("μ", "n") + sub("C", "ox")
                     + "ΔV " + sub("V", "DS") + "= 58.6 µA",
                     size=14, weight="bold"))
    body.append(text(320, 396, "at every floating voltage, for Metal1, "
                     "W/L = 10, ΔV = 5 V and " + sub("V", "DS") + "= 1 V",
                     size=13))
    body.append(text(320, 420, "The floating circuit must stay above both "
                     "thresholds: 11 V typical on Metal1", size=13,
                     fill=GREY))
    return svg(w, h, body)


FIGURES = {"level-shift.svg": level_shift}
