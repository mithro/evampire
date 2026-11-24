.. _ebat-power-without-lldp:

Power over Ethernet without LLDP
================================

This page explains why ebat, which has no Ethernet data path, requests at
most class 3 when it receives Power over Ethernet, and gives the power that
leaves. Supplying power is not limited in this way.

Classes 4 and higher need LLDP
------------------------------

A :term:`powered device` asks for its :term:`class` during Physical Layer
classification, before the power is switched on
(:doc:`../power/poe/sequence`). After the Ethernet link is up, the two
ends can change the allocation by exchanging :term:`LLDP` frames
(:doc:`../power/poe/lldp`). evampire's power tables treat port A as a
:term:`single-signature powered device` (:numref:`tab-usbpd-class-power`).
For such a device, IEEE 802.3 makes this exchange mandatory from class 4, as
:numref:`tab-ebat-lldp-needed` shows (:clause:`Table 145-19 <145>`,
:clause:`145.3.6`).

.. list-table:: When a single-signature powered device must support LLDP
   :name: tab-ebat-lldp-needed
   :header-rows: 1
   :widths: 50 50

   * - Class requested
     - LLDP
   * - 1 to 3
     - Optional
   * - 4 to 8
     - Required

:clause:`33`, which defines Types 1 and 2, says the same for Type 2
powered devices. These request class 4 and implement both two-event
classification and LLDP (:clause:`33.3.5`). LLDP frames are Ethernet
frames, so a powered device with no data path cannot take part. ebat's
port A, the same circuit as evampire's, therefore requests class 1, 2 or 3.

Class 3 gives 13 W
------------------

At class 3 a powered device may draw 13 W at its input
(:numref:`tab-poe-classes`). Every type of power sourcing equipment assigns
class 3 after one class event (:numref:`tab-poe-events`), so any power
sourcing equipment gives this power.

From 13 W, ebat leaves the same power for its outputs as evampire does at
class 3. The evampire pages give it, with the same illustrative
efficiencies and board power:

* Ethernet in, USB out: the class 3 row of
  :numref:`tab-usbpd-translation-examples`, a Port Present PDP of 8 W;
* Ethernet in, Ethernet out: the class 3 row of
  :numref:`tab-poe-pass-through`, class 2 on port B.

USB in, Ethernet out does not involve port A, so it is the same as on
evampire (:numref:`tab-poe-usb-in`). Port B can offer up to class 8 from a
USB contract of 100 W or more.

Other routes to more power, not taken
-------------------------------------

Each of these gives port A more than class 3. ebat takes none of them,
because each either changes evampire's power side or adds data circuits
back:

Request class 4 or higher without LLDP
   This does not meet :clause:`145.3.6`, which uses "shall".
Present two signatures
   A :term:`dual-signature powered device` is classified on each pair set
   separately (:clause:`145.3.5`), and LLDP stays optional while it
   requests class 3 or lower on both (:clause:`Table 145-19 <145>`). It
   draws up to 13 W on each pair set (:clause:`Table 145-27 <145>`), 26 W
   from power sourcing equipment that powers both pair sets. It changes
   evampire's powered-device front end, which then needs its own
   signature, class signature and isolation switch on each pair set
   (:doc:`../power/poe/pd-controller`), and no more than
   10 µA between the two pair sets while off (:clause:`145.4.1`).
Add an Ethernet link that carries only LLDP
   A transceiver on port A, 10BASE-T at its simplest (:ref:`phy-int-10`),
   with the frame logic and memory for the LLDP frames. This puts back data
   circuits that ebat drops (:ref:`req-ebat-no-data`).
Use evampire
   evampire handles LLDP in its processor (:ref:`req-forwarding`). A board
   that needs more than class 3 uses evampire instead of ebat.

Port B changes its allocation only by classifying again
-------------------------------------------------------

This section applies to boards that do not pass Ethernet data through.
On a board that does, LLDP frames pass between the far ends and can change
the allocation (:ref:`ebat-pass-through-lldp`).

As :term:`power sourcing equipment`, port B assigns a class by Physical
Layer classification, up to class 8 with 4-pair power
(:doc:`../power/poe/power-sourcing`). LLDP is optional for power sourcing
equipment (:clause:`145.2.8`, :clause:`145.5`), so ebat meets the standard
without it. A powered device on port B that requested class 4 or higher
keeps the class it was assigned, because no LLDP exchange changes it
(:clause:`145.3.6`).

Without LLDP, the software can lower port B's allocation only by removing
the power and classifying the powered device again with fewer class events,
which interrupts the device (:doc:`../power/poe/sharing`). Autoclass, in
which the power sourcing equipment measures the powered device's real draw
shortly after power-on, is an extension of Physical Layer classification and
needs no LLDP (:clause:`145.2.8.2`). It is defined only for
single-signature powered devices. If the powered device supports it, ebat
can use it to allocate less than the full class power
(:doc:`../power/poe/translation`).
