"""Draw the remaining schematic figures for the high-voltage pages.

discrete-stack.svg  ten packaged diodes in series on a board.
edge-remedies.svg   plan views of a well's corner and of a P+ region near
                    its edge, each in two variants.
barrier.svg         a signal crossing an insulator by capacitors or coils.
level-up.svg        the mirror-image metal-gate transistor in a floating
                    N-well.
sensors.svg         four ways to sense a high voltage.

The drawings are schematic. figures.py calls this module; it writes no
files itself.

SPDX-License-Identifier: Apache-2.0
"""

from svgdraw import well
from svgdraw import (ARROW, BLUE, DEPL, GREY, INK, METAL, NWELL, OXIDE,
                     POLY, PPLUS, SUB, line, path, polyline, rect, svg, text)

PKG = "#555555"
DIE = "#9cb7d6"


def resistor(x, y1, y2):
    """A vertical zigzag resistor from (x, y1) down to (x, y2)."""
    n, pts = 6, [(x, y1), (x, y1 + 8)]
    step = (y2 - y1 - 16) / n
    for k in range(n):
        pts.append((x + (8 if k % 2 == 0 else -8), y1 + 8 + step * (k + 0.5)))
    pts += [(x, y2 - 8), (x, y2)]
    return polyline(pts, width=1.6)


def capacitor(x, y1, y2):
    m = (y1 + y2) / 2
    return [line(x, y1, x, m - 4), line(x - 12, m - 4, x + 12, m - 4, width=2),
            line(x - 12, m + 4, x + 12, m + 4, width=2), line(x, m + 4, x, y2)]


def diode(x, y, colour=INK):
    """A diode at (x, y) pointing up: cathode above, so a higher voltage
    above reverse-biases it."""
    return [f'<polygon points="{x - 8},{y + 6} {x + 8},{y + 6} {x},{y - 6}" '
            f'fill="{colour}"/>', line(x - 8, y - 6, x + 8, y - 6, width=2,
                                       stroke=colour)]


def ground(x, y):
    return [line(x - 10, y, x + 10, y, width=2),
            line(x - 6, y + 4, x + 6, y + 4, width=1.5),
            line(x - 2, y + 8, x + 2, y + 8, width=1.5)]


def discrete_stack():
    w, h = 640, 240
    body = [ARROW]
    body.append(rect(20, 128, 600, 14, "#cfe3c7"))
    body.append(text(320, 160, "circuit board", size=13, fill=GREY))
    x0, pitch = 56, 54
    body.append(line(20, 100, x0, 100, width=2))
    body.append(line(x0 + 9 * pitch + 40, 100, 620, 100, width=2))
    for k in range(10):
        x = x0 + k * pitch
        body.append(rect(x, 80, 40, 40, PKG, rx=4))
        body.append(rect(x + 7, 89, 26, 22, DIE))
        # Cathode towards the higher voltage on the left: reverse biased.
        body.append(f'<polygon points="{x + 27},93 {x + 27},107 '
                    f'{x + 15},100" fill="{INK}"/>')
        body.append(line(x + 14, 93, x + 14, 107, width=2.5))
        body.append(text(x + 20, 72, "5 V", size=13))
        if k < 9:
            body.append(line(x + 40, 100, x + pitch, 100, width=2))
    body.append(text(20, 92, "50 V", anchor="start", size=14,
                     weight="bold"))
    body.append(text(620, 92, "0 V", anchor="end", size=14, weight="bold"))
    body.append(text(320, 30, "Ten packaged diodes in series, 50 V across "
                     "them", size=15, weight="bold"))
    body.append(text(320, 192, "each die (blue) sits in its own package:",
                     size=13))
    body.append(text(320, 212, "the board's ground touches no die", size=13))
    return svg(w, h, body)


def corner(ox, oy, drawn_r, label):
    """A well's corner in plan view: drawn window and diffused edge."""
    b = []
    d = 22                                    # lateral diffusion ~ depth
    x0, y0 = ox + 20, oy + 40
    b.append(path(f"M{x0 - d},{y0 + 140} L{x0 - d},{y0 + drawn_r} "
                  f"A{drawn_r + d},{drawn_r + d} 0 0 1 {x0 + drawn_r},"
                  f"{y0 - d} L{x0 + 160},{y0 - d} L{x0 + 160},{y0 + 140} Z",
                  stroke=INK, dash=None, fill=NWELL, width=1.5))
    if drawn_r:
        b.append(path(f"M{x0},{y0 + 140} L{x0},{y0 + drawn_r} "
                      f"A{drawn_r},{drawn_r} 0 0 1 {x0 + drawn_r},{y0} "
                      f"L{x0 + 160},{y0}", stroke=GREY, dash="4 3",
                      width=1.2))
    else:
        b.append(polyline([(x0, y0 + 140), (x0, y0), (x0 + 160, y0)],
                          stroke=GREY, dash="4 3", width=1.2))
    b.append(text(ox + 110, oy + 14, label, size=13, weight="bold"))
    return b


