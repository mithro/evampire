"""Print the numbers the test-die pages quote in their worked examples.

Usage: uv run python docs/high-voltage/test-die/calc.py

Standard library only. Each section names the page and the equation it
supports. The published inputs are the gf180mcu N-well junction model
(nwp_6p0: 1.4914e-4 F/m^2, 5.8719e-10 F/m, 0.43905 V, grading 0.30525)
and the Metal1 and polysilicon capacitances to the substrate.

SPDX-License-Identifier: Apache-2.0
"""

import json
import math

import physics as ph
import tdkit


def head(s):
    print(f"\n== {s} ==")


def ionisation():
    head("1. predictions: ionisation integral of an abrupt junction")
    n = 1e16
    for v in (20, 30, 40, 50, 55, 60):
        w = ph.depletion_width(n, v)
        emax = ph.Q * n * w / ph.EPS
        print(f"  {v:3d} V: W = {w * 1e4:.2f} um, Emax = {emax:.3g} V/cm, "
              f"alpha_n(Emax) = {ph.alpha_n(emax):.3g} /cm, "
              f"alpha_p(Emax) = {ph.alpha_p(emax):.3g} /cm, "
              f"I_n = {ph.integral_abrupt(n, v):.3f}")
    for dop in (1e15, 3.5e15, 1e16, 1e17):
        bv = ph.breakdown_abrupt(dop)
        print(f"  N = {dop:.1e}: breakdown at {bv:.1f} V, "
              f"W = {ph.depletion_width(dop, bv) * 1e4:.2f} um")


def cv():
    head("2. method: capacitance of the large wells")
    structs, _ = tdkit.load()
    ca, cp, vbi, m = ph.NW_CA, ph.NW_CP, ph.NW_VBI, ph.NW_M   # F/m2, F/m
    got = {}
    for name in ("CVN", "CVN2"):
        p = structs[name]
        area, per = ph.octagon(p["half"], p["corner"])
        c = ca * area * 1e-12 + cp * per * 1e-6
        got[name] = (area, per, c)
        print(f"  {name}: area {area:.0f} um2, perimeter {per:.1f} um, "
              f"area part {ca * area * 1e-12 * 1e12:.3f} pF, edge part "
              f"{cp * per * 1e-6 * 1e12:.3f} pF, total {c * 1e12:.3f} pF")
    (a1, p1, c1), (a2, p2, c2) = got["CVN"], got["CVN2"]
    det = a1 * p2 - a2 * p1
    print(f"  solved back: Ca = {(c1 * p2 - c2 * p1) / det * 1e12:.4e} F/m2,"
          f" Cp = {(c2 * a1 - c1 * a2) / det * 1e6:.4e} F/m")
    # doping from the slope of 1/C^2 between 2 V and 10 V, area part of CVN
    area_cm2 = a1 * 1e-8
    cs = [ph.c_junction(ca * 1e-4, vbi, m, v) * area_cm2 for v in (2, 10)]
    slope = (1 / cs[1] ** 2 - 1 / cs[0] ** 2) / 8
    n = 2 / (ph.Q * ph.EPS * area_cm2 ** 2 * slope)
    print(f"  CVN area part: C(2 V) = {cs[0] * 1e12:.3f} pF, C(10 V) = "
          f"{cs[1] * 1e12:.3f} pF, slope of 1/C2 = {slope:.3e} F^-2/V, "
          f"N = {n:.2e} cm^-3")
    for v, c in zip((2, 10), cs):
        print(f"  depth at {v} V: {ph.EPS * area_cm2 / c * 1e4:.2f} um")
    print(f"  depth at 0 V: {ph.EPS / (ca * 1e-4) * 1e4:.2f} um")
    print(f"  Metal5 pad 100 x 100 um at 5.798 aF/um2: "
          f"{1e4 * 5.798e-18 * 1e15:.0f} fF")


