Integrating the transceiver on evampire
=======================================

The full design of evampire contains the whole Ethernet transceiver for each
port on the chip, and connects to the cable without coupling transformers.
This page sets out, for each Ethernet speed, what evampire must implement to
do that, and assesses how far each speed can be built in the gf180mcu
process. It builds on the explanation in :doc:`../phy-electrical`. The
circuits that replace the coupling transformers are described in
:doc:`../magnetics`; where a result here depends on them, this page links
there.

Three kinds of value appear on this page, and each is labelled:

Required
   A limit from the IEEE 802.3 standard, taken from the conformance test
   documents that quote it ([PHY-UNH14]_, [PHY-UNH25]_, [PHY-UNH40]_,
   [PHY-UNH28]_).

Published
   A measured or reported result from a paper, presentation or datasheet,
   with its source.

Estimate
   A number calculated on this page from required or published values. Each
   estimate states its assumptions. Estimates are not requirements.

.. contents:: On this page
   :local:
   :depth: 2

The interface to the forwarding logic
-------------------------------------

The forwarding logic exchanges one byte per clock cycle with each port, plus
a "frame in progress" flag and an "error" flag in each direction (see
:doc:`../../architecture/index`). An integrated transceiver presents exactly
this interface, so the forwarding logic is the same in the first version and
in the full design.

At 1000 Mbit/s a byte moves every 8 ns, one per cycle of a 125 MHz clock.
In the receive direction the bytes are timed by the clock recovered from the
cable, as they are with RGMII, and the existing rate-matching buffer moves
them onto evampire's own 125 MHz clock. At 100 Mbit/s a byte moves every
80 ns, and at 10 Mbit/s every 800 ns; how those rates are carried on the
byte interface is listed under `Open design questions`_.

What every speed needs
----------------------

Some blocks are needed whichever speeds are supported.

Autonegotiation
~~~~~~~~~~~~~~~

Autonegotiation (explained in :doc:`../phy-electrical`) is required for
1000BASE-T and is what lets a port choose its speed automatically. It is
built from:

* a **link pulse transmitter**: single pulses about 100 ns wide, in bursts
  of 17 to 33 pulses with clock pulses 125 µs ± 14 µs apart, bursts
  repeated every 16 ms ± 8 ms (required, [PHY-UNH28]_). Each pulse is a
  10BASE-T link pulse, so the line driver must be able to produce one even
  if 10BASE-T itself is not supported;
* a **link pulse receiver**: a comparator with a threshold, and timers that
  check pulse spacing;
* three **state machines** defined in IEEE 802.3 Clause 28: the transmit
  state diagram (Figure 28-16), the receive state diagram (Figure 28-17) and
  the arbitration state diagram (Figure 28-18) [PHY-UNH28]_;
* **timers** with the required ranges below;
* for 1000BASE-T, the **next page** exchange carrying the 1000BASE-T
  abilities, the port type and the 11-bit random seed, and the
  master/slave resolution rules [PHY-UNH28M]_.

.. list-table:: Autonegotiation timers (required, [PHY-UNH28]_ [PHY-UNH14]_)
   :header-rows: 1
   :widths: 40 30 30

   * - Timer
     - Range
     - What it times
   * - Burst spacing
     - 16 ms ± 8 ms
     - Interval between fast link pulse bursts
   * - Pulse spacing within a burst
     - 62.5 µs ± 7 µs
     - Clock pulse to data pulse
   * - Link fail inhibit
     - 750 ms to 1000 ms
     - Time allowed for the chosen speed to report a working link
   * - Break link
     - 1200 ms to 1500 ms
     - Silence before negotiation restarts
   * - Autonegotiation wait
     - 500 ms to 1000 ms
     - Wait before accepting a speed found by parallel detection
   * - Link loss (10BASE-T)
     - 50 ms to 150 ms
     - Time without link pulses before the link is declared down

These timers are long compared with any clock on evampire. A counter that
measures time :math:`T` with a clock of frequency :math:`f_\text{clk}`
needs

.. math::

   N_\text{bits} = \left\lceil \log_2 (T \times f_\text{clk}) \right\rceil

bits, where :math:`\lceil\,\rceil` means rounding up to a whole number.
For the longest timer, :math:`T = 1.5` s, with the 25 MHz reference clock,
:math:`f_\text{clk} = 25 \times 10^{6}` Hz:

.. math::

   T \times f_\text{clk} = 1.5 \times 25 \times 10^{6} = 37.5 \times 10^{6}

   \log_2(37.5 \times 10^{6}) = 25.2

   N_\text{bits} = 26

So every autonegotiation timer fits in a counter of at most 26 bits
(estimate). Autonegotiation is simple digital logic; its only analog parts
are the link pulse driver and comparator.

Management registers
~~~~~~~~~~~~~~~~~~~~

IEEE 802.3 Clause 22 defines a set of 16-bit registers that every
transceiver provides, so that the same software can control any of them
[PHY-8023]_. With an integrated transceiver the processor reads and writes
them directly as on-chip registers; keeping the standard layout lets the
same software drive both the external transceiver of the first version and
the integrated one.

.. list-table:: Standard transceiver registers (IEEE 802.3 Clause 22; the
   same addresses are used by the TI DP83867 [PHY-DP83867]_)
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
     - Extended status (1000 Mbit/s abilities)

Register 9 also selects the four transmitter test modes that 1000BASE-T
conformance testing needs [PHY-UNH40]_; an integrated transceiver must
provide them to be tested.

Reference clock
~~~~~~~~~~~~~~~

Every speed needs a symbol clock that is accurate to within a stated
tolerance (required): ±50 parts per million at 125 MHz for 100BASE-TX
[PHY-UNH25]_ and ±100 parts per million for 1000BASE-T [PHY-UNH40]_. A
quartz crystal meets these easily; commercial transceivers use 25 MHz with
±50 parts per million [PHY-DP83867]_. A phase-locked loop (PLL) multiplies
it to 125 MHz.

