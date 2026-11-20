Source, sink and the configuration channel
==========================================

What a USB Type-C power connection is: the source, the sink and the configuration channel wires.

This page describes how the `RISC-V <https://riscv.org/>`__
:ref:`processor <arch-microcontroller>` carries out the USB Power Delivery
negotiation in software, by directly driving and sampling the configuration
channel; which analog circuits it needs for that; and what the gf180mcu
process allows on the chip.

A board built around evampire bridges power between Ethernet and USB Type-C
in both directions (see :doc:`index`). Every USB Type-C port on the board is
therefore *dual-role*: it can supply power (act as a *source*) or receive
power (act as a *sink*), it settles on one of the two when a cable is plugged
in, and it can swap roles with the other end while the cable stays connected.
The first version of the board has one USB Type-C port; the
:ref:`full design <power-board-configs>` has two, each dual-role.

USB Power Delivery is implemented mostly in software on the RISC-V processor.
The dedicated hardware is kept to the minimum: the analog circuits that
connect to the configuration channel wires, and only those digital helpers
whose timing cannot be met in software (power bridging
:ref:`requirements`).

The page first explains how two USB Type-C ports find each other and decide
who supplies power, then how they agree on a voltage, then the signal on the
wire in enough detail to receive and send it in software, the source side,
cables, role changes, two ports, the cost of doing all of this in software,
the analog blocks, and the on-chip and external options for each of them on
the `gf180mcu <https://gf180mcu-pdk.readthedocs.io/>`__ process (see
`Limits of the gf180mcu process`_).

Two specifications are quoted throughout. Both are free to download from the
`USB Implementers Forum <https://www.usb.org/>`__ (USB-IF) document library:

* **Type-C** means the :ref:`USB Type-C Cable and Connector Specification
  <usb-type-c-specification>`, Release 2.5, March 2026 [USBPD-TYPEC]_.
* **PD** means the :ref:`USB Power Delivery Specification
  <usb-pd-specification>`, Revision 3.3, Version 1.0, 2026-10-16
  [USBPD-PD]_.

Section and table numbers given in brackets, such as (:pd:`Table 5.10`),
refer to these documents and link to their entries on the
:doc:`standards page <../standards>`.

The connector and the CC wire
-----------------------------

A USB Type-C receptacle has 24 contacts. A port that only moves power uses
four kinds of them (:numref:`tab-usbpd-contacts`; :typec:`Table 3-4` and
:typec:`Section 4.2 <x>`):

.. list-table:: Type-C receptacle contacts used by a power-only port
   :name: tab-usbpd-contacts
   :header-rows: 1
   :widths: 15 25 60

   * - Signal
     - Contacts
     - Use
   * - VBUS
     - A4, A9, B4, B9
     - Power. Not driven by a source until it has detected a sink.
   * - GND
     - A1, A12, B1, B12
     - Power return.
   * - CC1
     - A5
     - Configuration channel, first position.
   * - CC2
     - B5
     - Configuration channel, second position.

The remaining contacts carry USB data and sideband signals. A board that does
not use USB data can leave them unconnected.

**Why there are two CC pins.** The plug can be inserted either way up. The
cable has only one CC wire, which in each plug is connected to contact A5.
Contact B5 of each plug is called VCONN and is not carried through to the
other end of the cable (:typec:`Section 2.5`; :typec:`Table 3-10 <x>`). Each
receptacle therefore has a CC contact in both positions, CC1 and CC2, and
only one of them meets the CC wire (:numref:`fig-usbpd-cc-wiring`). Which one
tells each side which way round the plug was inserted
(:typec:`Section 2.3.2`). A power-only port does not need the orientation
itself, but it must know which CC pin carries the CC wire, because that is
where messages arrive, and the source must know which pin is left over,
because that is where it supplies VCONN.

.. _fig-usbpd-cc-wiring:

.. graphviz:: cc-wiring.dot
   :caption: The single CC wire through a USB Type-C cable. In this example
             the plug at the sink end is turned over, so the source's CC1
             meets the sink's CC2. Each port's other CC pin meets the plug's
             VCONN contact, which is not connected to the far end.
   :align: center

Two layers of power negotiation
-------------------------------

1. **Resistor advertisement ("USB Type-C Current")**, described in
   `Layer 1: the resistor advertisement`_. The source's Rp value says how
   much current the sink may draw at 5 V: the default USB amount, 1.5 A or
   3.0 A. The sink measures the voltage on its CC pin. No messages are
   exchanged.
2. **USB Power Delivery messages**, described in
   `Layer 2: USB Power Delivery power levels`_ and the sections after it.
   Source and sink exchange messages on the CC wire. The source lists the
   voltages and currents it can supply and the sink asks for one. This is the
   only way to get more than 5 V or more than 3 A: the resistor
   advertisement stops at 3.0 A at 5 V, while USB Power Delivery goes up to
   48 V and 5 A (:typec:`Table 4-19`).
