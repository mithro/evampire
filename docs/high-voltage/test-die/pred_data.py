"""Read predictions.json and crosscheck.json and write their tables.

hvt-tab-pred-a.csv, -b.csv, -g.csv  predicted breakdown by structure, one
                      column per process, as "edge / corner".
hvt-tab-pred-band.csv   band of each structure under each family.
hvt-tab-pred-key.csv    a few structures that carry the main findings.
hvt-tab-processes.csv, hvt-tab-pred-source.csv   what was simulated.
hvt-tab-crosscheck.csv, hvt-tab-crosscheck-ring.csv and
hvt-tab-crosscheck-source.csv   the second simulator.

predictions.json is written by import_predictions.py: {"structures":
{NAME: {PROCESS: {"edge": volts or null, "corner": volts or null,
"reached": {shape: volts}, "ring_v": [[well volts, ring 1 rise], ...]}}},
"processes": {PROCESS: description}, "source": {...}}. A null voltage with
a "reached" entry is a sweep that ended at that voltage without breakdown;
a null without one was not simulated.

A process name is [G] + A, An or B + L or D + an optional modifier. A, An
and B say where the P-well is; L puts the deep P layer under deep N-well
only and D under the whole wafer; G holds the gated plate at 0 V. A family
is the first two parts, such as BL, and its modifiers (BLq) belong to it;
G processes are in no family. Under A no structure on an N-well is
simulated with D, because the layer cannot matter there: the L entry is
used for both. The band of a structure is the lowest to the highest
value, over a family, of the lower of the edge and corner voltages. A
process whose sweep ended on one shape below the breakdown of the other
is left out, since its lower value is not known, and so is a process one
of whose runs gave no result. figures.py calls this module.

SPDX-License-Identifier: Apache-2.0
"""

import json

import tables as tb
import tdkit

STRUCTS, MAN = tdkit.load()
PRED = json.loads((tdkit.HERE / "predictions.json").read_text())
CROSS = json.loads((tdkit.HERE / "crosscheck.json").read_text())

# Agreement range: each end of the band is widened down and up by the rule
# for its own value. The ionisation model reads high where a heavily doped
# surface limits (below REGIME volts) and low where the lightly doped
# substrate does (model_checks.json, "one_sided"). The widths are choices.
REGIME = 30.0
WIDEN_LOW = (0.30, 0.15)    # predicted value below REGIME
WIDEN_HIGH = (0.15, 0.25)   # predicted value of REGIME or above
RATIO = 0.15           # agreement of a ratio to the reference structure
SHAPES = ("edge", "corner")
ORDER = ("AL", "AD", "AnL", "AnD", "BL", "BD")
KEY = [("NT20", "Plain N-well"), ("NT1", "P+ ring 1 µm away"),
       ("NC15", "Largest corner cut"), ("NC0", "Sharp corner"),
       ("NM1_6C0", "Sharp corner under a Metal1 plate, 6 µm"),
       ("NW0", "Drawn P-well touching"), ("NW1p5", "Drawn P-well at 1.5 µm"),
       ("NW3", "Drawn P-well at 3 µm"), ("NA0p6", "NAT from 0.6 µm"),
       ("NP4", "Polysilicon plate, 4 µm"), ("NM1_6", "Metal1 plate, 6 µm"),
       ("NM2_12", "Metal2 plate, 12 µm"), ("NR1_2", "One ring at 2 µm"),
       ("NR3_2", "Three rings"), ("NAR1_2", "One ring under NAT"),
       ("NAR3_2", "Three rings under NAT"), ("DT20", "Deep N-well"),
       ("DAo1", "Deep N-well with NAT over its edge")]


def parse(proc):
    """(gated, P-well letters, deep-layer letter, modifier)."""
    gated = proc.startswith("G")
    base = proc[1:] if gated else proc
    pw = "An" if base.startswith("An") else base[0]
    return gated, pw, base[len(pw)], base[len(pw) + 1:]


def family(proc):
    gated, pw, deep, _ = parse(proc)
    return "G" if gated else pw + deep


def processes(fam):
    return [p for p in PRED["processes"] if family(p) == fam]


def families():
    return [f for f in ORDER if processes(f)]


def ordered():
    order = [s["name"] for s in MAN["sites"]]
    return [n for n in order if n in PRED["structures"]]


def off_die():
    """Structures in predictions.json that are no longer on the die; their
    results are left out of every table and figure."""
    order = {s["name"] for s in MAN["sites"]}
    return sorted(set(PRED["structures"]) - order)


def raw(name, proc):
    return PRED["structures"].get(name, {}).get(proc) or {}


def stands_in(name, proc):
    """The process whose entry serves for a missing one, or None. An
    equals A on a structure without NAT, and on an N-well under A the L
    entry serves for D."""
    gated, pw, deep, mod = parse(proc)
    if raw(name, proc) or name not in STRUCTS:
        return None
    g = "G" if gated else ""
    tries = []
    if pw == "An" and STRUCTS[name]["nat_gap"] is None:
        tries.append(g + "A" + deep + mod)
        pw = "A"
    if pw == "A" and deep == "D" and STRUCTS[name]["kind"] == "nw":
        tries.append(g + "AL" + mod)
    for twin in tries:
        if raw(name, twin):
            return twin
    return None


