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
:doc:`high-voltage/index`
   How a circuit can sit tens of volts above the chip's substrate.
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
   high-voltage/index
   usb-serial/index
   standards
   glossary
