.. _ebat-architecture:

ebat architecture
=================

This page shows the evampire blocks that ebat keeps, and lists the
evampire blocks and pins that it leaves out.

ebat is evampire's power and control blocks
-------------------------------------------

:numref:`fig-ebat-block-diagram` shows the blocks inside ebat. The
connectors and per-port circuits run along the top, the processor sits in
the middle, and the power monitoring and converter control connect it to
the converters' power stages below.

.. graphviz:: block-diagram.dot
   :name: fig-ebat-block-diagram
   :caption: Blocks inside ebat, where bold arrows carry signals between the
             chip and the board and dashed arrows carry control and
             measurements.
   :alt: Block diagram. Outside the chip, port A with its RJ45 socket and
         powered-device front end connects to the start-up sequencer and
         class signature block. The USB Type-C connector and power path
         connects to the configuration channel circuits and to the USB
         serial front end. Port B with its RJ45 socket and power sourcing
         switch connects to the detection and classification sequencing
         block. All four blocks connect to the RISC-V processor and
         memory, which connects to power monitoring and limiting and to
         converter control. Converter control drives the power stages of
         the voltage converters, drawn outside the chip as in evampire's
         first version, and power monitoring reads them.
   :align: center

The fill colour of each block shows its group. White blocks with a dashed
outline are outside the chip. Yellow blocks are Power over Ethernet
circuits, blue blocks USB Type-C circuits, green blocks power monitoring
and converter control, and the orange block the processor.

The converters' power stages are drawn outside the chip, as in evampire's
first version. Where they sit follows evampire's board configurations
(:numref:`tab-power-board-configs`).

Every block is an evampire block
--------------------------------

ebat adds no block of its own. :numref:`tab-ebat-blocks` gives, for each
block in :numref:`fig-ebat-block-diagram`, the evampire page that
describes it.

.. list-table:: The blocks of ebat and where each is described
   :name: tab-ebat-blocks
   :header-rows: 1
   :widths: 40 60

   * - Block
     - Described on
   * - Start-up sequencer and class signature
     - :doc:`../power/poe/pd-controller` and :doc:`../power/poe/startup`
   * - Detection and classification sequencing
     - :doc:`../power/poe/pse-sequencing`
   * - Configuration channel circuits
     - :doc:`../power/usb-pd/analogue`
   * - USB serial front end
     - :doc:`../usb-serial/analogue`
   * - RISC-V processor and memory
     - :ref:`The microcontroller <arch-microcontroller>`
   * - Power monitoring and limiting
     - :doc:`../power/poe/monitoring` and :doc:`../power/usb-pd/monitoring`
   * - Converter control
     - :doc:`../power/converters/first-version` and
       :doc:`../power/converters/integration`

The evampire block diagram (:numref:`fig-block-diagram`) draws the power
blocks as one "Power negotiation, monitoring and limiting" block
(:ref:`arch-power-negotiation`). ebat draws them separately, because they
are all that is left. The power flow on a board is the same as on an
evampire board (:numref:`fig-power-flow`), without the transceivers among
the board supplies.

ebat leaves out the frame path and its clock
--------------------------------------------

ebat does not have these blocks of evampire (:doc:`../architecture/index`):

* RGMII interfaces A and B, or the integrated transceivers that take their
  place;
* the rate-matching buffers and output selectors of the forwarding path;
* the destination address filter, the checksum check and the preamble and
  checksum generator;
* the receive and transmit frame buffers;
* the transceiver configuration interface.

The 125 MHz reference clock drives only these blocks
(:ref:`arch-clock`), so ebat does not need it.

The USB serial port needs a bit clock within ± 0.25 % of 12 MHz. Of the
three clock sources that the USB serial pages list, ebat does not have
the first, a clock derived from the 125 MHz Ethernet reference. The two
that remain are a local oscillator trimmed against the 1 ms start-of-frame
tokens from the host, and a dedicated crystal
(:doc:`../usb-serial/timing`).

The processor handles no frames. Its work is the power negotiation on each
port, the power budget and the USB serial port, as on evampire. The USB
Power Delivery messages keep the processor busy with interrupts off for
the length of each message (:doc:`../power/usb-pd/software`), and the
serial port shares the processor with them as described on
:doc:`../usb-serial/usb-pd-roles`.

ebat needs 27 fewer pins than a first-version evampire
------------------------------------------------------

The pins that ebat does not need are those of the two RGMII ports, the
management interface and the 125 MHz reference clock, 27 pins in all
(:numref:`tab-rgmii-pins`). The power-side pins are the same as on
evampire: the detection and classification connections of each Ethernet
port, the configuration channel and D+ and D− wires of each USB Type-C
port, and the converter control and measurement connections.
