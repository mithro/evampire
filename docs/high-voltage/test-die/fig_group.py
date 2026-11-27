"""Draw the trend graph of each catalogue group: predicted breakdown
against the dimension that the group varies.

catalogue/hvt-g-<group>.svg   one per group page.

A point is the lower of the straight-edge and corner values of one
structure under one process, from predictions.json through pred_data.py.
A structure with no resolved value has no point; an open triangle marks a
sweep that ended without breakdown. The capacitance graph of the large
wells is computed from the published N-well junction model. figures.py
calls this module through gen_catalogue.py.

SPDX-License-Identifier: Apache-2.0
"""

import physics as ph
import pred_data as pd
from fig_graphs import Axes
from fig_pred import COLOUR, marker
from svgdraw import GREY, line, polyline, svg, text

DASH = {"L": None, "D": "6 4"}


def point(name, proc):
    """(volts, kind) of a structure under a process, for the graphs."""
    if name not in pd.PRED["structures"] or not pd.known(name, proc):
        return None, None
    got = [pd.value(name, proc, s) for s in pd.SHAPES]
    nums = [v for v, k in got if k == "bv"]
    low = [v for v, k in got if k == "reached"]
    if nums and not (low and min(low) < min(nums)) \
            and not any(k == "failed" for _, k in got):
        return min(nums), "bv"
    return (min(low), "reached") if low else (None, None)


def trend(title, xlabel, xticks, curves, note=""):
    """curves: (label, process, [(x, structure), ...]). xticks: (x, text)."""
    xs = [x for x, _ in xticks]
    pad = (max(xs) - min(xs)) * 0.08 or 1
    vals = [point(n, c[1])[0] for c in curves for _, n in c[2]]
    vmax = 20 * (int(max([v for v in vals if v] + [40]) / 20) + 1)
    w, h = 640, 400
    ax = Axes(80, 44, 400, 270, (min(xs) - pad, max(xs) + pad), (0, vmax),
              False, False)
    b = [text(20, 24, title, anchor="start", weight="bold")]
    b += ax.frame(xticks, [(v, str(v)) for v in range(0, int(vmax) + 1, 20)],
                  xlabel, "predicted breakdown (V)")
    for v, s in ((14, "published 14 V"), (57, "57 V")):
        if v < vmax:
            _, y = ax.px(xs[0], v)
            b.append(line(ax.x0, y, ax.x0 + ax.w, y, stroke=GREY, dash="5 4",
                          width=1))
            b.append(text(ax.x0 + ax.w - 4, y - 4, s, anchor="end", size=10,
                          fill=GREY))
    seen = 0
    for label, proc, pts, *rest in curves:
        fam = pd.family(proc)
        col = rest[0] if rest else COLOUR.get(fam, GREY)
        got = [(x, *point(n, proc)) for x, n in pts]
        solid = [ax.px(x, v) for x, v, k in got if k == "bv"]
        if not any(k for _, _, k in got):
            continue
        if len(solid) > 1 and xlabel != "structure":
            b.append(polyline(solid, stroke=col, width=1.6,
                              dash=DASH.get(fam[-1])))
        for x, v, k in got:
            if k:
                b.append(marker(*ax.px(x, v), k, "edge", col))
        y = ax.y0 + 14 + 18 * seen
        b.append(marker(ax.x0 + ax.w + 16, y - 4, "bv", "edge", col))
        b.append(text(ax.x0 + ax.w + 26, y, label, anchor="start", size=11))
        seen += 1
    if not seen:
        b.append(text(ax.x0 + ax.w / 2, ax.y0 + ax.h / 2,
                      "not yet simulated", size=13))
    b.append(text(20, h - 28, "Each point: the lower of the straight-edge "
                  "and corner values. Open triangle: a lower bound.",
                  anchor="start", size=11))
    b.append(text(20, h - 12, note, anchor="start", size=11))
    return svg(w, h, b)


