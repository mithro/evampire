USB serial port in evampire
===========================

evampire runs its USB serial port mostly in software on the processor,
with hardware helpers and an analogue front end where USB timing needs
them.

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
