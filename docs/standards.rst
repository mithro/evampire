Standards
=========

The evampire design draws on standards for Ethernet, bridging and
discovery, USB, cabling, safety and electromagnetic compatibility,
integrated circuits, RGMII and RISC-V, each listed with a link to its
publisher. A reference such as "Clause 40.8.3.1" links to the entry for its
whole clause, Clause 40.

.. _std-802-3:

IEEE 802.3 (Ethernet)
---------------------

The Ethernet standard is IEEE Std 802.3-2022, *IEEE Standard for Ethernet*
(`standard page <https://standards.ieee.org/ieee/802.3/10422/>`_, see
:wikipedia:`IEEE 802.3 <IEEE_802.3>`). It is divided into numbered
clauses, each covering one part of Ethernet, and each clause into numbered
subclauses. A PDF copy
of the standard is available at no cost through the `IEEE GET Program
<https://standards.ieee.org/products-programs/ieee-get-program/>`_ (`IEEE 802
standards in the programme
<https://ieeexplore.ieee.org/browse/standards/get-program/page/series?id=68>`_),
after accepting its terms of use.

:numref:`tab-ieee8023-clauses` lists the cited clauses, each with its
title in IEEE Std 802.3-2022 and a description of what it covers.

.. list-table:: Cited IEEE 802.3 clauses
   :name: tab-ieee8023-clauses
   :header-rows: 1
   :widths: 20 80

   * - Clause
     - Title and what it covers
   * - .. _ieee8023-clause-3:

       Clause 3
     - *Media Access Control (MAC) frame and packet specifications*.

       The layout of an Ethernet frame: addresses, type or length field,
       payload and checksum.
   * - .. _ieee8023-clause-4:

       Clause 4
     - *Media Access Control*.

       Media access control: how a station sends and receives frames,
       including the minimum gap between frames.
   * - .. _ieee8023-clause-14:

       Clause 14
     - *Twisted-pair medium attachment unit (MAU) and baseband medium, type 10BASE-T including type 10BASE-Te*.

       10BASE-T: 10 Mbit/s over two twisted pairs, including the
       lower-amplitude 10BASE-Te variant and the isolation requirements for
       the cable connection.
   * - .. _ieee8023-clause-22:

       Clause 22
     - *Reconciliation Sublayer (RS) and Media Independent Interface (MII)*.

       The media independent interface (MII) between a media access
       controller and a transceiver, and the management interface (MDC and
       MDIO) with its standard registers.
   * - .. _ieee8023-clause-24:

       Clause 24
     - *Physical Coding Sublayer (PCS) and Physical Medium Attachment (PMA) sublayer, type 100BASE-X*.

       The coding layer of 100 Mbit/s Ethernet (4B5B coding) used by
       100BASE-TX.
   * - .. _ieee8023-clause-25:

       Clause 25
     - *Physical Medium Dependent (PMD) sublayer and baseband medium, type 100BASE-TX*.

       100BASE-TX: 100 Mbit/s over two twisted pairs, the signalling on the
       cable.
   * - .. _ieee8023-clause-28:

       Clause 28
     - *Physical Layer link signaling for Auto-Negotiation on twisted pair*.

       Autonegotiation on twisted-pair cable: the link pulses and the
       exchange that chooses the speed and duplex mode.
   * - .. _ieee8023-clause-33:

       Clause 33
     - *Power over Ethernet over 2 Pairs*.

       Power over Ethernet over two pairs (power types 1 and 2).
   * - .. _ieee8023-clause-35:

       Clause 35
     - *Reconciliation Sublayer (RS) and Gigabit Media Independent Interface (GMII)*.

       The gigabit media independent interface (GMII) between a media
       access controller and a transceiver.
   * - .. _ieee8023-clause-40:

       Clause 40
     - *Physical Coding Sublayer (PCS), Physical Medium Attachment (PMA) sublayer and baseband medium, type 1000BASE-T*.

       1000BASE-T: 1000 Mbit/s over four twisted pairs.
   * - .. _ieee8023-clause-79:

       Clause 79
     - *IEEE 802.3 Organizationally Specific Link Layer Discovery Protocol (LLDP) type, length, and value (TLV) information elements*.

       The Ethernet-specific information carried in link layer discovery
       protocol (LLDP) messages, including requests and offers of Power over
       Ethernet power.
   * - .. _ieee8023-clause-96:

       Clause 96
     - *Physical Coding Sublayer (PCS), Physical Medium Attachment (PMA) sublayer and baseband medium, type 100BASE-T1*.

       100BASE-T1: 100 Mbit/s over a single twisted pair.
   * - .. _ieee8023-clause-97:

       Clause 97
     - *Physical Coding Sublayer (PCS), Physical Medium Attachment (PMA) sublayer, and baseband medium, type 1000BASE-T1*.

       1000BASE-T1: 1000 Mbit/s over a single twisted pair.
   * - .. _ieee8023-clause-126:

       Clause 126
     - *Physical Coding Sublayer (PCS), Physical Medium Attachment (PMA) sublayer, and baseband medium, types 2.5GBASE-T and 5GBASE-T*.

       2.5GBASE-T and 5GBASE-T: 2.5 Gbit/s and 5 Gbit/s over four twisted
       pairs.
   * - .. _ieee8023-clause-145:

       Clause 145
     - *Power over Ethernet*.

       Power over Ethernet over two or four pairs (power types 1 to 4).
   * - .. _ieee8023-clause-146:

       Clause 146
     - *Physical Coding Sublayer (PCS), Physical Medium Attachment (PMA) sublayer and baseband medium, type 10BASE-T1L*.

       10BASE-T1L: 10 Mbit/s over a single twisted pair over long distances.
   * - .. _ieee8023-clause-147:

       Clause 147
     - *Physical Coding Sublayer (PCS), Physical Medium Attachment (PMA) sublayer and baseband medium, type 10BASE-T1S*.

       10BASE-T1S: 10 Mbit/s over a single twisted pair over short
       distances.

