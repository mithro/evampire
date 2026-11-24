.. _phy-10base-t:

10BASE-T: Manchester coding and link pulses
===========================================

This page describes 10BASE-T (:clause:`14`), the simplest of the three
twisted-pair speeds: its coding, its signal levels and the link pulses that
show a cable is connected.

.. _phy-manchester:

Manchester coding
-----------------

10BASE-T uses one pair for each direction: pins 1 and 2 of the
:term:`RJ45` socket to transmit and pins 3 and 6 to receive
(:clause:`14.5.1`). It sends the data bits at 10 Mbit/s with
:wikipedia:`Manchester coding <Manchester_code>`: each 100 ns bit is split
into two halves at opposite levels, so every bit has a transition in its
middle. A 1 bit goes from low to high in the middle of the bit and a 0 bit
goes from high to low (:numref:`fig-phy-manchester`) [PHY-UNH10T]_.

.. wavedrom::
   :caption: Manchester coding as used by 10BASE-T, 100 ns per bit.
   :name: fig-phy-manchester
   :alt: Timing diagram of the bits 1 0 1 1 0 0 1 and the Manchester
         waveform, which has a transition in the middle of every bit: low to
         high for a 1, high to low for a 0.

   { "signal": [
       { "name": "bit", "wave": "=======", "data": ["1","0","1","1","0","0","1"], "period": 2 },
       { "name": "Manchester", "wave": "01.0.101.010.1" }
     ],
     "config": { "hscale": 1 }
   }

The receiver recovers the bit clock from the mid-bit transitions, so no
separate clock is sent. The cost is bandwidth: the line changes up to twice
per bit, so the fundamental frequency lies between 5 MHz (alternating 1 and
0) and 10 MHz (all 1 bits or all 0 bits).

.. _phy-10base-t-levels:

Signal levels
-------------

A 10BASE-T transmitter drives a peak of 2.2 V to 2.8 V, and an idle
receiver ignores signals below 300 mV. :numref:`tab-phy-10base-t` gives
these and the other main transmitter and receiver limits.

.. list-table:: 10BASE-T transmitter and receiver limits
   :name: tab-phy-10base-t
   :header-rows: 1
   :widths: 40 15 15 30

   * - Quantity
     - Min
     - Max
     - Clause
   * - Peak differential output into 100 Ω (V)
     - 2.2
     - 2.8
     - :clause:`14.3.1.2.1`
   * - Peak differential output of 10BASE-Te into 100 Ω (V)
     - 1.54
     - 1.96
     - :clause:`14.3.1.2.1`
   * - Harmonics of an all-ones signal below the fundamental (dB)
     - 27
     -
     - :clause:`14.3.1.2.1`
   * - Output and input return loss, 5 MHz to 10 MHz (dB)
     - 15
     -
     - :clause:`14.3.1.2.2`, :clause:`14.3.1.3.4`
   * - Received signal rejected when idle, after a 15 MHz filter (mV)
     -
     - 300
     - :clause:`14.3.1.3.2`

10BASE-Te is a lower-amplitude version of 10BASE-T defined in the same
clause, for use with :wikipedia:`Energy-Efficient Ethernet
<Energy-Efficient_Ethernet>`. It interoperates with 10BASE-T when its
minimum cabling requirements are met (:clause:`14.1.1.1`). The waveform must also fit a voltage template
(:clause:`Figure 14-10 <14>`), which the transmitter meets by shaping its
output edges.

While idle, the receiver must ignore any signal whose peak is below 300 mV
after a 3-pole, 15 MHz low-pass filter, so that noise on a silent line is
not taken for data (:clause:`14.3.1.3.2`). For reference, the Microchip
KSZ9031 sets its squelch threshold at 300 mV ([PHY-KSZ9031]_ section
3.1.5).

.. _phy-link-pulses:

Link test pulses
----------------

Between frames the line is silent, except for a single positive
*link test pulse* after every 16 ms ± 8 ms of silence
(:clause:`14.2.1.1`), which shows the far end that the cable is connected. The pulse has to fit the template of
:clause:`Figure 14-13 <14>`: its peak lies between 585 mV and 3.1 V, and it
is about one bit time, 100 ns, wide.

A receiver that sees neither data nor a link test pulse for 50 ms to
150 ms, the *link_loss* time, declares the link failed and stops
transmitting data (:clause:`14.2.1.7`). The link pulses are also the
building blocks of :doc:`autonegotiation`, which replaces each single
pulse with a burst of pulses that carries data.
