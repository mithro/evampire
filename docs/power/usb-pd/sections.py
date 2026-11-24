# /// script
# requires-python = ">=3.10"
# ///
"""Draw the cross-sections for the USB Power Delivery implementation pages.
Run with:

    uv run docs/power/usb-pd/sections.py

Writes:

vertical-pnp.svg
    The vertical PNP transistor (analogue.rst).
deep-nwell.svg
    A P-well inside a deep N-well, with the junction breakdowns
    (on-chip-or-external.rst).
custom-structures.svg
    Four custom high-voltage structures (on-chip-or-external.rst).

The drawings are schematic: shapes and spacings are not to scale. The
colours follow docs/high-voltage/figures.py: blue for P-type, orange for
N-type, grey for insulator, purple for polysilicon.

SPDX-License-Identifier: Apache-2.0
"""

from svgfig import GREY, INK, line, rect, svg, text, write

SUB = "#dbe8f5"        # P-type substrate
PWELL = "#c6dbf0"      # P-well, a little darker than the substrate
PPLUS = "#7fa7d6"      # P+ contact or emitter
NWELL = "#fbd9b5"      # N-type well
NPLUS = "#f4b183"      # N+ contact
OXIDE = "#e8e8e8"      # insulator
POLY = "#c9a0dc"       # polysilicon
METAL = "#9aa5b1"      # metal


def region(x, y, w, h, fill, label=None, size=12, ly=None):
    out = [rect(x, y, w, h, fill)]
    if label:
        out.append(text(x + w / 2, ly if ly else y + h / 2 + 4, label, size,
                        "middle"))
    return out


def leader(x0, y0, x1, y1, label, anchor="start", size=11):
    dx = 4 if anchor == "start" else -4
    return [line(x0, y0, x1, y1, INK, 0.8),
            text(x1 + dx, y1 + 4, label, size, anchor)]


def vertical_pnp():
    body = []
    body += region(20, 90, 600, 140, SUB, "P substrate: collector", 13,
                   ly=215)
    body += region(130, 90, 310, 90, NWELL)
    body.append(text(380, 165, "N-well: base", 13, "middle"))
    body += region(190, 90, 90, 24, PPLUS, "P+ emitter", 11)
    body += region(360, 90, 60, 24, NPLUS, "N+", 11)
    body += region(520, 90, 70, 24, PPLUS, "P+", 11)
    for x, lab in ((235, "E"), (390, "B"), (555, "C, 0 V")):
        body.append(line(x, 90, x, 58, INK, 1.4))
        body.append(text(x, 50, lab, 13, "middle", "bold"))
    body.append(line(235, 118, 235, 200, INK, 1.4, arrow="end"))
    body.append(text(245, 140, "holes cross the base", 11))
    body.append(text(245, 154, "to the substrate", 11))
    body.append(text(20, 22, "VBE 0.63 to 0.83 V, current gain 0.8 to 2.4",
                     13))
    body.append(text(620, 22, "the collector is always the substrate", 12,
                     "end", fill=GREY))
    return svg(640, 245, body, "Vertical PNP cross-section")


def deep_nwell():
    body = []
    body += region(20, 110, 600, 170, SUB, "P substrate, 0 V", 13, ly=268)
    body += region(80, 110, 410, 120, NWELL)
    body.append(text(285, 222, "deep N-well", 12, "middle"))
    body += region(150, 110, 270, 75, PWELL, "P-well", 12, ly=170)
    body += region(95, 110, 40, 20, NPLUS, "N+", 11)
    body += region(190, 110, 40, 20, PPLUS, "P+", 11)
    body += region(290, 110, 40, 20, NPLUS, "N+", 11)
    body += region(355, 110, 40, 20, NPLUS, "N+", 11)
    body.append(text(342, 102, "NMOS in the P-well", 11, "middle"))
    body += region(530, 110, 70, 60, NWELL, "N-well", 11, ly=158)
    body += leader(115, 110, 115, 70, "N+ contact of the deep N-well: "
                   "the design rules tie it to the 6 V supply")
    body += leader(420, 160, 470, 160 - 120, "")
    body.append(text(474, 44, "P-well to deep N-well:", 11))
    body.append(text(474, 58, "14.732 V in the models", 11))
    body += leader(300, 230, 360, 250, "deep N-well to P substrate: 30.48 V "
                   "in the models")
    body += leader(600, 150, 625, 90, "", "end")
    body.append(text(626, 72, "N-well to P substrate:", 11, "end"))
    body.append(text(626, 86, "10 V min, 14 V typical", 11, "end"))
    return svg(640, 290, body, "Deep N-well cross-section")


