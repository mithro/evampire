"""Agreement rules of procedures P2 to P5 against the simulation.

method.rst states each rule and its basis; calc.py, section 5, prints the
numbers this module derives from the simulation records, and figures.py
writes hvt-tab-pt-range.csv from it. analyse.py applies the same
functions, so the page and the script cannot differ.

P2  layer_rule()    whether the area capacitance falls as under L or D,
                    from the ratios of model_checks.json ("capacitance").
    doping_rule()   a measured substrate doping against the dopings of the
                    simulated processes (predictions.json, "processes").
P3, P5  gap_fit(), pt_range(), pt_verdict()   a punch-through voltage
                    against the simulated one, through the equivalent gap.
P3  step_range()    the voltage held by the gap at the top of the sweep.
P4  gated_band()    the breakdown with the plate at 0 V (the G processes).

Standard library only.

SPDX-License-Identifier: Apache-2.0
"""

import math
import re

import measure
import pred_data as pd
import pred_extra as px
import tables as tb

# P2. The simulated N-well capacitance over the published model: under L
# a list against bias, under D a range over the whole sweep.
CAP = px.CHECKS["capacitance"]
CAP_L = dict(zip(CAP["volts"], CAP["without_layer"]))
CAP_D = tuple(float(x) for x in re.findall(r"\d+\.\d+", CAP["with_layer"]))
CAP_SEPARATION = 0.05  # least gap between the L value and the D range
SUB_FROM = 1.0         # V: profile windows centred below this are left out
WINDOW = 1.0           # V: width of the least-squares window of 1/C^2

# P3 and P5. GAP_TOL is one lateral spread of the N-well's deep part
# (0.29 um in tab-hvt-profiles, rounded), which no anchor fixes.
GAP_TOL = 0.3          # um of equivalent gap
STEP_TOL = (0.15, 1.0)  # the step: 15 % or 1 V, whichever is larger


def substrate_dopings():
    """{process: substrate doping in cm^-3} from the process descriptions
    of predictions.json."""
    out = {}
    for proc, text in pd.PRED["processes"].items():
        m = re.search(r"substrate ([0-9.]+e[0-9]+) cm", text)
        if m:
            out[proc] = float(m.group(1))
    return out


SUB = substrate_dopings()
SUB_NOMINAL = SUB["BL"]
SUB_RANGE = (min(SUB.values()), max(SUB.values()))


def sci(x):
    """3.56e15 written as 3.56e15, not 3.56e+15."""
    m, e = f"{x:.3g}".split("e") if "e" in f"{x:.3g}" else (f"{x:.3g}", "0")
    return f"{m}e{int(e)}"


def doping_rule(n):
    """Verdict on a measured substrate doping against the simulated ones."""
    if n is None:
        return "no value"
    f = n / SUB_NOMINAL
    span = f"{sci(SUB_RANGE[0])} to {sci(SUB_RANGE[1])} cm⁻³"
    if SUB_RANGE[0] <= n <= SUB_RANGE[1]:
        return (f"within the simulated range {span} ({f:.2f} times the "
                f"nominal {sci(SUB_NOMINAL)})")
    return (f"outside the simulated range {span}: {f:.2f} times the nominal "
            f"{sci(SUB_NOMINAL)}, so no simulated process has this doping")


def layer_rule(v):
    """(L value, lower end of D, threshold) of the capacitance at bias v
    over that at 0 V, each divided by the published model, or None where
    the two are not separated by CAP_SEPARATION."""
    if v not in CAP_L:
        return None
    l_norm = CAP_L[v] / CAP_L[0]
    d_low = CAP_D[0] / CAP_D[1]
    if d_low - l_norm < CAP_SEPARATION:
        return None
    return l_norm, d_low, (l_norm + d_low) / 2


def layer_bias(top):
    """The highest bias, up to `top`, at which layer_rule decides."""
    ok = [v for v in CAP_L if v <= top + 1e-9 and layer_rule(v)]
    return max(ok) if ok else None


def layer_call(s, v):
    """"L" or "D" from the normalised capacitance ratio s at bias v."""
    return "D" if s >= layer_rule(v)[2] else "L"


# P3 and P5: punch-through voltage V of a gap g follows V = k (g - g0)^2,
# so sqrt(V / k) is the gap beyond g0 and differences of it are gap errors.

def p5_entry(name, fam):
    """The p5.json entry of a structure under a family, with the stand-ins
    of pred_data (An is A where no NAT is drawn; under A, L serves for D)."""
    by = px.P5.get(name, {})
    tries = [fam]
    pw, deep = pd.parse(fam)[1:3]
    if pw == "An" and pd.STRUCTS[name]["nat_gap"] is None:
        tries.append("A" + deep)
        pw = "A"
    if pw == "A":
        tries.append("AL")
    return next((by[t] for t in tries if t in by), None)


def ring_prediction(name, proc):
    """(onset volts or None, highest simulated well volts) of ring 1 under
    one process, from ring_v; None if not simulated."""
    rv = pd.entry(name, proc).get("ring_v") if name in pd.STRUCTS else None
    if not rv:
        return None
    on = measure.linear_crossing([c[0] for c in rv], [c[1] for c in rv],
                                 measure.RING_LEVEL)
    return on, rv[-1][0]


def points(fam, which):
    """(gap um, volts) of every simulated punch-through under the nominal
    process of a family: which is "P5" (p5.json) or "P3" (ring_v)."""
    out = []
    for name, p in pd.STRUCTS.items():
        if not p["rings"]:
            continue
        if which == "P5":
            e = p5_entry(name, fam) if name in px.P5 else None
            v = e and e["punch_through_v"]
        else:
            r = ring_prediction(name, fam)
            v = r and r[0]
        if v:
            out.append((p["rings"][0][0], v))
    return out


