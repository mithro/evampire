"""Draw the structure figures of the test-structures page.

hvt-site.svg      one site in plan view, to scale: structure, lead, pad
                  and substrate bus.
hvt-section.svg   the reference structure NT20 in cross-section.
hvt-<group>.svg   what varies in each group of structures.

Every dimension comes from silicon/hvtest/structures.json and the site
constants of the layout generator's chip.py, repeated in SITE. figures.py
calls this module; it writes no files itself.

SPDX-License-Identifier: Apache-2.0
"""

import tdkit
from tdkit import PWELL, Section, num, plan
from svgdraw import (ARROW, GREY, INK, METAL, NWELL, POLY, PPLUS, line,
                     rect, svg, text)

# chip.py: site pitch, pad side and opening, bus width, structure centre and
# pad centre measured from the west edge of the site.
SITE = {"w": 300.0, "h": 150.0, "pad": 100.0, "open": 90.0, "bus": 6.0,
        "cx": 72.0, "px": 230.0, "lead": 6.0, "margin": 3.0}

STRUCTS, MAN = tdkit.load()


def block_half(p):
    return p["half"] + p["term"] + p["ncomp_w"] + SITE["margin"]


def site():
    """One standard site and the second pad of a two-pad structure."""
    s = 1.5
    w, h = 640, 530
    x0, y0 = 20, 40 + 2 * SITE["h"] * s    # south-west corner of the lower site
    p = STRUCTS["NR1S2"]
    b = [ARROW]
    b.append(text(20, 24, "One site, 300 µm × 150 µm, and the site above it "
                  "used by a second pad", anchor="start", weight="bold"))
    for k in (0, 1):
        b.append(rect(x0, y0 - (k + 1) * SITE["h"] * s, SITE["w"] * s,
                      SITE["h"] * s, "none", stroke=GREY, dash="4 4"))
    cx, cy = x0 + SITE["cx"] * s, y0 - SITE["h"] * s / 2
    bh = block_half(p) * s
    b.append(rect(cx - bh, cy - bh, 2 * bh, 2 * bh, "#f4f4f4", stroke=GREY,
                  dash="2 3"))
    b.append(rect(x0, y0 - 2 * SITE["h"] * s, SITE["bus"] * s,
                  2 * SITE["h"] * s, METAL))
    b.append(rect(x0, cy - 3, cx - (p["half"] + p["term"]) * s - x0, 6,
                  METAL))
    b += plan(p, cx, cy, s)
    px = x0 + SITE["px"] * s
    half_pad = SITE["pad"] * s / 2
    lead_x = cx + (p["half"] - p["inset"] - p["ncomp_w"] / 2) * s
    b.append(rect(lead_x, cy - SITE["lead"] * s / 2, px - half_pad - lead_x,
                  SITE["lead"] * s, METAL))
    for k, label in ((0, "well pad"), (1, "second pad")):
        py = cy - k * SITE["h"] * s
        b.append(rect(px - half_pad, py - half_pad, 2 * half_pad,
                      2 * half_pad, METAL))
        o = SITE["open"] * s / 2
        b.append(rect(px - o, py - o, 2 * o, 2 * o, "#c4ccd4", stroke=INK,
                      dash="3 3"))
        b.append(text(px, py - 4, label, size=13, weight="bold"))
        b.append(text(px, py + 14, "100 µm Metal5,", size=12))
        b.append(text(px, py + 30, "90 µm opening", size=12))
    # the second lead: Metal2 north from ring 1, then east
    ay = cy - SITE["h"] * s
    ring_y = cy - (p["half"] + p["rings"][0][0] + 1.0) * s
    b.append(rect(cx - 2.4, ay - 2.4, 4.8, ring_y - ay + 2.4, "#6f7d8c",
                  stroke="none"))
    b.append(rect(cx - 2.4, ay - 2.4, px - half_pad - cx + 6, 4.8, "#6f7d8c",
                  stroke="none"))
    b.append(text(cx + 8, ay + 18, "Metal2 lead from", anchor="start",
                  size=12))
    b.append(text(cx + 8, ay + 34, "ring 1 or the plate", anchor="start",
                  size=12))
    b.append(text(x0 + 18, y0 - 2 * SITE["h"] * s + 40, "Metal1",
                  anchor="start", size=12))
    b.append(text(x0 + 18, y0 - 2 * SITE["h"] * s + 56, "substrate bus",
                  anchor="start", size=12))
    b.append(text(x0 + 14, cy + bh + 16, "fill blocked inside the dotted "
                  "square", anchor="start", size=12))
    b.append(text(lead_x + 60, cy - 12, "Metal5 lead", anchor="start",
                  size=12))
    ya = y0 + 16
    b.append(line(x0 + 1, ya, x0 + SITE["w"] * s - 1, ya, marker=True,
                  start=True, width=1.2))
    b.append(text(x0 + SITE["w"] * s / 2, ya + 16, "300 µm", size=12))
    xa = x0 + SITE["w"] * s + 12
    b.append(line(xa, y0 - 1, xa, y0 - SITE["h"] * s + 1, marker=True,
                  start=True, width=1.2))
    b.append(text(xa + 6, y0 - SITE["h"] * s / 2 + 4, "150", anchor="start",
                  size=12))
    b.append(text(w - 6, 24, "north ↑", anchor="end", size=12, fill=GREY))
    return svg(w, h, b)


