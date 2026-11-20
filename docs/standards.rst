Standards
=========

This page lists the parts of the standards that the rest of the
documentation refers to. A reference such as "Clause 40.8.3.1" links to the
entry for the whole clause (here, Clause 40) on this page.

IEEE 802.3 (Ethernet)
---------------------

The Ethernet standard is IEEE Std 802.3-2022, *IEEE Standard for Ethernet*
(`standard page <https://standards.ieee.org/ieee/802.3/10422/>`_). It is
divided into numbered clauses, each covering one part of Ethernet, and each
clause into numbered subclauses. A PDF copy of the standard is available at
no cost through the `IEEE GET Program
<https://standards.ieee.org/products-programs/ieee-get-program/>`_ (`IEEE 802
standards in the programme
<https://ieeexplore.ieee.org/browse/standards/get-program/page/series?id=68>`_),
after accepting its terms of use.

The short descriptions below say what each clause covers, in the terms used
in this documentation. The exact clause titles are given in the standard.

.. _ieee8023-clause-3:

Clause 3
   The layout of an Ethernet frame: addresses, type or length field,
   payload and checksum.

.. _ieee8023-clause-4:

Clause 4
   Media access control: how a station sends and receives frames, including
   the minimum gap between frames.

.. _ieee8023-clause-14:

Clause 14
   10BASE-T: 10 Mbit/s over two twisted pairs, including the lower-amplitude
   10BASE-Te variant and the isolation requirements for the cable
   connection.

.. _ieee8023-clause-22:

Clause 22
   The media independent interface (MII) between a controller and a
   transceiver, and the management interface (MDC/MDIO) with its standard
   registers.

.. _ieee8023-clause-24:

Clause 24
   The coding layer of 100 Mbit/s Ethernet (4B5B coding) used by
   100BASE-TX.

.. _ieee8023-clause-25:

Clause 25
   100BASE-TX: 100 Mbit/s over two twisted pairs, the signalling on the
   cable.

.. _ieee8023-clause-28:

Clause 28
   Autonegotiation on twisted-pair cable: the link pulses and the exchange
   that chooses the speed and duplex mode.

.. _ieee8023-clause-33:

Clause 33
   Power over Ethernet over two pairs (power types 1 and 2).

.. _ieee8023-clause-35:

Clause 35
   The gigabit media independent interface (GMII) between a controller and a
   transceiver.

.. _ieee8023-clause-40:

Clause 40
   1000BASE-T: 1000 Mbit/s over four twisted pairs.

.. _ieee8023-clause-79:

Clause 79
   The Ethernet-specific information carried in link layer discovery
   protocol (LLDP) messages, including requests and offers of Power over
   Ethernet power.

.. _ieee8023-clause-96:

Clause 96
   100BASE-T1: 100 Mbit/s over a single twisted pair.

.. _ieee8023-clause-97:

Clause 97
   1000BASE-T1: 1000 Mbit/s over a single twisted pair.

.. _ieee8023-clause-126:

Clause 126
   2.5GBASE-T and 5GBASE-T: 2.5 Gbit/s and 5 Gbit/s over four twisted
   pairs.

.. _ieee8023-clause-145:

Clause 145
   Power over Ethernet over two or four pairs (power types 1 to 4).

.. _ieee8023-clause-146:

Clause 146
   10BASE-T1L: 10 Mbit/s over a single twisted pair over long distances.

.. _ieee8023-clause-147:

Clause 147
   10BASE-T1S: 10 Mbit/s over a single twisted pair over short distances.

USB
---

Both USB specifications are free to download from the USB Implementers
Forum document library, each as a zip file containing the PDF. They are
divided into numbered sections, tables and figures. A reference such as
"PD Table 5.10" or "Type-C Section 4.5.2.2" links to the entry for the whole
specification below; the number locates the part within the PDF.

.. _usb-pd-specification:

USB Power Delivery Specification ("PD")
   Revision 3.3, Version 1.0, 2026-10-16. The messages, timing and power
   levels used to negotiate power over a USB Type-C cable.
   `Document library page <https://www.usb.org/document-library/usb-power-delivery>`__
   (download ``USB_PD_R3.3_V1.0.zip``).

.. _usb-type-c-specification:

USB Type-C Cable and Connector Specification ("Type-C")
   Release 2.5, March 2026. The connector, the cable, and the configuration
   channel wires that detect a connection, its orientation and the basic
   current a source offers.
   `Document library page <https://www.usb.org/document-library/usb-type-cr-cable-and-connector-specification-release-25>`__
   (download ``USB Type-C 2.5 Release 202603``).
