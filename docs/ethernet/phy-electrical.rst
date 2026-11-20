How an Ethernet transceiver works
=================================

This page explains, from an electrical point of view, how an Ethernet
transceiver turns the digital RGMII signals into the analog signals carried
on an Ethernet cable, and back again. The page
:doc:`phy-electrical/integration` then sets out what evampire needs in order
to contain the whole transceiver itself.

The transceiver sits between the chip that handles frames and the cable. On
one side it exchanges bytes with that chip; on the other side it drives and
receives small analog voltages on the twisted pairs of the cable, normally
through coupling transformers (see :doc:`magnetics`). Ethernet documentation
calls the transceiver the *PHY*, short for "physical layer device". This
page uses "transceiver".

The requirements for evampire are:

* In the first version, each Ethernet port uses an external transceiver
  chip, connected to evampire over RGMII (see :doc:`rgmii`), and the
  transceiver connects to the cable through coupling transformers.
* The full design integrates all of the transceiver functions on evampire:
  the line driver and receiver, the analog-to-digital and digital-to-analog
  converters, the signal processing that removes echo, crosstalk and cable
  loss, clock recovery, line coding and autonegotiation. The forwarding
  logic connects to the integrated transceiver through the same
  one-byte-per-clock interface it uses with RGMII. The full design also
  connects to the cable without coupling transformers (see
  :doc:`magnetics`).
* Which Ethernet speeds the integrated transceiver supports is not yet
  fixed.

.. toctree::
   :maxdepth: 1

   phy-electrical/integration

.. contents:: On this page
   :local:
   :depth: 1

The job of the transceiver
--------------------------

A typical gigabit transceiver supports three speeds, each defined by its own
part of the IEEE 802.3 Ethernet standard:

* **1000BASE-T**: 1000 Mbit/s over all four twisted pairs of the cable
  (IEEE 802.3 Clause 40 [PHY-8023]_).
* **100BASE-TX**: 100 Mbit/s over two of the pairs (Clauses 24 and 25).
* **10BASE-T**: 10 Mbit/s over two of the pairs (Clause 14).

In the names, the number is the data rate in Mbit/s, "BASE" means the
signal is sent directly as voltage levels rather than modulated onto a
carrier, and "T" means twisted-pair cable.

When a cable is plugged in, the transceivers at the two ends first exchange
a short description of what each can do, and pick the fastest speed they
both support. This is called *autonegotiation* (Clause 28). After that,
the transceiver's work is to:

* take bytes from the frame-handling logic, add enough structure that the far end can find
  its clock and the frame boundaries, and turn them into a sequence of
  voltage levels that fits through the cable;
* receive the far end's voltage levels, which arrive smaller, smeared out in
  time and mixed with interference, and turn them back into the original
  bytes;
* report its status (cable connected, speed chosen, errors) through a set of
  registers. An external transceiver makes these readable over a two-wire
  management interface; in an integrated transceiver they are ordinary
  on-chip registers.

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
bit error in every :math:`10^{10}` bits. [PHY-HEALEY]_

The cable affects the signal in four ways that drive the whole design of the
transceiver:

Insertion loss (attenuation)
   The signal gets smaller as it travels. The loss grows with frequency
   because of the skin effect: at higher frequencies the current flows in a
   thinner layer at the surface of each conductor, so the resistance rises.
   On a 100 m channel the loss reaches 24 dB at 100 MHz (calculated below).
   A pulse sent down the cable therefore arrives both smaller and spread
   out in time, so that each symbol overlaps the next few. This overlap is
   called *inter-symbol interference*.

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

How large these effects are
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The 1000BASE-T channel limits are given as formulas of frequency. They set
how small the wanted signal can become and how large the interference can
be, and so how much the receiver has to correct. The formulas below are the
limits quoted in the IEEE 802.3ab tutorial [PHY-TUT98]_; all losses are
in decibels (dB), where a loss of :math:`L` dB means the voltage is
multiplied by :math:`10^{-L/20}`.

**Insertion loss.** The largest loss the cable may have at frequency
:math:`f`:

.. math::

   L_\text{IL}(f) = 2.1\,f^{0.529} + \frac{0.4}{f}

where:

