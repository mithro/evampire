How an Ethernet transceiver works
=================================

This page explains, from an electrical point of view, how an Ethernet
transceiver turns the digital RGMII signals into the analog signals carried
on an Ethernet cable, and back again.

The transceiver sits between evampire and the coupling transformers (the
"magnetics"). On one side it exchanges bytes with evampire over RGMII (see
:doc:`rgmii`). On the other side it drives and receives small analog
voltages on the twisted pairs of the cable, through the transformers
described in :doc:`magnetics`. Ethernet documentation calls this chip the
*PHY*, short for "physical layer device". This page uses "transceiver".

.. contents:: On this page
   :local:
   :depth: 1

The job of the transceiver
--------------------------

A typical gigabit transceiver supports three speeds, each defined by its own
part of the IEEE 802.3 Ethernet standard:

* **1000BASE-T**: 1000 Mbit/s over all four twisted pairs of the cable
  (IEEE 802.3 Clause 40).
* **100BASE-TX**: 100 Mbit/s over two of the pairs (Clauses 24 and 25).
* **10BASE-T**: 10 Mbit/s over two of the pairs (Clause 14).

In the names, the number is the data rate in Mbit/s, "BASE" means the
signal is sent directly as voltage levels rather than modulated onto a
carrier, and "T" means twisted-pair cable.

When a cable is plugged in, the transceivers at the two ends first exchange
a short description of what each can do, and pick the fastest speed they
both support. This is called *autonegotiation* (Clause 28). After that,
the transceiver's work is to:

* take bytes from evampire, add enough structure that the far end can find
  its clock and the frame boundaries, and turn them into a sequence of
  voltage levels that fits through the cable;
* receive the far end's voltage levels, which arrive smaller, smeared out in
  time and mixed with interference, and turn them back into the original
  bytes;
* report its status (cable connected, speed chosen, errors) through a set of
  registers that evampire reads over a two-wire management interface.

The units used throughout this page:

Symbol
   One voltage level held on the line for one fixed time slot. A symbol can
   carry less than one bit, one bit, or several bits, depending on how many
   distinct levels are allowed.

Symbol rate (baud)
   The number of symbols sent per second on one pair. 125 Mbaud means
   125 million symbols per second, one every 8 ns.

Differential signal
   Each pair carries the voltage difference between its two wires. All
   amplitudes on this page are differential voltages across the cable's
   100 Ω impedance.

The cable
---------

An Ethernet cable holds four pairs of copper wires. The two wires of each
pair are twisted around each other, which makes the pair a balanced
transmission line with a characteristic impedance of 100 Ω, and makes it
pick up and radiate much less interference than untwisted wires would.

1000BASE-T is designed for up to 100 m of "Category 5" cable, a grade of
cable whose performance is specified up to 100 MHz. That 100 m channel
includes up to 90 m of fixed building cable plus up to 10 m of flexible
patch cords and up to four connectors. The design target is fewer than one
bit error in every :math:`10^{10}` bits.

The cable affects the signal in four ways that drive the whole design of the
transceiver:

Insertion loss (attenuation)
   The signal gets smaller as it travels. The loss grows with frequency
   because of the skin effect: at higher frequencies the current flows in a
   thinner layer at the surface of each conductor, so the resistance rises.
   The 1000BASE-T channel is allowed a loss of up to
   :math:`2.1 f^{0.529} + 0.4/f` dB at frequency :math:`f` in MHz, which
   is 24 dB at 100 MHz. A pulse sent down the cable therefore arrives both
   smaller and spread out in time, so that each symbol overlaps the next few.
   This overlap is called *inter-symbol interference*.

Reflections
   Any change of impedance, at a connector, a patch cord or the far end,
   sends part of the signal back towards the sender. The size of the
   reflection is described by the *return loss*: how many dB weaker the
   reflected signal is than the incident one.

Near-end crosstalk (NEXT)
   A changing current in one pair induces a small voltage in the
   neighbouring pairs. When the disturbing transmitter and the disturbed
   receiver are at the same end of the cable, the coupling is called
   near-end crosstalk. It is strong because the disturbing signal has not
   yet been attenuated by the cable.

Far-end crosstalk (FEXT)
   The same coupling, but from a transmitter at the far end of the cable
   into a receiver at the near end. The disturbing signal has travelled the
   length of the cable, so far-end crosstalk is weaker than near-end
   crosstalk.

The table gives the limits used for the 1000BASE-T channel. Crosstalk is
given as *loss*: how many dB weaker the coupled signal is than the
disturbing signal. The far-end value is given relative to the wanted
signal, which has already lost the insertion loss on the same path.

.. list-table:: 1000BASE-T channel limits on a 100 m Category 5 channel
   (calculated from the limit formulas in the 802.3ab tutorial; see
   References)
   :header-rows: 1
   :widths: 16 22 22 22 18

   * - Frequency
     - Insertion loss (at most)
     - Signal remaining
     - Near-end crosstalk loss (at least)
     - Far-end crosstalk relative to the wanted signal (at least)
   * - 10 MHz
     - 7.1 dB
     - 44 %
     - 43.9 dB
     - 37.0 dB
   * - 31.25 MHz
     - 13.0 dB
     - 22 %
     - 35.6 dB
     - 27.1 dB
   * - 62.5 MHz
     - 18.7 dB
     - 12 %
     - 30.5 dB
     - 21.1 dB
   * - 100 MHz
     - 24.0 dB
     - 6 %
     - 27.1 dB
     - 17.0 dB

