"""Write the member table of each structure group and the pad table.

hvt-tab-<group>.csv   one row per structure: its drawn dimensions and the
                      centre of its pad on the die.
hvt-tab-pads.csv      the substrate pads and the second pads.

Dimensions come from silicon/hvtest/structures.json and positions from
manifest.json. figures.py calls this module; it writes no files itself.

SPDX-License-Identifier: Apache-2.0
"""

import csv
import io

import physics
import tdkit
from tdkit import num

WELL = {"nw": "N-well", "dnw": "Deep N-well", "open": "None"}
LAYER = {"poly": "polysilicon", "m1": "Metal1", "m2": "Metal2"}


def opt(v):
    return "–" if v is None else num(v)


def plate(p, layer):
    return opt(p["plates"].get(layer))


def gaps(p):
    return ", ".join(num(g) for g, _ in p["rings"]) or "–"


def pad(site):
    return f"{site['pad'][0]:.0f}, {site['pad'][1]:.0f}"


def area(p):
    a, per = physics.octagon(p["half"], p["corner"])
    return f"{a:.0f}", f"{per:.1f}"


T = ("P+ ring distance (µm)", lambda n, p, s: num(p["term"]))
C = ("Corner radius (µm)", lambda n, p, s: num(p["corner"]))
PAD = ("Pad centre x, y (µm)", lambda n, p, s: pad(s))
KIND = ("Well", lambda n, p, s: WELL[p["kind"]])
PLATES = [(f"{LAYER[k].capitalize()} plate (µm)",
           lambda n, p, s, k=k: plate(p, k)) for k in LAYER]

COLUMNS = {
    "surround": [T, C, PAD],
    "pwell": [("P-well start (µm)", lambda n, p, s: opt(p["pwell_gap"])),
              T, PAD],
    "nat": [("NAT start (µm)", lambda n, p, s: opt(p["nat_gap"])), T, C,
            PLATES[1], PLATES[2], PAD],
    "dnw": [T, C,
            ("P-well start (µm)", lambda n, p, s: opt(p["pwell_gap"])), PAD],
    "plates": [KIND] + PLATES + [PAD],
    "rings": [("Rings", lambda n, p, s: str(len(p["rings"]))),
              ("Gaps, innermost first (µm)", lambda n, p, s: gaps(p)),
              ("Ring width (µm)", lambda n, p, s: num(p["rings"][0][1])),
              T, PLATES[1],
              ("Ring 1 pad x, y (µm)", lambda n, p, s:
               "{:.0f}, {:.0f}".format(*s["aux_pad"]) if p["sense"]
               else "–"), PAD],
    "gated": [KIND,
              ("Plate", lambda n, p, s: LAYER[next(iter(p["plates"]))]),
              ("Plate length (µm)", lambda n, p, s:
               num(next(iter(p["plates"].values())))),
              ("NAT start (µm)", lambda n, p, s: opt(p["nat_gap"])),
              ("Plate pad x, y (µm)", lambda n, p, s:
               "{:.0f}, {:.0f}".format(*s["aux_pad"])), PAD],
    "large": [KIND, ("Side (µm)", lambda n, p, s: num(2 * p["half"])),
              C, T, ("Area (µm²)", lambda n, p, s: area(p)[0]),
              ("Perimeter (µm)", lambda n, p, s: area(p)[1]), PAD],
    "open": [("Contents", lambda n, p, s: "Metal5 lead and pad only"), PAD],
}


def write(rows):
    out = io.StringIO()
    csv.writer(out, lineterminator="\n").writerows(rows)
    return out.getvalue()


def tables():
    structs, man = tdkit.load()
    sites = {s["name"]: s for s in man["sites"]}
    files = {}
    for key, cols in COLUMNS.items():
        rows = [["Name"] + [c[0] for c in cols]]
        for name in tdkit.members(structs, man, key):
            rows.append([name] + [c[1](name, structs[name], sites[name])
                                  for c in cols])
        files[f"hvt-tab-{key}.csv"] = write(rows)
    rows = [["Pad", "Connects to", "Centre x, y (µm)"]]
    for k, (x, y) in enumerate(man["sub_pads"]):
        rows.append([f"SUB{k + 1}", "Substrate, through every P+ ring",
                     f"{x:.0f}, {y:.0f}"])
    for s in man["sites"]:
        if "aux_pad" in s:
            role = "ring 1" if s["aux_role"] == "ring1" else "plate"
            rows.append([f"{s['name']}.{s['aux_role'][0].upper()}",
                         f"{role.capitalize()} of {s['name']}",
                         "{:.0f}, {:.0f}".format(*s["aux_pad"])])
    files["hvt-tab-pads.csv"] = write(rows)
    return files


def counts():
    structs, man = tdkit.load()
    return {k: len(tdkit.members(structs, man, k)) for k in COLUMNS}
