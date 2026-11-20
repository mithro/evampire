Overview and requirements
=========================

What the chip does
------------------

evampire is a three-port :wikipedia:`gigabit <Gigabit_Ethernet>`
:wikipedia:`Ethernet hub <Ethernet_hub>` on a single chip.

* **Two external ports** (called *port A* and *port B*) each connect to an
  Ethernet cable through an Ethernet transceiver. The transceiver is the part
  that drives and receives the electrical signals on the cable (see
  :doc:`ethernet/phy-electrical`). Ethernet documentation usually calls it a
  *PHY*, short for "physical layer device" (see
  :wikipedia:`Ethernet physical layer <Ethernet_physical_layer>`). In the first version the
  transceiver is a separate chip; in the full design it is part of evampire.
  Each port ends in an :wikipedia:`RJ45 <8P8C>` Ethernet socket (see :doc:`ethernet/magnetics`).
* **One internal port** connects to a small `RISC-V <https://riscv.org/>`_
  microcontroller inside the chip.

Data arriving on port A is sent out of port B, and data arriving on port B is
sent out of port A. The chip does not wait for a whole frame to arrive before
it starts sending it on. Each byte is passed to the other side a few clock
cycles after it arrives. This is called *cut-through* forwarding (see
:wikipedia:`Cut-through switching <Cut-through_switching>`). It needs
only a few bytes of storage on each path, no matter how long the frame is.

The internal processor sees a filtered copy of the traffic and can add its own
frames into the stream.

The processor also manages power. A board built around evampire can be
powered from an Ethernet cable and supply power over USB Type-C, or be
powered from USB Type-C and supply power over an Ethernet cable. The
processor negotiates the role and power level on each port (see
:doc:`power/index`).

Terms used in this documentation
--------------------------------

Frame
   One Ethernet message (see :wikipedia:`Ethernet frame <Ethernet_frame>`).
   A frame starts with the 6-byte destination address
   and the 6-byte source address, carries between 46 and 1500 bytes of
   payload in a normal frame, and ends with a 4-byte checksum, the
   :wikipedia:`frame check sequence <Frame_check_sequence>` (:clause:`3`).

MAC address
   The 48-bit address that identifies a device on an Ethernet network (see
   :wikipedia:`MAC address <MAC_address>`). Every
   frame carries a destination MAC address and a source MAC address
   (:clause:`3`).

RGMII
   *Reduced Gigabit Media Independent Interface*. A digital interface
   between a chip and an Ethernet transceiver: 4 data bits and one control
   signal in each direction, transferred on both edges of a 125 MHz clock at
   gigabit speed. See :doc:`ethernet/rgmii` and
   :wikipedia:`Media-independent interface <Media-independent_interface>`.

.. _requirements:

Requirements
------------

Ethernet transceivers
   * In the first version, each external port presents an RGMII interface to
     an external Ethernet transceiver.
   * The full design integrates the Ethernet transceiver functions on
     evampire: the line driver and receiver, the analog-to-digital and
     digital-to-analog converters, the signal processing that removes echo,
     crosstalk and cable loss, clock recovery, line coding and automatic
     speed negotiation. The forwarding logic connects to an integrated
     transceiver through the same one-byte-per-clock interface it uses with
     an RGMII interface. See :doc:`ethernet/phy-electrical`.
   * Gigabit Ethernet (1000BASE-T, 1000 Mbit/s over four pairs,
     :clause:`40`) is a hard
     requirement for every port, in both the first version and the full
     design. The integrated transceiver must therefore implement 1000BASE-T.
     Whether it also supports 100 Mbit/s and 10 Mbit/s is not yet fixed.

Connection to the cable
   * In the first version, each Ethernet port connects to its RJ45 socket
     through standard coupling transformers (the "magnetics").
   * The full design connects the cable to the board without coupling
     transformers. The jobs the transformers normally do, such as electrical
     isolation, rejecting voltage that is common to both wires of a pair,
     and giving a path for Power over Ethernet current (see
     :doc:`power/poe`), are done instead by
     active analog circuits on evampire together with a small number of
     external passive components. See :doc:`ethernet/magnetics`.

