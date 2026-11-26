"""Generate the structure catalogue: its pages, entry figures and graphs.

catalogue.rst                    the group page, with an index of every
                                 structure on the die.
catalogue/<group>.rst            one page per group, one entry per
                                 structure.
catalogue/hvt-s-<NAME>.svg, catalogue/hvt-s-<NAME>-ring.svg and
catalogue/hvt-g-<group>.svg      the figures (fig_entry.py, fig_group.py).

The texts come from catalogue.py, the parameters from
silicon/hvtest/structures.json, the positions from manifest.json and the
predictions from predictions.json. The run stops if a structure on the
die has no text, a text names a structure that is not on the die, or a
link in a text has no target. figures.py calls this module.

SPDX-License-Identifier: Apache-2.0
"""

import re

import catalogue as cat
import fig_entry
import fig_group
import physics as ph
import pred_data as pd
import tdkit
from tdkit import num

STRUCTS, MAN = tdkit.load()
SITES = {s["name"]: s for s in MAN["sites"]}
ORDER = [s["name"] for s in MAN["sites"]]
PAGES = ["surround", "pwell", "nat", "plates", "rings", "gated", "dnw",
         "large"]
PROCS = {"P1": "Breakdown sweep", "P2": "Capacitance against voltage",
         "P3": "Floating-ring potential", "P4": "Gated diode",
         "P5": "Punch-through to a contacted ring"}
WELL = {"nw": "N-well", "dnw": "Deep N-well, with an N-well band under its "
        "contact ring", "open": "None"}
# published zero-bias models: area F/m2 and edge F/m, by kind of well
CMODEL = {"nw": (1.4914e-4, 5.8719e-10), "dnw": (2.2998e-4, 7.2369e-10)}


def slug(name):
    return name.lower().replace("_", "-")


def page_of(name):
    key = tdkit.group_of(name, STRUCTS[name])
    return "large" if key == "open" else key


def check():
    missing = [n for n in ORDER if n not in cat.E]
    extra = [n for n in cat.E if n not in STRUCTS]
    if missing or extra:
        raise SystemExit(f"catalogue.py: no entry for {missing}; entries "
                         f"for structures not on the die: {extra}")
    for name, e in cat.E.items():
        for other, _ in e["c"]:
            if other not in STRUCTS:
                raise SystemExit(f"catalogue.py: {name} is compared with "
                                 f"{other}, which is not on the die")


def link(s, where):
    def one(m):
        key = m.group(1)
        if key in PROCS:
            return f":ref:`{key} <hvt-{key.lower()}>`"
        if key not in STRUCTS:
            raise SystemExit(f"catalogue.py: {where} links to {key}, which "
                             f"is not on the die")
        return f":ref:`{key} <hvt-s-{slug(key)}>`"
    return re.sub(r"\{([A-Za-z0-9_]+)\}", one, s)


def wrap(s, indent="   "):
    out, cur = [], indent
    for word in s.split():
        if len(cur) + len(word) > 76 and cur.strip():
            out.append(cur.rstrip())
            cur = indent
        cur += word + " "
    return "\n".join(out + [cur.rstrip()])


def table(title, name, head, rows, widths):
    out = [f".. list-table:: {title}", f"   :name: {name}",
           "   :header-rows: 1", f"   :widths: {widths}", ""]
    for row in [head] + rows:
        for k, c in enumerate(row):
            out.append(("   * - " if k == 0 else "     - ") + str(c))
    return "\n".join(out) + "\n"


def position(site):
    x, y = site["pad"]
    if y > 2200:
        k = sorted(s["pad"][0] for s in MAN["sites"]
                   if s["pad"][1] > 2200).index(x) + 1
        return f"North band, position {k} from the west"
    return (f"Column {int((x - 290) / 300) + 1} from the west, row "
            f"{int((y - 295) / 150) + 1} from the south")


