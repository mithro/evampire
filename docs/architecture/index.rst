Architecture
============

This page gives a high-level view of the blocks inside evampire and how
frames move between them. The :doc:`../ethernet/index` and
:doc:`../power/index` pages describe each external interface in detail.

Forwarding and processor paths
------------------------------

:numref:`fig-block-diagram` shows the blocks inside evampire. The two
forwarding paths run down the left-hand side, and the processor's path to
and from them runs across to the right.

.. graphviz:: block-diagram.dot
   :name: fig-block-diagram
   :caption: Blocks inside evampire, where bold arrows carry Ethernet frame
             data and dashed arrows carry control.
   :alt: Block diagram. Port A and port B, each an RJ45 socket, magnetics
         and Ethernet transceiver outside the chip, connect to RGMII
         interfaces A and B. Each RGMII interface feeds a rate-matching
         buffer that leads to the output selector of the other port. Both
         rate-matching buffers also feed the address filter and checksum
         check, which feeds the receive frame buffer and then the RISC-V
         processor. The processor feeds the transmit frame buffer and the
         preamble and checksum generator, which feeds both output
         selectors. The processor also controls the transceiver
         configuration interface and the power negotiation, monitoring and
         limiting block, which connects to the power circuits outside the
         chip.
   :align: center

The fill colour of each block shows its group. White blocks with a dashed
outline are outside the chip. Blue blocks are the RGMII interfaces, grey
blocks the forwarding path, green blocks the processor's frame path, and
orange blocks the processor and its control interfaces.

Blocks
------

.. _arch-rgmii:

RGMII interfaces A and B
   Each interface connects to one external :term:`Ethernet transceiver`
   over :wikipedia:`RGMII <Media-independent_interface>`. It receives
   4 data bits and a control signal on both edges of the clock
   (:wikipedia:`double data rate <Double_data_rate>`) that the
   transceiver sends with the data. It converts them into one byte per
   clock cycle plus "frame in progress" and "error" flags. In the other
   direction it converts bytes back into 4-bit, both-edge signals and sends
   them with a transmit clock generated inside evampire. See
   :doc:`../ethernet/rgmii/index`.

   With an integrated Ethernet transceiver (see
   :numref:`tab-power-board-configs`), the transceiver takes the place of
   each RGMII interface and its external transceiver. It presents the same
   one-byte-per-clock interface to the :term:`forwarding logic`. See
   :doc:`../ethernet/phy-electrical/index` and :doc:`../ethernet/magnetics/index`.

.. _arch-rate-matching:

Rate-matching buffers
   Received data arrives on the clock that the transceiver recovers from the
   cable, which is set by the crystal at the far end of the cable.
   Transmitted data leaves on evampire's own 125 MHz clock. These two clocks
   have the same nominal frequency but are not identical. Gigabit Ethernet
   allows each end to be up to 100
   :wikipedia:`parts per million <Parts-per_notation>` away from 125 MHz
   (:clause:`40`, see :doc:`../ethernet/phy-electrical/index`), so the two
   can differ by up to 200 parts per million.

   A small :wikipedia:`first-in, first-out (FIFO) buffer
   <FIFO_(computing_and_electronics)>` of a few bytes in each direction
   crosses the data from the receive clock to the transmit clock (a
   :wikipedia:`clock domain crossing <Clock_domain_crossing>`). It absorbs
   the difference between the clocks over the length of one frame. The gap
   between frames gives the buffer time to return to its centre point
   before the next frame starts. The size of the buffer sets the longest
   frame that can be forwarded (see :ref:`the forwarding requirements <req-forwarding>`).

.. _arch-output-selectors:

Output selectors A and B
   Each output selector chooses whether the transmitter of its port sends
   forwarded data from the other port or a frame from the processor. A
   forwarded frame that is already being sent is never interrupted. A frame
   from the processor is started only when the port is idle, and waits
   otherwise.

   The forwarding path has no full-frame storage. A forwarded frame that
   starts arriving while a processor frame is being sent on the same port is
   therefore dropped. The share of the forwarded link's time taken by
   dropped frames is roughly

   .. math::

      D \approx U \times T

   where :math:`D` is the fraction of the forwarded link's time lost to
   dropped frames, :math:`U` is the utilisation of the forwarded link (the
   fraction of time it carries frames), and :math:`T` is the fraction of
   time the output port spends sending processor frames. All three are
   fractions with no unit. For example, a link at half load (:math:`U = 0.5`)
   and processor traffic of 1 Mbit/s on a 1000 Mbit/s port
   (:math:`T = 0.001`) give :math:`D \approx 0.0005`. On a 10 Mbit/s port
   the same processor traffic gives :math:`T = 0.1` and
   :math:`D \approx 0.05`, a hundred times more.

   Ethernet does not guarantee delivery. Higher-level protocols such as
   :wikipedia:`TCP <Transmission_Control_Protocol>` resend lost data;
   others such as :wikipedia:`UDP <User_Datagram_Protocol>` do not.

