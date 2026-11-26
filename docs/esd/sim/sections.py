"""Draw the output drivers of gf180mcu_fd_io__bi_t in cross-section.

Writes docs/esd/figures/driver-section.svg: the PMOS and NMOS output
transistors whose drains are the pad's primary protection, the diodes
those drains form with their wells, and the parasitic NPN transistor
inside the NMOS. The drawing is schematic, not to scale; the dimensions
written on it are from the cell netlist. Standard library only:

    uv run python docs/esd/sim/sections.py

SPDX-License-Identifier: Apache-2.0
"""

import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "figures"
SUB = "#dbe8f5"      # P substrate
PWELL = "#b9cfe8"
NWELL = "#fbd9b5"
NPLUS = "#f5b46e"
PPLUS = "#7fa7d6"
POLY = "#c9a0dc"
METAL = "#9aa5b1"
INK = "#222222"
HOT = "#c0392b"
SNAP = "#8e44ad"


def rect(x, y, w, h, fill, stroke=INK, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
            f'stroke="{stroke}"{d}/>')


def text(x, y, s, anchor="middle", size=13, fill=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'fill="{fill}" font-weight="{weight}">{s}</text>')


def line(x1, y1, x2, y2, stroke=INK, width=1.5, dash=None, arrow=False):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = ' marker-end="url(#arrow)"' if arrow else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{width}"{d}{m}/>')


def diode(x, y, up, label, anchor):
    """A diode symbol at (x, y), conducting upward if up, with a label."""
    t = (f"{x - 8},{y + 7} {x + 8},{y + 7} {x},{y - 7}" if up
         else f"{x - 8},{y - 7} {x + 8},{y - 7} {x},{y + 7}")
    bar = y - 7 if up else y + 7
    return [f'<polygon points="{t}" fill="{HOT}" stroke="{HOT}"/>',
            line(x - 8, bar, x + 8, bar, stroke=HOT, width=2.5),
            text(x + (12 if anchor == "start" else -12), y + 5, label,
                 anchor=anchor, size=12, fill=HOT)]


def bracket(x1, x2, y, label, anchor="middle"):
    tx = {"middle": (x1 + x2) / 2, "end": x2, "start": x1}[anchor]
    return [line(x1, y, x2, y, width=1), line(x1, y - 4, x1, y + 4, width=1),
            line(x2, y - 4, x2, y + 4, width=1),
            text(tx, y + 16, label, anchor=anchor, size=11)]


def driver_section():
    w, h = 660, 400
    b = ['<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
         'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="{SNAP}"/></marker></defs>']
    top = 170
    b.append(rect(10, top, 640, 200, SUB))
    b.append(text(20, 362, "P substrate", size=13, anchor="start"))
    # PMOS in an N-well tied to DVDD.
    b.append(rect(20, top, 300, 110, NWELL))
    b.append(text(170, top + 100, "N-well, on DVDD", size=12))
    b.append(rect(30, top, 30, 22, NPLUS))
    b.append(rect(80, top, 45, 22, PPLUS))
    b.append(rect(130, top - 10, 30, 10, POLY))
    b.append(rect(165, top, 120, 22, PPLUS))
    b.append(text(225, top + 16, "P+ drain", size=12))
    b += bracket(160, 236, top + 38, "blocked drain: 2.78 µm")
    # NMOS in a P-well tied to DVSS.
    b.append(rect(340, top, 300, 110, PWELL))
    b.append(text(490, top + 100, "P-well, on DVSS", size=12))
    b.append(rect(355, top, 120, 22, NPLUS))
    b.append(text(415, top + 16, "N+ drain", size=12))
    b.append(rect(480, top - 10, 34, 10, POLY))
    b.append(rect(519, top, 45, 22, NPLUS))
    b.append(rect(585, top, 30, 22, PPLUS))
    b += bracket(399, 480, top + 38, "blocked drain: 3.78 µm", anchor="end")
    b.append(text(530, top - 16, "gate length: 1.15 µm", size=11,
                  anchor="end"))
    for x, s in ((45, "N+"), (102, "P+"), (541, "N+"), (600, "P+")):
        b.append(text(x, top + 16, s, size=11))
    # Wiring: PAD to both drains, DVDD and DVSS to sources and taps.
    for x in (270, 370):
        b.append(rect(x - 4, 60, 8, top - 60, METAL))
    b.append(rect(266, 56, 112, 8, METAL))
    b.append(rect(290, 24, 64, 26, "#ffffff"))
    b.append(text(322, 42, "PAD", size=13, weight="bold"))
    b.append(line(322, 50, 322, 56, width=3))
    for x in (45, 102):
        b.append(rect(x - 3, 110, 6, top - 110, METAL))
    b.append(rect(42, 106, 63, 6, METAL))
    b.append(text(74, 98, "DVDD", size=13, weight="bold"))
    for x in (541, 600):
        b.append(rect(x - 3, 110, 6, top - 110, METAL))
    b.append(rect(538, 106, 65, 6, METAL))
    b.append(text(570, 98, "DVSS", size=13, weight="bold"))
    b.append(text(145, top - 16, "gate", size=11))
    # Diodes the drains form with their wells.
    b += diode(225, top + 66, False, "", "start")
    b.append(text(170, top + 128, "P+ drain to N-well: diode from PAD",
                  size=12, fill=HOT, anchor="middle"))
    b.append(text(170, top + 144, "to DVDD, 480 µm in all", size=12,
                  fill=HOT))
    b += diode(415, top + 66, True, "", "start")
    b.append(text(450, top + 128, "P-well to N+ drain: diode from DVSS",
                  size=12, fill=HOT))
    b.append(text(450, top + 144, "to PAD, 304 µm in all", size=12,
                  fill=HOT))
    # Parasitic NPN: drain collector, P-well base, source emitter.
    bx, by = 497, top + 52
    b.append(line(bx, by - 12, bx, by + 12, stroke=SNAP, width=3))
    b.append(line(bx, by - 5, 470, top + 24, stroke=SNAP, width=2))
    b.append(line(bx, by + 5, 530, top + 24, stroke=SNAP, width=2,
                  arrow=True))
    b.append(line(bx, by, bx - 10, by, stroke=SNAP, width=2))
    b.append(text(640, top + 172, "parasitic NPN (drain, P-well, source): "
                  "triggers at 10.7 V,", size=12, fill=SNAP, anchor="end"))
    b.append(text(640, top + 188, "snaps back to about 6 V", size=12,
                  fill=SNAP, anchor="end"))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" '
            f'height="{h}" viewBox="0 0 {w} {h}" font-family="sans-serif">\n'
            f'<rect width="{w}" height="{h}" fill="white"/>\n'
            + "\n".join(b) + "\n</svg>\n")


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "driver-section.svg").write_text(driver_section(),
                                            encoding="utf-8")


if __name__ == "__main__":
    main()
