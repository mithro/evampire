"""The test structures on the die: (name, junction parameters), in placement order.

Naming: N = N-well, D = deep N-well, then the feature that varies and its size in
micrometres (a "p" stands for the decimal point). Unless a name says otherwise the well is
30 um across with 8 um corners and the P+ substrate ring is 20 um from the well edge.

  T   distance to the P+ ring          C   corner radius of the well
  W   drawn P-well starting at         A   NAT (no P-well) starting at ("o1": overlapping
                                           the well edge by 1 um)
  P / M1 / M2   field plate of poly / Metal1 / Metal2, length beyond the well edge
  R   floating rings (number, then first gap)
  G   gated diode: the plate has its own pad      S  ring 1 has its own pad
  b   second copy                                  L  wide Metal5 lead
  V   in the 6 V (Dualgate) area

The P+ ring of a ring structure is at least 15 um beyond its last ring, so that the rings
and not the P+ ring limit it.
"""

BASE = {"half": 15.0, "corner": 8.0, "term": 20.0}


def s(**kw):
    return {**BASE, **kw}


def rings(*gaps, width=2.0):
    return [[g, width] for g in gaps]


# Two-pad structures come first: each also takes the site above it.
TWO_PAD = [
    ("NR1S2", s(rings=rings(2.0), sense=True)),
    ("NR1S3", s(rings=rings(3.0), sense=True)),
    ("NR4S", s(rings=rings(1.6, 2.0, 2.5, 3.0), term=35.0, sense=True)),
    ("NGP4", s(plates={"poly": 4.0}, gate=True)),
    ("NGM1", s(plates={"m1": 6.0}, gate=True)),
    ("NAGM1", s(plates={"m1": 6.0}, gate=True, nat_gap=0.6)),
    ("DGM1", s(kind="dnw", plates={"m1": 6.0}, gate=True)),
]

