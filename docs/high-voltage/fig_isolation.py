"""Draw the isolation cross-sections for the substrate and insulator pages.

dnw-stack.svg    the series stack with each transistor in its own deep
                 N-well, drawn like stack-section.svg.
poly-on-fox.svg  polysilicon diodes on the field oxide, and the inversion
                 that polysilicon at tens of volts causes beneath it.
oxide-isolation.svg  bulk silicon, silicon on insulator and a bulk die
                 with its substrate removed, side by side.

The drawings are schematic. figures.py calls this module; it writes no
files itself.

SPDX-License-Identifier: Apache-2.0
"""

from svgdraw import well
from svgdraw import (ARROW, BLUE, DEPL, FOX, INK, NPLUS, NWELL, OXIDE,
                     POLY, PPLUS, SUB, line, path, rect, svg, text)

PWELL = "#b9cfe8"
CARRIER = "#d9d2c3"


def dnw_stack():
    w, h = 640, 320
    body = [ARROW]
    body.append(rect(20, 110, 600, 170, SUB))
    body.append(text(320, 268, "P-type substrate, 0 V", size=14))
    n, x0, pitch, ww = 10, 30, 59, 50
    for k in range(n):
        x = x0 + k * pitch
        v = 50 - 5 * k
        body.append(well(x, 110, ww, 62, NWELL, r=8))
        body.append(well(x + 8, 110, ww - 16, 26, PWELL, r=4))
        body.append(text(x + ww / 2, 158, f"{v} V", size=13))
        if k < n - 1:
            body.append(text(x + ww / 2 + pitch / 2, 84, "5 V", size=11))
            body.append(f'<path d="M{x + ww / 2},104 '
                        f'Q{x + pitch / 2 + ww / 2},'
                        f'84 {x + pitch + ww / 2},104" stroke="{INK}" '
                        f'stroke-width="1.2" fill="none"/>')
    body.append(text(320, 30, "Each transistor in its own deep N-well",
                     size=14, weight="bold"))
    body.append(text(320, 50, "(blue: the P-well holding the transistor; "
                     "orange: its deep N-well)", size=12))
    # The weak point: the top deep N-well's junction with the substrate.
    xt = x0 + ww / 2
    body.append(path(f"M{x0 - 4},114 L{x0 - 4},168 Q{x0 - 4},176 {x0 + 4},176 "
                     f"L{x0 + ww - 4},176 "
                     f"Q{x0 + ww + 4},176 {x0 + ww + 4},168 "
                     f"L{x0 + ww + 4},114", stroke=DEPL, dash="5 3",
                     width=2.2))
    body.append(line(xt, 184, xt, 222, marker=True))
    body.append(text(xt + 10, 205, "50 V across the deep N-well's junction "
                     "to the substrate:", anchor="start", size=13,
                     weight="bold"))
    body.append(text(xt + 10, 222, "the model breaks down at about 31 V",
                     anchor="start", size=13, weight="bold"))
    body.append(text(320, 306, "The P-well to deep N-well junctions hold "
                     "little; each deep N-well still faces the substrate",
                     size=13))
    return svg(w, h, body)


def strip(x, y, n, wseg, labels):
    """A polysilicon strip of alternating P and N segments."""
    b = []
    for k in range(n):
        fill = PPLUS if k % 2 == 0 else NPLUS
        b.append(rect(x + k * wseg, y, wseg, 16, fill))
        b.append(text(x + k * wseg + wseg / 2, y + 12,
                      "P" if k % 2 == 0 else "N", size=11))
    for xx, s in labels:
        b.append(text(xx, y - 6, s, size=12))
    return b