IEEE 802.1 (bridging and discovery)
-----------------------------------

The IEEE 802.1 standards are sold through the IEEE and are also available
at no cost through the IEEE GET Program, like IEEE 802.3.

.. _std-802-1ab:

IEEE 802.1AB (LLDP)
   IEEE Std 802.1AB-2026, *IEEE Standard for Local and Metropolitan Area
   Networks - Station and Media Access Control Connectivity Discovery*,
   published 2026-11-06. The link layer discovery protocol (LLDP), by which
   directly connected devices tell each other about themselves.
   `Standard page <https://standards.ieee.org/ieee/802.1AB/11787/>`__.

.. _std-802-1q:

IEEE 802.1Q (bridges and virtual networks)
   IEEE Std 802.1Q-2022, *IEEE Standard for Local and Metropolitan Area
   Networks--Bridges and Bridged Networks*, published 2022-12-22. Bridges and
   virtual networks (VLANs), including the 4-byte VLAN tag in a frame.
   `Standard page <https://standards.ieee.org/ieee/802.1Q/10323/>`__.

USB
---

The USB specifications are free to download from the USB Implementers
Forum document library. They are divided into numbered sections, tables and
figures. A reference such as "PD Table 5.10" or "Type-C Section 4.5.2.2"
links to the entry for the whole specification below. The number locates
the part within the PDF.

.. _usb-pd-specification:
.. _std-usb-pd:

USB Power Delivery Specification ("PD")
   Revision 3.3, Version 1.0, 2026-10-16. The messages, timing and power
   levels used to negotiate power over a USB Type-C cable (see
   :wikipedia:`USB Power Delivery <USB_Power_Delivery>`).
   `Document library page <https://www.usb.org/document-library/usb-power-delivery>`__
   (download ``USB_PD_R3.3_V1.0.zip``).

.. _usb-type-c-specification:
.. _std-usb-type-c:

USB Type-C Cable and Connector Specification ("Type-C")
   Release 2.5, 2026-03. The connector, the cable, and the configuration
   channel wires that detect a connection, its orientation and the basic
   current a source offers.
   `Document library page <https://www.usb.org/document-library/usb-type-cr-cable-and-connector-specification-release-25>`__
   (download ``USB Type-C 2.5 Release 202603``).

.. _std-usb3-2:

