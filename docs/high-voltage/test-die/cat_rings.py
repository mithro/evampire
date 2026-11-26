"""Catalogue texts: floating rings and gated diodes.

catalogue.py joins these modules; its docstring describes the fields.

SPDX-License-Identifier: Apache-2.0
"""

E = {}

# ---- floating rings --------------------------------------------------------
E["NR1_1p4"] = dict(
    p="One ring at the smallest gap the rules allow, 1.4 µm.",
    w="The depletion region crosses 1.4 µm within the first volts. The "
      "ring then follows the well so closely that the step between them "
      "is small. Its outer edge carries nearly the full voltage and is "
      "little better off than the well's own edge was.",
    c=[("NT20", "one ring at 1.4 µm in place of none"),
       ("NR1_2", "a gap of 1.4 µm in place of 2 µm")],
    m="",
    r="Only a little above {NT20}: a ring this close moves the weak "
      "point outwards without relieving it.",
    l="The gap is at the rule's minimum, so its width is the most "
      "sensitive of the series to how the two well edges print.")
E["NR1_2"] = dict(
    p="One ring at a gap of 2 µm: the reference for the ring series.",
    w="The well's depletion region reaches the ring after a few volts. "
      "From then on the ring rises by most of every further volt on the "
      "well. The well's edge sees only the difference, and the ring's "
      "outer edge becomes the place that breaks down.",
    c=[("NR1_1p4", "a gap of 2 µm in place of 1.4 µm"),
       ("NR1_3", "a gap of 2 µm in place of 3 µm"),
       ("NR1S2", "no contact on the ring in place of one")],
    m="",
    r="Well above {NT20}: one ring is a real termination.",
    l="The ring's potential is not measured here; {NR1S2} does that.")
E["NR1_3"] = dict(
    p="One ring at a gap of 3 µm.",
    w="The ring picks up later, so the step between well and ring is "
      "larger. The well's edge holds more of the voltage and the ring's "
      "outer edge less. The best gap is the one that makes both edges "
      "fail at the same voltage.",
    c=[("NR1_2", "a gap of 3 µm in place of 2 µm"),
       ("NR1S3", "no contact on the ring in place of one")],
    m="",
    r="Above {NR1_2}: the best gap is 3 µm or more. Below: it lies "
      "between 2 µm and 3 µm.",
    l="No single-ring structure has a wider gap, so a value still "
      "rising has no end point.")
E["NR3_1p5"] = dict(
    p="Three rings with gaps of 1.5 µm, 2 µm and 2.5 µm.",
    w="Each ring picks up from the one inside it and passes the rest of "
      "the voltage outwards. The gaps widen outwards because each "
      "successive ring sits at a lower potential and its depletion "
      "region needs more room to reach the next.",
    c=[("NR1_1p4", "three rings in place of one, from a similar first "
                   "gap"),
       ("NR3_2", "gaps from 1.5 µm in place of from 2 µm")],
    m="",
    r="Above the single rings: more rings share the voltage further.",
    l="Its P+ ring is 30 µm from the well, further than that of "
      "{NT20}.")
E["NR3_2"] = dict(
    p="Three rings with gaps of 2 µm, 2.5 µm and 3 µm: the reference "
      "for the multi-ring structures.",
    w="The first gap is that of {NR1_2}, so ring 1 behaves as there. "
      "Rings 2 and 3 repeat its action at lower potentials, and the "
      "voltage falls in four steps between the well and the substrate.",
    c=[("NR1_2", "three rings in place of one"),
       ("NR3_1p5", "gaps from 2 µm in place of from 1.5 µm"),
       ("NR3W1", "rings 2 µm wide in place of 1 µm"),
       ("NR3W3", "rings 2 µm wide in place of 3 µm"),
       ("NR3M1", "no plate in place of a Metal1 plate")],
    m="Swept again at 85 °C.",
    r="Above {NR1_2}: rings 2 and 3 take a share.",
    l="As for {NR3_1p5}.")
E["NR3W1"] = dict(
    p="Three rings only 1 µm wide: tests whether a ring needs width.",
    w="A ring is depleted from both its edges. At 1 µm wide, close to "
      "the narrowest well the process prints, the two depletion regions "
      "may meet. The ring then no longer has a neutral core to hold one "
      "potential, and acts as lightly doped silicon instead.",
    c=[("NR3_2", "rings 1 µm wide in place of 2 µm")],
    m="",
    r="Equal to {NR3_2}: narrow rings work and save area. Lower: a ring "
      "needs a neutral core.",
    l="A ring this narrow may print narrower still, or not join up "
      "round the corners.")