def gated():
    head("3. method: field threshold under a plate with the well biased")
    for layer, cox in (("Metal1", ph.COX["m1"]), ("poly", ph.COX["poly"])):
        for n in (3.0e15, 4.8e15):
            row = [ph.field_threshold(n, cox, vr, ph.VFB_ILLUSTRATION)
                   for vr in (0, 5, 10)]
            print(f"  {layer}, N = {n:.1e}: VT at VR = 0, 5, 10 V: "
                  + ", ".join(f"{v:.1f}" for v in row) + " V")
    n, cox = 3.0e15, 2.9304e-9
    f2 = 2 * ph.phi_f(n)
    print(f"  phi_F = {ph.phi_f(n):.3f} V, 2 phi_F = {f2:.3f} V")
    for vr in (0, 5):
        qd = math.sqrt(2 * ph.EPS * ph.Q * n * (f2 + vr))
        print(f"  VR = {vr}: Qdep = {qd:.3e} C/cm2, Qdep/Cox = "
              f"{qd / cox:.2f} V")
    print(f"  shift from 1e11 cm^-2 of oxide charge: Metal1 "
          f"{ph.Q * 1e11 / 2.9304e-9:.1f} V, poly "
          f"{ph.Q * 1e11 / 1.1067e-8:.2f} V")


def currents():
    head("4. method: power, leakage and surface generation")
    print(f"  150 V x 10 uA = {150 * 10e-6 * 1e3:.1f} mW")
    structs, _ = tdkit.load()
    p = structs["NT20"]
    area, per = ph.octagon(p["half"], p["corner"])
    print(f"  NT20 well: area {area:.0f} um2, perimeter {per:.0f} um; "
          f"1 uA is {1e-6 / per * 1e9:.1f} nA per um of edge")
    r = structs["NR1S2"]
    gap, width = r["rings"][0]
    a_out, _ = ph.octagon(r["half"] + gap + width, r["corner"] + gap + width)
    a_in, _ = ph.octagon(r["half"] + gap, r["corner"] + gap)
    ring = a_out - a_in
    print(f"  NR1S2 ring 1: area {ring:.0f} um2; saturation current at "
          f"1.6119e-6 A/m2 = {1.6119e-6 * ring * 1e-12:.1e} A")
    g = structs["NGM1"]
    a_pl, _ = ph.octagon(g["half"] + g["plates"]["m1"],
                         g["corner"] + g["plates"]["m1"])
    a_w, _ = ph.octagon(g["half"], g["corner"])
    plate = a_pl - a_w
    for s0 in (1, 10, 100):
        i = ph.Q * ph.NI * s0 * plate * 1e-8
        print(f"  NGM1 plate beyond the well: {plate:.0f} um2; surface "
              f"generation at s0 = {s0} cm/s: {i * 1e15:.1f} fA")
    print(f"  plate capacitance to the surface: Metal1 "
          f"{plate * 0.0293:.1f} fF")
    print("  settling: 10 pF charged by 0.5 V at 1 pA takes "
          f"{10e-12 * 0.5 / 1e-12:.0f} s")
    print(f"  field in 0.32 um of trench oxide at 64 V: "
          f"{64 / 0.32e-4 / 1e6:.1f} MV/cm")


