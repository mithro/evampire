"""Assemble the test die: sites of (structure, pad) on a grid, substrate bus, labels.

    uv run --with klayout python silicon/hvtest/chip.py OUT.gds [MANIFEST.json]

The site list comes from structures.py. Each site is a junction cell with its Metal5
pad to the east; the P+ rings join a Metal1 substrate bus that runs up the west side of
every column to substrate pads. MANIFEST.json records every site's name, parameters and
pad centre, for the test method.
"""

from __future__ import annotations

import json
import sys

import klayout.db as kdb

import geom
import junction
import layers as L
import structures

DIE_W, DIE_H = 1936.0, 2531.0
EDGE = 60.0  # keep-out from the die edge (seal ring 26 um, guideline 30 um to pads)
PAD = 100.0  # Metal5 pad side
PAD_OPEN = 90.0
SITE_W, SITE_H = 300.0, 150.0  # site pitch
LARGE_BAND = 300.0  # band at the top for wells too big for a site
BUS_W = 6.0


def pad_cell(layout):
    c = layout.create_cell("pad")
    c.shapes(layout.layer(*L.METAL5)).insert(geom.box(-PAD / 2, -PAD / 2, PAD / 2, PAD / 2))
    h = PAD_OPEN / 2
    c.shapes(layout.layer(*L.PAD)).insert(geom.box(-h, -h, h, h))
    return c


def place(top, cell, x, y):
    top.insert(kdb.CellInstArray(cell.cell_index(), kdb.Trans(geom.nm(x), geom.nm(y))))


