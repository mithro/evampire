"""Draw the figure of one catalogue entry: a structure in plan view and in
cross-section along the edge that its lead crosses.

catalogue/hvt-s-<NAME>.svg       one per structure on the die.
catalogue/hvt-s-<NAME>-ring.svg  predicted rise of ring 1, for a structure
                                 with a pad on ring 1 that has a prediction.

Every dimension comes from the structure's parameters in manifest.json;
the site constants repeat those of the layout generator's chip.py.
figures.py calls this module through gen_catalogue.py.

SPDX-License-Identifier: Apache-2.0
"""

import pred_data as pd
import tdkit
from tdkit import NAT, PWELL, Section, num, plan
from fig_graphs import Axes
from svgdraw import (ARROW, BLUE, GREY, INK, METAL, NWELL, POLY, line,
                     polyline, rect, svg, text)

STRUCTS, MAN = tdkit.load()
SITES = {s["name"]: s for s in MAN["sites"]}
M2 = "#6f7d8c"
LAYER = {"poly": "polysilicon", "m1": "Metal1", "m2": "Metal2"}


def cut(p):
    """Length of the 45-degree cut along each side, in micrometres."""
    return min(0.586 * p["corner"], p["half"] * 0.999)


def summary(p):
    """One line of the drawn features, for the figure and its alt text."""
    if p["kind"] == "open":
        return "Metal5 lead and pad, no well"
    out = []
    for gap, width in p["rings"][:1]:
        gaps = ", ".join(num(g) for g, _ in p["rings"])
        count = {1: "one", 3: "three", 4: "four", 5: "five"}[len(p["rings"])]
        out.append(f"{count} floating ring"
                   f"{'s' if len(p['rings']) > 1 else ''} {num(width)} µm "
                   f"wide, gap{'s' if len(p['rings']) > 1 else ''} {gaps} µm")
    for layer, length in p["plates"].items():
        out.append(f"{LAYER[layer]} plate to {num(length)} µm"
                   + (" on its own pad" if p["gate"] else ""))
    if p["pwell_gap"] is not None:
        out.append(f"drawn P-well from {num(p['pwell_gap'])} µm")
    if p["nat_gap"] is not None:
        out.append(f"NAT from {num(p['nat_gap'])} µm" if p["nat_gap"] > 0
                   else f"NAT overlapping the well edge by "
                        f"{num(-p['nat_gap'])} µm")
    if p["lead_w"] != 6.0:
        out.append(f"Metal5 lead {num(p['lead_w'])} µm wide")
    if p["dualgate"]:
        out.append("in the 6 V area")
    return "; ".join(out) or "nothing drawn in the termination zone"