* :math:`L_\text{IL}` is the insertion loss, in dB;
* :math:`f` is the frequency, in MHz (the formula applies from 1 MHz to
  100 MHz);
* 2.1, 0.529 and 0.4 are the constants of the limit line, from the
  802.3ab tutorial [PHY-TUT98]_.

Worked example at :math:`f = 62.5` MHz, half the 1000BASE-T symbol rate:

.. math::

   62.5^{0.529} = 8.90

   2.1 \times 8.90 = 18.7

   \frac{0.4}{62.5} = 0.006

so :math:`L_\text{IL}(62.5) = 18.7` dB. The fraction of the voltage that
arrives is

.. math::

   10^{-18.7/20} = 10^{-0.935} = 0.116

that is, about 12 % of the transmitted voltage reaches the far end at this
frequency.

**Near-end crosstalk loss.** How much weaker the signal coupled from one
neighbouring pair at the same end is than the signal on that pair, at
least:

.. math::

   L_\text{NEXT}(f) = 27.1 - 16.8\,\log_{10}\!\left(\frac{f}{100}\right)

where :math:`L_\text{NEXT}` is in dB and :math:`f` in MHz as before; 27.1
and 16.8 are the constants of the limit line. At :math:`f = 62.5` MHz:
:math:`\log_{10}(0.625) = -0.204`, :math:`16.8 \times (-0.204) = -3.43`, so
:math:`L_\text{NEXT} = 27.1 + 3.43 = 30.5` dB.

**Far-end crosstalk.** How much weaker the signal coupled from one pair at
the far end is than the wanted signal that has crossed the same cable, at
least (this is called *equal-level* far-end crosstalk, because it is
measured against the already attenuated wanted signal):

.. math::

   L_\text{FEXT}(f) = 17 - 20\,\log_{10}\!\left(\frac{f}{100}\right)

At :math:`f = 62.5` MHz: :math:`20 \times (-0.204) = -4.08`, so
:math:`L_\text{FEXT} = 17 + 4.08 = 21.1` dB.

The same three calculations at other frequencies give:

.. list-table:: 1000BASE-T channel limits on a 100 m Category 5 channel
   (calculated from the formulas above)
   :header-rows: 1
   :widths: 16 22 22 22 18

   * - :math:`f`
     - :math:`L_\text{IL}` (at most)
     - Voltage that arrives, :math:`10^{-L_\text{IL}/20}`
     - :math:`L_\text{NEXT}` (at least)
     - :math:`L_\text{FEXT}` (at least)
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

**What this means.** Both the wanted signal and the near-end crosstalk start
from transmitters of the same size. The wanted signal is reduced by the
insertion loss; the crosstalk by the near-end crosstalk loss. The margin by
which the wanted signal exceeds the crosstalk from one neighbouring pair is
therefore

.. math::

   M(f) = L_\text{NEXT}(f) - L_\text{IL}(f)

At 62.5 MHz, :math:`M = 30.5 - 18.7 = 11.8` dB; at 100 MHz,
:math:`M = 27.1 - 24.0 = 3.1` dB. Near-end crosstalk from just one
neighbour is therefore within about 3 dB to 12 dB of the wanted signal in
the upper half of the band. There are three neighbouring pairs, and the
transceiver's own transmission on the same pair (the echo) is larger
still, so the receiver cannot work unless it removes these signals, using
the cancellation techniques described below.

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
   Receives one byte every 8 ns from the frame-handling chip (4 bits on
   each edge of a 125 MHz clock), and sends received bytes back the same
   way. In an integrated transceiver this is replaced by a plain on-chip
   interface of one byte per clock cycle.

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
   such as the TI DP83867 [PHY-DP83867]_ and Microchip KSZ9031
   [PHY-KSZ9031]_ both use a 25 MHz crystal,
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
the same time. The data rate in one direction is the number of pairs times
the symbol rate on each pair times the number of data bits each symbol
carries:

.. math::

   R = N_\text{pairs} \times f_\text{sym} \times b_\text{sym}

where:

* :math:`R` is the data rate in one direction, in bit/s;
* :math:`N_\text{pairs} = 4`, the number of pairs in the cable;
* :math:`f_\text{sym} = 125 \times 10^{6}` symbols per second, the symbol
  rate on each pair (IEEE 802.3 Clause 40);
