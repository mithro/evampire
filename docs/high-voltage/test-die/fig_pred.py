"""Draw the figures and write the tables of the predictions page.

hvt-sim-section.svg   where the two simulated sections are cut, and the
                      mesh of one.
hvt-ionisation.svg    field, ionisation coefficients and ionisation
                      integral of a one-sided abrupt junction (computed).
hvt-assumptions.svg   the two process assumptions on one structure.
hvt-pred-bv.svg       predicted breakdown voltage of every structure in
                      predictions.json.
hvt-pred-ring.svg     predicted ring potential against well voltage.
hvt-tab-pred.csv, hvt-tab-pred-band.csv, hvt-tab-processes.csv and
hvt-tab-pred-source.csv  the same results as tables.

predictions.json holds {"structures": {NAME: {PROCESS: {"edge": volts or
null, "corner": volts or null, "ring_v": [[well volts, ring 1 volts],
...]}}}, "processes": {PROCESS: description}, "source": {...}}. A process
whose name starts with "A" belongs to the family of assumption A, and
likewise "B"; the band of a structure is the lowest and highest predicted
breakdown over its family. figures.py calls this module; it writes no
files itself.

SPDX-License-Identifier: Apache-2.0
"""

import json

import physics as ph
import tables as tb
import tdkit
from tdkit import PWELL, Section, plan
from fig_graphs import Axes
from svgdraw import (ARROW, BLUE, DEPL, GREY, INK, line, polyline, rect,
                     svg, text)

STRUCTS, MAN = tdkit.load()
PRED = json.loads((tdkit.HERE / "predictions.json").read_text())
COLOURS = [DEPL, BLUE, "#2e8b57", "#8e44ad", "#d35400", "#16a085",
           "#7f8c8d", "#c2185b"]


def status():
    return str(PRED.get("source", {}).get("status", "status not stated"))


def both(entry):
    vals = [entry.get(k) for k in ("edge", "corner")]
    vals = [v for v in vals if v is not None]
    return min(vals) if vals else None


def ordered():
    order = [s["name"] for s in MAN["sites"]]
    unknown = sorted(set(PRED["structures"]) - set(order))
    if unknown:
        raise SystemExit(f"predictions.json: unknown structures {unknown}")
    return [n for n in order if n in PRED["structures"]]


def sim_section():
    w, h = 640, 560
    p = STRUCTS["NT20"]
    b = [ARROW, text(20, 24, "(a) The two sections simulated for each "
                     "structure, on NT20 in plan view", anchor="start",
                     weight="bold")]
    cx, cy, s = 150, 150, 2.6
    b += plan(p, cx, cy, s)
    far = (p["half"] + p["term"] + p["ncomp_w"] + 4) * s
    b.append(line(cx, cy, cx + far, cy, stroke=DEPL, width=2.2))
    d = far * 0.7071
    b.append(line(cx, cy, cx + d, cy - d, stroke=BLUE, width=2.2))
    b.append(text(cx + far + 8, cy - 4, "straight edge: a flat section, the",
                  anchor="start", size=12, fill=DEPL))
    b.append(text(cx + far + 8, cy + 12, "same at every point along the "
                  "side", anchor="start", size=12, fill=DEPL))
    b.append(text(cx + d + 8, cy - d - 10, "corner: the same section "
                  "rotated about the", anchor="start", size=12, fill=BLUE))
    b.append(text(cx + d + 8, cy - d + 6, "centre of the corner arc",
                  anchor="start", size=12, fill=BLUE))
    y0 = 400
    b.append(text(20, 296, "(b) The section and its mesh: fine at the "
                  "surface and at every drawn edge", anchor="start",
                  weight="bold"))
    sec = Section(p, 30, y0, 580)
    b += sec.silicon() + sec.metal(False)
    xs, x = [], sec.left
    while x < sec.right:
        near = min(abs(x - e) for e in (0, -2, -4, 20, 22))
        x += 0.25 + min(near, 4.0) * 0.22
        xs.append(x)
    for x in xs[:-1]:
        b.append(line(sec.x(x), y0, sec.x(x), y0 + sec.DEPTH,
                      stroke="#555555", width=0.4))
    y = 0.0
    while y < sec.DEPTH:
        y += 2.5 + y * 0.16
        if y < sec.DEPTH:
            b.append(line(sec.x0, y0 + y, sec.x0 + sec.wpx, y0 + y,
                          stroke="#555555", width=0.4))
    b.append(line(sec.x0, y0 - 70, sec.x0, y0 + sec.DEPTH + 8, stroke=DEPL,
                  dash="6 3", width=1.6))
    b.append(text(sec.x0 + 6, y0 - 60, "symmetry plane inside the well",
                  anchor="start", size=12, fill=DEPL))
    b.append(text(sec.x(-3), y0 - 42, "+V", size=12, weight="bold"))
    b += sec.dim(0, p["term"], "termination zone as drawn")
    return svg(w, h, b)


