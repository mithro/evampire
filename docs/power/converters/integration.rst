On-chip converter parts
=======================

This page describes the steps by which more of each converter moves onto
evampire, and what each step needs from the
`gf180mcu <https://gf180mcu-pdk.readthedocs.io/>`_ process. The first
version keeps the gate drivers and power transistors external
(:ref:`requirements`, :doc:`first-version`). The full design moves the
gate drivers on chip, and then the power transistors
(:numref:`tab-power-board-configs`).

The steps are explored by building and measuring them: a design simulated
with the gf180mcu models, then test structures on a wafer.space run, then a
board. Commercial parts and published chips appear below as reference
examples of what has been built elsewhere, not as evidence of what a
gf180mcu design will achieve.

Process documentation
---------------------

Three kinds of fact bear on each step, and they are kept apart here.

Ratings of the standard devices
   The foundry's continuous operating limits for long life
   (:numref:`tab-conv-gf180-ratings`).
Documented physical limits of the layers
   Breakdown voltages and current limits from the process documentation
   (:numref:`tab-conv-gf180-limits`). They are higher than the ratings; a
   design that works between the two needs its own reliability analysis.
What custom structures could reach
   Stacked or cascoded devices, custom drain-extended devices and other
   structures not in the device library, with published results from
   other processes as reference examples (:ref:`conv-custom`).

.. list-table:: Continuous ratings of standard gf180mcu devices
   :name: tab-conv-gf180-ratings
   :header-rows: 1
   :widths: 40 25 35

   * - Device
     - Rating (V)
     - Source
   * - Thin-oxide MOSFETs, gate to any node, DC
     - 3.3 nominal, 3.63 maximum
     - [CONV-GF180-DRM-14]_ (Sections 14.1.2 and 14.1.4.2)
   * - Thick-oxide MOSFETs, gate to any node, DC
     - 5 or 6 nominal, 6.5 or 6 maximum
     - [CONV-GF180-DRM-14]_ (Sections 14.1.2 and 14.1.4.2)
   * - 10 V LDNMOS and LDPMOS (drain extended)
     - 10
     - [CONV-GF180-EP-8]_ (Sections 8.1 and 8.2)
   * - MIM capacitor, 1 fF/µm² option
     - 20 maximum operating
     - [CONV-GF180-EP-MIM]_ (Section 6.2 b)
   * - MIM capacitor, 1.5 and 2 fF/µm² options
     - 10 and 6.6 maximum operating
     - [CONV-GF180-EP-MIM]_ (Section 6.2 a and c)

Supply and drain voltages may exceed the nominal value by 10 %
[CONV-GF180-DRM-14]_ (Section 14.1.2). The LDNMOS's well "share[s] the same
potential with P-substrate" [CONV-GF180-LDMOS]_ (Section 10.12.1), so its
source and body sit at the substrate voltage.

.. list-table:: Documented breakdown and current limits of gf180mcu
   :name: tab-conv-gf180-limits
   :header-rows: 1
   :widths: 46 30 24

   * - Layer or junction
     - Limit
     - Source
   * - Gate oxide, 3.3 V devices
     - 7 V minimum (8.8 V typical)
     - [CONV-GF180-EP-5]_ (Section 5.4)
   * - Gate oxide, 6 V devices
     - 12 V minimum (16 V typical)
     - [CONV-GF180-EP-5]_ (Section 5.4)
   * - N+ to p-well, 6 V NMOS
     - 8.5 V minimum (11 V typical)
     - [CONV-GF180-EP-5]_ (Section 5.5)
   * - N-well to substrate
     - 10 V minimum (14 V typical)
     - [CONV-GF180-EP-5]_ (Section 5.5)
   * - LDNMOS drain to source
     - 13.2 V minimum (14.5 V typical)
     - [CONV-GF180-EP-8]_ (Section 8.1)
   * - Vertical PNP, collector to emitter
     - 10 V minimum (15 V typical)
     - [CONV-GF180-EP-5]_ (Section 5.8)
   * - MIM dielectric, 1 fF/µm²
     - 20 V minimum (40 V typical)
     - [CONV-GF180-EP-MIM]_ (Section 6.2 b)
   * - Metal line, Metal 1 to top minus 1, 85 °C
     - 2.09 mA/µm
     - [CONV-GF180-DRM-EM]_ (Table 14.3)
   * - Top metal 30 kÅ, 85 °C
     - 16.52 mA/µm
     - [CONV-GF180-DRM-EM]_ (Table 14.3)
   * - Contact or via, 85 °C
     - 0.58 mA each
     - [CONV-GF180-DRM-EM]_ (Table 14.4)

