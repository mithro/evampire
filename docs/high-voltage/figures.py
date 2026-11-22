"""Draw the cross-section figures for the "High voltage above the substrate"
pages as SVG files.

Usage: python figures.py OUTPUT-DIRECTORY

Writes stack-section.svg, grading.svg and metal-gate.svg. The drawings are schematic: shapes
and spacings are not to scale.

SPDX-License-Identifier: Apache-2.0
"""

import pathlib
import sys

SUB = "#dbe8f5"        # P-type substrate
NWELL = "#fbd9b5"      # N-type regions
OXIDE = "#e8e8e8"      # insulator
POLY = "#c9a0dc"       # polysilicon
METAL = "#9aa5b1"      # metal
INK = "#222222"
DEPL = "#c0392b"       # depletion edge


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" '
            f'height="{h}" viewBox="0 0 {w} {h}" font-family="sans-serif" '
            f'font-size="13">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            + "\n".join(body) + "\n</svg>\n")


def rect(x, y, w, h, fill, rx=0, stroke=INK, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}"{d}/>')


def text(x, y, s, anchor="middle", size=13, weight="normal", fill=INK):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}">{s}</text>')


def line(x1, y1, x2, y2, stroke=INK, dash=None, width=1.5, marker=False):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = ' marker-end="url(#arrow)"' if marker else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{width}"{d}{m}/>')


def path(d, stroke=DEPL, dash="6 4", fill="none", width=1.8):
    return (f'<path d="{d}" stroke="{stroke}" stroke-width="{width}" '
            f'stroke-dasharray="{dash}" fill="{fill}"/>')


ARROW = ('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
         'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>')


def stack_section():
    w, h = 640, 300
    body = [ARROW]
    body.append(rect(20, 110, 600, 150, SUB))
    body.append(text(320, 245, "P-type substrate, 0 V", size=14))
    n, x0, pitch, ww = 10, 32, 59, 46
    for k in range(n):
        x = x0 + k * pitch
        v = 50 - 5 * k
        body.append(rect(x, 110, ww, 38, NWELL, rx=6))
        body.append(text(x + ww / 2, 134, f"{v} V", size=13))
        if k < n - 1:
            body.append(text(x + ww / 2 + pitch / 2, 84, "5 V", size=11))
            body.append(f'<path d="M{x + ww / 2},104 Q{x + pitch / 2 + ww / 2},84 '
                        f'{x + pitch + ww / 2},104" stroke="{INK}" '
                        f'stroke-width="1.2" fill="none"/>')
    body.append(text(320, 32, "Along the stack: 5 V between neighbours",
                     size=14, weight="bold"))
    body.append(text(320, 52, "(arcs show each device between two nodes)",
                     size=12))
    # Voltage to the substrate under the first and last node.
    body.append(line(55, 152, 55, 205, marker=True))
    body.append(text(64, 186, "50 V to substrate", anchor="start", size=13,
                     weight="bold"))
    xl = x0 + (n - 1) * pitch + ww / 2
    body.append(line(xl, 152, xl, 205, marker=True))
    body.append(text(xl - 9, 186, "5 V", anchor="end", size=13))
    body.append(text(320, 288, "Each node holds its full voltage to the "
                     "substrate below it", size=13))
    return svg(w, h, body)


def panel(ox, oy, title, extra):
    """One cross-section panel 300 x 210 at (ox, oy)."""
    body = [text(ox + 150, oy + 18, title, size=14, weight="bold")]
    body.append(rect(ox + 5, oy + 70, 290, 125, SUB))
    body.append(text(ox + 200, oy + 185, "P substrate, 0 V", size=12))
    # High-voltage N-well on the left.
    body.append(rect(ox + 5, oy + 70, 70, 55, NWELL, rx=8))
    body.append(text(ox + 40, oy + 102, "well, V", size=12))
    # Substrate contact on the right.
    body.append(rect(ox + 262, oy + 70, 28, 14, "#7fa7d6"))
    body.append(text(ox + 276, oy + 62, "0 V", size=11))
    body += extra(ox, oy)
    return body


def rings(ox, oy):
    b = []
    for i, x in enumerate((105, 145, 185)):
        b.append(rect(ox + x, oy + 70, 18, 26, NWELL, rx=5))
    b.append(text(ox + 150, oy + 50, "floating rings, each a step lower",
                  size=12))
    b.append(path(f"M{ox + 5},{oy + 150} Q{ox + 95},{oy + 150} {ox + 115},"
                  f"{oy + 112} Q{ox + 155},{oy + 120} {ox + 160},{oy + 108} "
                  f"Q{ox + 195},{oy + 112} {ox + 225},{oy + 70}"))
    return b


