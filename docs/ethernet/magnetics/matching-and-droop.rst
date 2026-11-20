Matching the cable and passing low frequencies
==============================================

This page works out two requirements that the :term:`magnetics` of a
gigabit port help to meet: how closely the port must match the 100 Ω cable
(its :term:`return loss`), and how much of a slow signal it must pass (its
:term:`droop`). The same numbers set the size of the capacitors that
replace the transformer on :doc:`coupling-capacitors`.

.. _magnetics-return-loss:

The port must match 100 Ω to within a return loss
-------------------------------------------------

Ethernet transceivers drive and terminate a 100 Ω differential load
directly ([MAG-KSZ9031]_, section 12; [MAG-DP83867]_, section 9.2),
so the transformer has a 1:1 ratio and the cable appears as 100 Ω at the
transceiver. Any difference between the port's impedance and the cable's
reflects part of the arriving signal. The reflection is described by the
:wikipedia:`reflection coefficient <Reflection_coefficient>`, and the return
loss says how much weaker the reflected signal is than the arriving one:

.. math::

   \Gamma = \frac{Z - Z_0}{Z + Z_0}

   \text{RL} = -20 \log_{10} \lvert \Gamma \rvert

.. list-table::
   :header-rows: 1
   :widths: 18 62 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`\Gamma`
     - Reflection coefficient: the reflected voltage divided by the arriving
       voltage
     - none
   * - :math:`Z`
     - Impedance of the port
     - Ω
   * - :math:`Z_0`
     - Impedance of the cable
     - Ω
   * - :math:`\text{RL}`
     - Return loss
     - dB

These are the standard definitions for a reflection at the end of a
transmission line (see :wikipedia:`Return loss <Return_loss>`).

A 1000BASE-T port must have a return loss of at least 16 dB from 1 MHz to
40 MHz, against any cable impedance from 85 Ω to 115 Ω, that is 100 Ω
± 15 % (:clause:`40.8.3.1`). Solving the two equations for a purely
resistive port on a 100 Ω cable gives the range of port impedance that
meets the limit:

.. math::

   \lvert\Gamma\rvert_\text{max} = 10^{-16/20} = 0.158

.. math::

   Z_\text{max} &= Z_0 \frac{1 + 0.158}{1 - 0.158} = 138\ \Omega

   Z_\text{min} &= Z_0 \frac{1 - 0.158}{1 + 0.158} = 73\ \Omega

The port alone can be anywhere from 73 Ω to 138 Ω on a 100 Ω cable. The
transceiver and everything between it and the cable share that budget.
Microchip recommends magnetics with at least 2 dB of margin on the limit
([MAG-ENT98]_, section 4.2).

From 40 MHz to 100 MHz the limit falls with frequency (:clause:`40.8.3.1`):

.. math::

   \text{RL}_\text{min}(f) = 10 - 20 \log_{10} \frac{f}{80\ \text{MHz}}

.. list-table::
   :header-rows: 1
   :widths: 18 62 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`\text{RL}_\text{min}`
     - Smallest return loss allowed
     - dB
   * - :math:`f`
     - Frequency, from 40 MHz to 100 MHz
     - Hz

At 100 MHz the limit is
:math:`10 - 20 \times \log_{10} 1.25 = 10 - 1.9 = 8.1\ \text{dB}`.

The :wikipedia:`insertion loss <Insertion_loss>` of the magnetics is the
signal lost in passing through them. Gigabit magnetics state at most 1 dB
from 1 MHz to 100 MHz ([MAG-PULSE]_, electrical table; [MAG-WURTH]_,
electrical table). An insertion loss of 1 dB is an amplitude ratio of
:math:`10^{-1/20} = 0.89`, so at most 11 % of the signal amplitude is lost.

.. _magnetics-droop:

The transformer's inductance sets the droop
-------------------------------------------

A transformer cannot pass direct current, and passes low frequencies
poorly. The reason is its
magnetising inductance (see :wikipedia:`Transformer`): the
inductance of one winding with the other left open, given in data sheets as
the open-circuit inductance. This inductance sits across the signal path
and shunts low frequencies away.

If the transmitter holds a constant voltage, the voltage on the cable side
decays towards zero. This decay is called droop. Long stretches of data
whose average is not zero make the received signal's average level drift,
which is called :term:`baseline wander` (see
:doc:`../phy-electrical/index`).

A first-order model gives the droop
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Treat the transformer as an ideal 1:1 transformer with its magnetising
inductance across it. Seen from that inductance, the transceiver's 100 Ω
source and the 100 Ω cable are in parallel. The circuit is a first-order
:wikipedia:`high-pass filter <High-pass_filter>`, and droop is an
exponential decay with a :wikipedia:`time constant <Time_constant>`:

