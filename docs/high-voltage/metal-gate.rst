.. _hv-metal-gate:

Transistors with a metal gate
=============================

This page describes a transistor whose gate is one of the metal layers,
which lets a high-voltage node control low-voltage silicon with only
insulator between them.

The gate can be any conductor
-----------------------------

A MOS transistor works because charge on its gate draws an equal and
opposite charge into the silicon below it. Above a threshold voltage that
charge includes a thin layer of free electrons at the surface of P-type
silicon, the inversion layer, which conducts between the source and drain
[HV-MIT-6012-L8]_ (slides 8-13 and 8-16). Nothing in that physics needs the
gate to be polysilicon or close to the silicon. A metal plate on any layer
does the same, with the whole insulator stack beneath it as the gate
insulator.

:numref:`fig-hv-metal-gate` shows such a transistor. Two N+ regions in the
substrate are its source and drain, the field oxide between them and the
dielectrics above it are its gate insulator, and a plate on a metal layer
is its gate. The plate connects to the high-voltage node being sensed. The
source and drain stay at low voltage.

.. figure:: metal-gate.svg
   :name: fig-hv-metal-gate
   :alt: Cross-section of a P-type substrate with two N+ regions, source and
         drain, separated by field oxide. Five dashed lines in the
         insulator above mark the metal levels. A plate on Metal5 above the
         field oxide is at 57 V, and an arrow marks 57 V across the
         insulator. A thin inversion layer under the field oxide joins
         source and drain. P+ taps sit outside the device.

   A transistor with its gate on Metal5. The insulator holds the whole
   voltage of the sensed node, and the silicon stays near the source
   voltage.

The silicon never sees the high voltage
---------------------------------------

Once the gate is above threshold, the inversion layer connects to the
source and sits near the source voltage. The silicon surface then changes
little as the gate voltage rises further: the extra gate charge is matched
by extra electrons in the inversion layer, not by a wider depletion region
[HV-MIT-6012-L8]_ (slide 8-15). The gate voltage therefore falls almost
entirely across the insulator. No junction holds the high voltage, so the
limits on :doc:`junctions` do not apply.

At 57 V the field in the insulator is 0.48 MV/cm under Metal1 and
0.10 MV/cm under Metal5
(`calc.py <https://github.com/mithro/evampire/blob/main/docs/high-voltage/calc.py>`__,
section 7), far below the fields on :doc:`dielectric`. The breakdown of the
gf180mcu dielectrics is not published, but these fields leave a wide
margin. The tighter limit is likely sideways, to low-voltage metal on the
same layer, which the spacing sets.

The plate inverts any P-type surface it covers, not only the channel. The
inversion layer would then join every N region under the plate. Heavily
doped P+ taps around the device stop it spreading
(:numref:`fig-hv-metal-gate`), because heavier doping raises the threshold
far above the sensed voltage, as the next section shows.

Each metal layer is a different gate insulator
----------------------------------------------

The open gf180mcu extraction rules give the capacitance per area of each
metal layer to the substrate [HV-OPENPDKS-EXTRACT]_. A capacitance per area
:math:`C` is that of a silicon dioxide layer of thickness
:math:`\varepsilon_\text{ox}/C`, which gives each layer an equivalent
thickness (:numref:`tab-hv-metal-stack`). The layers further from the
silicon have less capacitance and act as thicker gate insulators.

.. list-table:: Capacitance of each metal layer to the substrate, and the
               equivalent oxide thickness
   :name: tab-hv-metal-stack
   :header-rows: 1
   :widths: 20 30 25 25

   * - Layer
     - C over field oxide (aF/µm²)
     - Thickness over field oxide (µm)
     - Thickness over active (µm)
   * - Metal1
     - 29.3
     - 1.18
     - 0.87
   * - Metal2
     - 15.0
     - 2.30
     - 2.00
   * - Metal3
     - 10.1
     - 3.42
     - 3.12
   * - Metal4
     - 7.60
     - 4.54
     - 4.24
   * - Metal5
     - 5.80
     - 5.96
     - 5.65

The capacitances are nominal. The same rules give minimum and maximum
corners 7 % to 13 % either side
(`calc.py <https://github.com/mithro/evampire/blob/main/docs/high-voltage/calc.py>`__,
section 7). Over active silicon, with no field oxide below, each layer
sits closer to the channel.

The threshold rises with the insulator thickness
------------------------------------------------

The threshold is the gate voltage at which the electron concentration at
the surface equals the doping. It is the sum of the voltage needed to bring
the silicon to flat band, the voltage across the depleted silicon, and the
voltage across the insulator needed to hold the depletion charge
[HV-MIT-6012-L8]_ (slide 8-12) [HV-MIT-6012-L7]_ (slide 7-11):