E["NR3W3"] = dict(
    p="Three rings 3 µm wide: the wide end of the ring-width check.",
    w="A wide ring keeps a neutral core at any voltage, and is one "
      "potential all round. The price is length: each ring adds 3 µm "
      "over which no voltage falls.",
    c=[("NR3_2", "rings 3 µm wide in place of 2 µm"),
       ("NR3W1", "rings 3 µm wide in place of 1 µm")],
    m="",
    r="Equal to {NR3_2}: 2 µm is wide enough.",
    l="Its P+ ring is 35 µm from the well, further than that of "
      "{NR3_2}.")
E["NR5_1p4"] = dict(
    p="Five rings from the smallest gap: 1.4 µm, 1.7 µm, 2 µm, 2.4 µm "
      "and 2.8 µm.",
    w="Five small steps in place of three larger ones. Each edge holds "
      "less, so the structure tolerates gaps that are not ideal, at the "
      "cost of 20 µm of termination.",
    c=[("NR3_1p5", "five rings in place of three, from a similar first "
                   "gap"),
       ("NR5_2", "gaps from 1.4 µm in place of from 2 µm")],
    m="",
    r="Above the three-ring structures: the fourth and fifth rings "
      "still take voltage.",
    l="Its length makes it the structure most exposed to charge on the "
      "oxide between rings. Its P+ ring is 36 µm from the well, 15 µm "
      "beyond the last ring.")
E["NR5_2"] = dict(
    p="Five rings from a gap of 2 µm: the longest termination on the "
      "die, 25 µm of rings and gaps.",
    w="The gaps widen from 2 µm to 4 µm. The outer rings sit at low "
      "potentials, where a gap of 4 µm may be too wide for the "
      "depletion region to cross. A ring that is never reached takes no "
      "part.",
    c=[("NR5_1p4", "gaps from 2 µm in place of from 1.4 µm"),
       ("NR3_2", "five rings in place of three")],
    m="",
    r="Equal to {NR3_2}: the outer rings are never reached.",
    l="Its P+ ring is 40 µm from the well, the furthest on the die.")
E["NR3M1"] = dict(
    p="Three rings with a Metal1 plate over the first gap: rings and a "
      "plate combined.",
    w="The plate, joined to the well, extends 3 µm and covers the 2 µm "
      "gap and half of ring 1. It holds the surface of the first gap at "
      "a known potential, so charge on the oxide there cannot change "
      "when ring 1 picks up.",
    c=[("NR3_2", "a Metal1 plate of 3 µm in place of none"),
       ("NM1_3", "three rings under and beyond the plate in place of "
                 "none")],
    m="Three sweeps matter here: less walk-out than {NR3_2} is the "
      "plate's benefit.",
    r="Equal to {NR3_2} with less walk-out: the plate stabilises the "
      "first gap without changing the breakdown.",
    l="Only the first gap is covered, so charge over the outer gaps "
      "still acts.")
E["NR1S2"] = dict(
    p="Measures the potential of a floating ring directly: {NR1_2} with "
      "a contact on the ring and a second pad.",
    w="A small N+ contact on ring 1 leads on Metal2 to its own pad. A "
      "meter that draws no current reads the ring's potential while the "
      "well is swept. Held at 0 V instead, the ring is a second well "
      "2 µm from the first, and the current between them is "
      "punch-through.",
    c=[("NR1_2", "a contact and lead on the ring in place of none"),
       ("NR1S3", "a gap of 2 µm in place of 3 µm")],
    m="The ring pad needs a meter whose input current is below 100 fA, "
      "and seconds of settling at each step. The ring is grounded "
      "through its pad before each sweep, and only the sweep upwards is "
      "read.",
    r="The well voltage at which the ring starts to follow, and the "
      "step it then keeps, are compared with the predicted curve.",
    l="The pad, its lead and the meter's cable load the ring with "
      "capacitance and leakage that a floating ring does not have.")
