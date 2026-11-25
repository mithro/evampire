"""Draw the at-a-glance diagram of evampire as an SVG file.

The figure shows the main blocks of a board built around evampire and how
data and power flow between them. Data runs along the top row and power along
the bottom row, each in a straight line from Ethernet port A to port B. The
first-version chip is drawn as a die with a ring of bond pads; a pad filled in
a signal's colour marks where that signal leaves the chip. A dashed outline
marks the chip in the full design, which also holds the transceivers and the
power stages, except possibly some high-voltage switches. The power bus stays
on the board, so the dashed outline has a hole around it.

The speeds, protocols and voltages written on the figure come from these
pages, which are the place to change them:

- 10, 100 and 1000 Mbit/s on every port, both ports at the same speed:
  requirements.rst.
- RGMII clock up to 125 MHz (25 MHz and 2.5 MHz at the slower speeds):
  architecture/index.rst and ethernet/rgmii/port-logic.rst.
- Power stages on the chip in the full design, except possibly some
  high-voltage switches: power/index.rst (tab-power-board-configs).
- Processor network traffic below 1 Mbit/s: index.rst.
- USB 2.0 full speed, 12 Mbit/s, on D+ and D-: requirements.rst.
- USB-PD biphase mark coding on CC, 300 kbit/s: power/usb-pd/cc-signalling.rst.
- PoE 37 V to 57 V at the powered device, 44 V to 57 V from the power
  sourcing equipment, and VBUS 5 V to 20 V, up to 48 V in the extended power
  range: power/index.rst.

Usage: python overview.py OUTPUT.svg

SPDX-License-Identifier: Apache-2.0
"""

import sys

W, H = 944, 704

# Colours: one per kind of connection, a tint of each for the blocks it
# connects, and neutral colours for the silicon and text.
INK = "#1d2433"
MUTED = "#5b6577"
DATA, DATA_TINT, DATA_EDGE = "#1c64d4", "#eaf1fd", "#9dbcef"
POWER, POWER_TINT, POWER_EDGE = "#f2620c", "#fff2e8", "#f8b48a"
CTRL, CTRL_TINT, CTRL_EDGE = "#6b46d6", "#f2eefd", "#c2b2f0"
SILICON, DIE_FILL, PAD = "#2b3445", "#f7f8fb", "#cfd5df"

FONT = ("-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, "
        "sans-serif")

# Rows (centre y of each row of blocks).
Y_DATA, Y_CPU, Y_IF = 96, 206, 306
Y_POWER, Y_USB, Y_USBC = 446, 556, 656

# Outlines: (left, top, right, bottom).
DIE = (282, 44, 662, 356)
FULL = (90, 18, 846, 604)
BUS = (310, Y_POWER - 30, 488, Y_POWER + 30)   # the power bus, on the board
BUS_HOLE = (BUS[0] - 8, BUS[1] - 8, BUS[2] + 8, BUS[3] + 8)

# Board connectors: (left, top, right, bottom).
PORT_A = (12, 56, 80, 486)
PORT_B = (864, 56, 932, 486)
USBC = (300, Y_USBC - 28, 600, Y_USBC + 28)

# The only place where the data and power networks cross: the two USB wires,
# D+ and D- from the serial port and CC from USB-PD, pass over the power row
# between the power bus and the boost converter.
X_DPDM, X_CC = 506, 566
X_PCTRL = 350             # control from power control to the power bus

out = []


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, cls, anchor="middle"):
    out.append(f'<text x="{x:g}" y="{y:g}" class="{cls}" '
               f'text-anchor="{anchor}">{esc(s)}</text>')


def card(cx, cy, w, h, title, detail=None, kind="data"):
    """A block: a rounded box tinted by its kind, with a title and detail."""
    fill, edge = {"data": (DATA_TINT, DATA_EDGE),
                  "ctrl": (CTRL_TINT, CTRL_EDGE),
                  "power": (POWER_TINT, POWER_EDGE)}[kind]
    x, y = cx - w / 2, cy - h / 2
    out.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
               f'rx="8" fill="{fill}" stroke="{edge}" stroke-width="1.25"/>')
    lines = [(t, "title") for t in title] + ([(detail, "detail")]
                                             if detail else [])
    step = {"title": 16, "detail": 15}
    total = sum(step[c] for _, c in lines)
    ty = cy - total / 2 + 12
    for t, c in lines:
        text(cx, ty, t, c)
        ty += step[c]
    return (x, y, x + w, y + h)


