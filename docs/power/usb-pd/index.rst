USB Power Delivery
==================

How evampire's USB Type-C ports agree on power with the device at the other
end, using :term:`USB Power Delivery`, and the circuits evampire needs to do
it.

Every USB Type-C port on a board built around evampire is a
:term:`dual-role port`: it can supply power as a :term:`source` or receive it
as a :term:`sink` (see :ref:`the power roles <power-roles>`). The software on
the RISC-V processor carries out the negotiation, as the
:ref:`power bridging requirements <req-power-bridging>` set out. The number of
ports in each board configuration is given in
:numref:`tab-power-board-configs`.

The pages quote two specifications, linked from the
:doc:`standards page <../../standards>`: the
:std:`USB Type-C Cable and Connector Specification <usb-type-c>` (cited as
"Type‑C") and the :std:`USB Power Delivery Specification <usb-pd>` (cited as
"PD"). The specifications name each limit by its kind: names starting with
*t* are times, *v* voltages, *i* currents, *z* or *r* impedances, *c*
capacitances, *dc* duty cycles and *n* counts. The pages use the same names,
so that each can be found in the specifications.

How a USB Type-C port gets power
--------------------------------

:doc:`type-c-power`
   The source, the sink, the connector and the configuration channel wires.
:doc:`resistor-advertisement`
   How the source's pull-up tells the sink how much current it may draw at
   5 V.
:doc:`attach`
   How two dual-role ports find each other and settle on who supplies power.
:doc:`start-up`
   The power a USB Type-C charger makes available before any negotiation.

How the two ends agree on more power
------------------------------------

:doc:`power-levels`
   The voltages and currents USB Power Delivery offers, and the messages that
   carry offers and requests.
:doc:`negotiation`
   The message exchange that sets up a power contract, and its time limits.
:doc:`source-sink`
   What the source and the sink each do to set up and keep a contract.
:doc:`cables`
   How a port powers and queries the chip inside a marked cable.
:doc:`role-changes`
   Swapping the power role, the data role and VCONN, fast role swap, and
   Hard Reset.

How evampire uses the power
---------------------------

:doc:`power-translation`
   The USB source offers that fit the power granted by Power over Ethernet.
:doc:`two-ports`
   Sharing the power budget between two USB Type-C ports.
:doc:`monitoring`
   Measuring and limiting the power on each port.

How the messages are carried
----------------------------

:doc:`packets`
   How a message is framed, coded and checked.
:doc:`cc-signalling`
   The electrical signal on the configuration channel.

What evampire needs to build it
-------------------------------

:doc:`software`
   What the processor must do to send and receive messages, and the
   hardware helpers that reduce it.
:doc:`analogue`
   The analogue circuits for one port.
:doc:`cc-protection`
   Protecting the CC pins against a short to VBUS, and how that differs
   from electrostatic discharge.
:doc:`on-chip-or-external`
   The gf180mcu voltage limits, and which circuits can be on the chip.
:doc:`references`
   The documents cited on these pages.

.. toctree::
   :hidden:

   type-c-power
   resistor-advertisement
   attach
   start-up
   power-levels
   negotiation
   source-sink
   cables
   role-changes
   power-translation
   two-ports
   monitoring
   packets
   cc-signalling
   software
   analogue
   cc-protection
   on-chip-or-external
   references