def served(name, fam):
    """The families that the entry of family `fam` stands for, itself
    first."""
    return [fam] + [f for f in ORDER if f != fam and stands_in(name, f) == fam]


# The structures whose measured values are averaged, die by die, to give a
# reference's measured value; a reference not named here is measured alone.
REF_MEMBERS = {"NW0": ("NW0", "NW0b")}


def reference(name, fam):
    """The structure whose breakdown a ratio is taken against: DT20 for a
    deep N-well; under A, NW0 (measured as the mean of NW0 and NW0b); under
    An, NA0p6 for every other structure under NAT, since NT20 is limited
    by P-well there and NA0p6 is not; NT20 otherwise."""
    p = STRUCTS[name]
    if p["kind"] == "dnw":
        return "DT20"
    if parse(fam)[1] == "A":
        return "NW0"
    if parse(fam)[1] == "An" and p["nat_gap"] is not None \
            and name not in ("NA0p6", "NA0p6b"):
        return "NA0p6"
    return "NT20"


def nominal(name, fam):
    """Lower of the edge and corner values of a family's nominal process,
    or None if it is not resolved."""
    lo, hi, _ = band_of([fam], name)
    return lo


def ratio_value(name, fam):
    """(reference, predicted ratio or None, whether the ratio is a test).
    A ratio across the two regimes, one value below REGIME and the other
    not, is not a test."""
    ref = reference(name, fam)
    if ref == name:
        return ref, 1.0, True
    a, b = nominal(name, fam), nominal(ref, fam)
    if not (a and b):
        return ref, None, False
    return ref, a / b, (a < REGIME) == (b < REGIME)


def ratio_agrees(measured, predicted):
    """True when a measured ratio lies within RATIO of the predicted one."""
    return abs(measured / predicted - 1) <= RATIO


def ratio(name, fam):
    ref, r, test = ratio_value(name, fam)
    if ref == name:
        return ref, "1 (reference)"
    if r is None:
        return ref, "–"
    if not test:                        # one limited by a heavy surface
        return ref, f"{r:.2f}, across regimes: not a test"
    return ref, f"{r:.2f}"


def entry(name, proc):
    return raw(name, proc) or raw(name, stands_in(name, proc) or "")


def lost():
    """Cases the records list as having given no result, as (structure,
    process, shape) in the naming of predictions.json."""
    out = set()
    for rec in PRED.get("source", {}).get("records", []):
        for case in rec.get("not_converged", []):
            st, proc, shape = case.split("|")
            if st.endswith("@g0"):
                st, proc = st[:-3], "G" + proc
            elif st.endswith("@gw"):
                st = st[:-3]
            out.add((st, proc, shape))
    return out


LOST = lost()


def value(name, proc, shape):
    """(volts, kind): kind is "bv", "reached" (a lower bound), "failed"
    (the run gave no result) or None (not simulated). A sweep that ended
    below 1 V counts as failed."""
    e = entry(name, proc)
    if e.get(shape) is not None:
        return e[shape], "bv"
    at = e.get("reached", {}).get(shape)
    if at is not None and at >= 1.0:
        return at, "reached"
    src = stands_in(name, proc) or proc
    if at is not None or (name, src, shape) in LOST:
        return None, "failed"
    return None, None


def cell(name, proc, shape):
    v, kind = value(name, proc, shape)
    if kind == "bv":
        return f"{v:.1f}"
    if kind == "reached":
        return f"> {v:.1f}"
    return "failed" if kind == "failed" else "–"


def known(name, proc):
    return any(value(name, proc, s)[1] for s in SHAPES)


def pair(name, proc):
    if not known(name, proc):
        return "–"
    return f"{cell(name, proc, 'edge')} / {cell(name, proc, 'corner')}"


def band(name, fam):
    """(low, high, notes) over the family, or None if it has no value."""
    return band_of(processes(fam), name)


def band_of(procs, name):
    vals, notes = [], []
    for p in procs:
        if not known(name, p):
            continue
        got = {s: value(name, p, s) for s in SHAPES}
        for s, (v, kind) in got.items():
            if kind == "reached":
                notes.append(f"{p} {s} not resolved above {v:.1f} V")
            elif kind == "failed":
                notes.append(f"{p} {s} gave no result")
            elif kind is None:
                notes.append(f"{p} {s} not simulated")
        nums = [v for v, kind in got.values() if kind == "bv"]
        open_at = [v for v, kind in got.values() if kind == "reached"]
        failed = any(kind == "failed" for _, kind in got.values())
        if nums and not failed and not (open_at
                                        and min(open_at) < min(nums)):
            vals.append(min(nums))  # no unresolved shape could be lower
    if not vals:
        return None, None, notes
    return min(vals), max(vals), notes


