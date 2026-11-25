# /// script
# requires-python = ">=3.10"
# ///
"""Draw the polarity bridge schematics of the Power over Ethernet pages.
Run with:

    uv run docs/power/poe/drawings_pd.py

Writes:

bridges.svg
    Two full-wave bridges, one per pair set, joined into VDD and VSS, with
    the current path for one polarity (powered-device.rst).
active-bridge.svg
    The same bridge built from transistors on chip, with the substrate tied
    to the most negative rectified node, for both polarities
    (hv-options.rst).

SPDX-License-Identifier: Apache-2.0
"""

from svgfig import (EVP, GREY, INK, POWER, SRC_INK, box, diode, dot, line,
                    svg, text, wire, write)

HOP = 5


def hop_h(x1, x2, y, xs, stroke=INK, width=1.4):
    """A horizontal wire from x1 to x2 that hops over verticals at xs."""
    d = f"M{x1:.1f},{y:.1f} "
    for xc in sorted(xs):
        d += (f"L{xc - HOP:.1f},{y:.1f} A{HOP},{HOP} 0 0 1 "
              f"{xc + HOP:.1f},{y:.1f} ")
    d += f"L{x2:.1f},{y:.1f}"
    return (f'<path d="{d}" fill="none" stroke="{stroke}" '
            f'stroke-width="{width}"/>')


def bridge(xa, xb, y_top, y_bot, flip, hot=None, sym=diode):
    """One bridge of two legs at xa and xb between two rails.

    flip=False: VDD on y_top, VSS on y_bot, diodes conduct upwards.
    flip=True: VSS on y_top, VDD on y_bot, diodes conduct downwards.
    hot is a set of (leg, "upper" or "lower") drawn in the path colour.
    Returns the drawing and the node y of each leg."""
    out = []
    hot = hot or set()
    nodes = {}
    for leg, (x, frac) in enumerate(((xa, 0.42), (xb, 0.58))):
        yn = y_top + (y_bot - y_top) * frac
        nodes[leg] = yn
        yu = (y_top + yn) / 2
        yl = (yn + y_bot) / 2
        cu = SRC_INK if (leg, "upper") in hot else INK
        cl = SRC_INK if (leg, "lower") in hot else INK
        wu = 2.4 if cu == SRC_INK else 1.4
        wl = 2.4 if cl == SRC_INK else 1.4
        out.append(line(x, y_top, x, yu - 9, cu, wu))
        out.append(line(x, yu + 9, x, yn, cu, wu))
        out.append(line(x, yn, x, yl - 9, cl, wl))
        out.append(line(x, yl + 9, x, y_bot, cl, wl))
        direction = "down" if flip else "up"
        out += sym(x, yu, direction, stroke=cu, fill=cu)
        out += sym(x, yl, direction, stroke=cl, fill=cl)
        out.append(dot(x, yn, 3))
    return out, nodes