The formulas behind the table are :math:`27.1 - 16.8\log_{10}(f/100)` dB
for near-end crosstalk loss between pairs, and
:math:`17 - 20\log_{10}(f/100)` dB for the worst-pair far-end crosstalk
relative to the wanted signal.

Comparing the columns shows the difficulty. At 62.5 MHz the wanted signal
from the far end has lost 18.7 dB, while the near-end crosstalk from a single
neighbouring pair may be only 30.5 dB below a full-size transmitter, so only
about 12 dB below the wanted signal. At 100 MHz the gap shrinks to about
3 dB. With three neighbouring pairs, and with the transceiver's own
transmission on the same pair, the receiver would not work without the
cancellation techniques described below.

Inside a gigabit transceiver
----------------------------

.. _fig-phy-blocks:

.. graphviz:: phy-electrical/transceiver-blocks.dot
   :caption: Inside a gigabit transceiver. One of the four identical pair
             channels is shown. Bold arrows carry data; dashed arrows carry
             copies of transmitted symbols to the cancellers; dotted arrows
             carry clocks and control.
   :align: center

:numref:`fig-phy-blocks` shows the main blocks of a 10/100/1000 transceiver
working at 1000 Mbit/s. Each of the four pairs has its own copy of the
blocks in the middle; the blocks at the bottom are shared. The blocks are:

RGMII interface
   Receives one byte every 8 ns from evampire (4 bits on each edge of a
   125 MHz clock), and sends received bytes back the same way.

Scrambler and trellis encoder
   Mixes the data with a pseudo-random sequence, adds one bit of
   error-correcting redundancy, and maps the result onto five-level symbols
   for the four pairs. Described in `1000BASE-T in detail`_.

Transmit shaping filter
   A short digital filter that shapes the symbols so that less energy is
   sent at high frequencies, which reduces radiated interference.

DAC and line driver
   A digital-to-analog converter running at 125 million samples per second
   that drives the pair through the transformer. Because it must produce
   many distinct levels, the driver must be linear rather than just switch
   between two states.

Hybrid
   An analog circuit that lets the same pair carry both directions at once.
   It subtracts an estimate of the transceiver's own transmitted signal from
   the voltage on the pair, so that what goes on to the receiver is mostly
   the signal from the far end.

Variable-gain amplifier, filter and ADC
   Adjusts the received signal to fill the input range of the
   analog-to-digital converter, removes noise above the band of interest,
   and samples once per symbol at 125 million samples per second.

Echo canceller and near-end crosstalk cancellers
   Adaptive digital filters that predict, from the symbols this transceiver
   has just transmitted, how much of its own signal leaks into each receiver,
   and subtract it. Each receiver has one echo canceller (for its own pair)
   and three near-end crosstalk cancellers (one for each of the other
   pairs).

Adaptive equalizer
   An adaptive digital filter that undoes the cable's frequency-dependent
   loss and so removes most of the inter-symbol interference.

Trellis decoder and descrambler
   Uses the redundancy added by the encoder to choose the most likely
   sequence of transmitted symbols, even when noise has pushed individual
   samples closer to the wrong level, then removes the pseudo-random
   sequence to recover the original bytes.

Clock synthesis and clock recovery
   A phase-locked loop multiplies a 25 MHz reference, from a crystal or an
   oscillator, up to the 125 MHz symbol clock and the other internal clocks.
   A second loop adjusts the phase of the ADC sampling clock so that each
   sample is taken at the best point in the symbol. Common commercial parts
   such as the TI DP83867 and Microchip KSZ9031 both use a 25 MHz crystal,
   and both can output a 125 MHz clock for other chips on the board (the
   DP83867 can also output 25 MHz).

Autonegotiation
   Sends and receives the link pulses used to agree on a speed before data
   flows. Described in `Autonegotiation`_.

Management registers
   A set of 16-bit registers, read and written over a two-wire serial
   interface (a clock, MDC, and a bidirectional data line, MDIO). The first
   few registers are defined by the IEEE 802.3 standard (Clause 22) and are
   the same in every transceiver: control, status, identification and the
   autonegotiation advertisement and result. Further registers are specific
   to each part.

1000BASE-T in detail
--------------------

Where 1000 Mbit/s comes from
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1000BASE-T sends on all four pairs at the same time, in both directions at
the same time, at 125 Mbaud on every pair. Each symbol carries two data bits
per pair:

.. math::

   4\ \text{pairs} \times 125 \times 10^{6}\ \tfrac{\text{symbols}}{\text{s}}
   \times 2\ \tfrac{\text{bits}}{\text{symbol}}
   = 1000 \times 10^{6}\ \tfrac{\text{bits}}{\text{s}}

So in every 8 ns symbol period, the four pairs together carry exactly one
byte in each direction. This is the same byte rate as the RGMII interface,
which carries one byte per 8 ns cycle of its 125 MHz clock.

