Glossary
========

.. glossary::
   :sorted:

   Avalanche breakdown
      The sudden rise in current through a reverse-biased junction when the
      field in its depletion region is strong enough for carriers to free
      more carriers (see :wikipedia:`Avalanche_breakdown` and
      :ref:`hv-junctions`).

   Depletion region
      The layer either side of a P-N junction that is emptied of free
      carriers, across which a reverse-biased junction holds its voltage
      (see :wikipedia:`Depletion_region` and :ref:`hv-junctions`).

   Field plate
      A conductor over the insulator beside a junction's edge, held at the
      junction's voltage, which spreads the field and raises the breakdown
      voltage of the edge (see :ref:`hv-grading`).

   Floating field ring
      A ring of doped silicon around a high-voltage junction, connected to
      nothing, that takes part of the voltage as the depletion region
      reaches it (see :ref:`hv-grading`).

   RESURF
      Reduced surface field: a thin, lightly doped layer depleted from below
      as well as from its edge, so that the voltage falls evenly along the
      surface (see :ref:`hv-grading`).

   Silicon on insulator
      SOI
      A wafer with a layer of oxide under the silicon in which devices are
      built, so that each device can be isolated by insulator on every side
      (see :wikipedia:`Silicon_on_insulator` and :ref:`hv-dielectric`).

   Substrate
      The slab of silicon on which every device of a chip is built. In
      gf180mcu it is P-type and held at the lowest voltage on the chip (see
      :ref:`hv-substrate`).

   1000BASE-T
      Gigabit Ethernet over four twisted pairs, at 1000 Mbit/s
      (:clause:`40`). Every evampire port supports it (see
      :ref:`the transceiver requirements <req-transceivers>`).

   Autonegotiation
      The exchange of link pulse bursts by which the two transceivers on a
      twisted-pair Ethernet cable agree on speed, duplex mode and, for
      1000BASE-T, which end is master (:clause:`28`, see
      :doc:`the autonegotiation page <ethernet/phy-electrical/autonegotiation>` and
      :wikipedia:`Autonegotiation`).

   Baseline wander
      A slow drift of the average level of a received signal, caused when a
      high-pass filter in the path, such as a transformer or coupling
      capacitor, removes the low-frequency part of the data (see
      :doc:`ethernet/magnetics/matching-and-droop`).

   Bob Smith termination
      A network of 75 Ω resistors from each pair's centre tap to a shared
      capacitor to chassis ground, which absorbs common-mode currents on an
      Ethernet cable (see :doc:`ethernet/magnetics/functions`).

   Centre tap
      A connection to the middle of a transformer or inductor winding (see
      :doc:`ethernet/magnetics/standard-port`).

   Class
      In Power over Ethernet, a power level. The powered device requests a
      class during classification and the power sourcing equipment assigns
      one, which may be lower. Each class has a maximum power at the
      powered device (:clause:`145`, see :doc:`power/poe/types-classes`).

   Class event
      A step of Power over Ethernet classification in which the power
      sourcing equipment holds the cable at 15.5 V to 20.5 V and the powered
      device answers with a fixed current, its class signature
      (:clause:`145.2.8`, see :doc:`power/poe/sequence`).

   Common-mode choke
      Two windings on one core, one in each wire of a pair, that block
      current flowing the same way on both wires while passing the
      differential signal (see :doc:`ethernet/magnetics/functions` and
      :wikipedia:`Choke (electronics) <Choke_(electronics)>`).

   Common-mode voltage
      The average voltage of the two wires of a pair, measured against a
      ground. It carries no data (see :doc:`ethernet/magnetics/functions`
      and :wikipedia:`Common-mode signal <Common-mode_signal>`).

   Configuration channel
   CC
      The two wires of a USB Type-C connector, CC1 and CC2, that detect a
      connection and its orientation, give the basic current a source
      offers, and carry the USB Power Delivery messages (see
      :doc:`power/usb-pd/index`).

   Crosstalk
   NEXT
   FEXT
      Signal coupled from one pair of a cable into another. Near-end
      crosstalk (NEXT) comes from a transmitter at the same end as the
      receiver it disturbs; far-end crosstalk (FEXT) from one at the other
      end (:clause:`40.7.3`, see :doc:`ethernet/phy-electrical/job` and
      :wikipedia:`Crosstalk`).

   Cut-through forwarding
      Forwarding in which each byte of a frame is sent on a few clock cycles
      after it arrives, instead of after the whole frame has arrived. It
      needs only a few bytes of storage on each path (see
      :wikipedia:`Cut-through switching <Cut-through_switching>` and
      :ref:`the forwarding requirements <req-forwarding>`).

   Data Link Layer classification
      Changing the power allocation of a powered device after the link is
      up, in steps of 0.1 W, by exchanging LLDP frames (:clause:`145.5`,
      see :doc:`power/poe/lldp` and :doc:`power/poe/classification`).

   Detection signature
      The resistance of about 25 kΩ that a powered device shows at 2.7 V to
      10.1 V, so that power sourcing equipment can tell that a powered
      device is connected (:clause:`145.3.4`, see
      :doc:`power/poe/powered-device`).

   Differential-mode voltage
      The voltage difference between the two wires of a pair, which carries
      the data (see :doc:`ethernet/magnetics/cable` and
      :wikipedia:`Differential signalling <Differential_signalling>`).

   Droop
      The decay of a transmitted voltage that is held constant, caused by a
      high-pass filter in the path. IEEE 802.3 limits it for 1000BASE-T
      transmitters (:clause:`40.6.1.2.2`, see
      :doc:`ethernet/magnetics/matching-and-droop`).

   Dual-role port
      A USB Type-C port that can attach as either a source or a sink, and
      can swap roles while connected (see :ref:`the power roles <power-roles>`).

   Inrush current
      The current that flows when a supply is first switched on and the
      input capacitors charge. Power over Ethernet limits it for the first
      50 ms to 75 ms (:clause:`145.2.10.7`, see
      :wikipedia:`Inrush current <Inrush_current>` and
      :doc:`power/poe/power-sourcing`).

   Isolation switch
      The switch in a powered device that keeps its converter and input
      capacitor disconnected from the cable until the turn-on voltage, then
      connects them with a limited current (see
      :doc:`power/poe/pd-controller`).

   Equaliser
      A filter whose response is the inverse of the cable's, so that the
      received symbols no longer overlap. Gigabit receivers adapt it to each
      cable (see :doc:`ethernet/phy-electrical/1000base-t-receiver` and
      :wikipedia:`Equalization (communications)
      <Equalization_(communications)>`).

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

   Hybrid
      The analogue circuit that lets one pair carry both directions at once,
      by subtracting a replica of the transceiver's own transmitted signal
      from the voltage on the pair (see
      :doc:`ethernet/phy-electrical/1000base-t-echo`).

   Insertion loss
      How much smaller a signal becomes, in decibels, by passing through a
      cable or component. In a cable it grows with frequency and length
      (:clause:`40.7.2.1`, see :doc:`ethernet/phy-electrical/job` and
      :wikipedia:`Insertion loss`).

   Galvanic isolation
      The absence of any conducting path between two circuits, so that no
      direct current flows between them and a large voltage between them
      does no harm (see :wikipedia:`Galvanic isolation
      <Galvanic_isolation>` and :doc:`ethernet/magnetics/functions`).

   GMII
   Gigabit media independent interface
      The interface between a media access controller and a gigabit Ethernet
      transceiver: 8 data bits in each direction on the rising edge of a
      125 MHz clock (:clause:`35`, see :doc:`ethernet/rgmii/signals`).

   In-band status
      The link status, speed and duplex that an Ethernet transceiver can put
      on the RGMII receive data signals between frames (see
      :doc:`ethernet/rgmii/data`).

   LLDP
   Link Layer Discovery Protocol
      The protocol that two directly connected Ethernet devices use to tell
      each other about themselves (:std:`IEEE 802.1AB <802.1AB>`). Power
      over Ethernet devices use it for Data Link Layer classification, which
      changes the power after the link is up (:clause:`79`, see
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

   Maintain power signature
      The minimum current that a powered device keeps drawing once powered,
      so that the power sourcing equipment keeps the power on
      (:clause:`145.3.9`, see :doc:`power/poe/sequence`).

   Mark event
      A step of Power over Ethernet classification, between class events,
      in which the cable is held at 7 V to 10 V and the powered device draws
      a small current (:clause:`145.2.8.1`, see
      :doc:`power/poe/sequence`).

   MDI
   Medium dependent interface
      The connection between an Ethernet transceiver and the cable: the
      contacts of the socket and the electrical requirements on them. Also
      the name of the pin assignment in which a port transmits on contacts
      1 and 2 (see :doc:`ethernet/magnetics/cable`).

   MDI-X
      The crossed pin assignment, in which a port transmits on the contacts
      where an MDI port receives (see :doc:`ethernet/magnetics/cable`).

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

   Mutual identification
      The part of Power over Ethernet classification in which power
      sourcing equipment and a powered device each learn the type of the
      other (:clause:`145.2.8`, see :doc:`power/poe/classification`).

   Pair set
      Two pairs of an Ethernet cable, one positive and one negative, that
      carry Power over Ethernet current out and back (see
      :doc:`power/poe/basics`).

   PAM-5
      Five-level pulse amplitude modulation: each symbol is one of the
      levels −2, −1, 0, +1 and +2. 1000BASE-T uses it on all four pairs
      (:clause:`40.1.3`, see :doc:`ethernet/phy-electrical/1000base-t-coding`
      and :wikipedia:`Pulse-amplitude modulation
      <Pulse-amplitude_modulation>`).

   MII
   Media independent interface
      The interface between a media access controller and a 10 Mbit/s or
      100 Mbit/s Ethernet transceiver: 4 data bits in each direction on the
      rising edge of a 2.5 MHz or 25 MHz clock (:clause:`22`, see
      :doc:`ethernet/rgmii/signals`).

   Physical Layer classification
      Power over Ethernet classification by class events before the
      operating voltage is switched on. The number of class events and the
      class signatures decide the assigned class (:clause:`145.2.8`, see
      :doc:`power/poe/sequence` and :doc:`power/poe/classification`).

   Power budget
      The power that the processor may offer on the output ports: the power
      granted on the input port, minus the board's own consumption and the
      conversion losses (see :ref:`the power budget <power-budget>`).

   Power demotion
      Assigning a powered device a lower class than it requested, by
      issuing fewer class events, when power sourcing equipment cannot
      supply the requested class. The name comes from the Ethernet
      Alliance; the standard describes it without naming it
      (:clause:`145.2.8.1`, :clause:`Table 145-11 <145>`, see
      :ref:`poe-demotion`).

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

   Return loss
      How much weaker, in decibels, a reflection is than the signal that
      caused it. A port matched to the cable has a high return loss. IEEE
      802.3 sets a minimum for each Ethernet port (:clause:`40.8.3.1`, see
      :doc:`ethernet/phy-electrical/job`,
      :doc:`ethernet/magnetics/matching-and-droop` and
      :wikipedia:`Return loss <Return_loss>`).

   Preamble
      The 7 bytes of alternating ones and zeros at the start of every
      Ethernet frame on the wire, which let the receiver lock on to the
      signal (:clause:`3.2.1`, see :doc:`ethernet/rgmii/frames`).

   RGMII
      Reduced Gigabit Media Independent Interface. A digital interface
      between a chip and an Ethernet transceiver: 4 data bits and one
      control signal in each direction, transferred on both edges of a
      125 MHz clock at gigabit speed (:std:`RGMII v2.0 <rgmii-2-0>`, see
      :doc:`ethernet/rgmii/index` and
      :wikipedia:`Media-independent interface
      <Media-independent_interface>`).

   RJ45
      The 8-position modular socket and plug used on Ethernet cables (see
      :wikipedia:`8P8C`).

   Sink
      The end of a USB Type-C cable that receives power (see
      :ref:`the power roles <power-roles>`).

   Source
      The end of a USB Type-C cable that supplies power (see
      :ref:`the power roles <power-roles>`).

   Type (Power over Ethernet)
      One of four sets of rules for Power over Ethernet equipment. Types 1
      and 2 are specified in :clause:`33`, Types 3 and 4 in :clause:`145`
      (see :doc:`power/poe/types-classes`).

   Symbol
      One voltage level held on a pair for one fixed time slot. Depending on
      how many levels are allowed, it carries less than one bit, one bit or
      several bits (see :doc:`ethernet/phy-electrical/job` and
      :wikipedia:`Symbol rate`).

   Symbol rate
      The number of symbols sent per second on one pair, in baud (Bd).
      100BASE-TX and 1000BASE-T both run at 125 MBd (see
      :doc:`ethernet/phy-electrical/job` and :wikipedia:`Symbol rate`).

   Trellis code
      An error-correcting code in which a small state machine in the
      transmitter allows only some sequences of symbols, so that the
      receiver can pick the closest legal sequence. 1000BASE-T uses one
      with eight states (:clause:`40.3.1.3.4`, see
      :doc:`ethernet/phy-electrical/1000base-t-coding` and
      :wikipedia:`Trellis modulation <Trellis_modulation>`).

   Start frame delimiter
   SFD
      The byte 0xD5 that follows the preamble and marks the start of an
      Ethernet frame (:clause:`3.2.2`, see :doc:`ethernet/rgmii/frames`).

   Twisted pair
      Two wires twisted around each other and carrying equal and opposite
      signals. An Ethernet cable holds four (see
      :wikipedia:`Twisted pair <Twisted_pair>` and
      :doc:`ethernet/magnetics/cable`).

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
      :doc:`esd/index`).

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

   Charged device model
   CDM
      The ESD test in which the chip itself is charged and then discharged
      through one pin to ground, in under a nanosecond (see
      :doc:`esd/events`).

   Latch-up
      A short circuit between a chip's supply and ground through the
      parasitic thyristor formed by neighbouring N-wells and P-wells, which
      persists until the power is removed (see :wikipedia:`Latch-up`).

   Rail clamp
      A circuit between a chip's supply ring and ground ring that turns on
      during a fast ESD event and carries its current at a few volts (see
      :doc:`esd/io-cells`).

   Second breakdown current
   It2
      The current at which an ESD device fails by overheating in a
      transmission line pulse test, usually given per micrometre of device
      width (see :doc:`esd/io-cells`).

   Snapback
      The drop in voltage across an NMOS transistor when the parasitic
      bipolar transistor formed by its drain, body and source turns on in
      avalanche breakdown (see :doc:`esd/io-cells`).

   Transmission line pulse
   TLP
      A measurement of an ESD device with rectangular pulses, typically
      100 ns long, at rising current, recording the voltage and leakage after
      each pulse (see :doc:`esd/io-cells`).

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

   K-code
      In USB Power Delivery, one of six 5-bit symbols that never stand for
      data. K-codes mark the start of a packet, a reset and the end of a
      packet (:pd:`Table 5.2`, see :ref:`usbpd-4b5b`).

   Managed Capability Port
      A USB Power Delivery source port whose present power, the Port Present
      PDP, may be lower than its maximum and may change during operation, for
      example because it shares one supply with other ports
      (:pd:`Section 3.2.3`, see :doc:`power/usb-pd/two-ports`).

   Adjustable voltage supply
   AVS
      In USB Power Delivery, a supply whose voltage the sink sets in 100 mV
      steps, from 9 V to 20 V in the standard power range and from 15 V to
      48 V in the extended power range (:pd:`Table 4.3`, :pd:`Table 4.4`;
      see :ref:`usbpd-power-levels`).

   PDP
   PD Power
      In USB Power Delivery, the output power of a source or the input power
      of a sink. A source reports its Port Maximum PDP, the most it will
      ever provide, and its Port Present PDP, what it can provide at present
      (:pd:`Table 6.29`; see :ref:`usbpd-building-offer`).

   BVCEO
      The collector-to-emitter breakdown voltage of a bipolar transistor with
      its base left open (see :wikipedia:`breakdown voltage
      <Breakdown_voltage>` and :ref:`usbpd-process-limits`).

   BVDSS
      The drain-to-source breakdown voltage of a transistor that is switched
      off (see :wikipedia:`breakdown voltage <Breakdown_voltage>` and
      :ref:`usbpd-process-limits`).

   Deep N-well
      An N-type layer buried below a P-well, which isolates the transistors
      in that P-well from the P substrate. Its junction to the substrate
      limits how far above the substrate an isolated circuit can sit (see
      :ref:`usbpd-process-limits`).

   Field oxide
      The thick insulator between transistors on a chip, on which
      polysilicon resistors and metal tracks run (see
      :wikipedia:`LOCOS <LOCOS>` and :ref:`usbpd-process-limits`).

   Native transistor
      A transistor made without the threshold-adjusting implant, so that its
      threshold voltage is close to 0 V. The gf180mcu PDK has a 6 V native
      NMOS (see :wikipedia:`threshold voltage <Threshold_voltage>` and
      :ref:`usbpd-rd-circuit`).
