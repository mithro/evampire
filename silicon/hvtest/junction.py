"""One junction test structure: a well against the substrate with its edge termination.

The structure is concentric about (0, 0). From the centre outwards: the well (N-well or
deep N-well) with an N+ contact ring just inside its edge; the termination zone, which
may hold floating N-well rings, field plates tied to the well, a drawn P-well or a NAT
(native, no P-well) region; then a P+ substrate ring. The well's lead leaves on Metal5
to the east; the substrate ring's Metal1 tab leaves to the west.

Parameters (micrometres), with defaults in DEFAULTS:

  kind       "nw" (N-well) or "dnw" (deep N-well)
  half       half the side of the well
  corner     corner radius of the well outline (0 = sharp square); 45-degree cuts
             approximate the arc, and every outer outline is offset concentrically
  inset      distance from the well edge in to the N+ contact ring
  ncomp_w    width of the N+ contact ring and of the P+ substrate ring
  term       distance from the well edge to the P+ substrate ring
  rings      [[gap, width], ...] floating N-well rings, innermost first
  plates     {"poly": L, "m1": L, "m2": L}: length of each plate beyond the well edge
  pwell_gap  None, or the distance from the well edge at which a drawn P-well starts
  nat_gap    None, or the distance from the well edge at which the NAT layer starts
  sense      True adds a contact and a Metal2 lead (to the north) on the first ring
"""

from __future__ import annotations

import klayout.db as kdb

import geom
import layers as L

DEFAULTS = {
    "kind": "nw", "half": 15.0, "corner": 3.0, "inset": 2.0, "ncomp_w": 2.0, "term": 20.0,
    "rings": [], "plates": {}, "pwell_gap": None, "nat_gap": None, "sense": False,
}  # fmt: skip

CUT, CUT_PITCH = 0.22, 0.50  # contact size and pitch (0.28 space, as arrays need)
VIA, VIA_PITCH = 0.26, 0.62  # via size and pitch (0.36 space)
IMPLANT = 0.23  # N+/P+ implant beyond COMP
BLOCK_MARGIN = 3.0  # fill-block margin beyond the P+ ring
LEAD_W = 6.0  # Metal5 lead width
STACK = 2.6  # side of the via-stack squares


def outline(p, d):
    """The well outline moved out by d (in for d < 0), corners kept concentric."""
    return geom.shape(p["half"] + d, max(p["corner"] + d, 0.0))


def annulus(p, d0, d1):
    return outline(p, d1) - outline(p, d0)


def block_half(p):
    """Half the side of the square that the fill blocks and the cell occupy."""
    return p["half"] + p["term"] + p["ncomp_w"] + BLOCK_MARGIN


def build(layout: kdb.Layout, name: str, params: dict) -> kdb.Cell:
    p = {**DEFAULTS, **params}
    cell = layout.create_cell(name)
    reg = {}

    def add(layer, region):
        reg[layer] = reg.get(layer, kdb.Region()) + region

    half, inset, w, term = p["half"], p["inset"], p["ncomp_w"], p["term"]
    add(L.NWELL if p["kind"] == "nw" else L.DNWELL, outline(p, 0.0))

    # N+ contact ring inside the well edge
    ncomp = annulus(p, -inset - w, -inset)
    add(L.COMP, ncomp)
    # implants are drawn as offset outlines: sizing a 45-degree edge would leave the grid
    add(L.NPLUS, annulus(p, -inset - w - IMPLANT, -inset + IMPLANT))
    add(L.CONTACT, geom.contacts(ncomp, CUT, CUT_PITCH, 0.15))
    m1_out = -inset  # outer offset of the well's Metal1

    # field plates tied to the well
    plates = p["plates"]
    if "poly" in plates:
        poly = annulus(p, -inset + 0.4, plates["poly"])
        add(L.POLY2, poly)
        tie = annulus(p, -inset + 0.5, -inset + 1.2)  # contacts to the poly, under Metal1
        add(L.CONTACT, geom.contacts(tie, CUT, CUT_PITCH, 0.12))
        m1_out = -inset + 1.3
    if "m1" in plates:
        m1_out = plates["m1"]
    add(L.METAL1, annulus(p, -inset - w, m1_out))
    if "m2" in plates:
        add(L.METAL2, annulus(p, -inset - w, plates["m2"]))
        add(L.VIA1, geom.contacts(ncomp, VIA, VIA_PITCH, 0.3))

    # floating rings
    d = 0.0
    first_ring = None
    for gap, width in p["rings"]:
        d += gap
        add(L.NWELL, annulus(p, d, d + width))
        first_ring = first_ring or (d, width)
        d += width

    # P+ substrate ring, with a Metal1 tab to the west edge of the cell
    pcomp = annulus(p, term, term + w)
    add(L.COMP, pcomp)
    add(L.PPLUS, annulus(p, term - IMPLANT, term + w + IMPLANT))
    add(L.CONTACT, geom.contacts(pcomp, CUT, CUT_PITCH, 0.15))
    add(L.METAL1, pcomp)
    bh = block_half(p)
    add(L.METAL1, geom.box(-bh, -1.5, -(half + term), 1.5))

    if p["pwell_gap"] is not None:
        add(L.LVPWELL, annulus(p, p["pwell_gap"], term + w + 1.0))
    if p["nat_gap"] is not None:
        add(L.NAT, annulus(p, p["nat_gap"], term - 0.5))

    # the well's via stack and Metal5 lead to the east
    sx = half - inset - w / 2  # centre of the N+ ring on the east side
    sq = geom.box(sx - STACK / 2, -STACK / 2, sx + STACK / 2, STACK / 2)
    for metal in L.METALS:
        add(metal, sq)
    for via in L.VIAS:
        add(via, geom.contacts(sq, VIA, VIA_PITCH, 0.3))
    add(L.METAL5, geom.box(sx, -LEAD_W / 2, bh, LEAD_W / 2))

    # optional sense contact on the first ring, Metal2 lead to the north
    if p["sense"] and first_ring:
        rd, rw = first_ring
        y = half + rd + rw / 2
        tap = geom.box(-0.9, y - 0.3, 0.9, y + 0.3)
        add(L.COMP, tap)
        add(L.NPLUS, tap.sized(geom.nm(IMPLANT)))
        add(L.CONTACT, geom.contacts(tap, CUT, CUT_PITCH, 0.1))
        add(L.METAL1, geom.box(-1.2, y - 0.6, 1.2, y + 0.6))
        add(L.VIA1, geom.contacts(geom.box(-1.2, y - 0.6, 1.2, y + 0.6), VIA, VIA_PITCH, 0.15))
        add(L.METAL2, geom.box(-1.2, y - 0.6, 1.2, bh))

    # keep dummy fill out of the whole structure
    blk = geom.box(-bh, -bh, bh, bh)
    add(L.NDMY, blk)
    add(L.PMNDMY, blk)

    for layer, region in reg.items():
        region.merge()
        cell.shapes(layout.layer(*layer)).insert(region)
    return cell