USB 3.2 Specification
   USB 3.2 Revision 1.1, June 2022. The USB 3.2 data connection, including
   the default VBUS current a USB 3.2 port offers.
   `Document library page <https://www.usb.org/document-library/usb-32-revision-11-june-2022>`__.

.. _std-usb2:

USB 2.0 Specification
   Revision 2.0, 2000-04-27, with errata and engineering change notices up
   to 2025-04-08. The USB data connection at low, full and high speed,
   including the full-speed (12 Mbit/s) signalling on the D+ and D− wires.
   `Document library page <https://www.usb.org/document-library/usb-20-specification>`__.

.. _std-usb-cdc:

USB Class Definitions for Communications Devices ("CDC")
   Revision 1.2, with errata and engineering change notices up to
   2025-04-03. The USB device class for communications devices. The same
   download holds the subclass for PSTN devices, which defines the abstract
   control model used by USB serial ports.
   `Document library page <https://www.usb.org/document-library/class-definitions-communication-devices-12>`__.

Cabling
-------

.. _std-tia-568:

TIA-568 (cabling, North America)
   ANSI/TIA-568.2-E, *Balanced Twisted-Pair Telecommunications Cabling and
   Components Standard*, 2024. The balanced twisted-pair cable categories
   (Category 5e, 6, 6A and 8), their channels, links and components. The
   TIA-568 series also covers the general cabling requirements.
   `TIA-568 set page <https://tiaonline.org/standard/tia-568/>`__.

.. _std-iso-iec-11801:

ISO/IEC 11801 (cabling, international)
   ISO/IEC 11801-1:2017, *Information technology - Generic cabling for
   customer premises - Part 1: General requirements*, Edition 1.0,
   2017-11-13, with Amendment 1 of 2025. The requirements common to every
   part of the ISO/IEC 11801 generic cabling series, including the cable
   classes and categories.
   `IEC webstore page <https://webstore.iec.ch/en/publication/26450>`__.

.. _std-x3-263:

ANSI X3.263 (FDDI over twisted pair)
   ANSI X3.263-1995, now designated ANSI INCITS 263-1995. The twisted-pair
   physical layer of the Fibre Distributed Data Interface (FDDI), whose
   MLT-3 line coding 100BASE-TX reuses (:clause:`25`).
   `ANSI webstore page <https://webstore.ansi.org/standards/incits/ansiincits2631995s2010>`__.

Safety and electromagnetic compatibility
----------------------------------------

.. _std-iec-60384-14:

IEC 60384-14 (safety capacitors)
   IEC 60384-14:2023. The safety classes (X and Y) of capacitors used for
   interference suppression and across the supply mains, including those
   that may bridge an isolation barrier.
   `IEC webstore page <https://webstore.iec.ch/publication/64361>`__.

.. _std-iec-62368-1:

IEC 62368-1 (equipment safety)
   IEC 62368-1:2023, *Audio/video, information and communication technology
   equipment - Part 1: Safety requirements*, Edition 4.0, 2023-05-26. Safety
   of information technology equipment, including the classes of electrical
   energy source and the safeguards against each.
   `IEC webstore page <https://webstore.iec.ch/en/publication/69308>`__.

.. _std-iec-61000-4-2:

IEC 61000-4-2 (electrostatic discharge)
   IEC 61000-4-2:2025, *Electromagnetic compatibility (EMC) - Part 4-2:
   Testing and measurement techniques - Electrostatic discharge immunity
   test*, Edition 3.0, 2025-03-07. The test of a whole product against
   electrostatic discharges to its case and connectors.
   `IEC webstore page <https://webstore.iec.ch/en/publication/68954>`__.

.. _std-iec-61000-4-4:

IEC 61000-4-4 (fast transients)
   IEC 61000-4-4:2012, *Electromagnetic compatibility (EMC) - Part 4-4:
   Testing and measurement techniques - Electrical fast transient/burst
   immunity test*, Edition 3.0, 2012-04-30. The test of a product against
   bursts of fast pulses coupled onto its power and signal cables.
   `IEC webstore page <https://webstore.iec.ch/en/publication/4222>`__.

.. _std-iec-61000-4-5:

