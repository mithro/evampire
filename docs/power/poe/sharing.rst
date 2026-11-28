.. _poe-sharing:

Sharing the budget between ports
================================

When a power sourcing equipment port supplies power at the same time as
other output ports, the software shares the power budget between them and
moves power between them safely.

Offers within the budget
------------------------

Several ports can supply power at once (:ref:`power-sharing`): on a full
design board, two USB Type-C ports and an Ethernet port, or both Ethernet
ports when the board is powered from USB
(:ref:`board configurations <tab-power-board-configs>`). The software keeps
the sum of the offers within the power left for the outputs:

.. math::

   \sum_i P_{\text{offer},i} \le P_\text{out}

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`P_{\text{offer},i}`
     - Highest power offered on output port :math:`i`
     - W
   * - :math:`P_\text{out}`
     - Power left for the outputs (:doc:`translation`)
     - W

For a power sourcing equipment port, the offer is the power of its assigned
class at the power sourcing equipment (:numref:`tab-poe-classes`), the
allocated value set over LLDP plus the cable loss (:doc:`lldp`), or the
allocation from :ref:`Autoclass <poe-autoclass>`.

For example, with :math:`P_\text{out} = 80\ \text{W}`, a class 5 Ethernet
output takes 45 W and leaves 35 W for the USB Type-C ports together
(:numref:`fig-poe-budget-split`). The USB
offers that fit in 35 W are described on :doc:`../usb-pd/index`.

.. figure:: budget-split.svg
   :name: fig-poe-budget-split
   :alt: Bar of power offered from 0 to 80 W. A class 5 Ethernet output
         takes 45 W and the USB Type-C ports together take the remaining
         35 W of the 80 W output budget.
   :align: center

   An 80 W output budget shared between a class 5 Ethernet output and the
   USB Type-C ports.

.. _poe-allocation-changes:

Allocation changes
------------------

A USB Power Delivery source can change its offer while a device is
connected, by sending a new list of offers. A power sourcing equipment port
changes the power it allocates to a powered device, or stops supplying it,
in these ways:

Over LLDP
   In steps of 0.1 W, with a powered device that supports the exchange.
   Every powered device that requests class 4 or higher does
   (:numref:`tab-poe-class-methods`), and evampire's port always answers
   (:ref:`req-poe-classification`).
By classifying again
   Removing the power and running classification again with a different
   number of class events, which interrupts the powered device. This moves
   a device that requests class 4 or higher only between class 3 and its
   requested class, and cannot lower one that requests class 1 to 3
   (:ref:`poe-demotion`).
By Autoclass
   Only with a single-signature powered device that supports
   :ref:`Autoclass <poe-autoclass>` (:clause:`145.2.8.2`). The port
   measures the device's highest draw after each power-up, and may allocate
   that plus a margin, up to the power of the assigned class. If the
   measured power is 4 W or less, the allocation stays at the class power
   (:clause:`145.2.8`).
By powering one pair set
   Only with a :term:`dual-signature powered device`, whose pair sets the
   port classifies and powers separately (:clause:`145.2.8`). The device
   still shows a valid detection and class signature on the unpowered pair
   set (:clause:`145.3.5`, :clause:`145.3.6`), and receives only the class
   power of the powered one. evampire's port B can do this only if
   it powers both pair sets and supports dual-signature devices, which are
   open questions (:doc:`basics`, :doc:`power-sourcing`).
By refusing power
   Not switching the power on, or removing it and not switching it on
   again. Power sourcing equipment does not start to supply power when it
   has less than class 3 power and the powered device requests more than
   it has (:clause:`145.2.11`).

Power sourcing equipment may also base its allocation on more than the
class, but not only on how much power the powered device has drawn in the
past (:clause:`145.2.11`). Such an allocation does not change what the
powered device may draw: it conforms to its assigned class
(:clause:`145.3.6`), and the port must be able to supply the power of that
class (:clause:`145.2.8`).

A powered device that requests class 1 to 3 may lack
:term:`Data Link Layer classification` (:clause:`145.3.6`), as may every
Type 1 powered device (:clause:`33.3.5`). Without it, only Autoclass and
powering one pair set lower the power that the port must be able to supply
below the power of the assigned class, short of refusing power.

Moving power between ports
--------------------------

When a device on one port is unplugged or uses less than its share, the
software raises the offer on another port (:numref:`fig-power-sharing`
shows the offers over time). When a new device is plugged in,
it first lowers the offers on the other ports to make room. On a power
sourcing equipment port, lowering over LLDP is complete only when the
powered device has answered with the new value, which may take up to 10 s
(:clause:`145.5.2`). Until then the software keeps the old allocation in
the budget. A compliant powered device may keep drawing its old allocation
until it answers, so the port's built-in current and power limit
(:doc:`monitoring`) stays at the old allocation until then and is lowered
when the answer arrives. :numref:`fig-poe-sharing-move` shows the
order.

.. graphviz:: sharing-move.dot
   :name: fig-poe-sharing-move
   :caption: Moving power to a new device on a USB Type-C output by first
             lowering the allocation of an Ethernet output.
   :alt: Sequence diagram with three lifelines: the powered device on the
         Ethernet output, the software on evampire, and a new device on a
         USB Type-C output. The new device attaches and the budget needs
         room. The software sends an LLDP frame lowering the allocation;
         the old allocation is still counted and the hardware limit stays
         at the old value. Up to 10 s later the powered device echoes the
         new value; the lower allocation is counted and the hardware limit
         is lowered. The software then raises the offer on the USB Type-C
         output.
   :align: center

If the input power falls faster than the outputs can be lowered, for
example when the USB charger is unplugged, the software removes power from
output ports, starting with the ones it gives lowest priority.

Open questions
--------------

* The priority between output ports when the budget is short.
* The share each port starts with when several devices are connected at
  once.
