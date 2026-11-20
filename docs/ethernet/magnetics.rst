Magnetics and the RJ45 socket
=============================

This page explains how an Ethernet transceiver is connected to the RJ45
socket through coupling transformers, and the role those transformers play.

Every external port of evampire uses three parts between the chip and the
cable: an Ethernet transceiver (see :doc:`phy-electrical`), a set of small
transformers and chokes, and an RJ45 socket. Ethernet documentation and parts
catalogues call the transformers and chokes together the *magnetics*. None of
these parts is inside evampire. This page describes what the magnetics do,
why the Ethernet standard needs them, and what to look for when choosing and
placing them on a board.

The Ethernet standard referred to on this page is IEEE 802.3. The parts of
it that matter here are:

* Clause 14, for 10 Mbit/s over twisted-pair cable (*10BASE-T*);
* Clause 25, for 100 Mbit/s over twisted-pair cable (*100BASE-TX*);
* Clause 40, for 1000 Mbit/s (gigabit) over twisted-pair cable
  (*1000BASE-T*);
* Clauses 33 and 145, for Power over Ethernet.

The connection between the transceiver and the cable is called the *MDI*,
short for "medium dependent interface". In this page "MDI" means the eight
signal wires of the RJ45 socket and the electrical requirements placed on
them.

The cable and the RJ45 socket
-----------------------------

An Ethernet cable contains four *twisted pairs*: four pairs of wires, the two
wires of each pair twisted around each other. Each pair is a balanced
transmission line with a characteristic impedance of 100 Ω. A signal is sent
as a voltage *difference* between the two wires of a pair, and the receiver
looks only at that difference. Because both wires of a pair run along the
same path, interference picked up from outside reaches both wires nearly
equally and does not change the difference.

The RJ45 plug and socket have eight contacts, numbered 1 to 8. The pairs are
not on neighbouring pins throughout: one pair uses pins 3 and 6, which sit on
either side of the pair on pins 4 and 5. This layout comes from older
telephone wiring, where the centre two pins carried the first pair.

.. list-table:: RJ45 pin use. The 1000BASE-T names are those used in IEEE
                802.3 Clause 40; "BI" means the pair carries data in both
                directions at the same time.
   :header-rows: 1
   :widths: 12 18 25 25 20

   * - Pins
     - Pair name (1000BASE-T)
     - 1000BASE-T, MDI
     - 10BASE-T and 100BASE-TX, MDI
     - 10BASE-T and 100BASE-TX, MDI-X
   * - 1, 2
     - A (BI_DA)
     - BI_DA+, BI_DA−
     - transmit +, transmit −
     - receive +, receive −
   * - 3, 6
     - B (BI_DB)
     - BI_DB+, BI_DB−
     - receive +, receive −
     - transmit +, transmit −
   * - 4, 5
     - C (BI_DC)
     - BI_DC+, BI_DC−
     - not used
     - not used
   * - 7, 8
     - D (BI_DD)
     - BI_DD+, BI_DD−
     - not used
     - not used

At 10 Mbit/s and 100 Mbit/s only two pairs are used: one carries data in
each direction. At 1000 Mbit/s all four pairs are used, and each pair
carries data in both directions at the same time; the transceiver separates
its own transmitted signal from the received one (see :doc:`phy-electrical`).
The magnetics therefore have four identical channels, one per pair, even if a
board only ever runs at 100 Mbit/s.

Crossover and automatic crossover
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At 10 and 100 Mbit/s a transmitter at one end of the cable must reach the
receiver at the other end. With an ordinary "straight-through" cable (pin 1
to pin 1, pin 2 to pin 2, and so on), this works only if the two ends use
opposite pin assignments. The standard assignment, used by computers, is
called *MDI*. The swapped assignment, traditionally used by hubs and
switches, is called *MDI-X* ("X" for crossed). Two ports of the same kind
need a *crossover cable*, in which the pairs on pins 1, 2 and 3, 6 are
swapped.

.. _fig-magnetics-crossover:

.. graphviz:: magnetics/crossover.dot
   :caption: MDI and MDI-X at 10 and 100 Mbit/s. With a straight-through
             cable, the transmitter at one end reaches the receiver at the
             other end only if one port uses MDI and the other MDI-X.
   :align: center

At 1000 Mbit/s the MDI-X assignment swaps pair A with pair B, and pair C with
pair D (Table 3-1 of the Microchip KSZ9031RNX data sheet lists the full
mapping).

Many transceivers, including the KSZ9031RNX, choose between MDI and MDI-X
by themselves, so that either kind of cable works. IEEE 802.3 Clause 40.4.4 defines this *automatic MDI/MDI-X
configuration* (often shortened to "auto-MDIX"). While no link is
established, the port listens for the start-up pulses sent by the other end.
At intervals of about 62 ms it decides, using a pseudo-random bit sequence,
whether to stay with its present assignment or swap. The randomness stops two
identical ports from swapping in step forever. Once one port hears the other,
it stops swapping. At 1000 Mbit/s the transceiver also corrects pairs that
are swapped or whose two wires are reversed, as part of normal start-up.