The symbol rate of 125 Mbaud is the one 100BASE-TX had already shown to work
over Category 5 cable. Together with the transmit shaping, it keeps the
transmitted spectrum below about 80 MHz, inside the 100 MHz for which the
cable is specified. Half the symbol rate, 62.5 MHz, is the highest frequency
needed to tell one symbol from the next.

Five-level signalling (PAM-5)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two bits per symbol need at least four distinct voltage levels. 1000BASE-T
uses five, written -2, -1, 0, +1 and +2. This is called *five-level pulse
amplitude modulation*, or PAM-5. The extra level gives room for an
error-correcting code and for control symbols, as explained in
`The trellis code`_.

A group of four symbols, one on each pair in the same symbol period, can
take :math:`5^4 = 625` different values. Only :math:`2^9 = 512` are needed
to carry the 8 data bits plus the one extra code bit; the remaining
combinations are used for idle and control patterns.

.. wavedrom::

   { "signal": [
       { "name": "byte from RGMII", "wave": "======", "data": ["0x3A", "0x7F", "0x00", "0xC5", "0x18", "0xE2"] },
       { "name": "pair A", "wave": "======", "data": ["+1", "-2", "0", "+2", "-1", "+1"] },
       { "name": "pair B", "wave": "======", "data": ["-1", "0", "+2", "-1", "+1", "-2"] },
       { "name": "pair C", "wave": "======", "data": ["+2", "+1", "-1", "0", "-2", "0"] },
       { "name": "pair D", "wave": "======", "data": ["0", "-1", "+1", "+2", "0", "-1"] }
     ],
     "head": { "text": "One byte per 8 ns symbol period, spread over four pairs (illustrative values)" },
     "config": { "hscale": 2 }
   }

Five levels instead of three (as used by 100BASE-TX) for the same peak
voltage halve the spacing between adjacent levels. Halving the spacing
halves the noise voltage that can be tolerated before a level is mistaken
for its neighbour, which costs 6 dB of signal-to-noise ratio
(:math:`20\log_{10} 2 \approx 6` dB). The error-correcting code recovers
about that much.

Amplitudes. In the standard's transmitter test pattern, the peak
differential output must be between 0.67 V and 0.82 V into a 100 Ω load.
The TI DP83867 datasheet gives 0.745 V as typical. The 802.3ab tutorial
describes a transmit shaping filter that combines each symbol with the
previous one, :math:`0.75\,a_n + 0.25\,a_{n-1}`, which reduces the energy
at high frequencies. With five input levels this gives 17 possible output
levels (the multiples of 0.25 from -2 to +2), driven by a 17-level DAC. The
DP83867 datasheet likewise describes its output as 17-level
partial-response-shaped PAM-5.

Scrambling
~~~~~~~~~~

Before coding, the data is combined (bitwise exclusive-OR) with the output
of a *scrambler*: a 33-bit linear feedback shift register, which is a shift
register whose input is the exclusive-OR of two of its own taps, and which
produces a long sequence that looks random. Scrambling has two purposes:

* The transmitted symbols look random whatever the data is, so the
  transmitted power is spread over the band instead of piling up at a few
  frequencies, which keeps radiated interference low.
* The symbols are uncorrelated over time, between the four pairs, and
  between the two directions on each pair. The two ends use different
  scrambler polynomials for this: the *master* uses
  :math:`1 + x^{13} + x^{33}` and the *slave* uses
  :math:`1 + x^{20} + x^{33}` (see `Master and slave clocking`_). The
  adaptive cancellers rely on this: they must learn the coupling from the
  transceiver's own symbols while the far end's symbols are present at the
  same time, which works when the two are unrelated.

The scrambler runs continuously, also during idle periods, so the receiver
can lock its own copy of the sequence to the incoming idle stream before
data arrives.

The trellis code
~~~~~~~~~~~~~~~~

A *trellis code* is an error-correcting code in which a small state machine
in the transmitter (here a convolutional encoder with 8 states) adds one
redundant bit to each 8-bit group, and the choice of which symbols are
allowed depends on that state. Only certain sequences of four-pair symbol
groups are then legal. In 1000BASE-T the five levels are split into two
subsets, {-1, +1} and {-2, 0, +2}, and the encoder state decides which
subsets may follow which. The minimum distance between two legal *sequences*
is larger than the distance between two adjacent levels, and this is where
the coding gain of about 6 dB comes from.

The receiver decodes the code with a *Viterbi decoder*: rather than deciding
each symbol on its own, it keeps track of the most likely path through all
the possible encoder states over the last several symbol periods and picks
the legal sequence closest to what was received. The decoder and the
equalizer's feedback loop have to complete their work in one 8 ns symbol
period, which made this the critical timing path in the original designs.

Idle periods use only the three levels -1, 0 and +1. This makes it easier
for a receiver to lock on and train its filters before it can decode the
full five-level signal. The start and end of each frame are marked by
special symbol groups (delimiters) chosen to be easy to recognise.

Sending and receiving on the same pair at once
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each pair carries 250 Mbit/s in each direction at the same time. The voltage
at the transceiver's own pins is the sum of what it is transmitting and what
is arriving from the far end:

