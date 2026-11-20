Integrating the transceiver on evampire
=======================================

The requirements (see :ref:`requirements`) make 1000BASE-T mandatory on
every port and leave 100 Mbit/s and 10 Mbit/s open; in the full design the
transceiver is integrated on evampire and the cable is connected without
coupling transformers.

This page therefore treats the integrated 1000BASE-T transceiver as the main
design. It gives its block-level specification, works through each design
problem with the candidate approaches compared, gives rough area and power
estimates on the gf180mcu process [PHY-GF180PDK]_ (made through
`wafer.space <https://wafer.space/>`__), and then lists what 100BASE-TX and
10BASE-T would add. It builds on the explanation in :doc:`../phy-electrical`.
The circuits that replace the coupling transformers are described in
:doc:`../magnetics`; where a result here depends on them, this page links
there.

Three kinds of value appear on this page, and each is labelled:

Required
   A limit from the IEEE 802.3 standard (see :doc:`/standards`), taken from
   the conformance test documents that quote it ([PHY-UNH14]_,
   [PHY-UNH25]_, [PHY-UNH40]_, [PHY-UNH28]_). Subclause numbers are given
   as those documents quote them; they come from the 2002 to 2012 editions
   of the standard and may differ slightly in the current edition.

Published
   A measured or reported result from a paper, presentation or datasheet,
   with its source. Where only the paper's abstract was available, the
   number comes from the abstract.

Estimate
   A number calculated on this page from required or published values. Each
   estimate states its assumptions. Estimates are not requirements.

The interface to the forwarding logic
-------------------------------------

The forwarding logic exchanges one byte per clock cycle with each port, plus
a "frame in progress" flag and an "error" flag in each direction (see
:ref:`RGMII interfaces <arch-rgmii>`). An integrated transceiver presents
exactly this interface, so the forwarding logic is the same in the first
version and in the full design.

At 1000 Mbit/s a byte moves every 8 ns, one per cycle of a 125 MHz clock.
In the receive direction the bytes are timed by the clock recovered from the
cable, as they are with RGMII (see :doc:`../rgmii`), and the
:ref:`rate-matching buffer <arch-rate-matching>` moves them onto
evampire's own 125 MHz clock.

The gigabit transceiver
-----------------------

Required performance
~~~~~~~~~~~~~~~~~~~~

IEEE 802.3 defines four *transmitter test modes* (:clause:`40.6.1.1.2`):
fixed patterns that a 1000BASE-T transmitter sends on command so that its
output can be measured with no receiver involved [PHY-UNH40]_.
:numref:`tab-phy-int-reqs` lists the requirements.

.. list-table:: 1000BASE-T transmitter and link requirements (required,
   [PHY-UNH40]_)
   :name: tab-phy-int-reqs
   :header-rows: 1
   :widths: 40 40 20

   * - Quantity
     - Limit
     - Subclause
   * - Peak output in test mode 1
     - 0.67 V to 0.82 V; peaks matched within 1 %
     - :clause:`40.6.1.2.1`
   * - Droop in test mode 1
     - Output keeps more than 73.1 % of its peak value
     - :clause:`40.6.1.2.2`
   * - Peak distortion in test mode 4
     - Less than 10 mV for at least 60 % of the symbol period
     - :clause:`40.6.1.2.4`
   * - Common-mode output
     - Less than 50 mV peak-to-peak
     - :clause:`40.8.3.3`
   * - Return loss
     - At least 16 dB from 1 MHz to 40 MHz; at least
       :math:`10 - 20\log_{10}(f/80)` dB from 40 MHz to 100 MHz
       (:math:`f` in MHz)
     - :clause:`40.8.3.1`
   * - Transmit clock jitter, unfiltered
     - Less than 1.4 ns peak-to-peak
     - :clause:`40.6.1.2.5`
   * - Transmit clock jitter, filtered
     - Less than 0.3 ns (master), 0.4 ns (slave) peak-to-peak
     - :clause:`40.6.1.2.5`
   * - Transmit clock frequency
     - 125 MHz ± 12.5 kHz (±100 parts per million)
     - :clause:`40.6.1.2.6`
   * - Bit error rate over the worst-case 100 m channel
     - Better than :math:`10^{-10}`
     - :clause:`40.4.2.3`, :clause:`40.7`

Blocks
~~~~~~

The transceiver for one port contains the blocks below (see
:numref:`fig-phy-blocks`). The analog front end and the per-pair signal
processing are repeated four times, once per pair.

.. list-table:: Blocks of one integrated 1000BASE-T port
   :name: tab-phy-int-blocks
   :header-rows: 1
   :widths: 26 10 64

   * - Block
     - Per port
     - Specification
   * - DAC and line driver
     - 4
     - 17 shaped levels at 125 MHz, at least 7 bits of linearity, about
       1 V peak into 100 Ω from a matched source
       (:ref:`phy-int-transmitter`)
   * - Termination and line protection
     - 4
     - About 73 Ω to 138 Ω across process and temperature; connection
       without transformers per :doc:`../magnetics`
       (:ref:`phy-int-cable`)
   * - Hybrid (and optional analog echo pre-cancellation)
     - 4
     - Removes the transceiver's own signal before the ADC
       (:ref:`phy-int-echo`)
   * - Receive amplifier, filter and ADC
     - 4
     - 125 million samples per second, about 7 effective bits (ENOB,
       defined in :ref:`phy-int-adc`)
   * - Echo canceller, 3 near-end crosstalk cancellers, equalizers
     - 4
     - Adaptive digital filters, about 220 taps per pair at 125 MHz
       (:ref:`phy-int-dsp`)
   * - Trellis decoder with decision feedback
     - 1
     - One 8 ns loop across all four pairs (:ref:`phy-int-decision-loop`)
   * - Scrambler, coding, delimiters
     - 1
     - IEEE 802.3 :clause:`40` coding
   * - Clock synthesis and recovery
     - 1
     - 25 MHz reference, 125 MHz PLL, sampling phase adjustment, master and
       slave timing (:ref:`phy-int-clock`)
   * - Link pulses and autonegotiation
     - 1
     - :clause:`28` state machines and timers, 1000BASE-T next pages
       (:ref:`phy-int-autoneg`)
   * - Management registers
     - 1
     - :clause:`22` register set, including registers 9 and 10
       (:numref:`tab-phy-int-registers`)

.. _phy-int-transmitter:

Transmitter: DAC and line driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Linearity.** The distortion limit sets how linear the transmitter must be.
The worst error at any symbol must stay below 10 mV, against a peak of
about 0.745 V [PHY-DP83867]_, that is :math:`0.010 / 0.745 = 1.3\,\%` of the
peak. An ideal digital-to-analog converter (DAC) with :math:`N` bits
spanning :math:`\pm V_\text{pk}` has steps of :math:`2V_\text{pk}/2^N` and a
worst rounding error of half a step:

.. math::

   e_\text{max} = \frac{V_\text{pk}}{2^N}

where :math:`e_\text{max}` is the largest error in V and
:math:`V_\text{pk} = 0.745` V. Requiring :math:`e_\text{max} < 10` mV:

.. math::

   2^N > \frac{0.745}{0.010} = 74.5

.. math::

   N > \log_2 74.5 = 6.2

So the DAC and line driver together need at least 7 bits of linearity
(estimate, counting rounding error only; for 7 bits,
:math:`e_\text{max} = 0.745 / 128 = 5.8` mV, leaving about 4 mV for all
other errors). The 17 shaped levels of PAM-5 (see :ref:`phy-pam5`) need at least 5 bits of DAC resolution, so linearity, not the number of
levels, sets the DAC.

**Swing.** The driver's output impedance must match the 100 Ω line, so it
forms a voltage divider with the line and half of its internal voltage
appears on the line:

.. math::

   V_\text{src} = 2\,V_\text{line}

where :math:`V_\text{line}` is the peak differential voltage on the line
and :math:`V_\text{src}` the peak differential voltage the driver generates
behind its matching resistance. With the 2 V peak-to-peak launch level of
the 802.3ab design point [PHY-TUT98]_, :math:`V_\text{line} = 1` V and
:math:`V_\text{src} = 2` V. A differential driver whose outputs each swing
between 0 V and its supply can produce at most :math:`\pm V_\text{DD}`, so
a 3.3 V supply gives 1.3 V of headroom for the output transistors
(estimate). The 3.3 V transistors of gf180mcu (see :ref:`phy-int-devices`)
are therefore enough for the gigabit swing.