For the magnetics this means that the transmit and receive paths must be
identical, because either pair may end up carrying either direction. The
KSZ9031RNX data sheet recommends "an isolation transformer with symmetrical
transmit and receive data paths" for this reason. Magnetics sold for gigabit
use have four identical channels and meet this.

One port, wire by wire
----------------------

:numref:`fig-magnetics-one-pair` shows one pair in detail.
:numref:`fig-magnetics-four-pairs` shows how the four pairs of one port
share the parts on the cable side.

.. _fig-magnetics-one-pair:

.. graphviz:: magnetics/one-pair.dot
   :caption: One pair (pair A, RJ45 pins 1 and 2) between the transceiver and
             the RJ45 socket. Solid lines carry the signal. Dashed lines are
             the centre-tap connections: on the circuit side to signal ground
             through a capacitor, on the cable side to chassis ground through
             the common-mode termination. The other three pairs are wired the
             same way.
   :align: center

.. _fig-magnetics-four-pairs:

.. graphviz:: magnetics/four-pairs.dot
   :caption: All four pairs of one port. Each yellow block is one channel of
             the magnetics: an isolation transformer followed, on the cable
             side, by a common-mode choke. The 75 Ω resistors from the four
             cable-side centre taps join at one node, which goes through a
             single high-voltage capacitor to chassis ground. Pins are listed
             pair by pair, not in physical order. At 10 and 100 Mbit/s only
             pairs A and B carry data. Circuit-side centre taps are not shown
             here; see :numref:`fig-magnetics-centre-tap-bias`.
   :align: center

Starting from the transceiver, each pair passes through:

1. **Two traces on the circuit board**, routed as a 100 Ω differential pair
   from the transceiver pins to the transformer.
2. **The circuit-side winding of the isolation transformer.** This winding
   has a centre tap: a connection to the middle of the winding. What the
   centre tap connects to depends on the transceiver (see
   `The centre taps`_).
3. **The isolation barrier.** Nothing conducts across the transformer. The
   signal crosses only through the magnetic field in the core.
4. **The cable-side winding**, also centre-tapped.
5. **The common-mode choke**, two windings on one small core, one in each
   wire of the pair.
6. **The RJ45 pins** and then the cable.

The cable-side centre tap of each pair goes through a 75 Ω resistor to a node
shared by all four pairs. That node goes through one 1000 pF capacitor, rated
for 2 kV, to *chassis ground*: the metal of the enclosure and the shield of
the RJ45 socket. This network is described in
`The cable-side centre taps and common-mode termination`_.

Why a transformer is needed
---------------------------

IEEE 802.3 does not say that a transformer must be used. It sets electrical
requirements on the MDI (isolation, signal levels, return loss and others),
and a 1:1 transformer per pair is the usual way to meet them. Microchip's
*Magnetics Guide* (ENT-AN0098) describes magnetics as "the most commonly used
method" of meeting the electrical requirements of the 10/100/1000BASE-T
interface. The transformer does several jobs at once.

Galvanic isolation
~~~~~~~~~~~~~~~~~~

*Galvanic isolation* means there is no conducting path between two circuits:
no DC current can flow from one to the other, and a large voltage between
them does no harm up to a rated limit.

The two ends of an Ethernet cable can be up to 100 m apart, in different
rooms or buildings, powered from different parts of the mains wiring. Their
local ground voltages can differ by volts, and by much more during a fault in
the mains wiring or a nearby lightning strike. Without isolation, that
difference would drive current along the cable wires and through both
transceivers.

IEEE 802.3 requires each twisted-pair port to be isolated from the rest of
the equipment, including its frame ground (the metal frame or enclosure),
and to pass at least one of three
electrical strength tests. The requirement appears separately for each speed:
Clause 14.3.1.1 for 10BASE-T, Clause 25.4.6 for 100BASE-TX and
Clause 40.6.1.1 for 1000BASE-T.

.. list-table:: Isolation tests in IEEE 802.3 for twisted-pair ports
                without Power over Ethernet. A port must pass at least one.
                Ports that supply or take power have the variant noted in
                the text.
   :header-rows: 1
   :widths: 30 70

   * - Test
     - Requirement
   * - AC voltage
     - 1500 V rms at 50 Hz to 60 Hz for 60 s
   * - DC voltage
     - 2250 V DC for 60 s
   * - Impulses
     - Ten 2400 V impulses of alternating polarity, at least 1 s apart. Each
       impulse rises in 1.2 µs and falls to half its peak in 50 µs (the
       "1.2/50 µs" shape defined in IEC 60060).
   * - Pass condition
     - No insulation breakdown during the test, and at least 2 MΩ measured at
       500 V DC afterwards.

The AC and DC tests are applied as described in the safety standard
IEC 60950-1 (newer text also refers to its successor, IEC 62368-1). For
ports that supply or take Power over Ethernet (Clause 33.4.1 and
Clause 145.4.1), the impulse test uses ten 1500 V impulses with a slower
10/700 µs shape, and the isolation is measured from the cable wires to all
accessible conductors of the equipment.

A test with these voltages is commonly called a *hipot test* (short for
"high potential"), and magnetics data sheets give the voltage the part
withstands as its "hipot" rating, usually 1500 V rms.