def agreement_rules():
    head("5. method: the agreement rules of P2 to P5 and the decision")
    import decide
    import pred_data as pd
    import rules
    for v in (5, 7, 10):
        r = rules.layer_rule(v)
        lv, dv = (c[v] / c[0] for c in (rules.CAP_L, rules.CAP_D))
        print(f"  P2 at {v:2d} V: L {lv:.4f}, D {dv:.4f}, separation "
              f"{dv - lv:.4f}: "
              + ("no call" if r is None else f"threshold {r[2]:.4f}"))
    c0 = ph.NW_CA * 1e-4
    print(f"  published model at 0 V: doping from the slope of 1/C2 "
          f"{ph.NW_VBI * c0 ** 2 / (ph.Q * ph.EPS * ph.NW_M):.2e} cm^-3")
    print(f"  substrate doping of the processes: "
          + ", ".join(f"{p} {n:.3g}" for p, n in sorted(rules.SUB.items())))
    vs = [0.25 * k for k in range(41)]
    ca = [ph.c_junction(ph.NW_CA * 1e-4, ph.NW_VBI, ph.NW_M, v) for v in vs]
    lcap = [c * rules.CAP_L[v] for v, c in zip(vs, ca) if v in rules.CAP_L]
    dcap = [c * rules.CAP_D[v] for v, c in zip(vs, ca) if v in rules.CAP_D]
    for name, cs, xs in (("model", ca, vs),
                         ("model times the L ratios", lcap,
                          sorted(rules.CAP_L)),
                         ("model times the D ratios", dcap,
                          sorted(rules.CAP_D))):
        n = [2 / (ph.Q * ph.EPS * (1 / c2 ** 2 - 1 / c1 ** 2) / (v2 - v1))
             for (v1, c1), (v2, c2) in zip(zip(xs, cs), zip(xs[1:], cs[1:]))
             if v1 >= 2 and v2 <= 5]
        print(f"  doping from 1/C2 between 2 V and 5 V, {name}: "
              f"{min(n):.2e} to {max(n):.2e} cm^-3")
    for v in (5, 7, 10):
        lo, thr, hi = rules.layer_window(v)
        print(f"  P2 at {v:2d} V: L from {lo:.3f} to {thr:.3f}, D from "
              f"{thr:.3f} to {hi:.3f}, neither outside")
    import cv
    import p1rules
    for deep in ("L", "D"):
        print(f"  P2 reduction of the simulated curve under {deep}: "
              f"{cv.reference_doping(deep):.3g} cm^-3")
    kp3 = rules.gap_fit("BL", "P3")[0]
    pts = rules.doping_points()
    v0 = dict(pts)[1.0]
    print(f"  doping scaling: edge shift {rules.EDGE_SHIFT:.3f} um per "
          f"e-fold; NR3_2 onsets " + ", ".join(
              f"{f:.3f} x nominal {v:.2f} V (proportional {v0 * f:.2f} V, "
              f"scaled {rules.pt_scaled(v0, f, kp3):.2f} V)" for f, v in pts))
    print(f"  doping range {rules.DOPE_RANGE[0]:.3f} to "
          f"{rules.DOPE_RANGE[1]:.3f} x nominal; die band 1 +- "
          f"{p1rules.DIE_BAND}; stand-ins within {p1rules.SAME_PRED}")
    for which in ("P5", "P3"):
        for fam in ("BL", "BD"):
            k, g0, f = rules.gap_fit(fam, which)
            print(f"  {which} under {f}: V = {k:.2f} V/um2 x (gap - "
                  f"{g0:.2f} um)^2 from " + ", ".join(
                      f"{g:g} um {v:.1f} V"
                      for g, v in sorted(set(rules.points(f, which)))))
    k = rules.gap_fit("BL", "P5")[0]
    for g, v in ((1.6, 1.4), (2.0, 3.8), (3.0, 13.2), (5.0, 55.1)):
        print(f"  {rules.GAP_TOL} um of gap at {g:g} um ({v} V): "
              f"{rules.widen_gap(v, k, -1):.1f} V to "
              f"{rules.widen_gap(v, k, 1):.1f} V")
    low = [pd.nominal(n, f) for f in ("AL", "AnL", "AnD", "BL", "BD")
           for n in ("NT20", "NW0", "NA0p6") if pd.nominal(n, f) < pd.REGIME]
    high = [pd.nominal(n, f) for f in ("AnL", "AnD", "BL", "BD")
            for n in ("NT20", "NA0p6") if pd.nominal(n, f) >= pd.REGIME]
    r = min(high) / max(low)
    print(f"  decision: heavy surface up to {max(low):.1f} V, light "
          f"substrate from {min(high):.1f} V: ratio {r:.2f}; geometric mean "
          f"with 1 + {decide.SAME[0]:g}: {math.sqrt(r * (1 + decide.SAME[0])):.2f}"
          f"; MUCH = {decide.MUCH:g}")


if __name__ == "__main__":
    ionisation()
    cv()
    gated()
    currents()
    agreement_rules()
    print()
    print(json.dumps({"structures": len(tdkit.load()[0])}))