**Power.** Assume that PAM-5 symbols are equally likely to take each of the
five levels -2, -1, 0, +1, +2 (an assumption; scrambling makes the symbols
look random, but the trellis code and idle patterns make the levels not
exactly equally likely). With level 2 at 1 V, the mean square level is
:math:`(4 + 1 + 0 + 1 + 4)/5 = 2`, in units of
:math:`(0.5\ \text{V})^2`, so the rms line voltage is

.. math::

   V_\text{rms} = 0.5\ \text{V} \times \sqrt{2} = 0.707\ \text{V}

and the power delivered into the 100 Ω line is

.. math::

   P_\text{line} = \frac{V_\text{rms}^2}{R} = \frac{0.707^2}{100}
   = 5.0\ \text{mW}

The matching resistance dissipates the same again, so a perfect driver uses
10 mW per pair (estimate, ignoring shaping). Real drivers use more because
their output stage must be biased for linearity: line drivers "dominate the
GPHY power consumption" according to a 2014 gigabit line-driver paper
[PHY-PAN14]_ (*GPHY* is industry shorthand for a gigabit transceiver), and
published 180 nm drivers for the same ±1 V swing at 100 Mbit/s use 24 mW
[PHY-BUHR18]_ to 38 mW [PHY-RICHTER14]_. The estimates below use 24 mW to
38 mW per pair from the same two sources.

.. _phy-int-cable:

The cable interface
~~~~~~~~~~~~~~~~~~~

Each pair must look like a 100 Ω resistor to the cable, so that signals
arriving from the cable are not reflected back. The standard sets this as a
minimum *return loss* (:clause:`40.8.3.1`): 16 dB from 1 MHz to 40 MHz, and
:math:`10 - 20\log_{10}(f/80)` dB from 40 MHz to 100 MHz, which falls to
8.1 dB at 100 MHz (required, [PHY-UNH40]_). The 16 dB below 40 MHz is the
tighter limit and is used here. Return loss is the size of the reflection in decibels. The
reflection coefficient :math:`\Gamma` (the reflected voltage divided by the
incident voltage) is

.. math::

   |\Gamma| = 10^{-L_\text{RL}/20}

and a termination of impedance :math:`Z` reflects

.. math::

   |\Gamma| = \frac{|Z - R|}{Z + R}

where :math:`L_\text{RL}` is the return loss in dB and :math:`R` is the
reference impedance in Ω. Solving the second equation for :math:`Z` gives
the allowed range:

.. math::

   Z_\text{min} = R\,\frac{1 - |\Gamma|}{1 + |\Gamma|}

.. math::

   Z_\text{max} = R\,\frac{1 + |\Gamma|}{1 - |\Gamma|}

With :math:`L_\text{RL} = 16` dB and :math:`R = 100` Ω:

.. math::

   |\Gamma| = 10^{-16/20} = 10^{-0.8} = 0.158

.. math::

   Z_\text{min} = 100 \times \frac{0.842}{1.158} = 72.6\ \Omega

.. math::

   Z_\text{max} = 100 \times \frac{1.158}{0.842} = 137.7\ \Omega

So the termination must stay within about 73 Ω to 138 Ω across frequency,
temperature and process (estimate, from the required return loss). The
gf180mcu unsalicided P+ poly resistor ranges from 280 to 420 Ω per square,
±20 % around its typical value [PHY-GF180PDK]_, which uses most of that
range before any other error. The termination therefore needs trimming, or
an active termination whose impedance is set by feedback; a published
180 nm line driver with digital impedance control covers 80 Ω to 130 Ω
[PHY-BUHR20B]_.

The cable also carries voltages that are not part of the signal: voltage
common to both wires of a pair, surges, and in the full design Power over
Ethernet (see :doc:`../../power/poe`). Without transformers, these reach evampire's pins through the
external components described in :doc:`../magnetics`, and the common-mode
range, isolation and protection that the line driver and receiver must
withstand are set there. The standard analog pads of gf180mcu contain only
protection diodes [PHY-GF180IO]_, which are sized for short,
energy-limited discharge events rather than for continuous voltage stress.
The line driver and receiver are custom circuits and can use custom
protection structures and higher-voltage or stacked transistors where the
line interface needs them.

.. _phy-int-echo:

Hybrid and echo cancellation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**The problem.** The receiver sees its own transmission at full size while
the far-end signal may be reduced to 6 % of its voltage at 100 MHz (24 dB;
see :ref:`phy-echo` and :numref:`tab-phy-channel-limits`). The echo must be removed to below the noise
before the receiver can decide symbols. The removal is shared between an
analog hybrid, an optional analog pre-canceller, and the digital echo
canceller. Whatever the analog stages leave sets the input range the ADC
must handle, and so its resolution.

Without a transformer, the hybrid works on the capacitor-coupled pins, and
its balance depends on how well the on-chip replica network matches the
line and the external components of :doc:`../magnetics`.

.. list-table:: Approaches to echo removal (published results)
   :name: tab-phy-int-echo
   :header-rows: 1
   :widths: 26 37 37

   * - Approach
     - Published result
     - Effect on the rest of the design
   * - Analog hybrid, then a long digital echo canceller only
     - 802.3ab design point: 120-tap digital echo canceller, ADC input
       range 2.2 V peak-to-peak for a 2 V peak-to-peak launch
       [PHY-TUT98]_
     - ADC needs about 7 effective bits; the most digital taps
   * - Hybrid plus a 4-tap analog echo pre-canceller before the ADC
     - 10 dB echo suppression measured, 43 mW from 3 V, about 1 mm² in
       0.4 µm, and with a few more taps it can relax the ADC by one bit
       [PHY-LEE01]_; removes about 50 digital canceller taps [PHY-LEE00]_
     - About 1 ADC bit and 50 taps saved per pair, for about 43 mW and
       1 mm² per pair
   * - Driver and receiver merged into one circuit
     - Merges transmission, reception and termination, removes the
       separate hybrid, and enables adaptive echo cancellation; passes the
       1000BASE-T tests from 2.5 V in 28 nm [PHY-PAN14]_
     - Abstract only; no figures for a 180 nm process

Lee and Razavi also note that near-end crosstalk from the other pairs is
only about 16 dB below the uncorrected echo, so more than about 10 dB to
15 dB of analog echo cancellation brings no further benefit [PHY-LEE01]_.
Their pre-canceller, about 1 mm² and 43 mW, is of the same order as one of
the ADCs in :numref:`tab-phy-int-adcs` (estimate, comparing published
designs in different processes); it is worth adding only if it allows a
simpler ADC.

.. _phy-int-adc:

ADC
~~~

Each of the four pairs needs an analog-to-digital converter (ADC) running at
the 125 MHz symbol rate. An ideal :math:`N`-bit converter spanning a
full-scale range :math:`V_\text{FS}` has steps of
:math:`q = V_\text{FS}/2^N`. Its rounding error is spread evenly between
:math:`-q/2` and :math:`+q/2`, which has a mean-square value (noise power) of
:math:`q^2/12`. A full-scale sine wave has amplitude :math:`V_\text{FS}/2`
and power :math:`V_\text{FS}^2/8`. The ratio of the two, the
*signal-to-quantisation-noise ratio* (SQNR), is
:math:`(V_\text{FS}^2/8)/(q^2/12) = 1.5 \times 2^{2N}`, which in decibels is

.. math::

   \text{SQNR} = 10\log_{10}(1.5) + 20 N \log_{10} 2
   = 6.02\,N + 1.76\ \text{dB}

A real converter is described by its *effective number of bits* (ENOB, see
`effective number of bits <https://en.wikipedia.org/wiki/Effective_number_of_bits>`__),
found by putting its measured signal-to-noise-and-distortion ratio (SNDR)
into the same formula:

.. math::

   \text{ENOB} = \frac{\text{SNDR} - 1.76}{6.02}

The 802.3ab design points give the requirement: 6.5 bits ideal (SQNR
:math:`6.02 \times 6.5 + 1.76 = 40.9` dB) in one, 7 bits ideal
(:math:`6.02 \times 7 + 1.76 = 43.9` dB) in another [PHY-TUT98]_; an echo
canceller paper states at least 7 bits, and 8 bits in practice
[PHY-LEE01]_. The target is therefore an ADC of about 7 effective bits at
125 MHz (estimate), one bit fewer with analog echo pre-cancellation.