.. math::

   R_\text{p} = \frac{R_\text{s} Z_0}{R_\text{s} + Z_0}

   \tau = \frac{L}{R_\text{p}}

   f_\text{c} = \frac{1}{2\pi\tau}

.. list-table::
   :header-rows: 1
   :widths: 18 62 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`R_\text{s}`
     - Output resistance of the transceiver, 100 Ω
     - Ω
   * - :math:`Z_0`
     - Impedance of the cable, 100 Ω
     - Ω
   * - :math:`R_\text{p}`
     - The two in parallel
     - Ω
   * - :math:`L`
     - Magnetising inductance
     - H
   * - :math:`\tau`
     - Time constant of the droop
     - s
   * - :math:`f_\text{c}`
     - Corner frequency of the high-pass filter
     - Hz

The model leaves out the leakage inductance and the capacitance of the
windings, which matter only at high frequencies. IEEE 802.3 uses the same
model for the 100BASE-TX alternative described below, with
:math:`\tau = 2L/R` for a 100 Ω termination :math:`R` (:clause:`25.4.5.1`,
equation 25-1).

With :math:`R_\text{p} = 50\ \Omega` and the usual data-sheet value
:math:`L = 350\ \mu\text{H}` ([MAG-KSZ9031]_, section 12;
[MAG-WURTH]_):

.. math::

   \tau = \frac{350\ \mu\text{H}}{50\ \Omega} = 7.0\ \mu\text{s}

   f_\text{c} = \frac{1}{2\pi \times 7.0\ \mu\text{s}} = 23\ \text{kHz}

1000BASE-T needs at least 80 µH
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

500 ns after the start of a constant level in the transmitter test pattern,
more than 73.1 % of the voltage must remain, into a 100 Ω test load
(:clause:`40.6.1.2.2`). In the model the remaining fraction is
:math:`e^{-t/\tau}`:

.. math::

   e^{-t/\tau} > k

   \tau > \frac{t}{\ln(1/k)}

   L > \tau R_\text{p}

.. list-table::
   :header-rows: 1
   :widths: 18 62 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`t`
     - Time after the start of the constant level, 500 ns
     - s
   * - :math:`k`
     - Fraction of the voltage that must remain, 0.731
     - none

With these values:

.. math::

   \tau > \frac{500\ \text{ns}}{\ln(1/0.731)} = \frac{500\ \text{ns}}{0.313}
   = 1.6\ \mu\text{s}

   L > 1.6\ \mu\text{s} \times 50\ \Omega = 80\ \mu\text{H}

An IEEE 802.3 maintenance proposal reaches the same 80 µH ([MAG-TRACY]_,
slide 5). With 350 µH, :math:`e^{-0.5/7.0} = 0.93`: 93 % of the voltage
remains, a large margin over 73.1 %.

The transmit waveform templates of :clause:`40.6.1.2.3` were drawn for a
transformer high-pass pole anywhere from 1 Hz to 100 kHz
(:clause:`40.6.1.2.3`, note 1). A 1.6 µs time constant puts the pole at
99.5 kHz, at the edge of that range.

Gigabit magnetics are specified at 350 µH for 100BASE-TX
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Gigabit magnetics are specified at 350 µH because the same parts serve
100BASE-TX. 100BASE-TX takes its electrical specification from the FDDI
twisted-pair standard, :std:`ANSI X3.263 <X3.263>` (:clause:`25`). Its
section 9.1.7 requires at least 350 µH at the transmitter with any direct
bias current from 0 mA to 8 mA ([MAG-LAW]_, slide 3). Data sheets therefore
give the inductance at 100 kHz, 100 mV and 8 mA of bias
([MAG-KSZ9031]_, section 12).

IEEE 802.3-2022 gives a 100BASE-TX transmitter in Power over Ethernet
equipment a second way to comply. A transmitter in a Type 2 port above
13 W, or in any Type 3 or Type 4 port, can instead show an equivalent time
constant above 2.4 µs (:clause:`25.4.5`, :clause:`25.4.5.1`).

Two time constants are the targets for a port without a transformer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Whatever replaces the transformer must give a time constant of at least the
1000BASE-T minimum, :math:`\tau_\text{min} = 1.6\ \mu\text{s}`. Standard
magnetics give :math:`\tau_\text{mag} = 7.0\ \mu\text{s}`. Link partners'
transceivers are designed for magnetics of this kind (their data sheets ask
for them: [MAG-KSZ9031]_, section 12; [MAG-DP83867]_, section 9.2),
so matching :math:`\tau_\text{mag}` asks nothing new of their receivers.
:doc:`coupling-capacitors` turns both values into capacitor sizes.