.. math::

   v_\text{pins}(t) = v_\text{own}(t) + v_\text{far}(t) + \text{(reflections and crosstalk)}

The transceiver's own signal is at full size, while the far-end signal has
lost up to 24 dB in the cable. Two stages remove the own signal:

1. The **hybrid** is an analog bridge circuit. It drives a replica of the
   transmitted signal into a reference network matched to the line
   impedance, and the receiver takes the difference between the line side
   and the reference side. If the cable were a perfect 100 Ω, the own
   signal would cancel completely. In practice the cable and connectors are
   not perfect, and part of the own signal remains.
2. The **echo canceller** removes what the hybrid misses, including the
   reflections from connectors along the cable. It is an adaptive
   finite-impulse-response (FIR) filter: its input is the sequence of
   symbols the transceiver has just sent, its output is a prediction of the
   echo that those symbols cause at the ADC output, and this prediction is
   subtracted from the received samples. The filter coefficients are
   continuously adjusted to minimise the remaining error (usually with the
   least-mean-squares method). Reflections from far along the cable return
   long after the symbol that caused them, so the filter is long: the
   designs in the 802.3ab tutorial used 60 to 120 taps at 125 MHz.

.. _fig-phy-impairments:

.. graphviz:: phy-electrical/cable-impairments.dot
   :caption: Signals arriving at the receiver of pair A. The cancellers
             remove the echo and near-end crosstalk, whose source is known.
             The equalizer removes the cable's smearing of the wanted
             signal.
   :align: center

Crosstalk cancellation
~~~~~~~~~~~~~~~~~~~~~~

Near-end crosstalk is cancelled in the same way as echo: the transceiver
knows exactly what it is transmitting on the other three pairs, so for
every receiver it runs three more adaptive FIR filters that predict and
subtract the leakage from each of them. A complete receiver therefore has
five adaptive filters (one equalizer, one echo canceller, three near-end
crosstalk cancellers), and the transceiver as a whole has twenty.

Far-end crosstalk comes from symbols the receiving transceiver did not send.
It is weaker than near-end crosstalk because it has crossed the whole cable.
To keep it small enough, 1000BASE-T added a far-end crosstalk limit to the
cable requirements; the example design in the 802.3ab tutorial still had
5.7 dB of margin with worst-case far-end crosstalk and no far-end
crosstalk canceller. Adaptive filters can also be used to cancel it.

Equalization
~~~~~~~~~~~~

The *equalizer* is a filter whose frequency response is the inverse of the
cable's, so that the combination of cable and equalizer has a flat response
and each received symbol no longer overlaps its neighbours. Because the loss
depends on the cable length and type, the equalizer must adapt to each
cable, and it continues to adapt while the link runs, to follow changes such
as temperature.

Gigabit receivers combine two parts:

* a *feed-forward equalizer*, an FIR filter on the incoming samples, which
  removes the part of the overlap that reaches ahead of each symbol;
* a *decision-feedback equalizer*, an FIR filter fed with the symbols the
  receiver has already decided, which subtracts their lingering tails.
  Because its input is the clean decided symbols rather than the noisy
  samples, it removes overlap without adding noise.

The receive path also corrects *baseline wander*: the transformers block
DC, so a long run of symbols whose average is not zero shifts the zero level of
the received signal. A small feedback loop restores it.

Master and slave clocking
~~~~~~~~~~~~~~~~~~~~~~~~~

The echo and crosstalk cancellers are driven by the transceiver's own
transmit symbols, while the ADC samples the received signal at the far
end's symbol timing. For the cancellers to stay matched to the received
samples, the transmit and receive symbol clocks must have exactly the same
frequency. 1000BASE-T achieves this by making one end the timing reference:

* The **master** transmits using its own crystal-derived 125 MHz clock.
* The **slave** recovers the master's clock from the received signal with
  its clock-recovery loop, and uses that recovered clock for its own
  transmitter.

The whole link therefore runs on the master's crystal. The Microchip
KSZ9031 datasheet notes that without this, master and slave would drift
apart, and that it also helps echo and near-end crosstalk cancellation.
Each end's local
clock must be within :math:`\pm 0.01\,\%` (100 parts per million) of
125 MHz. Which end is master is decided during autonegotiation. Some
datasheets, such as TI's, use the words *leader* and *follower* for the same
roles.

Delay between pairs and pair swaps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The four pairs in a cable have slightly different lengths and propagation
speeds, so symbols sent at the same moment arrive up to a few tens of
nanoseconds apart; the Microchip KSZ9031 datasheet states that it corrects
up to 50 ns of difference. The receiver also detects and corrects swapped
pairs and reversed wires within a pair, using the idle patterns sent before
data starts.

