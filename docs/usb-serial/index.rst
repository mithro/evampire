USB serial port
===============

evampire's RISC-V :ref:`processor <arch-microcontroller>` appears to a
computer as a USB serial port, through a USB 2.0 full-speed (12 Mbit/s)
data connection on the D+ and D− wires of its USB Type-C connectors.

The :ref:`requirements <requirements>` ask for the USB data protocol to run
mostly in software on the processor, with built-in hardware only where the
timing of USB is beyond what the software can do. The same connectors also
carry the :doc:`USB Power Delivery </power/usb-pd/index>` negotiation, and
the same processor runs it.

:doc:`usb-device`
   What a USB serial port is, full-speed signalling, transactions and timing.
:doc:`implementation`
   Software cost and hardware helpers, the analogue front end, USB Power
   Delivery roles, and alternatives.
:doc:`references`
   The specifications, datasheets and projects cited for the USB serial port.

.. toctree::
   :hidden:

   usb-device
   implementation
   references
