"""Reduce the capacitance sweeps of procedure P2 (method.rst, hvt-p2).

For each die and each pair of N-wells of one kind and two sizes (CVN with
CVN2, CVNA2 with CVNA): OPEN is subtracted at each bias, the area and edge
parts are separated, and the area part gives the doping against depth
from the slope of 1/C^2. The substrate doping and the layer call follow
the rules of rules.py. CVD has no partner and is reported alone.

analyse.py calls reduce(). Standard library only.

SPDX-License-Identifier: Apache-2.0
"""

import statistics

import physics as ph
import pred_data as pd
import rules

PAIRS = (("CVN", "CVN2"), ("CVNA2", "CVNA"))   # (large, small)
ALONE = ("CVD",)
FREQ_AGREE = 0.01      # 100 kHz and 1 MHz differ by more: series resistance
D_MAX = 0.1            # largest dissipation factor


def geometry(name):
    """(area um^2, perimeter um) of a well as drawn."""
    p = pd.STRUCTS[name]
    return ph.octagon(p["half"], p["corner"])


def curve(sw, freq):
    """[(bias, C)] of a sweep at one frequency, in order of bias."""
    return sorted((r["v_well_v"], r["c_f"]) for r in sw.rows
                  if r["freq_hz"] == freq)


def at(pts, v):
    """C at bias v, linear between readings; None outside them."""
    for (v0, c0), (v1, c1) in zip(pts, pts[1:]):
        if v0 <= v <= v1 and v1 > v0:
            return c0 + (v - v0) / (v1 - v0) * (c1 - c0)
    return pts[0][1] if pts and abs(pts[0][0] - v) < 1e-9 else None


def checks(sw):
    """Problems of one P2 sweep: dissipation factor and frequency."""
    out = []
    high = sum(1 for r in sw.rows if r["d"] > D_MAX)
    if high:
        out.append(f"{high} readings with a dissipation factor above {D_MAX}")
    freqs = sorted({r["freq_hz"] for r in sw.rows})
    if len(freqs) >= 2:
        lo, hi = curve(sw, freqs[0]), curve(sw, freqs[-1])
        worst = max((abs(c / at(hi, v) - 1) for v, c in lo
                     if at(hi, v)), default=0)
        if worst > FREQ_AGREE:
            out.append(f"readings at {freqs[0]:g} Hz and {freqs[-1]:g} Hz "
                       f"differ by up to {100 * worst:.1f} %")
    return out


def model(v):
    """Area capacitance of the published model, F/cm^2."""
    return ph.c_junction(ph.NW_CA * 1e-4, ph.NW_VBI, ph.NW_M, v)


def profile(vs, ca):
    """[(bias, depth cm, doping cm^-3)] from the area capacitance ca
    (F/cm^2) at biases vs: the slope of 1/C^2 by least squares over a
    window of rules.WINDOW volts round each bias."""
    out = []
    for k, vc in enumerate(vs):
        win = [(v, 1 / c ** 2) for v, c in zip(vs, ca)
               if abs(v - vc) <= rules.WINDOW / 2 + 1e-9]
        if len(win) < 3 or win[0][0] > vc - rules.WINDOW / 2 + 1e-9 \
                or win[-1][0] < vc + rules.WINDOW / 2 - 1e-9:
            continue
        mx = sum(v for v, _ in win) / len(win)
        my = sum(y for _, y in win) / len(win)
        slope = sum((v - mx) * (y - my) for v, y in win) \
            / sum((v - mx) ** 2 for v, _ in win)
        if slope > 0:
            out.append((vc, ph.EPS / ca[k], 2 / (ph.Q * ph.EPS * slope)))
    return out


