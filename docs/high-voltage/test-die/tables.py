"""Write the member table of each structure group and the pad table.

hvt-tab-<group>.csv   one row per structure: its drawn dimensions and the
                      centre of its pad on the die.
hvt-tab-pads.csv      the substrate pads and the second pads.
hvt-tab-precheck.csv  the precheck result, from silicon/hvtest/PRECHECK.txt.
hvt-precheck-note.inc one sentence on the rerun on the committed file,
                      from the same record.

Dimensions come from silicon/hvtest/structures.json and positions from
manifest.json. figures.py calls this module; it writes no files itself.

SPDX-License-Identifier: Apache-2.0
"""

import csv
import io

import physics
import tdkit
from tdkit import num

PRECHECK = tdkit.HERE.parents[2] / "silicon" / "hvtest" / "PRECHECK.txt"
STRUCT_NAMES = set(tdkit.load()[0])
WELL = {"nw": "N-well", "dnw": "Deep N-well", "open": "None"}
LAYER = {"poly": "polysilicon", "m1": "Metal1", "m2": "Metal2"}


def opt(v):
    return "–" if v is None else num(v)


def plate(p, layer):
    return opt(p["plates"].get(layer))


def gaps(p):
    return ", ".join(num(g) for g, _ in p["rings"]) or "–"


def nat(p):
    v = p["nat_gap"]
    if v is None:
        return "–"
    return f"overlaps the well by {num(-v)}" if v < 0 else num(v)


def pad(site):
    return f"{site['pad'][0]:.0f}, {site['pad'][1]:.0f}"


def area(p):
    a, per = physics.octagon(p["half"], p["corner"])
    return f"{a:.0f}", f"{per:.1f}"


def note(n, p, s):
    out = []
    if p["lead_w"] != 6.0:
        out.append(f"Metal5 lead {num(p['lead_w'])} µm wide")
    if p["dualgate"]:
        out.append("In the 6 V area")
    if n[-1] in "bc" and n[:-1] in STRUCT_NAMES:
        out.append(f"{'Second' if n[-1] == 'b' else 'Third'} copy of "
                   f"{n[:-1]}")
    return "; ".join(out) or "–"


NOTE = ("Variant", note)
T = ("P+ ring distance (µm)", lambda n, p, s: num(p["term"]))
C = ("Corner radius (µm)", lambda n, p, s: num(p["corner"]))
PAD = ("Pad centre x, y (µm)", lambda n, p, s: pad(s))
KIND = ("Well", lambda n, p, s: WELL[p["kind"]])
PLATES = [(f"{LAYER[k].capitalize()} plate (µm)",
           lambda n, p, s, k=k: plate(p, k)) for k in LAYER]

COLUMNS = {
    "surround": [T, C, NOTE, PAD],
    "pwell": [("P-well start (µm)", lambda n, p, s: opt(p["pwell_gap"])),
              T, PAD],
    "nat": [("NAT start (µm)", lambda n, p, s: nat(p)), T, C,
            PLATES[1], PLATES[2],
            ("Ring gaps, innermost first (µm)", lambda n, p, s: gaps(p)),
            NOTE, ("Ring 1 pad x, y (µm)", lambda n, p, s:
                   "{:.0f}, {:.0f}".format(*s["aux_pad"]) if p["sense"]
                   else "–"), PAD],
    "dnw": [T, C,
            ("P-well start (µm)", lambda n, p, s: opt(p["pwell_gap"])),
            ("NAT start (µm)", lambda n, p, s: nat(p)), PLATES[1], NOTE,
            PAD],
    "plates": [KIND] + PLATES + [C, NOTE, PAD],
    "rings": [("Rings", lambda n, p, s: str(len(p["rings"]))),
              ("Gaps, innermost first (µm)", lambda n, p, s: gaps(p)),
              ("Ring width (µm)", lambda n, p, s: num(p["rings"][0][1])),
              T, PLATES[1], NOTE,
              ("Ring 1 pad x, y (µm)", lambda n, p, s:
               "{:.0f}, {:.0f}".format(*s["aux_pad"]) if p["sense"]
               else "–"), PAD],
    "gated": [KIND,
              ("Plate", lambda n, p, s: LAYER[next(iter(p["plates"]))]),
              ("Plate length (µm)", lambda n, p, s:
               num(next(iter(p["plates"].values())))),
              ("NAT start (µm)", lambda n, p, s: nat(p)),
              ("Plate pad x, y (µm)", lambda n, p, s:
               "{:.0f}, {:.0f}".format(*s["aux_pad"])), PAD],
    "large": [KIND, ("Side (µm)", lambda n, p, s: num(2 * p["half"])),
              C, T, ("NAT start (µm)", lambda n, p, s: nat(p)),
              ("Fill block", lambda n, p, s:
               {True: "Whole structure", False: "None",
                "ring": "Termination zone"}[p["block"]]),
              ("Area (µm²)", lambda n, p, s: area(p)[0]),
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
            ref = f":ref:`{name} <hvt-s-{name.lower().replace('_', '-')}>`"
            rows.append([ref] + [c[1](name, structs[name], sites[name])
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
    files["hvt-tab-precheck.csv"] = precheck()
    files["hvt-precheck-note.inc"] = precheck_note()
    return files


def precheck_note():
    """One sentence on whether the precheck was rerun on the committed
    file, from the line PRECHECK.txt has for it (or has not)."""
    key = "precheck rerun on the committed hvtest.oas itself:"
    for line in PRECHECK.read_text().splitlines():
        if line.startswith(key):
            result = line[len(key):].strip()
            if result.startswith("exit 0"):
                when = result[len("exit 0"):].strip(" ()")
                return ("The precheck was also run on the committed file "
                        "itself" + (f", on {when}," if when else "")
                        + " and passed.\n")
            return ("The precheck was also run on the committed file "
                    f"itself and did not pass: {result}.\n")
    return ("The precheck has not yet been run again on the committed file "
            "itself.\n")


def precheck():
    """The result table of the submission page, from PRECHECK.txt."""
    rows = [["Item", "Result"]]
    for line in PRECHECK.read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        if line.startswith("density ") and "\t" in line:
            name, value = line.split("\t", 1)
            if "MetalTop" in name:
                continue
            rows.append([name.replace("density ", "Density, ")
                         .replace(" ratio", ""), f"{float(value[:-2]):.1f} %"])
        elif line.startswith("precheck: Check for "):
            rest = line[len("precheck: Check for "):].rstrip(".")
            rows.append([rest.rsplit(" ", 1)[0], rest.rsplit(" ", 1)[1]
                         .capitalize()])
        elif ":" in line:
            key, value = line.split(":", 1)
            rows.append([key.capitalize(), value.strip()])
        else:                       # a line of another form: shown as it is
            rows.append([line.strip(), "–"])
    return write(rows)


def counts():
    structs, man = tdkit.load()
    return {k: len(tdkit.members(structs, man, k)) for k in COLUMNS}
