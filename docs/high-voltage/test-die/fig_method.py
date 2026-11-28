"""Draw the figures of the measurement-method page.

hvt-conn-p1.svg ... hvt-conn-p5.svg  the connections of each procedure,
                                     on a cross-section of the structure.
hvt-iv.svg         the shapes of reverse current against voltage.
hvt-ring-follow.svg  ring potential against well voltage.
hvt-gated-iv.svg   well current against plate voltage.
hvt-order.svg      the order of work.
hvt-build.svg      the steps from the layout generator to the submission.
hvt-analysis.svg   the steps of analyse.py from the records to the report.

The curves are schematic: they show the shapes that the procedures look
for, not predictions. figures.py calls this module; it writes no files
itself.

SPDX-License-Identifier: Apache-2.0
"""

import math

import tdkit
from tdkit import Section
from fig_graphs import Axes
from svgdraw import (ARROW, BLUE, DEPL, GREY, INK, line, polyline, rect,
                     svg, text)

STRUCTS, _ = tdkit.load()
BOX = "#eef3f8"


def conn(title, name, boxes, note):
    """A connection diagram. boxes: (terminal, lines) with terminal one of
    well, sub, ring, plate."""
    w, h = 640, 380
    y0 = 250
    p = STRUCTS[name]
    sec = Section(p, 40, y0, 560)
    b = [ARROW, text(20, 24, title, anchor="start", weight="bold")]
    b += sec.silicon() + sec.metal(False)
    ins, wd, term = p["inset"], p["ncomp_w"], p["term"]
    where = {"well": (sec.x(-ins - wd / 2), y0 - 36),
             "sub": (sec.x(term + wd / 2), y0 - 58)}
    if p["rings"]:
        g, rw = p["rings"][0]
        where["ring"] = (sec.x(g + rw / 2), y0)
    if p["gate"]:
        where["plate"] = (sec.x(3.0), y0 - 36)
    n = len(boxes)
    bw = 186 if n == 3 else 250
    step = (w - 40 - bw) / (n - 1)
    order = sorted(boxes, key=lambda bx: where[bx[0]][0])
    for k, (terminal, lines) in enumerate(order):
        x = 20 + k * step
        b.append(rect(x, 44, bw, 22 + 16 * len(lines), BOX, rx=5))
        for j, s in enumerate(lines):
            b.append(text(x + bw / 2, 64 + 16 * j, s, size=12,
                          weight="bold" if j == 0 else "normal"))
        tx, ty = where[terminal]
        yb = 66 + 16 * len(lines)
        xs = min(max(tx, x + 12), x + bw - 12)
        ym = 150 + 12 * k
        b.append(polyline([(xs, yb), (xs, ym), (tx, ym), (tx, ty)],
                          stroke=INK, width=1.6))
        b.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="3.5" '
                 f'fill="{INK}"/>')
    b.append(text(20, h - 12, note, anchor="start", size=12, fill=GREY))
    return svg(w, h, b)


def p1():
    return conn("P1: reverse-bias breakdown sweep, shown on NT20", "NT20", [
        ("well", ["SMU channel A, well pad", "force 0 V to 150 V, 0.5 V "
                  "steps", "measure current, limit 10 µA"]),
        ("sub", ["SMU channel B, substrate pads", "force 0 V",
                 "measure current"])],
        "Dark, shielded probe station; chuck at 0 V through channel B; "
        "25 °C, and 85 °C on a subset.")


def p2():
    return conn("P2: capacitance against voltage, shown on a large well",
                "CVN", [
        ("well", ["LCR meter, low terminal", "on the well pad: senses",
                  "the current, 100 kHz and 1 MHz"]),
        ("sub", ["LCR meter, high terminal", "on the substrate pads and",
                 "the chuck; DC bias to −60 V"])],
        "The chuck is joined to the high terminal or left floating, never "
        "grounded; repeat on OPEN and subtract.")


def p3():
    return conn("P3: floating-ring potential, shown on NR1S2", "NR1S2", [
        ("well", ["SMU channel A, well pad", "force 0 V to 150 V",
                  "limit 10 µA"]),
        ("ring", ["Electrometer, ring 1 pad", "force 0 A, read voltage",
                  "guarded cable"]),
        ("sub", ["Substrate pads", "0 V"])],
        "The ring is connected to nothing but the voltmeter.")


def p4():
    return conn("P4: gated diode, shown on NGM1", "NGM1", [
        ("well", ["SMU channel A, well pad", "hold a fixed reverse voltage",
                  "measure current"]),
        ("plate", ["SMU channel B, plate pad", "sweep negative to positive",
                   "limit 100 nA"]),
        ("sub", ["Substrate pads", "0 V"])],
        "The plate crosses the well edge on oxide, so its current is "
        "zero unless the oxide fails.")


