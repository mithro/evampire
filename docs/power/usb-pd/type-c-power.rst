.. _usbpd-type-c-power:

Source, sink and the configuration channel
==========================================

What a USB Type-C power connection is made of: the two ends, the contacts
and wires they use, and the two ways in which they agree on power.

A powered :wikipedia:`USB-C` cable joins a :term:`source`, the end that
supplies power, to a :term:`sink`, the end that receives it. A
:term:`dual-role port` can act as either. Every USB Type-C port on a board
built around evampire is a dual-role port, because the board moves power
between Ethernet and USB Type-C in both directions (:ref:`power-roles`,
:ref:`req-power-bridging`).

.. _usbpd-connector:

Receptacle contacts
-------------------

A USB Type-C receptacle has two rows of 12 contacts, row A and row B, one
above the other (:numref:`fig-usbpd-receptacle`; :typec:`Section 3.2.3`,
:typec:`Table 3-4`). Each row is the other turned through 180°, so a plug
fits either way up and still meets a contact of the same kind. The power
contacts, :term:`VBUS` and ground (GND), each appear four times and are
joined together on the board.

.. graphviz:: receptacle.dot
   :name: fig-usbpd-receptacle
   :caption: The 24 contacts of a USB Type-C receptacle, front view turned on
             its side, with the contacts evampire uses in bold
             (:typec:`Figure 2-1`).
   :alt: Two columns of 12 contacts, row A on the left and row B on the
         right, each B contact beside the A contact it faces. From the top:
         A1 GND and B12 GND; A2 TX1+ and B11 RX1+; A3 TX1− and B10 RX1−;
         A4 VBUS and B9 VBUS; A5 CC1 and B8 SBU2; A6 D+ and B7 D−; A7 D− and
         B6 D+; A8 SBU1 and B5 CC2; A9 VBUS and B4 VBUS; A10 RX2− and B3 TX2−;
         A11 RX2+ and B2 TX2+; A12 GND and B1 GND. GND, VBUS, CC1, CC2, D+ and
         D− are in bold.
   :align: center

:numref:`tab-usbpd-contacts` lists what each group of contacts carries and
whether evampire uses it.

.. list-table:: USB Type-C receptacle contacts and their use on evampire
   :name: tab-usbpd-contacts
   :header-rows: 1
   :widths: 20 30 50

   * - Signal
     - Contacts
     - Use on evampire
   * - VBUS
     - A4, A9, B4, B9
     - Power, at 5 V or a negotiated voltage.
   * - GND
     - A1, A12, B1, B12
     - Power return.
   * - CC1, CC2
     - A5, B5
     - Configuration channel.
   * - D+, D−
     - A6, A7, B6, B7
     - USB 2.0 data for the USB serial port.
   * - TX and RX pairs
     - A2, A3, A10, A11, B2, B3, B10, B11
     - none
   * - SBU1, SBU2
     - A8, B8
     - none

The TX and RX pairs carry USB 3.2 and USB4 data, and the :term:`SBU`
contacts carry other signals, for example in alternate modes
(:typec:`Section 4.2`, :typec:`Section 4.3`). The D+ and D− contacts carry
the :ref:`USB serial port requirement <req-usb-serial>` (see :doc:`/usb-serial/index`).

CC wire and plug orientation
----------------------------

The :term:`configuration channel` (CC) is the wire on which the two ends
find each other, agree on power and exchange messages
(:typec:`Section 2.3`). The receptacle has two CC contacts, CC1 (A5) and CC2
(B5), but a standard cable carries only one CC wire
(:numref:`fig-usbpd-cc-wiring`; :typec:`Table 3-10`).

In each plug the CC wire lands on contact A5. Contact B5 of the plug is
called :term:`VCONN`. It powers any chip inside the plug and does not reach
the far end of the cable (:typec:`Section 2.5`, :typec:`Section 4.9`).
Depending on which way up the plug is inserted, the CC wire meets either the
receptacle's CC1 or its CC2 pin.

.. graphviz:: cc-wiring.dot
   :name: fig-usbpd-cc-wiring
   :caption: The single CC wire through a USB Type-C cable, with the plug at
             the sink end turned over so that the source's CC1 meets the
             sink's CC2.
   :alt: The source pulls CC1 and CC2 up with Rp and the sink pulls its CC1
         and CC2 down with Rd. The source's CC1 connects through plug 1's CC
         contact, the single CC wire and plug 2's CC contact to the sink's
         CC2. The source's CC2 and the sink's CC1 each meet only a VCONN
         contact that ends in the plug. VBUS and GND wires join the source's
         VBUS switch to the sink's VBUS input.
   :align: center

Which CC pin meets the CC wire tells each end the plug's orientation
(:typec:`Section 2.3.2`). evampire uses no TX or RX pairs, so it does not
need the orientation to route data. It does need to know which pin carries
the CC wire, because the messages arrive there. As a source, it also needs
to know which pin is left over, because it supplies VCONN on that pin when
the cable needs it (:ref:`usbpd-vconn`).

.. _usbpd-two-mechanisms:

Two power mechanisms
--------------------

The source and the sink agree on power in one of two ways, summarised in
:numref:`tab-usbpd-mechanisms` (:typec:`Table 2-1`).

.. list-table:: The two ways a USB Type-C source and sink agree on power
   :name: tab-usbpd-mechanisms
   :header-rows: 1
   :widths: 50 25 25

   * - Mechanism
     - Voltage (V)
     - Current (A)
   * - Resistor advertisement
     - 5
     - up to 3.0
   * - USB Power Delivery messages
     - 5 to 48
     - up to 5

The resistor advertisement (:doc:`resistor-advertisement`), which the
specification calls :term:`USB Type-C Current`, works without messages. The source connects a
:wikipedia:`pull-up <Pull-up_resistor>`, :term:`Rp`, to each CC pin and the
sink connects a pull-down, :term:`Rd`. The value of Rp tells the sink how
much current it may draw at 5 V: the default USB current, 1.5 A or 3.0 A.
The sink reads it by measuring the voltage on its CC pin.

:term:`USB Power Delivery` uses messages on the same CC wire. The source
lists the voltages and currents it can supply and the sink asks for one of
them (:doc:`power-levels`, :ref:`usbpd-negotiation`). It is the only way to get more than 5 V or
more than 3.0 A. It also lets the two ends swap roles while the cable stays
connected (:ref:`usbpd-role-changes`).

A third method, USB Battery Charging 1.2, signals a charger on the D+ and D−
wires. A USB Type-C source that supports it and can supply 1.5 A also
advertises 1.5 A with Rp (:typec:`Section 4.6.2.2`), so a sink that reads Rp
does not need to detect it.