def plan_panel(name, p, site, x0, y0):
    """The structure enlarged, and beside it the site with its pads."""
    b = []
    outer = p["half"] + p["term"] + p["ncomp_w"] + 3.0
    s = 105.0 / outer
    cx, cy = x0 + 115, y0 + 115
    if p["kind"] == "open":
        b.append(rect(cx - 105, cy - 105, 210, 210, "#f4f4f4", stroke=GREY,
                      dash="2 3"))
        b.append(text(cx, cy - 20, "no well", size=12, fill=GREY))
    else:
        b.append(rect(cx - 105, cy - 105, 210, 210, "#f4f4f4", stroke=GREY,
                      dash="2 3"))
        b += plan(p, cx, cy, s)
        if p["sense"] or p["gate"]:
            b.append(rect(cx - 2, cy - 105, 4,
                          105 - (p["half"] - 1) * s, M2, stroke="none"))
        side = 2 * p["half"]
        b.append(text(cx, cy + 4, f"{num(side)} µm", size=11))
    lw = max(p["lead_w"] * s, 3)
    lead_x = cx + (p["half"] - p["inset"] - p["ncomp_w"] / 2) * s
    b.append(rect(lead_x, cy - lw / 2, cx + 105 - lead_x, lw, METAL))
    b.append(text(x0, y0 - 8, "Plan view, to scale", anchor="start",
                  size=12))
    if p["kind"] != "open" and p["corner"] > 0:
        b.append(text(cx, cy + 105 + 16, f"corner cut {cut(p):.1f} µm along "
                      f"each side", size=11))
    elif p["kind"] != "open":
        b.append(text(cx, cy + 105 + 16, "square corners, no cut", size=11))
    # the site, to a smaller scale, with its pads
    q = 0.62
    sx, sy = x0 + 330, y0 + 150
    two = "aux_pad" in site
    b.append(text(sx, y0 - 8, "Site and pads, to scale; north up",
                  anchor="start", size=12))
    px = sx + (site["pad"][0] - site["centre"][0]) * q + 60
    scx = sx + 60
    b.append(rect(scx - outer * q, sy - outer * q, 2 * outer * q,
                  2 * outer * q, NWELL if p["kind"] != "open" else "white",
                  stroke=GREY))
    b.append(rect(scx, sy - 2, px - 50 * q - scx, 4, METAL, stroke="none"))
    b.append(rect(px - 50 * q, sy - 50 * q, 100 * q, 100 * q, METAL))
    b.append(text(px, sy + 4, "well pad" if p["kind"] != "open" else "pad",
                  size=11))
    b.append(text(px, sy + 50 * q + 14,
                  f"{site['pad'][0]:.0f}, {site['pad'][1]:.0f}", size=11))
    if two:
        ay = sy - 150 * q
        role = "ring 1 pad" if site["aux_role"] == "ring1" else "plate pad"
        b.append(rect(scx - 1.5, ay, 3, sy - ay - outer * q, M2,
                      stroke="none"))
        b.append(rect(scx - 1.5, ay - 1.5, px - 50 * q - scx + 1.5, 3, M2,
                      stroke="none"))
        b.append(rect(px - 50 * q, ay - 50 * q, 100 * q, 100 * q, METAL))
        b.append(text(px, ay + 4, role, size=11))
        b.append(text(px, ay - 50 * q - 5,
                      f"{site['aux_pad'][0]:.0f}, {site['aux_pad'][1]:.0f}",
                      size=11))
    b.append(text(sx, y0 + 236, "pad centres in µm from the south-west "
                  "corner", anchor="start", size=11, fill=GREY))
    b.append(text(sx, y0 + 252, "dotted square: edge of the fill block",
                  anchor="start", size=11, fill=GREY))
    return b


def section_panel(p, y0):
    sec = Section(p, 30, y0, 580)
    b = [text(30, y0 - 112, "Cross-section along the lead, to scale along "
              "the surface only", anchor="start", size=12)]
    if p["kind"] == "open":
        b.append(rect(30, y0, 580, sec.DEPTH, tdkit.SUB))
        b.append(rect(30, y0, 580, 7, tdkit.FOX, stroke="none"))
        b.append(rect(30, y0 - 92, 580, 8, METAL))
        b.append(text(320, y0 - 98, "Metal5 lead, 5.76 µm above the "
                      "silicon", size=12))
        b.append(text(604, y0 + sec.DEPTH - 8, "P substrate", anchor="end",
                      size=12))
        return b
    spans = []
    if p["pwell_gap"] is not None:
        spans.append((p["pwell_gap"], p["term"] + p["ncomp_w"] + 1.0,
                      "drawn P-well"))
    b += sec.silicon(spans) + sec.nat() + sec.metal(True)
    b.append(text(sec.x(-3), y0 - 42, "+V", size=12, weight="bold"))
    if p["sense"]:
        g, rw = p["rings"][0]
        xr = sec.x(g + rw / 2)
        b.append(rect(xr - 1.5, y0 - 60, 3, 60, M2, stroke="none"))
        b.append(text(xr + 6, y0 - 62, "to the ring 1 pad", anchor="start",
                      size=11))
    if p["gate"]:
        length = max(p["plates"].values())
        xr = sec.x(length / 2)
        top = 36 if "m1" in p["plates"] else 7
        b.append(rect(xr - 1.5, y0 - 66, 3, 66 - top, M2, stroke="none"))
        b.append(text(xr + 6, y0 - 68, "to the plate pad", anchor="start",
                      size=11))
    feature = None
    if p["rings"]:
        feature = (0, p["rings"][0][0], f"{num(p['rings'][0][0])}")
    elif p["plates"]:
        length = max(p["plates"].values())
        feature = (0, length, f"plate, {num(length)}")
    elif p["pwell_gap"]:
        feature = (0, p["pwell_gap"], num(p["pwell_gap"]))
    elif p["nat_gap"] is not None and p["nat_gap"] != 0:
        a, e = sorted((0, p["nat_gap"]))
        feature = (a, e, num(abs(p["nat_gap"])))
    if feature:
        b += sec.dim(*feature, level=0)
    b += sec.dim(0, p["term"], f"well edge to P+ ring, {num(p['term'])} µm",
                 level=1 if feature else 0)
    return b