def p5():
    return conn("P5: punch-through to a contacted ring, shown on NR1S2",
                "NR1S2", [
        ("well", ["SMU channel A, well pad", "force 0 V upwards",
                  "limit 10 µA"]),
        ("ring", ["SMU channel B, ring 1 pad", "force 0 V",
                  "measure current"]),
        ("sub", ["Substrate pads", "0 V, measure current"])],
        "Current that enters the ring pad is punch-through; current that "
        "enters the substrate pads is avalanche.")


def logline(ax, f, lo, hi, n=160, **kw):
    pts = []
    for k in range(n + 1):
        v = lo + (hi - lo) * k / n
        pts.append(ax.px(v, min(max(f(v), 1e-13), 1e-5)))
    return polyline(pts, **kw)


def iv():
    w, h = 640, 400
    ax = Axes(90, 40, 520, 290, (0, 1), (1e-13, 1e-4), False, True)
    ticks = [(10.0 ** k, s) for k, s in ((-12, "1 pA"), (-10, "100 pA"),
                                         (-8, "10 nA"), (-7, "100 nA"),
                                         (-6, "1 µA"), (-5, "10 µA"))]
    b = ax.frame([], ticks, "well voltage (no scale: schematic)",
                 "well current")

    def aval(vb):
        return lambda v: 1e-12 * (1 + 3 * v) + 1e-12 * math.exp(
            (v - vb) * 180)

    for v, s in ((1e-7, "reported as well: 100 nA"),
                 (1e-6, "breakdown voltage: 1 µA"),
                 (1e-5, "current limit: 10 µA")):
        _, y = ax.px(0, v)
        b.append(line(ax.x0, y, ax.x0 + ax.w, y, stroke=GREY, dash="6 4",
                      width=1.2))
        b.append(text(ax.x0 + 8, y - 5, s, anchor="start", size=12))
    b.append(logline(ax, aval(0.55), 0, 0.66, stroke=DEPL, width=2.4))
    b.append(logline(ax, aval(0.60), 0, 0.71, stroke=DEPL, width=1.8,
                     dash="6 3"))
    b.append(logline(ax, lambda v: 2e-12 * math.exp(v * 15), 0, 1,
                     stroke=BLUE, width=2.2))
    b.append(text(*ax.px(0.03, 4e-13), "avalanche: flat, then a sharp knee",
                  anchor="start", size=12, fill=DEPL))
    b.append(text(*ax.px(0.72, 2e-11), "third sweep after", anchor="start",
                  size=12, fill=DEPL))
    b.append(text(*ax.px(0.72, 4e-12), "walk-out (dashed)", anchor="start",
                  size=12, fill=DEPL))
    b.append(text(*ax.px(0.97, 3e-9), "surface leakage: no knee",
                  anchor="end", size=12, fill=BLUE))
    return svg(w, h, b)


def ring_follow():
    w, h = 640, 400
    ax = Axes(90, 40, 520, 290, (0, 100), (0, 100), False, False)
    b = [ARROW] + ax.frame([(0, "0")], [(0, "0")],
                           "well voltage (no scale: schematic)",
                           "ring 1 voltage")
    b.append(polyline([ax.px(0, 0), ax.px(100, 100)], stroke=GREY,
                      dash="6 4", width=1.2))
    b.append(text(*ax.px(60, 66), "ring = well", anchor="end", size=12,
                  fill=GREY))
    b.append(polyline([ax.px(0, 0), ax.px(28, 0), ax.px(34, 3),
                       ax.px(100, 66)], stroke=BLUE, width=2.4))
    x, y = ax.px(28, 0)
    b.append(text(x, y - 46, "punch-through voltage:", size=12))
    b.append(text(x, y - 30, "the ring starts to follow", size=12))
    b.append(line(x, y - 24, x, y - 4, marker=True, width=1.2))
    xa, ya = ax.px(80, 80)
    _, yb = ax.px(80, 47)
    b.append(line(xa, ya + 2, xa, yb - 2, marker=True, start=True,
                  width=1.2))
    b.append(text(xa + 8, (ya + yb) / 2 + 4, "step held", anchor="start",
                  size=12))
    b.append(text(xa + 8, (ya + yb) / 2 + 20, "by the gap", anchor="start",
                  size=12))
    b.append(text(*ax.px(42, 5.5), "below it, the reading is set by",
                  anchor="start", size=12, fill=GREY))
    b.append(text(*ax.px(42, 1.5), "the meter and by leakage",
                  anchor="start", size=12, fill=GREY))
    return svg(w, h, b)