Published: a PLL in a 180 nm GlobalFoundries process, made for a
100BASE-TX transceiver, produces 125 MHz from a 25 MHz reference with
4.88 ps rms jitter integrated from 1 kHz to 30 MHz, using 0.044 mm² and
1.6 mA at 1.8 V [PHY-BUHR21]_.

The cable interface
~~~~~~~~~~~~~~~~~~~

Each pair must look like a 100 Ω resistor to the cable, so that signals
arriving from the cable are not reflected back. The standard sets this as a
minimum *return loss* (required): at least 16 dB from 1 MHz to 40 MHz for
1000BASE-T [PHY-UNH40]_, and at least 15 dB from 5 MHz to 10 MHz, measured
against any reference between 85 Ω and 111 Ω, for 10BASE-T [PHY-UNH14]_.

Return loss is the size of the reflection in decibels. The reflection
coefficient :math:`\Gamma` (the reflected voltage divided by the incident
voltage) is

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

   Z_\text{max} = R\,\frac{1 + |\Gamma|}{1 - |\Gamma|}

For 1000BASE-T, :math:`L_\text{RL} = 16` dB and :math:`R = 100` Ω:

.. math::

   |\Gamma| = 10^{-16/20} = 10^{-0.8} = 0.158

   Z_\text{min} = 100 \times \frac{0.842}{1.158} = 72.6\ \Omega

   Z_\text{max} = 100 \times \frac{1.158}{0.842} = 137.7\ \Omega

For 10BASE-T, :math:`L_\text{RL} = 15` dB gives :math:`|\Gamma| = 0.178`.
The termination must meet this against every reference from 85 Ω to
111 Ω, so the tightest bounds come from the two ends: :math:`Z_\text{min}`
with :math:`R = 111` Ω is 77.5 Ω, and :math:`Z_\text{max}` with
:math:`R = 85` Ω is 121.8 Ω.

So the termination of each pair must stay within about 78 Ω to 122 Ω
across frequency, temperature and process (estimate, from the required
return loss). On-chip resistors vary much more than this: the gf180mcu
unsalicided P+ poly resistor ranges from 280 to 420 Ω per square, ±20 %
around its typical value [PHY-GF180PDK]_. The termination therefore needs
trimming or an active termination whose impedance is set by feedback. A
published 180 nm line driver with digital impedance control covers 80 Ω to
130 Ω [PHY-BUHR20B]_.

The cable also carries voltages that are not part of the signal: voltage
common to both wires of a pair, surges, and in the full design Power over
Ethernet. Without transformers, these reach evampire's pins through the
external components described in :doc:`../magnetics`. The common-mode
range, isolation and protection that the line driver and receiver must
withstand are set there. The standard analog pads of gf180mcu contain only
protection diodes [PHY-GF180IO]_, which are sized for short,
energy-limited discharge events rather than for continuous voltage stress.
The line driver and receiver are custom circuits and can use custom
protection structures and higher-voltage or stacked transistors where the
line interface needs them.

10BASE-T
--------

Required performance
~~~~~~~~~~~~~~~~~~~~

.. list-table:: 10BASE-T requirements (required, [PHY-UNH14]_)
   :header-rows: 1
   :widths: 45 55

   * - Quantity
     - Limit
   * - Peak differential output into 100 Ω
     - 2.2 V to 2.8 V (10BASE-Te: 1.54 V to 1.96 V)
   * - Harmonics of an all-ones signal
     - At least 27 dB below the 10 MHz fundamental
   * - Common-mode output voltage
     - Less than 50 mV peak
   * - Output return loss, 5 MHz to 10 MHz
     - At least 15 dB against 85 Ω to 111 Ω
   * - Output short-circuit current
     - At most 300 mA, indefinitely, without damage
   * - Receiver input range
     - 585 mV to 3.1 V, with up to 13.5 ns of timing jitter
   * - Link pulse spacing
     - 16 ms ± 8 ms

Line driver
~~~~~~~~~~~

The hardest 10BASE-T requirement on chip is the output voltage. A driver
whose output impedance matches the 100 Ω line forms a voltage divider with
the line: half of its internal voltage appears across the line. The
internal (open-circuit) voltage must therefore be twice the line voltage:

.. math::

   V_\text{src} = 2\,V_\text{line}

where :math:`V_\text{line}` is the required peak differential voltage on
the line and :math:`V_\text{src}` the peak differential voltage the driver
must generate behind its matching resistance. A differential driver whose
two outputs each swing between 0 V and its supply :math:`V_\text{DD}` can
produce a differential voltage of at most :math:`\pm V_\text{DD}` (one
output at :math:`V_\text{DD}`, the other at 0 V), so it needs

.. math::

   V_\text{DD} \ge V_\text{src} = 2\,V_\text{line}

before allowing for the voltage lost across the output transistors. The
current into the line is :math:`I = V_\text{line} / 100\ \Omega`.

.. list-table:: Line driver needs with a passive matching resistance
   (estimate, from the required output voltages)
   :header-rows: 1
   :widths: 25 25 25 25

   * - Speed
     - :math:`V_\text{line}` (peak)
     - :math:`V_\text{DD}` needed, at least
     - Peak line current
   * - 10BASE-T
     - 2.2 V to 2.8 V
     - 4.4 V to 5.6 V
     - 22 mA to 28 mA
   * - 10BASE-Te
     - 1.54 V to 1.96 V
     - 3.08 V to 3.92 V
     - 15 mA to 20 mA
   * - 100BASE-TX
     - 0.95 V to 1.05 V
     - 1.9 V to 2.1 V
     - 10 mA
   * - 1000BASE-T
     - 1 V (2 V peak-to-peak launch level, [PHY-TUT98]_)
     - 2.0 V
     - 10 mA

So the 3.3 V transistors of gf180mcu are enough for 100BASE-TX and
1000BASE-T, but a passively matched driver for full-amplitude 10BASE-T
needs a supply of at least 4.4 V, and 10BASE-Te needs 3.1 V to 3.9 V with
no headroom at 3.3 V. Commercial transceivers avoid this with the
transformer: a current-mode driver with its centre tap at the supply can
swing each pin above the supply (see :doc:`../phy-electrical`). The
transformer-free design cannot use that.