def gap_fit(fam, which):
    """(k V/um^2, g0 um, family fitted): least squares of sqrt(V) on the
    gap, under B with the family's deep layer, where every gap is bare
    substrate; NAT gives the same values under An, and under A only one
    gap punches through before breakdown."""
    f = "B" + pd.parse(fam)[2]
    pts = points(f, which)
    xs, ys = [g for g, _ in pts], [math.sqrt(v) for _, v in pts]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    s = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) \
        / sum((x - mx) ** 2 for x in xs)
    return s * s, mx - my / s, f


def predicted_pt(name, fam, which):
    """(lowest volts or None, highest volts or None, bound volts or None):
    the band of the simulated punch-through over the family's processes.
    A process without punch-through gives a bound, the voltage its sweep
    reached; a band with a bound has no upper end."""
    vals, bounds = [], []
    if which == "P5":
        e = p5_entry(name, fam)
        if e:
            (vals if e["punch_through_v"] is not None else bounds).append(
                e["punch_through_v"] or e["reached_v"])
    else:
        for proc in pd.processes(fam):
            r = ring_prediction(name, proc)
            if r:
                (vals if r[0] is not None else bounds).append(r[0] or r[1])
    if not vals and not bounds:
        return None
    if not vals:
        return None, None, min(bounds)
    return min(vals), (None if bounds else max(vals)), \
        (min(bounds) if bounds else None)


def widen_gap(v, k, sign):
    """The voltage whose equivalent gap differs from that of v by GAP_TOL."""
    root = max(0.0, math.sqrt(v / k) + sign * GAP_TOL)
    return k * root * root


def pt_range(name, fam, which):
    """(predicted text, low volts, high volts or None) of the agreement
    range, or None where nothing is simulated."""
    pr, fit = predicted_pt(name, fam, which), gap_fit(fam, which)
    if pr is None or fit is None:
        return None
    lo, hi, bound = pr
    k = fit[0]
    if lo is None:
        return f"> {bound:.1f}", widen_gap(bound, k, -1), None
    text = f"{lo:.1f}" if hi == lo else (f"{lo:.1f} to {hi:.1f}" if hi
                                          else f"{lo:.1f} or none")
    return text, widen_gap(lo, k, -1), (widen_gap(hi, k, 1) if hi else None)


def pt_verdict(name, fam, which, measured, top):
    """Verdict on a measured punch-through voltage (None: none up to the
    highest well voltage `top`)."""
    rng, fit = pt_range(name, fam, which), gap_fit(fam, which)
    if rng is None:
        return "no prediction"
    _, lo, hi = rng
    k = fit[0]
    if measured is None:
        if hi is None or top <= hi:
            return ("agrees: none up to the end of the sweep" if hi is None
                    else f"inconclusive: the sweep ended at {top:.1f} V")
        return f"disagrees: none by {top:.1f} V, above the range"
    if lo <= measured and (hi is None or measured <= hi):
        return "agrees"
    edge = lo if measured < lo else hi
    dg = math.sqrt(measured / k) - math.sqrt(edge / k)
    return f"disagrees: equivalent gap {dg:+.2f} µm beyond the range"


def interp(curve, v):
    for (v0, r0), (v1, r1) in zip(curve, curve[1:]):
        if v0 <= v <= v1 and v1 > v0:
            return r0 + (v - v0) / (v1 - v0) * (r1 - r0)
    return None


def step_range(name, fam, top):
    """(low, high) volts of the agreement range of the P3 step at a well
    voltage `top`, or (None, reason)."""
    steps, ends = [], []
    for proc in pd.processes(fam):
        rv = pd.entry(name, proc).get("ring_v") if name in pd.STRUCTS else None
        if rv:
            ends.append(rv[-1][0])
            r = interp(rv, top)
            if r is not None:
                steps.append(top - r)
    if not steps:
        return None, ("no prediction" if not ends else
                      f"no prediction at {top:.1f} V: the simulated sweep "
                      f"ends at {max(ends):.1f} V")
    lo, hi = min(steps), max(steps)
    d = lambda x: max(STEP_TOL[0] * x, STEP_TOL[1])  # noqa: E731
    return lo - d(lo), hi + d(hi)


# P4: the breakdown with the plate at 0 V belongs to the G processes.

def gated_band(name, fam):
    """(low, high, joined) of the G band of a family and the nominal
    value with the plate joined to the well, or None."""
    procs = ["G" + p for p in pd.processes(fam)
             if "G" + p in pd.PRED["processes"]]
    lo, hi, _ = pd.band_of(procs or ["G" + fam], name)
    if lo is None:
        return None
    return lo, hi, pd.nominal(name, fam)


def pt_table():
    """hvt-tab-pt-range.csv: the agreement ranges of P3 and P5."""
    rows = [["Structure", "Family", "P3 predicted onset (V)",
             "P3 agreement range (V)", "P5 predicted (V)",
             "P5 agreement range (V)"]]
    for name in px.sense():
        fams = ["AL", "AnL", "AnD", "BL", "BD"] \
            if pd.STRUCTS[name]["nat_gap"] is not None else ["AL", "BL", "BD"]
        for fam in fams:
            cells = []
            for which in ("P3", "P5"):
                r = pt_range(name, fam, which)
                if r is None:
                    cells += ["–", "no prediction"]
                else:
                    cells += [r[0], f"{r[1]:.1f} to "
                              + ("no upper end" if r[2] is None
                                 else f"{r[2]:.1f}")]
            rows.append([name, fam] + cells)
    return tb.write(rows)


def tables():
    return {"hvt-tab-pt-range.csv": pt_table()}
