"""Draw the result figures of the predictions page.

hvt-pred-bv.svg     predicted breakdown of the plain, drawn P-well, NAT
                    and deep N-well structures (groups 1 to 4).
hvt-pred-bv2.svg    the same for field plates, rings and gated diodes.
hvt-pred-ring.svg   predicted rise of ring 1 against well voltage, for
                    the structures with a pad on ring 1.
hvt-crosscheck.svg  difference between the second simulator and the first.

All values come from predictions.json and crosscheck.json through
pred_data.py. figures.py calls this module; it writes no files itself.

SPDX-License-Identifier: Apache-2.0
"""

import pred_data as pd
import tdkit
from fig_graphs import Axes
from svgdraw import BLUE, DEPL, GREY, INK, line, polyline, rect, svg, text

GREEN = "#2e8b57"
COLOUR = {"A": DEPL, "An": GREEN, "B": BLUE}
BAND = {"A": "#f1c4be", "An": "#bfe3c8", "B": "#bcd9f5"}
FIRST = ("surround", "pwell", "nat", "dnw")
ROW = 19


def marker(x, y, kind, shape, col):
    if kind == "reached":      # lower bound: an open triangle pointing right
        return (f'<path d="M{x - 4:.1f},{y - 4:.1f} L{x + 4:.1f},{y:.1f} '
                f'L{x - 4:.1f},{y + 4:.1f} Z" fill="white" stroke="{col}" '
                f'stroke-width="1.3"/>')
    if shape == "edge":
        return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6" fill="{col}" '
                f'stroke="{INK}" stroke-width="0.6"/>')
    return rect(x - 3.2, y - 3.2, 6.4, 6.4, "white", stroke=col)


def chart(title, keys):
    names = [n for n in pd.ordered()
             if tdkit.group_of(n, pd.STRUCTS[n]) in keys]
    fams = pd.families()
    vmax = 40.0
    for nm in names:
        for f in fams:
            for p in pd.processes(f):
                for s in pd.SHAPES:
                    v, _ = pd.value(pd.entry(nm, p), s)
                    vmax = max(vmax, v or 0)
    vmax = 20 * (int(vmax / 20) + 1)
    top = 50
    w, h = 640, top + ROW * len(names) + 112
    ax = Axes(110, top, 500, ROW * len(names), (0, vmax), (0, 1), False,
              False)
    b = [text(20, 24, title, anchor="start", weight="bold")]
    b += ax.frame([(v, str(v)) for v in range(0, int(vmax) + 1, 20)], [],
                  "predicted breakdown voltage (V)", "")
    for v, s in ((14, "published 14 V"), (57, "57 V")):
        x, _ = ax.px(v, 0)
        b.append(line(x, top, x, top + ax.h, stroke=GREY, dash="5 4",
                      width=1.2))
        b.append(text(x + 3, top - 5, s, anchor="start", size=11,
                      fill=GREY))
    for k, nm in enumerate(names):
        y = top + ROW * (k + 0.5)
        if k % 2:
            b.append(rect(ax.x0, y - ROW / 2, ax.w, ROW, "#000000",
                          stroke="none", opacity=0.04))
        b.append(text(102, y + 4, nm, anchor="end", size=11))
        for j, f in enumerate(fams):
            yy = y + (j - (len(fams) - 1) / 2) * 5
            lo, hi, _ = pd.band(nm, f)
            if lo is not None:
                xa, xb = ax.px(lo, 0)[0], ax.px(hi, 0)[0]
                b.append(rect(xa, yy - 2.5, max(xb - xa, 1), 5, BAND[f],
                              stroke="none"))
            e = pd.entry(nm, f)     # the nominal process is named as its family
            for s in pd.SHAPES:
                v, kind = pd.value(e, s)
                if kind:
                    b.append(marker(ax.px(v, 0)[0], yy, kind, s, COLOUR[f]))
    y = top + ax.h + 58
    for j, f in enumerate(fams):
        x = 20 + j * 120
        b.append(rect(x, y - 9, 22, 6, BAND[f], stroke="none"))
        b.append(marker(x + 11, y - 6, "bv", "edge", COLOUR[f]))
        b.append(text(x + 28, y, f"process {f}", anchor="start", size=12))
    b.append(text(20, y + 20, "Filled circle: straight edge. Open square: "
                  "corner. Bar: band over the family.", anchor="start",
                  size=12))
    b.append(text(20, y + 38, "Open triangle: the sweep ended here without "
                  "breakdown, a lower bound and not a prediction.",
                  anchor="start", size=12))
    return svg(w, h, b)


