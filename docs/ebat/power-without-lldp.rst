.. _ebat-power-without-lldp:

Power over Ethernet without LLDP
================================

This page explains why ebat, which has no Ethernet data path, requests at
most class 3 when it receives Power over Ethernet, and gives the power that
leaves. Supplying power is not limited in this way.

Classes 4 and higher need LLDP
------------------------------

evampire uses both classification methods on every Ethernet port:
:term:`Physical Layer classification` before the power is switched on, and
:term:`Data Link Layer classification` over :term:`LLDP` once the link is
up (:ref:`req-poe-classification`). LLDP frames are Ethernet frames, so
ebat has only the first.

A powered device that requests class 4 or higher must implement Data Link
Layer classification, and one that requests class 1 to 3 need not
(:numref:`tab-poe-class-methods`). ebat's port A, the same circuit as
evampire's, therefore requests class 1, 2 or 3.

Class 3 gives 13 W
------------------

At class 3 a powered device may draw 13 W at its input
(:numref:`tab-poe-classes`). Every type of power sourcing equipment gives
the full power of class 1 to 3 from Physical Layer classification alone
(:numref:`tab-poe-class-outcome`).

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
(:doc:`../power/poe/power-sourcing`), and a powered device without LLDP
receives the full power of that class, as from evampire
(:ref:`req-poe-classification`). Data Link Layer classification is
optional for power sourcing equipment (:numref:`tab-poe-class-methods`),
so ebat meets the standard without it. ebat cannot answer LLDP power
requests, so a powered device on port B keeps the class it was assigned,
including after demotion (:ref:`poe-demotion`).

Without LLDP, the software can lower port B's allocation only by removing
the power and classifying the powered device again with fewer class events,
which interrupts the device (:doc:`../power/poe/sharing`).
:ref:`Autoclass <poe-autoclass>` is part of Physical Layer classification
and needs no LLDP (:clause:`145.2.8.2`). If the powered device supports
it, ebat can use it to allocate less than the full class power
(:doc:`../power/poe/translation`).