E["NR1S3"] = dict(
    p="Measures the potential of a ring at a gap of 3 µm.",
    w="As in {NR1S2}, with the ring further out. The ring should start "
      "to follow at a higher well voltage and keep a larger step. With "
      "the ring at 0 V, it gives the punch-through voltage of two wells "
      "3 µm apart.",
    c=[("NR1S2", "a gap of 3 µm in place of 2 µm"),
       ("NR1S5", "a gap of 3 µm in place of 5 µm"),
       ("NR1_3", "a contact and lead on the ring in place of none")],
    m="As for {NR1S2}.",
    r="A later onset and a larger step than {NR1S2}, in the ratio the "
      "simulation gives.",
    l="As for {NR1S2}.")
E["NR4S"] = dict(
    p="Measures the potential of ring 1 when three more rings stand "
      "outside it.",
    w="Four rings at gaps of 1.6 µm, 2 µm, 2.5 µm and 3 µm, with the "
      "contact on the innermost. The outer rings take up voltage that "
      "ring 1 would otherwise hold at its outer edge, so ring 1 can "
      "follow the well to a higher voltage before anything breaks down.",
    c=[("NR1S2", "four rings in place of one"),
       ("NR3_2", "four rings with a contact in place of three without")],
    m="As for {NR1S2}.",
    r="The ring curve runs to a higher well voltage than in {NR1S2}.",
    l="Only ring 1 has a pad, so how the voltage divides among the "
      "outer rings is not seen.")

E["NR1S5"] = dict(
    p="Gives the spacing between two wells at different voltages: a "
      "contacted ring 5 µm from the well.",
    w="With its pad at 0 V the ring is a neighbouring well at the "
      "substrate's potential. The well's depletion region crosses the "
      "5 µm of substrate at a voltage that rises roughly with the "
      "square of the gap, and current then flows from well to ring.",
    c=[("NR1S3", "a gap of 5 µm in place of 3 µm"),
       ("NR1S8", "a gap of 5 µm in place of 8 µm"),
       ("NT5", "an N-well ring at 5 µm in place of a P+ ring")],
    m="{P5} is the main procedure here: the ring pad is held at 0 V and "
      "its current recorded. {P3} is run as well, because the floating "
      "potential costs nothing to record and is simulated.",
    r="The well voltage at which ring current starts is what two wells "
      "5 µm apart can differ by.",
    l="Under assumption A the P-well between well and ring fails first, "
      "and the structure shows only that.")
E["NR1S8"] = dict(
    p="The same measurement at a gap of 8 µm, wider than the depletion "
      "region of a plain well at its breakdown voltage.",
    w="If the well breaks down before its depletion region has crossed "
      "8 µm, no current reaches the ring, and the substrate current "
      "rises instead. The gap is then wide enough for any voltage the "
      "well itself can hold.",
    c=[("NR1S5", "a gap of 8 µm in place of 5 µm"),
       ("NR1S12", "a gap of 8 µm in place of 12 µm"),
       ("NT10", "an N-well ring at 8 µm in place of a P+ ring at 10 µm")],
    m="As for {NR1S5}. Which pad the current leaves by, ring or "
      "substrate, is the result.",
    r="Substrate current first: 8 µm isolates two wells up to the "
      "breakdown voltage. Ring current first: it does not.",
    l="As for {NR1S5}.")
E["NR1S12"] = dict(
    p="The widest gap, 12 µm: the spacing expected to be safe at any "
      "voltage a well on this die holds.",
    w="Twelve micrometres is more than twice the flat depletion width "
      "at the plain well's predicted breakdown. The ring should stay "
      "unreached, and the well should break down as {NT20} does.",
    c=[("NR1S8", "a gap of 12 µm in place of 8 µm"),
       ("NT20", "an N-well ring at 12 µm in place of nothing")],
    m="As for {NR1S5}.",
    r="A breakdown voltage equal to {NT20}, with no ring current: a "
      "neighbouring well 12 µm away changes nothing.",
    l="If ring current still flows here, the die has no wider gap to "
      "show where it stops.")

E["NR1_2L"] = dict(
    p="Shows whether the Metal5 lead changes a well that has a floating "
      "ring.",
    w="The lead crosses the gap and the ring at the well's voltage. A "
      "ring takes its potential from the silicon all round it, so a "
      "conductor above one part of the gap could shift when that part "
      "of the ring is reached. Here the lead covers the whole east side "
      "in place of 6 µm of it.",
    c=[("NR1_2", "a lead 30 µm wide in place of 6 µm"),
       ("NT20L", "one floating ring under the lead in place of none")],
    m="",
    r="Equal to {NR1_2}: the lead does not disturb a ring. Different: "
      "every ring structure carries that effect over 6 µm.",
    l="The ring is one conductor, so an effect on its east side shows "
      "all round and cannot be located. The simulation has no lead, so "
      "its prediction is that of {NR1_2}.")