def edge_remedies():
    w, h = 660, 480
    body = [ARROW]
    body += corner(10, 30, 0, "Square drawn corner")
    body.append(text(140, 150, "corner radius ≈", size=12))
    body.append(text(140, 166, "the well's depth", size=12))
    body += corner(340, 30, 60, "Rounded drawn corner")
    body.append(text(470, 150, "larger radius:", size=12))
    body.append(text(470, 166, "higher breakdown", size=12))
    body.append(text(330, 230, "dashed: the drawn window; filled: the well "
                     "after diffusion", size=12, fill=GREY))
    # P+ near the edge against P+ set back, in cross-section.
    for k, (gap, title, note) in enumerate((
            (12, "P+ close to the well", "depletion squeezed: higher field"),
            (90, "P+ set back", "the lightly doped substrate takes it"))):
        ox, top = 10 + k * 330, 300
        body.append(text(ox + 155, top - 24, title, size=13, weight="bold"))
        body.append(rect(ox, top, 310, 150, SUB))
        body.append(well(ox, top, 120, 50, NWELL, r=10))
        body.append(text(ox + 60, top + 30, "well, V", size=12))
        xp = ox + 120 + gap
        body.append(rect(xp, top, 40, 16, PPLUS))
        body.append(text(xp + 20, top - 6, "P+, 0 V", size=11))
        reach = min(gap, 70)
        body.append(path(f"M{ox},{top + 110} Q{ox + 112},{top + 110} "
                         f"{ox + 120 + reach * 0.6},{top + 40} "
                         f"L{ox + 120 + reach},{top}"))
        body.append(text(ox + 155, top + 136, note, size=12, fill=DEPL))
    return svg(w, h, body)


def barrier():
    w, h = 640, 330
    body = [ARROW]
    for k, (title, note) in enumerate((
            ("Capacitors", "passes a changing voltage"),
            ("Coils", "passes a changing current"))):
        ox = 20 + k * 320
        body.append(text(ox + 140, 24, title, size=14, weight="bold"))
        xb = ox + 140
        body.append(line(xb, 40, xb, 250, stroke=GREY, dash="6 4", width=2))
        body.append(rect(ox, 90, 70, 110, "#fde9d3", rx=6))
        body.append(text(ox + 35, 140, "trans-", size=12))
        body.append(text(ox + 35, 156, "mitter", size=12))
        body.append(rect(ox + 210, 90, 70, 110, "#e2f0d9", rx=6))
        body.append(text(ox + 245, 140, "receiver", size=12))
        for y in (115, 175):
            body.append(line(ox + 70, y, xb - (8 if k == 0 else 34), y))
            body.append(line(xb + (8 if k == 0 else 34), y, ox + 210, y))
        if k == 0:
            for y in (115, 175):
                body.append(line(xb - 8, y - 14, xb - 8, y + 14, width=2.5))
                body.append(line(xb + 8, y - 14, xb + 8, y + 14, width=2.5))
        else:
            for side in (-1, 1):
                xc = xb + side * 26
                d = "M%g,115 " % (xc - side * 8)
                for j in range(4):
                    y = 115 + j * 15
                    d += (f"Q{xc + side * 10},{y + 7.5} "
                          f"{xc - side * 8},{y + 15} ")
                body.append(path(d, stroke=INK, dash=None, width=1.8))
                body.append(line(xc - side * 8, 175, xc - side * 8, 175))
        body.append(text(xb, 270, "insulator", size=12, fill=GREY))
        body.append(text(xb, 292, note, size=12))
        body.append(text(xb, 310, "no steady current", size=12))
    return svg(w, h, body)


