Converter fundamentals
======================

Switching voltage converters use transistors as switches and store energy
for a moment in an inductor.

:doc:`why-switching`
   Why the power path uses switching converters instead of linear
   regulators, with the losses worked out at evampire's voltages.
:doc:`buck`
   The step-down (buck) converter: how it works, its duty cycle, inductor
   ripple and conduction modes.
:doc:`boost`
   The step-up (boost) converter, worked the same way.
:doc:`buck-boost`
   Converters that step up or down: the inverting buck-boost, the
   four-switch buck-boost used in USB Power Delivery sources, and the
   isolated flyback converter.
:doc:`control`
   Pulse-width modulation, voltage-mode and current-mode control, the
   feedback loop, soft start, protection, dead time, high-side gate drive,
   switching frequency and losses.

.. toctree::
   :hidden:

   why-switching
   buck
   boost
   buck-boost
   control
