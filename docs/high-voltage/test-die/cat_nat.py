"""Catalogue texts: the NAT layer, rings under NAT and field plates.

catalogue.py joins these modules; its docstring describes the fields.

SPDX-License-Identifier: Apache-2.0
"""

E = {}

# ---- NAT -------------------------------------------------------------------
E["NA0p6"] = dict(
    p="The main test of the NAT layer: NAT as close to an N-well as the "
      "rules allow.",
    w="NAT covers the termination zone from 0.6 µm outwards. If it "
      "blocks the P-well, bare substrate lies beside the well except in "
      "a strip 0.6 µm wide. That strip is at the foundry's minimum P-well "
      "width, so the generated mask may leave it out.",
    c=[("NT20", "NAT over the termination zone in place of none"),
       ("NAR1_2", "no ring in place of one floating ring under NAT"),
       ("NA0p6b", "nothing: a second copy")],
    m="Swept again at 85 °C.",
    r="Much higher than {NT20} while {NT20} is near 14 V: NAT clears the "
      "edge (assumption An), and the plates and rings under NAT show what "
      "can be built on it. Equal to {NT20} at a low value: either the "
      "strip is filled or NAT blocks nothing (A). Equal to {NT20} at a "
      "high value: no P-well is generated anywhere (B), so NAT has "
      "nothing to block, which the simulation gives as well.",
    l="A strip always remains, so the structure never has NAT against "
      "the junction.")
E["NA0p6T10"] = dict(
    p="Repeats the ring-distance check under NAT with the P+ ring at "
      "10 µm.",
    w="NAT ends 0.5 µm short of the P+ ring, so here it is 8.9 µm wide. "
      "If NAT clears the P-well, the depletion region spreads through "
      "that width and the P+ ring is the first heavily doped region it "
      "can meet.",
    c=[("NA0p6", "the ring is at 10 µm in place of 20 µm"),
       ("NT5", "NAT and a ring at 10 µm in place of no NAT and a ring "
               "at 5 µm")],
    m="",
    r="Equal to {NA0p6}: a NAT region 9 µm wide is enough.",
    l="It tests the ring distance only if NAT clears the edge. "
      "Otherwise P-well limits it as it limits {NT20}.")
E["NA0p6C0"] = dict(
    p="Measures the cost of a square corner when NAT, not P-well, lies "
      "beside the well.",
    w="The well has four 90° vertices and the NAT outline follows them "
      "at 0.6 µm. If NAT clears the edge, the vertices carry the highest "
      "field, as in {NC0}.",
    c=[("NA0p6", "four 90° vertices in place of eight of 135°"),
       ("NC0", "NAT over the termination zone in place of none")],
    m="",
    r="Below {NA0p6} by the same amount as {NC0} is below {NT20}: the "
      "silicon under NAT behaves as bare substrate does.",
    l="The corner section is a cylinder of 1 µm radius, as for {NC0}, "
      "so the corner prediction is probably pessimistic: the measured "
      "value may be higher.")
E["NAM1_3"] = dict(
    p="The shortest Metal1 plate over NAT: 3 µm beyond the edge.",
    w="The plate crosses the 0.6 µm strip and 2.4 µm of NAT. It widens "
      "the depletion region under itself, but ends inside the width that "
      "the region would reach unaided, so it moves the field peak only "
      "part of the way.",
    c=[("NA0p6", "a Metal1 plate of 3 µm in place of none"),
       ("NAM1_6", "a plate of 3 µm in place of 6 µm"),
       ("NM1_3", "NAT under the plate in place of none")],
    m="",
    r="Above {NA0p6}: a plate works on the silicon under NAT.",
    l="If the strip beside the well holds P-well, the plate covers it "
      "and cannot help, as under assumption A.")
