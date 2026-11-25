USB serial port in evampire
===========================

These pages cover how evampire builds the USB serial port.

:doc:`software-cost`
   How much processor time each part of USB takes in software, and the
   hardware helpers that reduce it.
:doc:`analogue`
   The driver, receivers, pull-up resistor and protection, and how they can
   be built in gf180mcu.
:doc:`usb-pd-roles`
   Power roles and data roles, the data role swap, two ports, and sharing
   the processor with USB Power Delivery and Ethernet.
:doc:`alternatives`
   Other ways to give the processor a serial port, and why they are or are
   not used elsewhere.

.. toctree::
   :hidden:

   software-cost
   analogue
   usb-pd-roles
   alternatives
