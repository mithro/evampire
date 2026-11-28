"""Agreement rules of procedures P2 to P5 against the simulation.

method.rst states each rule and its basis; calc.py, section 5, prints the
numbers this module derives from the simulation records, and figures.py
writes hvt-tab-pt-range.csv from it. analyse.py applies the same
functions, so the page and the script cannot differ.

P2  layer_rule(), layer_call()   whether the area capacitance falls as
                    under L, as under D, or as under neither, from the
                    ratios of model_checks.json ("capacitance").
    doping_rule()   a measured substrate doping against the dopings of the
                    simulated processes (predictions.json, "processes").
P3, P5  gap_fit(), pt_range(), pt_verdict()   a punch-through voltage
                    against the simulated one, through the equivalent gap,
                    scaled to the substrate doping by pt_scaled().
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

# P2. The simulated N-well capacitance over the published model against
# bias, under L and under D (gf180-tcad record capacitance.json).
CAP = px.CHECKS["capacitance"]
CAP_L = dict(zip(CAP["volts"], CAP["without_layer"]))
CAP_D = dict(zip(CAP["volts"], CAP["with_layer"]))
CAP_SEPARATION = 0.05  # least gap between the L and D values of s
CAP_TOL = 0.05         # error of s: 2.5 % in reading, OPEN or area
SUB_FROM = 1.0         # V: profile windows centred below this are left out
WINDOW = 1.0           # V: width of the least-squares window of 1/C^2

# P3 and P5. The gap has two N-well edges, each with a lateral spread of
# 0.29 um (tab-hvt-profiles) that no anchor fixes. Both edges come from
# one implant and anneal, so an error in that spread moves both alike and
# the gap by twice it: 2 x 0.29 um, rounded.
GAP_TOL = 0.6          # um of equivalent gap
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
    """(s under L, s under D, threshold half-way) at bias v: the simulated
    capacitance over the published model, divided by the same at 0 V; None
    where the two are not separated by CAP_SEPARATION."""
    if v not in CAP_L or v == 0:
        return None
    l_norm, d_norm = CAP_L[v] / CAP_L[0], CAP_D[v] / CAP_D[0]
    if d_norm - l_norm < CAP_SEPARATION:
        return None
    return l_norm, d_norm, (l_norm + d_norm) / 2


def layer_bias(top):
    """The highest bias, up to `top`, at which layer_rule decides."""
    ok = [v for v in CAP_L if v <= top + 1e-9 and layer_rule(v)]
    return max(ok) if ok else None


def layer_window(v):
    """(lowest s of L, threshold, highest s of D) at bias v: each simulated
    value widened by CAP_TOL."""
    l_norm, d_norm, thr = layer_rule(v)
    return l_norm - CAP_TOL, thr, d_norm + CAP_TOL


def layer_call(s, v):
    """"L", "D" or "neither" from the normalised capacitance ratio s at
    bias v."""
    lo, thr, hi = layer_window(v)
    if s < lo or s > hi:
        return "neither"
    return "D" if s >= thr else "L"


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


def nominal_pt(name, fam, which):
    """([punch-through volts], [bound volts]) of the family's processes on
    the nominal substrate; a process without punch-through gives a bound,
    the voltage its sweep reached."""
    vals, bounds = [], []
    if which == "P5":
        e = p5_entry(name, fam)
        if e:
            (vals if e["punch_through_v"] is not None else bounds).append(
                e["punch_through_v"] or e["reached_v"])
    else:
        for proc in pd.processes(fam):
            r = ring_prediction(name, proc) if SUB.get(
                proc, SUB_NOMINAL) == SUB_NOMINAL else None
            if r:
                (vals if r[0] is not None else bounds).append(r[0] or r[1])
    return vals, bounds


def predicted_pt(name, fam, which, f=1.0):
    """(lowest volts or None, highest volts or None, bound volts or None):
    the band of the simulated punch-through over the family's processes,
    scaled to a substrate doping f times the nominal, or over DOPE_RANGE
    when f is None. A band with a bound has no upper end."""
    vals, bounds = nominal_pt(name, fam, which)
    if not vals and not bounds:
        return None
    k = gap_fit(fam, which)[0]
    fs = DOPE_RANGE if f is None else (f,)
    vals = [pt_scaled(v, x, k) for v in vals for x in fs]
    bounds = [pt_scaled(v, x, k) for v in bounds for x in fs]
    if not vals:
        return None, None, min(bounds)
    return min(vals), (None if bounds else max(vals)), \
        (min(bounds) if bounds else None)


def widen_gap(v, k, sign):
    """The voltage whose equivalent gap differs from that of v by GAP_TOL."""
    root = max(0.0, math.sqrt(v / k) + sign * GAP_TOL)
    return k * root * root


def pt_range(name, fam, which, f=1.0):
    """(predicted text, low volts, high volts or None) of the agreement
    range at doping factor f (None: unknown), or None where nothing is
    simulated."""
    pr, fit = predicted_pt(name, fam, which, f), gap_fit(fam, which)
    if pr is None or fit is None:
        return None
    lo, hi, bound = pr
    k = fit[0]
    if lo is None:
        return f"> {bound:.1f}", widen_gap(bound, k, -1), None
    text = f"{lo:.1f}" if hi == lo else (f"{lo:.1f} to {hi:.1f}" if hi
                                          else f"{lo:.1f} or none")
    return text, widen_gap(lo, k, -1), (widen_gap(hi, k, 1) if hi else None)


def pt_verdict(name, fam, which, measured, top, f=1.0):
    """Verdict on a measured punch-through voltage (None: none up to the
    highest well voltage `top`) at doping factor f (None: unknown)."""
    rng, fit = pt_range(name, fam, which, f), gap_fit(fam, which)
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


# Substrate doping. For a uniform substrate the gap punches through when
# V = (q N / 2 eps) g_e^2, so V scales with N at a fixed effective gap g_e.
# g_e itself grows with N, because each metallurgical edge sits where the
# graded N-well falls to N: by EDGE_SHIFT um per e-fold of N, fitted to the
# one gap simulated at three dopings (NR3_2 under BLlo, BL and BLhi, P3).

def doping_points():
    """[(N / nominal, onset volts)] of NR3_2 under BL and its doping
    variants, from ring_v."""
    out = []
    for proc in ("BLlo", "BL", "BLhi"):
        r = ring_prediction("NR3_2", proc)
        if r and r[0]:
            out.append((SUB[proc] / SUB_NOMINAL, r[0]))
    return out


def edge_shift():
    """um of effective gap per e-fold of doping, least squares through the
    nominal point."""
    k = gap_fit("BL", "P3")[0]
    pts = doping_points()
    g0 = next(math.sqrt(v / k) for f, v in pts if f == 1)
    xs = [math.log(f) for f, _ in pts if f != 1]
    ys = [math.sqrt(v / (k * f)) - g0 for f, v in pts if f != 1]
    return sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)


EDGE_SHIFT = edge_shift()
DOPE_RANGE = (SUB_RANGE[0] / SUB_NOMINAL, SUB_RANGE[1] / SUB_NOMINAL)


def pt_scaled(v, f, k, shift=EDGE_SHIFT):
    """Punch-through voltage v of the nominal substrate moved to a doping
    f times the nominal."""
    g = max(0.0, math.sqrt(v / k) + shift * math.log(f))
    return k * f * g * g


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
    """hvt-tab-pt-range.csv: the agreement ranges of P3 and P5 on the
    nominal substrate, and those of P5 when P2 gives no doping."""
    rows = [["Structure", "Family", "P3 predicted onset (V)",
             "P3 agreement range (V)", "P5 predicted (V)",
             "P5 agreement range (V)",
             "P5 agreement range, doping not measured (V)"]]

    def text(r):
        return "no prediction" if r is None else (
            f"{r[1]:.1f} to " + ("no upper end" if r[2] is None
                                 else f"{r[2]:.1f}"))
    for name in px.sense():
        fams = ["AL", "AnL", "AnD", "BL", "BD"] \
            if pd.STRUCTS[name]["nat_gap"] is not None else ["AL", "BL", "BD"]
        for fam in fams:
            cells = []
            for which in ("P3", "P5"):
                r = pt_range(name, fam, which)
                cells += ["–" if r is None else r[0], text(r)]
            rows.append([name, fam] + cells
                        + [text(pt_range(name, fam, "P5", None))])
    return tb.write(rows)


def tables():
    return {"hvt-tab-pt-range.csv": pt_table()}
