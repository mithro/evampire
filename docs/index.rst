evampire
========

evampire is an integrated circuit for the `GlobalFoundries 180 nm MCU
(gf180mcu) <https://gf180mcu-pdk.readthedocs.io/>`_ process, manufactured
through `wafer.space <https://wafer.space/>`_. It is a three-port
:wikipedia:`gigabit <Gigabit_Ethernet>`
:wikipedia:`Ethernet hub <Ethernet_hub>` with a small :wikipedia:`RISC-V`
processor that also moves power between
:wikipedia:`Power over Ethernet <Power_over_Ethernet>` and
:wikipedia:`USB Type-C <USB-C>`.

.. figure:: index/overview.svg
   :name: fig-overview
   :alt: Block diagram. Data runs in a straight line along the top, between
         Ethernet port A, Ethernet transceiver A, the cut-through hub,
         Ethernet transceiver B and Ethernet port B. Each transceiver is
         labelled 10, 100, 1000 Mbit/s, the hub same speed on both ports,
         and each link between a transceiver and the hub RGMII, up to
         125 MHz. The hub
         passes frames, below 1 Mbit/s, to and from the RISC-V processor
         below it. The processor connects to three blocks: power control
         (measure, limit), the USB 2.0 serial port (12 Mbit/s) and USB-PD
         (BMC, 300 kbit/s). The serial port connects straight down to the USB
         Type-C port over the D+ and D− wires, and USB-PD over the CC wire;
         both hop over the power row. Power control connects to the power
         bus. Power runs in a straight line along the bottom, from
         Ethernet port A (PoE in, 37–57 V) through the powered device and
         buck converter to the power bus on the board. From the bus it runs
         through the boost converter and power sourcing equipment to
         Ethernet port B (PoE out, 44–57 V). Below the bus, power comes up from the USB Type-C port
         through the VBUS sink switch, and goes down to it through the VBUS
         source buck-boost converter. The USB Type-C port is labelled VBUS
         5–20 V, up to 48 V with EPR. The first-version chip is drawn as a
         die with a ring of bond pads around the hub, processor, power
         control, serial port and USB-PD; coloured pads mark the RGMII links,
         the USB wires and the power control signals that leave it. A dashed
         outline that also includes both Ethernet transceivers and all the
         power stages marks the chip in the full design, with a note that
         some high-voltage switches may stay external parts. The outline has
         a hole around the power bus, which stays on the board.
   :align: center

   The main blocks of evampire. Data flows along the top row and power along
   the bottom row, each from Ethernet port A to port B. The first-version
   chip is drawn as a die, where a coloured pad marks each signal that leaves
   it, and the dashed outline is the chip in the full design. The power bus
   stays on the board.

Ports
-----

The hub has two external ports, called port A and port B, and one
internal port, all drawn in :numref:`fig-overview`.

Port A and port B
   Each external port connects to an Ethernet cable through an
   :term:`Ethernet transceiver`, the circuit that drives and receives the
   electrical signals on the cable (see :doc:`ethernet/phy-electrical/index`).
   Each port ends in an :term:`RJ45` socket (see
   :doc:`ethernet/magnetics/index`).

The internal port
   The internal port connects to the processor inside the chip.

Cut-through forwarding
----------------------

Ethernet carries data in :term:`frames <frame>`, messages that are
normally up to 1522 bytes long and each start with the address of the device
they are sent to.
A frame arriving on port A is sent out of port B, and a frame arriving on
port B is sent out of port A. The few exceptions are listed in
:ref:`the forwarding requirements <req-forwarding>`.

evampire does not wait for a whole frame to arrive before it starts sending
it on. Each byte is passed to the other side a few clock cycles after it
arrives. This is called :term:`cut-through forwarding`. It needs only a few
bytes of storage on each path, not a whole frame.
:numref:`fig-cut-through` compares it with store-and-forward, in which a
switch receives the whole frame before it starts sending it.