def section():
    """NT20 in cross-section with every part named."""
    p = STRUCTS["NT20"]
    w, h = 640, 330
    sec = Section(p, 30, 150, 580)
    b = [ARROW]
    b.append(text(20, 24, "Cross-section along a radius of NT20, to scale "
                  "along the surface only", anchor="start", weight="bold"))
    b += sec.silicon() + sec.metal()
    b.append(text(sec.x(9), 150 - 12, "trench oxide, 0.32 µm", size=12))
    b.append(text(sec.x(-3), 150 - 42, "+V", size=12, weight="bold"))
    b.append(text(sec.x(9), 150 - 50, "dielectric: 0.86 µm to Metal1, "
                  "5.76 µm to Metal5", size=12))
    b += sec.dim(-p["inset"], 0, "2", 0)
    b += sec.dim(0, p["term"], "termination zone, 20 µm", 0)
    b += sec.dim(p["term"], p["term"] + p["ncomp_w"], "2", 0)
    b.append(text(sec.x(0), 150 + sec.DEPTH + 62, "well edge", size=12))
    b.append(line(sec.x(0), 150 + sec.DEPTH + 48, sec.x(0),
                  150 + sec.DEPTH + 34, width=1, marker=True))
    return svg(w, h, b)


def panels(title, rows, height=250, top=118, legend=()):
    """A figure of stacked cross-sections. rows: (name, caption, pwell
    spans, dims, lead) with dims as (a, b, label)."""
    w = 640
    h = 40 + height * len(rows) + (22 if legend else 0)
    b = [ARROW, text(20, 24, title, anchor="start", weight="bold")]
    right = max(STRUCTS[r[0]]["term"] for r in rows) + 5.0
    for k, (name, caption, pwell, dims, lead) in enumerate(rows):
        y0 = 40 + k * height + top
        p = STRUCTS[name]
        sec = Section(p, 30, y0, 580, right=right)
        b.append(text(30, y0 - top + 16, f"{name}: {caption}",
                      anchor="start", size=13))
        b += sec.silicon(pwell) + sec.nat() + sec.metal(lead)
        for a, e, label in dims:
            b += sec.dim(a, e, label)
    x = 30
    for fill, label in legend:
        b.append(rect(x, h - 20, 16, 12, fill))
        b.append(text(x + 22, h - 9, label, anchor="start", size=12))
        x += 40 + 7 * len(label)
    return svg(w, h, b)


def surround():
    w, h = 640, 600
    p = STRUCTS["NT10"]
    b = [ARROW, text(20, 24, "Distance to the P+ ring (T) and corner radius "
                     "(C)", anchor="start", weight="bold")]
    sec = Section(p, 30, 150, 580, right=25.0)
    b.append(text(30, 56, "NT10 in cross-section: the P+ ring 10 µm from "
                  "the well edge", anchor="start"))
    b += sec.silicon() + sec.metal(False)
    b += sec.dim(0, p["term"], "T = 1, 5, 10 or 20 µm")
    b.append(text(30, 318, "NC0, NT20 and NC15 in plan view, to one scale: "
                  "corner radius 0, 8 and 15 µm", anchor="start"))
    for k, name in enumerate(("NC0", "NT20", "NC15")):
        q = STRUCTS[name]
        cx = 120 + k * 200
        b += plan(q, cx, 450, 2.4)
        b.append(text(cx, 450 + 4, name, size=13, weight="bold"))
        b.append(text(cx, 578, f"C = {num(q['corner'])} µm", size=12))
    b.append(text(w - 8, 340, "N+ ring inside the well, P+ ring outside",
                  anchor="end", size=12, fill=GREY))
    return svg(w, h, b)


def pwell():
    far = STRUCTS["NW0"]["term"] + 3.0  # P+ ring plus 1 um, as drawn
    return panels(
        "A drawn P-well that starts a set distance W from the well edge",
        [("NW0", "the drawn P-well touches the well", [(0, far, "drawn "
          "P-well")], [], False),
         ("NW3", "the drawn P-well starts 3 µm out", [(3, far, "drawn "
          "P-well")], [(0, 3, "W = 3")], False)],
        height=215, top=70, legend=((PWELL, "P-well drawn on the layout"),))


