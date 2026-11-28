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
in five ways. :numref:`fig-poe-allocation-ways` shows what each changes,
whether the device stays powered and whether the way needs LLDP.

By LLDP
   Changes the allocation in steps of 0.1 W while the device stays
   powered. The device must support the exchange: every powered device
   that requests class 4 or higher does (:numref:`tab-poe-class-methods`),
   and evampire's port always answers (:ref:`req-poe-classification`). A
   single-signature device can also request a new Autoclass measurement
   this way, if the port supports :ref:`Autoclass <poe-autoclass>`.
By classifying again
   Changes the assigned class, and removes the power while the port
   classifies the device with a different number of class events. It can
   lower only a device that requests class 4 or higher
   (:ref:`poe-demotion`).
By Autoclass
   Lowers the allocation to the device's measured draw plus a margin, for
   a single-signature device that supports
   :ref:`Autoclass <poe-autoclass>`. Without LLDP it acts only at
   power-up, so a device that is already powered loses power first, as
   when classifying again. Whether port B supports Autoclass is an open
   question (:doc:`power-sourcing`).
By powering one pair set
   Removes the class power of one pair set of a
   :term:`dual-signature powered device`, which the port classifies and
   powers pair set by pair set (:clause:`145.2.8`). The other pair set
   stays powered. The device still shows a valid detection signature
   (:clause:`145.3.4`) and class signature (:clause:`145.3.6.1`) on the
   unpowered pair set.
By refusing power
   Removes the power, or never switches it on.
   :ref:`Power sourcing equipment classification <poe-pse-classification>`
   gives when the port must refuse.

.. graphviz:: allocation-ways.dot
   :name: fig-poe-allocation-ways
   :caption: The five ways a power sourcing equipment port changes the
             power of a powered device, what each changes, whether the
             device stays powered, and whether the way needs LLDP.
   :alt: Five boxes stacked from top to bottom, each giving the way, what
         it changes, whether the device stays powered and whether LLDP is
         needed. By LLDP, green: the allocation, in 0.1 W steps; stays
         powered; needs LLDP. By classifying again, orange: the class, if
         the requested class is 4 or higher; power removed; no LLDP. By
         Autoclass, orange: the allocation, to the measured draw plus a
         margin; at power-up the power is removed and no LLDP is needed,
         or on request over LLDP the device stays powered. By powering one
         pair set, yellow: one pair set's power; the other pair set stays
         powered; no LLDP. By refusing power, orange: no power; power
         removed; no LLDP.
   :align: center

A dual-signature device need not work on one pair set. Only a
single-signature device that requests class 4 or less must work on any
valid arrangement of pairs, and other devices may need 4-pair power to
work at their nominal power level (:clause:`145.3.2`). evampire's port B
can power one pair set of a dual-signature device only if it can power
both pair sets and supports dual-signature devices, which are open
questions (:doc:`basics`, :doc:`power-sourcing`).

Power sourcing equipment may also base its allocation on more than the
class, but not only on how much power the powered device has drawn in the
past (:clause:`145.2.11`). An allocation that the port keeps to itself,
without LLDP or Autoclass, does not change what the powered device may
draw. The device conforms to its assigned class (:clause:`145.3.6`), and
the port's minimum output at its power interface is the power of that
class, unless Autoclass or LLDP sets it (:clause:`145.2.8`,
:clause:`145.3.8.2`). How a system shares power
between its ports near its maximum is outside the standard
(:clause:`145.2.11`).

A powered device that requests class 1 to 3 may lack
:term:`Data Link Layer classification` (:clause:`145.3.6`), as may a Type 1
powered device (:clause:`Table 33-8 <33>`). Without it, the port can lower
the power it must be able to supply only by Autoclass, for a
single-signature Type 3 or Type 4 powered device, or by powering one pair
set of a dual-signature one (:clause:`Table 145-19 <145>`). Otherwise its
only choices are the full class power or refusing power. A Type 1 powered
device supports neither Autoclass nor a dual signature, which
:clause:`Table 145-19 <145>` lists only for Types 3 and 4
(:clause:`145.3.1`, :clause:`33.3`).

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