The process also has a deep n-well layer [CONV-GF180-DRM-4]_ (Section 4.1).
The breakdown of the deep n-well to the substrate, and of the field oxide
under poly and metal to the substrate, are listed as open questions below;
they decide how high above the substrate an isolated circuit can sit.

Control only
------------

evampire generates the PWM signals and senses the converters; external
gate drivers switch external transistors (:doc:`first-version`). This
needs from the process only what evampire uses elsewhere:

* standard logic cells for the PWM counters and control, and fast cells,
  standard or custom, for the delay line and dead-time generation;
* custom analogue blocks: comparators, a DAC, an ADC and a voltage
  reference, because the PDK's IP blocks are only I/O cells and SRAM
  [CONV-GF180-IP]_;
* 5 V I/O to drive the gate driver inputs and receive the sensed signals.

For reference, the UCC27211 half-bridge driver's inputs accept logic levels
and tolerate −10 V to 20 V [CONV-UCC27211]_ (Features).

Gate drivers on chip
--------------------

A gate driver charges and discharges the power transistor's gate quickly.
The current it must supply follows from the gate charge and the switching
time:

.. math::

   I_\text{drive} = \frac{Q_g}{t_\text{sw}},
   \qquad
   W = \frac{I_\text{drive}}{I_\text{dsat}}

with the symbols in :numref:`tab-conv-sym-drive`. A 20 nC gate switched in
20 ns needs 1 A. With the documented saturation current of the 6 V NMOS,
570 µA/µm typical and 480 µA/µm minimum
[CONV-GF180-EP-2]_ (Section 2.0), the pull-down transistor would be
1754 µm to 2083 µm wide. For reference, the LM5177's integrated drivers have
pull-down resistances of about 0.6 Ω and pull-up resistances of 1.3 Ω to
1.6 Ω [CONV-LM5177]_ (Section 5.5).

.. list-table:: Symbols for gate drive
   :name: tab-conv-sym-drive
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`I_\text{drive}`
     - Average gate drive current during a transition
     - A
   * - :math:`Q_g`
     - Gate charge of the power transistor
     - C
   * - :math:`t_\text{sw}`
     - Time allowed for the transition
     - s
   * - :math:`W`
     - Width of the driver transistor
     - µm
   * - :math:`I_\text{dsat}`
     - Saturation current per µm of width
     - A/µm

Gate drive voltage
   gf180mcu's thick-oxide devices allow 6 V across the gate oxide. Power
   transistors made for a 5 V gate drive ("logic level") suit this
   directly. For reference, the LM5177 and LT8390 drive their external
   transistors from about 5 V supplies [CONV-LM5177]_ (Section 5.3)
   [CONV-LT8390]_ (Pin Functions), while the UCC27211 runs from 8 V to 17 V
   [CONV-UCC27211]_ (Features). A higher gate drive from evampire would
   need stacked devices.

Low-side drivers
   Their sources are at ground, so they need only the standard 5 V or 6 V
   devices. For reference, the open-source gf180-gate-driver project is
   designing a level shifter from 3.3 V logic to a 5 V to 6 V drive rail
   for an external transistor in gf180mcu [CONV-GF180-GATE-DRIVER]_.