def connector(x0, y0, x1, y1):
    out.append(f'<rect x="{x0:g}" y="{y0:g}" width="{x1 - x0:g}" '
               f'height="{y1 - y0:g}" rx="4" fill="#ffffff" stroke="{INK}" '
               f'stroke-width="1.5"/>')


def rj45(cx, cy):
    """Front view of an RJ45 socket: the opening, its latch slot and the
    eight contacts."""
    w, h = 36, 28
    x, y = cx - w / 2, cy - h / 2
    out.append(
        f'<path d="M{x:g} {y:g} h{w} v{h - 7} h-11 v7 h-14 v-7 h-11 z" '
        f'fill="none" stroke="{INK}" stroke-width="1.5" '
        f'stroke-linejoin="round"/>')
    for i in range(8):
        px = x + 6 + i * 3.4
        out.append(f'<line x1="{px:g}" y1="{y + 3:g}" x2="{px:g}" '
                   f'y2="{y + 9:g}" stroke="{INK}" stroke-width="1.2"/>')


def usbc_icon(cx, cy):
    """Front view of a USB Type-C socket: a rounded slot with its tongue."""
    out.append(f'<rect x="{cx - 17:g}" y="{cy - 6:g}" width="34" height="12" '
               f'rx="6" fill="none" stroke="{INK}" stroke-width="1.5"/>')
    out.append(f'<rect x="{cx - 9:g}" y="{cy - 1.5:g}" width="18" '
               f'height="3" rx="1.5" fill="{INK}"/>')


def outline(box, style, colour, width):
    x0, y0, x1, y1 = box
    dash = {"solid": "", "dashed": ' stroke-dasharray="7 5"',
            "dotted": ' stroke-dasharray="1.5 5" stroke-linecap="round"'}
    out.append(f'<rect x="{x0:g}" y="{y0:g}" width="{x1 - x0:g}" '
               f'height="{y1 - y0:g}" rx="14" fill="none" stroke="{colour}" '
               f'stroke-width="{width}"{dash[style]}/>')


def tag_width(label):
    return 7.6 * len(label) + 22


def tag(x, y, label, colour, filled):
    """A tab on an outline that names the stage it marks."""
    w = tag_width(label)
    fill, fg = (colour, "#ffffff") if filled else ("#ffffff", colour)
    out.append(f'<rect x="{x:g}" y="{y - 11:g}" width="{w:g}" height="22" '
               f'rx="11" fill="{fill}" stroke="{colour}" stroke-width="1.5"/>')
    out.append(f'<text x="{x + w / 2:g}" y="{y + 4.5:g}" class="tag" '
               f'text-anchor="middle" fill="{fg}">{esc(label)}</text>')
    return x + w


def line(points, kind, both=False, hop_at=None):
    """An orthogonal line through points, with an arrowhead at the end (and
    the start when both is set). hop_at is the y of a line crossed by a
    vertical segment, drawn as a small half circle."""
    colour, width, dash = {"data": (DATA, 3, ""),
                           "power": (POWER, 4.5, ""),
                           "ctrl": (CTRL, 1.75, ' stroke-dasharray="5 4"')}[kind]
    d = f"M{points[0][0]:g} {points[0][1]:g}"
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if hop_at is not None and x0 == x1 and min(y0, y1) < hop_at < max(
                y0, y1):
            r = 10 if y1 > y0 else -10
            sweep = 1 if y1 > y0 else 0   # the half circle bulges right
            d += (f" V{hop_at - r:g} A10 10 0 0 {sweep} {x0:g} "
                  f"{hop_at + r:g}")
        d += f" L{x1:g} {y1:g}"
    start = f' marker-start="url(#arrow-{kind})"' if both else ""
    out.append(f'<path d="{d}" fill="none" stroke="{colour}" '
               f'stroke-width="{width}"{dash} stroke-linejoin="round"'
               f'{start} marker-end="url(#arrow-{kind})"/>')


