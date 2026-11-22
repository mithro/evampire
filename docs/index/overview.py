"""Draw the at-a-glance diagram of evampire as an SVG file.

The figure shows the main blocks of a board built around evampire and how
data and power flow between them. Data runs along the top row and power along
the bottom row, each in a straight line from Ethernet port A to port B. The
first-version chip is drawn as a die with a ring of bond pads; a pad filled in
a signal's colour marks where that signal leaves the chip. A dashed outline
marks the chip in the full design, and a dotted outline the power stages
whose place, on the chip or in external parts, is an open question.

Usage: python overview.py OUTPUT.svg

SPDX-License-Identifier: Apache-2.0
"""

import sys

W, H = 936, 704

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
Y_DATA, Y_CPU, Y_IF = 96, 206, 302
Y_POWER, Y_USB, Y_USBC = 446, 556, 652

# Outlines: (left, top, right, bottom).
DIE = (310, 44, 626, 350)
FULL = (134, 18, 802, 366)
STAGES = (110, 396, 828, 604)

# The one place where the data and power networks cross: the USB data line
# passes over the power row between the buck converter and the power bus.
X_USB = 360

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
            r = 10
            d += f" V{hop_at - r:g} A{r} {r} 0 0 1 {x0:g} {hop_at + r:g}"
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

    taken = {pos for (_, pos) in signals}
    xs = [x for x in range(int(x0) + 26, int(x1) - 18, gap)]
    ys = [y for y in range(int(y0) + 26, int(y1) - 18, gap)]
    for x in xs:
        if all(abs(x - t) > gap / 2 for t in taken):
            pad(x, y1 - inset)
    for y in ys:
        if all(abs(y - t) > gap / 2 for t in taken):
            pad(x0 + inset, y)
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
    outline(STAGES, "dotted", POWER, 2.25)
    pads(DIE, {("left", Y_DATA): DATA, ("right", Y_DATA): DATA,
               ("bottom", X_USB): DATA, ("bottom", 548): CTRL})

    # Board connectors.
    connector(16, 56, 92, 486)
    connector(844, 56, 920, 486)
    for cx, label, flow in ((54, "port A", "in"), (882, "port B", "out")):
        text(cx, 232, "Ethernet", "port")
        text(cx, 249, label, "port")
        rj45(cx, 282)
        text(cx, 324, "data and", "note")
        text(cx, 339, f"power {flow}", "note")
    connector(340, Y_USBC - 24, 600, Y_USBC + 24)
    usbc_icon(390, Y_USBC)
    text(484, Y_USBC + 5, "USB Type-C port", "port")

    # Data path along the top row.
    card(220, Y_DATA, 140, 54, ["Ethernet", "transceiver A"])
    card(468, Y_DATA, 168, 54, ["Cut-through hub"],
         "forwards A to B, B to A")
    card(716, Y_DATA, 140, 54, ["Ethernet", "transceiver B"])

    # Processor and its interfaces.
    card(468, Y_CPU, 196, 56, ["RISC-V processor"],
         "runs the management software", "ctrl")
    card(388, Y_IF, 132, 56, ["USB interface"], "serial port, USB-PD",
         "ctrl")
    card(548, Y_IF, 132, 56, ["Power control"], "measures and limits",
         "ctrl")

    # Power path along the bottom row.
    card(178, Y_POWER, 108, 60, ["Powered", "device"], "PoE input", "power")
    card(298, Y_POWER, 84, 60, ["Buck"], "converter", "power")
    x0, y0, x1, y1 = 380, Y_POWER - 30, 576, Y_POWER + 30
    out.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" '
               f'rx="8" fill="{POWER_TINT}" stroke="{POWER}" '
               f'stroke-width="2"/>')
    text(478, Y_POWER - 2, "Power bus", "title")
    text(478, Y_POWER + 14, "on the board", "detail")
    card(644, Y_POWER, 80, 60, ["Boost"], "converter", "power")
    card(766, Y_POWER, 116, 60, ["Power sourcing", "equipment"], "PoE output",
         "power")
    card(428, Y_USB, 84, 56, ["USB-PD", "sink"], "switch", "power")
    card(528, Y_USB, 84, 56, ["USB-PD", "source"], "buck-boost", "power")

    # Outline tags, drawn over the outlines.
    label = "evampire chip, first version"
    tag(DIE[2] - 14 - tag_width(label), DIE[1], label, SILICON, True)
    tag(FULL[0] + 14, FULL[1], "Full design adds the transceivers", SILICON,
        False)
    tag(STAGES[0] + 14, STAGES[1], "Power stages: placement open", POWER,
        False)

    # Data connections.
    line([(92, Y_DATA), (150, Y_DATA)], "data", both=True)
    line([(290, Y_DATA), (384, Y_DATA)], "data", both=True)
    line([(552, Y_DATA), (646, Y_DATA)], "data", both=True)
    line([(786, Y_DATA), (844, Y_DATA)], "data", both=True)
    line([(468, Y_DATA + 27), (468, Y_CPU - 28)], "data", both=True)
    line([(410, Y_CPU + 28), (410, Y_IF - 28)], "data", both=True)
    line([(X_USB, Y_IF + 28), (X_USB, Y_USBC - 24)], "data", both=True,
         hop_at=Y_POWER)
    for x in (351, 585):
        out.append(f'<text x="{x}" y="{Y_DATA - 10}" class="net" '
                   f'text-anchor="middle" fill="{DATA}">RGMII</text>')
    out.append(f'<text x="{X_USB - 10}" y="{Y_USB + 4}" class="net" '
               f'text-anchor="end" fill="{DATA}">D+, D−, CC</text>')

    # Power connections.
    line([(92, Y_POWER), (124, Y_POWER)], "power")
    line([(232, Y_POWER), (256, Y_POWER)], "power")
    line([(340, Y_POWER), (380, Y_POWER)], "power")
    line([(576, Y_POWER), (604, Y_POWER)], "power")
    line([(684, Y_POWER), (708, Y_POWER)], "power")
    line([(824, Y_POWER), (844, Y_POWER)], "power")
    line([(428, Y_USBC - 24), (428, Y_USB + 28)], "power")
    line([(428, Y_USB - 28), (428, Y_POWER + 30)], "power")
    line([(528, Y_POWER + 30), (528, Y_USB - 28)], "power")
    line([(528, Y_USB + 28), (528, Y_USBC - 24)], "power")

    # Control.
    line([(530, Y_CPU + 28), (530, Y_IF - 28)], "ctrl")
    line([(548, Y_IF + 28), (548, STAGES[1])], "ctrl", both=True)

    # Legend.
    for i, (kind, label) in enumerate((("data", "Data"), ("power", "Power"),
                                       ("ctrl", "Control"))):
        y = 634 + i * 22
        line([(668, y), (712, y)], kind)
        text(724, y + 4, label, "note", anchor="start")

    out.append("</svg>")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
