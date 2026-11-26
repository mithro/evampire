"""Catalogue texts: plain N-wells and drawn P-well.

catalogue.py joins these modules; its docstring describes the fields.

SPDX-License-Identifier: Apache-2.0
"""

E = {}

# ---- plain N-wells ---------------------------------------------------------
E["NT1"] = dict(
    p="Tests whether a P+ region 1 µm from an N-well, with no P-well, is "
      "enough to explain the published 14 V.",
    w="The P+ ring is so heavily doped that the depletion region cannot "
      "enter it. With the ring 1 µm from the edge, the whole voltage falls "
      "across 1 µm of substrate, and the field reaches its limit at a far "
      "lower voltage than with a distant ring.",
    c=[("NT5", "the P+ ring is at 1 µm in place of 5 µm"),
       ("NW1p5", "a P+ ring in place of a P-well at a similar distance")],
    m="The knee is expected well below that of the other plain wells, so "
      "a sweep that ends early is not a fault.",
    r="A value near 14 V here, with the other plain wells much higher, "
      "means a nearby P+ region can produce the published value without "
      "any P-well. If every plain well is near 14 V, this structure adds "
      "nothing.",
    l="Under assumption A the P-well reaches the well edge before the P+ "
      "ring does and hides the ring's effect.")
E["NT5"] = dict(
    p="Finds whether a P+ ring 5 µm away already limits the well.",
    w="In substrate doped at 3.5 × 10\\ :sup:`15` cm\\ :sup:`-3` a flat "
      "depletion region is about 5 µm wide at 70 V. If the region reaches "
      "the ring before avalanche, it can spread no further and the field "
      "rises faster from then on.",
    c=[("NT1", "the ring is at 5 µm in place of 1 µm"),
       ("NT10", "the ring is at 5 µm in place of 10 µm")],
    m="",
    r="A value below {NT10} means the depletion region reaches 5 µm "
      "before breakdown. An equal value means the region at the surface "
      "is shorter than under a flat junction.",
    l="The simulation predicts no difference from {NT10}, so a measured "
      "difference would count against the model and not only against the "
      "structure.")
E["NT10"] = dict(
    p="Shows whether the breakdown voltage has stopped rising by a ring "
      "distance of 10 µm.",
    w="Ten micrometres is about twice the flat depletion width at the "
      "voltage that bare substrate allows. Under assumption B the ring "
      "should therefore be out of reach, and the well should behave as if "
      "it stood alone.",
    c=[("NT5", "the ring is at 10 µm in place of 5 µm"),
       ("NT20", "the ring is at 10 µm in place of 20 µm")],
    m="",
    r="Equal to {NT20}: the breakdown voltage stopped rising before "
      "10 µm, and the default ring distance of 20 µm is safely large.",
    l="None beyond those of the group.")
E["NT20"] = dict(
    p="The reference structure of the die: a plain N-well with the "
      "default dimensions, against which every termination is read.",
    w="Nothing is drawn in its 20 µm of termination zone, so what the "
      "process puts there decides the result: P-well against the edge, or "
      "bare substrate. In bare substrate the curved edge and the vertices "
      "concentrate the field and break down before the flat bottom, "
      "unless a deep P layer makes the bottom fail first.",
    c=[("NT20b", "nothing: a second copy elsewhere on the die"),
       ("NT20L", "the Metal5 lead is 6 µm wide in place of 30 µm"),
       ("NT20V", "the 3.3 V area in place of the 6 V area"),
       ("NT20c", "nothing: a third copy"),
       ("NT10", "the ring is at 20 µm in place of 10 µm")],
    m="It is the first structure swept on each die, and is swept again at "
      "85 °C. It is one of the three on which the light of the avalanche "
      "is always photographed at the current limit.",
    r="Near 14 V: P-well lies against the well. Much higher: it does not, "
      "and the other groups then show what each termination gains.",
    l="A single plain well cannot tell an edge that fails from a bottom "
      "that fails; the plates and rings do that, and the capacitance of "
      "{CVNA} shows the deep layer directly.")
