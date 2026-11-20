Glossary
========

The terms used in this documentation, in alphabetical order. Each entry
gives a short description and a link to the full explanation.

.. glossary::
   :sorted:

   1000BASE-T
      Gigabit Ethernet over four twisted pairs, at 1000 Mbit/s
      (:clause:`40`). Every evampire port supports it (see
      :ref:`the transceiver requirements <req-transceivers>`).

   Class
      In Power over Ethernet, the power level that a powered device asks for
      during classification. Each class has a maximum power at the powered
      device (:clause:`145`, see :doc:`power/poe/index`).

   Configuration channel
   CC
      The two wires of a USB Type-C connector, CC1 and CC2, that detect a
      connection and its orientation, give the basic current a source
      offers, and carry the USB Power Delivery messages (see
      :doc:`power/usb-pd/index`).

   Cut-through forwarding
      Forwarding in which each byte of a frame is sent on a few clock cycles
      after it arrives, instead of after the whole frame has arrived. It
      needs only a few bytes of storage on each path (see
      :wikipedia:`Cut-through switching <Cut-through_switching>` and
      :ref:`the forwarding requirements <req-forwarding>`).

   Dual-role port
      A USB Type-C port that can attach as either a source or a sink, and
      can swap roles while connected (see :ref:`the power roles <power-roles>`).

   Ethernet transceiver
   PHY
      The circuit that drives and receives the electrical signals on an
      Ethernet cable. Ethernet documentation usually calls it a PHY, short
      for "physical layer device" (see
      :wikipedia:`Ethernet physical layer <Ethernet_physical_layer>` and
      :doc:`ethernet/phy-electrical/index`).

   Forwarding logic
      The logic in evampire that passes frames between port A and port B,
      copies selected frames to the processor and sends the processor's
      frames (see :doc:`architecture/index`).

   Frame
      One Ethernet message. A frame starts with the 6-byte destination
      address and the 6-byte source address, carries between 46 and
      1500 bytes of payload in a normal frame, and ends with a 4-byte
      checksum, the frame check sequence (:clause:`3`, see
      :wikipedia:`Ethernet frame <Ethernet_frame>`).

   Frame check sequence
   FCS
      The 4-byte checksum at the end of every Ethernet frame, which lets the
      receiver detect a damaged frame (:clause:`3`, see
      :wikipedia:`Frame check sequence <Frame_check_sequence>`).

   LLDP
   Link Layer Discovery Protocol
      The protocol that two directly connected Ethernet devices use to tell
      each other about themselves (:std:`IEEE 802.1AB <802.1AB>`). Power
      over Ethernet devices use it to negotiate power after classification
      (:clause:`79`, see
      :wikipedia:`Link Layer Discovery Protocol
      <Link_Layer_Discovery_Protocol>`).

   MAC address
      The 48-bit address that identifies a device on an Ethernet network.
      Every frame carries a destination MAC address and a source MAC address
      (:clause:`3`, see :wikipedia:`MAC address <MAC_address>`).

   Magnetics
      The coupling transformers between an Ethernet transceiver and the RJ45
      socket. They isolate the board from the cable and give a path for
      Power over Ethernet current (see :doc:`ethernet/magnetics/index`).

   MDIO
   Management data input/output
      The two-wire serial interface, a clock and a bidirectional data line,
      for reading and setting the registers of an Ethernet transceiver
      (:clause:`22`, see
      :wikipedia:`Management Data Input/Output
      <Management_Data_Input/Output>`).

   Media access controller
   MAC
      The generic Ethernet role that sends and receives frames on a link
      (:clause:`4`). In evampire the forwarding logic and the processor
      share this role.

   Power budget
      The power that the processor may offer on the output ports: the power
      granted on the input port, minus the board's own consumption and the
      conversion losses (see :ref:`the power budget <power-budget>`).

   Power over Ethernet
   PoE
      Power carried on the same cable as the Ethernet data, from power
      sourcing equipment to a powered device (:clause:`145`, see
      :wikipedia:`Power over Ethernet <Power_over_Ethernet>` and
      :doc:`power/poe/index`).

   Power sourcing equipment
   PSE
      The end of an Ethernet cable that supplies Power over Ethernet power
      (see :ref:`the power roles <power-roles>`).

   Powered device
      The end of an Ethernet cable that receives Power over Ethernet power.
      The Power over Ethernet standard abbreviates it as PD (see
      :ref:`the power roles <power-roles>`).

   RGMII
      Reduced Gigabit Media Independent Interface. A digital interface
      between a chip and an Ethernet transceiver: 4 data bits and one
      control signal in each direction, transferred on both edges of a
      125 MHz clock at gigabit speed (:std:`RGMII v2.0 <rgmii-2-0>`, see
      :doc:`ethernet/rgmii/index` and
      :wikipedia:`Media-independent interface
      <Media-independent_interface>`).

   GMII
   Gigabit media independent interface
      The interface between a media access controller and a gigabit Ethernet
      transceiver: 8 data bits in each direction on the rising edge of a
      125 MHz clock (:clause:`35`, see :doc:`ethernet/rgmii/signals`).

   In-band status
      The link status, speed and duplex that an Ethernet transceiver can put
      on the RGMII receive data signals between frames (see
      :doc:`ethernet/rgmii/data`).

   MII
   Media independent interface
      The interface between a media access controller and a 10 Mbit/s or
      100 Mbit/s Ethernet transceiver: 4 data bits in each direction on the
      rising edge of a 2.5 MHz or 25 MHz clock (:clause:`22`, see
      :doc:`ethernet/rgmii/signals`).

   Preamble
      The 7 bytes of alternating ones and zeros at the start of every
      Ethernet frame on the wire, which let the receiver lock on to the
      signal (:clause:`3.2.1`, see :doc:`ethernet/rgmii/frames`).

   Start frame delimiter
   SFD
      The byte 0xD5 that follows the preamble and marks the start of an
      Ethernet frame (:clause:`3.2.2`, see :doc:`ethernet/rgmii/frames`).

   RJ45
      The 8-position modular socket and plug used on Ethernet cables (see
      :wikipedia:`8P8C`).

   Sink
      The end of a USB Type-C cable that receives power (see
      :ref:`the power roles <power-roles>`).

   Source
      The end of a USB Type-C cable that supplies power (see
      :ref:`the power roles <power-roles>`).

   USB Power Delivery
   USB PD
      The protocol that negotiates voltage and current between the two ends
      of a USB Type-C cable over the configuration channel
      (:std:`USB Power Delivery Specification <usb-pd>`, see
      :wikipedia:`USB Power Delivery <USB_Power_Delivery>` and
      :doc:`power/usb-pd/index`).

   USB Type-C
      The reversible 24-pin USB connector and its cable
      (:std:`USB Type-C Specification <usb-type-c>`, see
      :wikipedia:`USB-C`).

   VBUS
      The wire of a USB connector that carries power from the source to the
      sink (see :doc:`power/usb-pd/index`).

   VLAN tag
      An optional 4-byte field in an Ethernet frame that marks the frame as
      belonging to one of several virtual networks sharing the same cable
      (:std:`IEEE 802.1Q <802.1Q>`, see
      :wikipedia:`VLAN tagging <IEEE_802.1Q>`).

   Analogue-to-digital converter
   ADC
      A circuit that measures a voltage and gives it as a number (see
      :wikipedia:`Analog-to-digital_converter`).

   Bandgap reference
      A circuit whose output voltage stays steady as supply and temperature
      change, built from bipolar transistors (see
      :wikipedia:`Bandgap_voltage_reference`).

   Biphase mark coding
   BMC
      The line code that carries USB Power Delivery messages on the
      configuration channel. The level changes at the start of every bit, and
      again in the middle of a 1 (see
      :wikipedia:`Differential_Manchester_encoding` and
      :doc:`power/usb-pd/cc-signalling`).

   Comparator
      A circuit that compares a voltage with a threshold and gives a logic 1
      or 0 (see :wikipedia:`Comparator`).

   Contract
   Explicit contract
      In USB Power Delivery, the agreement between source and sink on the
      voltage and current. Before any message, the sink may draw the current
      the source's Rp advertises; after an explicit contract it may draw the
      current it requested (see :doc:`power/usb-pd/negotiation`).

   Data role
   DFP
   UFP
      In USB, the downstream facing port (DFP, the host side for data) or the
      upstream facing port (UFP, the device side). A port that attaches as a
      source starts as DFP, and one that attaches as a sink starts as UFP
      (see :doc:`power/usb-pd/role-changes`).

   Digital-to-analogue converter
   DAC
      A circuit that turns a number into a voltage or current (see
      :wikipedia:`Digital-to-analog_converter`).

   Discover Identity
      The USB Power Delivery message with which a port asks a cable plug, or
      the other port, for its identity and ratings (see
      :doc:`power/usb-pd/cables`).

   E-marker
      The chip inside an electronically marked USB Type-C cable plug. It
      reports the cable's current and voltage rating when asked with
      Discover Identity (see :doc:`power/usb-pd/cables`).

   Electrostatic discharge
   ESD
      A short high-voltage pulse from a charged person or object touching a
      pin (see :wikipedia:`Electrostatic_discharge` and
      :doc:`power/usb-pd/cc-protection`).

   Extended power range
   EPR
      The USB Power Delivery power levels above 100 W, with fixed supplies of
      28 V, 36 V and 48 V at up to 5 A (see
      :doc:`power/usb-pd/power-levels`).

   Fast role swap
   FRS
      A USB Power Delivery mechanism with which a sink takes over as source
      within a few hundred microseconds when the source's own power fails
      (see :doc:`power/usb-pd/role-changes`).

   FIFO
      A first-in, first-out buffer (see
      :wikipedia:`FIFO <FIFO_(computing_and_electronics)>`).

   gf180mcu
      The open 180 nm CMOS process from GlobalFoundries on which evampire is
      built, with transistors for 3.3 V, 5 V, 6 V and 10 V (see
      :ref:`the process requirement <req-process>` and
      :doc:`power/usb-pd/on-chip-or-external`).

   GoodCRC
      The short USB Power Delivery message with which a port acknowledges
      every message it receives with a correct checksum (see
      :doc:`power/usb-pd/negotiation`).

   Hard Reset
      A USB Power Delivery signal, not a message, that makes both ports
      return their supplies to the default state and start the negotiation
      again (see :doc:`power/usb-pd/role-changes`).

   Human body model
   HBM
      The standard test pulse for rating a chip pin's protection against
      electrostatic discharge: a 100 pF capacitor discharged through
      1.5 kΩ (:std:`JS-001`, see :wikipedia:`Human-body_model`).

   LDMOS
      A laterally diffused MOS transistor: a transistor with an extended,
      lightly doped drain that holds off a higher drain voltage than a
      standard transistor (see :wikipedia:`LDMOS`).

   MIM capacitor
      A metal-insulator-metal capacitor, built between two metal layers of a
      chip.

   MOSFET
   NMOS
   PMOS
      The metal-oxide-semiconductor field-effect transistor, in its
      N-channel (NMOS) and P-channel (PMOS) forms (see
      :wikipedia:`MOSFET`).

   PDO
   Power data object
      A 32-bit word in which a USB Power Delivery source describes one
      supply it offers, for example 9 V at up to 3 A (see
      :doc:`power/usb-pd/power-levels`).

   Process design kit
   PDK
      The device models, layout rules and cell libraries published for a
      chip manufacturing process (see :wikipedia:`Process_design_kit`).

   Programmable power supply
   PPS
      A USB Power Delivery supply whose voltage the sink sets in 20 mV steps
      within a range the source offers (see
      :doc:`power/usb-pd/power-levels`).

   Rd
      The 5.1 kΩ pull-down that a USB Type-C sink connects to its CC pins
      (see :doc:`power/usb-pd/resistor-advertisement`).

   RDO
   Request data object
      A 32-bit word in which a USB Power Delivery sink asks for one of the
      offered supplies (see :doc:`power/usb-pd/power-levels`).

   Rp
      The pull-up, a resistor or a current source, that a USB Type-C source
      connects to its CC pins. Its value tells the sink how much current it
      may draw (see :doc:`power/usb-pd/resistor-advertisement`).

   Ra
      The 800 Ω to 1.2 kΩ pull-down inside a powered USB Type-C cable plug,
      on the pin that receives VCONN (see :doc:`power/usb-pd/cables`).

   SBU
   Sideband use
      Two contacts of the USB Type-C connector reserved for other signals,
      for example in alternate modes. evampire does not use them.

   SOP
   Start of packet
      The 20-bit pattern at the start of each USB Power Delivery message. It
      marks the start and says who the message is for: the other port (SOP)
      or a cable plug (SOP′ or SOP″) (see :doc:`power/usb-pd/packets`).

   Standard power range
   SPR
      The USB Power Delivery power levels up to 100 W, with fixed supplies
      of 5 V, 9 V, 15 V and 20 V at up to 5 A (see
      :doc:`power/usb-pd/power-levels`).

   Transient voltage suppressor
   TVS
      A diode that clamps a voltage surge by conducting above its breakdown
      voltage (see :wikipedia:`Transient-voltage-suppression_diode`).

   Unit interval
   UI
      The duration of one bit on the configuration channel, about 3.3 µs
      (see :doc:`power/usb-pd/cc-signalling`).

   USB Implementers Forum
   USB-IF
      The organisation that publishes the USB specifications (see
      `usb.org <https://www.usb.org/>`__).

   VCONN
      The supply that a USB Type-C port puts on its unused CC pin to power the
      chip inside a cable plug, 3.0 V to 5.5 V (see
      :doc:`power/usb-pd/cables`).

   VDO
   Vendor data object
      A 32-bit data word in a USB Power Delivery Vendor_Defined message. A
      cable's answer to Discover Identity is made of VDOs (see
      :doc:`power/usb-pd/cables`).

   USB Type-C Current
      The current a USB Type-C source advertises to a sink at 5 V through
      the value of its pull-up, Rp, without any messages: the default USB
      current, 1.5 A or 3.0 A (see
      :doc:`power/usb-pd/resistor-advertisement`).

   Input capture
      A timer feature that copies a free-running counter into a register on
      each edge of an input, giving the edge a timestamp in hardware (see
      :ref:`usbpd-helpers`).

   Output compare
      A timer feature that changes an output when a free-running counter
      reaches the value in a compare register, placing an edge at a set time
      in hardware (see :ref:`usbpd-helpers`).
