Two ports and sharing the budget
================================

How a board with two USB Type-C ports shares its power.

Two ports
---------

In the :ref:`full design <power-board-configs>` the board has two dual-role
USB Type-C ports. This changes:

* **Roles.** One port can sink while the other sources, which makes the board
  a USB-to-USB power bridge as well as a USB-to-Ethernet one. The
  :ref:`power budget <power-budget>` then has two outputs sharing one input,
  or one USB input feeding a USB output and Ethernet.
* **Budget.** The offers on both outputs together must fit the budget. When
  a second device attaches, the processor may have to lower the first port's
  offer, with the Alert and new Source_Capabilities described in
  `Building the offer from the power budget`_. PD calls this a *Managed
  Capability Port* (:pd:`Section 3.2.3`).
* **Analog circuits.** Each port needs its own CC front end: both ports must
  present terminations and detect attach at the same time, and messages on
  the two ports arrive independently. Only slow measurements (attach levels,
  VBUS level) can share one comparator or ADC through a multiplexer.
* **Processor time.** Two negotiations can overlap. See
  `Two ports in software`_.
