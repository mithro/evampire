.. _phy-echo-page:

1000BASE-T: the channel limits, echo and crosstalk
==================================================

This page gives the size of the cable effects that 1000BASE-T must handle,
and explains how a :term:`hybrid` and adaptive cancellers let one pair carry
both directions at once. The effects themselves are introduced in
:doc:`job`.

.. _phy-channel-limits:

The standard limits loss and crosstalk as functions of frequency
----------------------------------------------------------------

:clause:`40.7` limits the link segment with three formulas of frequency.
Each is a loss in decibels; a loss of :math:`L` dB multiplies a voltage by
:math:`10^{-L/20}`.

.. math::

   L_\text{IL}(f) < 2.1\,f^{0.529} + \frac{0.4}{f}

   L_\text{NEXT}(f) \ge 27.1 - 16.8\,\log_{10}\!\left(\frac{f}{100}\right)

   L_\text{ELFEXT}(f) > 17 - 20\,\log_{10}\!\left(\frac{f}{100}\right)

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`f`
     - Frequency, from 1 MHz to 100 MHz; the numbers in the formulas
       assume :math:`f` in MHz
     - MHz
   * - :math:`L_\text{IL}`
     - :term:`Insertion loss` of one pair, at most (:clause:`40.7.2.1`)
     - dB
   * - :math:`L_\text{NEXT}`
     - Near-end :term:`crosstalk` loss between any two pairs, at least:
       how much weaker the signal coupled from one neighbouring pair at
       the same end is than the signal on that pair
       (:clause:`40.7.3.1.1`)
     - dB
   * - :math:`L_\text{ELFEXT}`
     - Equal-level far-end crosstalk loss between the worst two pairs, at
       least: the far-end crosstalk measured against the wanted signal
       after it has crossed the same cable (:clause:`40.7.3.2.1`)
     - dB

The formulas approximate the limits of a 100 m Class D channel and include
the patch cords and connectors (:clause:`40.7.2.1`). They are limits for
one disturbing pair; the three far-end disturbers together are limited by a
power sum, at least :math:`14.4 - 20\log_{10}(f/100)` dB
(:clause:`40.7.3.2.2`).

For example, at the Nyquist frequency :math:`f = 62.5` MHz:

.. math::

   L_\text{IL} &< 2.1 \times 62.5^{0.529} + \frac{0.4}{62.5} \\
               &= 2.1 \times 8.91 + 0.006 \\
               &= 18.7\ \text{dB}

   10^{-18.7/20} = 0.116

so at least 12 % of the transmitted voltage at that frequency reaches the
far end. :numref:`tab-phy-channel-limits` gives the same calculation at
other frequencies.

.. list-table:: 1000BASE-T channel limits for a 100 m channel, from the
   formulas of :clause:`40.7`
   :name: tab-phy-channel-limits
   :header-rows: 1
   :widths: 20 20 20 20 20

   * - :math:`f` (MHz)
     - :math:`L_\text{IL}` at most (dB)
     - Voltage that arrives (%)
     - :math:`L_\text{NEXT}` at least (dB)
     - :math:`L_\text{ELFEXT}` at least (dB)
   * - 10
     - 7.1
     - 44
     - 43.9
     - 37.0
   * - 31.25
     - 13.0
     - 22
     - 35.6
     - 27.1
   * - 62.5
     - 18.7
     - 12
     - 30.5
     - 21.1
   * - 100
     - 24.0
     - 6
     - 27.1
     - 17.0

.. _phy-next-margin:

Near-end crosstalk from one pair comes within 3 dB of the signal
----------------------------------------------------------------

The wanted signal and the near-end crosstalk start from transmitters of the
same size. The wanted signal is reduced by the insertion loss, and the
crosstalk by the near-end crosstalk loss, so the wanted signal exceeds the
crosstalk from one neighbouring pair by

.. math::

   M(f) = L_\text{NEXT}(f) - L_\text{IL}(f)

where :math:`M` is the margin in dB. At 62.5 MHz,
:math:`M = 30.5 - 18.7 = 11.8` dB; at 100 MHz, :math:`M = 27.1 - 24.0 =
3.1` dB. There are three neighbouring pairs, and the transceiver's own
transmission on the same pair, the echo, is larger still. The receiver
works only because it removes these known signals, as the rest of this
page describes.

