# /// script
# requires-python = ">=3.10"
# ///
"""Draw the cable pair figures of the Power over Ethernet pages. Run with:

    uv run docs/power/poe/drawings_pairs.py

Writes:

pairs.svg
    The power carried as a common-mode voltage on the centre taps of the
    cable-side windings, with the pair sets named at each end
    (basics.rst; IEEE 802.3 Table 145-3).
pair-sets.svg
    2-pair power and 4-pair power side by side (basics.rst; IEEE 802.3
    145.1.3 and 145.2.10.1).

SPDX-License-Identifier: Apache-2.0
"""

from svgfig import (EVP, FAR, GREY, INK, POWER, SRC_INK, box, coil, dot,
                    line, svg, text, wire, write)

PITCH = 34          # spacing of the two wires of a pair
WIRE = {"1": "orange", "3": "green", "4": "blue", "7": "brown"}


def transformer(xc, y1, y2, cable_side):
    """A transformer: data winding, core and cable-side winding.

    cable_side is "right" for the power sourcing end and "left" for the
    powered device end. Returns the drawing and the centre-tap point."""
    out = []
    if cable_side == "right":
        xd, xk, xc_w = xc - 26, xc - 10, xc + 6
        out.append(coil(xd, y1, y2, "right"))
        out.append(coil(xc_w, y1, y2, "left"))
    else:
        xd, xk, xc_w = xc + 26, xc + 10, xc - 6
        out.append(coil(xd, y1, y2, "left"))
        out.append(coil(xc_w, y1, y2, "right"))
    out.append(line(xk - 2, y1, xk - 2, y2, INK, 1.2))
    out.append(line(xk + 2, y1, xk + 2, y2, INK, 1.2))
    return out, xd, xc_w


def pairs():
    body = []
    xl, xr = 150, 530            # transformer centres
    rj_l, rj_r = 215, 465        # RJ45 positions
    rows = [("1", "2", "+"), ("3", "6", "-"), ("4", "5", None),
            ("7", "8", None)]
    top = 92
    ys = []
    y = top
    for k, r in enumerate(rows):
        if k == 2:
            y += 64
        ys.append(y)
        y += PITCH + 46
    bottom = ys[-1] + PITCH
    # Transceivers.
    body += box(8, top - 10, 78, bottom - top + 20,
                "Ethernet\ntrans-\nceiver", "#ffffff", 11)
    body += box(594, top - 10, 78, bottom - top + 20,
                "Ethernet\ntrans-\nceiver", "#ffffff", 11)
    # RJ45 planes.
    for x, anchor, dx in ((rj_l, "end", -4), (rj_r, "start", 4)):
        body.append(line(x, 26, x, bottom + 12, GREY, 1.0, "4,3"))
        body.append(text(x + dx, 52, "RJ45", 10, anchor, fill=GREY))
    body.append(text(xl - 10, 18, "Power sourcing equipment", 12, "middle",
                     "bold", SRC_INK))
    body.append(text(xr + 10, 18, "Powered device", 12, "middle", "bold",
                     SRC_INK))
    body.append(text(340, 18, "cable", 12, "middle", fill=GREY))
    taps_l, taps_r = [], []
    for (pa, pb, pol), y1 in zip(rows, ys):
        y2 = y1 + PITCH
        ym = (y1 + y2) / 2
        tl, xd_l, xw_l = transformer(xl, y1, y2, "right")
        tr, xd_r, xw_r = transformer(xr, y1, y2, "left")
        body += tl + tr
        # Data side, to the transceivers.
        for yy in (y1, y2):
            body.append(line(86, yy, xd_l, yy, INK, 1.2))
            body.append(line(xd_r, yy, 594, yy, INK, 1.2))
        # Cable wires.
        powered = pol is not None
        w = 2.4 if powered else 1.2
        col = INK if powered else GREY
        for yy, pin in ((y1, pa), (y2, pb)):
            body.append(line(xw_l, yy, xw_r, yy, col, w))
            body.append(text(rj_l + 4, yy - 4, pin, 10, "start", fill=GREY))
            body.append(text(rj_r - 4, yy - 4, pin, 10, "end", fill=GREY))
        body.append(text(rj_l + 20, ym + 4, f"{WIRE[pa]} pair", 10,
                         "start", fill=GREY))
        if powered:
            dc = "DC" if pol == "+" else "0 V"
            body.append(text(340, y1 - 5, f"{dc} + data/2", 10, "middle"))
            body.append(text(340, y2 + 14, f"{dc} − data/2", 10, "middle"))
        # Centre taps, drawn out between the core and the cable winding.
        body.append(dot(xw_l, ym, 2.5))
        body.append(dot(xw_r, ym, 2.5))
        taps_l.append((xw_l, ym, pol))
        taps_r.append((xw_r, ym, pol))
    body.append(text(30, top - 20, "data only", 10, "start", fill=GREY))
    body.append(text(650, top - 20, "data only", 10, "end", fill=GREY))
    # Pair set labels.
    for k, (label_a, label_m, pins) in enumerate((
            ("Alternative A", "Mode A", "pins 1, 2, 3, 6"),
            ("Alternative B", "Mode B", "pins 4, 5, 7, 8: idle here"))):
        yl = ys[2 * k] - 44
        body.append(text(rj_l + 6, yl, label_a, 11, "start", "bold"))
        body.append(text(rj_r - 6, yl, label_m, 11, "end", "bold"))
        body.append(text(340, yl + 13, pins, 10, "middle", fill=GREY))
    # Power sourcing supply and powered-device bridges.
    yb = bottom + 40
    xp, xn = 176, 192
    body += box(100, yb, 112, 44, "Supply\n44–57 V", POWER, 11)
    body += box(468, yb, 112, 44, "Polarity\nbridges", POWER, 11)
    for (x, y, pol) in taps_l:
        if pol == "+":
            body.append(wire([(x, y), (xp, y), (xp, yb)], INK, 1.8))
        elif pol == "-":
            body.append(wire([(x, y), (xn, y), (xn, yb)], INK, 1.8))
        else:
            body.append(line(x, y, x + 10, y, GREY, 1.0))
    body.append(text(xp - 4, yb - 6, "+", 12, "end"))
    body.append(text(xn + 4, yb - 6, "−", 12, "start"))
    xa, xb = 504, 488
    for (x, y, pol) in taps_r:
        if pol == "+":
            body.append(wire([(x, y), (xa, y), (xa, yb)], INK, 1.8))
        elif pol == "-":
            body.append(wire([(x, y), (xb, y), (xb, yb)], INK, 1.8))
        else:
            body.append(line(x, y, x - 10, y, GREY, 1.0))
    body.append(text(340, yb + 26, "DC on the centre taps", 11, "middle",
                     fill=GREY))
    return svg(680, int(yb + 56), body, "Power over Ethernet pairs")


