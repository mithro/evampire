USB serial port
===============

These pages explain how evampire's RISC-V :ref:`processor
<arch-microcontroller>` appears to a computer as a USB serial port, through
a USB 2.0 full-speed (12 Mbit/s) data connection on the D+ and D− wires of
its USB Type-C connectors. They are written for integrated circuit
designers, digital and analogue, who have not worked with USB.

The :ref:`requirements <requirements>` ask for the USB data protocol to run
mostly in software on the processor, with built-in hardware only where the
timing of USB is beyond what the software can do. The same connectors also
carry the USB Power Delivery negotiation (see :doc:`/power/usb-pd`), and
the same processor runs it.

.. toctree::
   :maxdepth: 1
   :hidden:

   what-it-is
   signalling
   transactions
   timing
   software-cost
   analogue
   usb-pd-roles
   alternatives
   references

What each page covers:

* :doc:`what-it-is`: what a computer sees, the communications device class
  and why no custom driver is needed.
* :doc:`signalling`: host and device, the D+ and D− wires, speeds, line
  states, coding, and the parts of a packet.
* :doc:`transactions`: how packets combine into transfers, frames, how a
  device is recognised, and the descriptors a serial port needs.
* :doc:`timing`: the bit time, the reply deadline, the end of a packet and
  clock accuracy, each from the :std:`USB 2.0 specification <usb2>`.
* :doc:`software-cost`: how much processor time each part of USB takes in
  software, and the hardware helpers that reduce it.
* :doc:`analogue`: the driver, receivers, pull-up resistor and protection,
  and how they can be built in gf180mcu.
* :doc:`usb-pd-roles`: power roles and data roles, the data role swap, two
  ports, and sharing the processor with USB Power Delivery and Ethernet.
* :doc:`alternatives`: other ways to give the processor a serial port, and
  why they are or are not used elsewhere.
* :doc:`references`: the specifications, datasheets and projects cited.
