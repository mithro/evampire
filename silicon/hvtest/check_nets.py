"""Check the die's electrical connections by extracting nets from the layout.

    uv run --with klayout python silicon/hvtest/check_nets.py RAW.gds MANIFEST.json

DRC cannot see an open circuit or a wrong connection, so this checks, from the geometry
alone: every well pad reaches the N+ ring of its own well and nothing else's; no two pads
share a net; no pad is on the substrate net; every P+ ring and every substrate pad is on
one substrate net; a ring-sense pad reaches ring 1; a gate pad reaches its plate and not
the well. It exits non-zero and lists the problems if any check fails.
"""

from __future__ import annotations

import json
import sys

import klayout.db as kdb

import layers as L

STACK = [(L.CONTACT, L.METAL1), (L.METAL1, L.VIA1), (L.VIA1, L.METAL2), (L.METAL2, L.VIA2),
         (L.VIA2, L.METAL3), (L.METAL3, L.VIA3), (L.VIA3, L.METAL4), (L.METAL4, L.VIA4),
         (L.VIA4, L.METAL5)]  # fmt: skip
PLATE_LAYER = {"poly": L.POLY2, "m1": L.METAL1, "m2": L.METAL2}


def extract(layout):
    top = layout.top_cell()
    l2n = kdb.LayoutToNetlist(kdb.RecursiveShapeIterator(layout, top, []))
    lay = {}
    for spec in (L.COMP, L.NPLUS, L.PPLUS, L.NWELL, L.DNWELL, L.POLY2, L.CONTACT,
                 *L.METALS, *L.VIAS):  # fmt: skip
        lay[spec] = l2n.make_layer(layout.layer(*spec), f"l{spec[0]}_{spec[1]}")
    wells = lay[L.NWELL] + lay[L.DNWELL]
    ntap = (lay[L.COMP] & lay[L.NPLUS]) & wells
    ptap = (lay[L.COMP] & lay[L.PPLUS]) - wells
    l2n.register(ntap, "ntap")
    l2n.register(ptap, "ptap")
    for region in (lay[L.NWELL], lay[L.DNWELL], ntap, ptap, lay[L.POLY2], lay[L.CONTACT],
                   *(lay[m] for m in L.METALS), *(lay[v] for v in L.VIAS)):  # fmt: skip
        l2n.connect(region)
    l2n.connect(lay[L.NWELL], ntap)
    l2n.connect(lay[L.DNWELL], ntap)
    l2n.connect(lay[L.DNWELL], lay[L.NWELL])
    for a in (ntap, ptap, lay[L.POLY2]):
        l2n.connect(a, lay[L.CONTACT])
    for a, b in STACK:
        l2n.connect(lay[a], lay[b])
    l2n.extract_netlist()
    return l2n, lay, ptap


def main(argv):
    layout = kdb.Layout()
    layout.read(argv[0])
    man = json.load(open(argv[1]))
    l2n, lay, ptap = extract(layout)

    def net(layer, x, y):
        n = l2n.probe_net(lay[layer] if not isinstance(layer, kdb.Region) else layer, kdb.DPoint(x, y))
        return None if n is None else n.cluster_id

    problems = []
    subs = {net(L.METAL5, x, y) for x, y in man["sub_pads"]}
    if len(subs) != 1 or None in subs:
        problems.append(f"substrate pads are on {len(subs)} nets")
    sub = next(iter(subs))
    sub_net = l2n.probe_net(lay[L.METAL5], kdb.DPoint(*man["sub_pads"][0]))
    off = ptap.merged() - l2n.shapes_of_net(sub_net, ptap, True)
    for poly in off.each():
        problems.append(f"P+ not on the substrate net at {poly.bbox()}")
    seen = {}
    for s in man["sites"]:
        name, p = s["name"], s["params"]
        cx, cy = s["centre"]
        pad = net(L.METAL5, *s["pad"])
        if pad is None or pad == sub:
            problems.append(f"{name}: pad is unconnected or on the substrate net")
        if pad in seen:
            problems.append(f"{name}: pad shares a net with {seen[pad]}")
        seen[pad] = name
        if p["kind"] != "open":
            well = net(L.DNWELL if p["kind"] == "dnw" else L.NWELL, cx, cy)
            if well is None or well != pad:
                problems.append(f"{name}: pad does not reach its well")
        if "aux_pad" in s:
            aux = net(L.METAL5, *s["aux_pad"])
            if aux is None or aux in (pad, sub) or aux in seen:
                problems.append(f"{name}: second pad is unconnected or shorted")
            seen[aux] = name + " (second pad)"
            if s["aux_role"] == "ring1":
                gap, width = p["rings"][0]
                want = net(L.NWELL, cx, cy - (p["half"] + gap + width / 2))
            else:
                layer, length = next(iter(p["plates"].items()))
                want = net(PLATE_LAYER[layer], cx, cy - (p["half"] + length - 0.3))
            if want is None or want != aux:
                problems.append(f"{name}: second pad does not reach its {s['aux_role']}")
        # every ring other than a sensed ring 1 floats: its net holds no pad and no P+ ring
        d = 0.0
        for k, (gap, width) in enumerate(p["rings"]):
            d += gap
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                r = p["half"] + d + width / 2
                ring = net(L.NWELL, cx + dx * r, cy + dy * r)
                sensed = k == 0 and p["sense"]
                if ring is None or (not sensed and (ring == pad or ring == sub or ring in seen)):
                    problems.append(f"{name}: ring {k + 1} is missing or connected")
                if sensed and ring != net(L.METAL5, *s["aux_pad"]):
                    problems.append(f"{name}: ring 1 is not continuous to its pad")
            d += width
        # a plate that is not gated is tied to the well, on every side
        if not p["gate"]:
            for layer, length in p["plates"].items():
                for dx, dy in ((0, -1), (0, 1), (-1, 0)):
                    r = p["half"] + length - 0.3
                    if net(PLATE_LAYER[layer], cx + dx * r, cy + dy * r) != pad:
                        problems.append(f"{name}: {layer} plate is not tied to the well")
    for line in problems:
        print("PROBLEM", line)
    print(f"{len(man['sites'])} sites checked, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
