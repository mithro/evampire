"""Catalogue texts: the introduction of each group.

catalogue.py joins these modules; its docstring describes the fields:
what the group is for, its shared mechanism (works), how its results
read together (read) and its shared limits.

SPDX-License-Identifier: Apache-2.0
"""

GROUPS = {
    "surround": dict(
        file="plain", title="Plain N-wells",
        what="The plain wells have nothing drawn between the well and the "
             "P+ ring. They show what the process itself puts beside an "
             "N-well, and every other group is read against them.",
        works="A reverse-biased well empties the more lightly doped silicon "
              "beside it of carriers. That depletion region widens with "
              "voltage, and the field at the well's edge rises with it "
              "until avalanche starts. Anything that stops the depletion "
              "region early forces the same voltage across less silicon, "
              "so the field reaches its limit sooner.",
        read="If the foundry generates P-well against the well, every "
             "member breaks down near the published 14 V, whatever its "
             "ring distance or corner. If only substrate lies beside the "
             "well, the values are much higher and fall only when the P+ "
             "ring comes within reach. If a deep P layer lies under the "
             "well, the values with a distant ring all stop at the "
             "breakdown of the well's flat bottom.",
        limits="Every corner on the die is a 45° cut, because the design "
               "rules allow no other angle on a well. The corner sections "
               "err in two directions. A cut corner is simulated as an arc "
               "of the nominal radius, and its 135° vertices are not "
               "modelled, so its prediction is optimistic there. A square "
               "corner is simulated as a cylinder of 1 µm radius, a thin "
               "post far smaller than the depletion region, so its "
               "prediction is probably pessimistic. The "
               "Metal5 lead crosses the termination zone of every member, "
               "and only {NT20L} varies it. The copies and the lead "
               "control have the simulated section of {NT20}, because a "
               "two-dimensional section cannot contain the lead."),
    "pwell": dict(
        file="p-well", title="Drawn P-well",
        what="A drawn P-well stands in for the P-well that the foundry may "
             "generate, at a distance that the layout sets.",
        works="A P-well is assumed to be about a hundred times more "
              "heavily doped than the substrate, so the depletion region "
              "enters it by only a fraction of a micrometre. A P-well at a "
              "distance from the well edge therefore holds the depletion "
              "region to about that distance, and the field at the edge "
              "rises to its limit at a lower voltage.",
        read="If the foundry already generates P-well against every "
             "N-well, the drawn one changes nothing and all four equal "
             "{NT20}. If it does not, the breakdown voltage rises with the "
             "distance and reaches the {NT20} value where the P-well stops "
             "mattering.",
        limits="Under assumption A the group shows nothing beyond {NT20}, "
               "and {NW0} with its copy {NW0b} becomes the reference that "
               "every N-well is divided by. "
               "The doping of the drawn P-well is not published, so the "
               "distance at which it stops mattering is known only from "
               "the simulation's assumed profile."),
    "nat": dict(
        file="nat", title="NAT layer",
        what="The NAT layer marks where a native transistor keeps the bare "
             "substrate as its channel. These structures test whether it "
             "also keeps a generated P-well away from an N-well edge, and "
             "measure floating and contacted rings under it.",
        works="The design manual says the P-well implant is blocked under "
              "NAT. If that holds with no transistor present, the silicon "
              "under NAT is bare substrate, and the well's depletion "
              "region can spread through it as under assumption B. Rule "
              "NAT.3 keeps NAT at least 0.5 µm from an N-well, so a strip "
              "of unprotected silicon always remains beside the edge. "
              "Rings are N-well too, so round {NAR1_2}, {NAR3_2}, {NAR1S3} "
              "and {NAR1S8} the layer is cut into strips that keep 0.6 µm "
              "from the well and from each side of every ring. If NAT is "
              "what clears an edge, the ordinary ring structures are still "
              "limited by P-well, and these four are the only ones that "
              "measure rings and the spacing to a neighbouring well "
              "there.",
        read="If NAT blocks the P-well and the strip stays empty, the "
             "members equal their counterparts without NAT under "
             "assumption B. If P-well fills the strip, or NAT blocks "
             "nothing, they equal {NT20} under assumption A, rings "
             "included, because P-well in the strips limits them as it "
             "limits the plain well. Under An and under B the rings under "
             "NAT behave as rings in bare substrate.",
        limits="No member has NAT touching the N-well or a ring, because "
               "the rules forbid it, and every strip left beside them is "
               "0.6 µm wide; no member has a wider strip. The group cannot "
               "tell a filled strip from a NAT layer that blocks nothing. "
               "No polysilicon may lie under NAT."),
    "plates": dict(
        file="field-plates", title="Field plates",
        what="A field plate is a conductor joined to the well that extends "
             "over the oxide beyond the well's edge. These structures "
             "measure what a plate of each layer and length gains.",
        works="The plate is at the well's voltage, so it pushes holes away "
              "from the silicon surface beneath it and widens the "
              "depletion region there. The field at the well's curved edge "
              "falls, and a new peak forms under the plate's end. The "
              "oxide under the plate sets the balance: 0.32 µm under "
              "polysilicon, 1.18 µm under Metal1 and 2.33 µm under Metal2. "
              "Thin oxide acts strongly and puts a high field at the "
              "plate's end; thick oxide acts weakly over a longer reach.",
        read="Under assumption A no plate helps, because the junction to "
             "the P-well at the surface fails first. Under B each plate "
             "raises the breakdown voltage above {NT20} by an amount that "
             "depends on layer and length. With a deep P layer under the "
             "well, every plate stops at the same voltage as the plain "
             "well, since the bottom of the well fails first.",
        limits="A plate tied to the well cannot be biased separately; the "
               "gated diodes do that. Oxide breakdown under a polysilicon "
               "plate would look like junction breakdown on the first "
               "sweep and like a short on the second."),
    "rings": dict(
        file="floating-rings", title="Floating rings",
        what="Floating rings are N-well rings round the well that connect "
             "to nothing. These structures find the gap at which a ring "
             "starts to take voltage, and what more rings add. Six of "
             "them bring ring 1 out to a pad. Five have one ring of the "
             "same width at gaps of 2 µm, 3 µm, 5 µm, 8 µm and 12 µm, and "
             "the sixth has four rings with ring 1 at 1.6 µm. Rings under "
             "NAT are in the :doc:`NAT group <nat>`.",
        works="The well's depletion region spreads outwards until it "
              "reaches ring 1. From then on the ring's potential rises "
              "with the well's, a fixed step below it. The well's own edge "
              "sees only that step. The rest of the voltage falls between "
              "the ring's outer edge and the substrate, where the next "
              "ring repeats the process.",
        read="Under assumption A the P-well between well and ring fails "
             "before the ring acts, and every member equals {NT20}. Under "
             "An the same holds, since no member has NAT. Under "
             "B a ring raises the breakdown voltage by an amount set by "
             "the gap, and more rings raise it further. With a deep P "
             "layer under the well, all stop at the plain well's value.",
        limits="Rule NW.2b forbids a gap below 1.4 µm. A contacted ring "
               "held at 0 V is a neighbouring well, and the wide gaps give "
               "the spacing two wells need; a floating ring at those gaps "
               "would never be reached. The simulation ends "
               "its ionisation path at a ring, and several multi-ring "
               "cases have no finished simulation, so their predictions "
               "are the weakest on the die."),
    "gated": dict(
        file="gated-diodes", title="Gated diodes",
        what="A gated diode has a plate over the well edge that is not "
             "joined to the well and has its own pad. The plate's voltage "
             "sets the state of the silicon surface while the junction is "
             "measured.",
        works="A negative plate attracts holes to the surface beside the "
              "well and strengthens the field at the edge. A positive "
              "plate first depletes that surface, then inverts it. The "
              "plate voltages at which the well current steps up and falls "
              "back give the flat-band voltage and the field threshold, "
              "and from them the oxide charge and the surface doping.",
        read="A surface of bare substrate inverts at a few tens of volts "
             "under Metal1. A surface of P-well does not invert within the "
             "plate's range, because its threshold is several times "
             "higher. The threshold therefore shows what silicon lies "
             "beside the well, without breaking the junction down.",
        limits="The plate starts 0.5 µm inside the well edge. Its Metal1 "
               "is 1.2 µm from the Metal1 of the well's via stack and "
               "1.5 µm from the well's Metal1 ring, so the voltage between "
               "plate and well stays within 80 V, which is 0.67 MV/cm "
               "across the narrower gap. On the polysilicon plate it stays "
               "within 60 V, 1.92 MV/cm across the 0.312 µm of oxide that "
               "the extraction capacitance gives. The current step of the first part "
               "may be only tens of femtoamperes. Over P-well the first "
               "part gives the flat-band voltage only."),
    "dnw": dict(
        file="deep-n-well", title="Deep N-wells",
        what="The deep N-well structures are a reference group. They "
             "repeat the edge variations of the other groups on a well "
             "that is expected to break down at its bottom: the ring "
             "distance, the square corner, a Metal1 plate, NAT over the "
             "edge, and NAT with a plate.",
        works="The published capacitance and breakdown of the deep N-well "
              "fit only if a heavily doped P layer lies just under it. The "
              "depletion region under the flat bottom is then held to a "
              "fraction of a micrometre, and the bottom reaches the "
              "critical field near 30 V. That is below what any edge of "
              "the well would hold, so nothing drawn at the edge changes "
              "the result.",
        read="If the picture is right, every member breaks down near "
             "30 V, the published model value, whatever its ring "
             "distance, corner, P-well, NAT or plate. A member that holds "
             "much more than the plain {DT20} shows that the edge limits "
             "after all, and the deep-layer picture is wrong for it.",
        limits="The group is partly circular. The deep N-well profile was "
               "fitted to the published 30.48 V model parameter with the "
               "same ionisation integral, so the value predicted for {DT20} "
               "is a fit and not a prediction. The group tests only that the result is "
               "insensitive to what is drawn at the edge. "
               "The simulated deep N-well is a buried layer with almost no "
               "donors at the surface, so its indifference to the edge is "
               "partly built into the model. If the real well is N-type "
               "up to the surface, the published value could be set at "
               "the edge, and the members with a close ring, a P-well or "
               "NAT would then differ. If the bottom does limit, the deep "
               "N-well is not a way to hold 57 V."),
    "large": dict(
        file="capacitance-wells", title="Capacitance wells and open reference",
        what="Five wells are large enough for their capacitance to be "
             "measured: an N-well and an N-well under NAT, each at two "
             "sizes, and one deep N-well. One more structure has a pad "
             "and a lead with no well. Together they give the doping under the wells and the "
             "part of every reading that the pad contributes.",
        works="The capacitance of a reverse-biased junction is that of a "
              "slab of silicon as thick as the depletion region. As the "
              "voltage rises the region widens and the capacitance falls. "
              "How fast it falls at each voltage gives the doping at the "
              "edge of the region, so a sweep reads the doping profile "
              "downwards from the junction.",
        read="A capacitance that keeps falling means lightly doped "
             "silicon continues below the well. A capacitance that stops "
             "falling means the depletion region has met a heavily doped "
             "layer. For an N-well that would be the deep P layer of "
             "assumption D.",
        limits="The sweep cannot go beyond the breakdown voltage of the "
               "well's own edge. Every large well receives dummy fill "
               "inside the well. Series resistance in the well and the "
               "substrate distorts the reading at high frequency."),
}
