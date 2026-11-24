.. _poe-pse-sequencing:

Supplying power, sequenced in software
======================================

This page describes the circuit blocks of a power sourcing equipment port
whose detection and classification are sequenced by evampire's software,
the timing that the software must meet, and the 44 V to 57 V supply.

Software runs the sequence; hardware does the fast parts
--------------------------------------------------------

Software on evampire's processor runs the steps of :doc:`power-sourcing`:
it sets each test voltage or current, reads the measurements, decides, and
switches the power on (:ref:`req-power-control`). No external power
sourcing equipment controller is needed. The hardware provides the
measurements, the current limit and a fast switch-off that does not wait
for software (:doc:`monitoring`). :numref:`fig-poe-pse-channel` shows one
channel.

.. graphviz:: pse-controller.dot
   :name: fig-poe-pse-channel
   :caption: One power sourcing equipment channel, with the switch in the
             negative pair and the sequence run by evampire's software.
   :alt: Block diagram. The high-voltage converter feeds the positive pairs
         of the port. The negative pairs pass through a power MOSFET switch
         and a sense resistor. A detection and class source applies test
         signals to the port, and a voltage measurement reads the port
         voltage. A current measurement and a fast fault comparator read the
         millivolts across the sense resistor. The comparator can turn the
         gate drive off directly. The software on evampire reads both
         measurements, steps the detection and class source, and sets the
         current limit of the gate drive and current-limit loop.
   :align: center

With the switch in the negative pair, the sense resistor, the
measurements and the gate drive sit close to the supply return, and the
sense voltages are millivolts. Only the switch and the detection and class
source see the full port voltage. :doc:`hv-options` discusses which of the
blocks can be on evampire.

The blocks are:

Detection and class source
   Forces the detection currents or voltages, holds the port at 15.5 V to
   20.5 V for class events and at 7 V to 10 V for mark events, and limits
   the current in each step (:doc:`power-sourcing`). For reference, the
   TPS23881 holds the class voltage by running its external power MOSFET
   in a linear loop, so the heat of the class current is in the MOSFET
   [POE-TPS23881]_ (Detailed Description).

Voltage measurement
   Reads the port voltage for detection and for the power-on checks.

Current measurement
   Reads the current through the sense resistor for classification, power
   policing and the maintain power signature, with the accuracy derived on
   :doc:`power-sourcing`.

Gate drive and current-limit loop
   Drives the switch: off, in a linear loop at the limit the software sets,
   or fully on.

Fast fault comparator
   Turns the switch off on a short circuit without waiting for software.

Switch and sense resistor
   For reference, Texas Instruments recommends a 100 V MOSFET and a 0.2 Ω,
   1 % sense resistor for the TPS23881 [POE-TPS23881]_ (Application and
   Implementation).

The software has millisecond deadlines
--------------------------------------

The steps have time windows of a few milliseconds and longer
(:numref:`tab-poe-step-times`). :numref:`tab-poe-sw-timing` lists the
windows that the software must place its actions in.

.. list-table:: Time windows the software must meet
   :name: tab-poe-sw-timing
   :header-rows: 1
   :widths: 40 20 20 20

   * - Action
     - Earliest (ms)
     - Latest (ms)
     - Width (ms)
   * - End a mark event
     - 6
     - 12
     - 6
   * - End the first class event
     - 88
     - 105
     - 17
   * - End a later class event
     - 6
     - 20
     - 14
   * - End the inrush period
     - 50
     - 75
     - 25
   * - Remove power after the signature stops
     - 320
     - 400
     - 80
   * - Reach full power after detection
     - none
     - 400
     - 400

The windows come from :clause:`Table 145-14 <145>` and
:clause:`Table 145-16 <145>`. The narrowest is 6 ms wide. An action placed
in the middle of it with a timing error of up to ± 1 ms leaves 2 ms of
margin on each side, so a timer resolution and a response latency of 1 ms
or better meet every window. This is an estimate of the need; the
processor that meets it is open (:ref:`requirements-open-questions`).

Each measurement is read after the port settles: at least 6 ms into a class
event (:clause:`Table 145-14 <145>`, item 7), and after the detection
voltage settles to within 1 % (:clause:`145.2.6.2`). The software takes a
few readings per step, so its measurement rate is tens to hundreds of
readings per second per port.

