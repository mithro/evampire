"""One junction test structure: a well against the substrate with its edge termination.

The structure is concentric about (0, 0). From the centre outwards: the well (N-well or
deep N-well) with an N+ contact ring just inside its edge; the termination zone, which
may hold floating N-well rings, field plates tied to the well, a drawn P-well or a NAT
(native, no P-well) region; then a P+ substrate ring. The well's lead leaves on Metal5
to the east; the substrate ring's Metal1 tab leaves to the west.

Parameters (micrometres), with defaults in DEFAULTS:

  kind       "nw" (N-well), "dnw" (deep N-well) or "open" (lead only, no junction)
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
             (at least 0.5 from an N-well, rule NAT.3; negative for a deep N-well, whose
             edge the NAT layer may overlap)
  sense      True adds a contact and a Metal2 lead (to the north) on the first ring
  gate       True ties the plates to their own Metal2 lead (to the north) instead of to
             the well, making a gated diode; the plates then start 0.5 um inside the well edge
  lead_w     width of the Metal5 lead where it crosses the termination (6 by default; a
             wide lead is the control for the lead's own effect on the junction)
  dualgate   True puts the structure in the 6 V (thick gate oxide) area
  block      False leaves out the fill blocks (for wells too large for one NDMY shape);
             "ring" blocks fill only over the termination zone

A structure has at most one north lead: sense or gate, not both.
"""

from __future__ import annotations

import klayout.db as kdb

import geom
import layers as L

DEFAULTS = {
    "kind": "nw", "half": 15.0, "corner": 3.0, "inset": 2.0, "ncomp_w": 2.0, "term": 20.0,
    "rings": [], "plates": {}, "pwell_gap": None, "nat_gap": None, "sense": False,
    "gate": False, "block": True, "lead_w": 6.0, "dualgate": False,
}  # fmt: skip