Two published ways round the limit, and one process option:

* **Active termination.** A driver with a low real output impedance can
  use feedback to *present* 100 Ω to the line while dropping less voltage
  internally. Published: a 180 nm class-AB voltage-mode driver with
  digital impedance control produced a 10BASE-T Manchester signal of about
  2.5 V amplitude from a 3.3 V supply, at 62 mW, and 100BASE-TX at 24.3 mW
  from 2.5 V; its area including its DAC and control is 0.16 mm²
  [PHY-BUHR21]_ [PHY-BUHR20B]_. A 0.4 µm current-feedback driver delivered
  a 10 MHz, 5 V peak-to-peak sine wave into 50 Ω from a 3.3 V supply with
  -43 dB total harmonic distortion, at 25 mW quiescent power and 0.15 mm²
  [PHY-BABANEZHAD99]_. Both were measured with coupling transformers.
* **Higher-voltage transistors.** gf180mcu has 5 V and 6 V transistors and
  10 V drain-extended (LDMOS) transistors [PHY-GF180PDK]_ (see
  `Physical limits of the process`_), which allow a supply above 4.4 V.

The 10 MHz signal and 27 dB harmonic limit need only modest linearity; a
pulse-shaping DAC of a few levels at a few times 10 MHz, as in published
10/100 transmitters ([PHY-SHOAEI99]_: 10BASE-T wave-shaping driver, 200 mW
from 5 V in 0.35 µm), meets it.

Receiver and clock recovery
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The receiver must accept 585 mV to 3.1 V and reject small noise (a
threshold of about 300 mV is used in the KSZ9031 [PHY-KSZ9031]_). Its
input range must therefore reach at least 3.1 V differential without
damage or saturation that corrupts timing. Manchester data has a
transition in the middle of every bit, and the receiver may see the
transitions displaced by up to 13.5 ns, which is

.. math::

   \frac{13.5\ \text{ns}}{100\ \text{ns}} = 0.135

of a 100 ns bit. A comparator followed by digital clock recovery that
samples the comparator output several times per bit, or a PLL locking to
the transitions, meets this (estimate). No ADC or equalizer is needed for
10BASE-T.

Assessment
~~~~~~~~~~

10BASE-T needs no ADC and no signal processing beyond decoding. Its one
demanding block is the line driver, whose transformer-free output must
reach 2.2 V to 2.8 V peak while matching 100 Ω. A published 180 nm driver
reaches about 2.5 V from 3.3 V with active termination, and the process
offers 5 V and 6 V transistors. 10BASE-T is therefore feasible with custom
design (estimate); the risk is concentrated in the line driver and its
protection.

100BASE-TX
----------

Required performance
~~~~~~~~~~~~~~~~~~~~

.. list-table:: 100BASE-TX requirements (required, [PHY-UNH25]_)
   :header-rows: 1
   :widths: 45 55

   * - Quantity
     - Limit
   * - Peak differential output into 100 Ω
     - 0.95 V to 1.05 V
   * - Symmetry of positive and negative peaks
     - 98 % to 102 %
   * - Rise and fall time (10 % to 90 %)
     - 3 ns to 5 ns, matched within 0.5 ns
   * - Overshoot
     - At most 5 %
   * - Duty cycle distortion
     - At most 0.5 ns peak-to-peak
   * - Transmit jitter
     - At most 1.4 ns peak-to-peak
   * - Transmit clock
     - 125 MHz ± 6.25 kHz (±50 parts per million)

Line driver
~~~~~~~~~~~

The output is three-level MLT-3 at ±1 V, which a 3.3 V driver can produce
with a passive matching resistance (table above). The edges must be slowed
on purpose: a rise time between 3 ns and 5 ns corresponds, for a
single-pole response, to a bandwidth of

.. math::

   f_\text{3dB} = \frac{0.35}{t_\text{r}}

where :math:`t_\text{r}` is the 10 % to 90 % rise time and 0.35 is the
constant of a single-pole (first-order) response. For
:math:`t_\text{r} = 5` ns this is :math:`0.35 / 5\ \text{ns} = 70` MHz;
for :math:`t_\text{r} = 3` ns it is 117 MHz. The driver must therefore
have a controlled bandwidth (or a few-level edge-shaping DAC) in that
range, and the ±2 % symmetry calls for matched positive and negative
halves (estimate).

Published: a 180 nm GlobalFoundries voltage-mode line driver with series
matching resistors uses 24 mW and 0.13 mm² [PHY-BUHR21]_ [PHY-BUHR18]_; a
180 nm current-mode driver that includes its DAC uses 38 mW
[PHY-RICHTER14]_.

Receiver
~~~~~~~~

At 31.25 MHz, the highest MLT-3 fundamental, a 100 m channel loses 13 dB
(see :doc:`../phy-electrical`), and the loss grows with frequency, so the
receiver needs an adaptive equalizer and baseline wander correction. Two
published approaches:

* **Analog equalizer and comparators.** A continuous-time equalizer
  restores the waveform, and five comparators decide the symbol: two at
  ±0.1 V for the data, three more for adaptation. No ADC is needed.
  Published, 180 nm GlobalFoundries: the equalizer (a transconductor and
  capacitor filter built from three first-order high-pass sections, with
  baseline wander compensation) uses 4.3 mW at 100 m of cable, and the
  receiver works without errors up to 120 m [PHY-BUHR21]_ [PHY-BUHR20A]_.
* **ADC and digital equalizer.** The 802.3ab tutorial lists a 100BASE-TX
  receiver with an ADC of 5.5 bits ideal resolution at 125 million samples
  per second, an 8-tap feed-forward and a 10-tap decision-feedback
  equalizer [PHY-TUT98]_. A digital 10/100 transceiver in 0.18 µm at 1.8 V
  used 6.6 mm² and 350 mW [PHY-HUSS01]_.

Clock recovery
~~~~~~~~~~~~~~

