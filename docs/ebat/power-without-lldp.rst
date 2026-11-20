.. _ebat-power-without-lldp:

Power over Ethernet without LLDP
================================

This page explains why ebat, which has no Ethernet data path, can request
at most class 3 on each pair set when it receives Power over Ethernet, and
gives the power that leaves for each operating mode. Supplying power is
not limited in this way.

Classes 4 and higher need LLDP
------------------------------

A :term:`powered device` asks for its :term:`class` during Physical Layer
classification, before the power is switched on
(:doc:`../power/poe/sequence`). After the Ethernet link is up, the two
ends can change the allocation by exchanging :term:`LLDP` frames
(:doc:`../power/poe/lldp`). IEEE 802.3 makes this exchange mandatory for
some powered devices and optional for others, as
:numref:`tab-ebat-lldp-needed` shows (:clause:`Table 145-19 <145>`,
:clause:`145.3.6`).

.. list-table:: Powered devices that must support LLDP
   :name: tab-ebat-lldp-needed
   :header-rows: 1
   :widths: 30 40 30

   * - Signature
     - Class requested
     - LLDP
   * - Single
     - 1 to 3
     - Optional
   * - Single
     - 4 to 8
     - Required
   * - Dual
     - 1 to 3 on both pair sets
     - Optional
   * - Dual
     - 4 or 5 on either pair set
     - Required

The older rules of :clause:`33` say the same for Type 2 powered devices,
which request class 4 and implement both two-event classification and
LLDP (:clause:`33.3.5`). LLDP frames are Ethernet frames, so a powered
device with no data path cannot take part. ebat therefore requests class 1,
2 or 3 on each pair set.

Two other routes give a powered device more than class 3, and ebat takes
neither of them:

Request class 4 or higher without LLDP
   This does not meet :clause:`145.3.6`, which uses "shall".
Keep a low-speed Ethernet link for LLDP only
   This is evampire's route, with its processor handling the LLDP frames
   (:ref:`req-forwarding`). ebat leaves out all Ethernet data circuits by
   definition (:ref:`req-ebat-no-data`).

A single signature gives 13 W
-----------------------------

A :term:`single-signature powered device` has one detection signature and
one class signature for both pair sets together. At class 3 it may draw 13 W
at its input (:numref:`tab-poe-classes`). Every type of power sourcing
equipment assigns class 3 after one class event (:numref:`tab-poe-events`),
so any power sourcing equipment gives this power.

.. _ebat-dual-signature:

Two signatures give 13 W on each powered pair set
-------------------------------------------------

A :term:`dual-signature powered device` presents an independent detection
signature on each pair set (:clause:`145.3.5`), and is classified on each
pair set separately (:clause:`Table 145-27 <145>`). At class 3 on a pair
set it may draw 13 W on that pair set (:clause:`Table 145-27 <145>`). The
power sourcing equipment allows for 14 W on that pair set at its own end
(:clause:`Table 145-11 <145>`).

Requesting class 3 on both pair sets keeps LLDP optional
(:numref:`tab-ebat-lldp-needed`), and gives:

* 26 W from power sourcing equipment that powers both pair sets, which
  Types 3 and 4 may do (:numref:`tab-poe-types`);
* 13 W from power sourcing equipment that powers one pair set, which
  includes every Type 1 and Type 2 device.

The cost is a second set of powered-device blocks on port A. Each pair set
needs its own polarity bridge, signature, class signature and isolation
switch (:doc:`../power/poe/pd-controller`), and the start-up sequencer
answers detection and classification on both. Whether port A presents a
single or a dual signature is an open question.

The power left in each mode
---------------------------

In each mode the software works out the power left for the outputs from
the power on the input port:

.. math::

   P_\text{out} = P_\text{in} \times \eta - P_\text{board}

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`P_\text{in}`
     - Power granted on the input port
     - W
   * - :math:`\eta`
     - Efficiency of the converters from the input port to the output port
     - none
   * - :math:`P_\text{board}`
     - Power the board itself uses
     - W
   * - :math:`P_\text{out}`
     - Power left for the output ports
     - W

