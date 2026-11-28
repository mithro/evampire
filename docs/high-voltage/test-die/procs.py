"""Reduce procedures P2 to P5 and compare them with the simulation.

Each verdict comes from rules.py; a measured quantity with no simulated
counterpart is reported with "no prediction". analyse.py calls
procedures() for the results and markdown() for the report.

Standard library only.

SPDX-License-Identifier: Apache-2.0
"""

import statistics

import cv
import measure
import physics as ph
import pred_data as pd
import rules


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def v(x, bound=False):
    return "–" if x is None else ("> " if bound else "") + f"{x:.1f}"


def procedures(sweeps, first, fam, cap):
    """{"P2": cap, "P3": [...], "P4": [...], "P4a": [...], "P5": [...]}."""
    p3, p4, p4a, p5 = {}, {}, {}, {}
    for w in sorted(sweeps, key=lambda w: w.sweep):
        if not w.room:
            continue
        if w.procedure == "P3" and w.direction == "up":
            p3.setdefault(w.structure, {}).setdefault(w.die,
                                                       measure.ring_onset(w))
        elif w.procedure == "P5" and w.direction == "up":
            p5.setdefault(w.structure, {}).setdefault(w.die, measure.punch(w))
        elif w.procedure == "P4" and measure.gated_part(w) == 2:
            plate = round(statistics.median(w.col("v_aux_v")), 1)
            b = measure.breakdown(w)
            if b.kind == "bv":
                p4.setdefault((w.structure, plate), {})[w.die] = b.bv
        elif w.procedure == "P4":
            well = round(statistics.median(w.col("v_well_v")), 2)
            p4a.setdefault((w.structure, well), {})[w.die] = \
                measure.gated_levels(w)
    out = {"P2": cap, "P3": [], "P4": [], "P4a": [], "P5": []}
    for st, by in sorted(p3.items()):
        ons = [x[0] for x in by.values()]
        on = med(ons)
        top = med([x[2] for x in by.values()])
        step = med([x[1] for x in by.values()])
        got = [x for x in ons if x is not None]
        meas = on if 2 * len(got) > len(ons) else None
        row = {"name": st, "dies": len(by), "onset": meas, "top": top,
               "step": step, "verdict": "no family", "step_verdict": "–"}
        if fam:
            rng = rules.pt_range(st, fam, "P3")
            row["range"] = rng
            row["verdict"] = rules.pt_verdict(st, fam, "P3", meas, top)
            srange = rules.step_range(st, fam, top)
            if srange[0] is None:
                row["step_verdict"] = srange[1]
            else:
                row["step_range"] = srange
                row["step_verdict"] = ("agrees" if srange[0] <= step
                                       <= srange[1] else "disagrees")
        out["P3"].append(row)
    for st, by in sorted(p5.items()):
        pts = [x[0] for x in by.values()]
        got = [x for x in pts if x is not None]
        meas = med(got) if 2 * len(got) > len(pts) else None
        top = med([x[1] for x in by.values()])
        mech = sorted(x[2] for x in by.values())[len(by) // 2]
        row = {"name": st, "dies": len(by), "pt": meas, "top": top,
               "mech": mech, "verdict": "no family"}
        if fam:
            row["range"] = rules.pt_range(st, fam, "P5")
            row["verdict"] = rules.pt_verdict(st, fam, "P5", meas, top)
        out["P5"].append(row)
    for (st, plate), by in sorted(p4.items()):
        out["P4"].append(gated_row(st, plate, by, first, fam))
    for (st, well), by in sorted(p4a.items()):
        vfb = med([x[0] for x in by.values()])
        vt = med([x[1] for x in by.values()])
        out["P4a"].append({"name": st, "well": well, "dies": len(by),
                           "vfb": vfb, "vt": vt,
                           "estimate": threshold_estimate(st, fam, well)})
    out["P4doping"] = gated_doping(out["P4a"])
    return out


def gated_row(st, plate, by, first, fam):
    """P4, second part: the breakdown at one plate voltage."""
    bv = med(list(by.values()))
    row = {"name": st, "plate": plate, "dies": len(by), "bv": bv,
           "verdict": "no prediction", "ratio": "no prediction"}
    if abs(plate) > 0.05 or not fam:
        return row
    g = rules.gated_band(st, fam)
    if g is None:
        return row
    lo, hi, joined = g
    a, b = pd.agreement(lo, hi)
    row["range"] = (a, b)
    row["verdict"] = "in range" if a <= bv <= b else (
        f"{'above' if bv > b else 'below'} the range")
    rs = [x / first[(st, d)].bv for d, x in by.items()
          if (st, d) in first and first[(st, d)].kind == "bv"]
    pred = pd.band_of(["G" + fam], st)[0]
    if rs and pred and joined:
        m, p = med(rs), pred / joined
        row["m_ratio"], row["p_ratio"] = m, p
        if (pred < pd.REGIME) != (joined < pd.REGIME):
            row["ratio"] = "across regimes: not a test"
        else:
            row["ratio"] = "agrees" if pd.ratio_agrees(m, p) else "disagrees"
    return row


def surface_is_pwell(st, fam):
    pw = pd.parse(fam)[1] if fam else None
    return pw == "A" or (pw == "An" and pd.STRUCTS[st]["nat_gap"] is None)


def threshold_estimate(st, fam, well):
    """The estimate of the field threshold from the equation of method.rst
    with the nominal substrate doping: not a simulation."""
    if not fam or surface_is_pwell(st, fam):
        return None
    cox = ph.COX[next(iter(pd.STRUCTS[st]["plates"]))]
    return ph.field_threshold(rules.SUB_NOMINAL, cox, well,
                              ph.VFB_ILLUSTRATION)


def doping_from_thresholds(cox, v1, t1, v2, t2):
    """Doping that gives thresholds t1 and t2 at well voltages v1 and v2,
    by bisection on the logarithm; the flat-band voltage cancels."""
    def gap(n):
        return (ph.field_threshold(n, cox, v2, 0) - ph.field_threshold(
            n, cox, v1, 0)) - (t2 - t1)
    lo, hi = 1e13, 1e19
    if gap(lo) > 0 or gap(hi) < 0:
        return None
    for _ in range(80):
        mid = (lo * hi) ** 0.5
        lo, hi = (mid, hi) if gap(mid) < 0 else (lo, mid)
    return (lo * hi) ** 0.5


def gated_doping(rows):
    out = []
    by = {}
    for r in rows:
        if r["vt"] is not None:
            by.setdefault(r["name"], []).append((r["well"], r["vt"]))
    for st, pts in sorted(by.items()):
        if len(pts) >= 2:
            (v1, t1), (v2, t2) = sorted(pts)[0], sorted(pts)[-1]
            cox = ph.COX[next(iter(pd.STRUCTS[st]["plates"]))]
            n = doping_from_thresholds(cox, v1, t1, v2, t2)
            out.append((st, n, rules.doping_rule(n)))
    return out


def markdown(o, fam):
    f = fam or "no family"
    out = ["", "## Other procedures", "",
           f"Compared under {f} by the rules of method.rst. \"No "
           "prediction\" marks a quantity the simulation does not give.", ""]
    out += p2_md(o["P2"])
    if o["P3"]:
        out += ["### P3, floating-ring potential", "",
                "| Structure | Dies | Onset at 1 V (V) | Agreement range (V) "
                "| Verdict | Top (V) | Step (V) | Step range (V) "
                "| Step verdict |", "|---|---|---|---|---|---|---|---|---|"]
        for r in o["P3"]:
            out.append(f"| {r['name']} | {r['dies']} | "
                       + (v(r["onset"]) if r["onset"] is not None
                          else f"none by {v(r['top'])}")
                       + f" | {rng(r.get('range'))} | {r['verdict']} | "
                       f"{v(r['top'])} | {v(r['step'])} | "
                       f"{pair(r.get('step_range'))} | {r['step_verdict']} |")
        out.append("")
    if o["P5"]:
        out += ["### P5, punch-through to a ring at 0 V", "",
                "| Structure | Dies | Punch-through at 1 nA (V) "
                "| Agreement range (V) | Verdict | Mechanism at the end |",
                "|---|---|---|---|---|---|"]
        for r in o["P5"]:
            got = v(r["pt"]) if r["pt"] is not None else f"none by {v(r['top'])}"
            out.append(f"| {r['name']} | {r['dies']} | {got} | "
                       f"{rng(r.get('range'))} | {r['verdict']} | "
                       f"{r['mech']} |")
        out.append("")
    out += p4_md(o)
    return out


def rng(r):
    if r is None:
        return "no prediction"
    return f"{r[1]:.1f} to " + ("no upper end" if r[2] is None
                                else f"{r[2]:.1f}")


def pair(r):
    return "–" if r is None else f"{r[0]:.1f} to {r[1]:.1f}"


def p2_md(c):
    out = ["### P2, capacitance against voltage", ""]
    if not c["pairs"] and not c["alone"]:
        return out + ["- No P2 records reduced.", ""]
    out += ["| Pair | Dies | Substrate doping (cm⁻³) | Against the simulation "
            "| Zero-bias area capacitance over the model | Ratio s | Bias (V) "
            "| Layer | Profile depth (µm) | Edge part at 0 V (fF/µm) |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for r in c["pairs"]:
        n = r["n_sub"]
        out.append(
            f"| {r['pair'][0]} and {r['pair'][1]} | {r['dies']} | "
            + ("–" if n is None else rules.sci(n))
            + f" | {rules.doping_rule(n)} | "
            + ("–" if r["r0"] is None else f"{r['r0']:.3f}") + " | "
            + ("–" if r["s"] is None else f"{r['s']:.3f}") + " | "
            + ("–" if r["v"] is None else f"{r['v']:g}") + " | "
            + (r["call"] or "no call") + " | "
            + ("–" if r["depth"] is None else f"{r['depth'] * 1e4:.2f}")
            + " | " + ("–" if r["cp0"] is None else f"{r['cp0'] * 1e15:.3f}")
            + " (published model "
            + f"{ph.NW_CP * 1e9:.3f}; no prediction) |")
    out += ["", f"- Layer call: **{c['call'] or 'none'}**: {c['why']}."]
    for name, n, c0 in c["alone"]:
        out.append(f"- {name}: {n} dies, "
                   + ("–" if c0 is None else f"{c0 * 1e12:.3f} pF")
                   + " at the first bias, OPEN subtracted; no partner to "
                   "separate the edge, and no prediction.")
    if c.get("nat") is not None:
        out.append(f"- CVNA over CVN2 at 0 V: {c['nat']:.3f}; what NAT "
                   "changes has no prediction.")
    out += [f"- {i}" for i in c["issues"]]
    return out + [""]


def p4_md(o):
    out = []
    if o["P4"]:
        out += ["### P4, gated diode: breakdown against plate voltage", "",
                "| Structure | Plate (V) | Breakdown, median (V) | Dies "
                "| Agreement range (V) | Verdict | Ratio to the plate "
                "joined: measured, predicted | Ratio verdict |",
                "|---|---|---|---|---|---|---|---|"]
        for r in o["P4"]:
            ratios = ("–" if "m_ratio" not in r else
                      f"{r['m_ratio']:.2f}, {r['p_ratio']:.2f}")
            out.append(f"| {r['name']} | {r['plate']:g} | {v(r['bv'])} | "
                       f"{r['dies']} | {pair(r.get('range'))} | "
                       f"{r['verdict']} | {ratios} | {r['ratio']} |")
        out.append("")
    if o["P4a"]:
        out += ["### P4, gated diode: current against plate voltage", "",
                "No simulation gives the flat-band voltage, the field "
                "threshold or the current step. The estimate is the "
                "threshold equation of method.rst with the nominal "
                "substrate doping and a flat-band voltage of −0.9 V, and "
                "carries no verdict.", "",
                "| Structure | Well (V) | Dies | Flat-band (V) "
                "| Field threshold (V) | Estimate, not a simulation (V) |",
                "|---|---|---|---|---|---|"]
        for r in o["P4a"]:
            out.append(f"| {r['name']} | {r['well']:g} | {r['dies']} | "
                       f"{v(r['vfb'])} | "
                       + (v(r["vt"]) if r["vt"] is not None
                          else "no fall in the range")
                       + " | " + (v(r["estimate"]) if r["estimate"] is not None
                                  else "P-well under the plate: none")
                       + " |")
        out.append("")
        for st, n, text in o["P4doping"]:
            out.append(f"- {st}: doping under the plate from the two "
                       "thresholds "
                       + ("–" if n is None else f"{rules.sci(n)} cm⁻³")
                       + f": {text}.")
        out.append("")
    return out


def p2(sweeps):
    c = cv.reduce(sweeps)
    c["nat"] = cv.nat_effect(sweeps)
    return c