E["NC0"] = dict(
    p="Measures what a square corner costs against a corner cut at 45°.",
    w="At a vertex the depletion region wraps round a point, so field "
      "lines converge from more directions than along a straight side and "
      "the field is higher at the same voltage. A 90° vertex is the "
      "sharpest the layout can draw. Diffusion of the implant rounds it "
      "to a radius of about the well's lateral spread.",
    c=[("NT20", "four 90° vertices in place of eight of 135°"),
       ("NC15", "no cut in place of the longest cut"),
       ("NM1_6C0", "no plate in place of a Metal1 plate")],
    m="Swept again at 85 °C. The light of the avalanche is always "
      "photographed at the current limit; the four vertices should light "
      "first.",
    r="Below {NT20}: the vertices set the breakdown, and a cut is worth "
      "having. Equal: something other than the corner limits both.",
    l="The simulation of this corner did not reach breakdown. The table "
      "gives a lower bound, and a straight-line extrapolation of the "
      "unfinished sweep ends below 57 V "
      "(:numref:`tab-hvt-mc-corner`). Under assumption A the surface "
      "junction fails first and hides the corner.")
E["NC15"] = dict(
    p="Tells whether the length of the corner cut matters once the vertex "
      "is 135°.",
    w="The cut for a 15 µm radius takes 8.8 µm off each side and leaves an "
      "almost regular octagon. Its vertices have the same angle as those "
      "of {NT20} and stand further apart. If the corners behaved like arcs "
      "of the nominal radius, a larger radius would hold more.",
    c=[("NT20", "a cut of 8.8 µm in place of 4.7 µm"),
       ("NC0", "the longest cut in place of none")],
    m="The light of the avalanche is always photographed at the current "
      "limit, to see whether it sits at the eight vertices.",
    r="Equal to {NT20}: the vertex angle decides and the nominal radius "
      "means little. Higher: the cut length matters as a radius would.",
    l="The well cannot be rounder than this at 30 µm across, so a trend "
      "that continues has no further point.")
E["NT20b"] = dict(
    p="Gives the spread across one die: a second copy of the reference "
      "well, 1750 µm from the first.",
    w="The drawing is identical to {NT20}. Any difference between the two "
      "comes from the process varying across the die, or from the "
      "measurement not repeating.",
    c=[("NT20", "nothing but the position on the die")],
    m="Swept with the same settings as {NT20} and in the same session.",
    r="The difference between the two copies is the smallest difference "
      "between any two structures that can be called real.",
    l="Two copies sample two points on the die; {NT20c} adds a third.")
E["NT20L"] = dict(
    p="Shows whether the Metal5 lead changes the junction it crosses.",
    w="The lead is at the well's voltage, 5.76 µm above the silicon, and "
      "acts as a weak field plate over the strip it crosses. Here it is "
      "30 µm wide in place of 6 µm, so it covers the whole east side of "
      "the well and both of that side's vertices.",
    c=[("NT20", "a lead 30 µm wide in place of 6 µm")],
    m="",
    r="Equal to {NT20}: leaving the lead out of the simulation costs "
      "nothing. Lower: the lead harms the junction, and every structure "
      "carries that harm over 6 µm.",
    l="A lead that helps cannot show here, because the three sides it "
      "does not cover still break down at the unchanged voltage. The "
      "structure bounds the effect on a plain well only.")
E["NT20V"] = dict(
    p="Shows whether an N-well in the 6 V area breaks down differently "
      "from one in the 3.3 V area.",
    w="The layer that selects the thick gate oxide covers the whole "
      "structure. The foundry's two N-well diode models have the same "
      "capacitance and different breakdown voltages, 11 V for the 3.3 V "
      "area and 14 V for the 6 V area. Equal capacitance suggests the same "
      "well, so the difference would lie in what surrounds it.",
    c=[("NT20", "the 6 V area in place of the 3.3 V area")],
    m="",
    r="A difference of about 3 V in the direction of the models confirms "
      "that the surroundings of the well differ between the two areas.",
    l="The layer covers the termination zone as well as the well, so a "
      "difference cannot be assigned to one of them. Only this one "
      "structure is in the 6 V area.")