def fams(pts, wanted=("AL", "AnL", "AnD", "BL", "BD")):
    return [(f, f, pts) for f in wanted if f in pd.PRED["processes"]]


def surround():
    pts = [(1, "NT1"), (5, "NT5"), (20, "NT20")]
    return trend("Plain N-wells: breakdown against the distance to the P+ "
                 "ring", "distance from the well edge to the P+ ring (µm)",
                 [(x, str(x)) for x, _ in pts], fams(pts, ("AL", "BL", "BD")),
                 "The corner-cut series NC0, NT20, NC15 is in the tables of "
                 "the entries.")


def pwell():
    pts = [(0, "NW0"), (1.5, "NW1p5"), (3, "NW3"), (6, "NW6")]
    return trend("Drawn P-well: breakdown against where the P-well starts",
                 "distance from the well edge to the drawn P-well (µm)",
                 [(x, f"{x:g}") for x, _ in pts],
                 fams(pts, ("AL", "BL", "BD")))


def nat():
    names = ["NA0p6", "NA0p6T10", "NA0p6C0", "NAR1_2", "NAR3_2", "NAR1S3",
             "NAR1S8"]
    pts = list(enumerate(names))
    return trend("NAT beside an N-well: plain, with rings and with a "
                 "contacted ring", "structure", [(k, n) for k, n in pts],
                 fams(pts), "The Metal1 plates under NAT are in the tables "
                 "of the entries.")


def plates():
    sets = [("polysilicon", [(1, "NP1"), (2, "NP2"), (4, "NP4")]),
            ("Metal1", [(3, "NM1_3"), (6, "NM1_6"), (10, "NM1_10")]),
            ("Metal2", [(6, "NM2_6"), (12, "NM2_12")])]
    cols = ("#8e44ad", COLOUR["BL"], "#16a085")
    curves = [(f"{lab}, BL", "BL", pts, col)
              for (lab, pts), col in zip(sets, cols)]
    every = [q for _, pts in sets for q in pts]
    curves += [(f"all layers, {proc}", proc, sorted(every))
               for proc in ("BD", "AL") if proc in pd.PRED["processes"]]
    return trend("Field plates: breakdown against plate length",
                 "length of the plate beyond the well edge (µm)",
                 [(x, str(x)) for x in (1, 2, 3, 4, 6, 10, 12)], curves)


def rings():
    one = [(1.4, "NR1_1p4"), (2, "NR1_2"), (3, "NR1_3")]
    three = [(1.5, "NR3_1p5"), (2, "NR3_2")]
    five = [(1.4, "NR5_1p4"), (2, "NR5_2")]
    wide = [(5, "NR1S5"), (8, "NR1S8"), (12, "NR1S12")]
    cols = (COLOUR["BL"], "#16a085", "#8e44ad")
    curves = [(f"{lab}, BL", "BL", pts, col) for (lab, pts), col in zip(
        (("one ring", one), ("three rings", three), ("five rings", five),
         ("one ring, wide gap", wide)), cols + ("#d35400",))]
    curves += [(f"all, {proc}", proc, sorted(one + three + five + wide))
               for proc in ("BD", "AL") if proc in pd.PRED["processes"]]
    return trend("Floating rings: breakdown against the first gap",
                 "gap from the well edge to ring 1 (µm)",
                 [(x, f"{x:g}") for x in (1.4, 3, 5, 8, 12)], curves,
                 "A count of rings with no point has no finished "
                 "simulation.")


def gated():
    names = ["NGP4", "NGM1", "NAGM1"]
    pts = list(enumerate(names))
    curves = []
    for base, dark in (("BL", "#7f8c8d"), ("BD", "#34495e"),
                       ("AL", "#d98880")):
        if base in pd.PRED["processes"]:
            curves.append((f"joined, {base}", base, pts))
        if "G" + base in pd.PRED["processes"]:
            curves.append((f"plate at 0 V, {base}", "G" + base, pts, dark))
    return trend("Gated diodes: plate joined to the well against plate at "
                 "0 V", "structure", [(k, n) for k, n in pts], curves)