The receiver must sample each 8 ns symbol at a fixed point, using a clock
recovered from the transitions. Published, 180 nm GlobalFoundries: a PLL
generating 125 MHz with a phase interpolator, which selects one of 256
phases, :math:`8\ \text{ns} / 256 = 31.25` ps apart; the digital part of
the clock recovery uses 204 standard cells and 0.016 mm², and the PLL plus
phase interpolator use 0.065 mm² and 4.0 mW [PHY-BUHR21]_.

Assessment
~~~~~~~~~~

A complete 100BASE-TX transceiver has been built and measured in a 180 nm
GlobalFoundries process: 2.6 mm², at most 69 mW, error-free over 100 m of
Category 5 cable [PHY-BUHR21]_ [PHY-BUHR19]_. It used coupling
transformers and 1.8 V transistors for most of its analog blocks. gf180mcu
has no 1.8 V transistor (its smallest is the 3.3 V transistor with
0.28 µm minimum length [PHY-GF180PDK]_), so this design cannot be copied
directly, but the block-level performance needed is shown to be reachable
in 180 nm. 100BASE-TX is feasible with custom design (estimate); the main
risks are the transformer-free line interface and porting the analog
blocks to 3.3 V transistors.

1000BASE-T
----------

Required performance
~~~~~~~~~~~~~~~~~~~~

.. list-table:: 1000BASE-T requirements (required, [PHY-UNH40]_)
   :header-rows: 1
   :widths: 45 55

   * - Quantity
     - Limit
   * - Peak output in test mode 1
     - 0.67 V to 0.82 V; peaks matched within 1 %
   * - Droop in test mode 1
     - Output keeps more than 73.1 % of its peak value
   * - Peak distortion in test mode 4
     - Less than 10 mV for at least 60 % of the symbol period
   * - Common-mode output
     - Less than 50 mV peak-to-peak
   * - Return loss, 1 MHz to 40 MHz
     - At least 16 dB
   * - Transmit clock jitter, unfiltered
     - Less than 1.4 ns peak-to-peak
   * - Transmit clock jitter, filtered
     - Less than 0.3 ns (master), 0.4 ns (slave) peak-to-peak
   * - Transmit clock frequency
     - 125 MHz ± 12.5 kHz (±100 parts per million)
   * - Bit error rate over the worst-case channel
     - Better than :math:`10^{-10}`

Transmitter
~~~~~~~~~~~

The distortion limit sets the transmitter's linearity. The worst error at
any symbol must stay below 10 mV, against a peak of about 0.745 V
[PHY-DP83867]_, that is :math:`0.010 / 0.745 = 1.3\,\%` of the peak.
An ideal digital-to-analog converter (DAC) with :math:`N` bits spanning
:math:`\pm V_\text{pk}` has steps of :math:`2V_\text{pk}/2^N` and a worst
rounding error of half a step:

.. math::

   e_\text{max} = \frac{V_\text{pk}}{2^N}

where :math:`e_\text{max}` is the largest error in V and
:math:`V_\text{pk} = 0.745` V. Requiring :math:`e_\text{max} < 10` mV:

.. math::

   2^N > \frac{0.745}{0.010} = 74.5

   N > \log_2 74.5 = 6.2

so the DAC and line driver together need at least 7 bits of linearity
(estimate, counting rounding error only; for 7 bits,
:math:`e_\text{max} = 0.745 / 128 = 5.8` mV, leaving 4 mV for all other
errors). The 17 shaped levels of PAM-5 (see :doc:`../phy-electrical`) need
at least 5 bits of DAC resolution, so linearity, not the number of levels,
sets the DAC. The 802.3ab design point used a 17-level DAC at 125 MHz and a
2 V peak-to-peak launch level [PHY-TUT98]_.

Echo removal and the receiver's input range
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The receiver sees its own transmission at full size while the far-end
signal may be reduced to 6 % of its voltage at 100 MHz (24 dB; see
:doc:`../phy-electrical`). The hybrid and the echo canceller must remove
the difference. Published figures:

* The 802.3ab design point used an ADC with a 2.2 V peak-to-peak input
  range [PHY-TUT98]_, slightly above the 2 V peak-to-peak launch level, so
  the hybrid is expected to leave the ADC input no larger than the
  transmitted signal.
* A 0.4 µm mixed-signal echo canceller with four analog taps in front of
  the ADC gave 10 dB of echo suppression at 125 MHz, 43 mW from 3 V, in
  about 1 mm²; its authors state that 1000BASE-T requires at least a 7-bit
  ADC and that 8 bits may be needed in practice [PHY-LEE01]_.

Without transformers, the hybrid works on the capacitor-coupled pins (see
:doc:`../magnetics`), and its balance depends on how well the on-chip
replica network matches the line and the external components. How much
echo rejection the analog hybrid must achieve before the digital echo
canceller is an open question.

ADC
~~~

Each of the four pairs needs an analog-to-digital converter (ADC) running
at the 125 MHz symbol rate. For an ideal :math:`N`-bit converter, the
ratio of a full-scale sine wave to the rounding noise is

.. math::

   \text{SQNR} = 6.02\,N + 1.76\ \text{dB}

where SQNR is the signal-to-quantisation-noise ratio. A real converter is
described by its *effective number of bits* (ENOB), found by putting its
measured signal-to-noise-and-distortion ratio (SNDR) into the same
formula:

.. math::

   \text{ENOB} = \frac{\text{SNDR} - 1.76}{6.02}

.. list-table:: ADC resolution for 1000BASE-T
   :header-rows: 1
   :widths: 45 20 35

   * - Source
     - Bits
     - SQNR or SNDR
   * - 802.3ab design point, ideal [PHY-TUT98]_
     - 6.5
     - :math:`6.02 \times 6.5 + 1.76 = 40.9` dB
   * - 802.3ab comparison table, ideal [PHY-TUT98]_
     - 7
     - :math:`6.02 \times 7 + 1.76 = 43.9` dB
   * - 8-bit 125 MS/s folding ADC for Gigabit Ethernet, 0.35 µm, 110 mW,
       0.8 mm² [PHY-YOON00]_
     - 6.4 ENOB
     - :math:`6.02 \times 6.4 + 1.76 = 40.3` dB
   * - 8-bit 200 MS/s pipelined ADC, 0.18 µm, 22 mW at 1.8 V
       [PHY-JIANG08]_
     - 7.2 ENOB
     - 45 dB measured; :math:`(45 - 1.76)/6.02 = 7.2`