def pred_bv():
    return chart("Predicted breakdown: plain, drawn P-well, NAT and deep "
                 "N-well structures", FIRST)


def pred_bv2():
    return chart("Predicted breakdown: field plates, floating rings and "
                 "gated diodes", ("plates", "rings", "gated"))


def pred_ring():
    curves = []
    for nm in pd.ordered():
        if not pd.STRUCTS[nm]["sense"]:
            continue
        for f in ("A", "B"):
            pts = pd.entry(nm, f).get("ring_v")
            if pts:
                curves.append((nm, f, pts))
    vmax = max([p[0] for _, _, c in curves for p in c] + [20])
    vmax = 20 * (int((vmax - 1) / 20) + 1)
    w, h = 640, 440
    ax = Axes(90, 40, 520, 300, (0, vmax), (0, vmax), False, False)
    ticks = [(v, str(v)) for v in range(0, int(vmax) + 1, 20)]
    b = [text(20, 24, "Predicted rise of ring 1 against well voltage",
              anchor="start", weight="bold")]
    b += ax.frame(ticks, ticks, "well voltage (V)", "rise of ring 1 (V)")
    b.append(polyline([ax.px(0, 0), ax.px(vmax, vmax)], stroke=GREY,
                      dash="6 4", width=1.2))
    cols = [BLUE, DEPL, GREEN, "#8e44ad"]
    seen = []
    for nm, f, pts in curves:
        if nm not in seen:
            seen.append(nm)
        col = cols[seen.index(nm) % len(cols)]
        b.append(polyline([ax.px(*p) for p in pts], stroke=col,
                          width=2.2 if f == "B" else 3.0,
                          dash=None if f == "B" else "2 3"))
    for k, nm in enumerate(seen):
        b.append(text(ax.x0 + 10, ax.y0 + 20 + 18 * k, nm, anchor="start",
                      size=12, fill=cols[k % len(cols)]))
    b.append(text(20, h - 34, "Solid: process B. Dotted, along the axis: "
                  "process A, which breaks down before the ring moves.",
                  anchor="start", size=12))
    b.append(text(20, h - 16, "Dashed diagonal: ring equal to well.",
                  anchor="start", size=12))
    if not curves:
        b.append(text(ax.x0 + ax.w / 2, ax.y0 + ax.h / 2,
                      "no ring potentials in predictions.json", size=13))
    return svg(w, h, b)


def crosscheck():
    cases = pd.CROSS["cases"]
    row = 44
    w, h = 640, 70 + row * len(cases) + 80
    ax = Axes(170, 50, 440, row * len(cases), (-1.5, 1.5), (0, 1), False,
              False)
    b = [text(20, 24, "Second simulator minus first, by case",
              anchor="start", weight="bold")]
    b += ax.frame([(v, f"{v:+.1f}" if v else "0")
                   for v in (-1.5, -1.0, -0.5, 0, 0.5, 1.0, 1.5)], [],
                  "Charon minus DEVSIM (V)", "")
    x0, _ = ax.px(0, 0)
    b.append(line(x0, ax.y0, x0, ax.y0 + ax.h, stroke=INK, width=1.2))
    for k, c in enumerate(cases):
        y = ax.y0 + row * (k + 0.5)
        b.append(text(162, y - 2, c["name"], anchor="end", size=12))
        b.append(text(162, y + 13, f"DEVSIM {c['devsim_v']:.2f} V",
                      anchor="end", size=11, fill=GREY))
        for key, col, shape in (("charon_integral_v", BLUE, "edge"),
                                ("charon_current_v", DEPL, "corner")):
            if c.get(key) is None:
                continue
            d = max(min(c[key] - c["devsim_v"], 1.5), -1.5)
            b.append(marker(ax.px(d, 0)[0], y, "bv", shape, col))
    y = ax.y0 + ax.h + 60
    b.append(marker(26, y - 4, "bv", "edge", BLUE))
    b.append(text(36, y, "ionisation integral on Charon's potential",
                  anchor="start", size=12))
    b.append(marker(26, y + 16, "bv", "corner", DEPL))
    b.append(text(36, y + 20, "Charon's own avalanche current",
                  anchor="start", size=12))
    return svg(w, h, b)


FIGURES = {"hvt-pred-bv.svg": pred_bv, "hvt-pred-bv2.svg": pred_bv2,
           "hvt-pred-ring.svg": pred_ring, "hvt-crosscheck.svg": crosscheck}
