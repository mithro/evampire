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

Forwarding between the external ports
   * Each external port presents an RGMII interface to an external Ethernet
     transceiver.
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

Process
   * The chip targets the gf180mcu process through wafer.space.