* :math:`b_\text{sym} = 2`, the data bits carried by one symbol.

Substituting:

.. math::

   R = 4 \times 125 \times 10^{6} \times 2 = 1000 \times 10^{6}\ \text{bit/s}

One symbol period lasts :math:`1 / (125 \times 10^{6}) = 8` ns, and in that
time the four pairs together carry :math:`4 \times 2 = 8` bits, exactly one
byte, in each direction. This is the same byte rate as the RGMII interface,
which carries one byte per 8 ns cycle of its 125 MHz clock, so no buffering
is needed between the two rates.

The symbol rate of 125 Mbaud is the one 100BASE-TX had already shown to work
over Category 5 cable. Together with the transmit shaping, it keeps the
transmitted spectrum below about 80 MHz, [PHY-DIMINICO]_ inside the 100 MHz for which the
cable is specified. Half the symbol rate, 62.5 MHz, is the highest frequency
needed to tell one symbol from the next.

Five-level signalling (PAM-5)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two bits per symbol need at least four distinct voltage levels. 1000BASE-T
uses five, written -2, -1, 0, +1 and +2. This is called *five-level pulse
amplitude modulation*, or PAM-5. The extra level gives room for an
error-correcting code and for control symbols, as explained in
`The trellis code`_.

Counting the combinations shows why five levels are enough. A group of four
symbols, one on each pair in the same symbol period, can take
:math:`5 \times 5 \times 5 \times 5 = 5^4 = 625` different values. Each
group must carry the 8 data bits plus one extra bit added by the
error-correcting code, which needs :math:`2^{9} = 512` different values.
Because :math:`625 > 512`, every data value has a code, and the
:math:`625 - 512 = 113` spare combinations are available for idle and
control patterns.

.. wavedrom::
   :caption: 1000BASE-T carries one byte per 8 ns symbol period, as one
             five-level symbol on each of the four pairs. The symbol values
             shown are illustrative, not the real code.
   :name: fig-phy-pam5
   :alt: Timing diagram: a row of bytes from the byte interface, one per
         symbol period, above four rows labelled pair A to pair D, each
         carrying one symbol from -2 to +2 in every period.

   { "signal": [
       { "name": "byte", "wave": "======", "data": ["0x3A", "0x7F", "0x00", "0xC5", "0x18", "0xE2"] },
       { "name": "pair A", "wave": "======", "data": ["+1", "-2", "0", "+2", "-1", "+1"] },
       { "name": "pair B", "wave": "======", "data": ["-1", "0", "+2", "-1", "+1", "-2"] },
       { "name": "pair C", "wave": "======", "data": ["+2", "+1", "-1", "0", "-2", "0"] },
       { "name": "pair D", "wave": "======", "data": ["0", "-1", "+1", "+2", "0", "-1"] }
     ],
     "config": { "hscale": 1.5 }
   }

Using five levels has a cost in noise tolerance. For the same peak voltage
:math:`V_\text{pk}`, three levels (-1, 0, +1, as used by 100BASE-TX) are
:math:`V_\text{pk}` apart, while five levels (-2 to +2) are
:math:`V_\text{pk}/2` apart. A receiver mistakes a level for its neighbour
when noise exceeds half the spacing, so with five levels it tolerates only
half the noise voltage. Expressed in decibels, a voltage ratio of 2 is

.. math::

   20 \log_{10} 2 = 20 \times 0.301 = 6.0\ \text{dB}

so PAM-5 needs about 6 dB more signal-to-noise ratio than three-level
signalling for the same error rate. The 802.3ab tutorial [PHY-TUT98]_
gives the same
6 dB figure, and the error-correcting code described below was chosen to
win back about that much.

Amplitudes. In the standard's transmitter test pattern, the peak
differential output must be between 0.67 V and 0.82 V into a 100 Ω load. [PHY-UNH40]_
The TI DP83867 datasheet gives 0.745 V as typical. [PHY-DP83867]_ The 802.3ab tutorial
describes a transmit shaping filter that mixes each symbol with the
previous one, which reduces the energy at high frequencies:

.. math::

   y_n = 0.75\,a_n + 0.25\,a_{n-1}

