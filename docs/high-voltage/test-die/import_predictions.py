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

PROCESSES = {
    "A": "P-well generated wherever no N-well, deep N-well (kept 1.5 um away) or NAT is "
         "drawn, including the strip between an N-well and NAT; nominal doping",
    "An": "As A, but no P-well in the strip between an N-well and NAT",
    "Aq": "As A, with fixed oxide charge of 1e11 cm^-2",
    "Alo": "As A, substrate 2e15 cm^-3",
    "Ahi": "As A, substrate 5e15 cm^-3",
    "B": "P-well only where the layout draws it; nominal doping (substrate 3.5e15 cm^-3)",
    "Bq": "As B, with fixed oxide charge of 1e11 cm^-2",
    "Bq3": "As B, with fixed oxide charge of 3e11 cm^-2",
    "Blo": "As B, substrate 2e15 cm^-3",
    "Bhi": "As B, substrate 5e15 cm^-3",
    "Bdp": "As B, substrate doping rising to 4e16 cm^-3 about 5 um below the surface",
}


def main(paths):
    cases, pins = {}, []
    for path in paths:
        rec = json.loads(pathlib.Path(path).read_text())
        cases.update(rec["cases"])
        pins.append({"record": pathlib.Path(path).name, "commit": rec["pins"]["commit"],
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
        procs[p] = PROCESSES[base] + ("; the gated plate held at 0 V" if p.startswith("G") else "")
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