E["NAM1_6"] = dict(
    p="The Metal1 plate of middle length over NAT. If NAT is what "
      "clears an N-well edge, this is the termination a circuit would "
      "use.",
    w="The plate ends 6 µm out, a little beyond the unaided depletion "
      "width. The surface under it is depleted to its end, the field at "
      "the well's curved edge is relieved, and the peak moves to the "
      "plate's end, where 1.18 µm of oxide keeps it moderate.",
    c=[("NAM1_3", "a plate of 6 µm in place of 3 µm"),
       ("NAM1_10", "a plate of 6 µm in place of 10 µm"),
       ("NM1_6", "NAT under the plate in place of none")],
    m="",
    r="Equal to {NM1_6} under assumption B: NAT changes nothing that a "
      "plate cares about.",
    l="Polysilicon may not lie under NAT, so the thinner-oxide plate "
      "that gains most elsewhere cannot be combined with it.")
E["NAM1_10"] = dict(
    p="The longest Metal1 plate over NAT: 10 µm, to see whether length "
      "beyond 6 µm adds anything.",
    w="Once the plate reaches past the depletion region it has nothing "
      "more to deplete. The extra length only moves the plate's end "
      "towards the P+ ring, which shortens the silicon left to hold the "
      "voltage.",
    c=[("NAM1_6", "a plate of 10 µm in place of 6 µm"),
       ("NM1_10", "NAT under the plate in place of none")],
    m="",
    r="Equal to {NAM1_6}: 6 µm is long enough.",
    l="The plate's end is 10 µm from the P+ ring. A lower value than "
      "{NAM1_6} could come from that distance and not from the plate.")
E["NAM2_12"] = dict(
    p="A Metal2 plate over NAT, 12 µm long: the thick-oxide alternative "
      "to Metal1.",
    w="Metal2 lies over 2.33 µm of oxide, so it draws the depletion "
      "region out more weakly than Metal1 and leaves a lower field at "
      "its own end. It needs more length for the same effect.",
    c=[("NAM1_6", "Metal2 to 12 µm in place of Metal1 to 6 µm"),
       ("NM2_12", "NAT under the plate in place of none")],
    m="",
    r="Above {NAM1_10}: thicker oxide is the better trade under NAT. "
      "Below: Metal1 is.",
    l="It is the only Metal2 plate under NAT, so length and layer "
      "cannot be separated within this group.")
E["NA0p6b"] = dict(
    p="Gives the spread across the die for a well under NAT: a second "
      "copy of {NA0p6}.",
    w="The drawing is identical to {NA0p6}. A well whose edge is cleared "
      "by NAT depends on the alignment of the NAT mask to the well, "
      "which a plain well does not, so its spread may be larger.",
    c=[("NA0p6", "nothing but the position on the die"),
       ("NT20b", "the same check on a plain well")],
    m="Swept with the same settings as {NA0p6} and in the same session.",
    r="A spread larger than that of the plain pair points to the "
      "0.6 µm strip, whose width is set by two masks.",
    l="One pair, as for the plain well.")

# ---- rings under NAT -------------------------------------------------------
# NAT keeps 0.6 um from the well and from each side of every ring, so the
# layer is cut into strips. Under A those strips hold P-well and the
# structures are limited by it; under An and B they are bare substrate.
E["NAR1_2"] = dict(
    p="One floating ring under NAT: what a ring gains where no P-well "
      "lies between it and the well.",
    w="The ring is 2 µm wide at a gap of 2 µm. NAT is cut into strips "
      "that keep 0.6 µm from the well and from each side of the ring, as "
      "rule NAT.3 requires. If NAT clears the P-well and the strips stay "
      "empty, the ring sits in bare substrate and acts as in {NR1_2} "
      "under assumption B.",
    c=[("NR1_2", "NAT round the ring in place of none"),
       ("NA0p6", "one floating ring in place of none"),
       ("NAR3_2", "one ring in place of three")],
    m="",
    r="Above {NA0p6} by the predicted ratio: a ring works under NAT, "
      "and the die's route to the working voltage can use rings. Equal to "
      "{NA0p6} and {NT20} at a low value: P-well fills the strips.",
    l="Three uncovered strips lie beside the ring and the well, each "
      "0.6 µm wide. A narrow strip may hold P-well even where NAT clears "
      "the wide parts, and the structure cannot tell which strip failed.")