An interpretation request sent to the IEEE 802.3 working group in 2011
(number 2-03/11) states that earlier interpretations treated this test as
protection of the Ethernet interface against common-mode voltages, rather
than as a safety test. Product safety for people is covered by the
equipment safety standards. Some application notes (for example Microchip
ENT-AN0098) describe the same requirement in terms of human safety. In
practice the isolation does both: it keeps ground differences and surges
off the chip, and it keeps the cable wires separate from the circuit inside
the equipment.

Differential-only coupling and common-mode rejection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any voltage on a pair can be split into two parts:

* the *differential-mode* voltage, the difference between the two wires,
  which carries the data; and
* the *common-mode* voltage, the average of the two wires measured against
  ground, which carries no data.

A transformer couples only the voltage *across* a winding, so it passes the
differential signal and blocks the common-mode voltage. A common-mode voltage
on the cable side moves both ends of the cable-side winding up and down
together, which drives no current through the winding and induces nothing on
the circuit side. The transformer also blocks DC entirely, which allows each
side to sit at whatever DC level suits it. This is what allows Power over
Ethernet to put a DC voltage on the cable-side centre taps without disturbing
the data (see `Power over Ethernet through the centre taps`_).

Real transformers are not perfect: the capacitance between the two windings
lets some common-mode voltage through at high frequencies. This is one reason
a separate common-mode choke is added (see `The common-mode choke`_).

Impedance matching and the 1:1 ratio
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A transformer with a turns ratio of :math:`n` (secondary turns to primary
turns) makes an impedance :math:`Z` on one side look like a different
impedance on the other:

.. math::

   Z_\text{seen} = \frac{Z}{n^2}

Ethernet transceivers are designed to drive, and to terminate, a 100 Ω
differential load directly, so the transformer's turns ratio is 1:1. The
100 Ω cable then appears as 100 Ω at the transceiver pins, and the
transceiver's 100 Ω termination appears as 100 Ω to the cable. Data sheets
write the ratio as "1CT:1CT", meaning 1:1 with a centre tap on both windings.
The ratio has to be accurate: Microchip ENT-AN0098 recommends a tolerance of
±2 % so that the transmitted amplitude stays inside the limits of the
standard, and typical parts specify ±2 % or ±3 %.

How closely the port matches 100 Ω is measured by the *return loss*: the
ratio, in decibels, between a signal arriving at the port and the part of it
that is reflected back. For an impedance :math:`Z` measured against a
reference impedance :math:`Z_0 = 100\ \Omega`, the reflection coefficient
:math:`\Gamma` and the return loss are:

.. math::

   \Gamma = \frac{Z - Z_0}{Z + Z_0},
   \qquad
   \text{return loss} = -20 \log_{10} \lvert \Gamma \rvert \ \text{dB}

IEEE 802.3 Clause 40.8.3.1 requires the return loss at a 1000BASE-T MDI to be
at least 16 dB from 1 MHz to 40 MHz, and at least
:math:`10 - 20 \log_{10}(f / 80\ \text{MHz})` dB from 40 MHz to 100 MHz
(8.1 dB at 100 MHz), against any cable impedance between 85 Ω and 115 Ω
(100 Ω ± 15 %). A return loss of 16 dB means :math:`\lvert\Gamma\rvert = 0.158`,
which for a purely resistive port allows anything between about 73 Ω and
138 Ω. The requirement applies to the transceiver and magnetics together, so
the magnetics themselves should do better. Microchip ENT-AN0098 recommends
at least 2 dB of margin in the magnetics.

The *insertion loss* is the signal power lost passing through the magnetics
when both sides are terminated in 100 Ω. Gigabit magnetics specify at most
1 dB from 1 MHz to 100 MHz, which means the signal amplitude falls by at most
11 %.

Bandwidth and the magnetising inductance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A transformer cannot pass DC, and it passes low frequencies poorly. The
reason is the *magnetising inductance*: the inductance of one winding with
the other winding left open. Data sheets call it the *open-circuit
inductance*, OCL. It appears in parallel with the signal path. At low
frequencies its impedance is small and it shunts the signal away.

Seen from that inductance, the transceiver's 100 Ω and the cable's 100 Ω are
in parallel, so it works into :math:`R = 50\ \Omega`. The transformer is
therefore a high-pass filter with a corner frequency of

.. math::

   f_c = \frac{R}{2 \pi L} = \frac{50\ \Omega}{2 \pi \times 350\ \mu\text{H}}
   \approx 23\ \text{kHz}

for the common 350 µH value. In the time domain the same effect appears as
*droop*: if the transmitter holds a constant voltage, the voltage at the far
side of the transformer decays towards zero with time constant
:math:`\tau = L / R`.

1000BASE-T limits droop directly. Clause 40.6.1.2.2 requires that, in a
transmitter test pattern that holds one level, the voltage 500 ns after the
peak is still more than 73.1 % of the peak. Treating the transformer as the
only cause of droop gives a minimum inductance:

.. math::

   e^{-500\ \text{ns} / \tau} \ge 0.731
   \;\Rightarrow\;
   \tau \ge 1.6\ \mu\text{s}
   \;\Rightarrow\;
   L = \tau R \ge 1.6\ \mu\text{s} \times 50\ \Omega = 80\ \mu\text{H}