def plate(ox, oy):
    b = [rect(ox + 60, oy + 58, 170, 12, OXIDE),
         rect(ox + 50, oy + 46, 130, 12, METAL),
         rect(ox + 50, oy + 58, 8, 14, METAL)]      # contact to the well
    b.append(text(ox + 150, oy + 38, "field plate at well voltage", size=12))
    b.append(path(f"M{ox + 5},{oy + 150} Q{ox + 120},{oy + 160} {ox + 190},"
                  f"{oy + 70}"))
    return b


def resurf(ox, oy):
    b = [rect(ox + 75, oy + 70, 170, 14, NWELL)]
    b.append(text(ox + 160, oy + 50, "thin N layer, depleted from below",
                  size=12))
    b.append(path(f"M{ox + 5},{oy + 145} L{ox + 75},{oy + 118} "
                  f"L{ox + 235},{oy + 96} L{ox + 250},{oy + 70}"))
    return b


def chain(ox, oy):
    b = [rect(ox + 60, oy + 58, 200, 12, OXIDE)]
    labels = ("3V/4", "V/2", "V/4")
    for i in range(4):
        b.append(rect(ox + 70 + i * 48, oy + 46, 40, 12, POLY))
    for i, s in enumerate(labels):
        b.append(text(ox + 114 + i * 48, oy + 40, s, size=11))
    b.append(path(f"M{ox + 5},{oy + 150} L{ox + 75},{oy + 130} "
                  f"L{ox + 255},{oy + 92} L{ox + 262},{oy + 70}"))
    return b


def grading():
    w, h = 640, 470
    body = [ARROW]
    body += panel(10, 5, "Floating rings", rings)
    body += panel(330, 5, "Field plate", plate)
    body += panel(10, 235, "Depleted thin layer (RESURF)", resurf)
    body += panel(330, 235, "Resistor chain over the oxide", chain)
    body.append(path("M210,462 L250,462"))
    body.append(text(258, 466, "edge of the depletion region", anchor="start",
                     size=12))
    return svg(w, h, body)


def metal_gate():
    w, h = 640, 400
    body = [ARROW]
    # Insulator stack above the silicon, with the five metal levels.
    body.append(rect(20, 40, 600, 220, OXIDE))
    for k in range(5):
        y = 230 - k * 45
        body.append(line(150, y, 560, y, stroke="#888888", dash="3 4",
                         width=1))
        body.append(text(570, y + 4, f"Metal{k + 1}", anchor="start",
                         size=12))
    # Gate plate on Metal5 at the high voltage.
    body.append(rect(210, 44, 220, 14, METAL))
    body.append(text(320, 32, "gate on Metal5, at the sensed node (57 V)",
                     size=13, weight="bold"))
    # Silicon.
    body.append(rect(20, 260, 600, 120, SUB))
    body.append(text(320, 370, "P substrate, 0 V", size=13))
    # Source and drain, with field oxide between them.
    body.append(rect(150, 260, 70, 26, NWELL))
    body.append(rect(420, 260, 70, 26, NWELL))
    body.append(text(185, 278, "N+", size=12))
    body.append(text(455, 278, "N+", size=12))
    body.append(rect(220, 260, 200, 22, "#cfcfcf"))
    body.append(text(320, 276, "field oxide", size=12))
    # Inversion layer under the field oxide.
    body.append(rect(220, 282, 200, 5, "#2e86de", stroke="#2e86de"))
    body.append(text(320, 304, "inversion layer, near 0 V", size=12))
    # Source and drain wires down through the stack.
    body.append(rect(176, 140, 6, 120, METAL))
    body.append(rect(458, 140, 6, 120, METAL))
    body.append(text(170, 134, "source, 0 V", anchor="end", size=12))
    body.append(text(470, 134, "drain, 1 V", anchor="start", size=12))
    # P+ taps that stop inversion spreading beyond the device.
    for x in (60, 540):
        body.append(rect(x, 260, 40, 16, "#7fa7d6"))
    body.append(text(80, 252, "P+ tap", size=11))
    body.append(text(560, 252, "P+ tap", size=11))
    # Voltage across the insulator.
    body.append(line(320, 62, 320, 255, marker=True))
    body.append(text(330, 160, "57 V across", anchor="start", size=12))
    body.append(text(330, 176, "the insulator", anchor="start", size=12))
    return svg(w, h, body)


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    out = pathlib.Path(argv[1])
    (out / "stack-section.svg").write_text(stack_section(), encoding="utf-8")
    (out / "grading.svg").write_text(grading(), encoding="utf-8")
    (out / "metal-gate.svg").write_text(metal_gate(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
