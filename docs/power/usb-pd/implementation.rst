USB Power Delivery in evampire
==============================

USB Power Delivery on evampire needs software on the processor, analogue
circuits for each port, protection for the CC pins, and circuits that the
gf180mcu voltage limits allow on the chip.

:doc:`software`
   What the processor must do to send and receive messages, and the hardware
   helpers that reduce it.
:doc:`analogue`
   The analogue circuits for one port.
:doc:`cc-protection`
   Protecting the CC pins against a short to VBUS, and how that differs from
   electrostatic discharge.
:doc:`on-chip-or-external`
   The gf180mcu voltage limits, and which circuits can be on the chip.

.. toctree::
   :hidden:

   software
   analogue
   cc-protection
   on-chip-or-external
