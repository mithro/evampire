.. _poe-pd-controller:

Powered-device controller
=========================

This page describes the circuit blocks that meet the
:doc:`powered-device requirements <powered-device>`, using commercial
controller chips as reference examples.

Controller blocks
-----------------

:numref:`fig-poe-pd-controller` shows the blocks. All of them work at the
cable voltage, up to 57 V, and all voltages inside are measured from the
negative output of the bridges, VSS. For reference, commercial controllers
are rated to 100 V: the TPS2372 has a 100 V isolation switch and the LT4275
a 100 V absolute maximum input [POE-TPS2372]_ [POE-LT4275]_ (Absolute
Maximum Ratings).

.. _fig-poe-pd-controller:

.. graphviz:: pd-controller.dot
   :caption: The blocks of a powered-device controller, with the isolation
             switch between the load return and VSS.
   :alt: Block diagram. The bridge outputs feed window comparators and the
         isolation switch. A reference sets the comparator thresholds. The
         comparators and thermal shutdown feed state logic, which turns on
         the signature switch, the mark-event load, the class current
         regulator and the isolation switch, and drives the power-good and
         assigned-class outputs. The signature switch connects an external
         24.9 kΩ resistor and the regulator an external class resistor. The
         isolation switch connects the input capacitor and input converter
         through the return node RTN. The status outputs go to evampire.
   :align: center

Signature switch
   Connects the 24.9 kΩ resistor while the input is in the detection range.
   For reference, the TPS2378 connects it between about 1.4 V and 10.9 V
   and disconnects it above that range to save power. Pulling its DEN pin
   low also turns the isolation switch off, so the board can refuse or drop
   the power [POE-TPS2378]_ (Detailed Description).

Mark-event load
   A lower resistance connected in parallel with the signature during mark
   events, so that the signature is invalid.

Class current regulator
   Holds a fixed voltage across an external resistor while the input is in
   the class range, so that the resistor sets the current. It is off above
   the class range and during thermal shutdown [POE-TPS2378]_ (Detailed
   Description).

Window comparators
   Compare the input voltage with thresholds placed in the gaps between the
   ranges of :numref:`tab-poe-steps`. Hysteresis keeps them from chattering
   on noise. :numref:`tab-poe-tps2372-cmp` gives the thresholds of one
   controller as a reference example.

State logic
   Combines the comparator outputs, counts class events, selects the class
   signature for each event and latches the assigned class.

Reference
   Sets the thresholds and the class voltage over the junction temperature
   range, −40 °C to 125 °C for the TPS2372 [POE-TPS2372]_ (Recommended
   Operating Conditions). A
   :wikipedia:`bandgap reference <Bandgap_voltage_reference>` is the usual
   way to build it.

Isolation switch
   An N-channel MOSFET that keeps the input converter and its capacitor
   disconnected until the turn-on voltage, then charges the capacitor at a
   limited current, then stays fully on with a higher current limit as
   overload protection. :numref:`tab-poe-iso-switch` gives two reference
   examples.

Power good and assigned class
   :wikipedia:`Open-drain <Open_collector>` outputs that tell the converter
   it may start and report the assigned class. :doc:`startup` describes how
   evampire uses them.

Thermal shutdown
   Turns the isolation switch and the class regulator off when they
   overheat, at 158 °C typical on the TPS2372 [POE-TPS2372]_ (Electrical
   Characteristics).

Input protection
   A :wikipedia:`transient-voltage suppressor
   <Transient-voltage-suppression_diode>` across the bridge outputs limits
   surges from the cable. For reference, Texas Instruments recommends an
   SMAJ58A for the TPS2372 [POE-TPS2372]_ (Application and
   Implementation). :doc:`hv-limits`
   describes the surge.

Class current
-------------

The regulator holds :math:`V_\text{CLS}` across the class resistor, so:

.. math::

   I_\text{class} = \frac{V_\text{CLS}}{R_\text{CLS}} + I_\text{bias}

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`V_\text{CLS}`
     - Voltage held across the class resistor
     - V
   * - :math:`R_\text{CLS}`
     - Class resistor
     - Ω
   * - :math:`I_\text{bias}`
     - Controller's own supply current during classification
     - mA
   * - :math:`I_\text{class}`
     - Current drawn from the cable
     - mA