def pads(box, signals):
    """Bond pads around the die. signals maps (side, position) to the colour
    of the signal that leaves through that pad. The top edge, which carries
    the die's tag, has no pads."""
    x0, y0, x1, y1 = box
    size, gap, inset = 7, 22, 8

    def pad(cx, cy, colour=None):
        s = size + 3 if colour else size
        out.append(f'<rect x="{cx - s / 2:g}" y="{cy - s / 2:g}" width="{s:g}" '
                   f'height="{s:g}" rx="1.5" fill="{colour or PAD}"/>')

    def free(pos, side):
        return all(abs(pos - p) > gap / 2
                   for (s, p) in signals if s == side)

    xs = [x for x in range(int(x0) + 26, int(x1) - 18, gap)]
    ys = [y for y in range(int(y0) + 26, int(y1) - 18, gap)]
    for x in xs:
        if free(x, "bottom"):
            pad(x, y1 - inset)
    for y in ys:
        if free(y, "left"):
            pad(x0 + inset, y)
        if free(y, "right"):
            pad(x1 - inset, y)
    for (side, pos), colour in signals.items():
        cx, cy = {"left": (x0 + inset, pos), "right": (x1 - inset, pos),
                  "top": (pos, y0 + inset),
                  "bottom": (pos, y1 - inset)}[side]
        pad(cx, cy, colour)


