.. _phy-int-dsp:

Signal processing
=================

This page states what the digital signal processing of one port must do
each 8 ns symbol period, how that depends on cable reach, and the one loop
that must close within a symbol period. It assumes no clock or supply for
the logic: those are options on :doc:`cells`.

.. _phy-int-work:

Work per symbol
---------------

Every 125 MBd symbol period (8 ns, :clause:`40.1.3`), for each of the four
pairs, the receiver evaluates one echo canceller, three near-end crosstalk
cancellers, a feed-forward equaliser and a decision-feedback equaliser, and
takes one step of the trellis decoder. With the 802.3ab tutorial's tap
counts that is 880 taps, or :math:`1.1 \times 10^{11}` multiply-and-adds
per second, plus about as many operations to adapt the coefficients
(:ref:`phy-dsp-rate`). A published Broadcom analysis
gives more than 150 × 10⁹ operations per second for a gigabit transceiver
([PHY-HATAMIAN98]_ abstract).

The logic can meet this at any clock and parallelism whose product gives
880 taps every 8 ns: for example one copy of each filter at 125 MHz, or two
copies at 62.5 MHz, each handling alternate symbols
(:numref:`fig-phy-int-parallel`). Every filter except
the decision loop below can be pipelined and split into parallel paths,
so for them the clock is a trade between area and power,
not a limit.

.. wavedrom::
   :caption: One filter copy at 125 MHz handles every symbol; two copies
             at 62.5 MHz each handle alternate symbols, doing the same
             work per 8 ns.
   :name: fig-phy-int-parallel
   :alt: Timing diagram of symbols n to n+7, one per 8 ns. Row "one copy,
         125 MHz" handles each symbol in its own 8 ns slot. Rows "copy A,
         62.5 MHz" and "copy B, 62.5 MHz" each take 16 ns per symbol: A
         handles n, n+2, n+4 and n+6, and B handles n+1, n+3 and n+5.

   { "signal": [
       { "name": "symbols", "wave": "========", "data": ["n", "n+1", "n+2", "n+3", "n+4", "n+5", "n+6", "n+7"] },
       { "name": "one copy, 125 MHz", "wave": "========", "data": ["n", "n+1", "n+2", "n+3", "n+4", "n+5", "n+6", "n+7"] },
       { "name": "copy A, 62.5 MHz", "wave": "=.=.=.=.", "data": ["n", "n+2", "n+4", "n+6"] },
       { "name": "copy B, 62.5 MHz", "wave": "x=.=.=.=", "data": ["n+1", "n+3", "n+5"] }
     ],
     "config": { "hscale": 2 }
   }

.. _phy-int-reach-taps:

Echo canceller length and reach
-------------------------------

The echo canceller must span the round trip to the furthest reflection it
cancels. The propagation delay of a link segment is at most 570 ns for
100 m (:clause:`40.7.4.1`), at most 5.7 ns per metre, so

.. math::

   N_\text{echo} \le \frac{2\,t_\text{d}\,L}{T}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`N_\text{echo}`
     - Echo canceller taps needed to span the whole cable
     - none
   * - :math:`t_\text{d}`
     - Propagation delay per metre, at most 5.7
     - ns/m
   * - :math:`L`
     - Cable reach
     - m
   * - :math:`T`
     - Symbol period, 8
     - ns

For :math:`L = 100` m, :math:`N_\text{echo} \le 2 \times 5.7 \times 100 / 8
= 143` taps; the tutorial's design point uses 120
([PHY-TUT98]_ slide 51), because reflections from the far end are weakened
twice by the cable. :numref:`tab-phy-int-reach-taps` and
:numref:`fig-phy-int-reach` give the upper bound at other reaches
(estimate). The near-end crosstalk cancellers model
coupling close to the connector and do not scale with reach. The equalisers
correct the cable's spreading, which grows with length, so their tap counts
at 100 m are an upper bound for shorter reach.

.. list-table:: Upper bound on echo canceller taps and total taps by cable
   reach (estimate)
   :name: tab-phy-int-reach-taps
   :header-rows: 1
   :widths: 25 35 40

   * - Reach (m)
     - Echo taps per pair, at most
     - Total taps for 4 pairs, at most
   * - 100
     - 143
     - 972
   * - 50
     - 71
     - 684
   * - 30
     - 43
     - 572
   * - 10
     - 14
     - 456

The total uses 72 near-end crosstalk taps, 16 feed-forward taps and 12
decision-feedback taps per pair at every reach, as at 100 m. Multiplying a
total by :math:`125 \times 10^{6}` per second gives the multiply-and-add
rate; at 30 m it is :math:`572 \times 125 \times 10^{6} = 7.2 \times
10^{10}` per second. Simulation against channel models sets the real tap
counts for each reach.

.. _phy-int-shift-add:

Shift-and-add multiplication
----------------------------

The echo and crosstalk cancellers multiply a coefficient by a transmitted
symbol. A PAM-5 symbol is one of −2, −1, 0, +1 and +2, so the product needs
only a shift, a negation or zero. A shaped level is a multiple of 0.25 from
−2 to +2 (:ref:`phy-shaping`), and every whole number from −8 to +8 is the
sum or difference of at most two powers of two, so each product needs at
most one shift-and-add. Only the feed-forward equaliser multiplies full ADC
samples.

.. _phy-int-adapt-split:

Coefficient adaptation rate
---------------------------

The filters must run every symbol, but their coefficients change slowly:
they track the cable and temperature. One alternative splits the work.
Hardware runs the filters at the symbol rate and collects error terms; the
coefficient updates run :math:`K` times less often, in slower hardware or
in software on the processor. The update rate is then

.. math::

   R_\text{upd} = \frac{N_\text{taps} \times f_\text{sym}}{K}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`R_\text{upd}`
     - Coefficient updates per second
     - s⁻¹
   * - :math:`N_\text{taps}`
     - Taps adapted, 880 for the tutorial's design point
     - none
   * - :math:`f_\text{sym}`
     - Symbol rate, :math:`125 \times 10^{6}` per second
     - s⁻¹
   * - :math:`K`
     - Symbols between updates of one coefficient
     - none

For :math:`K = 1000`, :math:`R_\text{upd} = 880 \times 125 \times 10^{6} /
1000 = 1.1 \times 10^{8}` updates per second, each about one multiply and
one add. During start-up the filters must train before the
*maxwait_timer* expires, 350 ms for a slave (:clause:`40.4.5.2`). In that
time each coefficient gets
:math:`0.35\ \text{s} \times 125 \times 10^{6} / K = 4.4 \times 10^{7} / K`
updates: 44 000 for :math:`K = 1000`. Whether that is enough for the
adaptation to converge, and whether the error terms can be collected
without moving 880 values every few symbols, is open; a simulation of the
training sequence answers it. :numref:`fig-phy-int-adapt-split` shows the
split.

.. graphviz:: adapt-split.dot
   :name: fig-phy-int-adapt-split
   :caption: The filters run every symbol in hardware; an update engine
             changes their coefficients K times less often.
   :alt: Samples enter filters in hardware that run every 8 ns symbol and
         output equalised samples. Error terms go down to an update
         engine, in slower hardware or software, running K times less
         often, which sends new coefficients back, drawn dashed. A note
         gives, for K = 1000, 1.1 × 10^8 updates per second and 44 000
         updates per coefficient in 350 ms.
   :align: center

.. _phy-int-decision-loop:

Decision loop
-------------

The decision-feedback equaliser subtracts the tails of symbols the receiver
has already decided, and the trellis decoder's decisions depend on that
subtraction. Each decision must be complete before the next symbol's
subtraction starts, so this loop must close in one 8 ns symbol period
whatever the clock of the rest of the logic ([PHY-TUT98]_ slides 23 and
33). The loop holds an add-compare-select step, an add, a 5-input select and
the branch-metric computation ([PHY-TUT98]_ slide 33). A common structure
is a parallel decision-feedback decoder, with one decision-feedback
equaliser for each of the 8 decoder states ([PHY-HARATSCH01]_).

*Look-ahead* rewrites the loop: the candidate results for each possible
previous decision are computed outside the loop, where they can be
pipelined, and the loop only selects one ([PHY-PARHI91]_,
:numref:`fig-phy-int-decision-loop`).

.. graphviz:: decision-loop.dot
   :name: fig-phy-int-decision-loop
   :caption: Look-ahead moves the arithmetic out of the decision loop and
             leaves only a selection inside it.
   :alt: Two columns. Left, direct loop: equalised samples, subtract
         feedback, decide symbols, decisions; a red loop runs from the
         decision through the feedback filter back to the subtraction and
         must close in one 8 ns period. Right, with look-ahead: equalised
         samples go to a pipelined block that precomputes candidates for
         each possible past decision, then to a select-and-decide block
         whose red loop only selects.
   :align: center

:numref:`tab-phy-int-loop` lists reference examples.

.. list-table:: Reference examples of gigabit decision loops
   :name: tab-phy-int-loop
   :header-rows: 1
   :widths: 40 25 35

   * - Structure and process
     - Throughput
     - Cost
   * - 14-tap parallel decision-feedback decoder, direct, 0.16 µm 3.3 V
       cells ([PHY-AZADET-PAT]_)
     - about 500 Mbit/s
     - 158 000 gates
   * - The same decoder, pipelined, 0.16 µm 3.3 V cells
       ([PHY-HARATSCH01B]_)
     - 125 MHz
     - extra pipeline registers
   * - Prefilter and 1-tap decoder with look-ahead, 0.25 µm 3.3 V cells
       ([PHY-HARATSCH01]_)
     - 1 Gbit/s at 125 MHz
     - half the gates of the 14-tap decoder; 1.3 dB less noise margin
   * - Pipelined parallel decoder ([PHY-GU07]_)
     - 125 MHz
     - 60 % less hardware overhead than earlier pipelined decoders

From the first and third rows, a look-ahead decoder needs about
:math:`158\,000 / 2 = 79\,000` gates (estimate; the two figures come from
different designs by the same group). Whether a look-ahead loop closes in
8 ns in gf180mcu depends on the cell library and supply
(:ref:`phy-int-logic-depth`); a synthesis and timing analysis for each
option answers it.

.. _phy-int-dsp-questions:

Open questions
--------------

* The cable reach the integrated transceiver supports, and the tap counts
  that simulation gives for it.
* Which decision-loop structure is used, and how many parallel paths the
  rest of the logic uses.
* Whether coefficient adaptation runs every symbol in hardware or less
  often in slower hardware or software, and how the training then meets
  the maxwait_timer.