CUT, CUT_PITCH = 0.22, 0.50  # contact size and pitch (0.28 space, as arrays need)
VIA, VIA_PITCH = 0.26, 0.62  # via size and pitch (0.36 space)
IMPLANT = 0.23  # N+/P+ implant beyond COMP
BLOCK_MARGIN = 3.0  # fill-block margin beyond the P+ ring
LEAD_W = 6.0  # Metal5 lead width outside the cell
STACK = 2.6  # side of the via-stack squares
NORTH_CLEAR = 4.0  # half-width of the gap in the P+ ring's Metal1 under a north lead


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
    if p["kind"] == "open":
        # reference for the pad and lead capacitance: the lead with no junction under it
        bh = block_half(p)
        sx = half - inset - w / 2
        cell.shapes(layout.layer(*L.METAL5)).insert(geom.box(sx, -p["lead_w"] / 2, bh, p["lead_w"] / 2))
        for layer in (L.NDMY, L.PMNDMY):
            cell.shapes(layout.layer(*layer)).insert(geom.box(-bh, -bh, bh, bh))
        return cell
    add(L.NWELL if p["kind"] == "nw" else L.DNWELL, outline(p, 0.0))

    if p["kind"] == "dnw":
        # an N-well under the contact ring: the deep N-well alone is lightly doped at the
        # surface, and its contact resistance is not published
        add(L.NWELL, annulus(p, -inset - w - 0.3, -inset + 0.3))
    # N+ contact ring inside the well edge
    ncomp = annulus(p, -inset - w, -inset)
    add(L.COMP, ncomp)
    # implants are drawn as offset outlines: sizing a 45-degree edge would leave the grid
    add(L.NPLUS, annulus(p, -inset - w - IMPLANT, -inset + IMPLANT))
    add(L.CONTACT, geom.contacts(ncomp, CUT, CUT_PITCH, 0.15))
    m1_out = -inset  # outer offset of the well's Metal1

    # field plates: tied to the well, or (gate) on their own lead
    plates = p["plates"]
    bh = block_half(p)
    north = None  # Metal1 patch that the north Metal2 lead lands on
    if p["gate"]:
        # plates start here: 1.2 um clear of the via stack's Metal1 and 1.5 um clear of the
        # well's Metal1 ring, so that 80 V between plate and well is under 0.7 MV/cm
        g0 = -0.5
        if "poly" in plates:
            add(L.POLY2, annulus(p, g0, plates["poly"]))
            patch = geom.box(-1.2, half + g0 + 0.1, 1.2, half + g0 + 1.3)
            add(L.CONTACT, geom.cut_row(0.0, half + g0 + 0.7, 3, CUT, CUT_PITCH))
            north = patch
        if "m1" in plates:
            add(L.METAL1, annulus(p, g0, plates["m1"]))
            north = geom.box(-1.2, half + g0 + 0.1, 1.2, half + g0 + 1.3)
        if "m2" in plates:
            add(L.METAL2, annulus(p, g0, plates["m2"]))
            if north is None:  # a Metal2-only gate needs no Metal1 patch
                add(L.METAL2, geom.box(-1.2, half + g0, 1.2, bh))
        add(L.METAL1, annulus(p, -inset - w, -inset))
    else:
        if "poly" in plates:
            add(L.POLY2, annulus(p, -inset + 0.4, plates["poly"]))
            # contacts to the poly, under Metal1; 1 um wide so that the 0.5 um contact grid
            # lands in it on every side
            tie = annulus(p, -inset + 0.45, -inset + 1.45)
            add(L.CONTACT, geom.contacts(tie, CUT, CUT_PITCH, 0.12))
            m1_out = -inset + 1.55
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
    pmetal = pcomp
    if p["sense"] or p["gate"]:
        # no grounded Metal1 under the north lead: the lead may sit at the well voltage, and
        # only 0.6 um of oxide separates Metal1 from Metal2
        pmetal = pcomp - geom.box(-NORTH_CLEAR, half, NORTH_CLEAR, half + term + w + 1.0)
    add(L.CONTACT, geom.contacts(pmetal, CUT, CUT_PITCH, 0.15))
    add(L.METAL1, pmetal)
    add(L.METAL1, geom.box(-bh, -1.5, -(half + term), 1.5))

    if p["pwell_gap"] is not None:
        add(L.LVPWELL, annulus(p, p["pwell_gap"], term + w + 1.0))
    if p["nat_gap"] is not None:
        nat = annulus(p, p["nat_gap"], term - 0.5)
        # rings under NAT: the layer keeps 0.5 um from every N-well (rule NAT.3; 0.6 drawn), so it
        # is cut into strips between the rings
        d = 0.0
        for gap, width in p["rings"]:
            d += gap
            nat -= annulus(p, d - 0.6, d + width + 0.6)
            d += width
        add(L.NAT, nat)

    # the well's via stack and Metal5 lead to the east
    sx = half - inset - w / 2  # centre of the N+ ring on the east side
    sq = geom.box(sx - STACK / 2, -STACK / 2, sx + STACK / 2, STACK / 2)
    for metal in L.METALS:
        add(metal, sq)
    for via in L.VIAS:
        add(via, geom.contacts(sq, VIA, VIA_PITCH, 0.3))
    add(L.METAL5, geom.box(sx, -p["lead_w"] / 2, bh, p["lead_w"] / 2))

    # optional sense contact on the first ring
    if p["sense"] and first_ring:
        rd, rw = first_ring
        y = half + rd + rw / 2
        tap = geom.box(-0.9, y - 0.3, 0.9, y + 0.3)
        add(L.COMP, tap)
        add(L.NPLUS, tap.sized(geom.nm(IMPLANT)))
        add(L.CONTACT, geom.cut_row(0.0, y, 3, CUT, CUT_PITCH))
        north = geom.box(-1.2, y - 0.6, 1.2, y + 0.6)
    # the north lead on Metal2, from its Metal1 patch to the cell edge
    if north is not None:
        add(L.METAL1, north)
        add(L.VIA1, geom.contacts(north, VIA, VIA_PITCH, 0.15))
        nb = north.bbox()
        add(L.METAL2, kdb.Region(kdb.Box(nb.left, nb.bottom, nb.right, geom.nm(bh))))

    # keep dummy fill out of the whole structure
    if p["dualgate"]:
        add(L.DUALGATE, geom.box(-bh, -bh, bh, bh))
    if p["block"]:
        blk = geom.box(-bh, -bh, bh, bh)
        if p["block"] == "ring":
            blk -= outline(p, -1.0)
        add(L.NDMY, blk)
        add(L.PMNDMY, blk)

    for layer, region in reg.items():
        region.merge()
        cell.shapes(layout.layer(*layer)).insert(region)
    return cell