def die_pair(big, small, opn):
    """The reduction of one pair on one die, as a dict."""
    freq = min(r["freq_hz"] for r in big.rows)
    cb, cs, co = curve(big, freq), curve(small, freq), curve(opn, freq)
    (a1, p1), (a2, p2) = geometry(big.structure), geometry(small.structure)
    det = a1 * p2 - a2 * p1
    vs, ca, cp = [], [], []
    for v, c1 in cb:
        c2, c0 = at(cs, v), at(co, v)
        if c2 is None or c0 is None:
            continue
        c1, c2 = c1 - c0, c2 - c0
        vs.append(v)
        ca.append((c1 * p2 - c2 * p1) / det * 1e8)      # F/um^2 to F/cm^2
        cp.append((c2 * a1 - c1 * a2) / det)            # F/um
    if len(vs) < 2 or vs[0] > 1e-9 or min(ca) <= 0:
        return None
    prof = profile(vs, ca)
    deep = [n for v, _, n in prof if v >= rules.SUB_FROM - 1e-9]
    r0 = ca[0] / model(0)
    s = {v: at(list(zip(vs, ca)), v) / model(v) / r0 for v in rules.CAP_L
         if rules.layer_rule(v) and v <= vs[-1] + 1e-9}
    return {"n_sub": min(deep) if deep else None, "s": s,
            "v": rules.layer_bias(vs[-1]),
            "r0": r0, "cp0": cp[0], "depth": prof[-1][1] if prof else None,
            "top": vs[-1], "freq": freq}


def first(sweeps):
    """{(structure, die): the first P2 sweep at 25 C}."""
    out = {}
    for w in sorted(sweeps, key=lambda w: w.sweep):
        if w.procedure == "P2" and w.room:
            out.setdefault((w.structure, w.die), w)
    return out


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def reduce(sweeps):
    """{"pairs": [...], "alone": [...], "issues": [...], "call": L, D or
    None, "why": reason}."""
    f = first(sweeps)
    issues = [f"{st} on {d}: {p}" for (st, d), w in sorted(f.items())
              for p in checks(w)]
    pairs = []
    for big, small in PAIRS:
        dies = sorted({d for (st, d) in f if st == big})
        got = {}
        for d in dies:
            ws = [f.get((n, d)) for n in (big, small, "OPEN")]
            if None in ws:
                issues.append(f"{big} on {d}: "
                              + ", ".join(n for n, w in zip(
                                  (small, "OPEN"), ws[1:]) if w is None)
                              + " not measured there; not reduced")
                continue
            r = die_pair(*ws)
            if r is None:
                issues.append(f"{big} and {small} on {d}: no common bias "
                              "from 0 V, or a negative area part")
            else:
                got[d] = r
        if not got:
            continue
        row = {"pair": (big, small), "dies": len(got)}
        for key in ("n_sub", "r0", "cp0", "depth", "top"):
            row[key] = med([r[key] for r in got.values()])
        vstars = [r["v"] for r in got.values()]
        row["v"] = None if None in vstars else min(vstars)
        row["s"] = med([r["s"][row["v"]] for r in got.values()]) \
            if row["v"] else None
        row["call"] = rules.layer_call(row["s"], row["v"]) \
            if row["v"] and row["s"] is not None else None
        pairs.append(row)
    alone = []
    for name in ALONE:
        cs = [(d, w) for (st, d), w in f.items() if st == name]
        if cs:
            c0 = [w.rows[0]["c_f"] - (at(curve(f[("OPEN", d)], w.rows[0][
                "freq_hz"]), w.rows[0]["v_well_v"]) or 0)
                  if ("OPEN", d) in f else None for d, w in cs]
            alone.append((name, len(cs), med(c0)))
    calls = {r["call"] for r in pairs if r["call"]}
    if len(calls) == 1:
        call = calls.pop()
        why = "the area capacitance falls as under " + call + " (" + \
            "; ".join(f"{r['pair'][0]} and {r['pair'][1]}: "
                      f"{r['s']:.3f} at {r['v']:g} V against a threshold of "
                      f"{rules.layer_rule(r['v'])[2]:.3f}"
                      for r in pairs if r["call"]) + ")"
    elif calls:
        call, why = None, "the two pairs of large wells disagree"
    else:
        call = None
        why = ("no pair of large wells reduced to a bias where L and D "
               "separate" if pairs else "no P2 records of the large wells")
    return {"pairs": pairs, "alone": alone, "issues": issues, "call": call,
            "why": why}


def nat_effect(sweeps):
    """CVNA over CVN2 at 0 V, median over the dies, or None; the two have
    the same area and perimeter, so the ratio shows what NAT changes."""
    f = first(sweeps)
    rs = []
    for (st, d), w in f.items():
        if st == "CVNA" and ("CVN2", d) in f and ("OPEN", d) in f:
            o = f[("OPEN", d)].rows[0]["c_f"]
            a, b = w.rows[0]["c_f"] - o, f[("CVN2", d)].rows[0]["c_f"] - o
            if b > 0:
                rs.append(a / b)
    return med(rs)