E["NAR3_2"] = dict(
    p="Three floating rings under NAT, at gaps of 2 µm, 2.5 µm and 3 µm: "
      "the multi-ring termination where no P-well lies between the rings.",
    w="The rings repeat those of {NR3_2}, with the P+ ring 30 µm out. NAT "
      "covers the gaps and the zone beyond the last ring, in strips that "
      "keep 0.6 µm from every ring. With the strips empty, each ring "
      "picks up from the one inside it in bare substrate.",
    c=[("NR3_2", "NAT round the rings in place of none"),
       ("NAR1_2", "three rings in place of one")],
    m="",
    r="Above {NAR1_2}: rings 2 and 3 take a share under NAT as they do "
      "in bare substrate.",
    l="Seven uncovered strips lie beside the rings and the well. The "
      "multi-ring simulations take hours each, so this prediction may "
      "come late or not converge.")
E["NAR1S3"] = dict(
    p="A contacted ring under NAT 3 µm from the well: the spacing between "
      "two wells where no P-well lies between them.",
    w="It is {NR1S3} with NAT over the gap and the termination zone, cut "
      "0.6 µm clear of the ring and the well. If NAT clears the P-well, "
      "the depletion region crosses the gap in bare substrate, and with "
      "the ring pad at 0 V the ring is a neighbouring well.",
    c=[("NR1S3", "NAT over the gap in place of none"),
       ("NAR1S8", "a gap of 3 µm in place of 8 µm"),
       ("NAR1_2", "a contact on the ring, at 3 µm in place of 2 µm")],
    m="As for {NR1S3}.",
    r="Under An the punch-through and the ring's rise follow {NR1S3} "
      "under B. Under A both are limited by P-well in the strips, as for "
      "{NR1S3}.",
    l="As for {NR1S2}. The strips beside the ring are only 0.6 µm wide, "
      "so a P-well that fills them would cut the gap short.")
E["NAR1S8"] = dict(
    p="A contacted ring under NAT 8 µm from the well: whether that spacing "
      "isolates two wells where NAT clears the P-well.",
    w="It is {NR1S8} with NAT over the gap. If the well breaks down before "
      "its depletion region has crossed 8 µm of bare substrate, no "
      "current reaches the ring, and the substrate current rises "
      "instead.",
    c=[("NR1S8", "NAT over the gap in place of none"),
       ("NAR1S3", "a gap of 8 µm in place of 3 µm")],
    m="As for {NR1S5}. Which pad the current leaves by, ring or "
      "substrate, is the result.",
    r="Substrate current first: 8 µm isolates two wells under NAT up to "
      "the breakdown voltage. Ring current first: it does not.",
    l="As for {NAR1S3}. No contacted ring under NAT lies between 3 µm "
      "and 8 µm, so a spacing that fails at 3 µm and holds at 8 µm is "
      "bracketed, not found.")

# ---- field plates ----------------------------------------------------------
E["NP1"] = dict(
    p="The shortest polysilicon plate: 1 µm beyond the well edge.",
    w="Polysilicon lies on the trench oxide, 0.32 µm from the silicon, "
      "so it controls the surface almost as a gate would. One micrometre "
      "is much less than the depletion width, so the plate relieves only "
      "the innermost part of the curved edge.",
    c=[("NT20", "a polysilicon plate of 1 µm in place of none"),
       ("NP2", "a plate of 1 µm in place of 2 µm")],
    m="",
    r="Above {NT20}: even a short plate over thin oxide helps.",
    l="The plate carries the well's voltage over oxide thinner than any "
      "the foundry rates for it; the manual's advisory limit is 6 V.")
E["NP2"] = dict(
    p="A polysilicon plate of 2 µm, the middle of the polysilicon "
      "series.",
    w="The plate holds the first 2 µm of surface at nearly the well's "
      "potential. The voltage then has to fall in the silicon beyond "
      "the plate's end, where the field peak now sits.",
    c=[("NP1", "a plate of 2 µm in place of 1 µm"),
       ("NP4", "a plate of 2 µm in place of 4 µm"),
       ("NPM12", "polysilicon alone in place of three stepped layers")],
    m="",
    r="Between {NP1} and {NP4}: the gain grows with length over this "
      "range.",
    l="As for {NP1}.")
