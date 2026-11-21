.. _hv-junctions:

How a junction holds voltage
============================

This page explains how a reverse-biased P-N junction holds a voltage, why
the doping on its lightly doped side sets how much, and why the curved
edges of a well break down long before its flat bottom.

The voltage sits across the depletion region
--------------------------------------------

A reverse-biased junction holds its voltage across a
:term:`depletion region`, a layer on both sides of the junction emptied of
free carriers. The fixed charge of the dopant atoms left in that layer sets
up an electric field, strongest at the junction itself
[HV-PARK]_ (Section 3.2.1.2). When the strongest field reaches the critical
field of silicon, about :math:`3 \times 10^5` V/cm [HV-IOFFE]_, carriers
crossing the layer
gain enough energy to free more carriers, and the current runs away. This
is :term:`avalanche breakdown`.

When one side of the junction is much more heavily doped than the other,
almost all of the depletion region lies in the lightly doped side, and that
side alone sets the breakdown voltage. For silicon, an empirical fit
by Baliga gives the breakdown voltage and the depletion width at breakdown
[HV-PARK]_ (Equations 3.30 and 3.31) [HV-US6344676]_ (Equation 1):

.. math::

   V_\text{B} &= 5.34 \times 10^{13} \times N^{-3/4} \\
   W_\text{B} &= 2.67 \times 10^{10} \times N^{-7/8}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`V_\text{B}`
     - Breakdown voltage of a flat junction
     - V
   * - :math:`W_\text{B}`
     - Width of the depletion region at breakdown
     - cm
   * - :math:`N`
     - Doping of the lightly doped side
     - cm\ :sup:`-3`

For :math:`N = 10^{15}\ \text{cm}^{-3}`:

.. math::

   V_\text{B} &= 5.34 \times 10^{13} \times (10^{15})^{-3/4} \\
     &= 5.34 \times 10^{13} \times 5.62 \times 10^{-12} \\
     &= 300\ \text{V} \\
   W_\text{B} &= 2.67 \times 10^{10} \times (10^{15})^{-7/8} \\
     &= 2.67 \times 10^{10} \times 7.50 \times 10^{-14} \\
     &= 2.0 \times 10^{-3}\ \text{cm} = 20\ \text{µm}

Lighter doping holds more and needs more room
---------------------------------------------

Lighter doping spreads the same charge over a wider layer, so the field
reaches its critical value only at a higher voltage. The price is width:
the depletion region needs room to spread
(:numref:`tab-hv-flat-breakdown`). A junction meant to hold a high voltage
needs that much lightly doped silicon on one side of it.

.. list-table:: Breakdown of a flat silicon junction against doping
   :name: tab-hv-flat-breakdown
   :header-rows: 1
   :widths: 34 33 33

   * - Doping of the lightly doped side (cm\ :sup:`-3`)
     - Breakdown voltage (V)
     - Depletion width at breakdown (µm)
   * - 10\ :sup:`14`
     - 1690
     - 150
   * - 10\ :sup:`15`
     - 300
     - 20
   * - 10\ :sup:`16`
     - 53
     - 2.7
   * - 10\ :sup:`17`
     - 9
     - 0.36

The values come from the two equations above
(`calc.py <https://github.com/mithro/evampire/blob/main/docs/high-voltage/calc.py>`__,
section 1).

The gf180mcu substrate is lightly doped
---------------------------------------

The gf180mcu documents give the substrate's type but not its doping. The
doping can be estimated from the junction capacitance in the PDK's models,
because the width of a depletion region, and so its capacitance per area,
depends on the doping of its lightly doped side. For a junction much more
heavily doped on one side, the capacitance per area at zero bias is
:math:`C_0 = \sqrt{q \varepsilon_\text{Si} N / (2 V_\text{bi})}`
[HV-MIT-6012]_ (slide 6-13), which gives the doping:

