"""Draw the result figures of the predictions page.

hvt-pred-bv.svg     predicted breakdown of the plain, drawn P-well and
                    NAT structures (groups 1 to 3).
hvt-pred-bv2.svg    the same for field plates, rings and gated diodes.
hvt-pred-bv3.svg    the same for the deep N-well structures.
hvt-pred-ring.svg   predicted rise of ring 1 against well voltage, for
                    the structures with a pad on ring 1.
hvt-crosscheck.svg  difference between the second simulator and the first.
hvt-p5.svg          predicted punch-through voltage to a grounded ring
                    against the gap, from p5.json when it exists.

All values come from predictions.json and crosscheck.json through
pred_data.py. figures.py calls this module; it writes no files itself.

SPDX-License-Identifier: Apache-2.0
"""

import pred_data as pd
import pred_extra as px
import tdkit
from fig_graphs import Axes
from svgdraw import BLUE, DEPL, GREY, INK, line, polyline, rect, svg, text

GREEN = "#2e8b57"
COLOUR = {"AL": DEPL, "AD": "#7b241c", "AnL": GREEN, "AnD": "#145a32",
          "BL": BLUE, "BD": "#1b3a6b"}
ROW = 28


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
                    vmax = max(vmax, pd.value(nm, p, s)[0] or 0)
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
            yy = y + (j - (len(fams) - 1) / 2) * 4.2
            e = pd.raw(nm, f)   # the nominal process is named as its family
            lo, hi, _ = pd.band(nm, f) if e else (None, None, None)
            if lo is not None:
                xa, xb = ax.px(lo, 0)[0], ax.px(hi, 0)[0]
                b.append(rect(xa, yy - 2.5, max(xb - xa, 1), 5, COLOUR[f],
                              stroke="none", opacity=0.3))
            for s in pd.SHAPES:
                v, kind = pd.value(nm, f, s) if e else (None, None)
                if v is not None:
                    b.append(marker(ax.px(v, 0)[0], yy, kind, s, COLOUR[f]))
    y = top + ax.h + 58
    for j, f in enumerate(fams):
        x = 20 + j * 100
        b.append(rect(x, y - 9, 22, 6, COLOUR[f], stroke="none",
                      opacity=0.3))
        b.append(marker(x + 11, y - 6, "bv", "edge", COLOUR[f]))
        b.append(text(x + 28, y, f, anchor="start", size=12))
    b.append(text(20, y + 20, "Filled circle: straight edge. Open square: "
                  "corner. Bar: band over the family.", anchor="start",
                  size=12))
    b.append(text(20, y + 38, "Open triangle: the sweep ended here without "
                  "breakdown, a lower bound and not a prediction.",
                  anchor="start", size=12))
    return svg(w, h, b)


def pred_bv():
    return chart("Predicted breakdown: plain, drawn P-well and NAT "
                 "structures", ("surround", "pwell", "nat"))


def pred_bv2():
    return chart("Predicted breakdown: field plates, floating rings and "
                 "gated diodes", ("plates", "rings", "gated"))


def pred_bv3():
    return chart("Predicted breakdown: deep N-well structures", ("dnw",))


def pred_ring():
    curves = []
    for nm in pd.ordered():
        if not pd.STRUCTS[nm]["sense"]:
            continue
        for f in ("BL", "BD"):
            pts = pd.raw(nm, f).get("ring_v")
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
                          width=2.2, dash=None if f == "BL" else "6 4"))
    for k, nm in enumerate(seen):
        b.append(text(ax.x0 + 10, ax.y0 + 20 + 18 * k, nm, anchor="start",
                      size=12, fill=cols[k % len(cols)]))
    b.append(text(20, h - 34, "Solid: process BL. Dashed: process BD.",
                  anchor="start", size=12))
    b.append(text(20, h - 16, "Grey diagonal: ring equal to well.",
                  anchor="start", size=12))
    if not curves:
        b.append(text(ax.x0 + ax.w / 2, ax.y0 + ax.h / 2,
                      "no ring potentials in predictions.json", size=13))
    return svg(w, h, b)


