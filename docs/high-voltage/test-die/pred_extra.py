"""Write the tables of the two side files of the predictions.

hvt-tab-p5.csv        punch-through to a grounded ring, from p5.json if
                      import_predictions.py --p5 has written it; "not yet
                      simulated" otherwise.
hvt-tab-mc-cap.csv, -corner.csv, -ceiling.csv, -source.csv   the values
                      of model_checks.json, which is edited by hand: the
                      numbers of the final review that no record holds.

figures.py calls this module; it writes no files itself.

SPDX-License-Identifier: Apache-2.0
"""

import json

import tables as tb
import tdkit

STRUCTS, MAN = tdkit.load()
CHECKS = json.loads((tdkit.HERE / "model_checks.json").read_text())
_P5 = tdkit.HERE / "p5.json"   # written by import_predictions.py --p5
P5 = json.loads(_P5.read_text())["structures"] if _P5.is_file() else {}
P5_PROCS = ("AL", "BL", "BD")


def sense():
    """The structures with a pad on ring 1, by gap of ring 1."""
    names = [s["name"] for s in MAN["sites"] if s["params"]["sense"]]
    return sorted(names, key=lambda n: STRUCTS[n]["rings"][0][0])


def p5_cell(name, proc):
    e = P5.get(name, {}).get(proc)
    if not e:
        return "not yet simulated"
    pt = (f"{e['punch_through_v']:.1f}" if e["punch_through_v"] is not None
          else f"> {e['reached_v']:.1f}")
    bv = (f"{e['breakdown_v']:.1f}" if e["breakdown_v"] is not None
          else f"> {e['reached_v']:.1f}")
    return f"{pt} / {bv}"


def p5_table():
    rows = [["Structure", "Gap to ring 1 (µm)", "Rings"] + [
        f"{p}: punch-through / breakdown (V)" for p in P5_PROCS]]
    for n in sense():
        rows.append([n, f"{STRUCTS[n]['rings'][0][0]:g}",
                     str(len(STRUCTS[n]["rings"]))]
                    + [p5_cell(n, p) for p in P5_PROCS])
    return tb.write(rows)


def corner_now(name, proc):
    """The converged corner value from predictions.json, as text."""
    import pred_data
    v, kind = pred_data.value(name, proc, "corner")
    return f"{v:.1f} V" if kind == "bv" else "not in the results file"


def check_tables():
    """The tables of model_checks.json: values from the final review that
    no simulation record holds yet."""
    cap, cor = CHECKS["capacitance"], CHECKS["corner"]
    rows = [["Reverse voltage (V)", "Layer under deep N-well only",
             "Layer under the N-well too",
             "Capacitance with the layer over without"]]
    for v, r in zip(cap["volts"], cap["without_layer"]):
        d = cap["difference_percent"].get(str(v))
        rows.append([str(v), f"{r:.2f}", cap["with_layer"] if v == 0
                     else "as above", f"+{d} %" if d else "–"])
    corner = [["Item", "Value"],
              ["Section", f"{cor['structure']} under {cor['process']}, "
               f"corner radius {cor['radius_um']:g} µm"],
              ["Last point of the stalled sweep", f"{cor['last_volts']} V"],
              ["Ionisation integral there", f"{cor['integral']}"],
              ["Rise of the integral", f"{cor['slope_per_volt']} per volt"],
              ["Integral reaches 1, by straight-line extrapolation",
               f"about {cor['extrapolated_volts']} V"],
              ["Converged result of the same section, 128-bit arithmetic",
               corner_now(cor["structure"], cor["process"])]]
    ceiling = [["Change to the assumed profile",
                "Breakdown of the flat bottom (V)"]] + CHECKS["ceiling"]["rows"]
    src = [["Item", "Value"]] + [[k.capitalize(), v]
                                 for k, v in CHECKS["source"].items()]
    return {"hvt-tab-mc-cap.csv": tb.write(rows),
            "hvt-tab-mc-corner.csv": tb.write(corner),
            "hvt-tab-mc-ceiling.csv": tb.write(ceiling),
            "hvt-tab-mc-source.csv": tb.write(src)}


def tables():
    out = check_tables()
    out["hvt-tab-p5.csv"] = p5_table()
    return out