def poly_on_fox():
    w, h = 640, 490
    body = [ARROW]
    # (a) Polysilicon diodes on the field oxide.
    body.append(text(20, 24, "(a) Polysilicon diodes on the field oxide",
                     anchor="start", size=14, weight="bold"))
    body.append(rect(20, 100, 600, 100, SUB))
    body.append(text(320, 188, "P substrate, 0 V", size=13))
    body.append(rect(60, 84, 520, 18, FOX))
    body += strip(80, 68, 12, 40, [(80, "57 V"), (560, "0 V")])
    body.append(text(320, 50, "a polysilicon strip: the voltage steps along "
                     "it at its P-N junctions", size=13))
    body.append(line(300, 116, 300, 104, marker=True, width=1.2))
    body.append(text(310, 124, "field oxide holds the whole voltage to the "
                     "substrate:", anchor="start", size=12))
    body.append(text(310, 140, "0.31 µm equivalent, 1.83 MV/cm at 57 V",
                     anchor="start", size=12))
    body.append(text(80, 98, "field oxide", anchor="start", size=11))
    # (b) Inversion under polysilicon at tens of volts, and a P+ cut.
    y0 = 260
    body.append(text(20, y0 - 20, "(b) Polysilicon at tens of volts inverts "
                     "the silicon under it", anchor="start", size=14,
                     weight="bold"))
    for k, (ox, cut) in enumerate(((20, False), (330, True))):
        body.append(rect(ox, y0 + 40, 290, 150, SUB))
        body.append(rect(ox + 20, y0 + 40, 50, 20, NPLUS))
        body.append(rect(ox + 220, y0 + 40, 50, 20, NPLUS))
        body.append(text(ox + 45, y0 + 80, "N, 0 V", size=12))
        body.append(text(ox + 245, y0 + 80, "N, 5 V", size=12))
        body.append(rect(ox + 50, y0 + 28, 190, 12, FOX))
        body.append(rect(ox + 60, y0 + 12, 170, 16, POLY))
        body.append(text(ox + 145, y0 + 25, "polysilicon at 40 V", size=11))
        if cut:
            body.append(f'<path d="M{ox + 70},{y0 + 42} L{ox + 125},'
                        f'{y0 + 42}" stroke="{BLUE}" stroke-width="4"/>')
            body.append(f'<path d="M{ox + 165},{y0 + 42} L{ox + 220},'
                        f'{y0 + 42}" stroke="{BLUE}" stroke-width="4"/>')
            body.append(rect(ox + 127, y0 + 40, 36, 18, "#5b8cc7"))
            body.append(text(ox + 145, y0 + 76, "P+ cut", size=12,
                             weight="bold"))
            body.append(text(ox + 145, y0 + 130, "the P+ stops the", size=12))
            body.append(text(ox + 145, y0 + 146, "inversion: no path",
                             size=12))
        else:
            body.append(f'<path d="M{ox + 70},{y0 + 42} L{ox + 220},'
                        f'{y0 + 42}" stroke="{BLUE}" stroke-width="4"/>')
            body.append(text(ox + 145, y0 + 130, "inversion layer joins",
                             size=12))
            body.append(text(ox + 145, y0 + 146, "the two N regions",
                             size=12))
        body.append(text(ox + 145, y0 + 180, "P substrate, 0 V", size=12))
    body.append(line(40, y0 + 210, 64, y0 + 210, stroke=BLUE, width=4))
    body.append(text(72, y0 + 214, "inversion layer of electrons",
                     anchor="start", size=12))
    return svg(w, h, body)


def labels(y, lines):
    """A bold title and plain lines beside a cross-section."""
    b = [text(268, y + 22, lines[0], anchor="start", size=16,
              weight="bold")]
    for k, s in enumerate(lines[1:]):
        b.append(text(268, y + 48 + k * 20, s, anchor="start", size=15))
    return b


def islands(y, h, top_oxide):
    """Three silicon islands at their own voltages, with oxide between
    them from y to y + h; top_oxide is the depth of oxide at the surface
    if the trenches below it are a separate, later fill."""
    b = []
    for k, v in enumerate(("0 V", "25 V", "50 V")):
        x = 22 + k * 80
        b.append(rect(x, y, 68, h, NWELL))
        b.append(text(x + 34, y + h / 2 + 6, v, size=15))
    for x in (10, 90, 170, 250):
        b.append(rect(x - 2, y, 14, h, OXIDE))
        if top_oxide:
            b.append(rect(x - 2, y, 14, top_oxide, "#bdbdbd"))
    return b


def oxide_isolation():
    w, h = 480, 600
    body = [ARROW]
    # Bulk silicon: junctions to one shared substrate.
    y = 20
    body.append(rect(10, y, 240, 150, SUB))
    body.append(well(30, y, 80, 46, NWELL, r=10))
    body.append(well(150, y, 80, 46, NWELL, r=10))
    body.append(text(70, y + 28, "0 V", size=15))
    body.append(text(190, y + 28, "50 V", size=15))
    body.append(line(190, y + 50, 190, y + 100, marker=True))
    body.append(text(130, y + 136, "P substrate, 0 V", size=15))
    body += labels(y, ("Bulk silicon", "junctions to one", "shared substrate",
                       "hold the voltage"))
    # Silicon on insulator.
    y = 210
    body += islands(y, 46, 0)
    body.append(rect(8, y + 46, 254, 20, OXIDE))
    body.append(text(135, y + 61, "buried oxide", size=14))
    body.append(rect(8, y + 66, 254, 84, SUB))
    body.append(text(135, y + 114, "handle wafer", size=15))
    body += labels(y, ("Silicon on insulator", "trenches and the",
                       "buried oxide hold", "the voltage"))
    # Thinned bulk die.
    y = 400
    body += islands(y, 62, 12)
    body.append(rect(8, y + 62, 254, 18, OXIDE))
    body.append(rect(8, y + 80, 254, 70, CARRIER))
    body.append(text(135, y + 120, "insulating carrier", size=15))
    body += labels(y, ("Thinned bulk die", "trenches etched from",
                       "the back stop on the", "shallow trench",
                       "isolation (dark grey)"))
    body.append(text(10, y + 176, "the dielectric under the islands is "
                     "added after thinning", anchor="start", size=14,
                     fill="#555555"))
    return svg(w, h, body)


FIGURES = {"dnw-stack.svg": dnw_stack, "poly-on-fox.svg": poly_on_fox,
           "oxide-isolation.svg": oxide_isolation}
