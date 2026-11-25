USB Power Delivery
==================

evampire's USB Type-C ports use :term:`USB Power Delivery` to agree on
power with the device at the other end of the cable.

Every USB Type-C port on a board built around evampire is a
:term:`dual-role port`: it can supply power as a :term:`source` or receive it
as a :term:`sink` (see :ref:`the power roles <power-roles>`). The software on
the RISC-V processor carries out the negotiation, as the
:ref:`power bridging requirements <req-power-bridging>` set out. The number of
ports in each board configuration is given in
:numref:`tab-power-board-configs`.

USB Power Delivery follows two specifications, linked from the
:doc:`standards page <../../standards>`: the
:std:`USB Type-C Cable and Connector Specification <usb-type-c>`
[USBPD-TYPEC]_, cited as "Type‑C", and the
:std:`USB Power Delivery Specification <usb-pd>` [USBPD-PD]_, cited as "PD". The specifications name each limit by its kind: names starting with
*t* are times, *v* voltages, *i* currents, *z* or *r* impedances, *c*
capacitances, *dc* duty cycles and *n* counts. Each limit here keeps its specification
name, so that it can be found there.

:doc:`port-power`
   The source, the sink and the configuration channel, the resistor
   advertisement, attaching, and the power available at start-up.
:doc:`contracts`
   Power levels, negotiating a contract, what the source and the sink each
   do, cables, and changing roles.
:doc:`messages`
   Packets and the electrical signal on the configuration channel.
:doc:`power-use`
   Offers from the Power over Ethernet budget, two ports, and monitoring the
   power.
:doc:`implementation`
   The processor's work, the analogue circuits, CC protection and the
   gf180mcu voltage limits.
:doc:`references`
   The specifications, datasheets and process documents cited for USB Power
   Delivery.

.. toctree::
   :hidden:

   port-power
   contracts
   messages
   power-use
   implementation
   references