Forwarding between the external ports
   * Every frame received on port A is transmitted on port B, and every frame
     received on port B is transmitted on port A, except frames that must not
     be forwarded for a specific, listed reason. Such frames are delivered
     only to the internal processor, or dropped.
   * The listed exceptions are:

     - :wikipedia:`Link layer discovery protocol <Link_Layer_Discovery_Protocol>`
       (LLDP) frames, sent to the destination
       address 01-80-C2-00-00-0E. They carry the Power over Ethernet power
       negotiation between the two ends of one cable (:clause:`79`, see
       :doc:`power/poe`). Forwarding them would let a device on one port
       negotiate power with the device on the other port. They are delivered
       only to the internal processor, which handles the power negotiation
       for its own port.

     Any further exception is added to this list together with its reason.
   * Forwarding is cut-through. The delay through the chip is a small fixed
     number of clock cycles, not a whole frame.
   * Forwarded frames are passed on unchanged.
   * Because no whole frame is stored on the forwarding path, the length of a
     forwarded frame is not limited by the chip's memory.

Delivery to the internal processor
   * Each received frame's destination MAC address is compared against a
     programmable *address* and *mask* pair. A frame matches when every bit
     set in the mask is equal in the destination address and the programmed
     address.
   * Matching frames are copied into a receive buffer that the processor can
     read.
   * The receive checksum is checked in hardware. A frame with a bad
     checksum is not given to the processor.

Transmission from the internal processor
   * The processor writes a frame into a transmit buffer and requests that it
     be sent out of port A, port B or both.
   * The chip adds the frame's start pattern and checksum.
   * Processor frames are sent only in the gaps between forwarded frames.

Memory
   * The chip does not store full frames on the forwarding path.
   * Frame storage for the processor holds one or two frames of up to
     1522 bytes in each direction. That is 1500 bytes of payload plus the
     two addresses, the 2-byte type field, the 4-byte checksum and an
     optional 4-byte tag used to separate virtual networks sharing the same
     cable (:wikipedia:`IEEE 802.1Q <IEEE_802.1Q>`, :clause:`3`). With two
     frames, the processor can work on
     one frame while the hardware fills or empties the other.
   * Frames longer than the processor's buffer (for example
     :wikipedia:`jumbo frames <Jumbo_frame>` of
     up to about 9000 bytes) are still forwarded between ports A and B, but
     are not delivered to the processor.

Processor
   * A small 32-bit :wikipedia:`RISC-V` core with on-chip program and data
     memory.
   * The processor's network traffic is expected to be well below
     1 Mbit/s. The processor does not need to keep up with gigabit traffic.
   * The processor also controls the configuration interface of each
     external transceiver (:clause:`22`, see :doc:`ethernet/rgmii`).

Power bridging
   * A board built around evampire can take its power from an Ethernet
     cable (:wikipedia:`Power over Ethernet <Power_over_Ethernet>`, see
     :doc:`power/poe`) or from a :wikipedia:`USB Type-C <USB-C>` connector
     (:wikipedia:`USB Power Delivery <USB_Power_Delivery>`, see
     :doc:`power/usb-pd`), and can pass
     that power on through the other kind of port. See :doc:`power/index`;
     the names of the two ends of a powered cable used below are explained
     in :ref:`power-roles`.
   * **Ethernet in, USB out:** evampire receives power from an Ethernet
     port as a *powered device* and supplies power on a USB Type-C port as
     a USB Power Delivery *source*.
   * **USB in, Ethernet out:** evampire receives power from a USB Type-C
     port as a USB Power Delivery *sink* and supplies power on an Ethernet
     port as Power over Ethernet *power sourcing equipment*.
   * Power received on one Ethernet port can also be supplied on the other
     Ethernet port.
   * Each USB Type-C port is *dual-role*: it can attach as either a source
     or a sink, and can swap roles while connected, without unplugging.
   * The power levels are negotiated on every port. The processor keeps a
     power budget: the power offered on the output ports never exceeds the
     power granted on the input port, minus the board's own consumption and
     conversion losses.
   * The software translates the power available on the input port into a
     valid offer in the standard used by each output port:

     - **Ethernet in, USB out:** from the Power over Ethernet power granted
       to the board, the software works out the USB Power Delivery source
       offer (the list of voltage and current combinations) that fits in
       the budget and follows the USB Power Delivery rules.
     - **USB in, Ethernet out:** from the power the USB Power Delivery
       source provides, the software chooses the Power over Ethernet type
       and class whose power fits in the budget, and the port advertises
       that class when it supplies power.
     - **Ethernet in, Ethernet out:** the same, from one Power over Ethernet
       port to the other.

     When the input power changes, the offers on the outputs are updated to
     match, reduced before the input power falls. See
     :ref:`power-translation`.
   * When more than one port supplies power at the same time, for example
     both USB Type-C ports of the full design, the software shares the
     output budget between them. It divides the power between the ports,
     and moves power from one port to the other when a device needs less,
     asks for more, or is unplugged. See :ref:`power-sharing`.
   * The first version of the board has one Ethernet port that receives
     power (port A), one Ethernet port that supplies power (port B), and one
     USB Type-C port. The full design allows either Ethernet port to take
     either role and has two USB Type-C ports.
   * USB Power Delivery is implemented mostly in software on the RISC-V
     processor. The dedicated hardware is kept to the minimum needed: the
     analog circuits that connect to the configuration channel wires (the
     two wires of a USB Type-C connector that carry the power negotiation,
     see :doc:`power/usb-pd`), and only those digital helpers whose timing
     cannot be met in software.
   * All Power over Ethernet types and all USB Power Delivery voltage ranges
     are documented. The maximum power the board supports is not yet fixed.

