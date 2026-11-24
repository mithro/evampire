Power over Ethernet through the centre taps
===========================================

This page describes how :term:`Power over Ethernet` current passes through
the cable-side :term:`centre taps <centre tap>` of standard
:term:`magnetics`, and how the transformer keeps the data circuits out of
the way of detection and classification. The power circuits themselves are
described on :doc:`../../power/poe/index`.

.. _magnetics-poe-current:

Current through the centre taps
-------------------------------

Power over Ethernet sends direct current on the data pairs. The
:term:`power sourcing equipment` puts one polarity on both wires of one
pair and the other polarity on both wires of another pair. A pair then
carries no differential direct voltage, so the data is not disturbed. The
pairs used, two or all four, are described on :doc:`../../power/poe/index`.
The :term:`powered device` must accept power on either set of pairs in
either polarity, so it uses two :wikipedia:`bridge rectifiers
<Diode_bridge>` (:numref:`fig-magnetics-poe`).

In a transformer, the current enters at the cable-side centre tap and
splits into the two halves of the winding, flowing outward in opposite
directions. Their magnetic fields cancel, so the full current does not
bias the core. Only the difference between the two wires' currents, caused
by unequal wire resistance, biases it ([MAG-TPS2376H]_, section 9.2.1.2).

.. graphviz:: poe-centre-taps.dot
   :name: fig-magnetics-poe
   :caption: A powered device taking Power over Ethernet from the cable-side
             centre taps of standard magnetics.
   :alt: Block diagram: the transceiver connects to the circuit side of
         PoE-rated magnetics, whose cable side goes to the RJ45 pins. The
         four cable-side centre taps go in pairs to two bridge rectifiers,
         which both feed the powered-device interface and power converter.
         Each centre tap also connects to the 75 ohm common-mode
         termination through a 10 nanofarad blocking capacitor.
   :align: center

The termination resistors of :doc:`functions` connect to the same centre
taps. In a Power over Ethernet port each 75 Ω resistor needs a series
capacitor of about 10 nF to block the direct voltage ([MAG-ENT98]_,
section 3.9).

:numref:`tbl-magnetics-poe-numbers` gives the Power over Ethernet values
that the front end of a port must handle. :doc:`../../power/poe/index`
explains each of them.

.. list-table:: Power over Ethernet values that constrain the front end
   :name: tbl-magnetics-poe-numbers
   :header-rows: 1
   :widths: 40 12 12 12 24

   * - Quantity
     - Min
     - Max
     - Unit
     - Source
   * - Power sourcing equipment output voltage, Type 1
     - 44
     - 57
     - V
     - :clause:`Table 33-11 <33>`
   * - Power sourcing equipment output voltage, Type 4
     - 52
     - 57
     - V
     - :clause:`Table 145-16 <145>`
   * - Powered device input voltage, Class 1
     - 42.8
     - 57
     - V
     - :clause:`Table 145-29 <145>`
   * - Current one pair must carry, Class 8, with unbalance
     - 0.948
     -
     - A
     - :clause:`Table 145-16 <145>`, item 5
   * - Powered device detection resistance
     - 23.7
     - 26.3
     - kΩ
     - :clause:`Table 145-21 <145>`
   * - Powered device capacitance during detection
     - 50
     - 120
     - nF
     - :clause:`Table 145-21 <145>`
   * - Powered device series inductance during detection
     -
     - 100
     - µH
     - :clause:`Table 145-21 <145>`
   * - Classification voltage
     - 15.5
     - 20.5
     - V
     - :clause:`Table 145-14 <145>`

An empty cell means that the standard sets no limit on that side. The
Ethernet Alliance overview of IEEE 802.3bt gives the same voltages and the
same detection signature ([MAG-EA8023BT]_, tables 15 and 16).

.. _magnetics-poe-detection:

Detection and classification
----------------------------

Before it switches power on, power sourcing equipment detects a powered
device by its signature resistance and capacitance, measured between 2.7 V
and 10.1 V, and then classifies it (:clause:`Table 145-21 <145>`). At direct
voltages the transceiver is not connected to the cable at all, because the
transformer blocks direct current. The power sourcing equipment therefore
sees only the powered device's signature.

Anything that replaces the transformer must keep the data circuits within
the signature limits of :numref:`tbl-magnetics-poe-numbers`, including the
capacitance and series inductance. :doc:`without-transformer` works out
how much capacitance coupling capacitors add.
