"""Write the tables of the two side files of the predictions.

hvt-tab-p5.csv        punch-through to a grounded ring, from p5.json if
                      import_predictions.py --p5 has written it; "not yet
                      simulated" otherwise.
hvt-tab-mc-cap.csv, -corner.csv, -ceiling.csv, -source.csv,
-onesided.csv, -radius.csv   the values of model_checks.json, which is
                      edited by hand: the numbers of the reviews, with the
                      record each comes from or the statement that none
                      holds it (its key "source"). Its key "corner_radius" is written once
                      the radius sensitivity runs end, as {"note": text,
                      "cases": [{"structure": NAME, "process": PROCESS,
                      "radius_um": number, "volts": number or null}]};
                      while it is absent the table reads "not yet
                      simulated".

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
    src = [["Values", "Where they come from"]] + [
        [TITLES.get(k, k), v] for k, v in CHECKS["source"].items()]
    return {"hvt-tab-mc-cap.csv": tb.write(rows),
            "hvt-tab-mc-corner.csv": tb.write(corner),
            "hvt-tab-mc-ceiling.csv": tb.write(ceiling),
            "hvt-tab-mc-source.csv": tb.write(src)}


RADII = (0.5, 1.0, 2.0, 4.0)   # radii of the sensitivity run
TITLES = {"capacitance": "Capacitance (tab-hvt-mc-cap)",
          "ceiling": "Ceiling under D (tab-hvt-cap-sens)",
          "corner": "Sharp corner (tab-hvt-mc-corner)",
          "one_sided": "One-sided junctions (tab-hvt-mc-onesided)",
          "corner_radius": "Corner radius (tab-hvt-mc-radius)"}


def closed_form(n):
    """Sze and Gibbons: 60 V x (N / 1e16 cm^-3)^-0.75."""
    return 60.0 * (n / 1e16) ** -0.75


def onesided_table():
    rows = [["Doping of the light side (cm⁻³)", "Ionisation integral (V)",
             "Closed form (V)", "Integral over closed form", "Source"]]
    for r in CHECKS["one_sided"]["rows"]:
        m, e = r["doping_cm3"].split("e")
        power = f"10\\ :sup:`{e}`"
        cf = closed_form(float(r["doping_cm3"]))
        rows.append([f"{m} × {power}" if m != "1" else power,
                     f"{r['integral_v']:.1f}", f"{cf:.1f}",
                     f"{100 * (r['integral_v'] / cf - 1):+.0f} %",
                     f"record {r['record']}" if r["record"] else
                     "estimate, no record"])
    return tb.write(rows)


def radius_table():
    rows = [["Corner radius of the section (µm)", "Section and process",
             "Corner breakdown (V)"]]
    cases = CHECKS.get("corner_radius", {}).get("cases")
    if not cases:
        return tb.write(rows + [[f"{r:g}", "–", "not yet simulated"]
                                for r in RADII])
    for c in sorted(cases, key=lambda c: (c["structure"], c["process"],
                                          c["radius_um"])):
        v = c.get("volts")
        rows.append([f"{c['radius_um']:g}",
                     f"{c['structure']} under {c['process']}",
                     "no result" if v is None else f"{v:.1f}"])
    return tb.write(rows)


def tables():
    out = check_tables()
    out["hvt-tab-mc-onesided.csv"] = onesided_table()
    out["hvt-tab-mc-radius.csv"] = radius_table()
    out["hvt-tab-p5.csv"] = p5_table()
    return out