.. wavedrom::
   :name: fig-cut-through
   :alt: Timing diagram. Port A receives a frame as a run of bytes, 1
         to N. With cut-through forwarding, port B starts
         sending byte 1 a few clock cycles after it arrives, while the rest
         of the frame is still arriving, and finishes a few cycles after
         the last byte arrives. With store-and-forward, port B starts
         sending only after the last byte has arrived, a whole frame later.
   :caption: One frame through cut-through forwarding, which starts a few
             clock cycles after the first byte, and through
             store-and-forward, which waits for the whole frame; schematic.

   { "signal": [
       { "name": "A receives", "wave": "x=====x.....",
         "data": ["1", "2", "3", "…", "N"] },
       { "name": "B, cut-through", "wave": "x.=====x....",
         "data": ["1", "2", "3", "…", "N"] },
       { "name": "B, stored first", "wave": "x......=====",
         "data": ["1", "2", "3", "…", "N"] }
     ],
     "head": { "text": "bytes 1 to N of one frame" },
     "config": { "hscale": 1 }
   }

.. _overview-processor-frames:

Processor traffic
-----------------

The processor sees a copy of the frames, from either port, whose destination
address matches a filter that it sets. It can also send frames of its own, which evampire
sends in the gaps between the frames it forwards
(:numref:`fig-output-selector`). The processor's network
traffic is below 1 Mbit/s, so it does not need to keep up with gigabit
traffic.

Power management
----------------

The processor also manages power, moving it between Ethernet and USB
Type-C. A board built around evampire can be
powered from an Ethernet cable and supply power over USB Type-C, or be
powered from USB Type-C and supply power over an Ethernet cable. The
processor negotiates the role and the power level on each port (see
:doc:`power/index`, which draws the modes in :numref:`fig-power-modes`).

Main blocks
-----------

:numref:`fig-overview` shows the main blocks of evampire and how data and
power flow between them.

The two chip outlines are the two board configurations of
:numref:`tab-power-board-configs`. The first version connects to separate
Ethernet transceiver chips over RGMII and uses external power stages. The
full design builds the transceivers and the power stages into evampire,
except possibly some high-voltage switches
(:ref:`requirements-open-questions`). Both ports run at the same speed, 10,
100 or 1000 Mbit/s, because forwarding is cut-through (see
:ref:`the forwarding requirements <req-forwarding>`).
The figure shows the power roles and the single USB Type-C port of the
first version: port A receives power and port B supplies it.

The labels use two abbreviations. USB Power Delivery messages on the
:term:`CC` wire use
:term:`biphase mark coding <Biphase mark coding>` (BMC). :term:`EPR` is the
extended power range of USB Power Delivery.

The chip
--------

:doc:`requirements`
   Every requirement the design meets, and the questions still open.
:doc:`architecture/index`
   The blocks inside evampire and how frames move between them.

.. toctree::
   :maxdepth: 2
   :caption: The chip
   :hidden:

   Home <self>
   requirements
   architecture/index

Data interfaces
---------------

:doc:`ethernet/index`
   The Ethernet interfaces, from the chip's pins to the cable.
:doc:`usb-serial/index`
   The USB serial port carried on the USB Type-C data wires.

.. toctree::
   :maxdepth: 2
   :caption: Data interfaces
   :hidden:

   ethernet/index
   usb-serial/index

Power
-----

:doc:`power/index`
   How power moves between Power over Ethernet and USB Type-C, and the
   board configurations.

.. toctree::
   :maxdepth: 2
   :caption: Power
   :hidden:

   power/index

Silicon
-------

:doc:`high-voltage/index`
   How a circuit can sit tens of volts above the chip's substrate.
:doc:`esd/index`
   How the gf180mcu I/O cells protect the pins against electrostatic
   discharge, with simulations of the foundry's cells.

.. toctree::
   :maxdepth: 2
   :caption: Silicon
   :hidden:

   high-voltage/index
   esd/index

Reference
---------

:doc:`standards`
   The standards that the pages cite, with links to each.
:doc:`glossary`
   The terms used in this documentation, in alphabetical order.

.. toctree::
   :maxdepth: 2
   :caption: Reference
   :hidden:

   standards
   glossary