def level_up():
    w, h = 640, 270
    body = [ARROW]
    top = 110
    body.append(rect(20, top, 600, 130, SUB))
    body.append(text(320, top + 118, "P substrate, 0 V", size=13))
    body.append(well(140, top, 360, 80, NWELL, r=14))
    body.append(text(320, top + 66, "N-well of the floating circuit, 40 V",
                     size=12))
    body.append(rect(190, top, 60, 20, PPLUS))
    body.append(rect(390, top, 60, 20, PPLUS))
    body.append(text(220, top + 15, "P+", size=12))
    body.append(text(420, top + 15, "P+", size=12))
    body.append(rect(250, top - 60, 140, 60, OXIDE))
    body.append(text(320, top - 26, "insulator", size=12))
    body.append(rect(250, top - 72, 140, 12, METAL))
    body.append(line(250, top + 3, 390, top + 3, stroke=BLUE, width=4))
    body.append(text(320, top - 82, "plate driven from ground, 0 V or 5 V",
                     size=13, weight="bold"))
    body.append(text(220, top - 10, "source", size=11))
    body.append(text(420, top - 10, "drain", size=11))
    body.append(text(320, top + 20, "inverted channel", size=11,
                     fill=BLUE))
    body.append(path(f"M130,{top} L130,{top + 82} Q130,{top + 92} 144,"
                     f"{top + 92} L496,{top + 92} Q510,{top + 92} 510,"
                     f"{top + 82} L510,{top}", stroke=DEPL, dash="5 3",
                     width=2))
    body.append(text(520, top + 106, "this junction still", anchor="start",
                     size=11, fill=DEPL))
    body.append(text(520, top + 120, "holds the 40 V", anchor="start",
                     size=11, fill=DEPL))
    return svg(w, h, body)


def sensor_cell(ox, oy, kind):
    b = []
    hv = (ox + 60, oy + 30)
    b.append(f'<circle cx="{hv[0]}" cy="{hv[1]}" r="4" fill="{INK}"/>')
    b.append(text(hv[0] - 10, hv[1] + 4, "57 V node", anchor="end", size=11))
    x = hv[0]
    if kind == "res":
        title = "Resistor divider"
        b += [resistor(x, oy + 30, oy + 90), resistor(x, oy + 90, oy + 150)]
        b.append(line(x, oy + 90, x + 50, oy + 90))
        b += ground(x, oy + 150)
        notes = ("a DC reading,", "but it draws current:", "57 µW at 1 µA")
    elif kind == "cap":
        title = "Capacitor divider"
        b += capacitor(x, oy + 30, oy + 90) + capacitor(x, oy + 90, oy + 150)
        b += ground(x, oy + 150)
        b.append(line(x, oy + 90, x + 50, oy + 90))
        b.append(rect(x + 50, oy + 82, 26, 16, POLY))
        b.append(text(x + 6, oy + 80, "floating node", anchor="start",
                      size=10, fill=DEPL))
        b.append(text(x + 63, oy + 112, "gate", size=10))
        notes = ("no current, but no DC:", "the middle node's charge",
                 "leaks and starts unknown")
    elif kind == "stack":
        title = "Junction-device stack"
        b.append(line(x, oy + 30, x, oy + 150))
        for y in (50, 80, 110, 140):
            b += diode(x, oy + y)
        b += ground(x, oy + 152)
        notes = ("every node also faces", "the substrate: the",
                 "substrate limit")
    else:
        title = "Metal-gate transistor"
        b.append(line(x, oy + 30, x, oy + 60))
        b.append(rect(x - 30, oy + 60, 60, 8, METAL))
        b.append(rect(x - 30, oy + 68, 60, 40, OXIDE))
        b.append(line(x - 30, oy + 112, x + 30, oy + 112, stroke=BLUE,
                      width=4))
        b.append(text(x, oy + 92, "insulator", size=10))
        b.append(text(x, oy + 132, "source, drain", size=10))
        b.append(text(x, oy + 146, "at low voltage", size=10))
        notes = ("a DC reading with", "no current from the node;",
                 "its threshold is measured")
    b.insert(0, text(ox + 150, oy + 6, title, size=13, weight="bold"))
    for k, s in enumerate(notes):
        b.append(text(ox + 160, oy + 70 + k * 16, s, anchor="start",
                      size=12))
    return b


def sensors():
    w, h = 640, 400
    body = []
    for k, kind in enumerate(("res", "cap", "stack", "metal")):
        body += sensor_cell(10 + (k % 2) * 320, 20 + (k // 2) * 195, kind)
    body.append(line(320, 10, 320, 390, stroke="#dddddd", width=1))
    body.append(line(10, 205, 630, 205, stroke="#dddddd", width=1))
    return svg(w, h, body)


FIGURES = {"discrete-stack.svg": discrete_stack,
           "edge-remedies.svg": edge_remedies, "barrier.svg": barrier,
           "level-up.svg": level_up, "sensors.svg": sensors}