Why this needs so much signal processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every 8 ns, for each of four pairs, the receiver must update and evaluate
five adaptive filters, run a Viterbi decoder step and update a
decision-feedback loop. The example design point in the 1998 IEEE 802.3ab
tutorial used an ADC with 6.5 bits of ideal resolution at 125 million
samples per second per pair (the same tutorial elsewhere gives 7 bits),
and per pair a 120-tap echo canceller, 72 taps of near-end crosstalk
cancellation, a 16-tap feed-forward equalizer and a 12-tap
decision-feedback equalizer, all at 125 MHz. Across four pairs that is of
the order of a thousand filter taps, each doing one multiply-and-add every
8 ns, or roughly :math:`10^{11}` multiply-and-add operations per second.
The tutorial estimated about 330,000 gates and 4 W for this design point;
its layout study put the DSP at about 400,000 gates and 3.1 W in 0.25 µm
CMOS at 2.5 V. Present-day 10/100/1000 transceivers made in finer
processes use around 0.5 W in total at 1000 Mbit/s (see `Power`_).

100BASE-TX
----------

100BASE-TX uses two of the four pairs: one pair for each direction, so it
needs no hybrid or echo canceller. On an RJ45 socket these are the pairs on
pins 1 and 2 and on pins 3 and 6.

Coding steps on the transmit side:

1. **4B5B coding.** Each 4-bit group of data is replaced by a 5-bit code
   word chosen from a fixed table. The 16 data code words all contain at
   least two 1 bits, which become transitions on the line, and some of the
   other 16 code words mark the start and end of a frame and the idle
   state. This raises the bit rate to

   .. math::

      100\ \tfrac{\text{Mbit}}{\text{s}} \times \tfrac{5}{4}
      = 125\ \text{Mbaud}

2. **Scrambling.** The 5-bit stream is combined with the output of an
   11-bit linear feedback shift register (polynomial
   :math:`1 + x^9 + x^{11}`, which repeats every 2047 bits). This spreads
   the transmitted power over the band. Without it, repetitive patterns such
   as the continuous idle code would concentrate the energy at a few
   frequencies and exceed radiated emission limits.

3. **MLT-3 line coding.** *MLT-3* (multi-level transmit, three levels) uses
   the levels -1, 0 and +1. A 1 bit moves the output one step along the
   repeating cycle 0, +1, 0, -1, 0, ...; a 0 bit leaves the output where it
   is. Because four 1 bits are needed for one full cycle, the highest
   fundamental frequency of the signal is a quarter of the bit rate,
   :math:`125/4 = 31.25` MHz, which is low enough to pass through Category 5
   cable with modest loss.

.. wavedrom::

   { "signal": [
       { "name": "bit", "wave": "==========", "data": ["1","1","1","1","0","1","1","0","0","1"] },
       { "name": "MLT-3", "wave": "1z0z.1z..0" }
     ],
     "head": { "text": "MLT-3: each 1 bit steps through 0, +1, 0, -1; each 0 bit holds the level" },
     "foot": { "text": "Upper line +1 V, middle line 0 V, lower line -1 V (nominal)" },
     "config": { "hscale": 2 }
   }

Amplitudes. The peak differential output is 0.95 V to 1.05 V (nominally
±1 V) into 100 Ω, with rise and fall times between 3 ns and 5 ns. The
transmit clock must be within 125 MHz ± 6.25 kHz (±50 parts per million).

The receiver has an adaptive equalizer for the cable loss, a baseline
wander correction loop, a clock-recovery loop that locks to the transitions
of the received signal, and then reverses the coding steps: MLT-3 to bits,
descrambling and 5B-to-4B decoding. The descrambler locks to the incoming
stream by recognising the scrambled idle pattern.

10BASE-T
--------

10BASE-T also uses one pair in each direction, on the same pins as
100BASE-TX. It sends the data bits directly at 10 Mbit/s using *Manchester
coding*: each bit period is split in two halves with opposite levels, so
there is always a transition in the middle of the bit. A 1 bit is a
transition from low to high in the middle of the bit, and a 0 bit is a
transition from high to low. The receiver recovers the clock from these
mid-bit transitions. The price is that the signal changes at up to twice the
bit rate, so the fundamental frequency is between 5 MHz and 10 MHz.

.. wavedrom::

   { "signal": [
       { "name": "bit", "wave": "=======", "data": ["1","0","1","1","0","0","1"], "period": 2 },
       { "name": "Manchester", "wave": "01.0.101.010.1" }
     ],
     "head": { "text": "Manchester coding, 100 ns per bit" },
     "config": { "hscale": 1 }
   }

Amplitudes. The peak differential output is 2.2 V to 2.8 V into 100 Ω.
A lower-power variant called 10BASE-Te, defined by the Energy Efficient
Ethernet amendment (IEEE 802.3az), uses 1.54 V to 1.96 V and works with
ordinary 10BASE-T receivers. The
receiver ignores signals below a threshold (about 300 mV in the Microchip
KSZ9031), so that noise on an idle line is not mistaken for data.

Between frames the line is silent at 0 V, except for a single short
*link pulse* (about 100 ns wide) every 16 ms ± 8 ms. These *normal link
pulses* tell the far end that the cable is connected and the transmitter is
working. A receiver that sees no link pulses or data for 50 ms to 150 ms
declares the link down.

Comparison of the three speeds
------------------------------