def crosscheck():
    cases = pd.CROSS["cases"]
    row = 44
    w, h = 640, 70 + row * len(cases) + 80
    diffs = [c[k] - c["devsim_v"] for c in cases
             for k in ("charon_integral_v", "charon_current_v")
             if c.get(k) is not None]
    lo = min(-1.0, int(min(diffs) - 1))
    hi = max(1.0, int(max(diffs) + 1))
    ax = Axes(200, 50, 410, row * len(cases), (lo, hi), (0, 1), False,
              False)
    b = [text(20, 24, "Second simulator minus first, by case",
              anchor="start", weight="bold")]
    b += ax.frame([(v, f"{v:+d}" if v else "0")
                   for v in range(int(lo), int(hi) + 1)], [],
                  "Charon minus DEVSIM (V)", "")
    x0, _ = ax.px(0, 0)
    b.append(line(x0, ax.y0, x0, ax.y0 + ax.h, stroke=INK, width=1.2))
    for k, c in enumerate(cases):
        y = ax.y0 + row * (k + 0.5)
        b.append(text(192, y - 2, c["name"], anchor="end", size=12))
        b.append(text(192, y + 13, f"DEVSIM {c['devsim_v']:.2f} V",
                      anchor="end", size=11, fill=GREY))
        for key, col, shape in (("charon_integral_v", BLUE, "edge"),
                                ("charon_current_v", DEPL, "corner")):
            if c.get(key) is None:
                continue
            b.append(marker(ax.px(c[key] - c["devsim_v"], 0)[0], y, "bv",
                            shape, col))
    y = ax.y0 + ax.h + 60
    b.append(marker(26, y - 4, "bv", "edge", BLUE))
    b.append(text(36, y, "ionisation integral on Charon's potential",
                  anchor="start", size=12))
    b.append(marker(26, y + 16, "bv", "corner", DEPL))
    b.append(text(36, y + 20, "Charon's own avalanche current",
                  anchor="start", size=12))
    return svg(w, h, b)


def p5():
    """Punch-through voltage to a grounded ring against the gap."""
    one = [n for n in px.sense() if len(pd.STRUCTS[n]["rings"]) == 1]
    gaps = sorted({pd.STRUCTS[n]["rings"][0][0] for n in one})
    vals = [e["punch_through_v"] for n in one
            for e in px.P5.get(n, {}).values() if e["punch_through_v"]]
    vmax = 20 * (int(max(vals + [40]) / 20) + 1)
    w, h = 640, 400
    ax = Axes(80, 44, 440, 270, (0, max(gaps) + 1), (0, vmax), False, False)
    b = [text(20, 24, "Predicted punch-through to a grounded ring against "
              "the gap", anchor="start", weight="bold")]
    b += ax.frame([(g, f"{g:g}") for g in gaps],
                  [(v, str(v)) for v in range(0, int(vmax) + 1, 20)],
                  "gap from the well edge to ring 1 (µm)",
                  "well voltage at 1 nA of ring current (V)")
    seen = 0
    plain = [n for n in one if pd.STRUCTS[n]["nat_gap"] is None]
    nat = [n for n in one if pd.STRUCTS[n]["nat_gap"] is not None]
    series = [(proc, plain, None, proc) for proc in px.P5_PROCS] + [
        (proc, nat, "5 4", f"{proc}, under NAT") for proc in px.P5_PROCS]
    for proc, names, dash, label in series:
        pts = [(pd.STRUCTS[n]["rings"][0][0], px.P5.get(n, {}).get(proc))
               for n in names]
        got = [(g, e["punch_through_v"]) for g, e in pts
               if e and e["punch_through_v"] is not None]
        low = [(g, e["reached_v"]) for g, e in pts
               if e and e["punch_through_v"] is None]
        if not got and not low:
            continue
        col = COLOUR[proc]
        if len(got) > 1:
            b.append(polyline([ax.px(*q) for q in got], stroke=col,
                              width=1.6, dash=dash))
        b += [marker(*ax.px(*q), "bv", "edge", col) for q in got]
        b += [marker(*ax.px(*q), "reached", "edge", col) for q in low]
        y = ax.y0 + 14 + 18 * seen
        b.append(marker(ax.x0 + ax.w + 16, y - 4, "bv", "edge", col))
        b.append(text(ax.x0 + ax.w + 26, y, label, anchor="start",
                      size=11))
        seen += 1
    if not seen:
        b.append(text(ax.x0 + ax.w / 2, ax.y0 + ax.h / 2,
                      "not yet simulated", size=13))
    b.append(text(20, h - 28, "Dashed: NAR1S3 and NAR1S8, the contacted "
                  "rings under NAT.", anchor="start", size=11))
    b.append(text(20, h - 12, "Open triangle: the ring current did not "
                  "reach 1 nA by the end of the sweep.", anchor="start",
                  size=11))
    return svg(w, h, b)


FIGURES = {"hvt-p5.svg": p5, "hvt-pred-bv.svg": pred_bv, "hvt-pred-bv2.svg": pred_bv2,
           "hvt-pred-bv3.svg": pred_bv3,
           "hvt-pred-ring.svg": pred_ring, "hvt-crosscheck.svg": crosscheck}