High-side drivers
   A high-side driver floats on the switch node, which swings up to 57 V
   every period; its supply sits a further 5 V or so above it, so up to
   62 V above the substrate. This is a continuous, periodic stress, present
   for the on time of every period, not a transient.

   A floating circuit in
   a standard n-well relies on the n-well to substrate junction, whose
   documented breakdown is 10 V minimum (:numref:`tab-conv-gf180-limits`).
   A high-side driver for a 57 V switch node on evampire therefore uses
   another isolation structure: a deep n-well, if its breakdown is high
   enough; more than one junction in series; or devices built in
   polysilicon, which has no junction to the substrate.

   For reference, a
   36 V charge pump has been built in nanometre-scale bulk CMOS
   [CONV-ISMAIL2017]_ (Title), and a charge pump with polysilicon diodes
   in low-voltage bulk CMOS [CONV-KER2007]_ (Title). For a lower switch
   node, such as a converter running
   from a bus of 6 V or less, the standard devices suffice.

Bootstrap supply
   The bootstrap diode blocks the input voltage while the switch node is
   high, so it needs the same voltage capability as the level shifter.
   The bootstrap capacitor (:ref:`conv-gate-drive`), tens of nanofarads,
   stays external.

Level shifter
   Moves the control signal from ground to the floating driver, holding off
   up to 57 V. Options are a custom drain-extended device that holds the
   voltage between its drain and source, a stack of devices, or capacitive
   coupling through capacitors in series. A stack of 1 fF/µm² MIM
   capacitors, each rated 20 V, needs at least
   :math:`\lceil 62 / 20 \rceil = 4` in series; their bottom plates sit over
   field oxide, whose breakdown is one of the open questions. For
   reference, level shifters for 50 V converters have been built in a
   180 nm BiCMOS process with high-voltage devices, with 1.45 ns delay
   [CONV-LUTZ2018]_ and with 5 ns delay at 20 V/ns [CONV-WITTMANN2014]_.

Power transistors on chip
-------------------------

A power transistor's on-resistance falls with its width. From the
documented linear current of the 10 V LDNMOS, 26.8 µA/µm at 6 V gate and
0.1 V drain [CONV-GF180-EP-8]_ (Section 8.1):

.. math::

   R_\text{on} \, W &= \frac{V_\text{ds}}{I_\text{dlin}}
                     = \frac{0.1}{26.8 \times 10^{-6}} \\
                   &= 3730 \ \Omega \, \mu\text{m} \\
                   &= 3.73 \ \Omega \, \text{mm}

with the symbols in :numref:`tab-conv-sym-ron`. A 100 mΩ switch needs
:math:`W = 3.73 / 0.1 = 37.3` mm of gate width. Its area is
:math:`A = W \, a`, where :math:`a` is the layout area per µm of width; for
an assumed :math:`a` of 2 µm to 5 µm the area is 0.07 mm² to 0.19 mm².

.. list-table:: Symbols for on-resistance and area
   :name: tab-conv-sym-ron
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`R_\text{on}`
     - On-resistance
     - Ω
   * - :math:`W`
     - Total gate width
     - µm
   * - :math:`V_\text{ds}`, :math:`I_\text{dlin}`
     - Drain voltage and drain current per µm in the linear region
     - V, A/µm
   * - :math:`A`, :math:`a`
     - Area, and area per µm of width
     - µm², µm
   * - :math:`n`
     - Number of devices in series
     - none

Voltage
   The LDNMOS is rated 10 V and breaks down at 13.2 V minimum, so it
   cannot block 57 V alone. A series stack of :math:`n` devices shares the
   voltage, at least :math:`\lceil 57 / 10 \rceil = 6`. For the same total
   resistance each device must be :math:`n` times wider, so the total width
   grows as :math:`n^2`: 6 devices for 100 mΩ need 224 mm each, 1343 mm in
   total. The LDNMOS body is tied to the substrate, so the upper devices of
   a stack need a custom device in an isolated well, with the same isolation
   question as the high-side driver.
Current
   At 85 °C, the Type 4 power sourcing equipment current of 1.731 A needs
   105 µm of 30 kÅ top metal, 828 µm of a lower metal, or 2985 contacts;
   5 A of USB current needs 303 µm of top metal and 8621 contacts
   (:numref:`tab-conv-gf180-limits`).
Heat
   1.731 A in 100 mΩ dissipates 0.30 W, and 5 A in 20 mΩ 0.5 W, in the
   die.