def widen(v):
    """(down, up) fractions of the agreement range at a predicted value."""
    return WIDEN_LOW if v < REGIME else WIDEN_HIGH


def agreement(lo, hi):
    """The agreement range of a band: each end widened by its own rule."""
    return lo * (1 - widen(lo)[0]), hi * (1 + widen(hi)[1])


def span(lo, hi, wide=False):
    """A band as text; wide=True widens it into the agreement range."""
    if lo is None:
        return "–"
    if wide:
        lo, hi = agreement(lo, hi)
    return f"{lo:.1f} to {hi:.1f}"


def pred_table(test):
    procs = [p for p in PRED["processes"] if test(p)]
    procs.sort(key=lambda p: (ORDER.index(family(p)) if family(p) in ORDER
                              else ORDER.index(family(p[1:])), p))
    titles = {k: t for k, t, _ in tdkit.GROUPS}
    rows = [["Structure", "Group"] + [f"{p}: edge / corner (V)"
                                      for p in procs]]
    for nm in ordered():
        if any(known(nm, p) for p in procs):
            rows.append([nm, titles[tdkit.group_of(nm, STRUCTS[nm])]]
                        + [pair(nm, p) for p in procs])
    return tb.write(rows)


def summarise(notes):
    """Shorten per-process notes: "A, Aq corner not simulated"."""
    by = {}
    for n in notes:
        proc, rest = n.split(" ", 1)
        by.setdefault(rest, []).append(proc)
    return "; ".join(f"{', '.join(ps)} {rest}" for rest, ps in by.items())


def band_table():
    rows = [["Structure", "Family", "Band (V)", "Agreement range (V)",
             "Reference", "Predicted ratio", "Gaps in the simulation"]]
    for nm in ordered():
        for f in families():
            if stands_in(nm, f) or not any(known(nm, p)
                                           for p in processes(f)):
                continue
            lo, hi, notes = band(nm, f)
            rows.append([nm, ", ".join(served(nm, f)), span(lo, hi),
                         span(lo, hi, True), *ratio(nm, f),
                         summarise(notes) or "None"])
    return tb.write(rows)


def key_table():
    cols = [p for p in ("AL", "AnL", "BL", "BD") if p in PRED["processes"]]
    rows = [["Structure", "Termination"] + [
        f"{p}: edge / corner (V)" for p in cols]]
    for nm, what in KEY:
        if nm in PRED["structures"]:
            rows.append([nm, what] + [pair(nm, p) for p in cols])
    return tb.write(rows)


def source_table():
    src = PRED.get("source", {})
    rows = [["Item", "Value"]]
    for k, v in src.items():
        if k != "records":
            rows.append([k.capitalize(), str(v)])
    if off_die():
        rows.append(["Results left out", "Structures no longer on the die: "
                     + ", ".join(off_die())])
    for r in src.get("records", []):
        lost = r.get("not_converged", [])
        rows.append([f"Record {r['record']}",
                     f"{r['cases']} cases, commit {r['commit'][:12]}; "
                     f"{len(lost)} cases gave no result"
                     + (": " + ", ".join(c.replace("|", " ") for c in lost)
                        if lost else "")])
    return tb.write(rows)


def cross_tables():
    rows = [["Case", "DEVSIM, integral (V)", "Charon, integral (V)",
             "Charon, current (V)", "Description"]]
    for c in CROSS["cases"]:
        rows.append([c["name"]] + [
            "–" if c.get(k) is None else f"{c[k]:.2f}"
            for k in ("devsim_v", "charon_integral_v", "charon_current_v")]
            + [c["description"]])
    src = [["Item", "Value"]] + [[k.capitalize(), str(v)]
                                 for k, v in CROSS["source"].items()]
    rr = CROSS["ring_rise"]
    ring = [["Well voltage (V)", "DEVSIM (V)", "Charon (V)",
             "Difference (V)"]]
    for v, d, c in zip(rr["well_v"], rr["devsim_v"], rr["charon_v"]):
        ring.append([f"{v:g}", f"{d:.2f}", f"{c:.2f}", f"{c - d:+.2f}"])
    return {"hvt-tab-crosscheck.csv": tb.write(rows),
            "hvt-tab-crosscheck-ring.csv": tb.write(ring),
            "hvt-tab-crosscheck-source.csv": tb.write(src)}


def tables():
    proc = [["Process", "Family", "Description"]] + [
        [k, family(k), v] for k, v in PRED["processes"].items()]
    out = {"hvt-tab-pred-a.csv": pred_table(
               lambda p: family(p) != "G" and parse(p)[1] != "B"),
           "hvt-tab-pred-b.csv": pred_table(
               lambda p: family(p) != "G" and parse(p)[1] == "B"),
           "hvt-tab-pred-g.csv": pred_table(lambda p: family(p) == "G"),
           "hvt-tab-pred-band.csv": band_table(),
           "hvt-tab-pred-key.csv": key_table(),
           "hvt-tab-processes.csv": tb.write(proc),
           "hvt-tab-pred-source.csv": source_table()}
    out.update(cross_tables())
    return out