def build(sites, large=()):
    layout = kdb.Layout()
    layout.dbu = geom.DBU
    top = layout.create_cell("hvtest")
    pad = pad_cell(layout)
    m1, m2, m5 = layout.layer(*L.METAL1), layout.layer(*L.METAL2), layout.layer(*L.METAL5)
    up = layout.create_cell("m2_to_m5")  # via stack from Metal2 to Metal5
    sq = geom.box(-2.0, -2.0, 2.0, 2.0)
    for metal in L.METALS[1:]:
        up.shapes(layout.layer(*metal)).insert(sq)
    for via in L.VIAS[1:]:
        up.shapes(layout.layer(*via)).insert(geom.contacts(sq, junction.VIA, junction.VIA_PITCH, 0.3))
    cols = int((DIE_W - 2 * EDGE) // SITE_W)
    # the bottom strip holds the bus pads, the top band the large structures
    rows = int((DIE_H - 2 * EDGE - 160.0 - LARGE_BAND) // SITE_H)
    taken = set()
    manifest = {"die": [DIE_W, DIE_H], "sites": []}
    y_bus = EDGE + 130.0
    slot = 0
    for name, params in sites:
        col, row = slot % cols, slot // cols
        two = params.get("sense") or params.get("gate")
        slot += 1
        if two:  # the site above in the same column holds the second pad
            if row % 2 == 1:
                raise ValueError(f"{name}: two-pad structures must sit in an even row")
            taken.add((col, row + 1))
        while (slot % cols, slot // cols) in taken:
            slot += 1
        x0 = EDGE + col * SITE_W  # west edge of the site
        cy = y_bus + 30.0 + SITE_H / 2 + row * SITE_H
        p = {**junction.DEFAULTS, **params}
        bh = junction.block_half(p)
        cx = x0 + BUS_W + 4.0 + 62.0  # structure centre: room for the largest block
        cell = junction.build(layout, f"s_{name}", params)
        place(top, cell, cx, cy)
        # Metal1 from the cell's west tab to the column bus
        top.shapes(m1).insert(geom.box(x0, cy - 1.5, cx - bh, cy + 1.5))
        # pad to the east, Metal5 lead from the cell edge
        px = x0 + SITE_W - 20.0 - PAD / 2
        place(top, pad, px, cy)
        top.shapes(m5).insert(geom.box(cx + bh, cy - junction.LEAD_W / 2, px - PAD / 2, cy + junction.LEAD_W / 2))
        top.shapes(m5).insert(geom.text(layout, name, 8.0, px - PAD / 2, cy + PAD / 2 + 4.0))
        site = {"name": name, "params": p, "pad": [px, cy], "centre": [cx, cy]}
        if p["sense"] or p["gate"]:
            # second pad in the site above: Metal2 north, then east, then up to Metal5
            ay = cy + SITE_H
            top.shapes(m2).insert(geom.box(cx - 1.2, cy + bh, cx + 1.2, ay + 1.2))
            top.shapes(m2).insert(geom.box(cx - 1.2, ay - 1.2, px - PAD / 2 + 4.0, ay + 1.2))
            place(top, up, px - PAD / 2 + 2.0, ay)
            place(top, pad, px, ay)
            role = "ring1" if p["sense"] else "gate"
            top.shapes(m5).insert(geom.text(layout, f"{name}.{role[0].upper()}", 8.0,
                                            px - PAD / 2, ay + PAD / 2 + 4.0))  # fmt: skip
            site["aux_pad"] = [px, ay]
            site["aux_role"] = role
        manifest["sites"].append(site)
    # large structures in the top band, each with its pad to the east
    y_top = y_bus + 30.0 + rows * SITE_H
    x_next = EDGE + BUS_W + 4.0
    for name, params in large:
        p = {**junction.DEFAULTS, **params}
        bh = junction.block_half(p)
        cx = x_next + bh
        cy = y_top + LARGE_BAND / 2
        px = cx + bh + 30.0 + PAD / 2
        x_next = px + PAD / 2 + 30.0
        if px + PAD / 2 > DIE_W - EDGE or bh > 125.0:
            raise ValueError(f"{name}: does not fit the large band")
        place(top, junction.build(layout, f"s_{name}", params), cx, cy)
        place(top, pad, px, cy)
        top.shapes(m5).insert(geom.box(cx + bh, cy - junction.LEAD_W / 2, px - PAD / 2, cy + junction.LEAD_W / 2))
        top.shapes(m5).insert(geom.text(layout, name, 8.0, px - PAD / 2, cy + PAD / 2 + 4.0))
        # substrate: a strap straight down from the bottom of the P+ ring to the top bus
        ring_bottom = cy - (p["half"] + p["term"])
        top.shapes(m1).insert(geom.box(cx - BUS_W / 2, y_top, cx + BUS_W / 2, ring_bottom))
        manifest["sites"].append({"name": name, "params": p, "pad": [px, cy], "centre": [cx, cy]})
    if (slot - 1) // cols >= rows:
        raise ValueError(f"sites need {(slot - 1) // cols + 1} rows; {rows} fit")
    # column buses and the bottom bus on Metal1, with substrate pads
    for col in range(cols):
        x0 = EDGE + col * SITE_W
        top.shapes(m1).insert(geom.box(x0, y_bus, x0 + BUS_W, y_top))
    if large:  # a bus along the top of the columns, which the large wells strap down to
        top.shapes(m1).insert(geom.box(EDGE, y_top, EDGE + cols * SITE_W, y_top + BUS_W))
    top.shapes(m1).insert(geom.box(EDGE, y_bus - BUS_W, EDGE + cols * SITE_W, y_bus))
    stack = layout.create_cell("sub_pad")
    place(stack, pad, 0, 0)
    sq = geom.box(-10, PAD / 2 - 20, 10, PAD / 2 + 14)
    for metal in L.METALS:
        stack.shapes(layout.layer(*metal)).insert(sq)
    for via in L.VIAS:
        stack.shapes(layout.layer(*via)).insert(geom.contacts(sq, junction.VIA, junction.VIA_PITCH, 0.3))
    manifest["sub_pads"] = []
    for col in range(cols):
        px = EDGE + col * SITE_W + 100.0
        place(top, stack, px, y_bus - BUS_W - 8.0 - PAD / 2)
        manifest["sub_pads"].append([px, y_bus - BUS_W - 8.0 - PAD / 2])
    top.shapes(m5).insert(geom.text(layout, "SUB", 8.0, EDGE + cols * SITE_W + 5.0, EDGE + 20.0))
    return layout, manifest


if __name__ == "__main__":
    layout, manifest = build(structures.SITES, structures.LARGE)
    opts = kdb.SaveLayoutOptions()
    opts.write_context_info = False
    layout.write(sys.argv[1], opts)
    if len(sys.argv) > 2:
        json.dump(manifest, open(sys.argv[2], "w"), indent=1)
    print(f"{len(structures.SITES)} + {len(structures.LARGE)} sites written to {sys.argv[1]}")