.. math::

   N \approx \frac{2 \times V_\text{bi} \times C_0^2}
                  {q \times \varepsilon_\text{Si}}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`C_0`
     - Capacitance per area at zero bias, :math:`1.49 \times 10^{-8}`
       for the N-well to substrate junction [HV-GF180-MODELS]_
     - F/cm\ :sup:`2`
   * - :math:`V_\text{bi}`
     - Built-in voltage of the junction, 0.439 in the same model
     - V
   * - :math:`q`
     - Electron charge, :math:`1.602 \times 10^{-19}`
     - C
   * - :math:`\varepsilon_\text{Si}`
     - Permittivity of silicon, :math:`1.035 \times 10^{-12}`
     - F/cm

.. math::

   N &\approx \frac{2 \times 0.439 \times (1.49 \times 10^{-8})^2}
                   {1.602 \times 10^{-19} \times 1.035 \times 10^{-12}} \\
     &= 1.2 \times 10^{15}\ \text{cm}^{-3}

The equation assumes an abrupt junction with uniform doping. The model's
capacitance falls more slowly with voltage than that. The same relation
says that :math:`1/C^2` rises in a straight line with reverse voltage, with a
slope of :math:`2/(q \varepsilon_\text{Si} N)`, so the slope of the model's
:math:`1/C^2` gives the doping at the depth the depletion region reaches.
Between 2 V and 10 V it gives :math:`5.3 \times 10^{15}\ \text{cm}^{-3}`
(`calc.py <https://github.com/mithro/evampire/blob/main/docs/high-voltage/calc.py>`__,
section 2). Both are estimates. A capacitance measurement on a large N-well
test structure would give the doping profile directly.

At :math:`1.2 \times 10^{15}` to :math:`5.3 \times 10^{15}\ \text{cm}^{-3}`,
a flat junction to the substrate would hold about 90 V to 270 V. The
published breakdown of the N-well to the substrate is 10 V minimum and
14 V typical [HV-GF180-EP-5]_. The flat bottom of the well is not what
breaks down.

Curved edges break down first
-----------------------------

A well is made by implanting dopant at the surface and letting it diffuse
down and sideways, so its edges are curved. Along a straight side the edge
is part of a cylinder, with a radius about equal to the well's depth. At a
corner it is part of a sphere. The field lines crowd together at a curved
edge, so the field there reaches the critical value at a lower voltage than
under the flat bottom [HV-SZE-GIBBONS]_ [HV-SPIRITO]_ (slide 21).

Baliga and Ghandhi give the breakdown of cylindrical and spherical
junctions as a fraction of the flat value, as a function of the radius
divided by the flat depletion width [HV-BALIGA-GHANDHI]_, as printed in
[HV-US6344676]_ (Equations 3 and 4) (:numref:`tab-hv-curved-breakdown`).
A tighter radius breaks down sooner, and a corner sooner than a side. A
published example for the same doping gives about 160 V for a spherical
junction of 10 µm radius, against about 320 V for a flat one
[HV-US5912501]_.

.. list-table:: Breakdown of curved junction edges in a substrate doped at
               10\ :sup:`15` cm\ :sup:`-3`
   :name: tab-hv-curved-breakdown
   :header-rows: 1
   :widths: 34 33 33

   * - Radius of the edge (µm)
     - Along a side, cylinder (V)
     - At a corner, sphere (V)
   * - 0.5
     - 50
     - 21
   * - 1
     - 74
     - 35
   * - 2
     - 103
     - 56
   * - 3
     - 123
     - 72

The values come from
`calc.py <https://github.com/mithro/evampire/blob/main/docs/high-voltage/calc.py>`__,
section 3. The published 14 V is lower again than the corner values, so the
field at the edge of a gf180mcu N-well is higher than curvature alone
explains. A more heavily doped layer at the surface beside the well, or an
edge sharper than 0.5 µm, would do it. Breakdown measurements on test wells
with different corner shapes and spacings would show which.

What this means for a design
----------------------------

The substrate's light doping is enough, in principle, for a junction that
holds well over 57 V. What limits a drawn well is its edges. Three things
raise the breakdown of an edge:

* Rounding the corners of the drawn well, which removes the spherical
  corners and leaves the cylindrical sides.
* Keeping more heavily doped layers away from the edge, so the lightly doped
  substrate takes the depletion region.
* Spreading the voltage over a wider part of the surface, which is the
  subject of :doc:`grading`.