def param_rows(name):
    p, site = STRUCTS[name], SITES[name]
    rows = [["Well", WELL[p["kind"]]]]
    if p["kind"] != "open":
        area, per = ph.octagon(p["half"], p["corner"])
        rows += [
            ["Side of the well", f"{num(2 * p['half'])} µm"],
            ["Corners", f"Cut of {fig_entry.cut(p):.1f} µm along each "
             f"side, for a nominal radius of {num(p['corner'])} µm; eight "
             f"vertices of 135°" if p["corner"] else
             "Square; four vertices of 90°"],
            ["Area and perimeter", f"{area:.0f} µm² and {per:.1f} µm"],
            ["N+ contact ring", f"{num(p['ncomp_w'])} µm wide, "
             f"{num(p['inset'])} µm inside the well edge"],
            ["P+ ring", f"{num(p['ncomp_w'])} µm wide, {num(p['term'])} µm "
             f"from the well edge"]]
        for k, (gap, width) in enumerate(p["rings"]):
            rows.append([f"Floating ring {k + 1}",
                         f"{num(width)} µm wide, after a gap of "
                         f"{num(gap)} µm"])
        for layer, length in p["plates"].items():
            start = ("1 µm inside the well edge" if p["gate"] else
                     "the contact ring")
            rows.append([f"{fig_entry.LAYER[layer].capitalize()} plate",
                         f"From {start} to {num(length)} µm outside the "
                         f"edge; " + ("on its own pad" if p["gate"]
                                      else "joined to the well")])
        if p["pwell_gap"] is not None:
            rows.append(["Drawn P-well", f"From {num(p['pwell_gap'])} µm "
                         f"outside the well edge to 1 µm beyond the P+ "
                         f"ring"])
        if p["nat_gap"] is not None:
            a = (f"{num(p['nat_gap'])} µm outside" if p["nat_gap"] > 0
                 else f"{num(-p['nat_gap'])} µm inside")
            rows.append(["NAT layer", f"From {a} the well edge to 0.5 µm "
                         f"short of the P+ ring"])
        if p["dualgate"]:
            rows.append(["Area", "6 V: the thick-oxide layer covers the "
                         "structure"])
        rows.append(["Fill block", {True: "Whole structure", False: "None",
                                    "ring": "Termination zone only"}
                     [p["block"]]])
    rows.append(["Metal5 lead", f"{num(p['lead_w'])} µm wide"])
    rows.append(["Site", position(site)])
    what = "Pad" if p["kind"] == "open" else "Well pad"
    rows.append([f"{what}, centre x, y",
                 f"{site['pad'][0]:.0f}, {site['pad'][1]:.0f} µm"])
    if "aux_pad" in site:
        role = "Ring 1" if site["aux_role"] == "ring1" else "Plate"
        rows.append([f"{role} pad, centre x, y",
                     f"{site['aux_pad'][0]:.0f}, {site['aux_pad'][1]:.0f} "
                     f"µm"])
    rows.append(["Substrate", "Any of the seven SUB pads "
                 "(:numref:`tab-hvt-pads`)"])
    return rows


def procedures(name):
    p = STRUCTS[name]
    if p["kind"] == "open":
        return ["P1", "P2"]
    if p["half"] >= 50:
        return ["P1", "P2"]
    if p["sense"]:
        return ["P1", "P3", "P5"]
    return ["P1", "P4"] if p["gate"] else ["P1"]


def measurement(name):
    p, site = STRUCTS[name], SITES[name]
    procs = procedures(name)
    s = " and ".join(f"{{{k}}}" for k in procs) if len(procs) < 3 else \
        ", ".join(f"{{{k}}}" for k in procs[:-1]) + f" and {{{procs[-1]}}}"
    s = (f"Procedures {s} apply. " if len(procs) > 1
         else f"Procedure {s} applies. ")
    s += (f"The {'pad' if p['kind'] == 'open' else 'well pad'} is at "
          f"{site['pad'][0]:.0f}, {site['pad'][1]:.0f} µm")
    if "aux_pad" in site:
        role = "ring 1" if site["aux_role"] == "ring1" else "plate"
        s += (f" and the {role} pad at {site['aux_pad'][0]:.0f}, "
              f"{site['aux_pad'][1]:.0f} µm")
    s += ". "
    if p["gate"]:
        s += ("For {P1} the two pads are shorted at the probes. In {P4} "
              "the voltage between well and plate stays within 80 V. ")
    if p["half"] >= 50 and p["kind"] != "open":
        s += ("{P1} is run on one die only, to find the breakdown voltage "
              "that limits the bias of {P2} on the others. ")
    return s + cat.E[name]["m"]


