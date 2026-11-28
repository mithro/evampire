"""Write synthetic measurement records of the test die.

The records are SYNTHETIC: ideal diode sweeps whose breakdown voltage is
the prediction of predictions.json under one process, times a factor,
with a die-to-die spread drawn from a fixed seed, and capacitance sweeps
that follow the simulated curve of model_checks.json. They follow the record
format of method.rst (table tab-hvt-record), so that analyse.py can be
tried without silicon, and test_analyse.py uses them to check it. No
value in them is a measurement.

analyse.py --example and test_analyse.py call this module.

SPDX-License-Identifier: Apache-2.0
"""

import math
import pathlib
import random

import cv
import measure
import physics as ph
import pred_data as pd
import procs
import rules

STEP, TOP, LIMIT = 0.5, 150.0, 1e-5   # the settings of P1
SLOPE = 0.15           # V per e-fold of the avalanche current
NOTE = ("SYNTHETIC DATA. These files were written by synth.py from the "
        "predictions under process {hyp}, times {factor}, with a spread of "
        "{spread:.0%} between dies (seed {seed}). They are not "
        "measurements.\n")


def write(out, die, st, proc, idx, rows, temp=25.0, direction="up"):
    path = pathlib.Path(out) / f"{die}.{st}.{proc}.{idx}.csv"
    lines = [",".join(measure.COLUMNS)]
    for k, r in enumerate(rows):
        r = {"die": die, "structure": st, "procedure": proc, "sweep": idx,
             "direction": direction, "temperature_c": temp,
             "time_s": round(0.1 * k, 3), **r}
        lines.append(",".join("" if r.get(c) is None else
                              (f"{r[c]:.6g}" if isinstance(r[c], float)
                               else str(r[c])) for c in measure.COLUMNS))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def diode(bv, leak=1e-12, short=False, aux=None, back=1.0):
    """Rows of a breakdown sweep: 0 V upwards in 0.5 V steps until the
    current reaches the limit or the voltage 150 V. bv None: no breakdown.
    back is the fraction of the well current that the substrate returns."""
    rows = []
    for k in range(int(TOP / STEP) + 1):
        v = k * STEP
        i = leak * (1 + v / 50)
        if short:
            i += v / 1e4
        if bv is not None:
            i += 1e-6 * math.exp(min((v - bv) / SLOPE, 50))
        i = min(i, LIMIT)
        rows.append({"v_well_v": v, "i_well_a": i, "i_sub_a": -back * i,
                     **(aux or {})})
        if i >= LIMIT:
            break
    return rows


def ring_rows(bv, curve, factor):
    """P3: the ring voltage follows the predicted rise of ring 1."""
    rows = diode(bv)
    pts = [(v * factor, r * factor) for v, r in curve]
    for r in rows:
        v = r["v_well_v"]
        rise = 0.0
        for (v0, r0), (v1, r1) in zip(pts, pts[1:]):
            if v0 <= v <= v1 and v1 > v0:
                rise = r0 + (v - v0) / (v1 - v0) * (r1 - r0)
        if pts and v > pts[-1][0]:
            rise = pts[-1][1] + (v - pts[-1][0])
        r["v_aux_v"], r["i_aux_a"] = round(rise, 4), 0.0
    return rows


def p5_rows(pt, bv):
    """P5: ring current from punch-through at pt, substrate current from
    avalanche at bv; either may be None."""
    rows = []
    for k in range(int(TOP / STEP) + 1):
        v = k * STEP
        ring = 1e-15 if pt is None else 1e-9 * math.exp(min((v - pt) / 0.4, 50))
        sub = 1e-12 + (0 if bv is None else
                       1e-6 * math.exp(min((v - bv) / SLOPE, 50)))
        scale = min(1.0, LIMIT / (ring + sub))   # the limit holds the sum
        ring, sub = ring * scale, sub * scale
        well = ring + sub
        rows.append({"v_well_v": v, "i_well_a": well, "i_sub_a": -sub,
                     "v_aux_v": 0.0, "i_aux_a": -ring})
        if well >= LIMIT * 0.999:
            break
    return rows


