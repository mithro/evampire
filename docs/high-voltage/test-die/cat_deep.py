"""Catalogue texts: deep N-wells, capacitance wells and the open reference.

catalogue.py joins these modules; its docstring describes the fields.

SPDX-License-Identifier: Apache-2.0
"""

E = {}

# ---- deep N-wells ----------------------------------------------------------
E["DT20"] = dict(
    p="The reference deep N-well: default dimensions, nothing drawn "
      "round it.",
    w="The deep N-well is implanted deep, with its peak about 2.5 µm "
      "down, and reaches the surface only through the N-well band under "
      "its contact. Its junction to a P layer just below it is the most "
      "heavily doped junction it has, and fails first.",
    c=[("NT20", "a deep N-well in place of an N-well"),
       ("DT20b", "nothing: a second copy"),
       ("DT2p6", "the ring is at 20 µm in place of 2.6 µm")],
    m="Swept again at 85 °C.",
    r="Near the published 30 V: the deep-layer picture holds. Far "
      "above it: the model value does not describe this well. Its "
      "prediction is a fit, not a test: the deep N-well profile was "
      "fitted to the published 30.48 V with the same ionisation "
      "integral.",
    l="A breakdown at the bottom cannot be told from one at the edge "
      "by this structure alone; the rest of the group does that.")
E["DT2p6"] = dict(
    p="A deep N-well with its P+ ring as close as the rules allow, "
      "2.6 µm.",
    w="At 2.6 µm the ring would cut the edge's depletion region short "
      "if the edge held the voltage. If the bottom fails first, the "
      "ring's distance is irrelevant.",
    c=[("DT20", "the ring is at 2.6 µm in place of 20 µm"),
       ("NT1", "the nearest ring on a deep N-well in place of on an "
               "N-well")],
    m="",
    r="Equal to {DT20}: the bottom limits. Lower: the edge does, at "
      "least with the ring this close.",
    l="Under assumption A a generated P-well would start 1.5 µm out, "
      "inside the ring, and would act before the ring.")
E["DC0"] = dict(
    p="A deep N-well with square corners.",
    w="A deep implant spreads sideways more than a shallow one, so its "
      "corners are rounder below the surface than the drawing. A "
      "square corner should cost a deep N-well less than it costs an "
      "N-well, and nothing if the bottom fails first.",
    c=[("DT20", "four 90° vertices in place of eight of 135°"),
       ("NC0", "a deep N-well in place of an N-well")],
    m="",
    r="Equal to {DT20}: corners do not matter for this well, which is "
      "what the simulated square corner gives.",
    l="The N-well band under the contact follows the square outline "
      "2 µm inside the edge, and has sharp corners of its own. The "
      "corner section is a cylinder of 1 µm radius, as for {NC0}, so an "
      "edge-limited corner would read pessimistic; a bottom-limited well "
      "is indifferent to it.")
E["DM1_6"] = dict(
    p="A deep N-well with a Metal1 plate of 6 µm: the deep-well "
      "counterpart of the plate that gains most among Metal1 plates on "
      "an N-well.",
    w="If any plate could raise a deep N-well's breakdown, this one "
      "should. The comparison with {NM1_6} is the clearest single test "
      "of whether the edge or the bottom limits.",
    c=[("DT20", "a Metal1 plate of 6 µm in place of none"),
       ("NM1_6", "a deep N-well in place of an N-well"),
       ("DAo1M1_6", "no NAT in place of NAT over the edge")],
    m="",
    r="Equal to {DT20} while {NM1_6} is above {NT20}: plates work on "
      "edges, and this well does not fail at its edge.",
    l="None beyond those of the group.")
