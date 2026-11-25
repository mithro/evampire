# /// script
# requires-python = ">=3.10"
# ///
"""Draw the cross-section of the gf180mcu breakdown limits. Run with:

    uv run docs/power/poe/drawings_hv.py

Writes:

limits-section.svg
    A schematic cross-section that places each documented and each
    undocumented breakdown of hv-limits.rst on the structure it belongs
    to. Not to scale.

The colours follow docs/high-voltage/svgdraw.py.

SPDX-License-Identifier: Apache-2.0
"""

from svgfig import GREY, INK, dot, line, rect, svg, text, write

SUB = "#dbe8f5"        # P-type substrate and p-wells
NWELL = "#fbd9b5"      # N-type regions
NPLUS = "#f5b46e"      # heavily doped N+
PPLUS = "#7fa7d6"      # heavily doped P+
FOX = "#cfcfcf"        # field oxide
IMD = "#efefef"        # inter-metal dielectric
POLY = "#c9a0dc"       # polysilicon
METAL = "#9aa5b1"      # metal
MARK = "#c00000"

SURF = 220             # silicon surface


def marker(x, y, n, known=True):
    fill = MARK if known else "#ffffff"
    col = "#ffffff" if known else MARK
    return [f'<circle cx="{x}" cy="{y}" r="9" fill="{fill}" '
            f'stroke="{MARK}" stroke-width="1.5"/>',
            text(x, y + 4.5, str(n), 10, "middle", "bold", col)]


def mos(x0, sd, well_fill, label):
    """Source, drain and gate of one transistor starting at x0."""
    out = [rect(x0, SURF, 40, 22, sd, INK, 0.8),
           rect(x0 + 90, SURF, 40, 22, sd, INK, 0.8),
           rect(x0 + 40, SURF - 4, 50, 4, "#ffffff", INK, 0.8),
           rect(x0 + 40, SURF - 20, 50, 16, POLY, INK, 0.8)]
    out.append(text(x0 + 65, SURF - 25, label, 10, "middle"))
    return out


def section():
    b = []
    b.append(rect(10, 60, 660, SURF - 60, IMD, "none"))
    b.append(rect(10, SURF, 660, 150, SUB, INK, 0.8))
    b.append(text(660, SURF + 142, "p-type substrate", 11, "end"))
    # Wells.
    b.append(rect(25, SURF, 170, 70, SUB, INK, 1.0, rx=8))
    b.append(text(110, SURF + 60, "p-well", 10, "middle"))
    b.append(rect(245, SURF, 170, 70, NWELL, INK, 1.0, rx=8))
    b.append(text(330, SURF + 60, "n-well", 10, "middle"))
    b.append(rect(465, SURF, 195, 100, NWELL, INK, 1.0, rx=8))
    b.append(rect(480, SURF, 165, 62, SUB, INK, 1.0, rx=8))
    b.append(text(562, SURF + 54, "p-well", 10, "middle"))
    b.append(text(562, SURF + 92, "deep n-well", 10, "middle"))
    # Field oxide between the wells.
    for x in (195, 415):
        b.append(rect(x - 4, SURF - 8, 58, 18, FOX, INK, 0.8, rx=6))
    # Transistors.
    b += mos(45, NPLUS, SUB, "6 V NMOS")
    b += mos(265, PPLUS, NWELL, "6 V PMOS")
    b += mos(497, NPLUS, SUB, "isolated NMOS")
    # Metal over the field oxide, the inter-metal dielectric and a MIM.
    b.append(rect(190, 168, 70, 10, METAL, INK, 0.8))
    b.append(text(225, 162, "metal at high voltage", 9, "middle"))
    b.append(rect(300, 100, 100, 8, METAL, INK, 0.8))
    b.append(rect(300, 118, 100, 8, METAL, INK, 0.8))
    b.append(text(410, 116, "MIM capacitor", 10))
    b.append(rect(120, 70, 120, 10, METAL, INK, 0.8))
    b.append(rect(120, 128, 120, 10, METAL, INK, 0.8))
    b.append(text(14, 56, "inter-metal dielectric and metal layers", 10,
                  fill=GREY))
    # Markers: filled are documented, open are not.
    marks = [(110, SURF - 2, 1, True), (88, SURF + 22, 2, True),
             (305, SURF + 22, 3, True), (330, SURF + 70, 4, True),
             (360, SURF + 40, 5, True), (562, SURF + 100, 6, False),
             (225, SURF - 30, 7, False), (180, 104, 8, False),
             (350, 113, 9, True)]
    for x, y, n, known in marks:
        b += marker(x, y, n, known)
    legend = [(1, True, "gate oxide: 7 V (3.3 V devices), 12 V (6 V)"),
              (2, True, "N+ to p-well: 8.5 V"),
              (3, True, "P+ to n-well: 8.5 V"),
              (4, True, "n-well to substrate: 10 V"),
              (5, True, "vertical PNP (P+, n-well, substrate): 10 V"),
              (6, False, "deep n-well to substrate: not documented"),
              (7, False, "field oxide under metal: not documented"),
              (8, False, "inter-metal dielectric: not documented"),
              (9, True, "MIM: 20 V (1 fF/µm²), 10 V (1.5, 2 fF/µm²)")]
    y0 = SURF + 175
    for k, (n, known, s) in enumerate(legend):
        col, row = divmod(k, 5)
        x = 20 + 340 * col
        y = y0 + 22 * row
        b += marker(x, y - 4, n, known)
        b.append(text(x + 14, y, s, 10))
    return svg(680, int(y0 + 22 * 5 + 4), b, "Breakdown limits")


if __name__ == "__main__":
    write("limits-section.svg", section())
