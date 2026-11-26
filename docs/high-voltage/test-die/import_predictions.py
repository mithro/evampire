"""Build predictions.json from the records of mithro/gf180-tcad.

    uv run python docs/high-voltage/test-die/import_predictions.py RECORD.json [RECORD.json ...]

The records are results/hv-junction/*.json of mithro/gf180-tcad (written by its
experiments/hv-junction/record.py). A case is named STRUCTURE|PROCESS|edge or corner; a
gated structure has @gw (plate tied to the well) or @g0 (plate held at 0 V) after its name.
Later records override earlier ones case by case. In predictions.json a gated structure's
@gw cases are filed under the process itself and its @g0 cases under "G" + process.
A case that reached the end of its sweep or stopped converging without breakdown has a
null voltage and its last converged voltage under "reached".
"""

import json
import pathlib
import sys

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


if __name__ == "__main__":
    main(sys.argv[1:])
