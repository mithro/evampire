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

   RJ45
      The 8-position modular socket and plug used on Ethernet cables (see
      :wikipedia:`8P8C`).

   Sink
      The end of a USB Type-C cable that receives power (see
      :ref:`the power roles <power-roles>`).

   Source
      The end of a USB Type-C cable that supplies power (see
      :ref:`the power roles <power-roles>`).

   Start pattern
      The fixed 8 bytes at the start of every Ethernet frame on the wire: a
      7-byte preamble and a 1-byte start frame delimiter. They let the
      receiver lock on to the frame (:clause:`3`).

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