def ionisation():
    n = 1e16
    bv = ph.breakdown_abrupt(n)
    wd = ph.depletion_width(n, bv)
    emax = ph.Q * n * wd / ph.EPS
    w, h = 640, 770
    b = []
    um = wd * 1e4
    ax = Axes(90, 50, 520, 150, (0, 3.5), (0, 5), False, False)
    b.append(text(20, 30, f"(a) Field at breakdown, {bv:.0f} V: a triangle "
                  f"{um:.2f} µm wide", anchor="start", weight="bold"))
    b += ax.frame([(v, str(v)) for v in (0, 1, 2, 3)],
                  [(v, str(v)) for v in (0, 1, 2, 3, 4, 5)],
                  "distance from the P-side edge of the depletion region "
                  "(µm)", "E (10⁵ V/cm)")
    b.append(polyline([ax.px(0, 0), ax.px(um, emax / 1e5), ax.px(um, 0)],
                      stroke=DEPL, width=2.4))
    b.append(text(*ax.px(um + 0.04, emax / 1e5 - 0.3), "junction",
                  anchor="start", size=12))
    ax2 = Axes(90, 300, 520, 150, (0, 3.5), (0, 4), False, False)
    b.append(text(20, 280, "(b) Ionisation coefficients along the same "
                  "line", anchor="start", weight="bold"))
    b += ax2.frame([(v, str(v)) for v in (0, 1, 2, 3)],
                   [(v, str(v)) for v in (0, 1, 2, 3, 4)],
                   "distance (µm)", "α (per µm)")
    for f, col, name, yy in ((ph.alpha_n, DEPL, "electrons, αₙ", 3.3),
                             (ph.alpha_p, BLUE, "holes, αₚ", 0.6)):
        b.append(ax2.curve(lambda x, f=f: f(ph.Q * n * x * 1e-4 / ph.EPS)
                           * 1e-4, 0.001, um, n=120, stroke=col, width=2.4))
        b.append(text(*ax2.px(um + 0.04, yy), name, anchor="start", size=12,
                      fill=col))
    ax3 = Axes(90, 550, 520, 150, (0, 70), (0, 1.4), False, False)
    b.append(text(20, 530, "(c) Ionisation integral against reverse "
                  "voltage", anchor="start", weight="bold"))
    b += ax3.frame([(v, str(v)) for v in range(0, 71, 10)],
                   [(v, f"{v:g}") for v in (0, 0.5, 1.0)],
                   "reverse voltage (V)", "integral")
    b.append(ax3.curve(lambda v: ph.integral_abrupt(n, v, 600), 1, 70,
                       n=70, stroke=DEPL, width=2.4))
    _, y1 = ax3.px(0, 1)
    b.append(line(ax3.x0, y1, ax3.x0 + ax3.w, y1, stroke=GREY, dash="6 4",
                  width=1.2))
    b.append(text(ax3.x0 + 8, y1 - 6, "breakdown: the integral reaches 1",
                  anchor="start", size=12))
    b.append(ax3.dot(bv, 1.0, DEPL))
    b.append(text(*ax3.px(bv - 1.5, 1.12), f"{bv:.0f} V", anchor="end",
                  size=12, weight="bold"))
    b.append(text(w - 30, 754, "one-sided abrupt junction, 10¹⁶ cm⁻³",
                  anchor="end", size=12, fill=GREY))
    return svg(w, h, b)