.. list-table:: Published 7-bit to 8-bit ADCs at 100 to 200 million samples
   per second
   :name: tab-phy-int-adcs
   :header-rows: 1
   :widths: 30 20 14 12 10 14

   * - Design
     - Process, supply
     - Rate (MS/s)
     - Power
     - Area
     - Accuracy
   * - Folding and interpolating [PHY-HEO02]_
     - 0.35 µm, 3.3 V
     - 200
     - 120 mW
     - 1.02 mm²
     - 42.5 dB SFDR
   * - Folding, for Gigabit Ethernet [PHY-YOON00]_
     - 0.35 µm
     - 125
     - 110 mW
     - 0.8 mm²
     - 6.4 ENOB
   * - Time-interleaved pipelined [PHY-LIMOTYRAKIS05]_
     - 0.18 µm, 1.8 V
     - 150
     - 71 mW
     - —
     - 45.4 dB SNDR (7.2 ENOB)
   * - Pipelined [PHY-JIANG08]_
     - 0.18 µm, 1.8 V
     - 200
     - 22 mW
     - —
     - 45 dB SNDR (7.2 ENOB)
   * - Pipelined, no sample-and-hold [PHY-ZHANG10]_
     - 0.18 µm, 1.8 V
     - 100
     - 23.4 mW
     - 0.53 mm²
     - 7.43 ENOB at 1 MHz, 6.94 at 80 MHz

SFDR is the *spurious-free dynamic range*: how far below the signal the
largest unwanted tone lies. The ENOB values in parentheses follow from the
formula above; for example :math:`(45.4 - 1.76) / 6.02 = 7.2`. The
architectures compare as follows:

* **Folding** converters reach 125 MS/s to 200 MS/s in 0.35 µm (at 3.3 V
  in [PHY-HEO02]_), the closest published match to the gf180mcu 3.3 V
  transistors, at about 110 mW to 120 mW each.
* **Pipelined** and **time-interleaved** converters reach the same
  accuracy at 22 mW to 71 mW, but the published examples use 1.8 V
  transistors, which gf180mcu does not have. With 3.3 V transistors they
  would need redesign; their power in gf180mcu is not known.
* No 8-bit *successive-approximation* (SAR) converter, which finds each
  bit in turn with one comparator and a capacitor DAC, at 125 MS/s or above
  in 0.18 µm was found.

The estimates below use 71 mW to 120 mW and 0.53 mm² to 1.02 mm² per ADC;
the low end comes from 1.8 V designs and is optimistic for gf180mcu.

.. _phy-int-dsp:

Signal processing
~~~~~~~~~~~~~~~~~

:ref:`phy-dsp-rate` derives the arithmetic rate: about 880 filter taps,
:math:`1.1 \times 10^{11}` multiply-and-add operations per second, for the
802.3ab design point; a published Broadcom analysis gives "over 150 Giga
operations per second" [PHY-HATAMIAN98]_. Two properties reduce the cost:

* The echo and near-end crosstalk cancellers multiply a coefficient by a
  transmitted symbol. If the symbol is one of the five PAM-5 levels -2, -1,
  0, +1, +2, multiplying needs only a shift, a negation or zero, not a
  general multiplier. If it is one of the 17 shaped levels (multiples of
  0.25 from -2 to +2), each product needs at most one shift-and-add, since
  every whole number from -8 to 8 is a sum or difference of at most two
  powers of two.
* Only the feed-forward equalizer multiplies full ADC samples.

All the filters can be pipelined (registers inserted between stages, with
the matching delay accounted for) and split into parallel paths, so their
speed is a matter of area, not of feasibility. The one part that cannot
simply be pipelined is the loop discussed next.

.. _phy-int-decision-loop:

The 8 ns decision loop
~~~~~~~~~~~~~~~~~~~~~~

**The problem.** The decision-feedback equalizer subtracts the tails of
symbols the receiver has just decided, and the trellis decoder's decisions
depend on that subtraction. The decision for one symbol period must
therefore be complete before the next one starts: a loop that must close in
8 ns [PHY-TUT98]_. The usual structure is a *parallel decision-feedback
decoder*, with one decision-feedback equalizer per decoder state (8 in all).
:numref:`tab-phy-int-loop` compares published ways to make it fast enough.

.. list-table:: Published approaches to the decision loop
   :name: tab-phy-int-loop
   :header-rows: 1
   :widths: 30 30 40

   * - Approach
     - Published result
     - Cost
   * - 14-tap parallel decision-feedback decoder, direct
     - About 500 Mbit/s in 3.3 V 0.16 µm cells; 158,000 gates
       [PHY-AZADET-PAT]_
     - Too slow without further measures
   * - Same decoder, pipelined
     - 125 MHz in 3.3 V 0.16 µm cells; processing speed improved by a
       factor of two [PHY-HARATSCH01B]_; a later pipelined version reduces
       the hardware overhead by 60 % [PHY-GU07]_
     - Extra pipeline hardware
   * - Decision-feedback prefilter and 1-tap decoder with look-ahead
     - 1 Gbit/s at 125 MHz in 3.3 V 0.25 µm cells; gate count and
       throughput both improved by a factor of two compared with the 14-tap
       decoder; 1.3 dB performance loss [PHY-HARATSCH01]_
     - 1.3 dB of noise margin
   * - 4-tap reduced-state (M-algorithm) decoder
     - Better performance than the 14-tap decoder at 39 % of its area, in
       0.18 µm (synthesis and post-layout simulation) [PHY-ZHU07]_
     - Not demonstrated in silicon

*Look-ahead* rewrites the loop so that the next decision is computed from
precomputed candidates for each possible previous decision, leaving only a
selection inside the loop [PHY-PARHI91]_. Applied to the gigabit decoder it
removed the speed problem in 3.3 V standard cells in a 0.25 µm process
[PHY-HARATSCH01]_. The gf180mcu standard cells use longer transistors
(0.5 µm and 0.6 µm, see :ref:`phy-int-cells`), so whether the same structure
closes in 8 ns there must be checked by synthesis and timing analysis.

For the gate count, the look-ahead design is reported to need half the
gates of a 14-tap parallel decision-feedback decoder [PHY-HARATSCH01]_, and
a 14-tap decoder of that kind has been reported at 158,000 gates
[PHY-AZADET-PAT]_. Applying the factor of two to that figure gives

.. math::

   \frac{158{,}000}{2} = 79{,}000\ \text{gates}

for the decoder (estimate; the two numbers come from different
implementations by the same group, so the result is approximate).

**Logic per cycle in gf180mcu.** The gf180mcu standard-cell libraries come
in a *7-track* and a *9-track* version: the number of routing tracks that
fit in the height of one cell row (3.92 µm and 5.04 µm) [PHY-GF180SC]_.
Taller cells have larger transistors and are faster. The time left for
logic in one clock period :math:`T` is

.. math::

   t_\text{logic} = T - t_\text{clk-Q} - t_\text{setup}

where :math:`t_\text{clk-Q}` and :math:`t_\text{setup}` are the flip-flop's
clock-to-output delay and setup time. Dividing by the delay of one
full-adder carry stage :math:`t_\text{carry}` gives how many such stages
fit. For example, at the typical 3.3 V corner and :math:`T = 8` ns:

.. math::

   t_\text{logic} = 8 - 1.203 - 0.378 = 6.42\ \text{ns}

.. math::

   \frac{6.42\ \text{ns}}{1.015\ \text{ns}} = 6.3\ \text{carry stages}

.. list-table:: Full-adder carry stages per clock period, gf180mcu 7-track
   cells (``dffq_1`` and ``addf_1``, input slew 0.287 ns, load 0.0122 pF,
   worst of rise and fall [PHY-GF180SC]_; estimate)
   :name: tab-phy-int-timing
   :header-rows: 1
   :widths: 30 20 16 17 17

   * - Corner
     - :math:`t_\text{clk-Q}` + :math:`t_\text{setup}`
     - :math:`t_\text{carry}`
     - Stages at 8 ns (125 MHz)
     - Stages at 16 ns (62.5 MHz)
   * - Typical, 3.3 V, 25 °C
     - 1.203 + 0.378 ns
     - 1.015 ns
     - 6.3
     - 14.2
   * - Slow, 3.0 V, 125 °C
     - 2.380 + 0.848 ns
     - 2.057 ns
     - 2.3
     - 6.2
   * - Typical, 1.8 V, 25 °C
     - 2.996 + 1.191 ns
     - 2.698 ns
     - 1.4
     - 4.4
   * - Slow, 1.62 V, 125 °C
     - 7.303 + 3.281 ns
     - 6.804 ns
     - none
     - 0.8

**Cells and supply voltage.** The standard cells of gf180mcu are built
from the 5 V transistors (gate lengths 0.6 µm and 0.5 µm) even when run from
3.3 V or 1.8 V [PHY-GF180SC]_. Three options:

