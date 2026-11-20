The boost converter
===================

This page explains the step-up converter, called a
:wikipedia:`boost converter <Boost_converter>`, in the same way as
:doc:`buck`: its parts, its duty cycle, its inductor ripple and what limits
it. On an evampire board the high-voltage converter, which produces the
44 V to 57 V for a power sourcing equipment port, is a step-up converter
(:ref:`power-flow`).

Parts and operation
-------------------

.. graphviz:: boost.dot
   :name: fig-conv-boost
   :caption: Power stage of a synchronous boost converter.
   :alt: Schematic: the input source connects through the inductor L to the
         switch node; switch S1 connects the switch node to ground; switch
         S2 connects the switch node to the output, where the output
         capacitor C and the load connect to ground.
   :align: center

The boost converter uses the same parts as the buck converter, rearranged
(:numref:`fig-conv-boost`). The inductor is now on the input side, the
low-side switch S1 does the switching, and S2 (a diode in the simplest
form) passes the inductor current to the output. Each period has two parts:

#. S1 on, S2 off, for a time :math:`D \, T`. The inductor has
   :math:`V_\text{in}` across it and its current rises, storing energy. The
   output capacitor alone supplies the load.
#. S1 off, S2 on, for :math:`(1 - D) \, T`. The inductor current flows
   through S2 into the output. The inductor has
   :math:`V_\text{in} - V_\text{out}` across it, which is negative because
   the output is higher than the input, so its current falls.

The duty cycle sets the output voltage
--------------------------------------

Volt-second balance on the inductor (:doc:`buck`) gives

.. math::

   V_\text{in} \, D \, T + (V_\text{in} - V_\text{out}) \, (1 - D) \, T = 0

.. math::

   \frac{V_\text{out}}{V_\text{in}} = \frac{1}{1 - D},
   \qquad
   D = 1 - \frac{V_\text{in}}{V_\text{out}}

with the symbols in :numref:`tab-conv-sym-boost`, for lossless parts in
continuous conduction. The ripple of the inductor current is the rise
during the on time [CONV-SLVA372]_ (Equation 2):

.. math::

   \Delta I_L = \frac{V_\text{in} \, D}{L \, f_\text{sw}}

.. list-table:: Symbols for the boost converter
   :name: tab-conv-sym-boost
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`V_\text{in}`, :math:`V_\text{out}`
     - Input and output voltage
     - V
   * - :math:`D`
     - Duty cycle, the fraction of the period with S1 on
     - fraction
   * - :math:`T`, :math:`f_\text{sw}`
     - Switching period and frequency
     - s, Hz
   * - :math:`L`
     - Inductance
     - H
   * - :math:`I_\text{in}`
     - Input current, equal to the average inductor current
     - A
   * - :math:`\Delta I_L`
     - Peak-to-peak inductor current ripple
     - A
   * - :math:`P_\text{out}`
     - Output power
     - W

As a worked example, take a high-voltage converter that raises a 20 V USB
Power Delivery input to 54 V for a Type 2 power sourcing equipment port,
which supplies at most 30 W (:clause:`33`, see :doc:`../poe/index`). The 54 V
output, 250 kHz and 100 µH are illustrative values. Then

.. math::

   D = 1 - \frac{20}{54} = 0.630

   I_\text{in} = \frac{P_\text{out}}{V_\text{in}} = \frac{30}{20} = 1.5 \ \text{A}

.. math::

   \Delta I_L = \frac{20 \times 0.630}{100 \times 10^{-6} \times 250 \times 10^{3}}
              = 0.504 \ \text{A}

The ripple is 34 % of the input current, within the 20 % to 40 % commonly
used [CONV-SLVA372]_ (Equation 6), and the inductor current peaks at
:math:`1.5 + 0.252 = 1.752` A. The output current is only
:math:`30 / 54 = 0.556` A: a boost converter draws more current from its
input than it delivers, in the ratio of the voltages.

Large step-up ratios need long on times
---------------------------------------

The USB Power Delivery source on the other end of the cable decides which
input voltages are available (:doc:`../usb-pd/index`).
:numref:`tab-conv-boost-duty` shows the duty cycle needed to reach 54 V from
each fixed USB Power Delivery voltage.

.. list-table:: Boost duty cycle from each fixed USB voltage to 54 V
   :name: tab-conv-boost-duty
   :header-rows: 1
   :widths: 34 33 33

   * - Input (V)
     - Duty cycle
     - Voltage gain
   * - 5
     - 0.907
     - 10.80
   * - 9
     - 0.833
     - 6.00
   * - 15
     - 0.722
     - 3.60
   * - 20
     - 0.630
     - 2.70
   * - 28
     - 0.481
     - 1.93
   * - 36
     - 0.333
     - 1.50
   * - 48
     - 0.111
     - 1.12

At high duty cycles the off time, during which all the energy is passed to
the output, becomes short. The current in S2 and the output capacitor then
comes in short, high pulses, and the losses in the parts' resistances rise.

Controllers limit the duty cycle: for example the LM5155 boost controller
has a maximum duty cycle of 80 % to 90 % or 90 % to 96 %, depending on its
frequency setting [CONV-LM5155]_ (Section 8.5, DMAX1 and DMAX2).

For reference, the PMP7979 design takes 12 V to 67 V in and produces 54 V at
4.8 A with a two-phase
boost converter [CONV-PMP7979]_. A large ratio can also be split between two
stages, or made with a transformer or a switched-capacitor stage
(:doc:`arrangement`).

A short on a boost output bypasses the switches
-----------------------------------------------

In a boost converter there is always a path from the input, through the
inductor and S2 (or its diode, or the body diode of a transistor), to the
output. If the output is short-circuited, current flows along that path
whatever the switches do, limited only by the source and the resistance of
the path. Turning S1 off does not stop it.

Stopping it needs a switch in
series with the input or the output that can block current, or a converter
in which a series switch is part of the power stage, such as the
four-switch buck-boost converter (:doc:`buck-boost`). This matters for the
high-voltage converter, whose output goes to an Ethernet cable that a user
can short (:doc:`first-version`).

The boost converter is harder to control
----------------------------------------

When the duty cycle of a boost converter increases, the output first
*falls*, because S2 conducts for a shorter time, and only rises once the
inductor current has grown. This delayed, wrong-direction response limits
how fast a feedback loop can correct the output. :doc:`control` explains it
and works out an example.