where :math:`a_n` is the PAM-5 symbol sent in symbol period :math:`n`
(one of -2, -1, 0, +1, +2), :math:`a_{n-1}` is the symbol of the period
before, and :math:`y_n` is the level driven onto the line, in the same
units. Because :math:`y_n = (3a_n + a_{n-1})/4`, and
:math:`3a_n + a_{n-1}` can be any whole number from
:math:`3 \times (-2) + (-2) = -8` to :math:`3 \times 2 + 2 = 8`, the
output takes 17 different levels: the multiples of 0.25 from -2 to +2. The
digital-to-analog converter (DAC) that drives the line therefore needs at
least 17 levels, not 5. The DP83867 datasheet likewise describes its
output as 17-level shaped PAM-5. [PHY-DP83867]_

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
  :math:`1 + x^{20} + x^{33}` (see `Master and slave clocking`_). [PHY-INTEL]_ The
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

Each pair carries :math:`1000 / 4 = 250` Mbit/s in each direction at the
same time. Because both ends drive the same two wires, the voltage at the
transceiver's own pins is the sum of several signals:

.. math::

   v_\text{pins} = v_\text{own} + v_\text{far} + v_\text{refl} + v_\text{xt}

where:

* :math:`v_\text{pins}` is the differential voltage at the pins, in V;
* :math:`v_\text{own}` is the transceiver's own transmitted signal, at
  full size (below about 1 V peak);
* :math:`v_\text{far}` is the signal from the far end, the one the receiver
  wants, reduced by the cable's insertion loss (up to 24 dB, that is to
  6 % of its original voltage, at 100 MHz; see `How large these effects
  are`_);
* :math:`v_\text{refl}` is the transceiver's own signal reflected back from
  connectors and impedance changes along the cable;
* :math:`v_\text{xt}` is the crosstalk coupled from the other pairs.

The receiver must recover :math:`v_\text{far}`, which can be much smaller
than :math:`v_\text{own}`. Two stages remove :math:`v_\text{own}` and
:math:`v_\text{refl}`, together called the *echo*:

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
   designs in the 802.3ab tutorial [PHY-TUT98]_ used 60 to 120 taps at
   125 MHz.

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
Each end's local clock must be within ±0.01 % of 125 MHz [PHY-UNH40]_. As a frequency, that is
:math:`125\ \text{MHz} \times 0.0001 = 12.5\ \text{kHz}`; as a ratio, 0.01 %
is 100 parts per million. Which end is master is decided during autonegotiation. Some
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
decision-feedback equalizer, all at 125 MHz.

A *tap* is one coefficient of a digital filter; each tap does one
multiply-and-add for every sample. The arithmetic rate of these filters is
the number of taps times the rate at which they run:

.. math::

   N_\text{taps} = N_\text{pairs} \times
   (N_\text{echo} + N_\text{NEXT} + N_\text{FFE} + N_\text{DFE})

.. math::

   R_\text{MAC} = N_\text{taps} \times f_\text{sym}

where:

* :math:`N_\text{pairs} = 4`;
* :math:`N_\text{echo} = 120`, :math:`N_\text{NEXT} = 72`,
  :math:`N_\text{FFE} = 16` and :math:`N_\text{DFE} = 12` are the tap
  counts per pair of the echo canceller, the near-end crosstalk
  cancellers, the feed-forward equalizer and the decision-feedback
  equalizer in the tutorial's design point;
* :math:`f_\text{sym} = 125 \times 10^{6}` per second, the symbol rate;
* :math:`R_\text{MAC}` is the number of multiply-and-add operations per
  second.

Substituting:

.. math::

   N_\text{taps} = 4 \times (120 + 72 + 16 + 12) = 4 \times 220 = 880

.. math::

   R_\text{MAC} = 880 \times 125 \times 10^{6}
   = 1.1 \times 10^{11}\ \text{per second}