So the ADC needs an ENOB of about 6.5 to 7 at 125 million samples per
second (estimate, from the design points), and ADCs with that performance
have been published in 0.35 µm and 0.18 µm processes. Four are needed per
port, eight for evampire's two ports.

Signal processing
~~~~~~~~~~~~~~~~~

:doc:`../phy-electrical` derives the arithmetic rate: about 880 filter
taps, :math:`1.1 \times 10^{11}` multiply-and-add operations per second,
for the 802.3ab design point. A published Broadcom analysis gives "over 150
Giga operations per second" for the DSP portion [PHY-HATAMIAN98]_. Two
facts reduce the cost:

* The echo and near-end crosstalk cancellers multiply a coefficient by a
  transmitted symbol, which is one of -2, -1, 0, +1, +2 (or one of 17
  shaped levels). Multiplying by these needs only a shift, a negation or
  zero, not a general multiplier.
* Only the feed-forward equalizer multiplies full ADC samples.

The hardest timing path is the loop formed by the decision-feedback
equalizer and the trellis decoder, which must complete within one 8 ns
symbol period [PHY-TUT98]_. A published 0.25 µm, 2.5 V standard-cell
1000BASE-T DSP has a 7.48 ns critical path in a 4.54 mm × 4.54 mm chip
[PHY-NTU04]_.

**Area (estimate).** The 802.3ab tutorial estimated 330,000 gates for its
design point and about 400,000 gates in its layout study [PHY-TUT98]_.
Taking one gate as one 2-input NAND gate, the standard-cell area is

.. math::

   A_\text{DSP} = \frac{N_\text{gates} \times A_\text{NAND2}}{u}

where:

* :math:`N_\text{gates}` = 330,000 to 400,000 (from [PHY-TUT98]_);
* :math:`A_\text{NAND2}` = 10.976 µm², the area of the smallest 2-input
  NAND in the gf180mcu 7-track library (14.112 µm² in the 9-track library)
  [PHY-GF180SC]_;
* :math:`u` = 0.7, the fraction of the core area filled by cells
  (an assumption; typical placement densities lie around this value).

For 330,000 gates in the 7-track library:

.. math::

   330{,}000 \times 10.976\ \mu\text{m}^2 = 3.62\ \text{mm}^2

   \frac{3.62}{0.7} = 5.2\ \text{mm}^2

and for 400,000 gates, :math:`4.39 / 0.7 = 6.3` mm². With the 9-track
library the range is 6.7 mm² to 8.1 mm². So the 1000BASE-T DSP for one
port needs roughly 5 mm² to 8 mm² (estimate; it assumes the gate count of
a 1998 design point carries over unchanged), and two ports twice that.

**Speed (estimate).** The gf180mcu standard cells are built from the 5 V
transistors, with 0.6 µm (n-channel) and 0.5 µm (p-channel) gate lengths,
even when run from 3.3 V [PHY-GF180SC]_. The time left for logic in one
8 ns cycle is

.. math::

   t_\text{logic} = T - t_\text{clk-Q} - t_\text{setup}

where :math:`T = 8` ns, and :math:`t_\text{clk-Q}` and
:math:`t_\text{setup}` are the flip-flop's clock-to-output delay and setup
time. Dividing by the delay of one full-adder carry stage
:math:`t_\text{carry}` gives how many such stages fit:

.. list-table:: Logic per 125 MHz cycle with gf180mcu standard cells
   (flip-flop ``dffq_1`` and full adder ``addf_1``, input slew 0.287 ns,
   load 0.0122 pF, worst of rise and fall [PHY-GF180SC]_; estimate)
   :header-rows: 1
   :widths: 28 18 14 18 22

   * - Library and corner
     - :math:`t_\text{clk-Q}` + :math:`t_\text{setup}`
     - :math:`t_\text{logic}`
     - :math:`t_\text{carry}`
     - Carry stages per cycle
   * - 7-track, typical, 3.3 V, 25 °C
     - 1.203 + 0.378 ns
     - 6.42 ns
     - 1.023 ns
     - 6.3
   * - 7-track, slow, 3.0 V, 125 °C
     - 2.380 + 0.848 ns
     - 4.77 ns
     - 2.057 ns
     - 2.3
   * - 9-track, slow, 4.5 V, 125 °C
     - 1.127 + 0.373 ns
     - 6.50 ns
     - 1.028 ns
     - 6.3
   * - 9-track, typical, 5.0 V, 25 °C
     - 0.645 + 0.187 ns
     - 7.17 ns
     - 0.581 ns
     - 12.3

In the slowest 3.3 V-class corner only about two full-adder stages fit in a
cycle. The filters can be pipelined and split into parallel paths without
limit, but the decision-feedback and trellis-decoder loop cannot simply be
pipelined; it needs look-ahead or parallel decoder structures, the 9-track
library at a higher supply, or custom cells built from the faster 3.3 V
transistors (no such library is part of the standard PDK).

**Power (estimate).** The 802.3ab layout study gives 3.1 W at 2.5 V in
0.25 µm [PHY-TUT98]_. Dynamic power scales with the square of the supply
voltage for the same switched capacitance:

.. math::

   P_{3.3} = P_{2.5} \times \left(\frac{3.3}{2.5}\right)^2
   = 3.1\ \text{W} \times 1.74 = 5.4\ \text{W}

This assumes the gf180mcu design switches the same capacitance as the 1998
design; the larger 5 V transistors of the gf180mcu cells would raise it,
while later algorithmic improvements would lower it. Published 0.18 µm and
0.13 µm commercial transceivers use 1.8 W for a
whole single-port 10/100/1000 chip ([PHY-ED2000]_, Marvell 88E1000) and
about 0.64 W per port ([PHY-VSC8244]_). The DSP power of a 1000BASE-T port
on gf180mcu is therefore likely to be measured in watts (estimate), which
also has to be considered against the power budget of a board that may be
powered over the cable (see :doc:`../../power/index`).