.. _phy-echo:

The hybrid removes most of the transceiver's own signal
-------------------------------------------------------

Each pair carries :math:`1000 / 4 = 250` Mbit/s in each direction at the
same time (:clause:`40.1.3`). Both ends drive the same two wires, so the
voltage at a transceiver's pins is the sum of several signals
(:numref:`fig-phy-impairments`):

#. the far end's signal, the one the receiver wants, reduced by the
   insertion loss;
#. the transceiver's own transmitted signal, at full size, and its
   reflections from connectors and impedance changes along the cable,
   together called the *echo*;
#. near-end crosstalk from the transceiver's own transmitters on the
   other three pairs;
#. far-end crosstalk from the far end's transmitters on the other three
   pairs.

.. graphviz:: cable-impairments.dot
   :name: fig-phy-impairments
   :caption: The four signals that reach the receiver of pair A; pairs C and
             D, not drawn, add more of signals 3 and 4.
   :alt: Two transceivers, local on the left and far end on the right, each
         with boxes for pair A and pair B. Four numbered lines reach the
         local pair A: 1, a thick line from the far-end pair A, the wanted
         signal; 2, a dashed loop from pair A back to itself, the echo;
         3, a dotted line from the local pair B, near-end crosstalk; 4, a
         thin line from the far-end pair B, far-end crosstalk.
   :align: center

The first stage is the :term:`hybrid`, an analogue circuit that lets one
pair carry both directions (:clause:`40.1.3`). It drives a replica of the
transmitted signal into a network matched to the line and subtracts the
replica from the line voltage, so the transceiver's own signal cancels and
the far end's signal remains (:numref:`fig-phy-hybrid`).

The subtraction is
exact only if the replica matches the real line, which a real cable and its
connectors never do, so part of the echo remains ([PHY-HEALEY]_ slides 24
to 27). In the Microchip KSZ9031 this stage is an analogue hybrid that
"relieves the burden of the ADC" ([PHY-KSZ9031]_ section 3.2.1).

.. graphviz:: hybrid.dot
   :name: fig-phy-hybrid
   :caption: A resistive hybrid subtracts a replica of the transceiver's
             own signal from the line, leaving the far-end signal.
   :alt: The driver feeds two branches: a matching resistance to the pair
         and cable, and a replica resistance to a replica load. A
         subtractor takes the line node minus the replica node and passes
         the far-end signal to the receiver and ADC.
   :align: center

.. _phy-echo-canceller:

The echo canceller predicts and subtracts what the hybrid leaves
----------------------------------------------------------------

The second stage is the echo canceller, a digital adaptive
:wikipedia:`finite impulse response <Finite_impulse_response>` (FIR)
filter. Its input is the sequence of symbols the transceiver has sent; its
output is a prediction of the echo those symbols cause at the
analogue-to-digital converter (ADC); the prediction is subtracted from the
received samples. Each filter coefficient, or *tap*, multiplies one past
symbol. The coefficients adapt continuously to keep the remaining error
small, commonly with the :wikipedia:`least-mean-squares
<Least_mean_squares_filter>` method ([PHY-TUT98]_ slide 58).

Reflections from far along the cable return long after the symbol that
caused them, so the filter is long. The 802.3ab tutorial's examples use 60
and 120 echo taps at 125 MHz ([PHY-TUT98]_ slides 33 and 51).
:doc:`integration/signal-processing` relates the length to the cable
reach.

.. _phy-crosstalk:

Three more cancellers remove near-end crosstalk
-----------------------------------------------

Near-end crosstalk comes from the transceiver's own transmitters on the
other three pairs, so the transceiver knows exactly what caused it. Each
receiver runs three more adaptive FIR filters, one for each other pair,
that predict and subtract that crosstalk ([PHY-KSZ9031]_ section 3.2.5).
With the :term:`equaliser` of :doc:`1000base-t-receiver`, each receiver has
five adaptive filters, and the transceiver has twenty ([PHY-HEALEY]_
slide 38).

Far-end crosstalk comes from symbols the receiving transceiver did not
send, so it cannot be predicted from its own symbols. The cable limits keep
it small instead (:clause:`40.7.3.2`). The 802.3ab tutorial's design point
keeps 5.7 dB of margin with worst-case far-end crosstalk and no far-end
canceller ([PHY-TUT98]_ slide 51).
