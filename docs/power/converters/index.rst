Voltage converters
==================

A board built around evampire has three converter functions
(:ref:`power-flow`, :ref:`requirements`):

* the *input converter*, which brings the Power over Ethernet input down to
  the board's power bus;
* the *USB converter*, which produces the USB Type-C output voltage when a
  USB port is a source;
* the *high-voltage converter*, which produces the 44 V to 57 V that a
  power sourcing equipment port puts on an Ethernet cable.

:doc:`fundamentals`
   Why switching converters, the buck, boost and buck-boost converters, and
   how a converter is controlled.
:doc:`in-evampire`
   How evampire's converters are arranged, how evampire controls external
   power stages, and bringing converter parts onto the chip.
:doc:`references`
   The datasheets, application notes, papers and process documents cited for
   the voltage converters.

.. toctree::
   :hidden:

   fundamentals
   in-evampire
   references