Clock recovery and master/slave timing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The slave recovers the master's clock and transmits with it; the master
transmits with its own crystal clock and recovers the slave's phase for its
receiver. The required jitter limit of 1.4 ns peak-to-peak is

.. math::

   \frac{1.4\ \text{ns}}{8\ \text{ns}} = 0.175

of a symbol period, with tighter limits of 0.3 ns (master) and 0.4 ns
(slave) after high-pass filtering [PHY-UNH40]_. Broadcom's 1997 jitter
analysis describes clock recovery by phase interpolation of a crystal
oscillator; as an example it takes 64 phases per symbol, giving steps of
:math:`8\ \text{ns}/64 = 125` ps, and states that a 125 ps step causes
tolerable degradation in PAM-5 [PHY-OSCAR97]_. The published 180 nm PLL
and 256-phase interpolator described for 100BASE-TX [PHY-BUHR21]_ has
finer steps, :math:`8\ \text{ns}/256 = 31.25` ps, and 4.9 ps rms jitter.

To compare an rms jitter :math:`\sigma` with a peak-to-peak limit, assume
the jitter has a Gaussian distribution. The peak-to-peak value that is
exceeded with probability :math:`10^{-12}` is

.. math::

   J_\text{pp} = 2\,Q\,\sigma

where :math:`Q = 7.03` is the number of standard deviations at which the
Gaussian tail probability is :math:`10^{-12}`. With
:math:`\sigma = 4.9` ps:

.. math::

   J_\text{pp} = 2 \times 7.03 \times 4.9\ \text{ps} = 14.06 \times 4.9\ \text{ps}
   = 69\ \text{ps}

(estimate), about 20 times below the 1.4 ns limit, so PLL jitter of this
quality leaves the jitter budget to the rest of the clock path.

Assessment
~~~~~~~~~~

No physical limit found in the gf180mcu documentation rules out
1000BASE-T. 1000BASE-T transceivers have been published in 0.18 µm CMOS
([PHY-HE01]_, a DSP receiver; [PHY-ED2000]_, a complete 10/100/1000 chip),
and each analog block (ADC, DAC and line driver, echo canceller, PLL) has a
published 0.18 µm to 0.4 µm counterpart with the needed performance. The
0.18 µm designs whose supply is stated used 1.8 V logic ([PHY-HUSS01]_,
[PHY-BUHR21]_, [PHY-JIANG08]_), and the 0.13 µm one 1.2 V ([PHY-VSC8244]_);
gf180mcu has no 1.8 V or 1.2 V transistor, and its standard cells use 5 V
transistors.

1000BASE-T on gf180mcu is therefore possible only with substantial custom
design, and is the hardest speed by a wide margin (estimate). The main
risks, in order:

1. Power and area of the DSP: several square millimetres and probably
   watts per port with the standard cells.
2. Timing of the decision-feedback and trellis-decoder loop in 8 ns with
   the standard cells' 5 V transistors.
3. Four 125 MHz ADCs of about 7 effective bits per port, built from 3.3 V
   transistors.
4. Hybrid and echo rejection through the transformer-free line interface.

Physical limits of the process
------------------------------

This section separates three kinds of limit.

Ratings and speed of the standard cells
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The standard-cell libraries are characterised conservatively and are the
starting point for the DSP estimates above [PHY-GF180SC]_:

* Both libraries (7-track, 3.92 µm rows; 9-track, 5.04 µm rows) use 5 V
  transistors, characterised at 1.8 V, 3.3 V and 5 V corners.
* Flip-flop minimum period: 1.54 ns to 1.71 ns (7-track, typical, 3.3 V);
  3.10 ns to 3.56 ns (7-track, slow, 3.0 V, 125 °C).
* The general-purpose I/O cells run at 100 MHz into 30 pF (fast slew,
  16 mA) from a 5 V I/O supply; analog pads contain only protection
  diodes [PHY-GF180IO]_.

Devices and their physical limits
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From the gf180mcu PDK electrical specifications and design manual
[PHY-GF180PDK]_:

.. list-table:: gf180mcu transistors (typical values)
   :header-rows: 1
   :widths: 22 14 18 22 24

   * - Device
     - Gate length
     - Threshold voltage
     - Saturation current, W/L = 10 µm/min
     - Breakdown
   * - 3.3 V n-channel
     - 0.28 µm
     - 0.63 V
     - 510 µA/µm at 3.3 V
     - Gate oxide 7 V minimum; drain 7 V to 9 V
   * - 3.3 V p-channel
     - 0.28 µm
     - -0.73 V
     - 250 µA/µm at 3.3 V
     - Gate oxide 7 V minimum
   * - 5 V n-channel
     - 0.6 µm
     - 0.70 V
     - 500 µA/µm at 5 V
     - Gate oxide 12 V minimum (6 V gate)
   * - 6 V n-channel
     - 0.7 µm
     - 0.73 V
     - 570 µA/µm at 6 V
     - Gate oxide 12 V minimum
   * - 10 V drain-extended n-channel (LDMOS), characterised device
     - 0.6 µm
     - 0.84 V
     - 535 µA/µm (gate 6 V, drain 10 V)
     - Drain 13.2 V minimum

Other devices: MIM capacitors (one of 1.0, 1.5 or 2.0 fF/µm² per process,
up to 20 V for the 1.0 fF/µm² option), polysilicon resistors from about
7 Ω to 3000 Ω per square, vertical NPN and PNP transistors, Schottky
diodes, and 2 to 6 metal layers with optional thick top metal.

Not documented: the transition frequency (:math:`f_\text{T}`), maximum
oscillation frequency and transconductance efficiency (:math:`g_m/I_D`) of
any transistor, and any inductor model. These matter for the 125 MHz ADC,
DAC and line driver, and must be obtained by simulation with the PDK models
or by measurement.

