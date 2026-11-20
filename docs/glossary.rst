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

   Autonegotiation
      The exchange of link pulse bursts by which the two transceivers on a
      twisted-pair Ethernet cable agree on speed, duplex mode and, for
      1000BASE-T, which end is master (:clause:`28`, see
      :doc:`ethernet/phy-electrical/autonegotiation` and
      :wikipedia:`Autonegotiation`).

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

   Dual-role port
      A USB Type-C port that can attach as either a source or a sink, and
      can swap roles while connected (see :ref:`the power roles <power-roles>`).

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

   PAM-5
      Five-level pulse amplitude modulation: each symbol is one of the
      levels −2, −1, 0, +1 and +2. 1000BASE-T uses it on all four pairs
      (:clause:`40.1.3`, see :doc:`ethernet/phy-electrical/1000base-t-coding`
      and :wikipedia:`Pulse-amplitude modulation
      <Pulse-amplitude_modulation>`).

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

   Return loss
      How much weaker, in decibels, a reflection is than the signal that
      caused it. A port matched to the cable has a high return loss
      (:clause:`40.8.3.1`, see :doc:`ethernet/phy-electrical/job` and
      :wikipedia:`Return loss`).

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