# ---- drawn P-well ----------------------------------------------------------
E["NW0"] = dict(
    p="Reproduces on purpose the junction suspected of setting the "
      "published 14 V: an N-well touching a P-well.",
    w="Both sides of the junction are heavily doped at the surface, so "
      "the depletion region is a fraction of a micrometre wide on each "
      "side. The field reaches its limit after a few volts, at the "
      "surface, along the whole edge.",
    c=[("NT20", "a drawn P-well against the edge in place of none"),
       ("NW1p5", "the P-well starts at 0 µm in place of 1.5 µm")],
    m="Swept again at 85 °C. The knee is expected early and sharp.",
    r="Equal to {NT20}: the foundry already puts P-well against a plain "
      "well. Far below {NT20}: it does not, and this junction is what "
      "the published value describes.",
    l="If the drawn and a generated P-well overlap, the layout cannot "
      "tell whether the implant is applied once or the doping is the "
      "same.")
E["NW1p5"] = dict(
    p="Tests whether 1.5 µm of clearance from a P-well is enough for an "
      "N-well. It is the clearance the rules give a deep N-well.",
    w="The depletion region crosses the 1.5 µm of substrate at a moderate "
      "voltage and then meets the P-well, where it stops. From there the "
      "field at the well edge rises with every further volt as it would "
      "against a wall.",
    c=[("NW0", "the P-well starts at 1.5 µm in place of 0 µm"),
       ("NW3", "the P-well starts at 1.5 µm in place of 3 µm"),
       ("NT1", "a P-well in place of a P+ ring at a similar distance")],
    m="",
    r="Well above {NW0} and below {NT20}: a P-well this close costs part "
      "of the voltage, and a generated P-well kept 1.5 µm away would too.",
    l="The gap is set by two mask edges that are aligned separately, so "
      "its true width varies from die to die by the alignment error.")
E["NW3"] = dict(
    p="Locates the distance at which a P-well stops lowering the "
      "breakdown voltage.",
    w="Three micrometres is a little less than the width the depletion "
      "region needs at the plain well's breakdown voltage. The P-well "
      "stops the region only near the end of the sweep, so little of the "
      "voltage is lost.",
    c=[("NW1p5", "the P-well starts at 3 µm in place of 1.5 µm"),
       ("NW6", "the P-well starts at 3 µm in place of 6 µm")],
    m="",
    r="Close to {NT20}: a clearance of 3 µm recovers most of the plain "
      "well's voltage.",
    l="Its difference from {NW6} is expected to be small, of the order of "
      "the spread between dies.")
E["NW6"] = dict(
    p="Confirms that a P-well 6 µm away no longer matters.",
    w="Six micrometres is wider than the depletion region at the plain "
      "well's breakdown voltage. The region never reaches the P-well, and "
      "the well breaks down as if the P-well were absent.",
    c=[("NW3", "the P-well starts at 6 µm in place of 3 µm"),
       ("NT20", "a P-well from 6 µm in place of none")],
    m="",
    r="Equal to {NT20}: 6 µm is a safe clearance. Higher than {NT20} "
      "while {NT20} is near 14 V: drawing a P-well keeps the generated "
      "one away, and a distant drawn P-well is itself a remedy.",
    l="No structure has a P-well further away, so a value still below "
      "{NT20} has no end point.")
E["NT20c"] = dict(
    p="A third copy of the reference well. The plain well is one half of "
      "the ratio that decides whether a deep P layer lies under N-wells.",
    w="The drawing is identical to {NT20}. Whether a plate raises the "
      "breakdown voltage is read from the plated wells divided by the "
      "plain ones. Three plain wells give a mean, and a spread to set "
      "against a predicted difference that is not much larger than the "
      "agreement limit.",
    c=[("NT20", "nothing but the position on the die"),
       ("NT20b", "nothing but the position on the die"),
       ("NM1_6b", "the plain half of the ratio, in place of the plated "
                  "half")],
    m="Swept with the same settings as {NT20} and in the same session.",
    r="The mean of the three plain wells is the denominator of the "
      "plate ratio.",
    l="Three points on one die still cannot separate a gradient from "
      "random variation.")