def make(out, hyp, factor=1.0, dies=5, spread=0.03, seed=1, sweeps=1,
         extra=False, edits=None, dope=1.0):
    """Write a measurement set under process `hyp` into out, with the
    substrate doping dope times the nominal in P2 and P5. edits maps
    (structure, die number or None for every die) to "short", "none" (no
    breakdown), "drop" (no file) or "leak" (the substrate returns 70 % of
    the well current). Returns {(structure, die): the
    breakdown voltage written, or None}."""
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rnd, edits, truth = random.Random(seed), edits or {}, {}
    names = [s["name"] for s in pd.MAN["sites"]]
    for k in range(1, dies + 1):
        die = f"SYN{k}"
        for st in names:
            what = edits.get((st, k), edits.get((st, None)))
            nom = pd.nominal(st, hyp)
            jitter = 1 + rnd.gauss(0, spread)
            bv = None if nom is None or what == "none" else nom * factor * jitter
            if bv is not None and bv > TOP:
                bv = None
            if what == "drop":
                continue
            truth[(st, die)] = None if what == "short" else bv
            leak = 1e-13 if st == "OPEN" else 1e-12
            for idx in range(1, sweeps + 1):
                walk = 0.1 * (idx - 1) if bv is not None else 0
                write(out, die, st, "P1", idx,
                      diode(None if bv is None else bv + walk, leak,
                            what == "short", back=0.7 if what == "leak"
                            else 1.0))
            if extra:
                extras(out, die, st, hyp, factor, bv, sweeps, dope)
    if extra:
        (out / "README.txt").write_text(NOTE.format(
            hyp=hyp, factor=factor, spread=spread, seed=seed),
            encoding="utf-8")
    return truth


def extras(out, die, st, hyp, factor, bv, sweeps, dope=1.0):
    """The P2 to P5 records and an 85 C sweep for one structure on a die."""
    p = pd.STRUCTS[st]
    idx = sweeps + 1
    if st == "NT20" and bv is not None:
        write(out, die, st, "P1", idx, diode(bv * 1.04), temp=85.0)
    if p["sense"]:
        curve = (pd.entry(st, hyp) or {}).get("ring_v") or []
        write(out, die, st, "P3", 1, ring_rows(bv, curve, factor))
        e = rules.p5_entry(st, hyp) or {}
        pt, b5 = e.get("punch_through_v"), e.get("breakdown_v")
        k = rules.gap_fit(hyp, "P5")[0]
        write(out, die, st, "P5", 1, p5_rows(
            None if pt is None else rules.pt_scaled(pt, dope, k) * factor,
            None if b5 is None else b5 * factor))
    if p["half"] >= 50 or st == "OPEN":
        write(out, die, st, "P2", 1, cv_rows(st, pd.parse(hyp)[2], dope))
    if p["gate"]:
        gated(out, die, st, hyp, factor, bv)


# P2: the area part is the published model times the simulated ratio of
# cv.sim_ratio (L: 0.83 at 10 V; D: 1), linear between the documented
# biases; a doping dope times the nominal multiplies it by sqrt(dope), as
# for a one-sided junction, so 1/C^2 falls by dope. The edge part is the
# published model, and OPEN_C is the pad, lead and probe.
OPEN_C = 0.15e-12      # F


def cv_rows(st, deep, dope=1.0, top=10.0):
    """P2 rows of a large well or OPEN under deep layer "L" or "D"."""
    volts = [0.25 * k for k in range(int(top / 0.25) + 1)]
    area, per = (0, 0) if st == "OPEN" else ph.octagon(
        pd.STRUCTS[st]["half"], pd.STRUCTS[st]["corner"])
    rows = []
    for v in volts:
        ca = cv.model(v) * cv.sim_ratio(deep, v) * math.sqrt(dope)
        c = OPEN_C + ca * area * 1e-8 + ph.c_junction(
            ph.NW_CP * 1e-6, ph.NW_VBI, ph.NW_M, v) * per
        for f in (1e5, 1e6):
            rows.append({"v_well_v": v, "c_f": c, "d": 0.01, "freq_hz": f})
    return rows


def gated(out, die, st, hyp, factor, bv):
    """P4: plate sweeps at two well voltages, then breakdown sweeps with
    the plate at 0 V (the G prediction) and at +10 V."""
    layer = next(iter(pd.STRUCTS[st]["plates"]))
    cox = ph.COX[layer]
    wells, low = ((0.0, 2.0), -10.0) if layer == "poly" else ((2.0, 5.0), -20.0)
    pwell = procs.surface_is_pwell(st, hyp)
    for idx, vr in enumerate(wells, start=1):
        vt = None if pwell else ph.field_threshold(
            rules.SUB_NOMINAL, cox, vr, ph.VFB_ILLUSTRATION)
        rows = []
        for k in range(int((60.0 - low) / 0.25) + 1):
            vp = low + 0.25 * k
            i = 1e-14 + 2e-13 / (1 + math.exp(-(vp - ph.VFB_ILLUSTRATION)
                                               / 0.3))
            if vt is not None:
                i -= 1.4e-13 / (1 + math.exp(-(vp - vt) / 0.3))
            rows.append({"v_well_v": vr, "i_well_a": i, "v_aux_v": vp,
                         "i_aux_a": 0.0})
        write(out, die, st, "P4", idx, rows)
    g = pd.band_of(["G" + hyp], st)[0]
    for idx, plate in ((3, 0.0), (4, 10.0)):
        b = None if g is None else g * factor * (1 + 0.1 * plate / 10)
        write(out, die, st, "P4", idx, diode(b, aux={"v_aux_v": plate,
                                                     "i_aux_a": 0.0}))
