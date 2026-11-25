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
2 or 3. Which of the three is open (:ref:`ebat-requirements-open-questions`).

Power at class 3
----------------

At class 3 a powered device may draw 13 W at its input
(:numref:`tab-poe-classes`). Every type of power sourcing equipment gives
the full power of class 1 to 3 from Physical Layer classification alone
(:numref:`tab-poe-class-outcome`).

The power that remains for the outputs is worked out as on evampire, from
the class power, the converter efficiency and the board's own power
(:doc:`../power/usb-pd/power-translation`). With evampire's illustrative
values, which include the transceivers in the board's own power, the class
3 rows give:

* Ethernet in, USB out: a Port Present PDP of 8 W
  (:numref:`tab-usbpd-translation-examples`);
* Ethernet in, Ethernet out: class 2 on port B
  (:numref:`tab-poe-pass-through`).

An ebat board has no transceivers, so its own power leaves out their
share, and the power for its outputs is higher by the same amount. Both
the board's own power and the transceivers' share are unknown, so the
power that remains is between the values above and 13 W times the
converter efficiency.

USB in, Ethernet out does not involve port A, so it is the same as on
evampire (:numref:`tab-poe-usb-in`). Port B can offer up to class 8 from a
USB contract of 100 W or more.

Alternatives for more power
---------------------------

Each of these gives port A more than class 3. ebat takes none of them,
because each either changes evampire's power side or adds data circuits
back:

Request class 4 or higher without LLDP
   This does not meet :clause:`145.3.6`, which uses "shall".
Present two signatures
   A :term:`dual-signature powered device` presents class signatures on
   each pair set separately (:clause:`145.3.6.1`), and LLDP stays optional
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
exchange with its powered device (:ref:`req-ebat-no-lldp`). A powered
device without LLDP receives the full power of its assigned class, as from
evampire (:ref:`req-poe-classification`). It keeps that class, including
after demotion (:ref:`poe-demotion`), because nothing can ask for more.
On a board with data pass-through, LLDP frames pass between the far ends
and can change the allocation (:ref:`ebat-pass-through-lldp`).

To change port B's allocation, the software removes the power, runs
detection again and classifies the powered device with a different number
of class events (:doc:`../power/poe/sharing`). The powered device is
unpowered while this happens. :numref:`fig-ebat-reclassify` shows the
order. Fewer class events give a lower class, and the class can rise again
only up to the one the device requests (:ref:`poe-demotion`).

.. graphviz:: reclassify.dot
   :name: fig-ebat-reclassify
   :caption: Changing the allocation of the powered device on port B
             without LLDP, by removing the power and classifying again;
             schematic and not to scale.
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