This calculation and its result of about 80 µH appear in an IEEE 802.3
maintenance proposal by TE Connectivity (Tracy and Eminhizer, 2011). With
350 µH the time constant is 7 µs, and the voltage after 500 ns is 93 % of
the peak.

The 350 µH figure itself comes from 100BASE-TX. Clause 25 adopts the
twisted-pair physical layer of FDDI, an older 100 Mbit/s network standard,
ANSI X3.263-1995 (often
called TP-PMD), and its subclause 9.1.7 requires at least 350 µH at the
transmitter "with any DC bias current between 0 mA and +8 mA". The reason is
*baseline wander*: the 100BASE-TX signal can contain long stretches whose
average is not zero, and the high-pass filter formed by the transformer then
lets the average level of the received signal drift (its "baseline"
wanders), which pushes symbols towards the receiver's decision thresholds.
A larger inductance makes the drift slower and smaller. The DC bias matters
because a magnetic core carrying DC is partly saturated, which lowers its
inductance; ANSI X3.263 notes that the inductance can vary by about 2:1 with
bias. The test conditions in data sheets, "100 kHz, 100 mV, 8 mA DC bias",
come from this requirement.

IEEE 802.3at (2009) added an alternative to the 350 µH requirement for
transmitters in equipment supplying or taking more than 13 W of Power over
Ethernet: a droop test with a defined DC bias. According to the TE
Connectivity proposal mentioned above, transceiver makers began adding
baseline-wander correction to their receivers in 1997. Magnetics for
10/100/1000 Mbit/s use still specify 350 µH at 8 mA, and transceiver data
sheets still ask for it (for example the KSZ9031RNX, and the DP83867,
whose data sheet lists 320 µH to 350 µH).

At the top of the band, the leakage inductance (the part of each winding's
inductance not shared with the other winding) and the capacitance between
turns and between windings limit the bandwidth and the return loss. Data
sheets do not give these values directly; they show up in the insertion loss
and return loss limits up to 100 MHz.

The common-mode choke
---------------------

A *common-mode choke* is two windings on one core, one in series with each
wire of the pair, wound so that the data current, which flows out on one wire
and back on the other, produces opposing magnetic fields that cancel. The
data signal therefore sees almost no inductance. A *common-mode current*,
which flows in the same direction on both wires (and returns through ground
or through the air), produces fields that add, and sees a high impedance.

Common-mode currents on an Ethernet cable come from two directions:

* **Emissions.** Noise from the board (switching power supplies, clocks,
  digital logic) couples equally onto both traces of a pair and becomes a
  common-mode voltage. Any imbalance in the transmitter does the same. An
  unshielded twisted-pair cable carrying common-mode current behaves as an
  antenna, and the radiation from it is what fails radio-interference limits
  such as FCC Part 15. The choke blocks this current.
* **Immunity.** The cable picks up common-mode noise from its surroundings.
  The choke, together with the transformer, keeps it away from the receiver.
  Microchip ENT-AN0098 calls this "electromagnetic immunity".

Choke placement
~~~~~~~~~~~~~~~

The choke can sit on either side of the transformer. In parts sold for
gigabit use it is almost always on the cable side, and transceiver makers
recommend that:

* Microchip ENT-AN0098 recommends "common-mode choke on the line side for all
  applications that permit line-side CMC" and reports less margin in the
  standard's transmit waveform tests with the choke on the transceiver side.
* A choke on the cable side also blocks common-mode noise coming from the
  circuit-side centre-tap circuits and the board.
* With a current-mode transceiver (see `The centre taps`_), the supply
  current enters through the centre tap and flows outward through both wires
  of the pair in the same direction. That is a common-mode DC current; a
  choke between the transceiver and the transformer would carry it and could
  saturate.

Some magnetics add a third component per pair after the choke: an
*autotransformer*, a single centre-tapped winding across the pair whose
centre tap goes to the common-mode termination. It has a high impedance for
the data signal and a low impedance for common-mode current, so it gives that
current a short path to the termination. Magnetics with a transformer, choke
and autotransformer per pair have three cores per pair, twelve in total, and
are sold as "12-core" parts; those without the autotransformer are "8-core".
Microchip ENT-AN0098 describes 12-core parts as easier to design with,
especially next to a large, noisy digital circuit, and noted in 2018 that no
Power over Ethernet magnetics then on the market included the
autotransformer.

The centre taps
---------------

Circuit-side centre taps
~~~~~~~~~~~~~~~~~~~~~~~~

How the circuit-side centre tap is connected depends on the type of line
driver in the transceiver. :doc:`phy-electrical` describes the two types.
From the magnetics' point of view the difference is this:

* A **current-mode driver** switches a current between the two pins of the
  pair. Its output transistors only *sink* current, so the current must be
  supplied from outside, through the transformer's centre tap. The centre tap
  is connected to a supply rail and decoupled to ground with a capacitor.
  Each pin often also has a resistor to the same supply to set the
  termination. TI's DP83848 (10/100 Mbit/s) is an example: its MDI pins each
  need a 49.9 Ω resistor to the 3.3 V analog supply, and the centre taps are
  joined and pulled up to the same supply with a 100 nF capacitor per
  channel (TI application note SDAA089). Microchip ENT-AN0106 describes a
  gigabit current-mode driver of this kind drawing about 40 mA per pair.