def predicted(name):
    """(text, table or None) of the Predicted part."""
    p = STRUCTS[name]
    e = cat.E[name]
    lab = f"tab-hvt-sp-{slug(name)}"
    if p["kind"] == "open" or p["half"] >= 50:
        text = "No breakdown voltage is simulated for this structure. "
        if p["kind"] in CMODEL:
            ca, cp = CMODEL[p["kind"]]
            area, per = ph.octagon(p["half"], p["corner"])
            a, b = ca * area, cp * per * 1e6
            text += (f"The published junction model gives its capacitance "
                     f"at zero bias (:numref:`{lab}`). ")
            return text + e.get("r", ""), table(
                f"{name}: capacitance expected at zero bias from the "
                f"published model", lab, ["Part", "Capacitance (pF)"],
                [["Flat bottom", f"{a:.3f}"], ["Edge", f"{b:.3f}"],
                 ["Total", f"{a + b:.3f}"]], "50 50")
        return text + e.get("r", ""), None
    procs = [q for q in pd.PRED["processes"] if pd.known(name, q)]
    if not procs:
        return ("Not yet simulated: the results file has no entry for "
                "this structure. " + e.get("r", "")), None
    def rank(q):
        base = q[1:] if q.startswith("G") else q
        return (q.startswith("G"), pd.ORDER.index(pd.family(base)), q)

    procs.sort(key=rank)
    rows = []
    for q in procs:
        fam = pd.family(q)
        lo, hi, _ = pd.band(name, q) if q == fam else (None, None, None)
        twin = q[:-1] + "D"
        label = f"{q} and {twin}" if pd.stands_in(name, twin) else q
        if pd.stands_in(name, q):
            continue
        rows.append([label, pd.cell(name, q, "edge"),
                     pd.cell(name, q, "corner"), pd.span(lo, hi),
                     pd.span(lo, hi, pd.WIDEN)])
    text = (f"The simulated breakdown voltages are in :numref:`{lab}`, "
            f"with the band and agreement range of each family on the row "
            f"of its nominal process. ")
    return text + e.get("r", ""), table(
        f"{name}: predicted breakdown voltage by process", lab,
        ["Process", "Straight edge (V)", "Corner section (V)",
         "Family band (V)", "Agreement range (V)"], rows, "16 21 21 21 21")


def entry(name, files):
    e = cat.E[name]
    s = slug(name)
    files[f"catalogue/hvt-s-{name}.svg"] = fig_entry.entry(name)
    out = [f".. _hvt-s-{s}:", "", name, "-" * len(name), "",
           f".. figure:: hvt-s-{name}.svg", f"   :name: fig-hvt-s-{s}",
           wrap(":alt: " + fig_entry.alt(name), "         ")
           .replace("         :alt:", "   :alt:", 1), "",
           f"   {name} in plan view and in cross-section.", "",
           table(f"{name}: drawn parameters and position",
                 f"tab-hvt-s-{s}", ["Parameter", "Value"], param_rows(name),
                 "35 65")]
    text, tab = predicted(name)
    ring = fig_entry.ring(name) if STRUCTS[name]["sense"] else None
    if ring:
        files[f"catalogue/hvt-s-{name}-ring.svg"] = ring
        text += (f" :numref:`fig-hvt-sr-{s}` plots the predicted rise of "
                 f"ring 1.")
    parts = [
        ("Purpose", e["p"] + f" :numref:`fig-hvt-s-{s}` shows the "
         f"structure and :numref:`tab-hvt-s-{s}` lists what is drawn."),
        ("How it works", e["w"]),
        ("Measurement", measurement(name)),
        ("Predicted", text),
        ("Limits", e["l"])]
    for term, body in parts[:2]:
        out += [term, wrap(link(body, name)), ""]
    out += ["Compared with"]
    for other, what in e["c"]:
        out += [wrap(f"* {{{other}}}: {what}.", "   ").replace(
            f"{{{other}}}", link(f"{{{other}}}", name))
            .replace("\n   ", "\n     ")]
    out += [""]
    for term, body in parts[2:]:
        out += [term, wrap(link(body, name)), ""]
    if tab:
        out += [tab]
    if ring:
        out += [f".. figure:: hvt-s-{name}-ring.svg",
                f"   :name: fig-hvt-sr-{s}",
                wrap(f":alt: Graph of the predicted rise of ring 1 of "
                     f"{name} against well voltage, one curve per process "
                     f"that has a result, with a diagonal marking ring "
                     f"voltage equal to well voltage. Each curve leaves "
                     f"zero after a few volts and then rises below the "
                     f"diagonal.", "         ")
                .replace("         :alt:", "   :alt:", 1), "",
                f"   Predicted rise of ring 1 of {name}.", ""]
    return "\n".join(out)


