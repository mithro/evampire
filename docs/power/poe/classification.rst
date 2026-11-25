.. _poe-classification:

Classification methods
======================

This page describes the two ways in which a powered device obtains its
power, which of them each type must implement, the power that each
combination of the two ends gives, and how evampire uses both in each of
its roles.

The two methods
---------------

The standard gives the two ends of a cable two ways to agree the power:

:term:`Physical Layer classification`
   The class events of :doc:`sequence`, before the operating voltage is
   switched on. The number of class events and the class signatures that
   the powered device shows decide the assigned class.
:term:`Data Link Layer classification`
   The exchange of LLDP frames after the link is up, which changes the
   allocation in steps of 0.1 W (:doc:`lldp`).

Both also give :term:`mutual identification`: each end learns the type of
the other (:clause:`33.2.6`, :clause:`145.2.8`).

Methods by type
---------------

:numref:`tab-poe-class-methods` lists the methods that each type must
implement. The Type 1 and Type 2 rows come from
:clause:`Table 33-8 <33>`, :clause:`33.2.6` and :clause:`33.3.5`, the
Type 3 and Type 4 rows from :clause:`145.2.8`, :clause:`145.3.6` and
:clause:`145.5`.

.. list-table:: Classification methods each type implements
   :name: tab-poe-class-methods
   :header-rows: 1
   :widths: 34 36 30

   * - Device
     - Physical Layer classification
     - Data Link Layer classification
   * - Type 1 power sourcing equipment
     - None, or 1 class event
     - Optional
   * - Type 2 power sourcing equipment
     - 2 class events, or 1 class event
     - Required if it issues 1 class event, otherwise optional
   * - Type 3 or Type 4 power sourcing equipment
     - As many class events as the assigned class needs, up to 4 or 5
     - Optional
   * - Type 1 powered device
     - Class signature 0 to 3 in 1 or 2 class events; class 0 is the
       default
     - Optional
   * - Type 2 powered device
     - Class signature 4 in each of 2 class events
     - Required
   * - Type 3 or Type 4 single-signature powered device, requesting
       class 1 to 3
     - Class signatures in up to 5 class events
     - Optional
   * - Type 3 or Type 4 single-signature powered device, requesting
       class 4 to 8
     - Class signatures in up to 5 class events
     - Required
   * - Type 3 or Type 4 dual-signature powered device
     - Class signatures on each pair set
     - Required if it requests class 4 or higher on either pair set,
       otherwise optional

The rules for power sourcing equipment differ by type:

* Type 2 power sourcing equipment implements 2-event Physical Layer
  classification, with or without Data Link Layer classification, or
  1-event Physical Layer classification with Data Link Layer
  classification. Data Link Layer classification alone, or one class event
  without it, is not allowed (:clause:`Table 33-8 <33>`,
  :clause:`33.2.6`).
* When the first class event shows class signature 4, Type 2 equipment may
  skip the second only if it implements Data Link Layer classification. It
  may then give class 0 power, 15.4 W at its output, until mutual
  identification is complete (:clause:`33.2.6.1`, :clause:`33.2.6.2`).
  When the first shows class signature 0 to 3, it treats the powered
  device as Type 1 and may stop there.
* Type 3 and Type 4 power sourcing equipment must perform multiple-event
  Physical Layer classification, and must be able to assign the highest
  class it can support that way (:clause:`145.2.8`). It therefore gives
  full class power without LLDP. It issues no more class events than the
  class it can support needs (:clause:`145.2.8.1`): one when the powered
  device requests class 0 to 3, or when it can support no more than
  class 3 (:clause:`Table 145-11 <145>`).
* Data Link Layer classification is optional for Type 3 and Type 4 power
  sourcing equipment (:clause:`145.2.8`, :clause:`145.5`).

The rules for powered devices are the reverse: Data Link Layer
classification is required for most of them. A Type 2 powered device
implements both 2-event class signatures and Data Link Layer
classification (:clause:`33.3.5`). Until either has completed, it keeps to
the limits of a Type 1 powered device, 13 W (:clause:`33.3.5.2`).
A single-signature Type 3 or Type 4 powered device that requests class 4
or higher, and a dual-signature one that requests class 4 or higher on
either pair set, implements Data Link Layer classification
(:clause:`145.3.6`, :clause:`145.5`). For other Type 3 and Type 4 powered
devices it is optional.

Some summaries are stricter than the standard. For reference, the TPS2373
datasheet states that every Type 3 and Type 4 powered device does Data
Link Layer classification [POE-TPS2373]_ (PoE Overview), whereas
:clause:`145.3.6` makes it optional for single-signature classes 1 to 3.
evampire implements it in either case (:ref:`req-poe-classification`).

.. _poe-class-outcome:

Power at the powered device
---------------------------

The power at the powered device depends on both ends.
:numref:`tab-poe-class-outcome` gives it for each kind of power sourcing equipment, by the class the powered device
requests. Each value is the power of the assigned class at the powered
device (:numref:`tab-poe-classes`), and assumes the power sourcing
equipment has the power to give.