Power control, monitoring and limiting
   * Software on the RISC-V processor makes every power decision once it is
     running: it carries out the negotiation on every port (Power over
     Ethernet detection and classification in both roles, and USB Power
     Delivery), keeps the power budget, and switches power on and off on
     each port. The only exception is the start-up sequencer described
     below, which works before the processor is running.
   * evampire has built-in power monitoring: it measures the voltage and
     current of every power port and of the board's power bus, so that the
     software can read the power flowing through each of them at any time.
   * A board powered only from one port must be able to start from nothing.
     Before a Power over Ethernet power source has detected the board and
     switched its power on, the cable carries only small test voltages and
     currents, too little to run the processor. evampire therefore has a
     small built-in sequencer, working without the processor, that answers
     the detection and classification steps and requests a power level
     large enough to start the processor. Once powered, the software
     carries out any further negotiation, for example asking for more power.
     How much of this the sequencer must do depends on how much power the
     board needs to start compared with how much the cable can give at
     each step; :doc:`power/poe` works this out. A board powered from USB
     Type-C starts in the same way from the basic 5 V that a USB charger
     supplies before any USB Power Delivery negotiation (see
     :doc:`power/usb-pd`).
   * evampire has built-in power limiting: each port has a current and power
     limit that the software sets. Built-in hardware enforces these limits
     and switches a port off when a fault happens faster than software can
     react, for example a short circuit, and then reports it to the
     software.

Voltage converters
   * evampire includes the functions of the three
     :wikipedia:`switching voltage converters <Switched-mode_power_supply>`
     in the power path: the converter that brings the Power over Ethernet
     input down to the board's power bus, the converter that produces the
     USB Type-C output voltage when a USB port is a source, and the
     converter that produces the 44 V to 57 V needed to supply Power over
     Ethernet. See :doc:`power/converters`.
   * The input and output voltage ranges of USB Power Delivery and Power
     over Ethernet overlap. Whether the three functions are three separate
     converters, one converter whose connections change with the operating
     mode, or another arrangement is not yet fixed.
   * The converter functions are brought onto evampire step by step. In the
     first version, evampire controls the converters while the power
     transistors and their gate drivers are external parts. Moving the gate
     drivers, and then the power transistors, onto evampire is explored in
     later versions.

USB serial port
   * Each USB Type-C port can also carry a
     :wikipedia:`USB 2.0 <USB_2.0>` full-speed (12 Mbit/s) data connection on
     its D+ and D− wires, through which the RISC-V processor appears to a
     computer as a :wikipedia:`USB serial port <USB_communications_device_class>`.
   * The USB data protocol is implemented mostly in software on the
     processor, with built-in hardware assistance only where the timing of
     USB cannot be met in software. How the work is split between hardware
     and software is analysed in :doc:`usb-serial`.

Process
   * The chip targets the `gf180mcu <https://gf180mcu-pdk.readthedocs.io/>`_
     process through `wafer.space <https://wafer.space/>`_.
