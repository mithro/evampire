"""Build predictions.json from the records of mithro/gf180-tcad.

    uv run python docs/high-voltage/test-die/import_predictions.py RECORD.json [RECORD.json ...]

The records are results/hv-junction/*.json of mithro/gf180-tcad (written by its
experiments/hv-junction/record.py). A case is named STRUCTURE|PROCESS|edge or corner; a
gated structure has @gw (plate tied to the well) or @g0 (plate held at 0 V) after its name.
Later records override earlier ones case by case. In predictions.json a gated structure's
@gw cases are filed under the process itself and its @g0 cases under "G" + process.
A case that reached the end of its sweep or stopped converging without breakdown has a
null voltage and its last converged voltage under "reached".

    uv run python docs/high-voltage/test-die/import_predictions.py --p5 P5.json [P5.json ...]

writes p5.json instead and leaves predictions.json alone. The P5 records
(results/hv-junction/p5.json of mithro/gf180-tcad) hold the same case names with ring 1 held
at 0 V, so they must never be merged with the ordinary records; the option keeps them
apart. For each structure and process p5.json stores the well voltage at which the current
into the grounded ring reaches the criterion of procedure P5, 1 nA, and the breakdown
voltage of that case. The record gives the well current per centimetre of edge, so

    current = |i_well| (A/cm) x perimeter of ring 1 (cm)

with the perimeter taken along the middle of ring 1: the outline of the well moved out by
the gap plus half the ring's width (for NR1S5: 15 + 5 + 1 = 21 um half-side with a 14 um
corner radius, 150.6 um, so 1 nA is 6.6e-8 A/cm). The voltage is interpolated on the
logarithm of the current between the two bias points either side of the criterion; it is
null, with the last voltage under "reached", if the current never gets there.
"""

import json
import math
import pathlib
import sys

import physics

HERE = pathlib.Path(__file__).resolve().parent

_PW = {
    "A": "P-well generated wherever no N-well, deep N-well (kept 1.5 um away) or NAT is "
         "drawn, including the strip between an N-well and NAT",
    "An": "P-well generated as in A, but not in the strip between an N-well and NAT",
    "B": "P-well only where the layout draws it",
}
_DEEP = {
    "L": "deep P layer under deep N-well only",
    "D": "deep P layer 4.4 um down under the whole wafer",
}
_MOD = {
    "": "nominal doping (substrate 3.56e15 cm^-3)",
    "q": "fixed oxide charge of 1e11 cm^-2",
    "q3": "fixed oxide charge of 3e11 cm^-2",
    "lo": "substrate 2e15 cm^-3",
    "hi": "substrate 5e15 cm^-3",
}


def describe(proc):
    """The description of a process name such as BL, AnD, BLq or BDhi."""
    for pw in ("An", "A", "B"):
        if proc.startswith(pw):
            deep, mod = proc[len(pw)], proc[len(pw) + 1:]
            return f"{_PW[pw]}; {_DEEP[deep]}; {_MOD[mod]}"
    raise KeyError(proc)


def main(paths):
    cases, pins = {}, []
    for path in paths:
        rec = json.loads(pathlib.Path(path).read_text())
        cases.update(rec["cases"])
        pins.append({"record": pathlib.Path(path).name, "commit": (rec["pins"].get("commit") or ", ".join(c[:12] for c in rec["pins"]["commits"])),
                     "image": rec["pins"]["image"], "cases": len(rec["cases"]),
                     "not_converged": rec.get("not_converged", [])})
    structures, used = {}, set()
    for name, c in sorted(cases.items()):
        st, proc, shape = name.split("|")
        if st.endswith("@g0"):
            st, proc = st[:-3], "G" + proc
        elif st.endswith("@gw"):
            st = st[:-3]
        used.add(proc)
        entry = structures.setdefault(st, {}).setdefault(proc, {"edge": None, "corner": None, "ring_v": []})
        entry[shape] = None if c["bv_v"] is None else round(c["bv_v"], 1)
        if c["bv_v"] is None:
            entry.setdefault("reached", {})[shape] = round(c["reached_v"], 1)
        if shape == "edge" and c["probes"] and c["probes"][0]:
            zero = c["probes"][0][0]
            entry["ring_v"] = [[round(v, 2), round(p[0] - zero, 2)] for v, p in zip(c["v"], c["probes"])]
    procs = {}
    for p in sorted(used):
        base = p[1:] if p.startswith("G") else p
        procs[p] = describe(base) + ("; the gated plate held at 0 V" if p.startswith("G") else "")
    out = {
        "source": {
            "status": "DEVSIM 2.11.1 drift-diffusion, breakdown by the ionisation integral",
            "simulator": "DEVSIM 2.11.1 (gf180-tcad dev image)",
            "repository": "mithro/gf180-tcad, experiments/hv-junction",
            "commit": ", ".join(sorted({p["commit"][:12] for p in pins})),
            "records": pins,
        },
        "processes": procs,
        "structures": structures,
    }
    (HERE / "predictions.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"{len(cases)} cases, {len(structures)} structures, processes {sorted(used)}")


P5_CRITERION = 1e-9  # A, the ring current that defines punch-through in procedure P5


def ring_perimeter_cm(p):
    """Perimeter along the middle of ring 1, in cm."""
    gap, width = p["rings"][0]
    d = gap + width / 2
    return physics.octagon(p["half"] + d, p["corner"] + d)[1] * 1e-4


def crossing(volts, amps, level):
    """Voltage at which amps first reaches level, by log interpolation, or None."""
    for k, a in enumerate(amps):
        if a >= level:
            if k == 0 or amps[k - 1] <= 0:
                return volts[k]
            f = (math.log(level) - math.log(amps[k - 1])) / (math.log(a) - math.log(amps[k - 1]))
            return volts[k - 1] + f * (volts[k] - volts[k - 1])
    return None


def main_p5(paths):
    structs = json.loads((HERE.parents[2] / "silicon" / "hvtest" / "structures.json").read_text())
    cases, pins = {}, []
    for path in paths:
        rec = json.loads(pathlib.Path(path).read_text())
        cases.update(rec["cases"])
        pins.append({"record": pathlib.Path(path).name, "commit": (rec["pins"].get("commit") or ", ".join(c[:12] for c in rec["pins"]["commits"])),
                     "cases": len(rec["cases"])})
    out = {}
    for name, c in sorted(cases.items()):
        st, proc, shape = name.split("|")
        if shape != "edge" or st not in structs or not structs[st]["rings"]:
            continue
        per = ring_perimeter_cm(structs[st])
        amps = [abs(i) * per for i in c["i_well"]]
        v = crossing(c["v"], amps, P5_CRITERION)
        out.setdefault(st, {})[proc] = {
            "punch_through_v": None if v is None else round(v, 1),
            "reached_v": round(max(c["v"]), 1),
            "breakdown_v": None if c["bv_v"] is None else round(c["bv_v"], 1),
            "perimeter_um": round(per * 1e4, 1),
        }
    doc = {"source": {"criterion": "ring current of 1 nA, as in procedure P5", "records": pins},
           "structures": out}
    (HERE / "p5.json").write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    print(f"{len(cases)} cases, {len(out)} structures with ring 1 at 0 V")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--p5"]:
        main_p5(sys.argv[2:])
    else:
        main(sys.argv[1:])