E["NP4"] = dict(
    p="The longest polysilicon plate: 4 µm, most of the depletion width.",
    w="The plate depletes nearly the whole width that the region would "
      "reach unaided. At its end, the silicon is near the substrate's "
      "potential while the plate is at the well's, so almost the full "
      "voltage stands across the oxide, 0.31 µm thick by its extraction "
      "capacitance: about 2.9 MV/cm at 90 V.",
    c=[("NP2", "a plate of 4 µm in place of 2 µm"),
       ("NM1_6", "polysilicon over 0.32 µm in place of Metal1 over "
                 "1.18 µm"),
       ("NGP4", "the plate joined to the well in place of on its own "
                "pad")],
    m="A second sweep straight after the first shows whether the oxide "
      "survived.",
    r="The highest value of the polysilicon series, if the oxide holds.",
    l="The oxide may fail before the silicon does. A sweep that cannot "
      "be repeated is an oxide failure, not a junction breakdown.")
E["NM1_3"] = dict(
    p="The shortest Metal1 plate: 3 µm beyond the well edge.",
    w="Metal1 lies over 1.18 µm of oxide. Its hold on the surface is "
      "about a quarter of polysilicon's, so at 3 µm it widens the "
      "depletion region only a little beyond the curved edge.",
    c=[("NT20", "a Metal1 plate of 3 µm in place of none"),
       ("NM1_6", "a plate of 3 µm in place of 6 µm"),
       ("NP2", "Metal1 in place of polysilicon at a similar length")],
    m="",
    r="Above {NT20}: Metal1 alone is a usable plate.",
    l="None beyond those of the group.")
E["NM1_6"] = dict(
    p="The Metal1 plate of middle length, 6 µm: the plate that every "
      "other Metal1 structure on the die repeats.",
    w="The plate, at the well's voltage over 1.18 µm of oxide, depletes "
      "the surface out to its end, a little beyond the unaided "
      "depletion width. The peak field moves from the well's curved "
      "edge to under the plate's end.",
    c=[("NM1_3", "a plate of 6 µm in place of 3 µm"),
       ("NM1_10", "a plate of 6 µm in place of 10 µm"),
       ("NGM1", "the plate joined to the well in place of on its own "
                "pad"),
       ("NAM1_6", "no NAT in place of NAT under the plate")],
    m="Swept again at 85 °C.",
    r="Above {NT20} by more than {NM1_3} is: length up to the depletion "
      "width is worth having.",
    l="None beyond those of the group.")
E["NM1_10"] = dict(
    p="The longest Metal1 plate, 10 µm: shows whether the gain stops "
      "once the plate passes the depletion width.",
    w="The surface under the first 5 µm to 6 µm is already depleted by "
      "the junction. Beyond that the plate adds depleted surface that "
      "holds little voltage, and brings its end nearer the P+ ring.",
    c=[("NM1_6", "a plate of 10 µm in place of 6 µm")],
    m="",
    r="Equal to {NM1_6}: the gain has stopped, and area spent on a "
      "longer plate is wasted.",
    l="The plate's end is 10 µm from the P+ ring, so a loss could come "
      "from that distance.")
E["NM2_6"] = dict(
    p="A Metal2 plate of 6 µm: the same length as {NM1_6} over twice the "
      "oxide.",
    w="Over 2.33 µm of oxide the plate couples to the surface half as "
      "strongly as Metal1. It depletes the surface less, and leaves a "
      "lower field at its own end and in the oxide.",
    c=[("NM1_6", "Metal2 in place of Metal1 at the same length"),
       ("NM2_12", "a plate of 6 µm in place of 12 µm")],
    m="",
    r="Below {NM1_6}: at this length the thinner oxide wins.",
    l="The Metal2 plate needs a via from the well's Metal1, and its "
      "edge lies above Metal1 of the contact ring, which screens the "
      "innermost part.")