IEC 61000-4-5 (surges)
   IEC 61000-4-5:2014, *Electromagnetic compatibility (EMC) - Part 4-5:
   Testing and measurement techniques - Surge immunity test*, Edition 3.0,
   2014-05-15, with Amendment 1 of 2017. The test of a product against
   high-energy surges, such as those caused by lightning, on its cables.
   `IEC webstore page <https://webstore.iec.ch/en/publication/4223>`__.

.. _std-fcc-part-15:

FCC Part 15 (radio emissions, United States)
   Title 47 of the Code of Federal Regulations, Part 15, *Radio Frequency
   Devices*. The limits on the radio-frequency energy that electronic
   equipment sold in the United States may emit.
   `Electronic Code of Federal Regulations page <https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15>`__.

Integrated circuits
-------------------

.. _std-js-001:

ANSI/ESDA/JEDEC JS-001 (human body model)
   ANSI/ESDA/JEDEC JS-001-2024, *ESDA/JEDEC Joint Standard for
   Electrostatic Discharge Sensitivity Testing – Human Body Model (HBM) –
   Device Level*. The test that classifies a chip by the electrostatic
   discharge from a person that its pins survive.
   `ESDA store page <https://www.esda.org/store/standards/product/392/ansiesdajedec-js-001-2024>`__.

.. _std-jesd8-5:

JEDEC JESD8-5 (2.5 V logic levels)
   JESD8-5A.01, 2007-09. The input and output voltage levels of digital
   interfaces with a 2.5 V supply, which RGMII version 1.3 uses.
   `JEDEC page <https://www.jedec.org/standards-documents/docs/jesd-8-5a01>`__.

.. _std-jesd8-6:

JEDEC JESD8-6 (HSTL logic levels)
   JESD8-6, 1995-08. High-speed transceiver logic (HSTL), digital
   interfaces with a 1.5 V output supply, which RGMII version 2.0 uses.
   `JEDEC page <https://www.jedec.org/standards-documents/docs/jesd-8-6>`__.

RGMII
-----

The RGMII specifications were published by Hewlett-Packard. The copies
linked below are kept by the Internet Archive.

.. _std-rgmii-1-3:

RGMII version 1.3
   *Reduced Gigabit Media Independent Interface (RGMII)*, Version 1.3,
   2000-12-10. The signals and timing of RGMII, with 2.5 V interface levels
   (:std:`JESD8-5`).
   `Archived PDF <http://web.archive.org/web/20160303212629/http://www.hp.com/rnd/pdfs/RGMIIv1_3.pdf>`__.

.. _std-rgmii-2-0:

RGMII version 2.0
   *Reduced Gigabit Media Independent Interface (RGMII)*, Version 2.0,
   2002-04-01. The signals and timing of RGMII, with HSTL interface levels
   (:std:`JESD8-6`) and the option of a clock delay inside the transmitter.
   `Archived PDF <http://web.archive.org/web/20160303171328/http://www.hp.com/rnd/pdfs/RGMIIv2_0_final_hp.pdf>`__.

RISC-V
------

The RISC-V specifications are published by RISC-V International and are
free to download from its
`specification library <https://docs.riscv.org/reference/isa/>`__.

.. _std-riscv-bitmanip:

RISC-V bit-manipulation extensions (Zba, Zbb, Zbc, Zbs)
   The bit-manipulation extensions to the RISC-V instruction set, including
   carry-less multiplication (Zbc), which speeds up CRC calculation.
   `riscv-bitmanip repository <https://github.com/riscv/riscv-bitmanip>`__.

.. _std-riscv-unpriv:

The RISC-V Instruction Set Manual, Volume I: Unprivileged Architecture
   Version 20260120. The instruction set that every RISC-V core runs,
   including the base 32-bit integer instruction set and its standard
   extensions.
   `Specification page <https://docs.riscv.org/reference/isa/v20260120/index.html>`__.

.. _std-riscv-priv:

The RISC-V Instruction Set Manual, Volume II: Privileged Architecture
   Version 20260120. The control registers, interrupts, exceptions and
   privilege levels of a RISC-V core.
   `Specification page <https://docs.riscv.org/reference/isa/v20260120/index.html>`__.
