.. _poe-lldp:

Negotiating power over LLDP
===========================

This page describes how the two ends of a cable change the power
allocation after the Ethernet link is up, and how evampire takes part as a
powered device and as power sourcing equipment.

Classification sets the first allocation
----------------------------------------

Classification (:doc:`sequence`) gives a powered device its first power
allocation, in fixed steps, before the link is up. After the link is up,
the two ends can change the allocation in steps of 0.1 W by exchanging
Ethernet frames. The standard calls this Data Link Layer classification
(:clause:`145.5`). When both are used, the Data Link Layer value takes
precedence (:clause:`145.2.8`).

The frames are LLDP frames
--------------------------

The frames belong to the Link Layer Discovery Protocol, :term:`LLDP`
(:std:`IEEE 802.1AB <802.1AB>`). Each is a small frame sent only to the
device at the other end of the cable, to the destination address
``01-80-C2-00-00-0E`` with :wikipedia:`EtherType <EtherType>` ``0x88CC``
[POE-802-1AB]_. IEEE 802.3 defines a *Power via MDI* field carried in them
(:clause:`79.3.2`). The MDI, the medium dependent interface, is the
connection to the cable, here the RJ45 socket.

The field's main entries are:

* the power the powered device requests;
* the power the power sourcing equipment allocates;
* copies of the other end's last values, so each end can see that the
  other has received its value.

Values are in units of 0.1 W, so 255 means 25.5 W
(:clause:`Table 145-12 <145>`).

Classes 4 and higher must support it
------------------------------------

A single-signature powered device that requests class 4 or higher must
support the exchange; for classes 1 to 3 it is optional
(:clause:`145.3.6`, :clause:`145.5`). The power sourcing equipment's
support is optional. A powered device of class 1 to 3 that does not support
it can have its power changed only by removing the power and classifying it
again.

The allocated value sets the assigned class (:clause:`Table 145-12 <145>`),
as in :numref:`tab-poe-dll-class`.

.. list-table:: Allocated power and the assigned class
   :name: tab-poe-dll-class
   :header-rows: 1
   :widths: 35 35 30

   * - From (0.1 W)
     - To (0.1 W)
     - Assigned class
   * - 1
     - 39
     - 1
   * - 40
     - 65
     - 2
   * - 66
     - 130
     - 3
   * - 131
     - 255
     - 4
   * - 256
     - 400
     - 5
   * - 401
     - 510
     - 6
   * - 511
     - 620
     - 7
   * - 621
     - 999
     - 8

On 2-pair power the allocation is at most 255, 25.5 W
(:clause:`Table 145-41 <145>`).

The two ends take turns
-----------------------

The rules of :clause:`145.5.2` and :clause:`145.5.5` are:

* The power sourcing equipment sends its first frame within 10 s of
  enabling the exchange.
* Each end answers a changed value from the other within 10 s.
* An end is *in sync* when the copy the other end sends back matches its
  own value. A powered device does not change its request or its power
  draw while it is out of sync.
* The power sourcing equipment may lower the allocation at any time, and
  raise it only while in sync.
* Values above 71.3 W are used only after both ends are in sync
  (:clause:`145.5.4`).

Deadlines of seconds let the software meet them without
special hardware.

LLDP frames on evampire go only to the processor
------------------------------------------------

evampire forwards every frame between ports A and B, except LLDP frames,
which it delivers only to its processor (:ref:`req-forwarding`).
:numref:`fig-poe-lldp-path` shows the paths. Each port's power exchange
stays on its own cable: the upstream power sourcing equipment sees
evampire as its powered device, and the downstream powered device sees
evampire as its power sourcing equipment. The address filter that selects
these frames is described in :ref:`arch-address-filter`.

.. graphviz:: lldp-path.dot
   :name: fig-poe-lldp-path
   :caption: LLDP frames from each port go to evampire's processor, and all
             other frames pass between the ports through the forwarding
             logic.
   :alt: Diagram. Upstream power sourcing equipment connects by cable to
         port A, and a downstream powered device connects by cable to port
         B. Ports A and B exchange other frames through the forwarding
         logic. Each port exchanges its LLDP frames only with the
         processor.
   :align: center

The software takes both roles
-----------------------------

As a powered device on port A, the software sends its requested power and
watches the allocated value. It may lower its request to hand power back,
or ask again for up to the class it requested during classification.

As power sourcing equipment on port B, the software reads the request,
decides from the power budget how much to allocate (:doc:`sharing`), and
answers with the allocated value. The new limit applies once both ends show
the same value. It also sets the current and power limits of the port to
match (:doc:`monitoring`).

When the power on port A falls, the software lowers the allocation on port
B first (:ref:`power budget <power-budget>`).

Open questions
--------------

* Whether port B supports the exchange, which the standard leaves optional
  for power sourcing equipment.
