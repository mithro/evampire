"""Read predictions.json and crosscheck.json and write their tables.

hvt-tab-pred-a.csv, -b.csv, -g.csv  predicted breakdown by structure, one
                      column per process of the family, as "edge / corner".
hvt-tab-pred-band.csv   band of each structure under each assumption.
hvt-tab-pred-key.csv    a few structures that carry the main findings.
hvt-tab-processes.csv, hvt-tab-pred-source.csv   what was simulated.
hvt-tab-crosscheck.csv, hvt-tab-crosscheck-source.csv   second simulator.

predictions.json is written by import_predictions.py: {"structures":
{NAME: {PROCESS: {"edge": volts or null, "corner": volts or null,
"reached": {shape: volts}, "ring_v": [[well volts, ring 1 rise], ...]}}},
"processes": {PROCESS: description}, "source": {...}}. A null voltage with
a "reached" entry is a sweep that ended at that voltage without breakdown;
a null without one was not simulated.

Families: a process named "G..." has the gated plate held at 0 V and is in
no band; "An..." is assumption A without the P-well strip beside NAT;
other names belong to the family of their first letter, A or B. The band
of a structure is the lowest to the highest value, over a family, of the
lower of the edge and corner voltages. A process whose sweep ended on one
shape below the breakdown of the other is left out, since its lower value
is not known. figures.py calls this module.

SPDX-License-Identifier: Apache-2.0
"""

import json

import tables as tb
import tdkit

STRUCTS, MAN = tdkit.load()
PRED = json.loads((tdkit.HERE / "predictions.json").read_text())
CROSS = json.loads((tdkit.HERE / "crosscheck.json").read_text())
WIDEN = 0.15           # agreement range: the band widened by this fraction
SHAPES = ("edge", "corner")
KEY = [("NT20", "Plain N-well"), ("NC0", "Sharp corner"),
       ("NW0", "Drawn P-well touching"), ("NW1p5", "Drawn P-well at 1.5 µm"),
       ("NW6", "Drawn P-well at 6 µm"), ("NA0p6", "NAT from 0.6 µm"),
       ("NP4", "Polysilicon plate, 4 µm"), ("NM1_6", "Metal1 plate, 6 µm"),
       ("NM1_10", "Metal1 plate, 10 µm"), ("NR1_2", "One ring at 2 µm"),
       ("NR3_2", "Three rings"), ("NR5_1p4", "Five rings"),
       ("DT20", "Deep N-well"), ("DC0", "Deep N-well, sharp corner"),
       ("DAo1", "Deep N-well with NAT over its edge")]


def family(proc):
    if proc.startswith("G"):
        return "G"
    return "An" if proc.startswith("An") else proc[0]


def processes(fam):
    return [p for p in PRED["processes"] if family(p) == fam]


def families():
    return [f for f in ("A", "An", "B") if processes(f)]


def ordered():
    order = [s["name"] for s in MAN["sites"]]
    unknown = sorted(set(PRED["structures"]) - set(order))
    if unknown:
        raise SystemExit(f"predictions.json: unknown structures {unknown}")
    return [n for n in order if n in PRED["structures"]]


def entry(name, proc):
    return PRED["structures"].get(name, {}).get(proc) or {}


def value(e, shape):
    """(volts, kind): kind is "bv", "reached" (a lower bound) or None."""
    if e.get(shape) is not None:
        return e[shape], "bv"
    if shape in e.get("reached", {}):
        return e["reached"][shape], "reached"
    return None, None


def cell(e, shape):
    v, kind = value(e, shape)
    if kind == "bv":
        return f"{v:.1f}"
    return f"> {v:.1f}" if kind == "reached" else "–"


def lower(e):
    """Lower of the edge and corner breakdown voltages, or None."""
    vals = [e[s] for s in SHAPES if e.get(s) is not None]
    return min(vals) if vals else None


def band(name, fam):
    """(low, high, notes) over the family, or None if it has no value."""
    vals, notes = [], []
    for p in processes(fam):
        e = entry(name, p)
        if not e:
            continue
        for s in SHAPES:
            v, kind = value(e, s)
            if kind == "reached":
                notes.append(f"{p} {s} not resolved above {v:.1f} V")
            elif kind is None:
                notes.append(f"{p} {s} not simulated")
        open_at = [e["reached"][s] for s in SHAPES
                   if value(e, s)[1] == "reached"]
        low = lower(e)
        if low is not None and not (open_at and min(open_at) < low):
            vals.append(low)    # an unresolved shape could not be lower
    if not vals:
        return None, None, notes
    return min(vals), max(vals), notes


def span(lo, hi, widen=0.0):
    if lo is None:
        return "–"
    return f"{lo * (1 - widen):.1f} to {hi * (1 + widen):.1f}"


def pred_table(fams):
    procs = [p for f in fams for p in processes(f)]
    titles = {k: t for k, t, _ in tdkit.GROUPS}
    rows = [["Structure", "Group"] + [f"{p}: edge / corner (V)"
                                      for p in procs]]
    for nm in ordered():
        if not any(entry(nm, p) for p in procs):
            continue
        rows.append([nm, titles[tdkit.group_of(nm, STRUCTS[nm])]] + [
            f"{cell(entry(nm, p), 'edge')} / {cell(entry(nm, p), 'corner')}"
            if entry(nm, p) else "–" for p in procs])
    return tb.write(rows)


def summarise(notes):
    """Shorten per-process notes: "A, Aq corner not simulated"."""
    by = {}
    for n in notes:
        proc, rest = n.split(" ", 1)
        by.setdefault(rest, []).append(proc)
    return "; ".join(f"{', '.join(ps)} {rest}" for rest, ps in by.items())


def band_table():
    fams = families()
    head = ["Structure"]
    for f in fams:
        head += [f"{f} band (V)", f"{f} agreement range (V)"]
    rows = [head + ["Gaps in the simulation"]]
    for nm in ordered():
        row, notes = [nm], []
        for f in fams:
            lo, hi, n = band(nm, f)
            row += [span(lo, hi), span(lo, hi, WIDEN)]
            notes += n
        rows.append(row + [summarise(notes) or "None"])
    return tb.write(rows)


def key_table():
    cols = [p for p in ("A", "An", "B") if p in PRED["processes"]]
    rows = [["Structure", "Termination"] + [
        f"{p}: edge / corner (V)" for p in cols]]
    for nm, what in KEY:
        if nm in PRED["structures"]:
            rows.append([nm, what] + [
                f"{cell(entry(nm, p), 'edge')} / "
                f"{cell(entry(nm, p), 'corner')}" if entry(nm, p) else "–"
                for p in cols])
    return tb.write(rows)


def source_table():
    src = PRED.get("source", {})
    rows = [["Item", "Value"]]
    for k, v in src.items():
        if k != "records":
            rows.append([k.capitalize(), str(v)])
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
    return {"hvt-tab-crosscheck.csv": tb.write(rows),
            "hvt-tab-crosscheck-source.csv": tb.write(src)}


def tables():
    proc = [["Process", "Family", "Description"]] + [
        [k, family(k), v] for k, v in PRED["processes"].items()]
    out = {"hvt-tab-pred-a.csv": pred_table(("A", "An")),
           "hvt-tab-pred-b.csv": pred_table(("B",)),
           "hvt-tab-pred-g.csv": pred_table(("G",)),
           "hvt-tab-pred-band.csv": band_table(),
           "hvt-tab-pred-key.csv": key_table(),
           "hvt-tab-processes.csv": tb.write(proc),
           "hvt-tab-pred-source.csv": source_table()}
    out.update(cross_tables())
    return out