ONE_PAD = [
    # what surrounds a plain N-well: distance to the P+ ring, and the corner
    ("NT1", s(term=1.0)), ("NT5", s(term=5.0)), ("NT10", s(term=10.0)), ("NT20", s()), ("NT35", s(term=35.0)),
    ("NC0", s(corner=0.0)), ("NC15", s(corner=15.0)),
    # a drawn P-well at a set distance
    ("NW0", s(pwell_gap=0.0)), ("NW1p5", s(pwell_gap=1.5)),
    ("NW3", s(pwell_gap=3.0)), ("NW6", s(pwell_gap=6.0)),
    # NAT keeps the generated P-well away
    ("NA0p6", s(nat_gap=0.6)), ("NA2", s(nat_gap=2.0)), ("NA0p6T10", s(nat_gap=0.6, term=10.0)),
    ("NA4", s(nat_gap=4.0)),
    ("NA0p6T35", s(nat_gap=0.6, term=35.0)), ("NA0p6C0", s(nat_gap=0.6, corner=0.0)),
    ("NAM1_3", s(nat_gap=0.6, plates={"m1": 3.0})), ("NAM1_6", s(nat_gap=0.6, plates={"m1": 6.0})),
    ("NAM1_10", s(nat_gap=0.6, plates={"m1": 10.0})),
    ("NAM2_12", s(nat_gap=0.6, plates={"m2": 12.0})),
    # field plates on a plain N-well
    ("NP1", s(plates={"poly": 1.0})), ("NP2", s(plates={"poly": 2.0})), ("NP4", s(plates={"poly": 4.0})),
    ("NM1_3", s(plates={"m1": 3.0})), ("NM1_6", s(plates={"m1": 6.0})), ("NM1_10", s(plates={"m1": 10.0})),
    ("NM2_6", s(plates={"m2": 6.0})), ("NM2_12", s(plates={"m2": 12.0})),
    ("NPM12", s(plates={"poly": 2.0, "m1": 5.0, "m2": 9.0})),
    # floating rings
    ("NR1_1p4", s(rings=rings(1.4))), ("NR1_2", s(rings=rings(2.0))), ("NR1_3", s(rings=rings(3.0))),
    ("NR3_1p5", s(rings=rings(1.5, 2.0, 2.5), term=30.0)), ("NR3_2", s(rings=rings(2.0, 2.5, 3.0), term=30.0)),
    ("NR3W1", s(rings=rings(2.0, 2.5, 3.0, width=1.0), term=30.0)),
    ("NR3W3", s(rings=rings(2.0, 2.5, 3.0, width=3.0), term=35.0)),
    ("NR5_1p4", s(rings=rings(1.4, 1.7, 2.0, 2.4, 2.8), term=35.0)),
    ("NR5_2", s(rings=rings(2.0, 2.5, 3.0, 3.5, 4.0), term=40.0)),
    ("NR3M1", s(rings=rings(2.0, 2.5, 3.0), plates={"m1": 3.0}, term=30.0)),
    # deep N-well
    ("DT2p6", s(kind="dnw", term=2.6)), ("DT5", s(kind="dnw", term=5.0)), ("DT10", s(kind="dnw", term=10.0)),
    ("DT20", s(kind="dnw")), ("DT35", s(kind="dnw", term=35.0)),
    ("DC0", s(kind="dnw", corner=0.0)), ("DC15", s(kind="dnw", corner=15.0)),
    ("DW1p5", s(kind="dnw", pwell_gap=1.5)), ("DW3", s(kind="dnw", pwell_gap=3.0)),
    ("DW6", s(kind="dnw", pwell_gap=6.0)),
    ("DM1_3", s(kind="dnw", plates={"m1": 3.0})), ("DM1_6", s(kind="dnw", plates={"m1": 6.0})),
    ("DM1_10", s(kind="dnw", plates={"m1": 10.0})),
    ("DPM12", s(kind="dnw", plates={"poly": 2.0, "m1": 5.0, "m2": 9.0})),
    # deep N-well with NAT overlapping its edge: no P-well can lie beside the junction
    ("DAo1", s(kind="dnw", nat_gap=-1.0)), ("DAo1T35", s(kind="dnw", nat_gap=-1.0, term=35.0)),
    ("DAo1C0", s(kind="dnw", nat_gap=-1.0, corner=0.0)),
    ("DAo1M1_6", s(kind="dnw", nat_gap=-1.0, plates={"m1": 6.0})),
    # references: a pad and lead with no junction; second copies of three structures, placed
    # far from the first, for the spread across the die; and a plain well whose Metal5 lead
    # is 30 um wide, to show what the lead itself does to the junction it crosses
    ("OPEN", s(kind="open")), ("NT20b", s()), ("DT20b", s(kind="dnw")),
    ("NA0p6b", s(nat_gap=0.6)), ("NT20L", s(lead_w=30.0)),
    # the plain well in the 6 V area: the PDK models give the N-well 11 V there and 14 V
    # in the 3.3 V area with the same capacitance
    ("NT20V", s(dualgate=True)),
]

SITES = TWO_PAD + ONE_PAD

# Wells too large for a standard site; no fill block (it would exceed the NDMY size limit).
BIG = {"corner": 20.0, "term": 6.0, "block": False}
LARGE = [
    ("CVN", {"half": 100.0, **BIG}),
    ("CVD", {"kind": "dnw", "half": 100.0, **BIG}),
    # the 100 um wells fit one fill block (122 um square, under the 15000 um2 limit)
    ("CVN2", {"half": 50.0, **BIG, "block": True}),
    ("CVD2", {"kind": "dnw", "half": 50.0, **BIG, "block": True}),
    # with NAT around it and the P+ ring 20 um out, so that the capacitance sweep can go
    # past the 14 V of a well with a P-well beside it
    ("CVNA", {"half": 50.0, "corner": 20.0, "term": 20.0, "nat_gap": 0.6, "block": "ring"}),
]