def gated_iv():
    w, h = 640, 400
    ax = Axes(90, 40, 520, 290, (-22, 50), (0, 10), False, False)
    b = ax.frame([(0, "0")], [(0, "0")],
                 "plate voltage (no scale beyond zero: schematic)",
                 "well current")

    def curve(vfb, vt, top):
        def f(v):
            up = 1 / (1 + math.exp(-(v - vfb) * 1.6))
            down = 1 / (1 + math.exp(-(v - vt) * 1.6))
            return 1.5 + top * up - 0.7 * top * down
        return f

    b.append(ax.curve(curve(-2, 14, 5), -22, 50, n=200, stroke=DEPL,
                      width=2.4))
    b.append(ax.curve(curve(-2, 36, 6), -22, 50, n=200, stroke=BLUE,
                      width=2.0, dash="6 3"))
    for v, s in ((-12, "accumulation"), (6, "depletion"), (24, "inversion")):
        b.append(text(*ax.px(v, 9.2), s, size=12, fill=DEPL))
    b.append(text(*ax.px(6, 8.5), "(low well voltage)", size=11, fill=DEPL))
    for v, s, col, yv in ((-2, "flat-band voltage", INK, 0.6),
                          (14, "field threshold", DEPL, 0.6),
                          (36, "field threshold at a", BLUE, 1.2)):
        x, _ = ax.px(v, 0)
        b.append(line(x, ax.y0, x, ax.y0 + ax.h, stroke=col, dash="2 4",
                      width=1))
        b.append(text(x + 4, ax.px(0, yv)[1], s, anchor="start", size=12,
                      fill=col))
    b.append(text(ax.px(36, 0)[0] + 4, ax.px(0, 0.6)[1],
                  "higher well voltage", anchor="start", size=12, fill=BLUE))
    b.append(text(*ax.px(-21, 2.1), "junction leakage only", anchor="start",
                  size=12))
    b.append(text(*ax.px(1, 5.6), "plus generation at the", anchor="start",
                  size=12))
    b.append(text(*ax.px(1, 5.0), "depleted surface", anchor="start",
                  size=12))
    return svg(w, h, b)


def order():
    steps = [
        ("1", "Contact check", "substrate pad to substrate pad; OPEN to "
         "150 V"),
        ("2", "P1 on groups 1 to 4", "plain wells, drawn P-well, NAT, deep "
         "N-well"),
        ("3", "Decision table", "select the process assumption"),
        ("4", "P2 on the large wells", "doping profile; bias kept below "
         "their breakdown"),
        ("5", "P1 on groups 5 and 6", "plates and rings; not polysilicon"),
        ("6", "P3 and P5", "ring potential and punch-through"),
        ("7", "P4", "gated diodes"),
        ("8", "P1 at 85 °C", "a subset, to separate the mechanisms"),
        ("9", "P1 on polysilicon plates", "NP1, NP2, NP4, NPM12, NGP4: "
         "oxide may fail"),
        ("10", "Comparison", "each structure against its prediction"),
    ]
    return flow("Order of work on each die", steps)


def build():
    return flow("From the generator to the submitted file", [
        ("1", "chip.py", "raw.gds: structures, pads, buses; manifest.json"),
        ("2", "check_nets.py", "every pad reaches its own well, ring or "
         "plate"),
        ("3", "Seal ring", "PDK script: ring.gds, 1936 µm × 2531 µm"),
        ("4", "Dummy fill", "PDK script, Metal4 fill allowed under Metal5"),
        ("5", "Precheck", "wafer.space checks for slot 0p5x0p5"),
        ("6", "hvtest.oas", "the file to submit, top cell hvtest"),
    ])


def analysis():
    return flow("From the records to the report: analyse.py", [
        ("1", "Sweep records", "one CSV file per sweep, as in the record "
         "table"),
        ("2", "Breakdown per die", "first sweep at 25 °C: 1 µA and 100 nA"),
        ("3", "Median over the dies", "with the spread; shorts left out"),
        ("4", "Decision", "A, An or B, and L or D, or undecided"),
        ("5", "Comparison", "ratio to the reference; agreement range"),
        ("6", "Report", "verdicts, P3 and P5, inconclusive items"),
    ])


def flow(title, steps):
    w, h = 640, 60 + 46 * len(steps)
    b = [ARROW, text(20, 24, title, anchor="start", weight="bold")]
    for k, (num, name, detail) in enumerate(steps):
        y = 44 + 46 * k
        b.append(rect(60, y, 520, 32, BOX, rx=5))
        b.append(text(40, y + 21, num, weight="bold"))
        b.append(text(72, y + 21, name, anchor="start", weight="bold"))
        b.append(text(568, y + 21, detail, anchor="end", size=12))
        if k:
            b.append(line(320, y - 14, 320, y - 1, marker=True, width=1.4))
    return svg(w, h, b)


FIGURES = {"hvt-conn-p1.svg": p1, "hvt-conn-p2.svg": p2,
           "hvt-conn-p3.svg": p3, "hvt-conn-p4.svg": p4,
           "hvt-conn-p5.svg": p5, "hvt-iv.svg": iv,
           "hvt-ring-follow.svg": ring_follow, "hvt-gated-iv.svg": gated_iv,
           "hvt-order.svg": order, "hvt-build.svg": build,
           "hvt-analysis.svg": analysis}