* A **voltage-mode driver** drives each pin from a low impedance and sets
  its own common-mode voltage. Its termination resistors are usually on the
  chip. The centre tap must *not* be connected to a supply; it is connected
  to ground only through a capacitor, which gives common-mode noise a path to
  ground. Microchip's KSZ9031RNX data sheet asks for each of the four
  circuit-side centre taps to be kept separate and connected through its own
  0.1 µF capacitor to ground, because the common-mode voltage on each pair
  can differ depending on speed. TI's DP83867 data sheet asks for the same,
  and TI's DP83826A (10/100 Mbit/s) uses 2 nF per channel.

.. _fig-magnetics-centre-tap-bias:

.. graphviz:: magnetics/centre-tap-bias.dot
   :caption: Circuit-side centre-tap connection for one pair. Left: a
             current-mode driver takes its current through the centre tap,
             which is tied to a supply and decoupled to ground; each pin also
             has a termination resistor to the supply. Right: a
             voltage-mode driver sets its own common-mode voltage, and the
             centre tap only goes to ground through a capacitor.
   :align: center

Getting this wrong stops the link from working, so the transceiver data
sheet is the authority. The magnetics must allow it: for voltage-mode
transceivers, choose parts whose four circuit-side centre taps are on
separate pins, not joined inside the part (Microchip ENT-AN0098 and the
KSZ9031RNX data sheet both ask for this).

The cable-side centre taps and common-mode termination
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The four pairs inside a cable are not only four separate transmission lines.
Each pair, taken as a whole, also forms a transmission line with every other
pair, and with the surroundings. Common-mode current travels along these
lines. If the ends of these lines are left open, the energy reflects back
and forth and builds up standing waves, and the cable radiates it.

The standard fix is to terminate these pair-to-pair lines in roughly their
characteristic impedance. Each cable-side centre tap goes through a 75 Ω
resistor to a shared node. Between any two pairs there are then two 75 Ω
resistors in series, 150 Ω, close to the roughly 145 Ω pair-to-pair
impedance of a Category 5 cable (a common grade of Ethernet cable). The energy is absorbed as heat in the
resistors instead of being radiated.