.. list-table:: 10BASE-T, 100BASE-TX and 1000BASE-T compared
   :header-rows: 1
   :widths: 28 24 24 24

   * -
     - 10BASE-T
     - 100BASE-TX
     - 1000BASE-T
   * - IEEE 802.3 clause
     - 14
     - 24, 25
     - 40
   * - Pairs used
     - 2 (one per direction)
     - 2 (one per direction)
     - 4 (all in both directions)
   * - Coding
     - Manchester
     - 4B5B, scrambling
     - scrambling, 8-state trellis code
   * - Levels on the line
     - 2
     - 3 (MLT-3)
     - 5 (PAM-5)
   * - Symbol rate per pair
     - 20 M half-bit periods per second
     - 125 Mbaud
     - 125 Mbaud
   * - Highest fundamental frequency
     - 10 MHz
     - 31.25 MHz
     - 62.5 MHz (spectrum kept below about 80 MHz)
   * - Peak differential output
     - 2.2 V to 2.8 V
     - 0.95 V to 1.05 V
     - 0.67 V to 0.82 V (test pattern)
   * - Hybrid and echo cancelling
     - no
     - no
     - yes
   * - Crosstalk cancelling
     - no
     - no
     - yes (near-end)
   * - Clock
     - each end uses its own
     - each end uses its own
     - master and slave
   * - Typical power, Microchip KSZ9031 (whole chip, from link up and idle
       to full traffic, over its supply options)
     - 44 mW to 149 mW
     - 154 mW to 228 mW
     - 419 mW to 621 mW

Autonegotiation
---------------

Before data can flow, the two transceivers must agree on speed, on whether
both directions may transmit at once (*full duplex*, the normal case today)
or only one at a time (*half duplex*, a mode kept for old shared-cable
networks), and, for 1000BASE-T, on which end is master. They do this with
autonegotiation (IEEE 802.3 Clause 28), using pulses of the same shape as
the 10BASE-T link pulses described above.

Fast link pulse bursts
~~~~~~~~~~~~~~~~~~~~~~

A transceiver that supports autonegotiation replaces each single 10BASE-T
link pulse with a *fast link pulse burst*. A burst lasts about 2 ms and
contains 17 *clock pulses* spaced 125 µs ± 14 µs apart. Halfway between
each pair of clock pulses (62.5 µs ± 7 µs after the first) there is either
a *data pulse*, meaning 1, or no pulse, meaning 0. A burst therefore holds
16 data bits and contains between 17 and 33 pulses. Bursts are repeated
every 16 ms ± 8 ms, the same spacing as normal link pulses.

.. wavedrom::

   { "signal": [
       { "name": "line", "wave": "hl..hl..hl..hl..hl..l...hl..hl..hl.." },
       { "name": "pulse", "wave": "=========", "data": ["clock","data: 1","clock","data: 1","clock","data: 0","clock","data: 1","clock"], "period": 4 }
     ],
     "head": { "text": "Start of a fast link pulse burst (not to scale: pulses are about 100 ns wide, 62.5 µs apart)" },
     "config": { "hscale": 1 }
   }

The 16 bits are called a *page*. The first page, the *base page*, contains:

* a 5-bit selector, set to say "this is IEEE 802.3 Ethernet";
* 8 ability bits: whether 10BASE-T and 100BASE-TX are supported, each in
  half and full duplex, a less common 100 Mbit/s mode, and whether
  flow-control ("pause") frames can be handled;
* a remote fault bit, an acknowledge bit, and a *next page* bit that says
  more pages follow.

Each side repeats its page until it has received the other side's page
several times without change, then sets the acknowledge bit to confirm.

1000BASE-T abilities do not fit in the base page and are sent in *next
pages*: one message page followed by two unformatted pages. They carry:

* whether 1000BASE-T is supported in half and in full duplex;
* whether the device is a single-port device (such as a computer's network
  interface) or a multi-port device (such as a switch);
* whether master or slave has been forced by configuration;
* an 11-bit random number, the *seed*.

Choosing the result
~~~~~~~~~~~~~~~~~~~

Each side compares its own abilities with its partner's and picks the best
mode that both support, in this order: 1000BASE-T full duplex, 1000BASE-T
half duplex, 100BASE-TX full duplex, 100BASE-TX half duplex, 10BASE-T full
duplex, 10BASE-T half duplex. Both sides reach the same answer because they
apply the same rules to the same information.

For 1000BASE-T, master and slave are chosen in this order:

1. A device configured to be master becomes master, and one configured to
   be slave becomes slave. If both are forced to the same role, the link
   fails with a configuration fault.
2. Otherwise, a multi-port device becomes master over a single-port device.
   A switch is therefore usually the clock master for the devices plugged
   into it.
3. Otherwise, the device that sent the larger random seed becomes master. If
   the seeds are equal, the resolution fails with a configuration fault.

If the partner sends normal 10BASE-T link pulses or 100BASE-TX idle signals
instead of fast link pulse bursts, the transceiver recognises the speed from
the signal itself and uses it. This is called *parallel detection*.

Link-up time
~~~~~~~~~~~~