E["DAo1"] = dict(
    p="A deep N-well with NAT over its edge, so that no P-well can lie "
      "beside the junction.",
    w="NAT starts 1 µm inside the well edge and covers the whole "
      "termination zone, which the rules allow on a deep N-well. If the "
      "edge limited a deep N-well because of nearby P-well, removing "
      "the P-well would raise the breakdown voltage.",
    c=[("DT20", "NAT over the edge in place of none"),
       ("DAo1M1_6", "no plate in place of a Metal1 plate of 6 µm"),
       ("NA0p6", "NAT overlapping the edge in place of 0.6 µm away")],
    m="",
    r="Equal to {DT20}: the bottom limits, with or without P-well at "
      "the edge. Much higher: P-well beside the edge was the limit, and "
      "NAT removes it.",
    l="Whether the foundry accepts NAT here with no transistor is not "
      "known, although the rule check passes it.")
E["DAo1M1_6"] = dict(
    p="A deep N-well with NAT over its edge and a Metal1 plate of 6 µm: "
      "every edge remedy the die has, on one well.",
    w="NAT removes any P-well and the plate relieves the curved edge. "
      "If the edge were what limits a deep N-well, this structure would "
      "hold the most of the group.",
    c=[("DAo1", "a Metal1 plate of 6 µm in place of none"),
       ("DM1_6", "NAT over the edge in place of none"),
       ("NAM1_6", "a deep N-well in place of an N-well")],
    m="",
    r="Equal to {DT20}: nothing at the edge matters, and the deep "
      "N-well's limit is its bottom. This is the decisive member of the "
      "group.",
    l="None beyond those of the group.")
E["DT20b"] = dict(
    p="Gives the spread across the die for a deep N-well: a second "
      "copy of {DT20}.",
    w="The drawing is identical to {DT20}. A breakdown at the flat "
      "bottom depends on implant doses and not on mask edges, so the "
      "two copies should agree more closely than the plain N-well "
      "pair.",
    c=[("DT20", "nothing but the position on the die: the two stand at "
                "opposite ends"),
       ("NT20b", "the same check on an N-well")],
    m="Swept with the same settings as {DT20} and in the same session.",
    r="A spread smaller than that of {NT20} and {NT20b} supports a "
      "breakdown that does not depend on the edge.",
    l="One pair, as for the plain well.")

# ---- capacitance wells and open reference ---------------------------------
E["CVN"] = dict(
    p="The large N-well: 200 µm across, for the doping profile under "
      "an N-well.",
    w="Its flat bottom supplies more than nine tenths of its "
      "capacitance, so the reading is mostly that of a flat junction. "
      "Sweeping the reverse voltage moves the edge of the depletion "
      "region downwards and reads the doping there.",
    c=[("CVN2", "200 µm across in place of 100 µm"),
       ("CVD", "an N-well in place of a deep N-well"),
       ("OPEN", "a well under the lead in place of none")],
    m="The bias stays below 80 % of the breakdown voltage that {P1} "
      "gives for this well on another die.",
    r="Its capacitance with that of {CVN2} gives the capacitance per "
      "area and per length of edge, and from the first the doping "
      "against depth.",
    l="It has no fill block, so dummy fill lies inside the well. Its "
      "P+ ring is 6 µm away, and if P-well surrounds it the sweep ends "
      "near 10 V. Even then, the capacitance below 10 V differs between "
      "a well with a deep P layer under it and one without.")
E["CVN2"] = dict(
    p="The small N-well: 100 µm across, to separate the capacitance of "
      "the edge from that of the bottom.",
    w="Its area is a quarter of that of {CVN} and its perimeter about "
      "half. The edge therefore supplies a larger share of its "
      "capacitance. Two wells of different size give two equations "
      "for the two unknowns.",
    c=[("CVN", "100 µm across in place of 200 µm"),
       ("CVNA", "no NAT and a ring at 6 µm in place of NAT and a ring "
                "at 20 µm"),
       ("CVNA2", "no NAT in place of NAT, at half the size")],
    m="As for {CVN}.",
    r="With {CVN}, the capacitance per area and per length of edge.",
    l="Neither it nor {CVN} has a fill block, so the pair differs in "
      "size alone. Both receive dummy fill inside the well.")
