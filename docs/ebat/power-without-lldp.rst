.. _ebat-power-without-lldp:

Power over Ethernet without LLDP
================================

Without LLDP, ebat receives Power over Ethernet at class 3 or lower, at
most 13 W at its input, and changes the power it supplies on an Ethernet
port only by classifying the powered device again. The highest class it
supplies is class 8, as on evampire.

.. _ebat-lldp-class-4:

LLDP requirement for class 4 and higher
---------------------------------------

evampire uses both classification methods on every Ethernet port:
:term:`Physical Layer classification` before the power is switched on, and
:term:`Data Link Layer classification` over :term:`LLDP` once the link is
up (:ref:`req-poe-classification`). LLDP frames are Ethernet frames, so
ebat has only the first.

A powered device that requests class 4 or higher must implement Data Link
Layer classification, and one that requests class 1 to 3 need not
(:numref:`tab-poe-class-methods`; :clause:`145.3.6`, :clause:`33.3.5`).
ebat's port A, the same circuit as evampire's, therefore requests class 1,
2 or 3.

Power at class 3
----------------

At class 3 a powered device may draw 13 W at its input
(:numref:`tab-poe-classes`). Every type of power sourcing equipment that
has the power to give gives the full power of class 1 to 3 from Physical
Layer classification alone (:numref:`tab-poe-class-outcome`).

The power that remains for the outputs is 13 W times the converter
efficiency, less the board's own power, worked out as on evampire
(:doc:`../power/usb-pd/power-translation`, :doc:`../power/poe/translation`).
The class 3 rows of evampire's examples give it for illustrative values:

* Ethernet in, USB out: a Port Present PDP of 8 W, with an efficiency of
  0.900 and 3.10 W of board power
  (:numref:`tab-usbpd-translation-examples`);
* Ethernet in, Ethernet out: class 2 on port B, with an efficiency of 0.85,
  while the board uses no more than 4.3 W (:numref:`tab-poe-pass-through`).
  Port B can then power only a device that requests class 1 or 2, because
  even one class event assigns class 3 to a device that requests class 3
  or higher (:clause:`Table 145-11 <145>`, :numref:`tab-poe-events`). Port
  B refuses power to such a device, unless the device supports Autoclass
  (:ref:`ebat-port-b-allocation`).

An ebat board has no transceivers, so its own power has no transceiver
share. Its value is unknown, as on evampire, and the power for the outputs
follows from it as in these examples.

USB in, Ethernet out does not involve port A, so it is the same as on
evampire (:numref:`tab-poe-usb-in`), with the same conditions on the
board's own power, the efficiency and the type of port B.

Alternatives for more power
---------------------------

Each of these gives port A more than class 3. ebat takes none of them,
because each either changes evampire's power side or adds data circuits
back:

Request class 4 or higher without LLDP
   This does not meet :clause:`145.3.6`, which uses "shall".
Present two signatures
   A :term:`dual-signature powered device` presents class signatures on
   each pair set separately (:clause:`145.3.5`, :clause:`145.3.6.1`), and LLDP stays optional
   while it requests class 3 or lower on both
   (:clause:`Table 145-19 <145>`). It draws up to 13 W on each pair set
   (:clause:`Table 145-27 <145>`), 26 W from power sourcing equipment that
   powers both pair sets. It changes evampire's powered-device front end,
   which then needs its own signature, class signature and isolation switch
   on each pair set (:doc:`../power/poe/pd-controller`). The leakage
   between the negative conductors of the two pair sets must then stay
   within 10 µA while either is below the turn-off voltage
   (:clause:`145.4.1`).
Add an Ethernet link that carries only LLDP
   A transceiver on port A, 10BASE-T at its simplest (:ref:`phy-int-10`),
   with the frame logic and memory for the LLDP frames. This puts back data
   circuits that ebat drops (:ref:`req-ebat-no-data`).
Use evampire
   evampire handles LLDP in its processor (:ref:`req-forwarding`). A board
   that needs more than class 3 uses evampire instead of ebat.

.. _ebat-port-b-allocation:

Allocation changes on port B
----------------------------

On a board that does not pass Ethernet data through, port B has no LLDP
exchange with its powered device (:ref:`req-ebat-no-lldp`). Without that
exchange, the powered device receives the full power of its assigned
class, as from evampire (:ref:`req-poe-classification`). Its class changes
only when port B removes the power and classifies it again, including
after demotion (:ref:`poe-demotion`). On a board with data pass-through, LLDP frames pass between the far ends
and can change the allocation (:ref:`ebat-pass-through-lldp`).

To change port B's allocation, the software removes the power, runs
detection again and classifies the powered device with a different number
of class events (:doc:`../power/poe/sharing`). The powered device is
unpowered while this happens. :numref:`fig-ebat-reclassify` shows the
order. The device gets the lower of its requested class and the class
that the number of class events allows, 3, 4, 6 or 8
(:numref:`tab-poe-events`, :ref:`poe-demotion`). Classifying again
therefore moves a device that requests class 4 to 8 between class 3 and
its requested class, and cannot lower a device that requests class 1
to 3. To give such a device less than its class power, port B uses
Autoclass, if the device supports it, or refuses power.

.. graphviz:: reclassify.dot
   :name: fig-ebat-reclassify
   :caption: Changing the allocation of the powered device on port B
             without LLDP, by removing the power and classifying again;
             schematic.
   :alt: Five steps from left to right. The powered device is powered at
         its assigned class. The software removes the power, and the
         powered device turns off. Port B runs detection again. Port B
         runs classification with a different number of class events,
         which sets the new class. Port B switches the power on at the new
         class. A bracket under the middle three steps marks the time the
         powered device has no power.
   :align: center

:ref:`Autoclass <poe-autoclass>` is part of Physical Layer classification
and needs no LLDP (:clause:`145.2.8.2`). If the powered device supports
it, ebat can use it to allocate less than the full class power
(:doc:`../power/poe/translation`).

Open questions
--------------

* Which class, 1, 2 or 3, port A's start-up sequencer requests. evampire
  leaves the class it requests open (:doc:`../power/poe/startup`).