* **5 V-transistor cells at 3.3 V** (characterised). At the slow corner
  only about two carry stages fit in 8 ns, so the decision loop needs the
  look-ahead structure above, and every other path must be pipelined
  finely.
* **5 V-transistor cells at 1.8 V** (characterised). Switching energy falls
  to about a quarter (see :ref:`switching energy <phy-int-energy>`), but
  at 1.8 V even the
  typical corner fits only 1.4 carry stages in 8 ns, and the slow corner
  (1.62 V, 125 °C) none. The decision loop would need at least two parallel
  paths at 62.5 MHz, and at the slow corner even 62.5 MHz leaves 0.8 carry
  stages (:numref:`tab-phy-int-timing`), so in practice it would also need a
  supply between 1.8 V and 3.3 V, which is not characterised. Because the
  parallelism and supply such a design needs are not known, the power
  estimates below do not include a reduced-voltage case.
* **Custom cells built from the 3.3 V transistors** (0.28 µm gate length
  [PHY-GF180PDK]_, not in the standard library). These are faster and
  smaller per gate than the 5 V-transistor cells, but would need to be
  designed, characterised and verified; no measured delay data was found.

.. _phy-int-energy:


**Switching energy.** Charging a node of capacitance :math:`C` to voltage
:math:`V` stores
:math:`\tfrac{1}{2} C V^2` in the capacitance and dissipates another
:math:`\tfrac{1}{2} C V^2` in the transistors; discharging it dissipates the
stored half. One full charge and discharge therefore draws
:math:`E = C V^2` from the supply. Taking the switched capacitance
of one gate as three times the input capacitance of a 2-input NAND gate
(the gate's own output and wiring plus two inputs it drives; an assumption)
gives:

.. math::

   E_{3.3} = 3 \times 4.70\ \text{fF} \times (3.3\ \text{V})^2
   = 14.1\ \text{fF} \times 10.89\ \text{V}^2 = 154\ \text{fJ}

.. math::

   E_{1.8} = 3 \times 4.275\ \text{fF} \times (1.8\ \text{V})^2
   = 12.8\ \text{fF} \times 3.24\ \text{V}^2 = 41.6\ \text{fJ}

where 4.70 fF and 4.275 fF are the input capacitances of ``nand2_1`` at the
3.3 V and 1.8 V typical corners [PHY-GF180SC]_. The ratio is
:math:`41.6 / 154 = 0.27`.

**DSP power (estimate).** The power of :math:`N_\text{gates}` gates, of which
a fraction :math:`\alpha` completes a charge and discharge in each cycle of
a clock :math:`f`, is

.. math::

   P_\text{DSP} = N_\text{gates} \times \alpha \times f \times E

where:

* :math:`N_\text{gates}` = 250,000 to 400,000 gate equivalents. The upper
  value is the 802.3ab layout study [PHY-TUT98]_; the lower value assumes
  the 330,000-gate design point [PHY-TUT98]_ with its decoder reduced from
  about 158,000 to 79,000 gates by look-ahead (estimate above),
  :math:`330{,}000 - 79{,}000 = 251{,}000`;
* :math:`\alpha` = 0.1 to 0.2, an assumed activity for datapath logic;
* :math:`f = 125 \times 10^{6}` per second;
* :math:`E` = 154 fJ at 3.3 V.

Low end: :math:`250{,}000 \times 0.1 \times 125 \times 10^{6} \times 154\
\text{fJ} = 0.48` W. High end: :math:`400{,}000 \times 0.2 \times 125
\times 10^{6} \times 154\ \text{fJ} = 1.54` W. These figures are for the
standard cells at 3.3 V; they leave out the clock network and leakage and
rest on the assumed activity, so they are rough estimates.

For comparison, scaling the 802.3ab tutorial's 3.1 W at 2.5 V
[PHY-TUT98]_ to 3.3 V with the square of the supply gives
:math:`3.1 \times (3.3/2.5)^2 = 5.4` W. The same authors' estimate for a
related design states that the 3.1 W figure includes the analog front end
[PHY-QAM97]_, so it is the power of a whole transceiver, and the scaled
5.4 W is an upper bound rather than a prediction (see also
:ref:`phy-dsp-rate`).

**DSP area (estimate).** Taking one gate as one 2-input NAND gate,

.. math::

   A_\text{DSP} = \frac{N_\text{gates} \times A_\text{NAND2}}{u}

where :math:`A_\text{NAND2}` = 10.976 µm² (7-track) or 14.112 µm²
(9-track) [PHY-GF180SC]_ and :math:`u` = 0.7 is the assumed fraction of
the area filled by cells. For 250,000 gates in the 7-track library:

.. math::

   \frac{250{,}000 \times 10.976\ \mu\text{m}^2}{0.7} = 3.9\ \text{mm}^2

and for 400,000 gates in the 9-track library, 8.1 mm².

.. _phy-int-clock:

Clock recovery and master/slave timing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The slave recovers the master's clock and transmits with it; the master
transmits with its own crystal clock and recovers the slave's phase for its
receiver. The required unfiltered jitter limit (:clause:`40.6.1.2.5`,
measured with the transmitter test modes) of 1.4 ns peak-to-peak is

.. math::

   \frac{1.4\ \text{ns}}{8\ \text{ns}} = 0.175

of a symbol period, with tighter limits of 0.3 ns (master) and 0.4 ns
(slave) after high-pass filtering [PHY-UNH40]_.

The usual approach is a phase-locked loop (PLL) at 125 MHz and a phase
interpolator that moves the sampling phase in small steps. Broadcom's 1997
jitter analysis takes 64 phases per symbol as an example, giving steps of
:math:`8\ \text{ns}/64 = 125` ps, and states that a 125 ps step causes
tolerable degradation in PAM-5 [PHY-OSCAR97]_. A published 180 nm PLL and
256-phase interpolator has finer steps, :math:`8\ \text{ns}/256 = 31.25` ps,
4.9 ps rms jitter, 4.0 mW and 0.065 mm²; its digital clock recovery uses 204
standard cells [PHY-BUHR21]_.

To compare an rms jitter :math:`\sigma` with a peak-to-peak limit, assume a
Gaussian distribution, and take as the peak-to-peak value the range whose
ends are exceeded on each side with probability :math:`10^{-12}`:

.. math::

   J_\text{pp} = 2\,Q\,\sigma

where :math:`Q = 7.03` is the number of standard deviations beyond which a
single tail of the Gaussian distribution holds probability
:math:`10^{-12}`. With :math:`\sigma = 4.9` ps:

.. math::

   J_\text{pp} = 2 \times 7.03 \times 4.9\ \text{ps} = 69\ \text{ps}

(estimate), about 20 times below 1.4 ns. No published measured 1000BASE-T
master/slave clock-recovery circuit was found; the timing-recovery loop
itself is digital and can be developed on samples captured from the ADCs.

.. _phy-int-autoneg:

Link pulses and autonegotiation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Autonegotiation (explained in :ref:`phy-autoneg`) is required for
1000BASE-T, so a gigabit-only transceiver still needs:

* a **link pulse transmitter**: single pulses about 100 ns wide, in bursts
  of 17 to 33 pulses with clock pulses 125 µs ± 14 µs apart, bursts
  repeated every 16 ms ± 8 ms (required, :clause:`28.3.2`) [PHY-UNH28]_.
  Each pulse is a 10BASE-T link pulse, so the line driver must be able to
  produce one;
* a **link pulse receiver**: a comparator with a threshold, and timers that
  check pulse spacing;
* three **state machines** defined in IEEE 802.3 :clause:`28`: the transmit
  state diagram (:clause:`Figure 28-16 <28>`), the receive state diagram
  (:clause:`Figure 28-17 <28>`) and the arbitration state diagram
  (:clause:`Figure 28-18 <28>`) [PHY-UNH28]_;
* the 1000BASE-T **next page** exchange (:clause:`40.5.1.2`) carrying the
  1000BASE-T abilities, the port type and the 11-bit random seed, and the
  master/slave resolution rules (:clause:`40.5.2`) [PHY-UNH28M]_;
* **timers** with the required ranges in :numref:`tab-phy-int-timers`
  (:clause:`28.3.2`).

.. list-table:: Autonegotiation timers (required, [PHY-UNH28]_ [PHY-UNH14]_)
   :name: tab-phy-int-timers
   :header-rows: 1
   :widths: 40 30 30

   * - Timer
     - Range
     - What it times
   * - Burst spacing
     - 16 ms ± 8 ms
     - Interval between fast link pulse bursts
   * - Pulse spacing within a burst
     - 62.5 µs ± 7 µs
     - Clock pulse to data pulse
   * - Link fail inhibit
     - 750 ms to 1000 ms
     - Time allowed for the chosen speed to report a working link
   * - Break link
     - 1200 ms to 1500 ms
     - Silence before negotiation restarts
   * - Autonegotiation wait
     - 500 ms to 1000 ms
     - Wait before accepting a speed found by parallel detection
   * - Link loss (10BASE-T)
     - 50 ms to 150 ms
     - Time without link pulses before the link is declared down

A counter that measures time :math:`T` with a clock of frequency
:math:`f_\text{clk}` needs

.. math::

   N_\text{bits} = \left\lceil \log_2 (T \times f_\text{clk}) \right\rceil

bits, where :math:`\lceil\,\rceil` means rounding up. For the longest timer,
:math:`T = 1.5` s, with the 25 MHz reference clock:

.. math::

   T \times f_\text{clk} = 1.5 \times 25 \times 10^{6} = 37.5 \times 10^{6}

.. math::

   \log_2(37.5 \times 10^{6}) = 25.2

so the longest timer needs a 26-bit counter (estimate). Autonegotiation is
simple digital logic; its only analog parts are the link pulse driver and
comparator. Whether the link pulses need full 10BASE-T amplitude is an open
question (see `Open design questions`_), because it decides how much of the
higher-swing 10BASE-T driver a gigabit-only transceiver still needs.

.. _phy-int-registers:

Management registers and reference clock
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

IEEE 802.3 :clause:`22` defines a set of 16-bit registers that every
transceiver provides, so that the same software can control any of them
[PHY-8023]_. With an integrated transceiver the processor reads and writes
them directly as on-chip registers; keeping the standard layout lets the
same software drive both the external transceiver of the first version and
the integrated one. :numref:`tab-phy-int-registers` lists them.

.. list-table:: Standard transceiver registers (IEEE 802.3 :clause:`22`; the
   same addresses are used by the TI DP83867 [PHY-DP83867]_)
   :name: tab-phy-int-registers
   :header-rows: 1
   :widths: 15 85

   * - Address
     - Contents
   * - 0
     - Control: reset, loopback, speed selection, enable and restart
       autonegotiation, power down
   * - 1
     - Status: link up, autonegotiation complete, abilities
   * - 2, 3
     - Identifier of the manufacturer and model
   * - 4
     - Autonegotiation advertisement (this end's abilities)
   * - 5
     - Link partner abilities (received)
   * - 6
     - Autonegotiation expansion (next page support, faults)
   * - 7, 8
     - Next page to transmit, and next page received
   * - 9, 10
     - 1000BASE-T control and status (master/slave configuration and result,
       1000BASE-T abilities, test modes)
   * - 15
     - Extended status (1000 Mbit/s abilities)

Register 9 also selects the four transmitter test modes
(:clause:`40.6.1.1.2`, see :numref:`tab-phy-int-reqs`) that 1000BASE-T
conformance testing needs [PHY-UNH40]_ [PHY-DP83867]_; the integrated
transceiver must provide them to be tested.

The symbol clock must be within ±100 parts per million of 125 MHz
(required, :clause:`40.6.1.2.6`) [PHY-UNH40]_. Commercial transceivers use a
25 MHz crystal of ±50 parts per million [PHY-DP83867]_ and a PLL to
125 MHz.

.. _phy-int-area-power:

Area and power of the gigabit transceiver
-----------------------------------------

This section adds up the estimates above for one port and for evampire's
two ports. Every value is a rough estimate derived from published designs
in other processes and from the stated assumptions, with large
uncertainty; the actual area and power of a gigabit transceiver on
gf180mcu are not known and remain open questions (see
`Open design questions`_). The signal-processing values are for the
standard cells at 3.3 V; reduced-voltage operation is not included because
the parallelism and supply it would need are not known (see
:ref:`phy-int-decision-loop`).

.. list-table:: Estimated area and power of one 1000BASE-T port on gf180mcu
   (rough estimate)
   :name: tab-phy-int-area-power
   :header-rows: 1
   :widths: 34 22 22 22

   * - Part
     - Basis
     - Area
     - Power
   * - 4 ADCs
     - 0.53–1.02 mm², 71–120 mW each (:numref:`tab-phy-int-adcs`)
     - 2.1–4.1 mm²
     - 0.28–0.48 W
   * - 4 DACs and line drivers
     - 0.13–0.16 mm² [PHY-BUHR21]_, 24 mW [PHY-BUHR18]_ to 38 mW
       [PHY-RICHTER14]_ each
     - 0.5–0.6 mm²
     - 0.10–0.15 W
   * - PLL and phase interpolator
     - [PHY-BUHR21]_
     - 0.07 mm²
     - 0.004 W
   * - Signal processing at 3.3 V
     - 250,000–400,000 gates (:ref:`switching energy <phy-int-energy>`)
     - 3.9–8.1 mm²
     - 0.48–1.54 W
   * - **Total**
     -
     - **6.6–12.8 mm²**
     - **0.86–2.17 W**

Not included: receive amplifiers and filters, the hybrids, protection,
clock distribution and leakage (no published gigabit figures were found for
these blocks in a comparable process), and the optional analog echo
pre-cancellers (about 1 mm² and 43 mW each in 0.4 µm [PHY-LEE01]_).

For the two ports:

.. math::

   A_\text{2 ports} = 2 \times (6.6\ \text{to}\ 12.8)\ \text{mm}^2
   = 13\ \text{to}\ 26\ \text{mm}^2

.. math::

   P_\text{2 ports} = 2 \times (0.86\ \text{to}\ 2.17)\ \text{W}
   = 1.7\ \text{to}\ 4.3\ \text{W}

These are rough, literature-derived ranges. The area in particular depends
on choices that are not yet made (decoder architecture, tap counts, cell
library, ADC architecture) and on blocks with no published figure, so it is
not compared with a die size here.

**Compared with commercial transceivers.** Published 0.13 µm parts use about
0.64 W per port (VSC8244 [PHY-VSC8244]_), and the external transceivers of
the first version 0.45 W to 0.62 W per chip (see :ref:`phy-power`). The
gf180mcu estimate per port, 0.86 W to 2.17 W, is
:math:`0.86 / 0.64 = 1.3` to :math:`2.17 / 0.64 = 3.4` times the VSC8244
figure.

**Compared with the power budget (estimate).** A board powered over
Ethernet (see :doc:`../../power/poe` and :clause:`145`) receives at most
the powered-device power of its type and class [PHY-EA-BT]_. The two
gigabit ports would take the share of it in :numref:`tab-phy-int-poe`.

.. list-table:: Two gigabit ports as a share of the Power over Ethernet
   input (estimate)
   :name: tab-phy-int-poe
   :header-rows: 1
   :widths: 30 20 25 25

   * - Powered device type
     - Power at the device
     - Share at 1.7 W
     - Share at 4.3 W
   * - Type 1 (class 3)
     - 13 W
     - 13 %
     - 33 %
   * - Type 2 (class 4)
     - 25.5 W
     - 6.8 %
     - 17 %
   * - Type 3 (class 6)
     - 51 W
     - 3.4 %
     - 8.5 %
   * - Type 4 (class 8)
     - 71.3 W
     - 2.4 %
     - 6.1 %

Each share is the two-port power divided by the input power, for example
:math:`4.34 / 13 = 33\,\%` and :math:`1.73 / 13 = 13\,\%`. The power
bridging requirement passes the input power on to a USB or Ethernet output
after the board's own consumption and the converters' losses (see
:ref:`power budget <power-budget>`), so every watt the transceivers use is
a watt less for the output port. With a 13 W input, the upper estimate
leaves about 8.7 W for the rest of the board, the converters' losses and
the output port.

Building it on gf180mcu
-----------------------

The assessment separates three kinds of limit: the ratings and speed of the
standard cells, the physical limits of the devices, and what custom circuits
have reached in comparable processes.

.. _phy-int-cells:

Ratings and speed of the standard cells
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The standard-cell libraries are the starting point for the
signal-processing estimates above [PHY-GF180SC]_:

* Both libraries (7-track, 3.92 µm rows; 9-track, 5.04 µm rows) use 5 V
  transistors, characterised at 1.8 V, 3.3 V and 5 V corners.
* Flip-flop minimum period: 1.54 ns to 1.71 ns (7-track, typical, 3.3 V);
  3.10 ns to 3.56 ns (7-track, slow, 3.0 V, 125 °C); 3.95 ns to 4.71 ns
  (7-track, typical, 1.8 V).
* The general-purpose I/O cells run at 100 MHz into 30 pF (fast slew,
  16 mA) from a 5 V I/O supply; analog pads contain only protection
  diodes [PHY-GF180IO]_.

.. _phy-int-devices:

Devices and their physical limits
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From the gf180mcu PDK electrical specifications and design manual
[PHY-GF180PDK]_:

.. list-table:: gf180mcu transistors (typical values)
   :name: tab-phy-int-devices
   :header-rows: 1
   :widths: 24 14 16 22 24

   * - Device
     - Gate length
     - Threshold voltage
     - Saturation current, W = 10 µm, L = minimum
     - Breakdown
   * - 3.3 V n-channel
     - 0.28 µm
     - 0.63 V
     - 510 µA/µm at 3.3 V
     - Gate oxide 7 V minimum; drain 7 V to 9 V
   * - 3.3 V p-channel
     - 0.28 µm
     - -0.73 V
     - 250 µA/µm at 3.3 V
     - Gate oxide 7 V minimum
   * - 5 V n-channel
     - 0.6 µm
     - 0.70 V
     - 500 µA/µm at 5 V
     - Gate oxide 12 V minimum (6 V gate)
   * - 6 V n-channel
     - 0.7 µm
     - 0.73 V
     - 570 µA/µm at 6 V
     - Gate oxide 12 V minimum
   * - 10 V drain-extended n-channel (LDMOS), characterised device
     - 0.6 µm
     - 0.84 V
     - 535 µA/µm (gate 6 V, drain 10 V)
     - Drain 13.2 V minimum

Other devices: MIM capacitors (one of 1.0, 1.5 or 2.0 fF/µm² per process,
up to 20 V for the 1.0 fF/µm² option), polysilicon resistors from about
7 Ω to 3000 Ω per square, vertical NPN and PNP transistors, Schottky
diodes, and 2 to 6 metal layers with optional thick top metal.

Not documented: the transition frequency (:math:`f_\text{T}`), maximum
oscillation frequency and transconductance efficiency (:math:`g_m/I_D`) of
any transistor, and any inductor model. These matter for the 125 MHz ADC,
DAC and line driver, and must be obtained by simulation with the PDK models
or by measurement.

.. _phy-int-published:

What custom circuits have reached
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Published Ethernet transceivers and blocks in 0.16 µm to
   0.6 µm CMOS
   :name: tab-phy-int-published
   :header-rows: 1
   :widths: 36 14 50

   * - Design
     - Process
     - Result
   * - 1000BASE-T DSP receiver [PHY-HE01]_
     - 0.18 µm
     - Trellis decoder with 6 dB coding gain at 125 MBaud
   * - 10/100/1000 single-port chip [PHY-ED2000]_
     - 0.18 µm
     - 1.8 W from 3.3 V (trade press)
   * - Joint equalizer and trellis decoder [PHY-HARATSCH01]_
     - 0.25 µm, 3.3 V
     - 1 Gbit/s at 125 MHz
   * - Pipelined 14-tap decoder [PHY-HARATSCH01B]_
     - 0.16 µm, 3.3 V
     - 125 MHz
   * - 1000BASE-T baseband DSP layout [PHY-NTU04]_
     - 0.25 µm, 2.5 V
     - 7.48 ns critical path, 4.54 mm × 4.54 mm chip
   * - Analog echo canceller, 4 taps [PHY-LEE01]_
     - 0.4 µm
     - 10 dB suppression, 43 mW, about 1 mm²
   * - 8-bit 200 MS/s folding ADC [PHY-HEO02]_
     - 0.35 µm, 3.3 V
     - 120 mW, 1.02 mm²
   * - 8-bit 150 MS/s time-interleaved ADC [PHY-LIMOTYRAKIS05]_
     - 0.18 µm, 1.8 V
     - 45.4 dB SNDR, 71 mW
   * - 100BASE-TX transceiver [PHY-BUHR21]_ [PHY-BUHR19]_
     - 180 nm GlobalFoundries
     - 2.6 mm², at most 69 mW, error-free over 100 m of Category 5 cable,
       with coupling transformers (measured)
   * - Line driver, active impedance [PHY-BUHR20B]_
     - 180 nm
     - 80 Ω to 130 Ω, 200 MHz bandwidth, 24.3 mW
   * - PLL and phase interpolator [PHY-BUHR21]_
     - 180 nm GlobalFoundries
     - 125 MHz, 4.9 ps rms, 4.0 mW, 0.065 mm²

No physical limit found in the gf180mcu documentation rules out
1000BASE-T, and every gigabit block has a published counterpart in a
process of similar or larger feature size. The 0.18 µm designs whose supply
is stated used 1.8 V transistors, which gf180mcu does not have; the gigabit
decoders above were, however, built from 3.3 V standard cells in 0.16 µm and
0.25 µm.

Design problems and how to reduce their risk
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Several checks below use an *FPGA* (field-programmable gate array), a
reprogrammable logic chip on which the signal processing can be run on
real cable samples before it is built in silicon.

.. list-table:: Gigabit design problems, candidate approaches and
   verification
   :name: tab-phy-int-risks
   :header-rows: 1
   :widths: 20 45 35

   * - Problem
     - Candidate approaches
     - How it can be verified before the whole transceiver exists
   * - Signal-processing area and power
       (:ref:`phy-int-dsp`, :ref:`phy-int-area-power`)
     - Shift-and-add cancellers; look-ahead or reduced-state decoder (about
       half the decoder gates); reduced tap counts; custom 3.3 V-transistor
       cells; lower supply with parallel paths
     - Synthesis and power estimation of the filters and decoder for
       gf180mcu; FPGA implementation on captured cable samples
   * - 8 ns decision loop (:ref:`phy-int-decision-loop`)
     - Look-ahead prefilter and 1-tap decoder (125 MHz shown at 3.3 V in
       0.25 µm); pipelined decoder; faster custom cells
     - Static timing of the loop at the slow corner after synthesis and
       layout
   * - Four 125 MHz ADCs of about 7 effective bits (:ref:`phy-int-adc`)
     - Folding (shown at 3.3 V in 0.35 µm); pipelined or time-interleaved
       redesigned for 3.3 V transistors; one bit fewer with analog echo
       pre-cancellation
     - A test chip with one ADC, measured for ENOB at 125 MS/s
   * - Hybrid without a transformer (:ref:`phy-int-echo`)
     - Replica hybrid on the capacitor-coupled pins; analog echo
       pre-canceller; merged driver and receiver
     - Measurement of echo rejection on a test chip with a real cable and
       the external components of :doc:`../magnetics`
   * - Echo and crosstalk cancellation (:ref:`phy-int-dsp`)
     - Adaptive filters with symbol inputs; tap counts set by simulation
       against the channel limits
     - Simulation with measured cable responses; FPGA on captured samples
   * - Clock recovery and master/slave timing (:ref:`phy-int-clock`)
     - PLL plus phase interpolator (180 nm example: 31.25 ps steps,
       4.9 ps rms); digital timing recovery
     - Jitter measurement of the PLL on a test chip; timing recovery on an
       FPGA
   * - Line driver linearity and swing (:ref:`phy-int-transmitter`)
     - Matched voltage-mode or active-termination driver from 3.3 V
     - The four transmitter test modes need no receiver and can be measured
       on the driver alone

Optional slower speeds
----------------------

Whether the integrated transceiver also supports 100BASE-TX and 10BASE-T is
not yet fixed. On top of the gigabit design, they would add the following.

100BASE-TX
~~~~~~~~~~

.. list-table:: 100BASE-TX requirements (required, :clause:`25`,
   [PHY-UNH25]_)
   :name: tab-phy-int-100
   :header-rows: 1
   :widths: 45 55

   * - Quantity
     - Limit
   * - Peak differential output into 100 Ω
     - 0.95 V to 1.05 V; peaks symmetric within 98 % to 102 %
   * - Rise and fall time (10 % to 90 %)
     - 3 ns to 5 ns, matched within 0.5 ns
   * - Overshoot
     - At most 5 %
   * - Transmit jitter
     - At most 1.4 ns peak-to-peak
   * - Transmit clock
     - 125 MHz ± 6.25 kHz (±50 parts per million)

What it adds:

* **Coding**: 4B5B, an 11-bit scrambler and MLT-3 (see
  :ref:`phy-100base-tx`); small digital logic.
* **Transmit edge control**: a rise time between 3 ns and 5 ns. For a
  single-pole (first-order) response with time constant :math:`\tau`, the
  output reaches 10 % of its final value at :math:`0.105\,\tau` and 90 % at
  :math:`2.303\,\tau`, so the 10 % to 90 % rise time is
  :math:`t_\text{r} = 2.2\,\tau`; the bandwidth is
  :math:`f_\text{3dB} = 1/(2\pi\tau)`. Eliminating :math:`\tau`:

  .. math::

     f_\text{3dB} = \frac{2.2}{2\pi\,t_\text{r}} = \frac{0.35}{t_\text{r}}

  For :math:`t_\text{r} = 5` ns this is :math:`0.35 / 5\ \text{ns} = 70`
  MHz, and for 3 ns, :math:`0.35 / 3\ \text{ns} = 117` MHz. The gigabit DAC
  and driver can produce MLT-3 at the same ±1 V swing, with the edge
  shaping done in the DAC codes (estimate).
* **Receiver**: 100BASE-TX uses one pair in each direction, so no echo or
  crosstalk cancellation is needed; the gigabit ADC and equalizer on one
  pair can receive it. A separate low-power alternative, published in a
  180 nm GlobalFoundries process, uses an analog equalizer and five
  comparators instead of an ADC [PHY-BUHR21]_ [PHY-BUHR20A]_; that
  transceiver's measured results are in :numref:`tab-phy-int-published`.

10BASE-T
~~~~~~~~

.. list-table:: 10BASE-T requirements (required, :clause:`14`,
   [PHY-UNH14]_)
   :name: tab-phy-int-10
   :header-rows: 1
   :widths: 45 55

   * - Quantity
     - Limit
   * - Peak differential output into 100 Ω
     - 2.2 V to 2.8 V (10BASE-Te: 1.54 V to 1.96 V)
   * - Harmonics of an all-ones signal
     - At least 27 dB below the 10 MHz fundamental
   * - Output return loss, 5 MHz to 10 MHz
     - At least 15 dB against 85 Ω to 111 Ω
   * - Output short-circuit current
     - At most 300 mA, indefinitely, without damage
   * - Receiver input range
     - 585 mV to 3.1 V, with up to 13.5 ns of timing jitter

What it adds:

* **Manchester coding** and decoding, and a comparator-based receiver that
  accepts up to 3.1 V; small digital logic and no ADC.
* **A higher-swing line driver.** With a matched source the driver needs
  :math:`V_\text{src} = 2 \times 2.2` to :math:`2 \times 2.8` V, that is
  4.4 V to 5.6 V peak, which the 3.3 V supply of the gigabit driver cannot
  provide (estimate; 10BASE-Te would need 3.1 V to 3.9 V). Published ways
  round this: an active-termination class-AB driver in 180 nm produced a
  10BASE-T signal of about 2.5 V amplitude from 3.3 V, at 62 mW
  [PHY-BUHR21]_ [PHY-BUHR20B]_; a 0.4 µm current-feedback driver delivered
  5 V peak-to-peak into 50 Ω from 3.3 V [PHY-BABANEZHAD99]_. gf180mcu also
  has 5 V, 6 V and 10 V transistors (:numref:`tab-phy-int-devices`).

Blocks evampire would need
--------------------------

The gigabit blocks are listed in the order in which they depend on each
other, with what can be verified on its own first. Blocks for the optional
slower speeds follow.

1. **Reference clock and PLL**: 25 MHz crystal oscillator, PLL to 125 MHz,
   phase interpolator. Verified alone by measuring frequency and jitter.
2. **Line interface and termination**: trimmed or active 100 Ω
   termination, protection, connection to the external components of
   :doc:`../magnetics`. Verified alone by return-loss measurement.
3. **DAC and line driver**: verified alone with the four 1000BASE-T
   transmitter test modes, which need no receiver.
4. **Link pulse driver and comparator, autonegotiation logic and
   management registers**: verified against a commercial transceiver,
   which reports the abilities it receives.
5. **Hybrid, receive amplifier and ADC** (and optional analog echo
   pre-canceller): verified alone by capturing samples while transmitting
   into a real cable.
6. **Signal processing**: equalizers, echo and crosstalk cancellers,
   trellis decoder, scramblers and timing recovery. Can be developed and
   checked in simulation and on an FPGA using samples captured from block
   5, and synthesised for gf180mcu to confirm area, power and timing before
   it is committed to silicon.
7. **Byte interface to the forwarding logic**: the same interface as the
   :ref:`RGMII block <arch-rgmii>`, verified with the first-version
   forwarding logic.
8. **Optional 100BASE-TX coding and edge shaping**, reusing blocks 3, 5
   and 6.
9. **Optional 10BASE-T Manchester coding and higher-swing driver.**

Open design questions
---------------------

* Whether 100 Mbit/s and 10 Mbit/s are also supported, and if so how their
  bytes are carried on the byte interface (a byte-enable flag on the
  125 MHz clock, or a slower clock).
* Whether link pulses for autonegotiation need full 10BASE-T amplitude. The
  conformance documents used here give the link pulse template's upper
  bound (±3.1 V) but no minimum amplitude; this needs to be checked in
  IEEE 802.3 :clause:`14`. The answer decides whether a gigabit-only
  transceiver needs any of the higher-swing driver.
* Which cells and supply the signal processing uses: 5 V-transistor
  standard cells at 3.3 V, the same cells at a lower supply with parallel
  paths, or custom cells built from 3.3 V transistors.
* Which decision-loop architecture is used, and how many filter taps are
  needed per pair for the worst-case channel.
* How large the gigabit transceivers will be. The rough, literature-derived
  range of 13 mm² to 26 mm² for two ports (:ref:`phy-int-area-power`) has
  large uncertainty.
* How much power the gigabit transceivers will use, and whether it fits the
  :ref:`power budget <power-budget>` of a board powered over Ethernet (see
  :doc:`../../power/poe`) and the package's thermal limit; the rough
  estimate is 1.7 W to 4.3 W for two ports.
* How much echo the analog hybrid must remove before the ADC, given the
  transformer-free connection, and therefore the ADC resolution and whether
  an analog echo pre-canceller is used.
* Which ADC architecture suits 3.3 V transistors at 125 MS/s and about
  7 effective bits.
* The :math:`f_\text{T}` and :math:`g_m/I_D` of the gf180mcu transistors,
  which are not documented and set the speed of the analog blocks.
* How the line driver and receiver survive surges, cable discharge and
  Power over Ethernet voltages without transformers, which depends on the
  protection described in :doc:`../magnetics`.

References
----------

Standards, conformance documents and datasheets cited on this page, such
as [PHY-8023]_, [PHY-UNH40]_ and [PHY-DP83867]_, are listed on
:doc:`../phy-electrical`.

.. [PHY-HARATSCH01] E. F. Haratsch, K. Azadet, "A 1-Gb/s joint equalizer
   and trellis decoder for 1000BASE-T Gigabit Ethernet", IEEE JSSC
   36(3):374-384, 2001. https://doi.org/10.1109/4.910476.

.. [PHY-HARATSCH01B] E. F. Haratsch, K. Azadet, "A pipelined 14-tap
   parallel decision-feedback decoder for 1000BASE-T Gigabit Ethernet",
   VLSI-TSA 2001, pp. 117-120. https://doi.org/10.1109/VTSA.2001.934497.

.. [PHY-AZADET-PAT] K. Azadet, E. F. Haratsch, "Method and apparatus for
   pipelined joint equalization and decoding for gigabit communications",
   US patent 7,000,175 B2. https://patents.google.com/patent/US7000175.
   Gate count and speed of a directly implemented 14-tap decoder.

.. [PHY-GU07] Y. Gu, K. K. Parhi, "Pipelined Parallel Decision-Feedback
   Decoders for High-Speed Ethernet Over Copper", IEEE Transactions on
   Signal Processing 55(2):707-715, 2007. https://doi.org/10.1109/TSP.2006.885776.

.. [PHY-ZHU07] Zhu Yue, Rong Mengtian, Mao Junfa, M-algorithm joint decoder
   and equalizer for 1000BASE-T, Journal of Shanghai Jiaotong University
   41(8):1358-1361, 2007. Print journal; no DOI or online copy was found
   (abstract seen through the journal's index).

.. [PHY-PARHI91] K. K. Parhi, "Pipelining in algorithms with quantizer
   loops", IEEE Transactions on Circuits and Systems 38(7):745-754, 1991.
   https://doi.org/10.1109/31.135746.

.. [PHY-QAM97] O. Agazzi, M. Hatamian, H. Samueli, "Update on QAM-Based
   1000BASE-T Transceiver", IEEE 802.3, May 1997.
   https://www.ieee802.org/3/z/public/presentations/may1997/mhQAMfld.pdf.
   Gives the 3.1 W 0.25 µm estimate as including the analog front end.

.. [PHY-HEO02] Heo, Jang, Park, Park, "An 8-bit 200 MS/s CMOS
   folding/interpolating ADC with a reduced number of preamplifiers using an
   averaging technique", IEEE ASIC Conference 2002, pp. 80-83.
   https://doi.org/10.1109/ASIC.2002.1158035.

.. [PHY-LIMOTYRAKIS05] S. Limotyrakis, S. D. Kulchycki, D. K. Su,
   B. A. Wooley, "A 150-MS/s 8-b 71-mW CMOS time-interleaved ADC", IEEE
   JSSC 40(5):1057-1067, 2005. https://doi.org/10.1109/JSSC.2005.845992.

.. [PHY-ZHANG10] Zhang, Yuan, Guo, Cheng, Zeng, "An 8-bit 100-MS/s pipelined
   ADC without dedicated sample-and-hold amplifier", Journal of
   Semiconductors 31(7):075006, 2010.
   https://doi.org/10.1088/1674-4926/31/7/075006.

.. [PHY-PAN14] Pan et al., "A Full-Duplex Line Driver for Gigabit Ethernet
   With Rail-to-Rail Class-AB Output Stage in 28 nm CMOS", IEEE JSSC
   49(12):3141-3155, 2014, https://doi.org/10.1109/JSSC.2014.2353796; and the ISSCC
   2014 paper of the same title, https://doi.org/10.1109/ISSCC.2014.6757376.

.. [PHY-LEE00] C. Lee, B. Razavi, "A 125-MHz mixed-signal echo canceller
   for Gigabit Ethernet on copper wire", IEEE CICC 2000.
   https://doi.org/10.1109/CICC.2000.852708. Reduction of the digital cancellers by
   50 taps.

.. [PHY-EA-BT] L. Yseboodt, D. Abramson, *Overview of 802.3bt - Power over
   Ethernet standard*, Ethernet Alliance white paper, 2019-12.
   https://ethernetalliance.org/wp-content/uploads/2019/12/WP_EA_Overview8023bt_V2p1_FINAL.pdf.
   Powered-device power of each type and class.

.. [PHY-BUHR21] S. Buhr, *Energieeffiziente integrierte Schaltungen zur
   Basisbandsignalverarbeitung und Zeitsynchronisation für drahtgebundene
   Ethernet-Echtzeitkommunikation* (energy-efficient integrated circuits
   for baseband signal processing and time synchronisation in wired
   real-time Ethernet), Dr.-Ing. dissertation, TU Dresden, 2021.
   https://tud.qucosa.de/api/qucosa%3A77692/attachment/ATT-0/. 180 nm
   100BASE-TX transceiver: die size, power, line drivers, equalizer,
   comparator receiver, PLL and phase interpolator.

.. [PHY-BUHR19] S. Buhr, X. Xu, M. Kreißig, F. Ellinger, "A Low Power Fast
   Ethernet Physical Layer Transceiver", IEEE ICECS 2019, pp. 478-481.
   https://doi.org/10.1109/ICECS46596.2019.8964920.

.. [PHY-BUHR20A] S. Buhr, X. Xu, M. Kreißig, C. Matthus, F. Ellinger, "Low
   power analogue equaliser with adaptive digital tuning for fast
   ethernet", IET Circuits, Devices & Systems 14(5):600-610, 2020.
   https://doi.org/10.1049/iet-cds.2019.0370.

.. [PHY-BUHR18] S. Buhr, M. Kreißig, S. Protze, F. Ellinger, "Ultra Low
   Power Class-AB Voltage Mode Line Driver for Fast Ethernet", IEEE MWSCAS
   2018, pp. 17-20. https://doi.org/10.1109/MWSCAS.2018.8623924.

.. [PHY-BUHR20B] S. Buhr, M. Kreißig, C. Matthus, S. Protze, F. Ellinger,
   "Low Power Class-AB Line Driver with Adaptive Digital Impedance Control
   for Fast Ethernet", IEEE NorCAS 2020.
   https://doi.org/10.1109/NorCAS51424.2020.9265004.

.. [PHY-RICHTER14] A. Richter, C. Tzschoppe, F. Ellinger, "Low power fast
   Ethernet line driver", IEEE ICECS 2014, pp. 52-55.
   https://doi.org/10.1109/ICECS.2014.7049919.

.. [PHY-BABANEZHAD99] J. N. Babanezhad, "A 100-MHz, 50-Ω, -45-dB
   distortion, 3.3-V CMOS line driver for Ethernet and fast Ethernet
   networking applications", IEEE JSSC 34(8):1044-1050, 1999.
   https://doi.org/10.1109/4.777101.

.. [PHY-HE01] R. He, N. Nazari, S. Sutardja, "A DSP based receiver for
   1000BASE-T PHY", IEEE ISSCC 2001, pp. 308-309.
   https://doi.org/10.1109/ISSCC.2001.912651.

.. [PHY-HATAMIAN98] M. Hatamian et al., "Design considerations for gigabit
   Ethernet 1000Base-T twisted pair transceivers", IEEE CICC 1998,
   pp. 335-342. https://doi.org/10.1109/CICC.1998.694994.

.. [PHY-LEE01] C. Lee, B. Razavi, "A 125-MHz mixed-signal echo canceller
   for Gigabit Ethernet on copper wire", IEEE JSSC 36(3):366-373, 2001.
   https://doi.org/10.1109/4.910475.

.. [PHY-YOON00] Yoon, Lee, Jeong, Kim, "An 8-bit 125 MS/s CMOS folding ADC
   for Gigabit Ethernet LSI", Symposium on VLSI Circuits 2000,
   pp. 212-213. https://doi.org/10.1109/VLSIC.2000.852893.

.. [PHY-JIANG08] Jiang, Do, Yeo, Lim, "An 8-bit 200-MSample/s Pipelined ADC
   With Mixed-Mode Front-End S/H Circuit", IEEE TCAS-I 55(6):1430-1440,
   2008. https://doi.org/10.1109/TCSI.2008.916613.

.. [PHY-NTU04] Lin, Chen, Lai, Wu, "1000BASE-T Gigabit Ethernet baseband
   DSP IC design", IEEE ISCAS 2004. https://doi.org/10.1109/ISCAS.2004.1329025.

.. [PHY-OSCAR97] O. Agazzi, M. Hatamian, H. Samueli, "Jitter Specifications
   for 1000Base-T", IEEE 802.3ab, September 1997.
   https://grouper.ieee.org/groups/802/3/ab/public/sept97/oscar2.PDF.

.. [PHY-ED2000] "Gigabit transceiver enables higher-port-density Ethernet
   switches", Electronic Design, 2000-08-01.
   https://www.electronicdesign.com/technologies/industrial/boards/article/21782037/gigabit-transceiver-enables-higher-port-density-ethernet-switches.
   Marvell Alaska 88E1000: 0.18 µm, 10/100/1000, 1.8 W from 3.3 V.

.. [PHY-VSC8244] Microchip (Vitesse), *VSC8244 Quad 10/100/1000BASE-T PHY*
   datasheet, VMDS-10108.
   https://ww1.microchip.com/downloads/en/DeviceDoc/VMDS-10108.pdf.
   0.13 µm, 640 mW per port; section 13 describes transformer-free
   operation with capacitor coupling on backplanes.

.. [PHY-GF180PDK] GlobalFoundries and Google, *gf180mcu PDK documentation*:
   electrical parameters specification and design manual.
   https://gf180mcu-pdk.readthedocs.io/ (source:
   https://github.com/google/gf180mcu-pdk, ``docs/analog/spice/elec_specs``
   and ``docs/physical_verification/design_manual``).

.. [PHY-GF180SC] GlobalFoundries, gf180mcu standard-cell libraries
   ``gf180mcu_fd_sc_mcu7t5v0`` and ``gf180mcu_fd_sc_mcu9t5v0``: cell
   netlists and Liberty timing files.
   https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_sc_mcu7t5v0
   and https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_sc_mcu9t5v0.

.. [PHY-GF180IO] GlobalFoundries, gf180mcu I/O library
   ``gf180mcu_fd_io`` documentation.
   https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_io.
