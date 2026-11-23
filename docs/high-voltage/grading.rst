.. _hv-grading:

Spreading the voltage across the surface
========================================

This page describes ways to make the voltage between a high-voltage region
and the surrounding substrate fall gradually across the surface, instead of
all at one edge, so that no point reaches the critical field.

A gradual fall keeps the field low
----------------------------------

The field at a point is how steeply the voltage changes there. A voltage
that falls evenly over a length :math:`L` has a field of :math:`V/L`
everywhere along it. A carrier crossing a field frees new carriers at a
rate per centimetre :math:`\alpha`, which Fulop's fit gives as
:math:`a_\alpha E^7` [HV-PARK]_ (Equation 3.25). Avalanche runs away when
each carrier crossing the field frees one more, that is, when
:math:`\alpha L = 1` for a uniform field. Setting :math:`E = V/L` gives the
shortest length over which a voltage can fall:

.. math::

   L_\text{min} = \left(a_\alpha V^7\right)^{1/6}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`L_\text{min}`
     - Shortest distance for the voltage to fall over
     - cm
   * - :math:`V`
     - Voltage between the high-voltage region and the substrate
     - V
   * - :math:`a_\alpha`
     - Fulop's coefficient for silicon, :math:`1.8 \times 10^{-35}`
       [HV-PARK]_ (Section 3.1.5)
     - cm\ :sup:`6` V\ :sup:`-7`

For 57 V:

.. math::

   L_\text{min} &= \left(1.8 \times 10^{-35} \times 57^7\right)^{1/6} \\
     &= 1.8 \times 10^{-4}\ \text{cm} = 1.8\ \text{µm}

The field is then 3.2 × 10\ :sup:`5` V/cm, and holding 100 V takes 3.5 µm
(`calc.py <https://github.com/mithro/evampire/blob/main/docs/high-voltage/calc.py>`__,
section 4). The flat-junction fit on :doc:`junctions` comes from the same
coefficient: its triangular field gives an ionisation integral of 0.98.
The length does not depend on the doping, because a uniform field needs
the charge that would bend it to be absent or balanced.

That is the ideal of a perfectly even fall. Real structures leave the field
peaked at their edges, so they need more length than this, by an amount
found by device simulation of each structure. The structures below are
ways of getting closer to the ideal (:numref:`fig-hv-grading`).

.. figure:: grading.svg
   :name: fig-hv-grading
   :alt: Four cross-sections of a high-voltage N-well in a P-type substrate.
         The first has floating rings beside the well. The second has a
         field plate over the edge. The third has a thin N layer depleted
         from below. The fourth has a resistor chain over the surface with
         taps at falling voltages.

   Four ways to spread the voltage of a high-voltage well across the
   surface: floating rings, a field plate, a depleted thin layer and a
   resistive chain.

Floating rings take the voltage in steps
----------------------------------------

Rings of N-type silicon drawn around the high-voltage well, and connected
to nothing, are called :term:`floating field rings <floating field ring>`.
As the voltage rises, the depletion region around the well spreads outward
until it reaches the first ring. The ring then rises with it, a fixed step
below the well, and the depletion region spreads on from the ring to the
next one [HV-KAO-WOLLEY]_ [HV-US4573066]_. Each ring holds part of the
voltage, and the spacing between rings sets how large each step is. Four or
five rings are usual [HV-SPIRITO]_ (slide 26).

The rings need nothing beyond the wells the process already has, and no
current. Their spacing is critical, because a gap too wide leaves the
whole voltage on one edge and a gap too narrow lets two rings share their
voltage. For one worked case, the best gap from the well to the first
ring is about a third of the flat depletion width [HV-SPIRITO]_ (slide 25).
Spacings are found by device simulation and checked on test structures.

A field plate pushes the field away from the edge
-------------------------------------------------

A :term:`field plate` is a conductor, metal or polysilicon, connected to the
well and extending over the insulator beyond the well's edge. Its voltage
pulls the depletion region in the substrate below it further out, which
lowers the field at the curved edge [HV-SPIRITO]_ (slide 27)
[HV-PARK]_ (Section 2.3.1). A thin insulator under the plate moves the
breakdown to the end of the plate, and a thick one leaves it at the
junction [HV-SPIRITO]_ (slide 28). A plate built in steps over different
thicknesses balances the two. In a standard process, polysilicon on the
:term:`field oxide` and then each metal layer over the dielectrics above it
give a set of steps.

A thin layer depleted from below spreads the field evenly
---------------------------------------------------------

A thin, lightly doped N layer lying on a P substrate is depleted from two
sides at once: sideways from its edge, and upward from the junction with
the substrate below it. When the total charge in the layer is small
enough, it is fully depleted before the surface field reaches its critical
value, and the voltage then falls almost evenly along the surface. This is
:term:`RESURF`, for reduced surface field [HV-APPELS-VAES]_
[HV-PARK]_ (Section 2.3).

RESURF works only when the layer's dopant charge per area is close to a
value set by silicon's critical field. With a critical field of
:math:`3 \times 10^5` V/cm, the formula in [HV-PARK]_ (Equation 2.10)
gives at most about :math:`1.4 \times 10^{12}\ \text{cm}^{-2}`.
[HV-US5223919]_ gives about :math:`2 \times 10^{12}\ \text{cm}^{-2}`. Whether a gf180mcu N-well,
or an N-well with part of its area blocked from the implant, comes near
that value is a question for measurement on test structures.

A resistor chain forces an even gradient
----------------------------------------

The rings and layers above find their own voltages. A resistor chain sets
them instead. A long polysilicon resistor, often drawn as a spiral, runs
over the field oxide from the high-voltage well to the substrate contact.
The current through it makes its voltage fall evenly along its length, and
through the oxide its voltage pulls the surface below it into the same
even gradient [HV-EP2779225]_ [HV-US10217861]_. Taps along the chain can also drive a set of rings
directly, so that each ring sits at a chosen fraction of the voltage.

The cost is the current that flows down the chain all the time. A chain
holding 57 V with 1 µA flowing needs 57 MΩ and takes 57 µW; with 10 µA it
takes 570 µW
(`calc.py <https://github.com/mithro/evampire/blob/main/docs/high-voltage/calc.py>`__,
section 6). A high-resistance polysilicon resistor of that value is long, so
its area is part of the design.

Current through the substrate grades only at high power
-------------------------------------------------------

The substrate itself could be graded by driving a current through it
between two contacts, so that its voltage falls steadily from one to the
other. The substrate is a thick, fairly conductive slab. At
:math:`10^{15}\ \text{cm}^{-3}` P-type silicon has a resistivity of about
14 Ω·cm [HV-NBS]_ (Table 5), so a slab 1 mm long, 1 mm wide and 300 µm
thick has about 450 Ω between its ends. Holding 57 V across it takes about
130 mA and 7 W
(`calc.py <https://github.com/mithro/evampire/blob/main/docs/high-voltage/calc.py>`__,
section 6). The thickness and resistivity are illustrations: thinning the
die or a lighter-doped substrate would raise the resistance.

Commercial chips float a well hundreds of volts up
--------------------------------------------------

Commercial gate-driver chips for half bridges are built on bulk silicon
with junction isolation. Their high-side circuits sit in a floating well that
rises to the full bus voltage above the grounded substrate,
in an isolation tub that International Rectifier describes as able to
float from 500 V or 1200 V down to −5 V [HV-IR-AN978]_ (Section 2.3). That
is a reference example from a dedicated
high-voltage process, not evidence of what gf180mcu can hold. The gf180mcu
values depend on the doping and edges described on :doc:`junctions`, which
test structures would measure.
