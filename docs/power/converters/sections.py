# /// script
# requires-python = ">=3.10"
# ///
"""Write hs-isolation.svg: cross-sections of three ways to float a
high-side gate driver above the gf180mcu substrate.

The drawing is schematic: shapes and spacings are not to scale. Run with:

    uv run docs/power/converters/sections.py

SPDX-License-Identifier: Apache-2.0
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from svgplot import Svg, INK, RED, GREY  # noqa: E402

HERE = pathlib.Path(__file__).parent

SUB = "#dbe8f5"        # P-type substrate
PWELL = "#c3d7ee"      # P-type well inside a deep n-well
NWELL = "#fbd9b5"      # N-type well
DNW = "#f4b98a"        # deep N-type well
OXIDE = "#e8e8e8"      # field oxide
POLY = "#c9a0dc"       # polysilicon


def substrate(s, oy, title):
    s.text(300, oy + 14, title, size=14, weight="bold")
    s.rect(20, oy + 60, 560, 105, fill=SUB, stroke=INK)
    s.text(470, oy + 150, "P-type substrate, 0 V", size=13)


def junction(s, d):
    s.add(f'<path d="{d}" stroke="{RED}" stroke-width="2.2" '
          'stroke-dasharray="6 4" fill="none"/>')


def main():
    s = Svg(600, 600)
    # (a) Standard n-well.
    oy = 10
    substrate(s, oy, "(a) Standard n-well")
    s.rect(80, oy + 60, 200, 55, fill=NWELL, stroke=INK, rx=8)
    s.text(180, oy + 80, "n-well of the driver", size=12)
    s.text(180, oy + 98, "up to 62 V", size=12, weight="bold")
    junction(s, f"M80,{oy + 70} L80,{oy + 115} L280,{oy + 115} L280,{oy + 70}")
    s.text(300, oy + 100, "junction holds up to 62 V;\ndocumented breakdown "
           "10 V minimum", size=12, anchor="start", fill=RED)
    s.text(300, oy + 40, "driver supply 5 V above a 57 V switch node",
           size=12, fill=GREY)

    # (b) Deep n-well.
    oy = 200
    substrate(s, oy, "(b) Deep n-well around the driver")
    s.rect(60, oy + 60, 300, 80, fill=DNW, stroke=INK, rx=8)
    s.text(210, oy + 130, "deep n-well, up to 62 V", size=12,
           weight="bold")
    s.rect(80, oy + 60, 120, 45, fill=PWELL, stroke=INK, rx=6)
    s.text(140, oy + 76, "p-well", size=12)
    s.text(140, oy + 93, "switch node, 57 V", size=11)
    s.rect(220, oy + 60, 120, 45, fill=NWELL, stroke=INK, rx=6)
    s.text(280, oy + 76, "n-well", size=12)
    s.text(280, oy + 93, "driver supply, 62 V", size=11)
    junction(s, f"M60,{oy + 70} L60,{oy + 140} L360,{oy + 140} "
             f"L360,{oy + 70}")
    s.text(375, oy + 85, "about 5 V across the\ninner junctions", size=12,
           anchor="start")
    s.text(375, oy + 120, "deep n-well to substrate:\nbreakdown an open "
           "question", size=12, anchor="start", fill=RED)

    # (c) Polysilicon on field oxide.
    oy = 390
    substrate(s, oy, "(c) Polysilicon devices on field oxide")
    s.rect(60, oy + 45, 320, 15, fill=OXIDE, stroke=INK)
    s.text(66, oy + 53, "field oxide", size=11, anchor="start")
    s.rect(110, oy + 32, 220, 13, fill=POLY, stroke=INK)
    s.text(340, oy + 32, "polysilicon devices, 57 V to 62 V", size=12,
           weight="bold", anchor="start")
    junction(s, f"M60,{oy + 60} L380,{oy + 60}")
    s.text(395, oy + 95, "no junction to the\nsubstrate; field oxide\n"
           "breakdown an open\nquestion", size=12, anchor="start", fill=RED)
    s.text(300, 585, "Red dashed lines: where the full voltage to the "
           "substrate is held", size=12, fill=GREY)
    s.save(HERE / "hs-isolation.svg")


if __name__ == "__main__":
    main()
