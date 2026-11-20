Architecture
============

This page gives a high-level view of the blocks inside evampire and how data
moves between them. Later pages describe each external interface in detail.

Block diagram
-------------

.. _fig-block-diagram:

.. graphviz:: block-diagram.dot
   :caption: evampire block diagram. Bold arrows carry Ethernet frame data.
             Dashed arrows carry control.
   :align: center

Blocks
------

RGMII interfaces A and B
   Each interface connects to one external Ethernet transceiver. It receives
   4 data bits and a control signal on both edges of the clock that the
   transceiver sends with the data, and converts them into one byte per
   clock cycle plus "frame in progress" and "error" flags. In the other
   direction it converts bytes back into 4-bit, both-edge signals and sends
   them with a transmit clock generated inside evampire. See
   :doc:`../ethernet/rgmii`.

Rate-matching buffers
   Received data arrives on the clock that the transceiver recovers from the
   cable, which is set by the crystal at the far end of the cable.
   Transmitted data leaves on evampire's own 125 MHz clock. These two clocks
   have the same nominal frequency but are not identical. Ethernet allows
   each end to be up to 100 parts per million away from 125 MHz, so the two
   can differ by up to 200 parts per million. A small buffer of a few bytes
   in each direction crosses the data from the receive clock to the transmit
   clock and absorbs this difference over the length of one frame. The gap
   between frames gives the buffer time to return to its centre point before
   the next frame starts.

Output selectors A and B
   Each output selector chooses whether the transmitter of its port sends
   forwarded data from the other port or a frame from the processor. A
   forwarded frame that is already being sent is never interrupted. A frame
   from the processor is started only when the port is idle, and waits
   otherwise. Because the forwarding path has no full-frame storage, a
   forwarded frame that starts arriving while a processor frame is being
   sent on the same port is dropped. The processor sends little traffic, so
   this is rare. Ethernet does not guarantee delivery, and higher-level
   protocols resend lost data.

Destination address filter and checksum check
   Watches the frames received on both external ports, taking them from the
   output of the rate-matching buffers so that all of its logic runs on the
   one 125 MHz clock. The first 6 bytes of
   every frame are its destination MAC address. The filter compares those
   bytes with a programmed address, using a programmed mask to select which
   bits must match. A matching frame is copied into the receive frame
   buffer. The 4-byte checksum at the end of the frame is checked as the
   frame arrives, and a frame with a bad checksum, or one too long to fit
   in the buffer, is discarded instead of being handed to the processor.
   Filtering has no effect on forwarding: every frame is still forwarded to
   the other external port.

Receive and transmit frame buffers
   SRAM that holds whole frames for the processor, each slot large enough for
   the longest normal frame (1522 bytes). With two slots in a direction, the
   hardware can fill (or empty) one slot while the processor works on the
   other.

Start pattern and checksum generator
   Every Ethernet frame on the wire starts with a fixed 8-byte pattern that
   lets the receiver lock on to the frame, and ends with a 4-byte checksum.
   This block adds both to frames from the processor, so that the processor
   only writes the addresses, type field and payload.

Microcontroller
   A small 32-bit RISC-V core with its own program and data memory. It
   reads frames from the receive buffer, writes frames to the transmit
   buffer, sets the address filter, and handles any higher-level network
   protocol in software. Its network traffic is well below 1 Mbit/s.

Transceiver configuration interface
   A two-wire serial interface (a clock and a bidirectional data line) that
   every Ethernet transceiver provides for reading its status, such as
   whether a cable is connected and at what speed, and for changing its
   settings.

Power negotiation interface
   The analog and digital circuits the processor uses to request power from
   a Power over Ethernet or USB Power Delivery source. See
   :doc:`../power/index`.

Clock and reset
   A 125 MHz reference clock drives the transmit side of both RGMII
   interfaces, the forwarding logic and the address filter. Many Ethernet
   transceivers can output a 125 MHz clock for this purpose. The processor
   may run from a slower clock derived from it.

Data paths
----------

Port A to port B
   RGMII interface A, rate-matching buffer A to B, output selector B, RGMII
   interface B. The delay is a fixed small number of clock cycles.

Port B to port A
   The same path in the other direction.

Port A or B to the processor
   RGMII interface A or B, rate-matching buffer, address filter, receive
   frame buffer, processor.
   The frame is also forwarded to the other port as usual.

Processor to port A or B
   Processor, transmit frame buffer, start pattern and checksum generator,
   output selector A and/or B, RGMII interface.