def pair_sets():
    body = []
    panels = (("2-pair power: one pair set", 10, False),
              ("4-pair power: both pair sets", 350, True))
    for title, x0, four in panels:
        body.append(text(x0 + 160, 20, title, 12, "middle", "bold"))
        body += box(x0, 40, 70, 230, "Power\nsourcing\nequip-\nment", FAR,
                    11)
        body += box(x0 + 250, 40, 70, 230, "Powered\ndevice", FAR, 11)
        sets = (("A", 1, 2, 3, 6), ("B", 4, 5, 7, 8))
        y = 80
        for name, a, b, c, d in sets:
            powered = name == "A" or four
            for k, (p1, p2, pol) in enumerate(((a, b, "+"), (c, d, "−"))):
                yy = y + k * 46
                col = INK if powered else GREY
                wdt = 2.6 if powered else 1.2
                for dy in (0, 10):
                    body.append(line(x0 + 70, yy + dy, x0 + 250, yy + dy,
                                     col, wdt))
                lab = f"pins {p1}, {p2}"
                if powered:
                    lab += f": {pol} and data"
                else:
                    lab += ": data only"
                body.append(text(x0 + 160, yy - 5, lab, 10, "middle",
                                 fill=INK if powered else GREY))
            body.append(text(x0 + 160, y - 24, f"pair set {name}", 11,
                             "middle", fill=GREY))
            y += 116
        note = ("Types 1 to 4, classes 1 to 4" if not four
                else "Types 3 and 4; needed for classes 5 to 8")
        body.append(text(x0 + 160, 292, note, 11, "middle"))
    return svg(680, 304, body, "2-pair and 4-pair power")


if __name__ == "__main__":
    write("pairs.svg", pairs())
    write("pair-sets.svg", pair_sets())