def main(out_path):
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" '
               f'height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">')
    out.append(f"""<style>
  .title {{ font-size: 14px; font-weight: 600; fill: {INK}; }}
  .detail {{ font-size: 12.5px; fill: {MUTED}; }}
  .tag {{ font-size: 12.5px; font-weight: 600; }}
  .port {{ font-size: 14px; font-weight: 600; fill: {INK}; }}
  .note {{ font-size: 12.5px; fill: {MUTED}; }}
  .net {{ font-size: 11.5px; font-weight: 600; }}
</style>""")
    out.append("<defs>")
    for kind, colour, size in (("data", DATA, 9), ("power", POWER, 8),
                               ("ctrl", CTRL, 11)):
        out.append(
            f'<marker id="arrow-{kind}" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="{size * 0.37:g}" markerHeight="{size * 0.37:g}" '
            f'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" '
            f'fill="{colour}"/></marker>')
    out.append("</defs>")
    out.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')

    # Outlines, behind everything else.
    x0, y0, x1, y1 = DIE
    out.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" '
               f'rx="6" fill="{DIE_FILL}" stroke="{SILICON}" '
               f'stroke-width="2.5"/>')
    outline(FULL, "dashed", SILICON, 1.5)
    outline(BUS_HOLE, "dashed", SILICON, 1.5)
    pads(DIE, {("left", Y_DATA): DATA, ("right", Y_DATA): DATA,
               ("bottom", X_PCTRL): CTRL, ("bottom", X_DPDM): DATA,
               ("bottom", X_CC): DATA})

    # Board connectors.
    connector(*PORT_A)
    connector(*PORT_B)
    for box, label, flow, volts in ((PORT_A, "port A", "in", "37–57 V"),
                                    (PORT_B, "port B", "out", "44–57 V")):
        cx = (box[0] + box[2]) / 2
        text(cx, 222, "Ethernet", "port")
        text(cx, 239, label, "port")
        rj45(cx, 272)
        text(cx, 314, f"PoE {flow}", "note")
        text(cx, 330, volts, "note")
    connector(*USBC)
    usbc_icon(332, Y_USBC)
    text(362, Y_USBC - 2, "USB Type-C port", "port", anchor="start")
    text(362, Y_USBC + 15, "VBUS 5–20 V, up to 48 V with EPR", "note",
         anchor="start")

    # Data path along the top row.
    a = card(200, Y_DATA, 136, 58, ["Ethernet", "transceiver A"],
             "10, 100, 1000 Mbit/s")
    hub = card(472, Y_DATA, 168, 58, ["Cut-through hub"],
               "same speed on both ports")
    b = card(744, Y_DATA, 136, 58, ["Ethernet", "transceiver B"],
             "10, 100, 1000 Mbit/s")

    # Processor and its interfaces, along the bottom of the die.
    cpu = card(472, Y_CPU, 200, 56, ["RISC-V processor"],
               "runs the management software", "ctrl")
    pctl = card(350, Y_IF, 110, 64, ["Power", "control"], "measure, limit",
                "ctrl")
    ser = card(472, Y_IF, 110, 64, ["USB 2.0", "serial port"], "12 Mbit/s",
               "ctrl")
    upd = card(594, Y_IF, 110, 64, ["USB-PD"], "BMC, 300 kbit/s", "ctrl")

    # Power path along the bottom row.
    pdev = card(147, Y_POWER, 90, 60, ["Powered", "device"], "PoE input",
                "power")
    buck = card(251, Y_POWER, 74, 60, ["Buck"], "converter", "power")
    bus = BUS
    out.append(f'<rect x="{bus[0]}" y="{bus[1]}" width="{bus[2] - bus[0]}" '
               f'height="{bus[3] - bus[1]}" rx="8" fill="{POWER_TINT}" '
               f'stroke="{POWER}" stroke-width="2"/>')
    text((bus[0] + bus[2]) / 2, Y_POWER - 2, "Power bus", "title")
    text((bus[0] + bus[2]) / 2, Y_POWER + 14, "on the board", "detail")
    boost = card(640, Y_POWER, 80, 60, ["Boost"], "converter", "power")
    pse = card(765, Y_POWER, 122, 60, ["Power sourcing", "equipment"],
               "PoE output", "power")
    sink = card(352, Y_USB, 72, 56, ["VBUS", "sink"], "switch", "power")
    src = card(448, Y_USB, 72, 56, ["VBUS", "source"], "buck-boost", "power")

    # Outline tags, drawn over the outlines.
    label = "evampire chip, first version"
    tag(DIE[2] - 14 - tag_width(label), DIE[1], label, SILICON, True)
    tag(FULL[0] + 14, FULL[1],
        "Full design adds the transceivers and power stages", SILICON, False)
    text(FULL[0] + 16, Y_USB - 6, "Some high-voltage switches", "note",
         anchor="start")
    text(FULL[0] + 16, Y_USB + 10, "may stay external parts", "note",
         anchor="start")

    def net(x, y, s, colour=DATA, anchor="middle"):
        out.append(f'<text x="{x:g}" y="{y:g}" class="net" '
                   f'text-anchor="{anchor}" fill="{colour}">{esc(s)}</text>')

    # Data connections. Top row, left to right.
    line([(PORT_A[2], Y_DATA), (a[0], Y_DATA)], "data", both=True)
    line([(a[2], Y_DATA), (hub[0], Y_DATA)], "data", both=True)
    line([(hub[2], Y_DATA), (b[0], Y_DATA)], "data", both=True)
    line([(b[2], Y_DATA), (PORT_B[0], Y_DATA)], "data", both=True)
    for x in ((DIE[0] + hub[0]) / 2 + 4, (DIE[2] + hub[2]) / 2 - 4):
        net(x, Y_DATA - 9, "RGMII")
        net(x, Y_DATA + 19, "up to 125 MHz")
    # Down to the processor and out to USB.
    line([(472, hub[3]), (472, cpu[1])], "data", both=True)
    net(480, (hub[3] + cpu[1]) / 2 + 4, "frames, below 1 Mbit/s",
        anchor="start")
    line([(472, cpu[3]), (472, ser[1])], "data", both=True)
    line([(556, cpu[3]), (556, upd[1])], "data", both=True)
    line([(X_DPDM, ser[3]), (X_DPDM, USBC[1])], "data", both=True,
         hop_at=Y_POWER)
    line([(X_CC, upd[3]), (X_CC, USBC[1])], "data", both=True,
         hop_at=Y_POWER)
    net(X_DPDM - 6, USBC[1] - 8, "D+, D−", anchor="end")
    net(X_CC - 6, USBC[1] - 8, "CC", anchor="end")

    # Power connections. Bottom row, left to right.
    line([(PORT_A[2], Y_POWER), (pdev[0], Y_POWER)], "power")
    line([(pdev[2], Y_POWER), (buck[0], Y_POWER)], "power")
    line([(buck[2], Y_POWER), (bus[0], Y_POWER)], "power")
    line([(bus[2], Y_POWER), (boost[0], Y_POWER)], "power")
    line([(boost[2], Y_POWER), (pse[0], Y_POWER)], "power")
    line([(pse[2], Y_POWER), (PORT_B[0], Y_POWER)], "power")
    # USB Type-C: up through the sink switch, down through the source.
    line([(352, USBC[1]), (352, sink[3])], "power")
    line([(352, sink[1]), (352, bus[3])], "power")
    line([(448, bus[3]), (448, src[1])], "power")
    line([(448, src[3]), (448, USBC[1])], "power")

    # Control.
    line([(X_PCTRL + 36, cpu[3]), (X_PCTRL + 36, pctl[1])], "ctrl")
    line([(X_PCTRL, pctl[3]), (X_PCTRL, bus[1])], "ctrl", both=True)

    # Legend.
    for i, (kind, label) in enumerate((("data", "Data"), ("power", "Power"),
                                       ("ctrl", "Control"))):
        y = 636 + i * 22
        line([(672, y), (716, y)], kind)
        text(728, y + 4, label, "note", anchor="start")

    out.append("</svg>")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