What custom circuits have reached
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Published Ethernet transceivers and blocks in 0.18 µm to
   0.6 µm CMOS
   :header-rows: 1
   :widths: 34 14 52

   * - Design
     - Process
     - Result
   * - 100BASE-TX transceiver [PHY-BUHR21]_ [PHY-BUHR19]_
     - 180 nm GF
     - 2.6 mm², at most 69 mW, error-free to 100 m (measured)
   * - 10/100 transceiver, digital receiver [PHY-HUSS01]_
     - 0.18 µm, 1.8 V
     - 6.6 mm², 350 mW
   * - 10/100 transceiver, mixed-signal [PHY-EVERITT98]_
     - 0.6 µm, 5 V
     - 23 mm², 850 mW
   * - 1000BASE-T DSP receiver [PHY-HE01]_
     - 0.18 µm
     - 6 dB coding gain trellis decoder at 125 MBaud
   * - 10/100/1000 single-port chip [PHY-ED2000]_
     - 0.18 µm
     - 1.8 W from 3.3 V (trade press)
   * - Analog echo canceller, 4 taps [PHY-LEE01]_
     - 0.4 µm
     - 10 dB suppression, 43 mW, about 1 mm²
   * - 8-bit 125 MS/s ADC [PHY-YOON00]_
     - 0.35 µm
     - 6.4 ENOB, 110 mW, 0.8 mm²
   * - 8-bit 200 MS/s ADC [PHY-JIANG08]_
     - 0.18 µm
     - 45 dB SNDR, 22 mW
   * - Line driver, active impedance [PHY-BUHR20B]_
     - 180 nm
     - 80 Ω to 130 Ω, 200 MHz bandwidth, 24.3 mW
   * - PLL and phase interpolator [PHY-BUHR21]_
     - 180 nm GF
     - 125 MHz, 4.9 ps rms, 4.0 mW, 0.065 mm²

Summary by speed
----------------

.. list-table:: Feasibility of each speed on gf180mcu (estimate)
   :header-rows: 1
   :widths: 16 34 50

   * - Speed
     - Conclusion
     - Hardest part
   * - 10BASE-T
     - Feasible with custom design
     - Transformer-free line driver reaching 2.2 V to 2.8 V peak while
       matching 100 Ω; needs active termination or 5 V/6 V transistors
   * - 100BASE-TX
     - Feasible with custom design; demonstrated in 180 nm
     - Transformer-free line interface; analog equalizer and clock
       recovery with 3.3 V transistors
   * - 1000BASE-T
     - Possible only with substantial custom design; highest risk
     - DSP power, area and loop timing with 5 V standard cells; four
       125 MHz ADCs per port; hybrid without transformers

Blocks evampire would need
--------------------------

The blocks are listed in the order in which they depend on each other, with
what can be verified on its own first. Blocks marked 10, 100 or 1000 are
needed only for that speed.

1. **Reference clock and PLL** (all speeds): crystal oscillator at 25 MHz,
   PLL to 125 MHz. Verified alone by measuring frequency and jitter.
2. **Line interface and termination** (all speeds): trimmed or active
   100 Ω termination, protection, connection to the external components of
   :doc:`../magnetics`. Verified alone by return-loss measurement.
3. **Link pulse driver and comparator, autonegotiation logic and
   management registers** (all speeds): verified against a commercial
   transceiver, which will report the abilities it receives.
4. **10BASE-T driver and receiver, Manchester coding** (10): verified
   against a commercial transceiver and the 10BASE-T output template.
5. **100BASE-TX driver, MLT-3 coding, 4B5B coding and scrambler** (100):
   the transmit side can be verified alone, against the output limits,
   before the receiver exists.
6. **100BASE-TX equalizer, baseline wander correction, comparators and
   clock recovery** (100): verified with cables of several lengths.
7. **1000BASE-T DAC and line driver** (1000): verified alone with the four
   transmitter test modes, which need no receiver.
8. **1000BASE-T ADC and hybrid** (1000): verified alone by capturing
   samples while transmitting.
9. **1000BASE-T signal processing** (1000): equalizers, echo and crosstalk
   cancellers, trellis decoder, scramblers and timing recovery. Can be
   developed and checked in simulation and on an FPGA using samples captured
   from block 8, before it is committed to silicon.
10. **Byte interface to the forwarding logic** (all speeds): the same
    interface as the RGMII block, verified with the first-version forwarding
    logic.

Open design questions
---------------------

* Which speeds the integrated transceiver supports. 1000BASE-T requires
  autonegotiation and so link pulses; whether 10BASE-T and 100BASE-TX are
  included changes the line driver and receiver needed.
* How 100 Mbit/s and 10 Mbit/s bytes are carried on the byte interface:
  a byte-enable flag on the 125 MHz clock, or a slower clock.
* Whether 10BASE-T uses active termination from 3.3 V or 5 V/6 V
  transistors, and whether the reduced-amplitude 10BASE-Te is enough.
* Whether link pulses for autonegotiation need full 10BASE-T amplitude. The
  conformance documents used here give the link pulse template's upper
  bound (±3.1 V) but no minimum amplitude; this needs to be checked in
  IEEE 802.3 Clause 14.
* How much echo the analog hybrid must remove before the ADC, given the
  transformer-free connection, and therefore the ADC resolution.
* Whether the 1000BASE-T DSP uses the 5 V-transistor standard cells, a
  higher supply, or custom cells built from 3.3 V transistors, and what its
  power is compared with the board's power budget.
* The :math:`f_\text{T}` and :math:`g_m/I_D` of the gf180mcu transistors,
  which are not documented and set the speed of the analog blocks.
* How the line driver and receiver survive surges, cable discharge and
  Power over Ethernet voltages without transformers, which depends on the
  protection described in :doc:`../magnetics`.
* Whether the 100BASE-TX receiver uses an analog equalizer with
  comparators, or an ADC shared with 1000BASE-T.

References
----------