# ---- gated diodes ----------------------------------------------------------
E["NGP4"] = dict(
    p="A polysilicon plate on its own pad: the most sensitive probe of "
      "the surface beside a plain N-well.",
    w="The plate lies on 0.32 µm of trench oxide, from 1 µm inside the "
      "well edge to 4 µm outside it. Over oxide that thin, bare "
      "substrate inverts at a few volts. P-well at 4 × 10\\ :sup:`17` "
      "cm\\ :sup:`-3` inverts at about 31 V with the well at 0 V and "
      "about 58 V with it at 2 V, by the threshold equation of the "
      "method.",
    c=[("NP4", "the plate on its own pad in place of joined to the "
               "well"),
       ("NGM1", "polysilicon over 0.32 µm in place of Metal1 over "
                "1.18 µm")],
    m="The plate is swept to +60 V with the well at 0 V and at 2 V, so "
      "that a threshold over P-well falls inside the sweep. The oxide "
      "under the plate sees the whole voltage between plate and well, "
      "which stays within 60 V: 1.8 MV/cm across 0.33 µm.",
    r="A threshold of a few volts: bare substrate beside the well. A "
      "threshold near 30 V with the well at 0 V: P-well.",
    l="The threshold over P-well lies close to the 60 V limit once the "
      "well is at 2 V, so the second point may be out of reach.")
E["NGM1"] = dict(
    p="A Metal1 plate on its own pad beside a plain N-well: {NM1_6} "
      "with the plate under separate control.",
    w="The plate lies over 1.18 µm of oxide. With the plate at the "
      "well's voltage it is {NM1_6}. With it at 0 V it holds the surface "
      "at the substrate's potential, the depletion region cannot spread "
      "along the surface, and the edge breaks down earlier.",
    c=[("NM1_6", "the plate on its own pad in place of joined to the "
                 "well"),
       ("NAGM1", "no NAT in place of NAT under the plate"),
       ("NGP4", "Metal1 over 1.18 µm in place of polysilicon over "
                "0.32 µm")],
    m="A plate at 0 V lets the well reach 80 V, which covers the "
      "breakdown voltage predicted for that case.",
    r="A threshold near the published Metal1 field threshold: bare "
      "substrate. No threshold within the range: a surface as heavily "
      "doped as P-well.",
    l="Over P-well the threshold is above 100 V, outside the plate's "
      "range. The first part then gives the flat-band voltage only, and "
      "the doping is bounded from below but not measured.")
E["NAGM1"] = dict(
    p="A Metal1 plate on its own pad over NAT: reads directly whether "
      "P-well lies under the NAT layer.",
    w="The plate covers the 0.6 µm strip and 5.4 µm of NAT. The plate "
      "voltage at which the surface under it inverts depends on the "
      "doping there. Bare substrate under NAT inverts at a far lower "
      "voltage than P-well would.",
    c=[("NGM1", "NAT under the plate in place of none"),
       ("NAM1_6", "the plate on its own pad in place of joined to the "
                  "well")],
    m="As for {NGM1}.",
    r="A lower threshold than {NGM1}: NAT removes P-well that is "
      "present beside a plain well. Equal thresholds: the two surfaces "
      "are the same silicon.",
    l="The plate also covers the strip beside the well, whose doping "
      "may differ from that under NAT; the reading mixes the two.")
E["DGM1"] = dict(
    p="A Metal1 plate on its own pad beside a deep N-well: reads the "
      "surface there, and checks that the plate does not change the "
      "breakdown.",
    w="If the deep N-well breaks down at its bottom, the plate's "
      "voltage alters the surface without altering the breakdown "
      "voltage. The threshold still reports the doping beside the well, "
      "where a generated P-well would start 1.5 µm out.",
    c=[("NGM1", "a deep N-well in place of an N-well"),
       ("DM1_6", "the plate on its own pad in place of joined to the "
                 "well")],
    m="As for {NGM1}.",
    r="A breakdown voltage that does not move with the plate voltage: "
      "the bottom of the well limits. One that moves: the edge does.",
    l="The N-well band under the contact ring lies under the inner part "
      "of the plate, so the surface there is not deep N-well.")