E["NM2_12"] = dict(
    p="A Metal2 plate of 12 µm: tests whether length makes up for the "
      "thicker oxide.",
    w="A weakly coupled plate spreads the surface potential over a "
      "longer distance. With twice the length of {NM2_6}, the voltage "
      "under the plate has room to fall more gradually before the "
      "plate's end.",
    c=[("NM2_6", "a plate of 12 µm in place of 6 µm"),
       ("NM1_10", "Metal2 in place of Metal1 at a similar length")],
    m="",
    r="Above {NM2_6}: Metal2 wants more length than Metal1.",
    l="The plate's end is 8 µm from the P+ ring, the closest of any "
      "plate.")
E["NPM12"] = dict(
    p="A stepped plate of three layers: polysilicon to 2 µm, Metal1 to "
      "5 µm and Metal2 to 9 µm.",
    w="Each layer ends where the next, over thicker oxide, takes over. "
      "The surface potential is stepped down in three stages, so no "
      "single plate end carries the whole field peak, and the oxide "
      "under the polysilicon sees only the first part of the voltage.",
    c=[("NP2", "three stepped layers in place of polysilicon alone"),
       ("NM1_6", "three stepped layers in place of Metal1 alone")],
    m="",
    r="Above every single-layer plate: stepping is worth its "
      "complexity. Equal to the best single plate: it is not.",
    l="It is the only stepped plate on an N-well, so the lengths of its "
      "steps are not varied.")
E["NM1_6b"] = dict(
    p="A second copy of the Metal1 plate of 6 µm. It is the other half "
      "of the ratio that decides the deep-layer question.",
    w="The drawing is identical to {NM1_6}. A plate raises the breakdown "
      "voltage of an edge and does nothing for a bottom. If a deep P "
      "layer makes the bottom fail first, the plated wells equal the "
      "plain ones; if not, they exceed them by an amount close to the "
      "agreement limit, so one pair is not enough.",
    c=[("NM1_6", "nothing but the position on the die"),
       ("NT20c", "the plated half of the ratio, in place of the plain "
                 "half")],
    m="Swept with the same settings as {NM1_6} and in the same session.",
    r="The mean of {NM1_6} and this copy, divided by the mean of the "
      "three plain wells, is compared with the predicted ratio.",
    l="Two copies give a difference, not a distribution.")
E["NM1_6L"] = dict(
    p="Shows whether the Metal5 lead changes a well that has a Metal1 "
      "plate.",
    w="The Metal1 plate lies between the lead and the silicon over the "
      "first 6 µm and screens the surface there from the lead. Beyond the "
      "plate's end, where the field now peaks, a lead 30 µm wide covers "
      "the whole east side in place of a strip 6 µm wide.",
    c=[("NM1_6", "a lead 30 µm wide in place of 6 µm"),
       ("NT20L", "a Metal1 plate under the lead in place of none")],
    m="",
    r="Equal to {NM1_6}: the lead does not disturb the plate's end. "
      "Lower: it does, on every plated structure.",
    l="As for {NT20L}, a lead that helps is hidden by the three sides it "
      "does not cover. The simulation has no lead, so its prediction is "
      "that of {NM1_6}.")
E["NM1_6C0"] = dict(
    p="Shows whether a field plate rescues a square corner. A product's "
      "wells must have vertices, so this is the practical form of the "
      "corner question.",
    w="The Metal1 plate follows the square outline and extends 6 µm "
      "beyond each side and each 90° vertex. Over a vertex the plate "
      "spreads the depletion region outwards in every direction at "
      "once, which relieves exactly the crowding that makes a vertex "
      "weak.",
    c=[("NC0", "a Metal1 plate of 6 µm in place of none"),
       ("NM1_6", "four 90° vertices in place of eight of 135°")],
    m="The light of the avalanche, photographed at the current limit, "
      "shows whether the vertices still fail first.",
    r="The simulation puts it between the two: the plate lifts the "
      "square corner above the 57 V working voltage, but not to the "
      "value of the plate on a cut corner. If the measurement agrees, a "
      "product's wells need cut corners and plates together.",
    l="The plate's own outline has 90° corners over the oxide, where "
      "the field in the oxide is highest. The corner section is a "
      "cylinder of 1 µm radius, as for {NC0}, so the corner prediction "
      "is probably pessimistic: the measured value may be higher.")