Once the result is chosen, the selected receiver must report a working link
within 750 ms to 1000 ms, otherwise the transceiver stops transmitting for
1200 ms to 1500 ms and starts negotiating again. For 1000BASE-T, the
start-up, in which the slave locks to the master's clock and
both ends train their equalizers and cancellers on idle symbols, must
happen within this period. The TI
DP83867 datasheet gives 2 to 3 seconds as the typical time for
autonegotiation to complete.

Line driver types and the transformer centre tap
------------------------------------------------

Each pair is connected to the cable through a transformer, with the
transceiver side of each transformer winding brought out at its midpoint,
the *centre tap* (see :doc:`magnetics`). How the centre tap must be
connected depends on how the transceiver's line driver is built.

Current-mode driver
   The output stage switches controlled currents into one wire or the other
   of the pair, like a current-steering DAC, with termination resistors from
   each wire to the supply. The output transistors only sink current, so
   their current must be supplied through the transformer winding. The
   centre tap is therefore connected to the transceiver's analog supply (and
   decoupled to ground with a capacitor), which provides both the current
   and the DC bias of the output pins. Examples: TI DP83848 and DP83822
   (10/100 transceivers), whose datasheets require the centre tap to be
   tied to the analog supply rail.

Voltage-mode driver
   The output stage drives a voltage onto each wire through an on-chip
   source impedance that also serves as the line termination, like a
   low-impedance amplifier output. It sets its own common-mode voltage and
   needs no current through the centre tap. The centre taps must then not be
   connected to any supply. Each one is connected to ground only through its
   own capacitor (0.1 µF is the recommended value in both datasheets cited
   here). The four centre taps must be kept separate from each other because
   the drivers may hold different pairs at different common-mode voltages,
   depending on the speed in use. Examples: Microchip KSZ9031 (which its
   datasheet describes as using voltage-mode drivers) and TI DP83867 (whose
   datasheet requires the same separate, capacitor-only centre-tap
   connection).

The two connections are not interchangeable, so the board design must follow
the datasheet of the transceiver actually used.

Power
-----

The Microchip KSZ9031 datasheet gives the whole chip's power, at
1000 Mbit/s with full traffic, as between 452 mW and 621 mW depending on
how its supplies are generated, and at 100 Mbit/s as between 156 mW and
228 mW. The TI DP83867 datasheet gives 457 mW to 530 mW for 1000BASE-T,
depending on package and supply arrangement.

Why evampire uses an external transceiver
-----------------------------------------

evampire connects to a commercial transceiver over RGMII instead of
integrating a 1000BASE-T transceiver on the gf180mcu die. The reasons follow
from the requirements above:

Analog front end
   Each of the four pairs needs a linear line driver, a hybrid, a
   variable-gain amplifier and filter, a 125 million samples per second DAC
   with 17 output levels, and an ADC of about 7 bits at 125 million samples
   per second, all meeting tight linearity and noise targets. The standard
   limits the transmit clock jitter to 1.4 ns peak-to-peak. Each of these
   is a substantial analog design and verification effort on its own.

Digital signal processing
   Twenty adaptive filters, four Viterbi decoders and four decision-feedback
   loops running at 125 MHz, with a one-symbol-period critical path,
   amount to several hundred thousand gates. In the 1998 estimates above
   this cost 3 W to 4 W in 0.25 µm CMOS. gf180mcu is a 0.18 µm process with
   3.3 V and 5 V devices, aimed at microcontroller designs. By comparison,
   evampire's forwarding path handles one byte per clock cycle with a few
   bytes of buffering (see :doc:`../architecture/index`).

Standards compliance
   A transceiver must pass the IEEE 802.3 transmitter and receiver
   conformance tests (output levels, distortion, jitter, return loss) and
   electromagnetic emission limits. Commercial transceivers are designed
   and characterised against these tests.

Interchangeability
   RGMII is supported by many transceivers from several manufacturers, so
   the board can use any of them, and the same digital design in evampire
   works with each.

The external transceiver also handles autonegotiation, 10 and 100 Mbit/s
signalling and cable diagnostics, leaving evampire to deal only with bytes,
frame boundaries and the management registers.

References
----------

IEEE standards
   * IEEE Std 802.3, *IEEE Standard for Ethernet*. Clause 14 (10BASE-T),
     Clause 22 (media independent interface and management registers),
     Clauses 24 and 25 (100BASE-TX), Clause 28 (autonegotiation on twisted
     pair), Clause 40 (1000BASE-T). Available at no cost through the IEEE
     GET program: https://ieeexplore.ieee.org/browse/standards/get-program/page/series?id=68
   * ANSI X3.263-1995, *Fibre Distributed Data Interface (FDDI) - Token Ring
     Twisted Pair Physical Layer Medium Dependent (TP-PMD)*, the basis of the
     100BASE-TX electrical signalling
     referenced by IEEE 802.3 Clause 25.

