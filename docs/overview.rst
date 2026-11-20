Overview and requirements
=========================

What the chip does
------------------

evampire is a three-port gigabit Ethernet hub on a single chip.

* **Two external ports** (called *port A* and *port B*) each connect to an
  external Ethernet transceiver chip. The transceiver is the part that drives
  and receives the electrical signals on the Ethernet cable. Ethernet
  documentation usually calls this transceiver a *PHY*, short for "physical
  layer device". Each transceiver connects to an RJ45 Ethernet socket.
* **One internal port** connects to a small RISC-V microcontroller inside the
  chip.

Data arriving on port A is sent out of port B, and data arriving on port B is
sent out of port A. The chip does not wait for a whole frame to arrive before
it starts sending it on. Each byte is passed to the other side a few clock
cycles after it arrives. This is called *cut-through* forwarding. It needs
only a few bytes of storage on each path, no matter how long the frame is.

The internal processor sees a filtered copy of the traffic and can add its own
frames into the stream.

The processor also manages power. A board built around evampire can be
powered from an Ethernet cable and supply power over USB Type-C, or be
powered from USB Type-C and supply power over an Ethernet cable. The
processor negotiates the role and power level on each port.

Terms used in this documentation
--------------------------------

Frame
   One Ethernet message. A frame starts with the 6-byte destination address
   and the 6-byte source address, carries between 46 and 1500 bytes of
   payload in a normal frame, and ends with a 4-byte checksum.

MAC address
   The 48-bit address that identifies a device on an Ethernet network. Every
   frame carries a destination MAC address and a source MAC address.

RGMII
   *Reduced Gigabit Media Independent Interface*. A digital interface
   between a chip and an Ethernet transceiver: 4 data bits and one control
   signal in each direction, transferred on both edges of a 125 MHz clock at
   gigabit speed. See :doc:`ethernet/rgmii`.

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
   * Which Ethernet speeds the integrated transceiver supports is not yet
     fixed.

Connection to the cable
   * In the first version, each Ethernet port connects to its RJ45 socket
     through standard coupling transformers (the "magnetics").
   * The full design connects the cable to the board without coupling
     transformers. The jobs the transformers normally do, such as electrical
     isolation, rejecting voltage that is common to both wires of a pair,
     and giving a path for Power over Ethernet current, are done instead by
     active analog circuits on evampire together with a small number of
     external passive components. See :doc:`ethernet/magnetics`.

Forwarding between the external ports
   * Every frame received on port A is transmitted on port B, and every frame
     received on port B is transmitted on port A.
   * Forwarding is cut-through. The delay through the chip is a small fixed
     number of clock cycles, not a whole frame.
   * Frames are forwarded unchanged.
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
     cable. With two frames, the processor can work on
     one frame while the hardware fills or empties the other.
   * Frames longer than the processor's buffer (for example "jumbo" frames of
     up to about 9000 bytes) are still forwarded between ports A and B, but
     are not delivered to the processor.

Processor
   * A small 32-bit RISC-V core with on-chip program and data memory.
   * The processor's network traffic is expected to be well below
     1 Mbit/s. The processor does not need to keep up with gigabit traffic.
   * The processor also controls the configuration interface of each
     external transceiver.

Power bridging
   * A board built around evampire can take its power from an Ethernet
     cable (Power over Ethernet) or from a USB Type-C connector (USB Power
     Delivery), and can pass that power on through the other kind of port.
     See :doc:`power/index`.
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
   * The first version of the board has one Ethernet port that receives
     power (port A), one Ethernet port that supplies power (port B), and one
     USB Type-C port. The full design allows either Ethernet port to take
     either role and has two USB Type-C ports.
   * All Power over Ethernet types and all USB Power Delivery voltage ranges
     are documented. The maximum power the board supports is not yet fixed.

Process
   * The chip targets the gf180mcu process through wafer.space.
