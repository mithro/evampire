evampire
========

evampire is an integrated circuit for the `GlobalFoundries 180 nm MCU
(gf180mcu) <https://gf180mcu-pdk.readthedocs.io/>`_ process, manufactured
through `wafer.space <https://wafer.space/>`_. It is a three-port gigabit
:wikipedia:`Ethernet` hub with a small :wikipedia:`RISC-V` processor that
also moves power between
:wikipedia:`Power over Ethernet <Power_over_Ethernet>` and
:wikipedia:`USB Type-C <USB-C>`.

The chip passes traffic straight through between two Ethernet ports,
except for a few kinds of frame listed in
:ref:`the forwarding requirements <req-forwarding>`. The
processor receives selected frames from either port and sends frames of its
own. A
board built around evampire can be powered over Ethernet and supply power
over USB Type-C, or the other way around.

:numref:`fig-overview` shows the main blocks of evampire and how data and
power flow between them.

.. figure:: index/overview.svg
   :name: fig-overview
   :alt: Block diagram. Data runs in a straight line along the top, between
         Ethernet port A, Ethernet transceiver A, the cut-through hub,
         Ethernet transceiver B and Ethernet port B, with RGMII links between
         each transceiver and the hub. The hub exchanges data with the RISC-V
         processor below it, which exchanges data with the USB interface for
         the serial port and USB Power Delivery. That interface connects
         straight down to the USB Type-C port over the D+, D− and CC wires,
         hopping over the power row. The processor controls the power control
         block, which measures and limits the power stages. Power runs in a
         straight line along the bottom: from Ethernet port A through the
         powered device and buck converter to the power bus on the board,
         then through the boost converter and power sourcing equipment to
         Ethernet port B. Below the bus, power comes up from the USB Type-C
         port through the USB Power Delivery sink switch, and goes down to it
         through the USB Power Delivery source buck-boost converter. The
         first-version chip is drawn as a die with a ring of bond pads around
         the hub, processor, USB interface and power control; coloured pads
         mark the RGMII links, the USB wires and the power control signals
         that leave it. A dashed outline that also includes both Ethernet
         transceivers marks the chip in the full design. A dotted outline
         around the power stages is labelled "placement open".
   :align: center

   The main blocks of evampire. Data flows along the top row and power along
   the bottom row, each from Ethernet port A to port B. The first-version
   chip is drawn as a die, where a coloured pad marks each signal that leaves
   it, and the dashed outline is the chip in the full design.

The two chip outlines are the two board configurations of
:numref:`tab-power-board-configs`. The first version connects to separate
Ethernet transceiver chips over RGMII, and the full design builds the
transceivers into evampire. Which power stages inside the dotted outline
move onto the chip is an open question (:ref:`requirements-open-questions`).
The figure shows the power roles of the first version: port A receives power
and port B supplies it.

This documentation describes what the chip does and explains the Ethernet
and power-delivery standards that evampire implements. It is written for
readers who are familiar with digital and analogue integrated circuit design
but not with the Ethernet or USB Power Delivery standards.

:doc:`overview`
   What evampire does, in outline.
:doc:`requirements`
   Every requirement the design meets, and the questions still open.
:doc:`architecture/index`
   The blocks inside evampire and how frames move between them.
:doc:`ethernet/index`
   The Ethernet interfaces, from the chip's pins to the cable.
:doc:`power/index`
   How power moves between Power over Ethernet and USB Type-C, and the
   board configurations.
:doc:`usb-serial/index`
   The USB serial port carried on the USB Type-C data wires.
:doc:`standards`
   The standards that the pages cite, with links to each.
:doc:`glossary`
   The terms used in this documentation, in alphabetical order.

.. toctree::
   :maxdepth: 2
   :caption: Contents
   :hidden:

   overview
   requirements
   architecture/index
   ethernet/index
   power/index
   usb-serial/index
   standards
   glossary