Standards, conformance documents and datasheets cited on this page, such
as [PHY-8023]_, [PHY-UNH40]_ and [PHY-DP83867]_, are listed on
:doc:`../phy-electrical`.

.. [PHY-BUHR21] S. Buhr, *Energieeffiziente integrierte Schaltungen zur
   Basisbandsignalverarbeitung und Zeitsynchronisation für drahtgebundene
   Ethernet-Echtzeitkommunikation* (energy-efficient integrated circuits
   for baseband signal processing and time synchronisation in wired
   real-time Ethernet), Dr.-Ing. dissertation, TU Dresden, 2021.
   https://tud.qucosa.de/api/qucosa%3A77692/attachment/ATT-0/. 180 nm
   100BASE-TX transceiver: die size, power, line drivers, equalizer,
   comparator receiver, PLL and phase interpolator.

.. [PHY-BUHR19] S. Buhr, X. Xu, M. Kreißig, F. Ellinger, "A Low Power Fast
   Ethernet Physical Layer Transceiver", IEEE ICECS 2019, pp. 478-481.
   doi:10.1109/ICECS46596.2019.8964920.

.. [PHY-BUHR20A] S. Buhr, X. Xu, M. Kreißig, C. Matthus, F. Ellinger, "Low
   power analogue equaliser with adaptive digital tuning for fast
   ethernet", IET Circuits, Devices & Systems 14(5):600-610, 2020.
   doi:10.1049/iet-cds.2019.0370.

.. [PHY-BUHR18] S. Buhr, M. Kreißig, S. Protze, F. Ellinger, "Ultra Low
   Power Class-AB Voltage Mode Line Driver for Fast Ethernet", IEEE MWSCAS
   2018, pp. 17-20. doi:10.1109/MWSCAS.2018.8623924.

.. [PHY-BUHR20B] S. Buhr, M. Kreißig, C. Matthus, S. Protze, F. Ellinger,
   "Low Power Class-AB Line Driver with Adaptive Digital Impedance Control
   for Fast Ethernet", IEEE NorCAS 2020.
   doi:10.1109/NorCAS51424.2020.9265004.

.. [PHY-RICHTER14] A. Richter, C. Tzschoppe, F. Ellinger, "Low power fast
   Ethernet line driver", IEEE ICECS 2014, pp. 52-55.
   doi:10.1109/ICECS.2014.7049919.

.. [PHY-BABANEZHAD99] J. N. Babanezhad, "A 100-MHz, 50-Ω, -45-dB
   distortion, 3.3-V CMOS line driver for Ethernet and fast Ethernet
   networking applications", IEEE JSSC 34(8):1044-1050, 1999.
   doi:10.1109/4.777101.

.. [PHY-SHOAEI99] O. Shoaei, A. Shoval, R. Leonowich, "A dual-speed
   125 Mbaud/10 Mbaud CMOS transmitter for Fast Ethernet", IEEE CICC 1999,
   pp. 257-260. doi:10.1109/CICC.1999.777286.

.. [PHY-HUSS01] S. Huss et al., "A DSP based 10BaseT/100BaseTX Ethernet
   transceiver in a 1.8 V, 0.18 µm CMOS technology", IEEE CICC 2001,
   pp. 135-138. doi:10.1109/CICC.2001.929741.

.. [PHY-EVERITT98] J. Everitt et al., "A CMOS transceiver for 10-Mb/s and
   100-Mb/s Ethernet", IEEE JSSC 33(12):2169-2177, 1998.
   doi:10.1109/4.735701.

.. [PHY-HE01] R. He, N. Nazari, S. Sutardja, "A DSP based receiver for
   1000BASE-T PHY", IEEE ISSCC 2001, pp. 308-309.
   doi:10.1109/ISSCC.2001.912651.

.. [PHY-HATAMIAN98] M. Hatamian et al., "Design considerations for gigabit
   Ethernet 1000Base-T twisted pair transceivers", IEEE CICC 1998,
   pp. 335-342. doi:10.1109/CICC.1998.694994.

.. [PHY-LEE01] C. Lee, B. Razavi, "A 125-MHz mixed-signal echo canceller
   for Gigabit Ethernet on copper wire", IEEE JSSC 36(3):366-373, 2001.
   doi:10.1109/4.910475.

.. [PHY-YOON00] Yoon, Lee, Jeong, Kim, "An 8-bit 125 MS/s CMOS folding ADC
   for Gigabit Ethernet LSI", Symposium on VLSI Circuits 2000,
   pp. 212-213. doi:10.1109/VLSIC.2000.852893.

.. [PHY-JIANG08] Jiang, Do, Yeo, Lim, "An 8-bit 200-MSample/s Pipelined ADC
   With Mixed-Mode Front-End S/H Circuit", IEEE TCAS-I 55(6):1430-1440,
   2008. doi:10.1109/TCSI.2008.916613.

.. [PHY-NTU04] Lin, Chen, Lai, Wu, "1000BASE-T Gigabit Ethernet baseband
   DSP IC design", IEEE ISCAS 2004. doi:10.1109/ISCAS.2004.1329025.

.. [PHY-OSCAR97] O. Agazzi, M. Hatamian, H. Samueli, "Jitter Specifications
   for 1000Base-T", IEEE 802.3ab, September 1997.
   https://grouper.ieee.org/groups/802/3/ab/public/sept97/oscar2.PDF.

.. [PHY-ED2000] "Gigabit transceiver enables higher-port-density Ethernet
   switches", Electronic Design, 2000-08-01.
   https://www.electronicdesign.com/technologies/industrial/boards/article/21782037/gigabit-transceiver-enables-higher-port-density-ethernet-switches.
   Marvell Alaska 88E1000: 0.18 µm, 10/100/1000, 1.8 W from 3.3 V.

.. [PHY-VSC8244] Microchip (Vitesse), *VSC8244 Quad 10/100/1000BASE-T PHY*
   datasheet, VMDS-10108.
   https://ww1.microchip.com/downloads/en/DeviceDoc/VMDS-10108.pdf.
   0.13 µm, 640 mW per port; section 13 describes transformer-free
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