For reference, commercial controllers do the same in firmware. The TPS23881
runs its sequences on an internal processor whose firmware the host loads
at start-up [POE-TPS23881]_ (Detailed Description). :numref:`tab-poe-pse-chips`
lists other commercial controllers.

.. list-table:: Example power sourcing equipment controller chips
   :name: tab-poe-pse-chips
   :header-rows: 1
   :widths: 25 25 20 30

   * - Part
     - Maker
     - Highest type
     - Two-pair ports
   * - TPS23881
     - Texas Instruments
     - 4
     - 8
   * - TPS2388
     - Texas Instruments
     - 2
     - 8
   * - TPS23861
     - Texas Instruments
     - 2
     - 4
   * - LTC4279
     - Analog Devices
     - 2
     - 1
   * - Si3474
     - Skyworks
     - 4
     - 8

The rows come from [POE-TPS23881]_, [POE-TPS2388]_, [POE-TPS23861]_,
[POE-LTC4279]_ and [POE-SI3474]_. A 4-pair port uses two of the two-pair
ports, one for each pair set. The LTC4279 runs a port without a host processor
[POE-LTC4279]_; the LTC4291-1 and LTC4292 pair carries its host link
across a transformer [POE-LTC4291]_.

The supply sits inside the output range
---------------------------------------

The port needs a supply inside the output range of its type
(:numref:`tab-poe-pse-voltage`). A value near 54 V, as in the TPS23881
application examples, leaves room above the 50 V or 52 V minimum for the
drop in the switch and sense resistor, and below 57 V for tolerance
[POE-TPS23881]_ (Application and Implementation). On an evampire board the
high-voltage converter makes it from the power bus
(:doc:`../converters/index`). Its ripple and noise must stay within the
limits on :doc:`monitoring`.

For reference, the TPS23881 examples put a 0.1 µF, 100 V capacitor and a
transient-voltage suppressor of at least 58 V standoff on each port, and a
fuse rated for at least 60 V DC [POE-TPS23881]_ (Application and
Implementation). The port capacitance during detection is limited to
520 nF (:clause:`Table 145-7 <145>`).

Two alternatives for the supply
-------------------------------

A switched-capacitor supply for low classes
   Classes 1 and 2 need at most 6.7 W at the power sourcing equipment
   (:numref:`tab-poe-classes`), 0.134 A at 50 V. A switched-capacitor
   converter, a :wikipedia:`charge pump <Charge_pump>` with no inductor,
   can multiply a bus voltage by a fixed ratio. A fixed ratio is efficient
   only when the output is close to that ratio times the input, so this
   suits a bus held at a fixed fraction of 54 V, for example 18 V for a
   ratio of 3. For reference, Ismail and others reach 36 V from a charge
   pump in 65 nm bulk CMOS [POE-Ismail2017]_. Whether the bus voltage and
   the capacitor voltage ratings allow it is an open question
   (:ref:`conv-alternatives`).

A 48 V USB supply used directly
   A USB Power Delivery source in the extended power range can supply a
   fixed 48 V (:pd:`Table 3.6`). Its tolerance is ± 5 %, plus 0.5 V during
   transitions (:pd:`Table 4.7`):

   .. math::

      V_\text{min} = 48\ \text{V} \times 0.95 - 0.5\ \text{V} = 45.1\ \text{V}

   .. list-table::
      :header-rows: 1
      :widths: 22 58 20

      * - Symbol
        - Meaning
        - Unit
      * - :math:`V_\text{min}`
        - Lowest 48 V supply voltage at the source
        - V

   45.1 V is above the 44 V minimum of Type 1 power sourcing equipment but
   below the 50 V of Types 2 to 4. During a peak current the source may
   fall to 90 %, 43.2 V (:pd:`Table 4.7`), and the USB cable and the switch
   drop more. So a 48 V input could feed a Type 1 port without a converter
   only if those drops and peaks are excluded; this is an open question.

Open questions
--------------

* The highest type port B supports, which sets the supply voltage range
  and the number of class events.
* Whether a switched-capacitor supply or a 48 V USB input is used for low
  classes.
* The detection method and measurement resolution, within the accuracy on
  :doc:`power-sourcing`.