This assumes the tutorial's 72 near-end crosstalk taps are the total for
the three cancellers of a pair; if each of the three had 72 taps, the
total would be :math:`4 \times (120 + 3 \times 72 + 16 + 12) = 1456` taps
and :math:`1.8 \times 10^{11}` operations per second. Either way, the
filters need on the order of :math:`10^{11}` multiply-and-add operations
per second, plus a similar number of operations to adapt the
coefficients. The tutorial estimated about 330,000 gates and 4 W for this design point;
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
   state. Because every 4 data bits become 5 line bits, the rate on the
   line is 5/4 of the data rate:

   .. math::

      f_\text{line} = R \times \frac{5}{4}
      = 100 \times 10^{6} \times 1.25 = 125 \times 10^{6}\ \text{per second}

   where :math:`R = 100` Mbit/s is the data rate and :math:`f_\text{line}`
   is the number of line bits (here equal to symbols) per second. This is
   why 100BASE-TX runs at 125 Mbaud.

2. **Scrambling.** The 5-bit stream is combined with the output of an
   11-bit linear feedback shift register (polynomial
   :math:`1 + x^9 + x^{11}`, which repeats every 2047 bits). [PHY-CAM96]_ [PHY-KSZ9031]_ This spreads
   the transmitted power over the band. Without it, repetitive patterns such
   as the continuous idle code would concentrate the energy at a few
   frequencies and exceed radiated emission limits.

3. **MLT-3 line coding.** *MLT-3* (multi-level transmit, three levels) uses
   the levels -1, 0 and +1. A 1 bit moves the output one step along the
   repeating cycle 0, +1, 0, -1, 0, ...; a 0 bit leaves the output where it
   is. A full cycle of the waveform (0, +1, 0, -1, back to 0) needs four
   1 bits, so the fastest repeating pattern, all 1 bits, has a period of
   four bit times. Its frequency is a quarter of the line rate:
   :math:`125\ \text{MHz} / 4 = 31.25` MHz. At that frequency a 100 m
   channel loses about 13 dB (table in `How large these effects are`_),
   much less than the 24 dB at 100 MHz.

.. wavedrom::
   :caption: MLT-3 line coding. Each 1 bit moves the output one step along
             the cycle 0, +1, 0, -1; each 0 bit holds the level. The upper
             line is +1 V, the middle line 0 V and the lower line -1 V
             (nominal).
   :name: fig-phy-mlt3
   :alt: Timing diagram of the bits 1 1 1 1 0 1 1 0 0 1 and the resulting
         three-level MLT-3 waveform, which steps +1, 0, -1, 0, 0, +1, 0, 0,
         0, -1.

   { "signal": [
       { "name": "bit", "wave": "==========", "data": ["1","1","1","1","0","1","1","0","0","1"] },
       { "name": "MLT-3", "wave": "1z0z.1z..0" }
     ],
     "config": { "hscale": 1.2 }
   }

Amplitudes. The peak differential output is 0.95 V to 1.05 V (nominally
±1 V [PHY-X3263]_) into 100 Ω, with rise and fall times between 3 ns and 5 ns. [PHY-UNH25]_ The
transmit clock must be within 125 MHz ± 6.25 kHz, that is
:math:`6.25\ \text{kHz} / 125\ \text{MHz} = 50 \times 10^{-6}`, or ±50 parts
per million.

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
transition from high to low. [PHY-UNH10T]_ The receiver recovers the clock from these
mid-bit transitions. The price is that the signal changes at up to twice the
bit rate, so the fundamental frequency is between 5 MHz and 10 MHz.

.. wavedrom::
   :caption: Manchester coding as used by 10BASE-T, 100 ns per bit. A 1 bit
             goes from low to high in the middle of the bit; a 0 bit goes
             from high to low.
   :name: fig-phy-manchester
   :alt: Timing diagram of the bits 1 0 1 1 0 0 1 and the Manchester
         waveform, which has a transition in the middle of every bit.

   { "signal": [
       { "name": "bit", "wave": "=======", "data": ["1","0","1","1","0","0","1"], "period": 2 },
       { "name": "Manchester", "wave": "01.0.101.010.1" }
     ],
     "config": { "hscale": 1 }
   }

Amplitudes. The peak differential output is 2.2 V to 2.8 V into 100 Ω. [PHY-UNH14]_
A lower-power variant called 10BASE-Te, defined by the Energy Efficient
Ethernet amendment (IEEE 802.3az), uses 1.54 V to 1.96 V and works with
ordinary 10BASE-T receivers. The
receiver ignores signals below a threshold (about 300 mV in the Microchip
KSZ9031 [PHY-KSZ9031]_), so that noise on an idle line is not mistaken
for data.