For class signature 4, ignoring :math:`I_\text{bias}`, with the TPS2378
(2.5 V, 63.4 Ω [POE-TPS2378]_) and the LT4275 (1.40 V, 34.8 Ω
[POE-LT4275]_):

.. math::

   I_\text{TPS2378} &= \frac{2.5\ \text{V}}{63.4\ \Omega} = 39\ \text{mA} \\
   I_\text{LT4275} &= \frac{1.40\ \text{V}}{34.8\ \Omega} = 40.2\ \text{mA}

Both land in the 36 mA to 44 mA window of class signature 4
(:numref:`tab-poe-class-sig`). The margin of about 4 mA on each side covers
the resistor tolerance, the regulator's error and :math:`I_\text{bias}`.

Comparator thresholds
---------------------

Each comparator threshold sits in a gap between two neighbouring ranges of
:numref:`tab-poe-steps`, so that noise within a range does not cross it.

.. list-table:: Typical comparator thresholds of the TPS2372
   :name: tab-poe-tps2372-cmp
   :header-rows: 1
   :widths: 40 30 30

   * - Comparator
     - Threshold (V)
     - Hysteresis (V)
   * - Class range, lower edge (rising)
     - 12.5
     - 1.6
   * - Class range, upper edge (rising)
     - 22
     - 0.78
   * - Mark reset (falling)
     - 3.9
     - none
   * - Turn on (rising)
     - 38.1
     - 6.1

The thresholds are from [POE-TPS2372]_ (Electrical Characteristics). The
lower class edge, 12.5 V, falls in the 10.1 V to 14.5 V gap of
:clause:`Table 145-25 <145>`. The mark reset, 3.9 V, falls in the 2.81 V
to 6.9 V gap.

Isolation switch
----------------

The isolation switch limits the inrush current while it charges the input
capacitor, then allows a higher operating current.
:numref:`tab-poe-iso-switch` gives two reference examples.

.. list-table:: Isolation switches of two controllers
   :name: tab-poe-iso-switch
   :header-rows: 1
   :widths: 28 24 24 24

   * - Controller
     - On resistance (Ω)
     - Inrush limit (mA)
     - Operating limit (A)
   * - TPS2378
     - 0.42
     - 140
     - 1
   * - TPS2372-4
     - 0.1
     - 335
     - 2.2

The values are from [POE-TPS2378]_ and [POE-TPS2372]_ (Electrical
Characteristics). If the load pulls the switch out of full conduction for
longer than a filter time, 800 µs on the TPS2378, the controller falls back
to the inrush limit. For reference, the LT4275 drives an external MOSFET
instead and sets the inrush current with a capacitor on the gate
[POE-LT4275]_ (Applications Information).

Commercial controllers
----------------------

:numref:`tab-poe-pd-chips` lists commercial powered-device controllers as
reference examples. They show which blocks are commonly combined in one chip.

.. list-table:: Example powered-device controller chips
   :name: tab-poe-pd-chips
   :header-rows: 1
   :widths: 25 25 20 30

   * - Part
     - Maker
     - Highest type
     - Isolation switch
   * - TPS2378
     - Texas Instruments
     - 2
     - Internal
   * - TPS2372-4
     - Texas Instruments
     - 4
     - Internal
   * - TPS23753A
     - Texas Instruments
     - 1
     - Internal
   * - LT4275A
     - Analog Devices
     - 2
     - External
   * - LTC4269-1
     - Analog Devices
     - 2
     - Internal
   * - NCP1096
     - onsemi
     - 4
     - Internal

The rows come from [POE-TPS2378]_, [POE-TPS2372]_, [POE-TPS23753A]_,
[POE-LT4275]_, [POE-LTC4269-1]_ and [POE-NCP1096]_. The TPS23753A and
LTC4269-1 also include the controller of an isolated input converter. The
LT4275A also accepts Analog Devices' LTPoE++ classification up to 90 W
[POE-LT4275]_. For reference, the Microchip PD70224 replaces the two diode
bridges with MOSFETs [POE-PD70224]_.

Input converter
---------------

After the isolation switch the board has a supply of 30 V to 57 V. The
input converter brings it down to the board's power bus. Whether it is
isolated depends on the isolation route (:doc:`isolation`).
:doc:`../converters/index` describes the converter and its control.

Open questions
--------------

* Which of these blocks are built on evampire, by function
  (:doc:`hv-options`).
* Whether the input converter is isolated (:doc:`isolation`).
