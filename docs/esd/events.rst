.. _esd-events:

ESD tests and what reaches the pin
==================================

This page describes the electrostatic discharge (ESD) tests that chips and
products are rated against. It then shows why a test at thousands of volts
leaves only a few volts on a pin whose protection conducts.

The chip tests and the product test differ
------------------------------------------

An ESD rating names a test and a voltage. The voltage is the voltage to
which the tester charges a capacitor, which then discharges through a
resistor into the pin. :numref:`tab-esd-tests` lists the tests that this
section uses.

.. list-table:: ESD tests used in this section
   :name: tab-esd-tests
   :header-rows: 1
   :widths: 26 18 16 40

   * - Test
     - Capacitor (pF)
     - Resistor (Ω)
     - What it imitates
   * - :term:`Human body model` (:std:`JS-001`)
     - 100
     - 1500
     - A charged person touching a pin while handling a chip
   * - :term:`Charged device model`
     - none
     - none
     - A charged chip touching a grounded metal surface
   * - :std:`IEC 61000-4-2`
     - 150
     - 330
     - A charged person touching a finished product, through a metal tool

The human body model values are from the ESD Association
([ESD-ESDA-P5]_, "Human Body Model (HBM) Testing") and the IEC values from
Renesas TB505 ([ESD-TB505]_, Figure 1). In the charged device model the
chip itself is the charged capacitor. The discharge often lasts less than
1 ns, with a peak of several tens of amperes ([ESD-ESDA-P5]_, "Charged
Device Model (CDM) Testing").

The human body model and charged device model rate a chip for handling in
a factory with ESD controls. :std:`IEC 61000-4-2` rates a finished product
in use, where nobody takes precautions ([ESD-TND410]_, page 3). A
connector pin wired straight to a chip, with no protection between, faces
the IEC test.

The IEC test has two methods. In contact discharge the generator tip
touches the product before the discharge. In air discharge the charged tip
approaches until a spark jumps. :numref:`tab-esd-iec-levels` gives the
test levels. Each level counts as equivalent between the two methods, so
level 4 is 8 kV contact or 15 kV air ([ESD-TND410]_, page 3 and Table 2).

.. list-table:: :std:`IEC 61000-4-2` test levels ([ESD-TND410]_, Table 2)
   :name: tab-esd-iec-levels
   :header-rows: 1
   :widths: 20 40 40

   * - Level
     - Contact discharge (kV)
     - Air discharge (kV)
   * - 1
     - 2
     - 2
   * - 2
     - 4
     - 4
   * - 3
     - 6
     - 8
   * - 4
     - 8
     - 15

A ±15 kV figure on a datasheet can name either of two tests. In
:std:`IEC 61000-4-2` it is level 4 air discharge, the same severity as 8 kV
contact discharge. Some parts also quote ±15 kV human body model, such as
the bus pins of the TRS3232E ([ESD-TRS3232E]_, section 5.2). The name of
the test, not the voltage, says how severe it is.

The test voltage appears across the resistor, not the pin
---------------------------------------------------------

At the moment of discharge, the tester's capacitor, its resistor and the
pin form one loop. The protection on the pin starts to conduct at a few
volts. From then on, the pin voltage is small, and almost the whole test
voltage lies across the tester's resistor. The resistor therefore sets the
current:

.. math::

   I_\text{peak} = \frac{V_\text{test} - V_\text{pin}}{R_\text{test}}
   \approx \frac{V_\text{test}}{R_\text{test}}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`I_\text{peak}`
     - Peak current into the pin
     - A
   * - :math:`V_\text{test}`
     - Voltage the tester's capacitor is charged to
     - V
   * - :math:`V_\text{pin}`
     - Voltage on the pin while the protection conducts
     - V
   * - :math:`R_\text{test}`
     - Tester's series resistor
     - Ω

The approximation holds while :math:`V_\text{pin}` is much smaller than
:math:`V_\text{test}`. For a 2 kV human body model test with a pin held at
10 V:

.. math::

   I_\text{peak} = \frac{2000\ \text{V} - 10\ \text{V}}{1500\ \Omega}
   = 1.33\ \text{A}

The 10 V on the pin changes the current by 0.5 %. The ESD Association gives
the same peak, 0.67 A per kilovolt of test voltage ([ESD-ESDA-P5]_).

The IEC network has about a fifth of the resistance, and its fast first peak
is higher still: 3.75 A per kilovolt, 30 A at 8 kV ([ESD-TB505]_,
Figure 2). An IEC contact discharge at 2 kV gives a higher peak current
than a human body model test at 8 kV ([ESD-TND410]_, Table 3).

The protection's job is to carry the current
--------------------------------------------

A kilovolt test does not put kilovolts on the chip. It puts amperes through
the chip for a short time, and the chip survives if two conditions hold:

#. Every device on the current path carries its share of the current
   without overheating. The gf180mcu design manual gives this limit as a
   current per micrometre of device width (:ref:`esd-limits`).
#. The voltage that the current develops across the protection stays below
   the breakdown voltage of every device it reaches, in particular the
   gate oxide of the input transistors.

This is how a process whose transistors are rated for 5 V survives a
2000 V test. :doc:`io-cells` shows the structures in the gf180mcu I/O cells
that do this, and :doc:`results-hbm` and :doc:`results-iec` simulate
them.

Most of the stored energy stays in the tester
---------------------------------------------

The energy stored in the tester's capacitor bounds the energy any test can
deliver:

.. math::

   E = \tfrac{1}{2} \times C_\text{test} \times V_\text{test}^2

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`E`
     - Energy stored in the tester's capacitor
     - J
   * - :math:`C_\text{test}`
     - Tester's capacitor
     - F

For the human body model at 2 kV,
:math:`E = 0.5 \times 100\ \text{pF} \times (2000\ \text{V})^2 = 0.2\ \text{mJ}`.
For the IEC network at 8 kV,
:math:`E = 0.5 \times 150\ \text{pF} \times (8000\ \text{V})^2 = 4.8\ \text{mJ}`.

Most of this energy heats the tester's resistor, because the resistor holds
almost all of the voltage. If the protection holds the pin at a steady
voltage while the capacitor discharges, the pin receives the capacitor's
whole charge at that voltage:

.. math::

   E_\text{pin} = V_\text{pin} \times C_\text{test} \times
   (V_\text{test} - V_\text{pin})
   \approx 2 \times \frac{V_\text{pin}}{V_\text{test}} \times E

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`E_\text{pin}`
     - Energy dissipated in the chip's protection
     - J

For the 2 kV human body model with the pin at 4 V (:doc:`results-hbm`),
:math:`E_\text{pin} = 4\ \text{V} \times 100\ \text{pF} \times 1996\ \text{V}
= 0.8\ \text{µJ}`, 0.4 % of the stored 0.2 mJ. The ESD Association names
the energy of the pulse as what usually causes failure in the human body
model test ([ESD-ESDA-P5]_, "Human Body Model (HBM) Testing"). That energy
arrives in a few hundred nanoseconds, so the protection devices must absorb
it without overheating, and their measured limits (:ref:`esd-limits`) are
for pulses of that length.