.. list-table:: Power at the powered device, in watts, by requested class
   :name: tab-poe-class-outcome
   :header-rows: 1
   :widths: 32 17 17 17 17

   * - Power sourcing equipment
     - Class 1 to 3
     - Class 4
     - Class 5 or 6
     - Class 7 or 8
   * - Type 1, 1 class event
     - Class power
     - 13
     - 13
     - 13
   * - Type 2, 2 class events
     - Class power
     - 25.5
     - 25.5
     - 25.5
   * - Type 2, 1 class event, before LLDP
     - Class power
     - 13
     - 13
     - 13
   * - Type 2, 1 class event, after LLDP
     - Class power
     - Up to 25.5
     - Up to 25.5
     - Up to 25.5
   * - Type 3, up to 4 class events
     - Class power
     - 25.5
     - 40 or 51
     - 51
   * - Type 4, up to 5 class events
     - Class power
     - 25.5
     - 40 or 51
     - 62 or 71.3

The rows follow from :numref:`tab-poe-events` and the Type 2 rules above. A
Type 1 power sourcing equipment assigns class 0 to a powered device that
shows class signature 4 (:clause:`33.2.6.1`), and a Type 1 powered device
of class 0 gets 13 W from all of them. A powered device that requests
class 5 to 8 shows class signature 4 in the first two class events
(:numref:`tab-poe-request`), so Type 1 and Type 2 power sourcing equipment
sees a class 4 powered device.

For a powered device that requests class 4 or higher, only Type 2
equipment that issues two class events, and Types 3 and 4, give the power
of class 4 or higher without LLDP.

.. _poe-demotion:

Power demotion
--------------

The assigned class is the lower of the requested class and the class that
the number of class events allows (:numref:`tab-poe-events`). A power
sourcing equipment that cannot supply the requested class, because of its
type or its power budget, issues fewer class events (:clause:`145.2.8.1`,
:clause:`Table 145-11 <145>`). The standard has no name for this; the
Ethernet Alliance overview calls it :term:`power demotion` [POE-EA-BT]_
(Section 5).

Demotion follows from the power sourcing equipment's capability, not from
a missing LLDP exchange. The powered device conforms to its assigned class
whatever class it requested, and gives an active indication when
underpowered (:clause:`145.3.6`, :ref:`poe-pd-dll`).

Over LLDP a demoted powered device can ask again for up to its requested
class, and the power sourcing equipment grants it if its budget allows. It
cannot ask for more than its requested class: the variable
``pd_dllmax_value`` limits its request to the power of that class for
classes 1 to 7, and to 99.9 W for class 8 (:clause:`145.5.3.3.1`,
:clause:`145.3.8.2.1`).
Autoclass only lowers the allocation (:ref:`autoclass <poe-autoclass>`).

Before classification is complete, and in the first 80 ms after turn-on,
the powered device stays within the
:ref:`start-up limits <poe-pd-inrush>`.

Methods used in the field
-------------------------

Power sourcing equipment differs in which method it relies on. The
following are reference examples of products, not evidence of what the
standard requires:

* Cisco Catalyst 9300 switches in 802.3at mode first allocate 15.4 W to
  class 0, 3 and 4 powered devices. A class 4 device gets up to 30 W by
  asking over CDP or LLDP, unless the port is set to issue two class
  events [POE-CISCO-9300]_ (IEEE 802.3at). Cisco's protocol, CDP, is not
  part of the standard.
* On Catalyst 9200 and 9300 switches the per-port command
  ``power inline port 2-event`` makes the switch allocate 30 W to class 4
  from Physical Layer classification [POE-CISCO-9300]_ (IEEE 802.3at)
  [POE-CISCO-9200]_ (Third-party Powered Device Scenarios).
* Cisco switches that support Type 3 can be in 802.3at mode by default. In
  802.3bt mode they allocate the full class power from Physical Layer
  classification [POE-CISCO-9300]_ [POE-CISCO-9200]_.
* Extreme Networks describes LLDP as optional for the power sourcing
  equipment, but required by a Type 2 powered device that needs more than
  12.95 W, because some switches do not negotiate power in hardware
  [POE-EXTREME-LLDP]_.
* Juniper EX switches in class mode allocate by class, and LLDP refines
  the allocation [POE-JUNIPER-POE]_ (Power Management Modes).
* Midspan injectors such as the Microchip PD-9001GR use 2-event
  classification and supply 30 W [POE-PD-9001GR]_.

A powered device that shows class signatures but does not answer LLDP
therefore gets 13 W from the first kind of switch. One that shows a lower
class signature and relies on LLDP to raise it gets only the power of that
class from equipment without Data Link Layer classification, such as a
midspan injector. Full power from both needs both methods.

Summaries of the standard can hide this. The power management row of the
comparison table in :wikipedia:`Power over Ethernet <Power_over_Ethernet>`
says classes are negotiated by signature or in 0.1 W steps by LLDP. That
holds for Types 3 and 4. For Type 2 it is incomplete, because compliant
power sourcing equipment may rely on one class event and LLDP.

Methods in evampire
-------------------

evampire uses both methods in both roles, as :ref:`req-poe-classification`
sets out for each role. These pages describe how:

As a powered device
   The start-up sequencer shows the class signatures (:doc:`startup`), and
   the software takes part in the LLDP exchange (:doc:`lldp`).
As power sourcing equipment
   The software runs the class events (:doc:`power-sourcing`), answers
   LLDP requests (:doc:`lldp`) and decides each allocation from the power
   budget (:doc:`sharing`).

Open questions
--------------

* Which board functions run while the powered-device port is held at
  13 W or demoted, before LLDP raises the allocation.
* How often the powered-device software asks again over LLDP after the
  power sourcing equipment has refused a request.