def assumptions():
    w, h = 640, 700
    b = [ARROW, text(20, 24, "Where the P-well lies under each assumption",
                     anchor="start", weight="bold")]
    rows = [("NT20", "assumption A: generated P-well up to the well edge",
             [(0, 25, "generated P-well")]),
            ("NA2", "assumption A with NAT: no P-well under the NAT layer",
             [(0, 2, ""), (19.5, 25, "")]),
            ("NT20", "assumption B: no P-well unless the layout draws one",
             [])]
    for k, (name, caption, spans) in enumerate(rows):
        y0 = 110 + k * 215
        p = STRUCTS[name]
        sec = Section(p, 30, y0, 580)
        b.append(text(30, y0 - 54, f"{name}, {caption}", anchor="start"))
        b += sec.silicon(spans) + sec.nat() + sec.metal(False)
    b.append(rect(30, h - 22, 16, 12, PWELL))
    b.append(text(52, h - 11, "P-well that the foundry generates",
                  anchor="start", size=12))
    return svg(w, h, b)


def pred_bv():
    names = ordered()
    procs = list(PRED["processes"])
    vmax = 20.0
    for nm in names:
        for e in PRED["structures"][nm].values():
            for k in ("edge", "corner"):
                if e.get(k) is not None:
                    vmax = max(vmax, e[k])
    vmax = 20 * (int(vmax / 20) + 1)
    row = 22
    top = 70
    w, h = 640, top + row * len(names) + 100
    ax = Axes(120, top, 480, row * len(names), (0, vmax), (0, 1), False,
              False)
    b = [text(20, 24, "Predicted breakdown voltage by structure",
              anchor="start", weight="bold"),
         text(20, 44, f"Status of the values: {status()[:70]}",
              anchor="start", size=11, fill=DEPL)]
    b += ax.frame([(v, str(v)) for v in range(0, int(vmax) + 1, 20)], [],
                  "predicted breakdown voltage (V)", "")
    for v, s in ((14, "published 14 V"), (57, "57 V")):
        if v < vmax:
            x, _ = ax.px(v, 0)
            b.append(line(x, top, x, top + ax.h, stroke=GREY, dash="5 4",
                          width=1.2))
            b.append(text(x + 3, top - 5, s, anchor="start", size=11,
                          fill=GREY))
    for k, nm in enumerate(names):
        y = top + row * (k + 0.5)
        b.append(text(112, y + 4, nm, anchor="end", size=12))
        if k % 2:
            b.append(rect(ax.x0, y - row / 2, ax.w, row, "#000000",
                          stroke="none", opacity=0.04))
        for j, pr in enumerate(procs):
            e = PRED["structures"][nm].get(pr)
            if not e:
                continue
            col = COLOURS[j % len(COLOURS)]
            off = (j - (len(procs) - 1) / 2) * 5
            if e.get("edge") is not None:
                x, _ = ax.px(e["edge"], 0)
                b.append(f'<circle cx="{x:.1f}" cy="{y + off:.1f}" r="4" '
                         f'fill="{col}" stroke="{INK}" stroke-width="0.7"/>')
            if e.get("corner") is not None:
                x, _ = ax.px(e["corner"], 0)
                b.append(rect(x - 3.5, y + off - 3.5, 7, 7, "white",
                              stroke=col))
    y = top + ax.h + 60
    x = 20
    for j, pr in enumerate(procs):
        col = COLOURS[j % len(COLOURS)]
        b.append(f'<circle cx="{x + 6}" cy="{y - 4}" r="4" fill="{col}" '
                 f'stroke="{INK}" stroke-width="0.7"/>')
        b.append(text(x + 16, y, f"process {pr}", anchor="start", size=12))
        x += 40 + 8 * len(pr) + 60
    b.append(text(20, y + 22, "Filled circle: straight edge. Open square: "
                  "corner.", anchor="start", size=12))
    return svg(w, h, b)


