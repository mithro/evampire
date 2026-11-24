# /// script
# requires-python = ">=3.10"
# ///
"""Draw the pictorial figures for the magnetics pages as SVG files.

Usage: uv run docs/ethernet/magnetics/drawings.py

Writes, next to this script:

- choke.svg: currents and magnetic flux in a common-mode choke, for
  differential and common-mode current;
- die-barrier.svg: cross-section of an isolation capacitor between the
  lowest and highest metal layers of the evampire die;
- embedded.svg: a transformer embedded in a circuit board;
- cap-area.svg: series capacitor devices and the two kinds of on-chip
  capacitor, drawn by drawings_cap.py.

The drawings are schematic: shapes and spacings are not to scale.

SPDX-License-Identifier: Apache-2.0
"""

import pathlib

HERE = pathlib.Path(__file__).parent

INK = "#222222"
GREY = "#7f7f7f"
CORE = "#bfbfbf"
BLUE = "#1f4e79"
ORANGE = "#c55a11"
RED = "#c00000"
GREEN = "#548235"
SUB = "#dbe8f5"        # P-type substrate
OXIDE = "#e8e8e8"      # insulator
METAL = "#9aa5b1"      # metal


def svg(w, h, body):
    defs = ['<defs>']
    for name, col in (("k", INK), ("b", BLUE), ("o", ORANGE), ("r", RED)):
        defs.append(f'<marker id="{name}" viewBox="0 0 10 10" refX="8" '
                    'refY="5" markerWidth="6" markerHeight="6" '
                    'orient="auto-start-reverse">'
                    f'<path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>')
    defs.append('</defs>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" '
            f'height="{h}" viewBox="0 0 {w} {h}" '
            'font-family="Helvetica, Arial, sans-serif" font-size="13">\n'
            f'<rect width="{w}" height="{h}" fill="white"/>\n'
            + "".join(defs) + "\n" + "\n".join(body) + "\n</svg>\n")


def text(x, y, s, anchor="middle", size=13, weight="normal", fill=INK):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}">{s}'
            '</text>')


def line(x1, y1, x2, y2, stroke=INK, width=1.5, marker=None, dash=None):
    m = f' marker-end="url(#{marker})"' if marker else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{width}"{m}{d}/>')


def path(d, stroke, width=2.0, marker=None, fill="none"):
    m = f' marker-end="url(#{marker})"' if marker else ""
    return (f'<path d="{d}" stroke="{stroke}" stroke-width="{width}" '
            f'fill="{fill}"{m}/>')


def rect(x, y, w, h, fill, stroke=INK, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}"{d}/>')


# ---------------------------------------------------------------------------

def choke_panel(x0, title, same_way, result):
    """One choke: a ring core, one winding on the top limb carrying wire +,
    one on the bottom limb carrying wire -, and the flux each makes."""
    b = [text(x0 + 150, 22, title, weight="bold", size=13)]
    # Core: a ring.
    b.append(rect(x0 + 60, 70, 180, 120, CORE, rx=18))
    b.append(rect(x0 + 88, 98, 124, 64, "white", rx=6))
    # Wires with their windings.
    for y, col, mk, label in ((50, BLUE, "b", "wire +"),
                              (210, ORANGE, "o", "wire −")):
        lim = 84 if y < 100 else 176
        top = lim - 22 if y < 100 else lim + 22
        b.append(path(f"M{x0 + 10},{y} L{x0 + 104},{y} L{x0 + 112},{top}",
                      col, 2))
        b.append(path(f"M{x0 + 188},{top} L{x0 + 196},{y} L{x0 + 290},{y}",
                      col, 2))
        for k in range(5):
            cx = x0 + 112 + 19 * k
            b.append(f'<ellipse cx="{cx}" cy="{lim}" rx="7" ry="22" '
                     f'fill="none" stroke="{col}" stroke-width="2"/>')
        b.append(text(x0 + 10, y - 8, label, "start", 12, fill=col))
        # Current direction on the wire.
        right = (y < 100) or same_way
        xa, xb = (x0 + 240, x0 + 285) if right else (x0 + 285, x0 + 240)
        b.append(line(xa, y, xb, y, col, 2.5, marker=mk))
        b.append(text(x0 + 262, y + (16 if y < 100 else -8),
                      "current", "middle", 11, fill=col))
    # Flux of each winding around the ring (centre line of the core).
    # Wire + flux: clockwise arrow on the outer part of the limb.
    b.append(path(f"M{x0 + 100},77 L{x0 + 205},77", BLUE, 2.5, "b"))
    b.append(path(f"M{x0 + 228},100 L{x0 + 228},150", BLUE, 2.5, "b"))
    if same_way:
        b.append(path(f"M{x0 + 200},183 L{x0 + 95},183", ORANGE, 2.5, "o"))
        b.append(path(f"M{x0 + 72},160 L{x0 + 72},110", ORANGE, 2.5, "o"))
    else:
        b.append(path(f"M{x0 + 95},183 L{x0 + 200},183", ORANGE, 2.5, "o"))
        b.append(path(f"M{x0 + 72},110 L{x0 + 72},160", ORANGE, 2.5, "o"))
    b.append(text(x0 + 150, 134, "flux in", size=11, fill=GREY))
    b.append(text(x0 + 150, 148, "the core", size=11, fill=GREY))
    for k, s in enumerate(result):
        b.append(text(x0 + 150, 245 + 16 * k, s, size=12))
    return b