This network is widely called the *Bob Smith termination*, after Robert W.
Smith, whose patent (US 5,321,372, 1994-06-14, "Apparatus and method for
terminating cables to minimize emissions and susceptibility") describes it.
The patent describes four 75 Ω resistors joined at one node and reports
"upwards of approximately 10 dB improvement in emissions and susceptibility".

The shared node is then connected to chassis ground through one capacitor,
typically 1000 pF rated for 2 kV. Microchip ENT-AN0098 points out that this
capacitor is not part of Smith's patent; it gives the common-mode noise that
leaks through a path to chassis ground. Its impedance shows why a capacitor
is used:

.. math::

   \lvert Z_C \rvert = \frac{1}{2 \pi f C}:
   \qquad
   3.2\ \text{M}\Omega \ \text{at}\ 50\ \text{Hz},
   \qquad
   5.3\ \Omega \ \text{at}\ 30\ \text{MHz}
   \qquad (C = 1000\ \text{pF})

At high frequencies it is close to a short circuit, so the termination works.
At mains frequencies and DC it is close to an open circuit, so it does not
undo the isolation. The 2 kV rating is needed because the capacitor sits
across the isolation barrier, between the cable wires and the chassis, and
must survive the isolation test.

The 75 Ω resistors and 1000 pF, 2 kV capacitor are what transceiver makers
show in their reference circuits (for example in the KSZ9031RNX and DP83867 data sheets)
and what integrated sockets contain.

Power over Ethernet through the centre taps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Power over Ethernet (PoE) sends DC power along the same cable as the data.
It uses the pairs in a common-mode way: the power source puts one polarity on
both wires of one pair and the other polarity on both wires of another pair.
A pair carries no differential DC voltage, so the data is not affected.

On the receiving side (the *powered device*), power is taken from the
cable-side centre taps. The DC current enters at the centre tap and splits
into the two halves of the winding, flowing outward in opposite directions,
so the magnetic fields it creates in the core cancel and the core is not
biased. Any imbalance between the two wires' resistances leaves a net DC
current in the winding; IEEE 802.3 Clause 33 accounts for this imbalance,
and it is one reason magnetics sold for PoE use are rated for the current and keep
their inductance with DC bias.

IEEE 802.3 Clause 33 (the 802.3af and 802.3at amendments) defines two ways
of using the pairs: *Alternative A* puts power on the pairs on pins 1, 2 and
3, 6, and *Alternative B* on the pairs on pins 4, 5 and 7, 8. A powered
device must accept power on either set of pairs, in either polarity. It
therefore has two bridge rectifiers, one on the centre taps of pairs A and
B, the other on the centre taps of pairs C and D, with their outputs joined.
Clause 145 (the 802.3bt amendment) adds power on all four pairs at once.

The DC voltage on the centre taps would flow through the 75 Ω resistors of
the common-mode termination, so in PoE designs each 75 Ω resistor is put in
series with a small capacitor (Microchip ENT-AN0098 suggests about 10 nF)
that blocks the DC.

.. _fig-magnetics-poe:

.. graphviz:: magnetics/poe-centre-taps.dot
   :caption: Taking Power over Ethernet from the cable-side centre taps
             ("CT") of a powered device. The bridge rectifiers make the
             power input independent of which pairs, and which polarity, the
             source uses.
   :align: center

The detection, classification and power conversion circuits after the
bridges are described in :doc:`../power/poe`.

Practical parts
---------------

Discrete magnetics and integrated sockets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Magnetics are sold in two forms:

* **Discrete transformer modules**: a small surface-mount part with all four
  channels, placed between the transceiver and an ordinary RJ45 socket. The
  75 Ω resistors and the high-voltage capacitor are then separate parts on
  the board.
* **Integrated sockets**: an RJ45 socket with the magnetics, and usually the
  75 Ω resistors and the high-voltage capacitor, built inside its metal
  shield. Bel Fuse sells these as "MagJack"; other makers use similar names.

Microchip ENT-AN0098 compares the two. Integrated sockets save board area and
parts, and their metal shield screens the cable-side wiring. Their cores are
smaller and closer together, which can make crosstalk, losses and common-mode
rejection worse, and a faulty one is harder to replace. Discrete modules
allow better separation, but the traces between the module and the socket
must then be routed with care, away from noise sources. TI's DP83867 data
sheet recommends a discrete transformer for better EMC (electromagnetic
compatibility) performance. Both forms are widely used.

Integrated sockets usually also contain two LEDs, visible on the front of
the socket. These are ordinary LEDs on separate pins, driven by the
transceiver's LED outputs to show link and activity. They are on the circuit
side and have nothing to do with the isolation.

Protection against electrostatic discharge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An Ethernet port is touched by people and connected to long cables, so it
must survive electrostatic discharge (ESD) and surges. The transformer
already blocks common-mode surges up to its isolation rating. Extra
protection diodes (transient voltage suppressors, which conduct above a set
voltage) are often added for differential surges. TI's *Ethernet PHY PCB
Design Layout Checklist* (SNLA387) notes that TI's Ethernet-specific guidance
places these diodes on the transceiver side of the magnetics: on the cable
side, large common-mode voltages could make them conduct and fail during
events that are not ESD. Their capacitance and working voltage must suit the
signal; the transceiver data sheet gives the levels.

Chassis ground and the shield
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are two separate grounds near the socket:

* **Signal ground** (also called circuit ground): the ground of the
  transceiver and the rest of the board.
* **Chassis ground**: the enclosure, the metal shield of the RJ45 socket, and
  the cable-side common-mode termination.

TI's DP83867 data sheet asks for a metal shielded RJ45 socket with its shield
connected to chassis ground, and for chassis ground to be an isolated area of
copper that does not overlap the signal ground planes. Both TI documents
suggest joining the two grounds through a resistor and a capacitor. SNLA387,
which calls the chassis area "earth ground", suggests a resistor of 1 MΩ or
more and a keep-out of at least 20 mil (about 0.5 mm) on all layers around
that area. These parts and spacings
bridge the isolation barrier, so their voltage rating and spacing must suit
the isolation test that the equipment has to pass.

Layout
~~~~~~

.. _fig-magnetics-layout:

.. graphviz:: magnetics/layout.dot
   :caption: Board areas around one port, seen from above. The transceiver
             and the circuit-side centre-tap capacitors sit on a solid signal
             ground plane. There is no copper on any layer under the
             transformer. The RJ45 socket, the common-mode termination and
             the shield connection sit on a separate chassis ground area.
             With an integrated socket the transformer is inside the socket.
   :align: center

The main rules, from TI's DP83867 data sheet and TI SNLA387:

* Route each pair as a 100 Ω differential pair (50 Ω from each trace to
  ground) with a continuous ground plane beneath it. SNLA387 gives ±10 %
  for the impedance, a total length under 2 inches (about 50 mm), and
  matching of the two traces of a pair to within 20 mil (about 0.5 mm) at
  1000 Mbit/s.
* Keep different pairs at least 30 mil (about 0.75 mm) apart, keep vias and
  stubs to a minimum, and route each pair to the transformer on one layer.
* Remove supply and ground copper from under the magnetics on all layers
  (SNLA387 asks for no metal under the magnetics on any layer; metal under
  an integrated socket is allowed). Copper under the transformer adds
  capacitance between the two sides, which weakens both the isolation and
  the common-mode rejection.
* Keep the cable-side traces (between a discrete module and the socket)
  short, matched and away from noisy circuits.
* Place the centre-tap capacitors close to the centre-tap pins.

What to look for in a magnetics data sheet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Typical requirements for 10/100/1000 Mbit/s magnetics, from
                transceiver data sheets (KSZ9031RNX Table 12-1, DP83867
                Table 9-1) and Microchip ENT-AN0098
   :header-rows: 1
   :widths: 28 32 40

   * - Parameter
     - Typical requirement
     - Why
   * - Turns ratio
     - 1CT:1CT, within ±2 % to ±3 %
     - Keeps 100 Ω matching and the transmit amplitude.
   * - Open-circuit inductance
     - 350 µH minimum at 100 kHz, 100 mV, 8 mA DC bias
     - Limits droop and baseline wander.
   * - Insertion loss
     - 1 dB maximum, 1 MHz to 100 MHz
     - Signal level at the receiver.
   * - Return loss
     - Better than the IEEE 802.3 MDI limit, with about 2 dB margin
       (about 18 dB from 1 MHz to 30 MHz in typical parts)
     - The transceiver and magnetics together must meet 16 dB.
   * - Common-mode rejection
     - 30 dB or more (often given separately for common-mode to
       differential and differential to common-mode conversion)
     - Emissions and immunity.
   * - Crosstalk between channels
     - 30 dB or more
     - Signals from one pair must not leak into another.
   * - Isolation ("hipot")
     - 1500 V rms for 1 minute
     - IEEE 802.3 isolation test.
   * - Centre taps
     - Four separate circuit-side centre taps; four cable-side centre taps
       available for the 75 Ω termination
     - Needed by voltage-mode transceivers and for the termination.
   * - Choke position
     - Cable side
     - See `Choke placement`_.
   * - Power over Ethernet
     - Rated for the PoE current, if the port takes or supplies power
     - Centre taps carry the power current.
   * - Temperature range
     - 0 °C to 70 °C (commercial) or −40 °C to 85 °C (industrial)
     - Inductance changes with temperature.

Example parts
~~~~~~~~~~~~~

The following parts were checked against their manufacturers' data sheets.
They are examples, not a selection for evampire.

.. list-table:: Example gigabit magnetics
   :header-rows: 1
   :widths: 22 18 60

   * - Part
     - Form
     - Key data sheet values
   * - Pulse Electronics H5007NL
     - Discrete surface-mount module, one port
     - 1:1 ratio; insertion loss 1 dB maximum (1 MHz to 100 MHz); return
       loss at least 18 dB from 1 MHz to 30 MHz and at 40 MHz, 16 dB at
       50 MHz, 12 dB from 60 MHz to 80 MHz, 10 dB at 100 MHz; hipot 1500 V rms; 0 °C to
       70 °C. Listed as a 12-core part in Microchip ENT-AN0098 and the
       KSZ9031RNX data sheet. The data sheet (HC500.T) does not list the
       inductance.
   * - Würth Elektronik 7499111221A
     - RJ45 socket with integrated magnetics, through-hole, two green LEDs
     - 350 µH minimum at 100 kHz, 100 mV, 8 mA; 1500 V rms for 1 minute;
       insertion loss 1 dB maximum (1 MHz to 100 MHz); return loss at least
       18 dB (1 MHz to 30 MHz), 14 dB (30 MHz to 60 MHz), 9 dB (60 MHz to
       80 MHz), 8 dB (80 MHz to 100 MHz); common-mode rejection 30 dB; ratio
       1:1 ±3 %; four 75 Ω resistors and 1000 pF, 2 kV capacitor inside; not
       for PoE.
   * - Bel Fuse 0826-1G1T-23-F (MagJack)
     - RJ45 socket with integrated magnetics, through-hole, two green LEDs,
       12 cores
     - Ratio 1CT:1CT ±2 %; 350 µH minimum at 100 kHz, 100 mV rms, 8 mA;
       return loss at least 18 dB (0.5 MHz to 40 MHz); common-mode to
       common-mode rejection 30 dB, common-mode to differential rejection
       35 dB (100 kHz to 100 MHz); 1500 V rms, every part tested; four 75 Ω
       resistors and 1000 pF, 2 kV capacitor to the shield inside.

Magnetics in evampire designs
-----------------------------

evampire has no analog Ethernet circuits on the chip. Its ports A and B are
RGMII interfaces (see :doc:`rgmii`), and everything described on this page
belongs to the board. For each of ports A and B, a board needs:

* one Ethernet transceiver with an RGMII interface;
* one set of four-channel magnetics for 1000BASE-T, either a discrete module
  or built into the RJ45 socket;
* the circuit-side centre-tap connection that the chosen transceiver's data
  sheet asks for (separate capacitors to ground for a voltage-mode driver, or
  a supply connection for a current-mode driver);
* the cable-side common-mode termination (four 75 Ω resistors and one
  1000 pF, 2 kV capacitor to chassis ground), unless it is inside the socket;
* a shielded RJ45 socket, its shield connected to a chassis ground area kept
  apart from signal ground, and the resistor and capacitor joining the two
  grounds;
* optionally, the two LEDs driven by the transceiver, and protection diodes
  on the circuit side of the magnetics as the transceiver maker recommends.

A port that is used to power the board from the cable also needs PoE-rated
magnetics, the two bridge rectifiers on the cable-side centre taps, DC
blocking capacitors in the common-mode termination, and the powered-device
circuits described in :doc:`../power/poe`.

The magnetics do not change anything that evampire sees. The transceiver
handles the analog signals on its side of the transformer, and evampire
exchanges only digital RGMII signals with the transceiver.

References
----------

IEEE 802.3 and related documents
   * Clause numbers on this page are those given in the documents below,
     which quote editions of IEEE 802.3 from 2002 to 2015. They were not
     checked against the text of the 2022 edition.
   * IEEE Std 802.3-2022, *IEEE Standard for Ethernet*.
     https://standards.ieee.org/ieee/802.3/10422/ (also offered through
     the IEEE GET Program). Clauses used on this page: 14.3.1.1
     (10BASE-T isolation), 25 and 25.4.6 (100BASE-TX, isolation), 33 and
     33.4.1 (Power over Ethernet, isolation with power), 40.4.4 (automatic
     MDI/MDI-X configuration), 40.6.1.1 (1000BASE-T isolation), 40.6.1.2.2
     (maximum output droop), 40.8.1 (MDI connectors), 40.8.3.1 (MDI return
     loss), 145 and 145.4.1 (Power over Ethernet over four pairs).
   * ANSI X3.263-1995 (ANSI INCITS 263), *FDDI Token Ring Twisted Pair
     Physical Layer Medium Dependent (TP-PMD)*, subclause 9.1.7 (minimum
     transmitter open-circuit inductance), as quoted in D. Law, *IEEE
     P802.3at 350 µH ad hoc report*, 2008.
     https://www.ieee802.org/3/at/public/2008/06/law_1_0608.pdf
   * D. Walker and C. Bullock, *Summary of Isolation Requirements, 802.3-2015,
     Clause 126, & Clause 145 D3.0*, IEEE 802.3 isolation ad hoc, 2017-08-17.
     https://www.ieee802.org/3/ad_hoc/isolation/public/Walker_1_08172017_rev_1.pdf
   * IEEE 802.3 interpretation request 2-03/11, *Isolation Criteria*,
     2011-03-20. https://www.ieee802.org/3/interp/interp-2-0311.pdf
   * N. Tracy and E. Eminhizer (TE Connectivity), *Proposed Changes to IEEE
     Std 802.3, Sub-clauses 25.4.5, 25.4.5.1 and 25.4.7, to address the need
     for reduced Open Circuit Inductance in Ethernet Magnetics*, 2011.
     https://www.ieee802.org/3/maint/public/tracy_1_0911.pdf
   * University of New Hampshire InterOperability Laboratory, *Clause 40
     Physical Medium Attachment (PMA) Test Suite*, version 1.1.
     https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/CL40_PMA/PMA_Test_Suite_v1.1.pdf
   * University of New Hampshire InterOperability Laboratory, *100BASE-TX
     PMD Test Suite*, version 3.5 (test 25.1.7, transmitter open-circuit
     inductance).
     https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/CL25_PMD/PMD_Test_Suite_v3.5.pdf
   * M. Hersh, *Auto-Crossover White Paper*, University of New Hampshire
     InterOperability Laboratory, 2006.
     https://www.iol.unh.edu/sites/default/files/knowledgebase/ethernet/Auto-Crossover_White_Paper.pdf
   * R. W. Smith, *Apparatus and method for terminating cables to minimize
     emissions and susceptibility*, US patent 5,321,372, 1994-06-14.
     https://patents.google.com/patent/US5321372A