The equation is the one on :ref:`power-translation`. ebat's own power,
the board's power and the converter efficiencies are all unknown, so the
examples use the illustrative values of the evampire pages they link to.
These are :math:`\eta` = 0.900 and :math:`P_\text{board}` = 3.10 W from
Ethernet to USB, and :math:`\eta` = 0.846 from Ethernet to Ethernet.
:numref:`tab-ebat-modes` gives the results for 13 W and 26 W on port A. The
script :download:`calc.py` recomputes every value on this page.

.. list-table:: The output for each input on port A, with illustrative
   efficiencies and board power
   :name: tab-ebat-modes
   :header-rows: 1
   :widths: 40 30 30

   * - Output
     - From 13 W
     - From 26 W
   * - USB Port Present PDP (W)
     - 8
     - 20
   * - USB fixed offers
     - 5 V at 1.60 A
     - 5 V at 3.00 A, 9 V at 2.22 A
   * - Highest class on port B
     - 2
     - 3
   * - Board power at that class, up to (W)
     - 4.3
     - 8.0

Ethernet in, USB out
   With both pair sets powered:

   .. math::

      P_\text{out} = 26\ \text{W} \times 0.900 - 3.10\ \text{W} = 20.3\ \text{W}

   The USB port reports 20 W, rounded down to 1 W, as its Port Present PDP.
   With Power over Ethernet as its only input, its Port Maximum PDP, the
   most it will ever provide, is also 20 W. A source above 15 W must offer
   9 V, and may not offer 15 V unless its Port Maximum PDP is above 27 W
   (:numref:`tab-usbpd-pdp-voltages`).

   The 9 V current is
   :math:`20\ \text{W} / 9\ \text{V} = 2.22\ \text{A}`, rounded down to
   10 mA (:ref:`usbpd-pd-power-rules`). From 13 W the result is 8 W and a
   single 5 V offer, the class 3 row of :numref:`tab-usbpd-translation-examples`.

Ethernet in, Ethernet out
   The input converter and the high-voltage converter, assumed 90 % and
   94 % efficient, give :math:`\eta = 0.90 \times 0.94 = 0.846`. From 26 W
   that leaves :math:`26\ \text{W} \times 0.846 = 22.0\ \text{W}`. Class 3
   needs 14 W at the power sourcing equipment and class 4 needs 30 W
   (:numref:`tab-poe-classes`), so port B offers class 3 while the board
   uses no more than :math:`22.0\ \text{W} - 14\ \text{W} = 8.0\ \text{W}`.
   From 13 W, port B offers class 2, the class 3 row of
   :numref:`tab-poe-pass-through`.

USB in, Ethernet out
   This mode does not involve port A, so it is the same as on evampire
   (:numref:`tab-poe-usb-in`). Port B can offer up to class 8 from a large
   enough USB contract.

Port B changes its allocation only by classifying again
-------------------------------------------------------

As :term:`power sourcing equipment`, port B assigns a class by Physical
Layer classification, up to class 8 with 4-pair power
(:doc:`../power/poe/power-sourcing`). LLDP is optional for power sourcing
equipment (:clause:`145.5`), so ebat meets the standard without it. A
powered device on port B that requested class 4 or higher keeps the class
it was assigned, because no LLDP exchange changes it (:clause:`145.3.6`).

Without LLDP, the software can lower port B's allocation only by removing
the power and classifying the powered device again with fewer class events,
which interrupts the device (:doc:`../power/poe/sharing`). Autoclass, in
which the power sourcing equipment measures the powered device's real draw
shortly after power-on, is an extension of Physical Layer classification and
needs no LLDP (:clause:`145.2.8.2`). It is defined only for
single-signature powered devices. If the powered device supports it, ebat
can use it to allocate less than the full class power
(:doc:`../power/poe/translation`).

Open questions
--------------

* Whether port A presents a single signature or a dual signature.
* Which class, 1, 2 or 3, the start-up sequencer requests on each pair set.
* Whether port B uses autoclass when the powered device supports it.