def choke():
    w, h = 640, 290
    b = []
    b += choke_panel(10, "Differential (data) current", False,
                     ["out on one wire, back on the other:",
                      "the fluxes cancel, low inductance"])
    b += choke_panel(330, "Common-mode current", True,
                     ["the same way on both wires:",
                      "the fluxes add, high impedance"])
    b.append(line(320, 10, 320, h - 10, GREY, 0.8))
    return svg(w, h, b)


# ---------------------------------------------------------------------------

def die_barrier():
    """Isolation capacitor between M1 and M5, with the cable-side bond pad
    and circuits above the oxide."""
    w, h = 640, 330
    b = []
    x0, x1 = 20, 590
    b.append(rect(x0, 260, x1 - x0, 50, SUB))
    b.append(text(305, 292, "substrate, at the chip ground", size=12))
    b.append(rect(x0, 66, x1 - x0, 194, OXIDE))
    for y, name in ((239, "M1"), (194, "M2"), (149, "M3"), (104, "M4"),
                    (59, "M5")):
        b.append(text(x1 + 6, y + 4, name, "start", 11, fill=GREY))
    for y in (217, 172, 127, 82):
        b.append(line(x0, y, x1, y, GREY, 0.6, dash="4,3"))
    b.append(rect(200, 232, 200, 14, METAL))
    b.append(text(410, 243, "M1 plate: chip side", "start", 12))
    b.append(rect(200, 52, 200, 14, "#e6b8a2", stroke=RED))
    b.append(text(300, 44, "M5 plate: cable side", size=12, fill=RED))
    b.append(rect(450, 52, 110, 14, "#e6b8a2", stroke=RED))
    b.append(text(505, 44, "bond pad to the cable", size=12, fill=RED))
    for x in (215, 255, 345, 385):
        b.append(line(x, 68, x, 228, RED, 1.2, marker="r"))
    b.append(text(30, 140, "4 oxide layers,", "start", 12))
    b.append(text(30, 155, "1.15 µm to 1.45 µm", "start", 12))
    b.append(text(30, 170, "each, 4.6 µm to", "start", 12))
    b.append(text(30, 185, "5.8 µm in all", "start", 12))
    b.append(text(300, 130, "oxide strength", size=12, weight="bold",
                  fill=RED))
    b.append(text(300, 146, "about 500 V rms/µm:", size=12, weight="bold",
                  fill=RED))
    b.append(text(300, 162, "2300 V rms to", size=12, weight="bold",
                  fill=RED))
    b.append(text(300, 178, "2900 V rms", size=12, weight="bold", fill=RED))
    for k, s in enumerate(("everything connected", "to the cable sits on",
                           "the top metal, above", "the whole oxide stack")):
        b.append(text(505, 140 + 15 * k, s, size=12))
    return svg(w, h, b)


def embedded():
    """Board-embedded transformer: a cross-section through one limb of the
    core and a top view of the racetrack core with its two windings."""
    w, h = 640, 300
    lam, cop, fer = "#e2efda", "#c55a11", "#7f7f7f"
    b = [text(150, 22, "Cross-section through one limb", weight="bold"),
         text(470, 22, "Top view", weight="bold")]
    # Cross-section: laminate, embedded core, one turn of copper and vias.
    b.append(rect(20, 80, 260, 120, lam))
    b.append(rect(95, 118, 110, 44, fer, rx=4))
    b.append(text(150, 145, "ferrite core", size=12, fill="white"))
    b.append(rect(70, 72, 160, 8, cop, stroke=cop))
    b.append(rect(70, 200, 160, 8, cop, stroke=cop))
    for x in (70, 222):
        b.append(rect(x, 72, 8, 136, cop, stroke=cop))
    b.append(text(150, 64, "top copper layer", size=12))
    b.append(text(150, 226, "bottom copper layer", size=12))
    b.append(text(150, 248, "vias join the two layers into a turn",
                  size=12))
    b.append(text(150, 266, "around the core", size=12))
    b.append(text(25, 96, "laminate", "start", 11, fill=GREEN))
    # Top view: racetrack core with turns on the two straight sides.
    b.append(f'<rect x="360" y="70" width="220" height="130" rx="55" '
             f'fill="none" stroke="{fer}" stroke-width="22"/>')
    for k in range(6):
        x = 410 + 24 * k
        b.append(line(x, 48, x, 92, cop, 3))
        b.append(line(x, 178, x, 222, BLUE, 3))
    b.append(text(470, 40, "winding on one limb", size=12, fill=cop))
    b.append(text(470, 240, "winding on the other limb", size=12, fill=BLUE))
    b.append(text(470, 140, "racetrack-shaped", size=12))
    b.append(text(470, 155, "ferrite core", size=12))
    return svg(w, h, b)


if __name__ == "__main__":
    from drawings_cap import cap_area
    (HERE / "choke.svg").write_text(choke())
    (HERE / "die-barrier.svg").write_text(die_barrier())
    (HERE / "embedded.svg").write_text(embedded())
    (HERE / "cap-area.svg").write_text(cap_area())