Application notes
   * Microchip (Microsemi), *Magnetics Guide*, ENT-AN0098, revision 2.2.
     https://www.microchip.com/en-us/application-notes/entan0098magneticsguide
   * Microchip (Microsemi), *SimpliPHY Architecture Advantages*, ENT-AN0106
     (current-mode and voltage-mode line drivers).
   * Microchip (Microsemi), *SimpliPHY Transformerless Ethernet Designs*,
     ENT-AN0114.
   * Texas Instruments, *Ethernet PHY PCB Design Layout Checklist*, SNLA387.
     https://www.ti.com/lit/an/snla387/snla387.pdf
   * Texas Instruments, *DP83848 to DP83826A Hardware Rollover Document*,
     SDAA089. https://www.ti.com/lit/pdf/sdaa089
   * Texas Instruments, *PoE PD Schematic Review Guidelines*, SLVAF59.
     https://www.ti.com/lit/an/slvaf59/slvaf59.pdf

Data sheets
   * Microchip, *KSZ9031RNX Gigabit Ethernet Transceiver with RGMII Support*,
     DS00002117F (Table 3-1, MDI/MDI-X pin mapping; section 12, magnetics).
     https://ww1.microchip.com/downloads/en/DeviceDoc/00002117F.pdf
   * Texas Instruments, *DP83867IR/CR Robust, High Immunity, Small Form
     Factor 10/100/1000 Ethernet PHY Layer Transceiver*, SNLS484 (section
     9.2, magnetics connections and layout).
     https://www.ti.com/lit/ds/symlink/dp83867ir.pdf
   * Texas Instruments, *TPS2376-H*, SLVS646 (Power over Ethernet input
     bridges and magnetics). https://www.ti.com/lit/ds/symlink/tps2376-h.pdf
   * Pulse Electronics, *1000BASE-T Magnetics Module* (H5004NL, H5007NL),
     HC500.T, 2020-06. https://www.pulseelectronics.com/
   * Würth Elektronik, *WE-RJ45LAN Transformer 10/100/1000Base-T*,
     7499111221A, revision 005.000, 2020-10-07.
     https://www.we-online.com/components/products/datasheet/7499111221A.pdf
   * Bel Fuse, *gigabit MagJack 0826-1G1T-23-F*, drawing revision F.
     https://www.belfuse.com/media/drawings/products/magjack%20ICMs/dr-mag-0826-1g1t-23-f.pdf