def nat():
    return panels(
        "The NAT layer, which marks silicon that receives no P-well",
        [("NA2", "NAT starts 2 µm from the well edge", [],
          [(0, 2, "A = 2")], False),
         ("NAM1_6", "NAT from 0.6 µm, under a Metal1 field plate 6 µm long",
          [], [(0, 6, "plate, 6 µm")], False)],
        height=225, top=78)


def dnw():
    far = STRUCTS["DW1p5"]["term"] + 3.0  # P+ ring plus 1 um, as drawn
    return panels(
        "A deep N-well in place of the N-well",
        [("DT20", "P+ ring 20 µm from the edge of the deep N-well", [],
          [(0, 20, "T = 2.6 or 20 µm")], False),
         ("DW1p5", "a drawn P-well that starts 1.5 µm out",
          [(1.5, far, "drawn P-well")], [(0, 1.5, "1.5")], False),
         ("DAo1", "the NAT layer overlaps the edge of the deep N-well by "
          "1 µm", [], [(-1, 0, "1")], False)],
        height=215, top=70)


def plates():
    return panels(
        "Field plates tied to the well: polysilicon, Metal1, Metal2 and "
        "stepped",
        [("NP2", "polysilicon on the trench oxide, 2 µm beyond the edge",
          [], [(0, 2, "P = 2")], False),
         ("NM1_6", "Metal1, 6 µm beyond the edge", [],
          [(0, 6, "M1 = 6")], False),
         ("NPM12", "stepped: polysilicon 2 µm, Metal1 5 µm, Metal2 9 µm",
          [], [(0, 9, "2, 5 and 9 µm")], False)],
        height=240, top=96,
        legend=((POLY, "polysilicon"), (METAL, "metal")))


def rings():
    p = STRUCTS["NR3_2"]
    g = [r[0] for r in p["rings"]]
    return panels(
        "Floating N-well rings between the well and the P+ ring",
        [("NR1_2", "one ring, 2 µm wide, 2 µm from the well", [],
          [(0, 2, "gap 2")], False),
         ("NR3_2", f"three rings, gaps {num(g[0])}, {num(g[1])} and "
          f"{num(g[2])} µm", [], [(0, g[0], "gap 1"),
                                  (g[0] + 2, g[0] + 2 + g[1], "gap 2")],
          False)],
        height=215, top=70, legend=((NWELL, "N-well"), (PPLUS, "P+ ring")))


def gated():
    w, h = 640, 300
    p = STRUCTS["NGM1"]
    sec = Section(p, 30, 150, 580)
    b = [ARROW, text(20, 24, "NGM1: a Metal1 plate over the well edge with "
                     "its own pad", anchor="start", weight="bold")]
    b += sec.silicon() + sec.metal(True)
    xm = sec.x(2.5)
    b.append(rect(xm - 2, 150 - 60, 4, 24, "#6f7d8c", stroke="none"))
    b.append(rect(xm - 2, 150 - 66, 90, 6, "#6f7d8c", stroke="none"))
    b.append(text(xm + 94, 150 - 60, "Metal2 lead to the plate pad",
                  anchor="start", size=12))
    b.append(text(sec.x(-3), 150 - 42, "+V", size=12, weight="bold"))
    b += sec.dim(0, p["plates"]["m1"], "plate, 6 µm beyond the edge")
    return svg(w, h, b)


def large():
    """The large wells and the open reference, in plan to one scale."""
    w, h = 640, 290
    s = 0.5
    b = [ARROW, text(20, 24, "Large wells and the open reference, to one "
                     "scale", anchor="start", weight="bold")]
    for name, cx, note in (("CVN", 75, "CVD: deep N-well"),
                           ("CVN2", 185, "no NAT"),
                           ("CVNA", 285, "NAT from 0.6 µm"),
                           ("CVNA2", 430, "NAT from 0.6 µm")):
        p = STRUCTS[name]
        b += plan(p, cx, 140, s)
        b.append(text(cx, 144, name, size=12, weight="bold"))
        b.append(text(cx, 236, f"{num(2 * p['half'])} µm across", size=12))
        b.append(text(cx, 254, note, size=12))
    ox = 525
    b.append(rect(ox, 140 - 1.5, 30, 3, METAL))
    b.append(rect(ox + 30, 140 - 25, 50, 50, METAL))
    b.append(text(ox + 55, 144, "pad", size=12))
    b.append(text(ox + 45, 236, "OPEN: lead and", size=12))
    b.append(text(ox + 45, 254, "pad, no well", size=12))
    return svg(w, h, b)


FIGURES = {"hvt-site.svg": site, "hvt-section.svg": section,
           "hvt-surround.svg": surround, "hvt-pwell.svg": pwell,
           "hvt-nat.svg": nat, "hvt-dnw.svg": dnw, "hvt-plates.svg": plates,
           "hvt-rings.svg": rings, "hvt-gated.svg": gated,
           "hvt-large.svg": large}