def group_page(key, files):
    g = cat.GROUPS[key]
    names = [n for n in ORDER if page_of(n) == key]
    files[f"catalogue/hvt-g-{key}.svg"] = fig_group.FIGURES[key]()
    title = g["title"]
    lab = f"hvt-g-{g['file']}"
    listed = ", ".join(names)
    what = fig_group.ALT[key]
    out = [f".. _{lab}:", "", title, "=" * len(title), "",
           wrap(link(g["what"], key), ""), "",
           wrap(f"The group has {len(names)} structures: "
                + ", ".join(link(f"{{{n}}}", key) for n in names) + ".",
                ""), "",
           "Mechanism", "---------", "", wrap(link(g["works"], key), ""), "",
           "Expected results", "----------------", "",
           wrap(link(g["read"], key) + f" :numref:`fig-{lab}` shows the "
                f"trend that the simulation predicts.", ""), "",
           f".. figure:: hvt-g-{key}.svg", f"   :name: fig-{lab}",
           wrap(f":alt: Graph of {what}. The structures of the group are "
                f"{listed}. The plotted values are those of the tables in "
                f"the entries.", "         ")
           .replace("         :alt:", "   :alt:", 1), "",
           f"   Trend that the simulation predicts across the group.", "",
           "Limits of the group", "-------------------", "",
           wrap(link(g["limits"], key), ""), ""]
    out += [entry(n, files) for n in names]
    files[f"catalogue/{g['file']}.rst"] = "\n".join(out)


def first_sentence(s):
    return re.split(r"(?<=[.:])\s", s, 1)[0].rstrip(":") \
        if ". " in s or ": " in s else s


def generate():
    check()
    files = {}
    for key in PAGES:
        group_page(key, files)
    rows = []
    for n in ORDER:
        g = cat.GROUPS[page_of(n)]
        rows.append([link(f"{{{n}}}", n),
                     f":doc:`{g['title']} <catalogue/{g['file']}>`",
                     link(first_sentence(cat.E[n]["p"]), n)])
    title = "Structure catalogue"
    out = [".. _hvt-catalogue:", "", title, "=" * len(title), "",
           wrap(f"Each of the {len(ORDER)} structures on the test die has "
                f"an entry that states the one question it answers, how it "
                f"works, what it is compared with, how it is measured, what "
                f"the simulation predicts and what it cannot show. The "
                f"entries are grouped by what the structures vary.", ""), ""]
    for key in PAGES:
        g = cat.GROUPS[key]
        out += [f":doc:`catalogue/{g['file']}`",
                wrap(first_sentence(link(g["what"], key)), "   "), ""]
    out += [wrap("Every figure, parameter, position and predicted value of "
                 "an entry is generated from the layout's own data, so the "
                 "entries follow the layout. :numref:`tab-hvt-index` lists "
                 "every structure in the order of the floor plan "
                 "(:numref:`fig-hvt-floorplan`).", ""), "",
            table("Every structure on the die", "tab-hvt-index",
                  ["Structure", "Group", "Purpose"], rows, "14 22 64"),
            ".. toctree::", "   :hidden:", ""]
    out += [f"   catalogue/{cat.GROUPS[k]['file']}" for k in PAGES]
    files["catalogue.rst"] = "\n".join(out) + "\n"
    return files


def name_ref(name):
    """The link to an entry, for the tables of the structures page."""
    return f":ref:`{name} <hvt-s-{slug(name)}>`"