def panel(ox, oy, title):
    return [text(ox + 150, oy + 18, title, 13, "middle", "bold"),
            rect(ox, oy + 100, 300, 110, SUB),
            text(ox + 150, oy + 200, "P substrate, 0 V", 11, "middle")]


def stacked(ox, oy):
    b = panel(ox, oy, "Stacked transistors in isolated wells")
    for k, v in enumerate(("V/3", "2V/3", "V")):
        x = ox + 15 + k * 95
        b += region(x, oy + 100, 80, 60, NWELL)
        b += region(x + 12, oy + 100, 56, 32, PWELL, "NMOS", 10)
        b.append(text(x + 40, oy + 150, f"well at {v}", 10, "middle"))
    b.append(text(ox + 150, oy + 48, "each transistor holds V/3", 11,
                  "middle"))
    b.append(text(ox + 150, oy + 64, "the top well holds V to the substrate",
                  11, "middle"))
    return b


def drain_extended(ox, oy):
    b = panel(ox, oy, "Drain-extended transistor")
    b += region(ox + 20, oy + 100, 260, 50, PWELL)
    b += region(ox + 130, oy + 100, 150, 55, NWELL)
    b.append(text(ox + 205, oy + 145, "lightly doped drain", 10, "middle"))
    b += region(ox + 40, oy + 100, 40, 18, NPLUS, "N+", 10)
    b += region(ox + 230, oy + 100, 40, 18, NPLUS, "N+", 10)
    b += region(ox + 80, oy + 92, 90, 8, OXIDE)
    b += region(ox + 80, oy + 80, 90, 12, POLY, "gate", 10, ly=oy + 90)
    for x, lab in ((ox + 60, "source"), (ox + 250, "drain, high V")):
        b.append(line(x, oy + 100, x, oy + 70, INK, 1.2))
        b.append(text(x, oy + 64, lab, 10, "middle"))
    b.append(text(ox + 150, oy + 40, "the drift region spreads the voltage",
                  11, "middle"))
    return b


def mim(ox, oy):
    b = panel(ox, oy, "Series MIM capacitor")
    b += region(ox + 20, oy + 76, 260, 24, OXIDE, "insulator", 10)
    b += region(ox + 60, oy + 64, 180, 12, METAL)
    b += region(ox + 60, oy + 56, 180, 8, "#ffffff")
    b += region(ox + 80, oy + 44, 140, 12, METAL)
    b.append(text(ox + 150, oy + 36, "top plate", 10, "middle"))
    b += leader(ox + 240, oy + 70, ox + 262, oy + 52, "bottom plate", "start",
                10)
    b.append(text(ox + 150, oy + 150, "both plates sit on the insulator,", 10,
                  "middle"))
    b.append(text(ox + 150, oy + 164, "not on a junction", 10, "middle"))
    return b


def poly(ox, oy):
    b = panel(ox, oy, "Polysilicon resistor on field oxide")
    b += region(ox + 20, oy + 70, 260, 30, OXIDE, "field oxide", 10,
                ly=oy + 94)
    b += region(ox + 50, oy + 58, 200, 12, POLY)
    for x, lab in ((ox + 60, "VBUS"), (ox + 240, "tap")):
        b += region(x - 8, oy + 46, 16, 12, METAL)
        b.append(text(x, oy + 40, lab, 10, "middle"))
    b.append(text(ox + 150, oy + 150, "the oxide holds VBUS to the", 10,
                  "middle"))
    b.append(text(ox + 150, oy + 164, "substrate: no junction", 10,
                  "middle"))
    return b


def custom_structures():
    body = []
    body += stacked(10, 10)
    body += drain_extended(340, 10)
    body += mim(10, 250)
    body += poly(340, 250)
    return svg(650, 470, body, "Custom high-voltage structures")


if __name__ == "__main__":
    write("vertical-pnp.svg", vertical_pnp())
    write("deep-nwell.svg", deep_nwell())
    write("custom-structures.svg", custom_structures())
