Architecture
============

This page gives a high-level view of the blocks inside evampire and how data
moves between them. The :doc:`../ethernet/index` and :doc:`../power/index`
pages describe each external interface in detail.

Block diagram
-------------

.. _fig-block-diagram:

.. graphviz:: block-diagram.dot
   :caption: evampire block diagram. Bold arrows carry Ethernet frame data.
             Dashed arrows carry control.
   :align: center

Blocks
------

.. _arch-rgmii:

RGMII interfaces A and B
   Each interface connects to one external Ethernet transceiver. It receives
   4 data bits and a control signal on both edges of the clock
   (:wikipedia:`double data rate <Double_data_rate>`) that the
   transceiver sends with the data, and converts them into one byte per
   clock cycle plus "frame in progress" and "error" flags. In the other
   direction it converts bytes back into 4-bit, both-edge signals and sends
   them with a transmit clock generated inside evampire. See
   :doc:`../ethernet/rgmii`.

   In the full design, an integrated Ethernet transceiver can take the place
   of each RGMII interface and its external transceiver. It presents the
   same one-byte-per-clock interface to the forwarding logic, and drives the
   cable without coupling transformers. See :doc:`../ethernet/phy-electrical`
   and :doc:`../ethernet/magnetics`.

.. _arch-rate-matching:

Rate-matching buffers
   Received data arrives on the clock that the transceiver recovers from the
   cable, which is set by the crystal at the far end of the cable.
   Transmitted data leaves on evampire's own 125 MHz clock. These two clocks
   have the same nominal frequency but are not identical. Gigabit Ethernet
   allows each end to be up to 100
   :wikipedia:`parts per million <Parts-per_notation>` away from 125 MHz
   (:clause:`40`, see :doc:`../ethernet/phy-electrical`), so the two
   can differ by up to 200 parts per million. A small buffer of a few bytes
   in each direction crosses the data from the receive clock to the transmit
   clock (a :wikipedia:`clock domain crossing <Clock_domain_crossing>`) and absorbs this difference over the length of one frame. The gap
   between frames gives the buffer time to return to its centre point before
   the next frame starts.

.. _arch-output-selectors:

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

.. _arch-address-filter:

Destination address filter and checksum check
   Watches the frames received on both external ports, taking them from the
   output of the rate-matching buffers so that all of its logic runs on the
   one 125 MHz clock. The first 6 bytes of every frame are its destination
   MAC address (:clause:`3`). The filter compares those
   bytes with a programmed address, using a programmed mask to select which
   bits must match. A matching frame is copied into the receive frame
   buffer. The 4-byte checksum at the end of the frame is checked as the
   frame arrives, and a frame with a bad checksum, or one too long to fit
   in the buffer, is discarded instead of being handed to the processor.
   Filtering has no effect on forwarding: every frame is still forwarded to
   the other external port.

Receive and transmit frame buffers
   :wikipedia:`SRAM <Static_random-access_memory>` that holds whole frames
   for the processor, each slot large enough for
   the longest normal frame (1522 bytes). With two slots in a direction, the
   hardware can fill (or empty) one slot while the processor works on the
   other.

Start pattern and checksum generator
   Every Ethernet frame on the wire starts with a fixed 8-byte pattern that
   lets the receiver lock on to the frame, and ends with a 4-byte checksum
   (:clause:`3`; see also the frame structure on :doc:`../ethernet/rgmii`).
   This block adds both to frames from the processor, so that the processor
   only writes the addresses, type field and payload.

.. _arch-microcontroller:

Microcontroller
   A small 32-bit `RISC-V <https://riscv.org/>`_ core with its own program
   and data memory. It
   reads frames from the receive buffer, writes frames to the transmit
   buffer, sets the address filter, and handles any higher-level network
   protocol in software. Its network traffic is well below 1 Mbit/s.

.. _arch-config-interface:

Transceiver configuration interface
   A two-wire serial interface (a clock and a bidirectional data line) that
   every Ethernet transceiver provides for reading its status, such as
   whether a cable is connected and at what speed, and for changing its
   settings. The interface and its standard registers are defined in
   :clause:`22`; :doc:`../ethernet/rgmii` describes how evampire uses it.

.. _arch-power-negotiation:

Power negotiation interface
   The analog and digital circuits the processor uses to negotiate power on
   each port: to request power as a Power over Ethernet powered device or
   USB Power Delivery sink, to offer power as Power over Ethernet power
   sourcing equipment or a USB Power Delivery source, and to swap the power
   role of a USB Type-C port. It also controls the power switches and
   voltage converters that move power between the ports. Software on the
   processor makes every decision: it runs the negotiations and switches
   power on and off. The interface measures the voltage and current of every
   power port and of the board's power bus, and enforces the current and
   power limits that the software sets, switching a port off by itself when
   a fault is too fast for software. A small built-in start-up sequencer
   answers Power over Ethernet detection and classification while the
   processor is not yet running, so that a board powered only from Ethernet
   can start. See :doc:`../power/index`.

.. _arch-clock:

Clock and reset
   A 125 MHz reference clock drives the transmit side of both RGMII
   interfaces, the forwarding logic and the address filter. Where this clock
   comes from (a separate oscillator, or a clock output of an external
   transceiver) is discussed on :doc:`../ethernet/rgmii`. The processor may
   run from a slower clock derived from it.

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