def bridges():
    body = []
    xa, xb = 250, 340
    xs, xd = 520, 640            # VSS bus and VDD bus
    # Bridge A: VDD on top.
    ya_t, ya_b = 50, 210
    hot = {(0, "upper"), (1, "lower")}
    d, na = bridge(xa, xb, ya_t, ya_b, False, hot)
    body += d
    body.append(wire([(xa, ya_t), (xd, ya_t)], SRC_INK, 2.4))
    body.append(wire([(xa, ya_b), (xs, ya_b)], SRC_INK, 2.4))
    # Bridge B: VSS on top, drawn upside down so the buses do not cross.
    yb_t, yb_b = 270, 430
    d, nb = bridge(xa, xb, yb_t, yb_b, True)
    body += d
    body.append(wire([(xa, yb_t), (xs, yb_t)]))
    body.append(wire([(xa, yb_b), (xd, yb_b)]))
    # Buses and the load.
    body.append(wire([(xd, ya_t), (xd, 240)], SRC_INK, 2.4))
    body.append(wire([(xd, 240), (xd, yb_b)]))
    body.append(wire([(xs, ya_b), (xs, 240)], SRC_INK, 2.4))
    body.append(wire([(xs, 240), (xs, yb_t)]))
    body.append(line(xs, 240, 530, 240, SRC_INK, 2.4))
    body.append(line(630, 240, xd, 240, SRC_INK, 2.4))
    body.append(dot(xd, 240, 3))
    body.append(dot(xs, 240, 3))
    body.append(text(xd - 6, ya_t - 6, "VDD", 12, "end", "bold"))
    body.append(text(xs - 6, ya_b - 6, "VSS", 12, "end", "bold"))
    body += box(530, 218, 100, 44, "signature,\nclass, switch", POWER, 10)
    # Inputs from the centre taps.
    inputs = [("pins 1, 2", na[0], xa, [], SRC_INK),
              ("pins 3, 6", na[1], xb, [xa], SRC_INK),
              ("pins 4, 5", nb[0], xa, [], INK),
              ("pins 7, 8", nb[1], xb, [xa], INK)]
    for label, y, x, hops, col in inputs:
        w = 2.4 if col == SRC_INK else 1.4
        body.append(hop_h(150, x, y, hops, col, w))
        body.append(text(144, y + 4, label, 11, "end"))
    body.append(text(10, 30, "Mode A", 12, "start", "bold"))
    body.append(text(10, 250, "Mode B", 12, "start", "bold"))
    body.append(text(10, 46, "(either polarity)", 10, fill=GREY))
    body.append(text(10, 266, "(either polarity)", 10, fill=GREY))
    body.append(text(10, 470, "Highlighted: the path with pins 1, 2 "
                     "positive. With pins 3, 6 positive the other two "
                     "diodes", 11, fill=GREY))
    body.append(text(10, 486, "of bridge A conduct. Bridge B carries the "
                     "current when Mode B is powered.", 11, fill=GREY))
    return svg(680, 498, body, "Polarity bridges")


def mosfet(x, y, direction="up", stroke=INK, fill=INK):
    """A transistor drawn as a box with a body diode, in place of a diode."""
    from svgfig import rect
    out = [rect(x - 11, y - 9, 22, 18, "#ffffff", stroke, 1.2, rx=2)]
    out += diode(x, y, direction, 5, stroke, fill)
    return out


def active_bridge():
    body = []
    panels = (("pins 1, 2 positive", 30, {(0, "upper"), (1, "lower")}, 1),
              ("pins 3, 6 positive", 370, {(1, "upper"), (0, "lower")}, 0))
    for title, x0, hot, neg in panels:
        xa, xb = x0 + 90, x0 + 170
        yt, yb = 60, 230
        body.append(text(x0 + 140, 22, title, 12, "middle", "bold"))
        d, nodes = bridge(xa, xb, yt, yb, False, hot, mosfet)
        body += d
        body.append(wire([(xa, yt), (x0 + 270, yt)], SRC_INK, 2.4))
        body.append(wire([(xa, yb), (x0 + 270, yb)], SRC_INK, 2.4))
        body.append(text(x0 + 274, yt + 4, "VDD", 11, "start", "bold"))
        body.append(text(x0 + 274, yb + 4, "VSS", 11, "start", "bold"))
        body.append(hop_h(x0 + 30, xa, nodes[0], [], INK))
        body.append(hop_h(x0 + 30, xb, nodes[1], [xa], INK))
        body.append(text(x0 + 26, nodes[0] + 4, "1, 2", 10, "end"))
        body.append(text(x0 + 26, nodes[1] + 4, "3, 6", 10, "end"))
        # The substrate follows VSS, which is the negative input pair.
        body.append(box(x0 + 40, 262, 230, 34,
                        "substrate at VSS", EVP, 11)[0])
        body += box(x0 + 40, 262, 230, 34, "substrate at VSS", EVP, 11)[1:]
        body.append(line(x0 + 200, yb, x0 + 200, 262, INK, 1.4, "4,3"))
        neg_pins = "3, 6" if neg else "1, 2"
        body.append(text(x0 + 155, 318, f"VSS is joined to pins {neg_pins}",
                         10, "middle", fill=GREY))
    body.append(text(10, 350, "Boxes: transistors switched on as "
                     "rectifiers, with the direction each conducts. "
                     "Highlighted: the", 11, fill=GREY))
    body.append(text(10, 366, "conducting path. The substrate stays at "
                     "VSS, which is a different cable pair in each "
                     "polarity.", 11, fill=GREY))
    return svg(680, 378, body, "Active bridge")


if __name__ == "__main__":
    write("bridges.svg", bridges())
    write("active-bridge.svg", active_bridge())