.. _arch-address-filter:

Destination address filter and checksum check
   Watches the frames received on both external ports. It takes them from
   the output of the rate-matching buffers, so that all of its logic runs on
   the one 125 MHz clock. The first 6 bytes of every frame are its
   destination :term:`MAC address` (:clause:`3`). The filter compares those
   bytes with a programmed address, using a programmed mask to select which
   bits must match. A matching frame is copied into the receive frame
   buffer.

   The 4-byte checksum at the end of the frame is checked as the frame
   arrives. A frame with a bad checksum, or one too long to fit in the
   buffer, is discarded instead of being handed to the processor. Filtering
   has no effect on forwarding: every frame is still forwarded to the other
   external port, except the frames listed in :ref:`the forwarding requirements <req-forwarding>`.

Receive and transmit frame buffers
   :wikipedia:`SRAM <Static_random-access_memory>` that holds whole frames
   for the processor, each slot large enough for the longest normal frame
   (1522 bytes). With two slots in a direction, the hardware can fill or
   empty one slot while the processor works on the other.

Preamble and checksum generator
   Every Ethernet frame on the wire starts with a 7-byte :term:`preamble`
   and a 1-byte :term:`start frame delimiter`, which let the receiver lock
   on to the frame, and ends with a 4-byte checksum (:clause:`3`; see also the frame structure on
   :doc:`../ethernet/rgmii/index`). This block adds both to frames from the
   processor, so that the processor only writes the addresses, type field
   and payload.

.. _arch-microcontroller:

Microcontroller
   A :wikipedia:`RISC-V` core with its own program and data memory. It
   reads frames from the receive buffer, writes frames to the transmit
   buffer, sets the address filter, and handles any higher-level network
   protocol in software. Its network traffic is below 1 Mbit/s.

.. _arch-config-interface:

Transceiver configuration interface
   A two-wire serial interface, the
   :wikipedia:`MDIO <Management_Data_Input/Output>` interface, with a clock
   and a bidirectional data line. Every Ethernet transceiver provides it for
   reading its status, such as whether a cable is connected and at what
   speed, and for changing its settings. The interface and its standard
   registers are defined in :clause:`22`. :doc:`../ethernet/rgmii/index` describes
   how evampire uses it.

.. _arch-power-negotiation:

Power negotiation interface
   The analogue and digital circuits that the processor uses to negotiate
   power on each port. With them the processor requests power as a
   :term:`powered device` or a USB Power Delivery :term:`sink`, and offers
   power as :term:`power sourcing equipment` or a USB Power Delivery
   :term:`source`. It also swaps the power role of a USB Type-C port.

   The interface controls the power switches and voltage converters that
   move power between the ports. Software on the processor makes every
   decision: it runs the negotiations and switches power on and off. The
   interface measures the voltage and current of every power port and of the
   board's power bus. It enforces the current and power limits that the
   software sets, and switches a port off by itself when a fault is too fast
   for software.

   A small built-in start-up sequencer answers Power over Ethernet detection
   and classification while the processor is not running, so that a board
   powered only from Ethernet can request power. See :doc:`../power/index`.

.. _arch-clock:

Clock and reset
   A 125 MHz reference clock drives the transmit side of both RGMII
   interfaces, the forwarding logic and the address filter. Where this clock
   comes from, a separate oscillator or a clock output of an external
   transceiver, is discussed on :doc:`../ethernet/rgmii/index`. The processor's
   clock is an open question (see :ref:`requirements-open-questions`).

Data paths
----------

.. list-table:: Blocks on each data path, in order
   :name: tab-data-paths
   :header-rows: 1
   :widths: 25 75

   * - Path
     - Blocks in order
   * - Port A to port B
     - RGMII interface A, rate-matching buffer A to B, output selector B,
       RGMII interface B
   * - Port B to port A
     - RGMII interface B, rate-matching buffer B to A, output selector A,
       RGMII interface A
   * - Port A or B to the processor
     - RGMII interface A or B, rate-matching buffer, address filter, receive
       frame buffer, processor
   * - Processor to port A or B
     - Processor, transmit frame buffer, preamble and checksum
       generator, output selector A or B or both, RGMII interface A or B or
       both

:numref:`tab-data-paths` lists the blocks on each path. The delay from one
external port to the other is a fixed small number of clock cycles. A frame
copied to the processor is also forwarded to the other port as usual.