def entry(name):
    p, site = STRUCTS[name], SITES[name]
    w, h = 640, 640
    b = [ARROW, text(20, 24, f"{name}: {summary(p)}", anchor="start",
                     weight="bold", size=13)]
    b += plan_panel(name, p, site, 30, 56)
    b += section_panel(p, 440)
    x = 30
    for fill, label in ((NWELL, "N-type well"), (tdkit.NPLUS, "N+"),
                        (tdkit.PPLUS, "P+"), (PWELL, "P-well"),
                        (POLY, "polysilicon"), (METAL, "metal")):
        b.append(rect(x, h - 20, 14, 11, fill))
        b.append(text(x + 19, h - 10, label, anchor="start", size=11))
        x += 34 + 6.2 * len(label)
    b.append(rect(x, h - 20, 14, 11, "none", stroke=NAT, dash="4 2"))
    b.append(text(x + 19, h - 10, "NAT", anchor="start", size=11))
    return svg(w, h, b)


def alt(name):
    p, site = STRUCTS[name], SITES[name]
    if p["kind"] == "open":
        return (f"Plan view and cross-section of {name}: a Metal5 lead and "
                f"a pad 100 µm square over bare substrate, with no well.")
    kind = "an N-well" if p["kind"] == "nw" else "a deep N-well"
    corners = (f"corners cut {cut(p):.1f} µm along each side"
               if p["corner"] else "square corners")
    pads = (f"A Metal5 lead joins the well to a pad at "
            f"{site['pad'][0]:.0f}, {site['pad'][1]:.0f} µm.")
    if "aux_pad" in site:
        what = "ring 1" if site["aux_role"] == "ring1" else "the plate"
        pads += (f" A Metal2 lead joins {what} to a second pad at "
                 f"{site['aux_pad'][0]:.0f}, {site['aux_pad'][1]:.0f} µm.")
    return (f"Plan view and cross-section of {name}: {kind} "
            f"{num(2 * p['half'])} µm across with {corners}, an N+ contact "
            f"ring inside its edge and a P+ ring {num(p['term'])} µm outside "
            f"it; {summary(p)}. {pads}")


def ring(name):
    """Predicted rise of ring 1, or None if no process has a curve."""
    curves = [(f, pd.raw(name, f).get("ring_v")) for f in pd.families()]
    curves = [(f, c) for f, c in curves if c and max(v for _, v in c) > 1]
    if not curves:
        return None
    vmax = 20 * (int((max(p[0] for _, c in curves for p in c) - 1) / 20) + 1)
    ax = Axes(90, 40, 520, 260, (0, vmax), (0, vmax), False, False)
    ticks = [(v, str(v)) for v in range(0, int(vmax) + 1, 20)]
    b = [text(20, 24, f"{name}: predicted rise of ring 1", anchor="start",
              weight="bold")]
    b += ax.frame(ticks, ticks, "well voltage (V)", "rise of ring 1 (V)")
    b.append(polyline([ax.px(0, 0), ax.px(vmax, vmax)], stroke=GREY,
                      dash="6 4", width=1.2))
    cols = [BLUE, "#1b3a6b", "#2e8b57", "#c0392b", INK, GREY]
    for k, (f, pts) in enumerate(curves):
        b.append(polyline([ax.px(*q) for q in pts], stroke=cols[k % 6],
                          width=2.2))
        b.append(text(ax.x0 + 10, ax.y0 + 20 + 18 * k, f"process {f}",
                      anchor="start", size=12, fill=cols[k % 6]))
    b.append(line(ax.x0, ax.y0 + ax.h, ax.x0 + ax.w, ax.y0 + ax.h,
                  width=1))
    return svg(640, 360, b)