def pred_ring():
    curves = []
    for nm in ordered():
        for pr, e in PRED["structures"][nm].items():
            if e.get("ring_v"):
                curves.append((f"{nm}, process {pr}", e["ring_v"]))
    vmax = max([p[0] for _, c in curves for p in c] + [20])
    vmax = 20 * (int((vmax - 1) / 20) + 1)
    w, h = 640, 420
    ax = Axes(90, 60, 520, 280, (0, vmax), (0, vmax), False, False)
    ticks = [(v, str(v)) for v in range(0, int(vmax) + 1, 10)]
    b = [text(20, 24, "Predicted potential of ring 1 against well voltage",
              anchor="start", weight="bold"),
         text(20, 44, f"Status of the values: {status()[:70]}",
              anchor="start", size=11, fill=DEPL)]
    b += ax.frame(ticks, ticks, "well voltage (V)", "ring 1 voltage (V)")
    b.append(polyline([ax.px(0, 0), ax.px(vmax, vmax)], stroke=GREY,
                      dash="6 4", width=1.2))
    for j, (label, pts) in enumerate(curves):
        col = COLOURS[j % len(COLOURS)]
        b.append(polyline([ax.px(*p) for p in pts], stroke=col, width=2.2))
        for p in pts:
            b.append(ax.dot(p[0], p[1], col))
        b.append(text(ax.x0 + 10, ax.y0 + 20 + 18 * j, label, anchor="start",
                      size=12, fill=col))
    if not curves:
        b.append(text(ax.x0 + ax.w / 2, ax.y0 + ax.h / 2,
                      "no ring potentials in predictions.json", size=13))
    return svg(w, h, b)


def volts(v):
    return "–" if v is None else f"{v:.0f}"


def tables():
    titles = {k: t for k, t, _ in tdkit.GROUPS}
    rows = [["Structure", "Group", "Process", "Straight edge (V)",
             "Corner (V)", "Predicted breakdown (V)"]]
    band = [["Structure", "Assumption", "Lowest (V)", "Highest (V)",
             "Processes"]]
    for nm in ordered():
        group = titles[tdkit.group_of(nm, STRUCTS[nm])]
        fam = {}
        for pr in PRED["processes"]:
            e = PRED["structures"][nm].get(pr)
            if not e:
                continue
            rows.append([nm, group, pr, volts(e.get("edge")),
                         volts(e.get("corner")), volts(both(e))])
            if both(e) is not None:
                fam.setdefault(pr[0], []).append((both(e), pr))
        for letter, vals in sorted(fam.items()):
            band.append([nm, letter, volts(min(vals)[0]),
                         volts(max(vals)[0]),
                         " ".join(pr for _, pr in vals)])
    proc = [["Process", "Description"]] + [
        [k, v] for k, v in PRED["processes"].items()]
    src = [["Item", "Value"]] + [[k, str(v)]
                                 for k, v in PRED.get("source", {}).items()]
    return {"hvt-tab-pred.csv": tb.write(rows),
            "hvt-tab-pred-band.csv": tb.write(band),
            "hvt-tab-processes.csv": tb.write(proc),
            "hvt-tab-pred-source.csv": tb.write(src)}


FIGURES = {"hvt-sim-section.svg": sim_section,
           "hvt-ionisation.svg": ionisation,
           "hvt-assumptions.svg": assumptions, "hvt-pred-bv.svg": pred_bv,
           "hvt-pred-ring.svg": pred_ring}