.. math::

   V_\text{T} &= V_\text{FB} + 2\phi_\text{F}
     + \frac{Q_\text{dep}}{C_\text{ox}} \\
   Q_\text{dep} &= \sqrt{2 q \varepsilon_\text{Si} N \times 2\phi_\text{F}}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`V_\text{T}`
     - Threshold voltage of the gate to the source
     - V
   * - :math:`V_\text{FB}`
     - Flat-band voltage: the gate voltage that leaves the silicon surface
       uncharged, set by the gate material and charge in the insulator.
       Taken as −0.9 V for an aluminium gate as an illustration
     - V
   * - :math:`\phi_\text{F}`
     - :math:`(kT/q) \ln(N/n_\text{i})`, the depth of the Fermi level below
       the middle of the band gap, with :math:`n_\text{i} = 10^{10}`
       cm\ :sup:`-3` [HV-MIT-6012-L7]_ (slide 7-12)
     - V
   * - :math:`Q_\text{dep}`
     - Charge per area in the depleted silicon at threshold
     - C/cm\ :sup:`2`
   * - :math:`q`
     - Electron charge, :math:`1.602 \times 10^{-19}`
     - C
   * - :math:`\varepsilon_\text{Si}`
     - Permittivity of silicon, :math:`1.035 \times 10^{-12}`
     - F/cm
   * - :math:`N`
     - Doping of the P-type silicon under the gate
     - cm\ :sup:`-3`
   * - :math:`C_\text{ox}`
     - Capacitance per area of the gate insulator, from
       :numref:`tab-hv-metal-stack`
     - F/cm\ :sup:`2`

For Metal5 over field oxide, :math:`C_\text{ox} = 5.80 \times 10^{-10}`
F/cm², on substrate doped at :math:`1.2 \times 10^{15}` cm\ :sup:`-3`
(:doc:`junctions`):

.. math::

   \phi_\text{F} &= 0.02585 \times \ln(1.2 \times 10^{5}) \\
     &= 0.302\ \text{V} \\
   Q_\text{dep} &= 1.55 \times 10^{-8}\ \text{C/cm}^2 \\
   V_\text{T} &= -0.9 + 0.60
     + \frac{1.55 \times 10^{-8}}{5.80 \times 10^{-10}} \\
     &= -0.9 + 0.60 + 26.8 \\
     &= 26.5\ \text{V}

The last term dominates for every metal layer, so the threshold rises
almost in proportion to the insulator thickness
(:numref:`tab-hv-metal-vt`). It also rises with the doping, and steeply.
The substrate estimates on :doc:`junctions` give the first two columns. The
third is an illustration of a more heavily doped P-type well under the
channel, whose doping in gf180mcu is not published.

.. list-table:: Threshold of a metal-gate transistor over field oxide,
               against doping under the gate
   :name: tab-hv-metal-vt
   :header-rows: 1
   :widths: 25 25 25 25

   * - Gate layer
     - 1.2 × 10\ :sup:`15` cm\ :sup:`-3` (V)
     - 5.3 × 10\ :sup:`15` cm\ :sup:`-3` (V)
     - 10\ :sup:`17` cm\ :sup:`-3` (V)
   * - Metal1
     - 5.0
     - 11.6
     - 57
   * - Metal2
     - 10.0
     - 22.8
     - 111
   * - Metal3
     - 15.1
     - 34.1
     - 165
   * - Metal4
     - 20.1
     - 45.3
     - 219
   * - Metal5
     - 26.5
     - 59.5
     - 287

The values come from
`calc.py <https://github.com/mithro/evampire/blob/main/docs/high-voltage/calc.py>`__,
section 7.

Charge in the insulator moves the threshold
-------------------------------------------

Fixed charge trapped in the insulator adds to the gate's charge. By
:math:`Q = CV`, a charge per area :math:`Q_\text{ox}` shifts the threshold
by :math:`Q_\text{ox}/C_\text{ox}`
[HV-MIT-6012-L8]_ (slide 8-16). A charge of :math:`10^{11}` electron
charges per cm² shifts it by 5.5 V under Metal1 and by 27.6 V under Metal5
(`calc.py <https://github.com/mithro/evampire/blob/main/docs/high-voltage/calc.py>`__,
section 7). The charge in the gf180mcu dielectrics is not published, and
deposited dielectrics may hold more than grown oxide. The threshold
of each layer is therefore known only once measured, and it may drift with
temperature and time.

Two plates on the same layer, side by side, share the same charge per area
to the extent the dielectric is uniform. A circuit that compares two such
transistors cancels most of the shift, as the level shifter below does.

Turning on is gradual
---------------------