Between frames the line is silent at 0 V, except for a single short
*link pulse* (about 100 ns wide) every 16 ms ± 8 ms. These *normal link
pulses* tell the far end that the cable is connected and the transmitter is
working. A receiver that sees no link pulses or data for 50 ms to 150 ms
declares the link down. [PHY-UNH14]_

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
autonegotiation (IEEE 802.3 Clause 28 [PHY-8023]_), using pulses of the same shape as
the 10BASE-T link pulses described above.

Fast link pulse bursts
~~~~~~~~~~~~~~~~~~~~~~

A transceiver that supports autonegotiation replaces each single 10BASE-T
link pulse with a *fast link pulse burst*. A burst lasts about 2 ms and
contains 17 *clock pulses* spaced 125 µs ± 14 µs apart. Halfway between
each pair of clock pulses (62.5 µs ± 7 µs after the first) there is either
a *data pulse*, meaning 1, or no pulse, meaning 0. A burst therefore holds
16 data bits and contains between 17 and 33 pulses. Bursts are repeated
every 16 ms ± 8 ms, the same spacing as normal link pulses. [PHY-UNH28]_ [PHY-KSZ9031]_

.. wavedrom::
   :caption: Start of a fast link pulse burst carrying the bits 1, 0, 1.
             Not to scale: each pulse is about 100 ns wide, and pulses are
             62.5 µs apart.
   :name: fig-phy-flp
   :alt: Timing diagram of a line with short pulses: a clock pulse, a data
         pulse, a clock pulse, a gap where the data pulse is absent, a
         clock pulse, a data pulse and a clock pulse.

   { "signal": [
       { "name": "line", "wave": "hlhlhl..hlhlhl" },
       { "name": "pulse", "wave": "=======", "data": ["clock","1","clock","0","clock","1","clock"], "period": 2 }
     ],
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
* an 11-bit random number, the *seed*. [PHY-UNH28M]_

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
autonegotiation to complete. [PHY-DP83867]_

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
   (10/100 transceivers) [PHY-DP83848]_ [PHY-DP83822]_, whose datasheets
   require the centre tap to be
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

Building the transceiver on evampire
------------------------------------

The page :doc:`phy-electrical/integration` takes each of the three speeds
in turn and lists what evampire must contain to replace the external
transceiver: the analog front-end performance, the signal processing and
its arithmetic rate, clock recovery, coding, autonegotiation and the
management registers. It then assesses how far each speed can be built in
the gf180mcu process.

References
----------

.. [PHY-8023] IEEE Std 802.3, *IEEE Standard for Ethernet*. Clause 14
   (10BASE-T), Clause 22 (media independent interface and management
   registers), Clauses 24 and 25 (100BASE-TX), Clause 28 (autonegotiation on
   twisted pair), Clause 40 (1000BASE-T). Available at no cost through the
   IEEE GET program:
   https://ieeexplore.ieee.org/browse/standards/get-program/page/series?id=68

.. [PHY-X3263] ANSI X3.263-1995, *Fibre Distributed Data Interface (FDDI) -
   Token Ring Twisted Pair Physical Layer Medium Dependent (TP-PMD)*. The
   100BASE-TX electrical signalling, referenced by IEEE 802.3 Clause 25.

.. [PHY-TUT98] C. Mick, C. DiMinico, S. Raghavan, S. Rao, M. Hatamian,
   *802.3ab (1000BASE-T) Tutorial*, IEEE 802.3 plenary, March 1998.
   https://www.ieee802.org/3/tutorial/march98/mick_170398.pdf. Channel limit
   formulas, 125 Mbaud PAM-5, the 0.75/0.25 shaping filter, the trellis
   subsets, the 6 dB figures, and the design point (ADC resolution, filter
   lengths, gate count and power).

.. [PHY-DIMINICO] C. T. Di Minico, P. Kish, *Development of Equal Level
   Far-End Crosstalk (ELFEXT) and Return Loss Specifications for Gigabit
   Ethernet Operation on Category 5 Copper Cabling*.
   https://www.ieee802.org/3/an/public/material/diminico_IWCS.PDF.
   250 Mbit/s per pair, transmit spectrum below 80 MHz, echo and crosstalk
   cancellation.

.. [PHY-HEALEY] A. Healey, *1000BASE-T Technology Overview, Part 1: Design
   Challenges*, University of New Hampshire InterOperability Laboratory,
   1998. https://www.iol.unh.edu/sites/default/files/knowledgebase/ge/1000tcable.pdf.
   Cable impairments, the 100 m channel, the error rate target, the
   resistive hybrid, five adaptive filters per receiver.

.. [PHY-UNH40] University of New Hampshire InterOperability Laboratory,
   *Clause 40 1000BASE-T PMA Test Suite*, v2.5.
   https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/CL40_PMA/PMA_Test_Suite_v2.5.pdf.
   Transmitter peak voltage, droop, distortion, jitter, common-mode output,
   return loss and clock frequency limits.

.. [PHY-UNH25] University of New Hampshire InterOperability Laboratory,
   *Clause 25 100BASE-TX PMD Test Suite*, v3.4.
   https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/CL25_PMD/PMD_Test_Suite_v3.4.pdf.
   Output voltage, symmetry, rise and fall time, overshoot, jitter and
   clock frequency limits.

.. [PHY-UNH14] University of New Hampshire InterOperability Laboratory,
   *Clause 14 10BASE-T MAU Test Suite*, v5.2.
   https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/CL14_MAU/MAU_Test_Suite_v5.2.pdf.
   Output voltage, harmonic content, impedance, receiver input range, link
   pulse timing and link loss time.

.. [PHY-UNH10T] University of New Hampshire InterOperability Laboratory,
   *10BASE-T MAU* overview.
   https://www.iol.unh.edu/sites/default/files/knowledgebase/ethernet/10basetmau.pdf.
   Manchester bit convention and link pulse shape.

.. [PHY-UNH28] University of New Hampshire InterOperability Laboratory,
   *Clause 28 Auto-Negotiation State Machine Base Page Exchange Test Suite*,
   v6.4.
   https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/State_Machine_Suite/IEEE802.3_CL28_BPE_TestPlan_rev6.4.pdf.
   Fast link pulse timing, base page fields, autonegotiation timers and
   state diagrams.

.. [PHY-UNH28M] University of New Hampshire InterOperability Laboratory,
   *Clause 28 Management System Test Suite*, v3.0.
   https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/Management_System_Suite/Management_System_Test_Suite_v3.0.pdf.
   1000BASE-T next pages, the 11-bit seed and master/slave resolution.

.. [PHY-DP83867] Texas Instruments, *DP83867IR/CR Robust, High Immunity
   10/100/1000 Ethernet Physical Layer Transceiver*, SNLS484.
   https://www.ti.com/lit/ds/symlink/dp83867ir.pdf.

.. [PHY-KSZ9031] Microchip, *KSZ9031RNX Gigabit Ethernet Transceiver with
   RGMII Support*, DS00002117.
   https://ww1.microchip.com/downloads/en/DeviceDoc/00002117F.pdf.

.. [PHY-DP83848] Texas Instruments, *DP83848 PHYTER Single Port 10/100 Mb/s
   Ethernet Physical Layer Transceiver*, SNLS266.
   https://www.ti.com/lit/ds/symlink/dp83848c.pdf.

.. [PHY-DP83822] Texas Instruments, *DP83822 Robust, Low Power 10/100 Mbps
   Ethernet Physical Layer Transceiver*.
   https://www.ti.com/lit/ds/symlink/dp83822i.pdf.

.. [PHY-INTEL] Intel, *PCI/PCI-X Family of Gigabit Ethernet Controllers
   Software Developer's Manual*, section 11.11.3.7, as reproduced at
   https://auto.manualsonline.com/manuals/mfg/intel/pci.html?p=212.
   Master and slave scrambler polynomials.

.. [PHY-CAM96] R. Cam, *Scrambling and 4LZS with Run Substitution*, IEEE
   802.3z presentation, November 1996.
   https://grouper.ieee.org/groups/802/3/z/public/presentations/nov1996/BHgutp_f.pdf.
   100BASE-TX scrambler polynomial and period.