def dnw():
    pts = [(2.6, "DT2p6"), (20, "DT20")]
    return trend("Deep N-wells: breakdown against the distance to the P+ "
                 "ring", "distance from the well edge to the P+ ring (µm)",
                 [(x, f"{x:g}") for x, _ in pts],
                 fams(pts, ("AL", "AD", "BL", "BD")))


def large():
    """Capacitance of CVN and CVN2 from the published N-well model."""
    ca, cp = 1.4914e-4, 5.8719e-10
    w, h = 640, 400
    ax = Axes(80, 44, 400, 270, (0, 10), (0, 7), False, False)
    b = [text(20, 24, "Large N-wells: capacitance expected from the "
              "published model", anchor="start", weight="bold")]
    b += ax.frame([(v, str(v)) for v in range(0, 11, 2)],
                  [(v, str(v)) for v in range(0, 8)],
                  "reverse voltage (V)", "capacitance (pF)")
    for k, (name, half, col) in enumerate((("CVN", 100, COLOUR["BL"]),
                                           ("CVN2 and CVNA", 50,
                                            COLOUR["AL"]))):
        area, per = ph.octagon(half, 20)

        def c(v, area=area, per=per):
            return (ph.c_junction(ca * area * 1e-12, 0.43905, 0.30525, v)
                    + ph.c_junction(cp * per * 1e-6, 0.48991, 0.21757, v)
                    ) * 1e12

        b.append(ax.curve(c, 0, 10, stroke=col, width=2.2))
        b.append(text(ax.x0 + ax.w + 12, ax.px(10, c(10))[1] + 4, name,
                      anchor="start", size=11, fill=col))
    b.append(text(20, h - 28, "Area part with grading 0.305 and edge part "
                  "with grading 0.218, from the N-well diode model.",
                  anchor="start", size=11))
    b.append(text(20, h - 12, "CVNA follows the CVN2 curve if the NAT layer "
                  "changes nothing at its edge.", anchor="start", size=11))
    return svg(w, h, b)


_BV = ("predicted breakdown voltage, the lower of the straight-edge and "
       "corner values, against ")
_END = (", one curve per process, with dashed lines at the published 14 V "
        "and at 57 V and an open triangle where a sweep ended without "
        "breakdown")
ALT = {
    "surround": _BV + "the distance from the well edge to the P+ ring, "
                "1 µm, 5 µm and 20 µm" + _END,
    "pwell": _BV + "the distance at which the drawn P-well starts, from "
             "0 µm to 6 µm" + _END,
    "nat": _BV + "seven structures under NAT: NA0p6, NA0p6T10, NA0p6C0, "
           "NAR1_2, NAR3_2, NAR1S3 and NAR1S8" + _END,
    "plates": _BV + "plate length from 1 µm to 12 µm, with separate curves "
              "for polysilicon, Metal1 and Metal2 plates" + _END,
    "rings": _BV + "the gap from the well to ring 1, from 1.4 µm to 12 µm, "
             "with separate curves for one, three and five rings and for "
             "one ring at the wide gaps" + _END,
    "gated": _BV + "the three gated diodes, with the plate joined to the "
             "well and with the plate at 0 V" + _END,
    "dnw": _BV + "the distance from the edge of the deep N-well to the P+ "
           "ring, 2.6 µm and 20 µm" + _END,
    "large": "the capacitance of the 200 µm and the 100 µm N-well against "
             "reverse voltage from 0 V to 10 V, computed from the "
             "published junction model, falling from 6.4 pF to 2.5 pF and "
             "from 1.7 pF to 0.7 pF",
}

FIGURES = {"surround": surround, "pwell": pwell, "nat": nat,
           "plates": plates, "rings": rings, "gated": gated, "dnw": dnw,
           "large": large}