Below threshold the current does not stop. It falls tenfold for every
:math:`(kT/q) \ln 10`, 60 mV at room temperature, of change in the surface
potential, because the electron concentration at the surface is
exponential in that potential [HV-MIT-6012-L8]_ (slide 8-10). The gate
reaches the surface through a divider of two capacitances in series: the
insulator, and the depletion region below it. The thick insulator has the
smaller capacitance, so the gate controls the surface weakly, and the gate
voltage needed per tenfold change is much larger: about 320 mV with Metal1
and 1.4 V with Metal5 on substrate at :math:`1.2 \times 10^{15}`
cm\ :sup:`-3`
(`calc.py <https://github.com/mithro/evampire/blob/main/docs/high-voltage/calc.py>`__,
section 7). A sensor whose output is a current above threshold is not
affected. A sensor that has to switch hard on and off within a small
voltage window needs gain after it.

The current above threshold
---------------------------

With its drain a volt or so above its source, the transistor works in its
linear region [HV-MIT-6012-L10]_ (slide 10-3):

.. math::

   I_\text{D} = \frac{W}{L} \mu_\text{n} C_\text{ox}
     \left(V_\text{G} - \frac{V_\text{DS}}{2} - V_\text{T}\right)
     V_\text{DS}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`I_\text{D}`
     - Drain current
     - A
   * - :math:`W/L`
     - Width of the channel divided by its length
     - —
   * - :math:`\mu_\text{n}`
     - Mobility of electrons in the inversion layer, taken as 400 as an
       illustration
     - cm²/(V·s)
   * - :math:`V_\text{G}`
     - Gate voltage above the source
     - V
   * - :math:`V_\text{DS}`
     - Drain voltage above the source
     - V

For Metal5, with :math:`W/L = 10`, the gate at 57 V and the drain at 1 V:

.. math::

   I_\text{D} &= 10 \times 400 \times 5.80 \times 10^{-10} \\
     &\quad \times (57 - 0.5 - 26.5) \times 1 \\
     &= 70\ \mu\text{A}

The same transistor with its gate on Metal1 carries 604 µA
(`calc.py <https://github.com/mithro/evampire/blob/main/docs/high-voltage/calc.py>`__,
section 7). The thick insulator weakens the gate, but the large gate
voltage makes up much of it, so currents of tens to hundreds of microamps
are available from a modest width. The channel needs to be long compared
with the insulator thickness, so that the gate rather than the drain
controls it. How long is a question for measurement.

The sensed node carries no DC current, since the gate is an insulator. It
carries only the charge of the plate's capacitance: 58 fF for a plate
100 µm square on Metal5, and 293 fF on Metal1.

What it can be used for
-----------------------

Detecting a voltage
   The transistor turns on when the sensed node crosses its threshold, with
   no divider drawing current. Five layers give five thresholds from one
   doping, about 5 V to 27 V on the lightest substrate estimate
   (:numref:`tab-hv-metal-vt`), so a set of transistors forms a coarse
   ladder of trip points. Since the thresholds are known only once
   measured, each needs calibration.
Measuring a voltage
   Above threshold the current rises in proportion to the gate voltage, so
   the transistor is a voltmeter that draws no current from the node. A
   calibration at two known voltages fixes the slope and the threshold.
Shifting a signal down
   A circuit sitting tens of volts above the substrate can pass a logic
   signal down to ground-referenced circuits through two metal-gate
   transistors. One gate follows the signal and the other its complement.
   Because the current in the linear region is linear in the gate voltage,
   the difference between the two currents is
   :math:`(W/L)\,\mu_\text{n} C_\text{ox}\,\Delta V\,V_\text{DS}`,
   whatever the floating circuit's voltage. With Metal1, a 5 V swing,
   :math:`W/L = 10` and 1 V on the drains, it is 58.6 µA at every floating
   voltage from 10 V to 40 V
   (`calc.py <https://github.com/mithro/evampire/blob/main/docs/high-voltage/calc.py>`__,
   section 7). Matched plates also cancel most of the charge in the
   insulator. The floating circuit must stay above both thresholds.

A signal travelling up, from ground to a floating circuit such as the
high-side gate driver on :ref:`conv-gate-drive`, needs the mirror image:
P+ source and drain in the floating circuit's N-well, under a plate driven
from ground. That transistor sits in the floating well, so the well's own
isolation from the substrate, the subject of :doc:`junctions` and
:doc:`grading`, still limits it. Capacitive coupling across an insulator
(:doc:`dielectric`) is the alternative in that direction.

Alternatives for sensing a high voltage
---------------------------------------

A resistor divider sets a voltage proportional to the node, but draws
current all the time: 57 µW at 1 µA (:doc:`grading`). A capacitor divider
onto the polysilicon gate of a standard transistor draws no current but
holds no DC voltage, because the charge on the node between the
capacitors leaks away and its starting value is unknown. A stack of
junction devices meets the substrate limit on :doc:`substrate`. The
metal-gate transistor gives a DC reading with no current from the node, at
the cost of a threshold that has to be measured. Its open questions are on
:doc:`routes`.