E["CVNA"] = dict(
    p="An N-well whose capacitance can be followed beyond the plain "
      "well's breakdown. That sweep shows whether a deep P layer lies "
      "under N-wells.",
    w="NAT from 0.6 µm and a P+ ring 20 µm away let the well hold more "
      "voltage if NAT clears its edge. The depletion region under the "
      "bottom then reaches several micrometres down. If it meets a "
      "heavily doped P layer there, it stops widening and the "
      "capacitance stops falling.",
    c=[("CVNA2", "100 µm across in place of 200 µm"),
       ("CVN2", "NAT and a ring at 20 µm in place of neither"),
       ("NA0p6", "a well 100 µm across in place of 30 µm")],
    m="The bias follows the well's own breakdown voltage from {P1}, "
      "and may need the external bias source of 60 V.",
    r="Capacitance that flattens beyond about 15 V: a deep P layer "
      "under N-wells, assumption D. Capacitance that keeps falling: "
      "none within the depth reached.",
    l="It works only if NAT clears the edge. Its ring distance differs "
      "from that of {CVN2}, so the two do not differ in NAT alone. Its "
      "edge supplies a large share of its capacitance, which {CVNA2} "
      "removes.")
E["CVNA2"] = dict(
    p="The large N-well with NAT: 200 µm across, to separate the bottom "
      "of {CVNA} from its edge at voltages the plain wells cannot reach.",
    w="A deep P layer under the well shows in the capacitance of the "
      "flat bottom. The edge of a well under NAT faces different silicon "
      "from its bottom and its capacitance falls at a different rate. "
      "With two sizes the edge's share is solved for and removed, as "
      "{CVN} and {CVN2} do for a plain well.",
    c=[("CVNA", "200 µm across in place of 100 µm, and a ring at 11 µm "
                "in place of 20 µm"),
       ("CVN", "NAT round the well in place of none")],
    m="As for {CVNA}.",
    r="With {CVNA}, the capacitance per area of an N-well's bottom up "
      "to the breakdown voltage of a well under NAT.",
    l="Its P+ ring is 11 µm away against 20 µm for {CVNA}, so the two "
      "edges are not identical. If the ring limits it first, its sweep "
      "ends below that of {CVNA}.")
E["CVD"] = dict(
    p="The large deep N-well: 200 µm across, for the doping under a "
      "deep N-well.",
    w="The published deep N-well capacitance falls unusually slowly "
      "with voltage. That is what a heavily doped layer close under "
      "the well would cause, because the depletion region has little "
      "room to widen. This well measures that curve on silicon.",
    c=[("CVN", "a deep N-well in place of an N-well")],
    m="The bias stays below 80 % of this well's breakdown voltage, "
      "which is expected near 30 V.",
    r="A capacitance that falls as slowly as the published model's "
      "confirms a heavily doped layer under the deep N-well.",
    l="It is the only large deep N-well, so its edge capacitance cannot "
      "be separated from that of its bottom. By the published model the "
      "edge is about 6 % of the total, which is the size of that "
      "uncertainty. It has no fill block, and the N-well band under its "
      "contact adds capacitance at the perimeter.")
E["OPEN"] = dict(
    p="The part of every reading that is not the junction: a pad and "
      "a lead with no well.",
    w="A Metal5 lead and a pad stand over bare substrate on a standard "
      "site. Whatever capacitance and leakage they show, every other "
      "structure shows too, and it is subtracted.",
    c=[("NT20", "no well under the lead in place of one"),
       ("CVN2", "no well in place of a large one")],
    m="Swept to the full 150 V on every die, which no junction "
      "structure may reach.",
    r="Its current at each voltage is the floor below which no "
      "structure's current means anything.",
    l="Its lead has the standard length, and those of the large wells "
      "differ by tens of micrometres. Dummy Metal4 lies under its pad "
      "as under every pad.")