IEEE 802.3 working group material
   * C. Mick, C. DiMinico, S. Raghavan, S. Rao, M. Hatamian, *802.3ab
     (1000BASE-T) Tutorial*, IEEE 802.3 plenary, March 1998:
     https://www.ieee802.org/3/tutorial/march98/mick_170398.pdf. Source of
     the channel limit formulas, the 125 Mbaud PAM-5 design, the 0.75/0.25
     partial-response shaping, the trellis subsets, the 6 dB figures, the
     design point (ADC resolution, filter lengths, gate count and power) and
     the 0.25 µm layout estimate.
   * C. T. Di Minico, P. Kish, *Development of Equal Level Far-End
     Crosstalk (ELFEXT) and Return Loss Specifications for Gigabit Ethernet
     Operation on Category 5 Copper Cabling*:
     https://www.ieee802.org/3/an/public/material/diminico_IWCS.PDF.
     Source of the 250 Mbit/s per pair, the transmit spectrum below 80 MHz,
     and the description of echo and crosstalk cancellation.

Conformance test documents (University of New Hampshire InterOperability Laboratory)
   * A. Healey, *1000BASE-T Technology Overview, Part 1: Design Challenges*,
     1998: https://www.iol.unh.edu/sites/default/files/knowledgebase/ge/1000tcable.pdf.
     Source of the cable impairments, the 100 m channel, the 10\ :sup:`-10`
     error rate target, the resistive hybrid and the count of five adaptive
     filters per receiver.
   * *Clause 40 1000BASE-T PMA Test Suite*, v2.5:
     https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/CL40_PMA/PMA_Test_Suite_v2.5.pdf.
     Source of the 0.67 V to 0.82 V transmitter peak, the 1.4 ns transmit
     clock jitter limit and the
     125.00 MHz ± 0.01 % clock.
   * *Clause 25 100BASE-TX PMD Test Suite*, v3.4:
     https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/CL25_PMD/PMD_Test_Suite_v3.4.pdf.
     Source of the 0.95 V to 1.05 V output and the 125 MHz ± 6.25 kHz clock.
   * *Clause 14 10BASE-T MAU Test Suite*, v5.2:
     https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/CL14_MAU/MAU_Test_Suite_v5.2.pdf.
     Source of the 2.2 V to 2.8 V and 1.54 V to 1.96 V outputs, the link
     pulse spacing of 16 ms ± 8 ms and the 50 ms to 150 ms link loss time.
   * *10BASE-T MAU* overview:
     https://www.iol.unh.edu/sites/default/files/knowledgebase/ethernet/10basetmau.pdf.
     Source of the Manchester bit convention.
   * *Clause 28 Auto-Negotiation State Machine Base Page Exchange Test
     Suite*, v6.4:
     https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/State_Machine_Suite/IEEE802.3_CL28_BPE_TestPlan_rev6.4.pdf.
     Source of the fast link pulse timing, the base page fields and the
     autonegotiation timers.
   * *Clause 28 Management System Test Suite*, v3.0:
     https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/Management_System_Suite/Management_System_Test_Suite_v3.0.pdf.
     Source of the 1000BASE-T next pages, the 11-bit seed and the
     master/slave resolution rules.

Transceiver datasheets and application notes
   * Texas Instruments, *DP83867IR/CR Robust, High Immunity 10/100/1000
     Ethernet Physical Layer Transceiver*, SNLS484:
     https://www.ti.com/lit/ds/symlink/dp83867ir.pdf. Block diagram,
     25 MHz crystal, output amplitudes, centre-tap connection,
     autonegotiation time and power.
   * Microchip, *KSZ9031RNX Gigabit Ethernet Transceiver with RGMII
     Support*, DS00002117:
     https://ww1.microchip.com/downloads/en/DeviceDoc/00002117F.pdf.
     1000BASE-T and 100BASE-TX block descriptions, voltage-mode drivers,
     master/slave timing recovery, pair skew, speed priority, fast link
     pulse timing and power.
   * Texas Instruments, *DP83848 PHYTER Industrial Temperature Single Port
     10/100 Mb/s Ethernet Physical Layer Transceiver*, SNLS266:
     https://www.ti.com/lit/ds/symlink/dp83848c.pdf. 4B5B code table,
     scrambler, MLT-3 conversion, current-mode output and centre tap to
     supply.
   * Texas Instruments, *DP83822 Robust, Low Power 10/100 Mbps Ethernet
     Physical Layer Transceiver*:
     https://www.ti.com/lit/ds/symlink/dp83822i.pdf. Current-mode line
     driver and centre-tap connection.
   * Texas Instruments, *How to Pass IEEE Ethernet Compliance Tests*,
     SNLA385: https://www.ti.com/lit/an/snla385/snla385.pdf. List of the
     1000BASE-T transmitter tests and their IEEE 802.3 subclauses.
   * Intel, *PCI/PCI-X Family of Gigabit Ethernet Controllers Software
     Developer's Manual*, section 11.11.3.7, as reproduced at
     https://auto.manualsonline.com/manuals/mfg/intel/pci.html?p=212.
     Master and slave scrambler polynomials.
   * R. Cam, *Scrambling and 4LZS with Run Substitution*, IEEE 802.3z
     presentation, November 1996:
     https://grouper.ieee.org/groups/802/3/z/public/presentations/nov1996/BHgutp_f.pdf.
     100BASE-TX scrambler polynomial and period.

Process
   * GlobalFoundries 0.18 µm 3.3 V/(5 V) 6 V MCU PDK documentation:
     https://gf180mcu-pdk.readthedocs.io/