Lower voltages
   evampire's own low-voltage supplies, converted from 6 V or less, are
   within the ratings of the standard thick-oxide devices, and a converter
   working below 10 V is within the LDMOS rating.

.. _conv-custom:

Custom devices and reference examples
-------------------------------------

The standard devices do not set the limit of what can be built. These custom
structures are options for each step:

Custom power-transistor layouts
   Layouts that minimise the area per width and the metal resistance for
   the LDMOS or the 6 V devices.
Custom drain-extended or stacked devices
   For reference, drain-extended NMOS and PMOS made in a 0.18 µm logic CMOS
   process without process changes reach a breakdown above 10 V with the
   core gate oxide [CONV-MITROS2001]_ (Abstract), and high-voltage devices
   have been designed in a fully implanted twin-well CMOS process
   [CONV-DOSSANTOS2003]_ (Title). Stacked low-voltage transistors drive 3 times the nominal
   supply in 0.25 µm CMOS [CONV-SERNEELS2005]_ (Abstract) and switch a
   3.5 V to 5.5 V buck converter with three stacked 2.5 V devices in 65 nm
   CMOS [CONV-PASHMINEH2016]_ (Abstract). A class-D amplifier in standard
   1.8 V and 3.3 V 0.18 µm CMOS switches a 10 V output with stacked devices
   from a boosted supply [CONV-SERNEELS2012]_ (Title). A cascoded
   buck converter in
   0.18 µm CMOS converts 5.4 V to 0.9 V in simulation [CONV-KURSUN2004]_
   (Abstract).
Parasitic bipolar transistors
   The process documents a vertical PNP transistor
   [CONV-GF180-EP-5]_ (Section 5.8). Bipolar transistors serve as voltage
   references, temperature sensors, current sensing and clamps.
Custom fast logic cells
   For the delay line and dead-time generation of the PWM generator, where
   standard cells are too coarse or too slow.
Isolated circuits above the substrate
   In bulk silicon the top of a stack still sits at its full voltage above
   the substrate, so some junction or dielectric holds that voltage
   continuously. The charge pumps of [CONV-ISMAIL2017]_ and
   [CONV-KER2007]_ are reference examples of bulk CMOS circuits built for
   this. A gf180mcu structure for 57 V is established by test structures
   on a wafer.space run.

Process needs of each step
--------------------------

:numref:`tab-conv-process-needs` lists what each integration step needs
from the gf180mcu process.

.. list-table:: Process needs for each integration step
   :name: tab-conv-process-needs
   :header-rows: 1
   :widths: 22 39 39

   * - Step
     - Documented and available
     - To be established
   * - First version: control
     - Standard cells; 3.3 V and 5 V devices; 5 V I/O cells
     - Custom comparators, ADC, DAC and reference; delay-line resolution
   * - Low-side gate drivers
     - 6 V devices; their saturation current
     - Driver design and its switching speed with the gf180mcu models
   * - High-side gate drivers and level shifters
     - N-well to substrate 10 V minimum; MIM 20 V rating
     - Breakdown of deep n-well and field oxide to substrate; a custom
       level-shifting device to 57 V
   * - Power transistors below 10 V
     - 10 V LDMOS; its linear current; metal current limits
     - Layout area per width; switching loss
   * - Power transistors to 57 V
     - None beyond the 10 V LDMOS
     - A custom drain-extended or stacked device in an isolated well,
       characterised on a test chip

Open questions
--------------

* The breakdown voltage of the deep n-well to the substrate, and of field
  oxide under poly and metal, in gf180mcu; established with test
  structures on a wafer.space run or from foundry data.
* Which optional layers (LDMOS, MIM option, deep n-well) are available on
  wafer.space runs.
* The gate drive voltage evampire uses, and so which external power
  transistors suit it.
* The switching speed and drive strength of an on-chip driver, from a design
  simulated with the gf180mcu models.
* The on-resistance per area of a custom power transistor layout, from
  layout and extraction, then measurement.
* Whether isolated circuits for high-side drivers sit on evampire, on a
  second die, or stay external.
* The power the die can dissipate in its package, which limits on-chip
  power transistors.
