Voltage converters
==================

These pages explain how the switching voltage converters in evampire's power
path work, starting from the simplest converter, and what evampire needs in
order to control them and, step by step, to take over more of each converter.
They are written for chip designers, digital and analogue, who have not
designed power converters before.

A board built around evampire has three converter functions
(:ref:`power-flow`, :ref:`requirements`):

* the *input converter*, which brings the Power over Ethernet input down to
  the board's power bus;
* the *USB converter*, which produces the USB Type-C output voltage when a
  USB port is a source;
* the *high-voltage converter*, which produces the 44 V to 57 V that a
  power sourcing equipment port puts on an Ethernet cable.

The pages build up in this order:

:doc:`converters/why-switching`
   Why the power path uses switching converters instead of linear
   regulators, with the losses worked out at evampire's voltages.

:doc:`converters/buck`
   The step-down (buck) converter: how it works, its duty cycle, inductor
   ripple and conduction modes.

:doc:`converters/boost`
   The step-up (boost) converter, worked the same way.

:doc:`converters/buck-boost`
   Converters that step up or down: the inverting buck-boost, the
   four-switch buck-boost used in USB Power Delivery sources, and the
   isolated flyback converter.

:doc:`converters/control`
   Pulse-width modulation, voltage-mode and current-mode control, the
   feedback loop, soft start, protection, dead time, high-side gate drive,
   switching frequency and losses.

:doc:`converters/arrangement`
   The voltage and current ranges of evampire's three converters in every
   operating mode, where the ranges overlap, and the ways of arranging the
   converters, including less common alternatives.

:doc:`converters/first-version`
   What evampire provides to control external gate drivers and power
   transistors, which parts of the control run in software, how the
   converter sensing also serves power monitoring and limiting, and how the
   board starts before any software runs.

:doc:`converters/integration`
   Moving the gate drivers, and then the power transistors, onto evampire,
   and what each step needs from the gf180mcu process.

:doc:`converters/references`
   The data sheets, application notes, papers and process documents cited
   on these pages.

.. toctree::
   :hidden:

   converters/why-switching
   converters/buck
   converters/boost
   converters/buck-boost
   converters/control
   converters/arrangement
   converters/first-version
   converters/integration
   converters/references
