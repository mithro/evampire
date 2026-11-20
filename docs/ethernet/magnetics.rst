Magnetics and the RJ45 socket
=============================

This page explains how an Ethernet transceiver is connected to the RJ45
socket, what the coupling transformers between them (the "magnetics") do,
and how those jobs can be done without transformers.

The requirements for evampire are (see :doc:`../overview`):

* **First version:** each Ethernet port uses an external transceiver chip
  with an RGMII interface (see :doc:`rgmii`), and standard magnetics between
  that transceiver and the RJ45 socket.
* **Full design:** the transceiver is integrated on evampire, and the cable
  connects to the board *without coupling transformers*. Every job the
  transformers normally do is done instead by active analog circuits on
  evampire together with a small number of external passive components. Each
  port must also be able to receive or supply Power over Ethernet, up to all
  Power over Ethernet types (see :doc:`../power/index`).

The transformer is therefore the reference point. The first half of this
page explains each job it does and the numbers the Ethernet standard sets.
The second half works through how each job can be done without it, what that
means for a chip made in the gf180mcu process, and which questions are still
open. How the transceiver itself works is covered in :doc:`phy-electrical`.

The Ethernet standard is IEEE 802.3 [MAG-IEEE8023]_. The parts of it that
matter here are :clause:`14` (10 Mbit/s over twisted-pair cable, called
*10BASE-T*), :clause:`25` (100 Mbit/s, *100BASE-TX*), :clause:`40`
(1000 Mbit/s, *1000BASE-T*), and :clause:`Clauses 33 <33>` and
:clause:`145 <145>` (Power over Ethernet). The connection
between the transceiver and the cable is called the *MDI*, short for "medium
dependent interface": the eight wires of the RJ45 socket and the electrical
requirements on them. Clause numbers on this page are those given in the
cited documents, which quote editions of IEEE 802.3 from 2002 to 2022; they
were not checked against the text of the 2022 edition.

The cable and the RJ45 socket
-----------------------------

An Ethernet cable contains four *twisted pairs*: four pairs of wires, the two
wires of each pair twisted around each other. Each pair is a balanced
transmission line with a characteristic impedance of 100 Ω. A signal is sent
as a voltage *difference* between the two wires of a pair, and the receiver
looks only at that difference. Interference from outside reaches both wires
of a pair nearly equally and does not change the difference.

The RJ45 plug and socket have eight contacts, numbered 1 to 8. One pair uses
pins 3 and 6, which sit on either side of the pair on pins 4 and 5.

.. list-table:: RJ45 pin use. The 1000BASE-T names are those of IEEE 802.3
                :clause:`40`; "BI" means the pair carries data in both
                directions at once [MAG-KSZ9031]_.
   :header-rows: 1
   :widths: 12 18 25 25 20

   * - Pins
     - Pair (1000BASE-T)
     - 1000BASE-T, MDI
     - 10/100 Mbit/s, MDI
     - 10/100 Mbit/s, MDI-X
   * - 1, 2
     - A (BI_DA)
     - BI_DA+, BI_DA−
     - transmit +, −
     - receive +, −
   * - 3, 6
     - B (BI_DB)
     - BI_DB+, BI_DB−
     - receive +, −
     - transmit +, −
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

At 10 and 100 Mbit/s two pairs are used, one in each direction. At
1000 Mbit/s all four pairs carry data in both directions at the same time.

At 10 and 100 Mbit/s a transmitter at one end must reach the receiver at the
other end. With a "straight-through" cable (pin 1 to pin 1 and so on) this
works only if the two ends use opposite pin assignments, called *MDI* and
*MDI-X* (:numref:`fig-magnetics-crossover`). At 1000 Mbit/s, MDI-X swaps
pair A with B and pair C with D [MAG-KSZ9031]_. IEEE 802.3 :clause:`40.4.4`
defines *automatic MDI/MDI-X configuration*: while there is no link, a port
switches between the two assignments at pseudo-random times (a sample timer
of 62 ms ± 2 ms) until it hears the other end [MAG-UNHXO]_. Because either
pair can end up carrying either direction, all channels of the front end must
be identical.

.. _fig-magnetics-crossover:

.. graphviz:: magnetics/crossover.dot
   :caption: MDI and MDI-X at 10 and 100 Mbit/s. With a straight-through
             cable, the transmitter at one end reaches the receiver at the
             other end only if one port uses MDI and the other MDI-X.
   :alt: Two ports joined by a straight cable. On the MDI port the
         transmitter uses pins 1 and 2 and the receiver pins 3 and 6; on the
         MDI-X port these are swapped, so each transmitter reaches the other
         port's receiver.
   :align: center

A port with standard magnetics
------------------------------

:numref:`fig-magnetics-one-pair` shows one pair of a standard port, as used
in the first version. :numref:`fig-magnetics-four-pairs` shows all four
pairs and the parts they share.

.. _fig-magnetics-one-pair:

.. graphviz:: magnetics/one-pair.dot
   :caption: One pair (pair A, RJ45 pins 1 and 2) of a standard port.
             Solid lines carry the signal. Dashed lines are the centre-tap
             connections: on the circuit side to signal ground through a
             capacitor (for a transceiver with a voltage-mode driver), on
             the cable side to chassis ground through the common-mode
             termination.
   :alt: Schematic of one pair: transceiver pins pair A plus and minus go to
         the circuit-side winding of a 1:1 transformer. The cable-side
         winding goes through a common-mode choke to RJ45 pins 1 and 2. The
         circuit-side centre tap goes through 0.1 microfarads to signal
         ground; the cable-side centre tap goes through 75 ohms and a shared
         1000 picofarad, 2 kilovolt capacitor to chassis ground, which also
         connects to the socket shield.
   :align: center

.. _fig-magnetics-four-pairs:

.. graphviz:: magnetics/four-pairs.dot
   :caption: All four pairs of a standard port. Each yellow block is one
             channel of the magnetics: a transformer followed, on the cable
             side, by a common-mode choke. The 75 Ω resistors from the four
             cable-side centre taps join at one node, which goes through one
             high-voltage capacitor to chassis ground. Pins are listed pair
             by pair, not in physical order.
   :alt: Schematic of four channels, pairs A to D, between the transceiver
         and the RJ45 socket. Pair A goes to pins 1 and 2, B to 3 and 6, C
         to 4 and 5, D to 7 and 8. Each channel's cable-side centre tap has
         a 75 ohm resistor to a common line, which goes through a 1000
         picofarad, 2 kilovolt capacitor to chassis ground.
   :align: center

Each pair passes through a *transformer* (two windings on one magnetic core,
with no conducting path between them), then a *common-mode choke* (two
windings on one core, one in each wire), then the RJ45 pins. Both windings
of the transformer have a *centre tap*, a connection to the middle of the
winding. These parts are described in the next section.

What the magnetics do
---------------------

The transformer, the common-mode choke, the centre-tap connections and the
cable-side termination together do the jobs listed in
:numref:`tbl-magnetics-functions`. IEEE 802.3 does not require a
transformer; it sets electrical requirements on the MDI, and a 1:1
transformer per pair is "the most commonly used method" of meeting them
[MAG-ENT98]_.

.. _tbl-magnetics-functions:

.. list-table:: Functions of the magnetics, and the requirement each one
                meets
   :header-rows: 1
   :widths: 5 24 18 53

   * - #
     - Function
     - Done by
     - Requirement (source)
   * - F1
     - Galvanic isolation between the cable and the equipment
     - transformer
     - Withstand 1500 V rms at 50–60 Hz for 60 s, *or* 2250 V DC for 60 s,
       *or* ten 2400 V impulses (1500 V with Power over Ethernet); at least
       2 MΩ at 500 V afterwards (:clause:`Clauses 14.3.1.1 <14.3.1.1>`,
       :clause:`25.4.6 <25.4.6>`, :clause:`40.6.1.1 <40.6.1.1>`,
       :clause:`33.4.1 <33.4.1>`, :clause:`145.4.1 <145.4.1>`)
       [MAG-WALKER]_.
   * - F2
     - Rejecting common-mode voltage, and letting each side sit at its own
       voltage level
     - transformer, choke
     - No direct limit in IEEE 802.3. Typical magnetics reject 30 dB to
       43 dB [MAG-PULSE]_ [MAG-BEL]_.
   * - F3
     - Blocking DC between the cable and the transceiver
     - transformer
     - Needed for F1 and for Power over Ethernet (up to 57 V on the cable)
       [MAG-EA8023BT]_.
   * - F4
     - Matching the 100 Ω cable
     - 1:1 transformer
     - 1000BASE-T return loss ≥ 16 dB from 1 MHz to 40 MHz, against 85 Ω to
       115 Ω (:clause:`40.8.3.1`) [MAG-UNH40]_.
   * - F5
     - Passing low frequencies (limiting droop and baseline wander)
     - transformer inductance
     - 1000BASE-T: more than 73.1 % of the voltage left 500 ns after a step
       (:clause:`40.6.1.2.2`) [MAG-UNH40]_. 100BASE-TX, if supported: at
       least 350 µH with 0 mA to 8 mA DC bias (ANSI X3.263, section 9.1.7)
       [MAG-LAW]_.
   * - F6
     - Terminating common-mode signals on the cable (lower emissions and
       better immunity)
     - 75 Ω resistors, 1000 pF capacitor
     - No IEEE limit. About 10 dB improvement reported [MAG-SMITH]_.
   * - F7
     - Filtering common-mode noise to and from the cable
     - choke
     - Radio-interference limits for the equipment (for example FCC
       Part 15) [MAG-ENT106]_.
   * - F8
     - Withstanding surges and electrostatic discharge
     - transformer, plus protection diodes
     - No IEEE limit beyond F1. Equipment standards set test levels (see
       `Voltages and events at the cable`_).
   * - F9
     - Supplying or biasing the transceiver's line driver
     - circuit-side centre tap
     - Set by the transceiver design [MAG-SDAA089]_ [MAG-KSZ9031]_.
   * - F10
     - Carrying Power over Ethernet current
     - cable-side centre taps
     - Up to 938 mA in one pair (Class 8) [MAG-EA8023BT]_.
   * - F11
     - Keeping the data circuits invisible to Power over Ethernet detection
       and classification
     - transformer
     - Powered device signature 23.7 kΩ to 26.3 kΩ, 50 nF to 120 nF, and
       less than 100 µH in series [MAG-EA8023BT]_.
   * - F12
     - Identical channels, so any pair can carry any direction
     - four identical channels
     - Automatic MDI/MDI-X (:clause:`40.4.4`) [MAG-KSZ9031]_.

F1: Galvanic isolation
~~~~~~~~~~~~~~~~~~~~~~

*Galvanic isolation* means there is no conducting path between two circuits:
no DC current can flow between them, and a large voltage between them does
no harm up to a rated limit. The two ends of an Ethernet cable can be in
different buildings, powered from different parts of the mains wiring, and
their ground voltages can differ, by much more during a fault or a nearby
lightning strike. Without isolation, that difference would drive current
along the cable and through both transceivers.

IEEE 802.3 requires each twisted-pair port to be isolated from the rest of
the equipment, including its frame ground (the metal frame or enclosure), and
to pass at least one of the tests in :numref:`tbl-magnetics-hipot`. The
isolation clauses as quoted in IEEE 802.3 working documents contain no
exception for equipment inside one enclosure [MAG-POTTERF]_. A test like this is commonly called a *hipot test* ("high
potential").

.. _tbl-magnetics-hipot:

.. list-table:: Isolation tests in IEEE 802.3. A port must pass at least
                one [MAG-WALKER]_ [MAG-INTERP0311]_.
   :header-rows: 1
   :widths: 30 70

   * - Test
     - Requirement
   * - AC voltage
     - 1500 V rms at 50 Hz to 60 Hz for 60 s (2121 V peak)
   * - DC voltage
     - 2250 V DC for 60 s
   * - Impulses, port without Power over Ethernet
     - Ten 2400 V impulses of alternating polarity, at least 1 s apart. Each
       rises in 1.2 µs and falls to half its peak in 50 µs ("1.2/50 µs").
   * - Impulses, port with Power over Ethernet
     - Ten 1500 V impulses with a 10/700 µs shape
   * - Pass condition
     - No insulation breakdown, and at least 2 MΩ measured at 500 V DC
       afterwards

The AC and DC tests are applied as described in the safety standard
IEC 60950-1, or its successor IEC 62368-1 in newer text [MAG-WALKER]_. An
interpretation request to the IEEE 802.3 working group (2-03/11) states that
earlier interpretations treated the test as protection of the interface
against common-mode voltages rather than as a safety test, and notes that
protection diodes connected to ground defeat isolation [MAG-INTERP0311]_.

For Power over Ethernet, :clause:`33` also distinguishes *Environment A* (a
network inside one building and one low-voltage power distribution system)
from *Environment B* (a network that crosses between buildings or power
systems). Environment A relaxes only the isolation *between the power
circuits of different ports*; it does not relax the isolation between the
MDI and the transceiver circuits [MAG-HSTEWART]_.

Magnetics data sheets give the isolation the part withstands, usually
1500 V rms for 60 s [MAG-PULSE]_ [MAG-WURTH]_ [MAG-BEL]_.

F2 and F3: common-mode rejection, level shifting and DC blocking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any voltage on a pair can be split into two parts:

* the *differential-mode* voltage, the difference between the two wires,
  which carries the data; and
* the *common-mode* voltage, the average of the two wires measured against
  a ground, which carries no data.

A transformer couples only the voltage *across* a winding, so it passes the
differential signal and blocks the common-mode voltage and DC. Each side of
the transformer can therefore sit at its own voltage: the transceiver near
its own supply rails, the cable at whatever voltage the far end, a ground
difference or Power over Ethernet puts on it. Real transformers let some
common-mode signal through their inter-winding capacitance at high
frequencies, which is why a choke is added (F7). Magnetics data sheets give
the rejection as "common-mode rejection" or "differential to common-mode
rejection": for example 33 dB to 43 dB from 30 MHz to 100 MHz for the Pulse
H5007NL [MAG-PULSE]_, and 30 dB to 35 dB for the Bel 0826-1G1T-23-F
[MAG-BEL]_.

F4: impedance matching and return loss
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ethernet transceivers drive and terminate a 100 Ω differential load
directly, so the transformer ratio is 1:1 and the 100 Ω cable appears as
100 Ω at the transceiver. How closely a port matches 100 Ω is measured by
its *return loss*: how much weaker the reflected signal is than the signal
arriving at the port.

**Reflection and return loss.** The reflection is set by the difference
between the port impedance and the cable impedance:

.. math::

   \Gamma = \frac{Z - Z_0}{Z + Z_0}
   \qquad
   \text{RL} = -20 \log_{10} \lvert \Gamma \rvert

where:

* :math:`\Gamma` is the reflection coefficient (no unit): the reflected
  voltage divided by the arriving voltage;
* :math:`Z` is the impedance of the port, in Ω;
* :math:`Z_0` is the impedance of the cable, nominally 100 Ω, allowed to be
  85 Ω to 115 Ω [MAG-UNH40]_;
* :math:`\text{RL}` is the return loss, in dB.

IEEE 802.3 :clause:`40.8.3.1` requires a 1000BASE-T port to have a return loss
of at least 16 dB from 1 MHz to 40 MHz [MAG-UNH40]_. To see what that means
for the port impedance, solve for :math:`\lvert\Gamma\rvert` and then for a
purely resistive :math:`Z` with :math:`Z_0 = 100\ \Omega`:

.. math::

   \lvert\Gamma\rvert_\text{max} = 10^{-16/20} = 0.158

.. math::

   Z_\text{max} = Z_0 \frac{1 + 0.158}{1 - 0.158} = 137.7\ \Omega
   \qquad
   Z_\text{min} = Z_0 \frac{1 - 0.158}{1 + 0.158} = 72.6\ \Omega

So the port only needs to be within roughly 73 Ω to 138 Ω of a 100 Ω cable,
but the transceiver and everything between it and the cable share that
budget. Microchip recommends magnetics with at least 2 dB of margin on this
limit [MAG-ENT98]_. Above 40 MHz the limit falls to
:math:`10 - 20 \log_{10}(f / 80\ \text{MHz})` dB, which at
:math:`f = 100\ \text{MHz}` is
:math:`10 - 20 \times \log_{10}(1.25) = 10 - 20 \times 0.0969 = 8.1` dB
[MAG-UNH40]_.

The *insertion loss* is the signal lost passing through the magnetics.
Gigabit magnetics specify at most 1 dB from 1 MHz to 100 MHz
[MAG-PULSE]_ [MAG-WURTH]_, an amplitude ratio of
:math:`10^{-1/20} = 0.891`: at most 11 % of the signal amplitude is lost.

100BASE-TX, through the FDDI standard ANSI X3.263 that :clause:`25` adopts
(FDDI is an older 100 Mbit/s network standard), additionally requires the
port impedance to be "nominally resistive with a phase angle less than 3°"
from 2 MHz to 80 MHz [MAG-SNLA088]_. This matters for capacitor coupling
(see `Coupling capacitor size`_).

F5: low-frequency response, droop and baseline wander
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A transformer cannot pass DC and passes low frequencies poorly. The reason
is its *magnetising inductance*: the inductance of one winding with the other
left open, given in data sheets as the *open-circuit inductance* (OCL). This
inductance sits in parallel with the signal path and shunts low frequencies
away. If the transmitter holds a constant voltage, the voltage on the cable
side decays towards zero; this is called *droop*. Long stretches of data
whose average is not zero make the received signal's average level drift;
this is called *baseline wander*.

**Model.** Treat the transformer as an ideal 1:1 transformer with the
inductance :math:`L` in parallel. Seen from :math:`L`, the 100 Ω source and
the 100 Ω cable are in parallel. The circuit is then a first-order high-pass
filter, and droop is an exponential decay with time constant :math:`\tau`:

.. math::

   R_\text{p} = \frac{R_\text{s} R_\text{L}}{R_\text{s} + R_\text{L}}
   \qquad
   \tau = \frac{L}{R_\text{p}}
   \qquad
   f_\text{c} = \frac{1}{2\pi\tau} = \frac{R_\text{p}}{2\pi L}

where:

* :math:`R_\text{s}` is the transceiver's output resistance, 100 Ω (it
  terminates the line);
* :math:`R_\text{L}` is the cable impedance, 100 Ω;
* :math:`R_\text{p}` is their parallel combination, in Ω;
* :math:`L` is the magnetising inductance, in H;
* :math:`\tau` is the time constant of the droop, in s;
* :math:`f_\text{c}` is the corner frequency of the high-pass filter, in Hz.

This model ignores the leakage inductance and the winding capacitance, which
matter only at high frequencies.

**Corner frequency with 350 µH.** With :math:`R_\text{p} = 100 \times 100 /
200 = 50\ \Omega` and :math:`L = 350\ \mu\text{H}` (the usual data-sheet
value [MAG-KSZ9031]_ [MAG-WURTH]_):

.. math::

   f_\text{c} = \frac{50\ \Omega}{2\pi \times 350\ \mu\text{H}}
   = \frac{50}{2.199 \times 10^{-3}}\ \text{Hz}
   = 22.7\ \text{kHz}

Signals below about 23 kHz are attenuated. Ethernet signals have little
energy that low, but long runs of the same symbol do.

**Minimum inductance for 1000BASE-T.** :clause:`40.6.1.2.2` requires that, 500 ns
after the start of a constant level in a test pattern, more than 73.1 % of
the voltage remains [MAG-UNH40]_. In the model the remaining fraction is
:math:`e^{-t/\tau}`, so:

.. math::

   e^{-t/\tau} \ge k
   \quad\Rightarrow\quad
   \tau \ge \frac{t}{\ln(1/k)}
   \quad\Rightarrow\quad
   L \ge \tau R_\text{p}

where:

* :math:`t` is the time after the step, 500 ns [MAG-UNH40]_;
* :math:`k` is the fraction that must remain, 0.731 [MAG-UNH40]_.

Substituting: :math:`\ln(1/0.731) = 0.313`, so
:math:`\tau \ge 500\ \text{ns} / 0.313 = 1.60\ \mu\text{s}`, and
:math:`L \ge 1.60\ \mu\text{s} \times 50\ \Omega = 80\ \mu\text{H}`.
The same result appears in an IEEE 802.3 maintenance proposal [MAG-TRACY]_
and in IEEE 802.3bu work on power over a single pair [MAG-GARDNER14]_. With
350 µH, :math:`\tau = 350\ \mu\text{H} / 50\ \Omega = 7.0\ \mu\text{s}` and
:math:`e^{-0.5/7.0} = 0.931`: 93 % remains, a large margin over 73.1 %.

**Why 350 µH.** The 350 µH figure comes from 100BASE-TX: ANSI X3.263
section 9.1.7 requires at least 350 µH at the transmitter "with any DC
bias current between 0 mA and +8 mA", to limit baseline wander, and notes
that DC bias can change the inductance by about 2:1 [MAG-LAW]_. Data sheets
therefore quote the inductance at 100 kHz, 100 mV and 8 mA of DC bias
[MAG-KSZ9031]_. IEEE 802.3at added an alternative droop test for
transmitters in equipment that supplies or takes more than 13 W of Power
over Ethernet [MAG-TRACY]_.

For a design without a transformer, these two numbers become the targets
for whatever replaces the transformer: a time constant of at least 1.6 µs
for 1000BASE-T, and about 7 µs to match the low-frequency behaviour that
100BASE-TX receivers expect.

F6: common-mode termination of the cable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each pair, taken as a whole, also forms a transmission line with every other
pair. Common-mode currents travel along these lines and, if their ends are
left open, reflect back and forth and radiate. Each cable-side centre tap
therefore goes through a 75 Ω resistor to a node shared by the four pairs.
Between any two pairs there are then two resistors in series, 150 Ω, close to
the roughly 145 Ω pair-to-pair impedance of Category 5 cable (a common grade
of Ethernet cable), so the energy is absorbed in the resistors instead of
radiated. The patent that describes it reports "upwards of approximately
10 dB improvement in emissions and susceptibility" [MAG-SMITH]_. This network
is widely called the *Bob Smith termination*, after the inventor's name.

The shared node goes to chassis ground through one capacitor, usually
1000 pF rated 2 kV [MAG-KSZ9031]_ [MAG-WURTH]_ [MAG-BEL]_. Microchip notes
that the capacitor is not part of the patent [MAG-ENT98]_. Its impedance
shows why a capacitor is used:

.. math::

   \lvert Z_C \rvert = \frac{1}{2\pi f C}

where :math:`f` is the frequency in Hz and :math:`C = 1000\ \text{pF}`. At
:math:`f = 50\ \text{Hz}`:
:math:`2\pi \times 50 \times 10^{-9} = 3.14 \times 10^{-7}\ \text{S}`, so
:math:`\lvert Z_C \rvert = 3.2\ \text{M}\Omega`. At :math:`f = 30\ \text{MHz}`:
:math:`2\pi \times 3 \times 10^{7} \times 10^{-9} = 0.189\ \text{S}`, so
:math:`\lvert Z_C \rvert = 5.3\ \Omega`. The termination works at signal
frequencies, but at mains frequencies the capacitor is nearly an open
circuit and does not undo the isolation. It sits across the isolation
barrier, so it is rated for the isolation test.

F7: filtering common-mode noise
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A *common-mode choke* is two windings on one core, one in each wire of a
pair. The data current flows out on one wire and back on the other, so the
magnetic fields of the two windings cancel and the data sees almost no
inductance. A common-mode current flows the same way on both wires, the
fields add, and it sees a high impedance.

Noise from the board couples equally onto both traces of a pair and becomes
common-mode voltage; any imbalance in the transmitter does the same. An
unshielded twisted pair carrying common-mode current radiates, and that
radiation is what fails radio-interference limits. In the other direction,
the cable picks up common-mode noise from its surroundings; the choke and
transformer keep it from the receiver ("electromagnetic immunity")
[MAG-ENT98]_.

Microchip recommends the choke on the cable side of the transformer, and
reports less margin in the transmit waveform tests with it on the
transceiver side [MAG-ENT98]_. Some magnetics add a third part per pair, an
*autotransformer* (one centre-tapped winding across the pair) that gives
common-mode current a low-impedance path to the termination; parts with a
transformer, choke and autotransformer per pair are sold as "12-core", those
without as "8-core" [MAG-ENT98]_.

F8: surges and electrostatic discharge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A common-mode surge on the cable (the whole cable rising in voltage against
the equipment) appears across the transformer's isolation, which holds it up
to its rating; the transceiver sees only what couples through the winding
capacitance. A differential surge (between the wires of a pair) passes
through the transformer like a signal and is clamped by protection diodes.
TI's guidance places these diodes on the transceiver side of the magnetics,
because on the cable side large common-mode voltages could make them conduct
and fail [MAG-SNLA387]_. The numbers for these events are in
`Voltages and events at the cable`_.

F9: biasing the line driver through the circuit-side centre tap
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

How the circuit-side centre tap is connected depends on the transceiver's
line driver (:numref:`fig-magnetics-centre-tap-bias`; see also
:doc:`phy-electrical`):

* A **current-mode driver** switches a current between the two pins of the
  pair, and its transistors only sink current. The current is supplied
  through the centre tap, which is tied to a supply. TI's DP83848 needs a
  49.9 Ω resistor from each pin to the 3.3 V analog supply and the centre
  taps pulled up to the same supply [MAG-SDAA089]_. Microchip describes such
  a driver for 1000BASE-T as about 40 mA per pair [MAG-ENT106]_.
* A **voltage-mode driver** drives each pin from a low impedance, sets its
  own common-mode voltage, and has its termination on the chip. The centre
  tap must not be tied to a supply; each centre tap goes to ground through
  its own 0.1 µF capacitor [MAG-KSZ9031]_ [MAG-DP83867]_. Microchip gives
  the peak current of such a driver as 10 mA [MAG-ENT106]_.

Only a voltage-mode driver can work without a transformer, since a
current-mode driver gets its supply through the transformer
[MAG-ENT114]_.

.. _fig-magnetics-centre-tap-bias:

.. graphviz:: magnetics/centre-tap-bias.dot
   :caption: Circuit-side centre tap for one pair. Top: a current-mode
             driver takes its current through the centre tap, which is tied
             to a supply and decoupled to ground. Bottom: a voltage-mode
             driver sets its own common-mode voltage; the centre tap only
             goes to ground through a capacitor.
   :alt: Two schematics. Top: transceiver with switched current sinks, each
         pin with a 50 ohm resistor to a supply rail, the transformer centre
         tap tied to the same rail and to a 0.1 microfarad capacitor.
         Bottom: transceiver with push-pull drivers, the transformer centre
         tap connected only to a 0.1 microfarad capacitor to signal ground.
   :align: center

F10 and F11: Power over Ethernet through the centre taps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Power over Ethernet (PoE) sends DC power on the data pairs. The *power
sourcing equipment* puts one polarity on both wires of one pair and the other
polarity on both wires of another pair; a pair carries no differential DC, so
the data is unaffected. *Alternative A* uses the pairs on pins 1, 2 and 3, 6;
*Alternative B* the pairs on pins 4, 5 and 7, 8; :clause:`145` (four-pair power)
uses both [MAG-SLVAF59]_. The *powered device* must accept power on either
set of pairs in either polarity, so it uses two bridge rectifiers
[MAG-TPS2376H]_ (:numref:`fig-magnetics-poe`).

In a transformer the current enters at the cable-side centre tap and splits
into the two halves of the winding, flowing outward in opposite directions.
Their magnetic fields cancel, so the core is not biased by the full current;
only the difference between the two wires' currents (caused by unequal wire
resistance) biases it [MAG-TPS2376H]_.

.. _tbl-magnetics-poe-numbers:

.. list-table:: Power over Ethernet numbers that constrain the front end
                [MAG-EA8023BT]_
   :header-rows: 1
   :widths: 40 60

   * - Quantity
     - Value
   * - Power sourcing equipment output voltage
     - Type 1: 44 V to 57 V; Type 2 and 3: 50 V to 57 V; Type 4: 52 V to
       57 V
   * - Maximum voltage at a powered device
     - 57 V
   * - Highest current in one pair (Class 8, with allowed unbalance)
     - 938 mA (865 mA with perfect balance)
   * - Powered device detection signature
     - 23.7 kΩ to 26.3 kΩ, measured with 2.7 V to 10.1 V
   * - Powered device input capacitance during detection
     - 50 nF to 120 nF
   * - Series inductance of the powered device input
     - less than 100 µH
   * - Classification voltage (power sourcing equipment)
     - 15.5 V to 20.5 V

The transformer also keeps the transceiver out of the way of detection and
classification (F11): at DC the transceiver is not connected to the cable at
all, so the power sourcing equipment sees only the powered device's signature
resistor and capacitor. Any replacement must keep the data circuits within
the signature limits above, including the capacitance and series inductance
limits.

.. _fig-magnetics-poe:

.. graphviz:: magnetics/poe-centre-taps.dot
   :caption: Taking Power over Ethernet from the cable-side centre taps
             ("CT") of standard magnetics in a powered device. The bridge
             rectifiers make the input independent of which pairs, and which
             polarity, the source uses.
   :alt: Block diagram: the transceiver connects to the circuit side of
         PoE-rated magnetics, whose cable side goes to the RJ45 pins. The
         four cable-side centre taps go in pairs to two bridge rectifiers,
         which both feed the powered-device interface and power converter.
         A 75 ohm termination through 10 nanofarad blocking capacitors also
         connects to the magnetics.
   :align: center

In PoE designs each 75 Ω termination resistor needs a series capacitor (about
10 nF) to block the DC [MAG-ENT98]_.

Voltages and events at the cable
--------------------------------

Whatever replaces the transformer must survive the voltages in
:numref:`tbl-magnetics-cable-events` and keep the signal intact.

.. _tbl-magnetics-cable-events:

.. list-table:: Voltages and events at an Ethernet port
   :header-rows: 1
   :widths: 30 28 42

   * - Event
     - Size
     - Duration and source
   * - 1000BASE-T signal
     - 0.67 V to 0.82 V peak differential in the test pattern
     - continuous [MAG-UNH40]_
   * - 100BASE-TX signal
     - 0.95 V to 1.05 V peak differential
     - continuous [MAG-UNH25]_
   * - 10BASE-T signal
     - 2.2 V to 2.8 V peak differential
     - continuous [MAG-INTERP1196]_
   * - Power over Ethernet
     - up to 57 V DC between pairs; up to 938 mA per pair
     - continuous [MAG-EA8023BT]_
   * - Isolation test
     - 1500 V rms (2121 V peak), or 2250 V DC
     - 60 s [MAG-WALKER]_
   * - Isolation impulse test
     - 2400 V (1500 V with PoE)
     - 1.2/50 µs (10/700 µs with PoE), ten times [MAG-WALKER]_
   * - Human-body model discharge (chip handling)
     - 2 kV into 100 pF through 1.5 kΩ: 1.33 A peak, 0.2 mJ
     - about 200 ns [MAG-ESDA]_
   * - System-level discharge, IEC 61000-4-2, contact, level 4
     - 8 kV from 150 pF through 330 Ω: 4.8 mJ
     - rise 0.7 ns to 1 ns [MAG-SLVA711]_ [MAG-POMMERENKE]_
   * - Surge, IEC 61000-4-5, data line
     - 1 kV to 2 kV through 42 Ω: about 24 A to 48 A peak
     - 1.2/50 µs voltage, 8/20 µs current [MAG-SLVA711]_
   * - Charged cable discharge
     - "as high as a few thousand volts", low source impedance
     - tests with cables charged to 0.75 kV to 5 kV; events longer than
       600 ns [MAG-SNLA087]_ [MAG-DEATHERAGE]_

The energies in the table are the energy stored in the test capacitor,
:math:`E = \tfrac{1}{2} C V^2`, where :math:`E` is the energy in J,
:math:`C` the test capacitance in F and :math:`V` the test voltage in V. For
the human-body model:
:math:`E = 0.5 \times 100\ \text{pF} \times (2000\ \text{V})^2 = 0.2\ \text{mJ}`,
and the peak current is :math:`I = V / R = 2000\ \text{V} / 1500\ \Omega =
1.33\ \text{A}`. For the system-level test:
:math:`E = 0.5 \times 150\ \text{pF} \times (8000\ \text{V})^2 = 4.8\ \text{mJ}`.
For the surge, the peak current is the test voltage divided by the source
resistance: :math:`1000\ \text{V} / 42\ \Omega = 23.8\ \text{A}`.

These events differ in kind, and that decides what can protect against
them:

* **Short, energy-limited events** such as the human-body model are what
  on-chip protection is designed for. The protection diodes and clamps in an
  I/O cell conduct for a few hundred nanoseconds and absorb a bounded
  charge. The gf180mcu I/O library targets 2000 V
  human-body model [MAG-GFIO]_. A system-level discharge carries about 24
  times the energy (4.8 mJ against 0.2 mJ) and a peak current of tens of
  amps, so it is normally absorbed by an external protection diode.
* **Long or large events** (surges, charged cables) deliver tens of amps for
  microseconds. They need external protection sized for them.
* **Sustained voltages** (Power over Ethernet at 57 V, the 60 s isolation
  test at 1500 V rms) are not events at all: a clamp that conducted during
  them would be destroyed or would break the isolation. They must be held
  off by something that withstands the full voltage continuously.

Limits of the gf180mcu process
------------------------------

Three different kinds of limit apply when deciding what can be built on the
chip.

(a) **Ratings of the standard devices and cells.** These are the
    conservative continuous operating limits the foundry guarantees.
(b) **Physical limits of the process layers.** Oxide, junction and
    dielectric breakdown, where documented. A circuit made of standard
    devices can sometimes exceed (a) by stacking devices so that each sees
    only part of the voltage, but it cannot exceed (b) for any layer that
    sees the full voltage.
(c) **What custom structures could reach.** Structures not in the standard
    library, such as stacked or cascoded transistors in isolated wells,
    custom drain-extended transistors, series capacitor stacks, custom
    clamps, and active inductors. These need design and characterisation
    work but are not ruled out unless (b) rules them out.

.. list-table:: gf180mcu limits from the PDK documentation [MAG-GF180]_.
                "Not documented" means the PDK gives no value.
   :header-rows: 1
   :widths: 34 33 33

   * - Item
     - Rated operation, limit kind (a)
     - Breakdown, limit kind (b)
   * - 3.3 V transistor
     - 3.3 V; maximum DC gate voltage 3.63 V
     - gate oxide at least 7 V; drain at least 7 V
   * - 5 V and 6 V transistor (6 V gate oxide)
     - 5 V or 6 V; maximum DC gate voltage 6.5 V
     - gate oxide at least 12 V; drain at least 8.5 V
   * - 10 V drain-extended transistor (LDMOS)
     - 10 V drain (separate 10 V high-voltage process models; its well is
       tied to the substrate)
     - drain at least 13.2 V
   * - N-well to substrate junction
     - —
     - at least 10 V
   * - Deep N-well to substrate junction
     - —
     - not documented (the SPICE model uses about 30 V)
   * - MIM capacitor, 1.0 fF/µm²
     - 20 V
     - at least 20 V
   * - MIM capacitor, 1.5 fF/µm²
     - 10 V
     - at least 10 V
   * - MIM capacitor, 2.0 fF/µm²
     - 6.6 V
     - not documented
   * - Oxide between metal layers
     - —
     - not documented; about 1.15 µm per layer, five metal layers in the
       wafer.space flow
   * - I/O cell protection
     - target 2000 V human-body model, 500 V charged-device model
     - —

Whether the wafer.space flow (which uses the open_pdks "gf180mcuD" variant
with five metal layers and a MIM capacitor) offers the 10 V LDMOS is not
documented.

What follows from these limits:

* **Continuous 57 V on a chip pin.** Any node on the chip has some junction
  to the substrate that sees its full voltage. The highest documented
  junction breakdown is 10 V (N-well to substrate), and the highest value in
  the models is about 30 V (deep N-well, not a specification). Stacking
  transistors divides the voltage between their drains but not between a
  well and the substrate. Holding off 57 V (plus surges and the
  isolation test) on a pin that connects directly to a cable wire is
  therefore ruled out by (b), unless a custom structure with a documented
  higher breakdown is characterised.
* **Isolation through on-chip dielectric.** The oxide between the first and
  fifth metal layers is about 4.6 µm to 5.8 µm thick (an estimate from four
  layers of about 1.15 µm to 1.45 µm). TI gives the short-term strength of
  silicon dioxide as about 500 V rms per µm [MAG-SSZY028]_, so the stack
  would break down at roughly :math:`4.6 \times 500 = 2300` V rms to
  :math:`5.8 \times 500 = 2900` V rms in a short test, an *estimate*. That
  is above the 1500 V rms test level, but with no margin for a lifetime of
  use. Commercial capacitive isolators use at least 13.5 µm of oxide with
  two capacitors in series [MAG-SSZY024]_, and a published digital isolator
  in standard CMOS reached 2.5 kV [MAG-KAERIYAMA]_. On-chip isolation is
  not ruled out by (b), but it is unproven in this process.
* **Isolation capacitors large enough to carry the signal.** The data needs
  tens of nanofarads per wire (see `Coupling capacitor size`_). On-chip
  capacitance is far too small for that, as the next calculation shows.

**Area of an on-chip coupling capacitor (estimate).** The area needed is the
capacitance divided by the capacitance per area:

.. math::

   A = \frac{C}{c_\text{A}}

where:

* :math:`A` is the area, in µm²;
* :math:`C` is the capacitance needed, 16 nF per wire (the 1000BASE-T
  minimum calculated in `Coupling capacitor size`_);
* :math:`c_\text{A}` is the capacitance per area: 2.0 fF/µm² for the
  densest MIM capacitor (rated 6.6 V) [MAG-GF180]_, or, for a capacitor
  using the whole 5 µm oxide stack, :math:`\varepsilon_0 \varepsilon_\text{r}
  / d = 8.854 \times 10^{-12} \times 3.9 / (5 \times 10^{-6}) = 6.9 \times
  10^{-6}\ \text{F/m}^2 = 0.0069\ \text{fF/µm}^2` (silicon dioxide,
  :math:`\varepsilon_\text{r} = 3.9`).

With the MIM capacitor:
:math:`A = 16\ \text{nF} / 2.0\ \text{fF/µm}^2 = 8 \times 10^6\ \mu\text{m}^2
= 8\ \text{mm}^2` per wire, 64 mm² for eight wires, and the capacitor is
rated for only 6.6 V. With the thick oxide stack:
:math:`A = 16\ \text{nF} / 0.0069\ \text{fF/µm}^2 \approx 2300\ \text{mm}^2`
per wire. The first would take tens of square millimetres of die area for
one port; the second is far beyond any practical die. On-chip capacitors can therefore isolate only a signal that has
been converted to a high-frequency form (as digital isolators do), with
active circuits on both sides of the barrier. They cannot simply replace the
external coupling capacitors.

Doing each job without a transformer
------------------------------------

Several kinds of equipment already connect twisted-pair cables without
transformers, and they show which techniques are proven:

* **Capacitor-coupled 10/100 Mbit/s.** TI documents connecting its DP83848
  family through 33 nF capacitors per wire, for connections "shorter than
  1 meter", at forced 100 Mbit/s [MAG-SNLA088]_. Microchip documents
  direct connection of its voltage-mode transceivers through DC-blocking
  capacitors on one board or over a backplane [MAG-ENT114]_.
* **Single-pair automotive and industrial Ethernet** (100BASE-T1,
  1000BASE-T1, 10BASE-T1L). These use 100 nF DC-blocking capacitors, a
  common-mode choke and a common-mode termination of two 1 kΩ resistors and a
  4.7 nF capacitor, with no transformer [MAG-DP83TC811]_ [MAG-OA100T1]_.
  Their clauses list no isolation requirement for data-only ports
  [MAG-LEWIS]_ [MAG-POTTERF]_, and the capacitors are rated only 50 V to
  100 V [MAG-OA100T1]_.
* **Power over a single pair** (IEEE 802.3bu and 802.3cg). Power is put on
  the pair through inductors and taken off the data path by capacitors, with
  the inductor sized from the transmitter droop requirement [MAG-GARDNER14]_
  [MAG-DP83TD510E]_ [MAG-TDKSPE]_.
* **Transformerless Power over Ethernet** has been described in patents
  (per-wire inductors or active circuits for the power, high-voltage
  capacitors for the data) [MAG-US8132027]_ [MAG-US7851938]_
  [MAG-US9189036]_, but no product data sheet was found.

No vendor document was found that covers capacitor-coupled 1000BASE-T over a
full-length cable.

The rest of this section takes each function in turn. For each, it lists
options using external passive parts and options built on the chip, with
their requirements and risks. The choice between them is an open decision.

Coupling capacitor size
~~~~~~~~~~~~~~~~~~~~~~~

Replacing the transformer with a capacitor in each wire makes the data path a
series capacitor instead of a parallel inductor. Three requirements set the
smallest capacitor. In all three the model is: the transceiver as a 100 Ω
source, the cable as a 100 Ω load, and one capacitor :math:`C_\text{w}` in
each of the two wires. The two capacitors are in series around the loop, so
the pair sees

.. math::

   C_\text{pair} = \frac{C_\text{w}}{2}

**1. Phase angle (100BASE-TX).** The port must look resistive within 3° from
2 MHz [MAG-SNLA088]_. A series capacitor adds a reactance
:math:`X = 1 / (2\pi f C_\text{pair})` in series with the 100 Ω, and the
phase angle is :math:`\arctan(X / 100\ \Omega)`. So:

.. math::

   X_\text{max} = 100\ \Omega \times \tan 3^\circ
   \qquad
   C_\text{pair} \ge \frac{1}{2\pi f X_\text{max}}

where :math:`f = 2\ \text{MHz}`. Substituting:
:math:`\tan 3^\circ = 0.0524`, so :math:`X_\text{max} = 5.24\ \Omega`;
:math:`C_\text{pair} \ge 1 / (2\pi \times 2 \times 10^6 \times 5.24) =
15.2\ \text{nF}`; and :math:`C_\text{w} \ge 30.4\ \text{nF}`. TI calculates
30.42 nF and recommends the next standard value, 33 nF [MAG-SNLA088]_.

**2. Return loss (1000BASE-T).** The port must have at least 16 dB return
loss from 1 MHz. With the capacitor in series with a perfectly matched
100 Ω port, the reflection is
:math:`\lvert\Gamma\rvert = X / \sqrt{(2 \times 100\ \Omega)^2 + X^2}`. Setting
:math:`\lvert\Gamma\rvert = 0.158` (16 dB, from F4) and solving:

.. math::

   X_\text{max} = \frac{200\ \Omega \times 0.158}{\sqrt{1 - 0.158^2}}
   = 32.1\ \Omega

At :math:`f = 1\ \text{MHz}`: :math:`C_\text{pair} \ge 1 / (2\pi \times 10^6
\times 32.1) = 4.96\ \text{nF}`, so :math:`C_\text{w} \ge 9.9\ \text{nF}`.
This uses the whole 16 dB budget for the capacitors alone, so in practice
they must be larger.

**3. Droop (1000BASE-T) and baseline wander.** The series capacitor forms a
high-pass filter with the source and load resistances in series, so its time
constant is

.. math::

   \tau = (R_\text{s} + R_\text{L}) \, C_\text{pair}
   \qquad
   C_\text{w} = \frac{2\tau}{R_\text{s} + R_\text{L}}

where :math:`R_\text{s} + R_\text{L} = 200\ \Omega`. For the 1000BASE-T droop
limit, :math:`\tau \ge 1.6\ \mu\text{s}` (from F5):
:math:`C_\text{w} \ge 2 \times 1.6\ \mu\text{s} / 200\ \Omega = 16\ \text{nF}`.
To match a 350 µH transformer (:math:`\tau = 7.0\ \mu\text{s}`):
:math:`C_\text{w} = 2 \times 7.0\ \mu\text{s} / 200\ \Omega = 70\ \text{nF}`.

.. list-table:: Smallest coupling capacitor per wire (model above; the
                transceiver's own baseline-wander correction can relax the
                last row)
   :header-rows: 1
   :widths: 50 25 25

   * - Requirement
     - Capacitor per wire
     - Source of the limit
   * - 1000BASE-T return loss at 1 MHz (no margin)
     - 9.9 nF
     - [MAG-UNH40]_
   * - 1000BASE-T droop, 500 ns
     - 16 nF
     - [MAG-UNH40]_
   * - 100BASE-TX phase angle at 2 MHz
     - 30.4 nF (33 nF used)
     - [MAG-SNLA088]_
   * - Same low-frequency corner as a 350 µH transformer
     - 70 nF
     - [MAG-LAW]_

For example, 100 nF per wire gives
:math:`\tau = 200\ \Omega \times 50\ \text{nF} = 10\ \mu\text{s}`, a corner
frequency of :math:`1 / (2\pi \times 10\ \mu\text{s}) = 16\ \text{kHz}`, and
95 % of the voltage left after 500 ns.

F1 without a transformer: isolation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Options:

* **External high-voltage coupling capacitors** (proven in patents and in
  TI's note, which says "high voltage multi-layer ceramic capacitors are
  readily available" [MAG-SNLA088]_ [MAG-US8132027]_). A capacitor blocks DC,
  so it passes the 2250 V DC test (the second of the three allowed tests)
  if it is rated for it. Ceramic capacitors of 10 nF rated 2000 V DC with a
  2400 V DC withstand test exist in a 4.5 mm × 3.2 mm package
  [MAG-KEMET1812]_; capacitors of 33 nF to 100 nF at that rating were not
  found and may need several in parallel.
* **Safety-rated capacitors.** Capacitors certified for bridging insulation
  (class Y2 under IEC 60384-14) were found only up to 4.7 nF in surface-mount
  packages [MAG-KEMETCAS]_, below the 16 nF needed. Whether the
  IEEE 802.3 isolation is a safety function for evampire boards (and so
  needs safety-rated parts) is a question for the product safety standard,
  not answered here.
* **On-chip isolation** with a second, line-side circuit powered separately
  and a high-frequency link across an on-chip barrier. Not ruled out by the
  process limits, but unproven at 1500 V rms in this process (see
  `Limits of the gf180mcu process`_), and it needs the line-side circuit to
  be on a separate die or an insulating substrate, because both sides would
  otherwise share the silicon substrate.
* **No isolation**, for boards used only inside one enclosure with a shared
  ground. This does not meet IEEE 802.3 (there is no exception for this
  case in the quoted clauses [MAG-POTTERF]_).

The AC test (1500 V rms) is hard to pass with capacitors because they
conduct at 50 Hz. The current is :math:`I = 2\pi f C_\text{total} V`, where
:math:`C_\text{total}` is all eight capacitors in parallel (the test is
applied between all MDI wires together and the equipment):

.. list-table:: Current through the coupling capacitors in the 1500 V rms,
                50 Hz test (:math:`I = 2\pi \times 50\ \text{Hz} \times
                8 C_\text{w} \times 1500\ \text{V}`)
   :header-rows: 1

   * - Capacitor per wire
     - Total capacitance
     - Test current
   * - 10 nF
     - 80 nF
     - 37.7 mA
   * - 33 nF
     - 264 nF
     - 124 mA
   * - 100 nF
     - 800 nF
     - 377 mA

These currents are far above what a hipot tester normally allows before
deciding that the insulation has failed (an assumption; the trip current is
set by the tester and the safety standard, not by IEEE 802.3). A
capacitor-coupled port should therefore be designed for the DC test.

Isolation also has to hold in the power path. With capacitor-coupled data,
the Power over Ethernet circuits connect to the cable directly, so they must
be isolated from the rest of the board by an isolated power converter (as a
standard powered device usually is) for the port to pass the test. This is
an inference, not a documented requirement [MAG-US8132027]_.

F2 without a transformer: common-mode rejection and level shifting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The coupling capacitors block DC and slow changes of common-mode voltage, so
the chip-side common-mode voltage is set by the chip, not by the cable. Fast
common-mode changes pass through the capacitors and must be handled on the
chip-side nodes.

**Common-mode at mains frequency (estimate).** This estimates how much of a
slow ground difference between the two ends of the cable reaches the chip.
Suppose the cable's common-mode voltage moves at 50 Hz relative to the chip
ground, and the chip holds each pair's common-mode node at its bias voltage
through a resistance. The two capacitors of the pair act in parallel for
common-mode signals, and form a divider with that resistance:

.. math::

   \frac{V_\text{chip}}{V_\text{cable}} =
   \frac{R_\text{cm}}{\sqrt{R_\text{cm}^2 + X_\text{cm}^2}}
   \qquad
   X_\text{cm} = \frac{1}{2\pi f \cdot 2 C_\text{w}}

where:

* :math:`V_\text{chip} / V_\text{cable}` is the fraction of the cable's
  common-mode voltage that appears at the chip (no unit);
* :math:`R_\text{cm}` is the resistance from the chip-side common-mode node to
  the bias voltage, in Ω; 1 kΩ is *assumed* here;
* :math:`X_\text{cm}` is the reactance of the pair's two coupling capacitors
  in parallel, in Ω;
* :math:`f` is the frequency, 50 Hz;
* :math:`C_\text{w}` is the coupling capacitor per wire, 33 nF (from
  `Coupling capacitor size`_).

Substituting:
:math:`X_\text{cm} = 1 / (2\pi \times 50 \times 66\ \text{nF}) = 48.2\ \text{kΩ}`
and the fraction is :math:`1 / \sqrt{1 + 48.2^2} = 0.021`: about 2 % of a
mains-frequency ground difference reaches the chip. At signal frequencies
the capacitors pass common-mode noise almost completely, so rejection there
must come from the receiver and from a choke or termination.

Options:

* **External common-mode choke**, as in single-pair automotive Ethernet
  (proven; for example 200 µH chokes with −42 dB common-mode rejection from
  10 MHz to 100 MHz for 100BASE-T1 [MAG-DP83TC811]_).
* **On-chip receiver with a wide common-mode range and high rejection**, and
  a **common-mode feedback loop** that senses the pair's common-mode voltage
  and drives it back to the bias point. Integrated receivers for other
  twisted-pair buses show what is possible in high-voltage processes: CAN
  receivers with a ±12 V common-mode range and ±58 V fault protection
  [MAG-TCAN1044]_, RS-485 receivers with ±25 V range and ±70 V fault
  protection [MAG-THVD2450]_. In gf180mcu the range is limited to the
  supplies of the 5 V or 6 V devices unless a custom structure is used.
* **Active common-mode choke**: a circuit that senses and cancels
  common-mode current. A commercial part adds "up to 10dB" of common-mode
  suppression from 1 MHz to 125 MHz, but alongside a transformer, not instead
  of one [MAG-KTA1552]_; the patent behind it notes "a fundamental trade-off
  between loop stability and common mode rejection ratio" [MAG-US7965480]_.

The rejection a transformer gives (30 dB to 43 dB, F2) is a reasonable
*estimate* of the target for the combination of choke, capacitors and
on-chip circuits.

F4 without a transformer: synthesised termination
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With a voltage-mode driver the 100 Ω termination is already on the chip
[MAG-KSZ9031]_ [MAG-DP83TC811]_, so impedance matching does not need the
transformer. The coupling capacitors add series reactance at low frequencies
(see `Coupling capacitor size`_). *Active termination* (also called
synthesised impedance), in which feedback in the driver sets the output
impedance instead of a resistor, saves transmit power and has been used in
line drivers for telephone-line data links [MAG-US6538500]_; no published
1000BASE-T driver using it was found. It could also compensate the coupling
capacitors' reactance; this is an idea, not a proven technique.

F5 without a transformer: low-frequency response
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The coupling capacitors set the droop (see `Coupling capacitor size`_). If
Power over Ethernet inductors are fitted across the pair, they also shunt
low frequencies, exactly as a transformer's magnetising inductance does, so
the same 80 µH minimum (1000BASE-T) applies to their inductance across the
pair [MAG-GARDNER14]_. The receiver's baseline-wander correction (see
:doc:`phy-electrical`) can tolerate a faster droop; how much is a design
choice for the integrated transceiver. Whether IEEE 802.3 accepts a
100BASE-TX transmitter without a 350 µH inductance is not settled: the
requirement is written in terms of inductance, with a droop alternative only
for Power over Ethernet equipment above 13 W [MAG-TRACY]_.

F6 and F7 without a transformer: common-mode termination and filtering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **External termination** on the cable side, as in the standard circuit
  (75 Ω per pair to a shared capacitor to chassis), with a DC-blocking
  capacitor per resistor when Power over Ethernet is present. Without the
  transformer the pair has no centre tap, so the termination needs two
  resistors per pair, one from each wire, to form one; single-pair
  automotive Ethernet does this with two 1 kΩ resistors and a 4.7 nF
  capacitor [MAG-OA100T1]_. The values for four-pair BASE-T are not
  documented anywhere found.
* **External choke**, as above.
* **On-chip active termination** of the common mode: the common-mode feedback
  loop of F2 can present a defined impedance (for example 75 Ω) to
  common-mode signals at the chip side of the capacitors. This is an idea,
  not a proven technique; its bandwidth must reach the frequencies where
  emissions are measured.

F8 without a transformer: surges and electrostatic discharge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Without a transformer, a common-mode surge is held off only by the coupling
capacitors' voltage rating, and the fast edge that passes through them must
be clamped on the chip side.

* **External protection diodes** between each chip-side node and signal
  ground, after the coupling capacitors. They do not break the isolation,
  because the capacitors are in series with them.
* **On-chip clamps.** The I/O cells target 2000 V human-body model
  [MAG-GFIO]_; the analog cells contain only diodes, and the designer must
  add charged-device-model protection. Custom on-chip clamps sized for the
  charge that passes the coupling capacitors are possible (a capacitor of
  :math:`C_\text{w}` charged by a step :math:`\Delta V` passes a charge
  :math:`C_\text{w} \Delta V`), but the system-level and surge events in
  :numref:`tbl-magnetics-cable-events` carry tens of times more energy than
  the I/O cells are designed for. Sizing on-chip clamps for them is an open
  question.
* **Differential protection** (a diode across each pair on the cable side)
  does not connect to ground and does not affect isolation.

F9 without a transformer: line-driver bias
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An integrated voltage-mode driver sets its own common-mode voltage and needs
no centre tap [MAG-ENT114]_. This function disappears.

F10 without a transformer: the Power over Ethernet current path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The power must reach both wires of a pair (equally) without loading the data.

* **Centre-tapped inductor across each pair** (one winding with a centre
  tap; no second winding). This is the cable-side half of a transformer: the
  DC enters at the centre tap and splits, the fields cancel, and the core
  sees only the unbalance. TI mentions "the addition of a center-tapped
  inductor" as a way to carry Power over Ethernet current [MAG-TPS2376H]_.
  Across the pair it must have at least 80 µH (F5). For the Power over
  Ethernet series-inductance limit (less than 100 µH, F11) only its leakage
  inductance counts, because the current flows through the two halves in
  opposite directions. Proven as part of Power over Ethernet magnetics;
  not found as a stand-alone part for this use.
* **Two separate inductors per pair.** Simple, but each inductor carries the
  full current of one wire (up to :math:`938\ \text{mA} / 2 = 469\ \text{mA}`
  with equal sharing, Class 8 [MAG-EA8023BT]_) without saturating, and the
  two together must still exceed 80 µH across the pair. Their series
  inductance on the power path is the full inductance, which conflicts with
  the 100 µH limit for a powered device. Coupled inductors sold for
  single-pair power have 56 µH to 250 µH per winding, with saturation
  currents from 0.36 A to 2.1 A depending on size [MAG-TDKSPE]_.
* **Active inductor** (*gyrator*): a transistor circuit that passes DC with
  low resistance but presents a high impedance at signal frequencies. Patented
  for single-pair power, with a drop of about 2 V per device and an emulated
  inductance "on the order of millihenries", adequate "up to about 100 Mbps"
  [MAG-US11038490]_ [MAG-US11394315]_. No product was found. The pass
  device must withstand 57 V and carry about 0.5 A, beyond any gf180mcu
  device, so it would be an external transistor controlled from the chip.
  Its noise, linearity and loss (about 1 W at 0.5 A and 2 V, an estimate)
  are open questions.

F11 without a transformer: detection and classification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The coupling capacitors block DC, so the data circuits do not disturb the
signature resistance. They do add capacitance between the two pair sets
during detection. **Estimate:** if every chip-side node returns to one ground,
each pair's two capacitors are in parallel (:math:`2 C_\text{w}`), and the
two pair sets are joined through two such groups in series:

.. math::

   C_\text{extra} = \frac{(2C_\text{w})(2C_\text{w})}{2C_\text{w} + 2C_\text{w}}
   = C_\text{w}

With :math:`C_\text{w} = 33\ \text{nF}` this adds 33 nF to the 50 nF to
120 nF window; with 100 nF it adds 100 nF, which uses almost the whole
window. The actual value depends on where the chip ground sits relative to
the powered device's input, and is an open question.

When the port supplies power, the chip-side nodes of the capacitors must
also survive the detection, classification and power-on steps of the
power sourcing equipment (2.7 V to 57 V, see :doc:`../power/poe`); the
capacitors hold this DC voltage.

F12 without a transformer: identical channels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All four channels of the front end must be identical, including the Power
over Ethernet inductors (fitted on all four pairs for four-pair power).

Candidate front ends for the full design
----------------------------------------

The following two front ends cover the range of choices. Both use a
voltage-mode driver on evampire. They differ in how much of the work is done
by external passive parts.

Front end 1: high-voltage capacitors and passive power separation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _fig-magnetics-arch-capacitor:

.. graphviz:: magnetics/arch-capacitor.dot
   :caption: Front end 1, one pair shown. High-voltage capacitors carry the
             data and block DC; a centre-tapped inductor across the pair
             carries the Power over Ethernet current; an optional
             common-mode choke and a cable-side termination handle
             common-mode noise; clamps protect the chip-side nodes; active
             circuits on evampire terminate the line, receive, and control
             the common-mode voltage.
   :alt: Block diagram. RJ45 pins 1 and 2 go through an optional
         common-mode choke and high-voltage coupling capacitors to the
         evampire pins. A centre-tapped inductor across the pair feeds the
         Power over Ethernet circuits. A 75 ohm and capacitor termination
         connects at the socket. Surge and ESD clamps connect at the chip
         side of the capacitors. Inside evampire, the pins connect to a line
         driver with synthesised 100 ohm termination, a receiver with wide
         common-mode range, a common-mode sense and feedback block, and pin
         protection; converters and signal processing follow.
   :align: center

External parts per port (four pairs): eight high-voltage coupling capacitors
(at least 16 nF each for 1000BASE-T, 33 nF to also meet 100BASE-TX, rated
for the DC isolation test), four centre-tapped inductors (if the port
carries Power over Ethernet on all pairs), protection diodes, the
common-mode termination, and optionally four common-mode chokes.

Every part of this front end has been used in shipping products in some
form: capacitor coupling in automotive and backplane Ethernet, inductors in
power over a single pair, centre-tapped windings in Power over Ethernet
magnetics. The combination at 1000 Mbit/s over 100 m of cable is not
documented.

Front end 2: more on the chip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The same structure, with these changes:

* the common-mode choke is replaced by on-chip common-mode feedback and
  termination (F2, F6, F7);
* the centre-tapped inductors are replaced by active inductors: external
  high-voltage transistors controlled by circuits on evampire (F10);
* the external protection diodes are reduced to what the coupling capacitors
  and custom on-chip clamps cannot handle (F8).

This front end needs fewer and smaller external parts, but each change is
proven only in patents or papers, not in products.

On-chip coupling capacitors are not a candidate: they would need tens of
square millimetres per wire and could not hold the Power over Ethernet
voltage (see `Limits of the gf180mcu process`_).

Key circuit specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Specifications for the on-chip circuits. Values marked
                "estimate" are derived on this page, not taken from a
                standard.
   :header-rows: 1
   :widths: 32 30 38

   * - Circuit
     - Specification
     - Basis
   * - Line driver
     - Up to 2.8 V peak differential (10BASE-T), about 1 V
       (100BASE-TX, 1000BASE-T); 100 Ω output impedance within the return
       loss budget
     - [MAG-INTERP1196]_ [MAG-UNH25]_ [MAG-UNH40]_; F4
   * - Voltage at each chip pin
     - ±1.4 V around the common-mode level for 10BASE-T (half of 2.8 V),
       plus the received signal, which overlaps the transmitted one at
       1000 Mbit/s
     - estimate; fits within 5 V or 6 V devices
   * - Receiver common-mode rejection
     - 30 dB to 43 dB, 1 MHz to 100 MHz, with any external choke
     - estimate, matching magnetics [MAG-PULSE]_ [MAG-BEL]_
   * - Common-mode feedback
     - holds the pair's common-mode voltage within the receiver's range for
       fast common-mode steps passed by the capacitors; bandwidth to at
       least 100 MHz if it replaces the choke
     - estimate
   * - Pin protection
     - survives the charge passed by :math:`C_\text{w}` during common-mode
       steps; human-body model 2000 V as a minimum
     - [MAG-GFIO]_; F8
   * - Active inductor control (front end 2)
     - high impedance across the pair down to about 23 kHz (equivalent to
       350 µH) or at least 80 µH; about 0.5 A per wire through an external
       transistor rated above 57 V
     - F5, F10

Which IEEE 802.3 requirements a transformer-free port can meet
--------------------------------------------------------------

.. list-table:: IEEE 802.3 requirements for a port with front end 1
   :header-rows: 1
   :widths: 30 15 55

   * - Requirement
     - Can meet?
     - How, and consequence
   * - Isolation, DC test (2250 V DC, 60 s)
     - Yes, with suitable parts
     - Coupling capacitors rated above 2250 V DC, and an isolated Power over
       Ethernet power path.
   * - Isolation, AC test (1500 V rms, 60 s)
     - Unlikely
     - 38 mA to 377 mA flows through the capacitors; the port should be
       qualified with the DC test instead.
   * - Isolation, impulse test
     - Depends on the capacitors and clamps
     - The capacitors must hold 2400 V (1500 V with Power over Ethernet).
   * - Return loss
     - Yes
     - Capacitors of at least about 16 nF per wire, plus margin for the
       chip's termination.
   * - Droop (1000BASE-T)
     - Yes
     - Capacitors and any inductors as calculated above.
   * - 350 µH inductance (100BASE-TX)
     - Not as written
     - Equivalent behaviour is possible; the requirement is written for an
       inductance.
   * - Power over Ethernet signature and classification
     - Yes, with care
     - Extra capacitance from the coupling capacitors must fit in the
       50 nF to 120 nF window; series inductance must stay under 100 µH.
   * - Radio interference limits
     - Unproven
     - Must be measured; a common-mode choke reduces the risk.

Consequences:

* A transformer-free port talks to standard equipment: the signals on the
  cable are the same as those of a port with magnetics.
* If the isolation is met only in part (for example, by the DC test but not
  the AC test), or not at all, the board can be used safely only where both
  ends of every cable share a ground, such as inside one piece of equipment
  or one rack. Connecting it between buildings, or to equipment on a
  different power system, exposes the chip to ground differences and surges
  that the isolation exists to block.

First version: practical magnetics
----------------------------------

The first version uses standard magnetics. This section collects the
practical guidance for choosing and placing them.

Discrete magnetics and integrated sockets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Magnetics come either as a **discrete module** (all four channels in one
surface-mount part, placed between the transceiver and an ordinary RJ45
socket, with the 75 Ω resistors and the high-voltage capacitor as separate
parts) or built into an **RJ45 socket with integrated magnetics**, usually
including the termination and two LEDs driven by the transceiver. Integrated
sockets save space and screen the cable-side wiring in their metal shield;
their smaller cores can make crosstalk and common-mode rejection worse
[MAG-ENT98]_. TI recommends a discrete transformer for better
electromagnetic compatibility [MAG-DP83867]_.

Chassis ground, shield and layout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _fig-magnetics-layout:

.. graphviz:: magnetics/layout.dot
   :caption: Board areas around one first-version port, seen from above.
             The transceiver and its centre-tap capacitors sit on a solid
             signal ground plane. There is no copper on any layer under the
             transformer. The RJ45 socket, the common-mode termination and
             the shield connection sit on a separate chassis ground area.
   :alt: Top view with three areas: a signal ground plane holding the
         transceiver and centre-tap capacitors, a copper-free area under the
         transformer module, and a chassis ground island holding the RJ45
         socket and the 75 ohm and 1000 picofarad termination. A resistor
         and capacitor join signal ground and chassis ground.
   :align: center

* Use a metal shielded RJ45 socket with its shield on chassis ground, and
  keep chassis ground an isolated area that does not overlap the signal
  ground planes [MAG-DP83867]_.
* Join the two grounds through a resistor of 1 MΩ or more and a capacitor,
  with a keep-out of at least 20 mil (about 0.5 mm) on all layers
  [MAG-SNLA387]_. These parts bridge the isolation barrier and must be rated
  for the isolation test.
* Route each pair as a 100 Ω ± 10 % differential pair over a continuous
  ground plane, under 2 inches (about 50 mm) long, with the two traces
  matched within 20 mil at 1000 Mbit/s and pairs at least 30 mil apart
  [MAG-SNLA387]_.
* Keep all copper away from under the magnetics on every layer
  [MAG-SNLA387]_ [MAG-DP83867]_.
* Place protection diodes on the transceiver side of the magnetics
  [MAG-SNLA387]_.

What to look for in a magnetics data sheet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Typical requirements for 10/100/1000 Mbit/s magnetics
                [MAG-KSZ9031]_ [MAG-DP83867]_ [MAG-ENT98]_
   :header-rows: 1
   :widths: 35 65

   * - Parameter
     - Typical requirement
   * - Turns ratio
     - 1CT:1CT within ±2 % to ±3 %
   * - Open-circuit inductance
     - 350 µH minimum at 100 kHz, 100 mV, 8 mA DC bias
   * - Insertion loss
     - 1 dB maximum, 1 MHz to 100 MHz
   * - Return loss
     - at least about 18 dB from 1 MHz to 30 MHz (2 dB margin on the
       standard)
   * - Common-mode rejection and crosstalk
     - 30 dB or more
   * - Isolation
     - 1500 V rms for 1 minute
   * - Centre taps
     - four separate circuit-side centre taps (for a voltage-mode
       transceiver); cable-side centre taps available for the termination
   * - Choke position
     - cable side
   * - Power over Ethernet
     - rated for the current, on the port that takes or supplies power

.. list-table:: Example gigabit magnetics, checked against the
                manufacturers' data sheets
   :header-rows: 1
   :widths: 25 20 55

   * - Part
     - Form
     - Key values
   * - Pulse H5007NL
     - discrete module
     - 1:1; insertion loss 1 dB max; return loss 18 dB (1–30 MHz and
       40 MHz), 16 dB (50 MHz), 12 dB (60–80 MHz), 10 dB (100 MHz);
       1500 V rms; inductance not listed [MAG-PULSE]_
   * - Würth Elektronik 7499111221A
     - RJ45 with magnetics, two LEDs
     - 350 µH min at 8 mA; 1500 V rms for 1 min; insertion loss 1 dB max;
       return loss 18 / 14 / 9 / 8 dB over 1–30 / 30–60 / 60–80 /
       80–100 MHz; four 75 Ω and 1000 pF, 2 kV inside; not for Power over
       Ethernet [MAG-WURTH]_
   * - Bel Fuse 0826-1G1T-23-F
     - RJ45 with magnetics, two LEDs, 12 cores
     - 1CT:1CT ±2 %; 350 µH min at 8 mA; return loss 18 dB (0.5–40 MHz);
       1500 V rms, every part tested; four 75 Ω and 1000 pF, 2 kV inside
       [MAG-BEL]_

First-version board, per port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each of ports A and B needs one external transceiver with an RGMII
interface; one set of four-channel magnetics for 1000BASE-T (discrete or in
the socket); the circuit-side centre-tap connection its data sheet asks for;
the cable-side termination unless it is in the socket; a shielded RJ45 socket
on a chassis ground area; and the resistor and capacitor joining the two
grounds. The port that takes or supplies Power over Ethernet (port A takes
power and port B supplies it, see :doc:`../power/index`) also needs
PoE-rated magnetics, DC-blocking capacitors in the termination, and the power
circuits on the cable-side centre taps.

Open design questions
---------------------

1. **Isolation.** Is the full design required to pass the IEEE 802.3
   isolation test, and is the DC test (2250 V) an acceptable way to do so?
   Are safety-rated capacitors required, and if so how is the 16 nF minimum
   met when certified surface-mount parts stop at 4.7 nF?
2. **Coupling capacitors.** Which parts give 16 nF to 100 nF per wire at
   more than 2250 V DC, and at what size and cost for eight per port?
3. **Power path isolation.** Must the Power over Ethernet converter on each
   port be isolated, given that capacitor coupling puts the power circuits
   directly on the cable?
4. **Power separation.** Centre-tapped inductors, separate inductors, or
   active inductors? Can a centre-tapped inductor meet both the 80 µH data
   requirement and the 100 µH powered-device limit at 938 mA per pair?
5. **Common-mode noise.** Is an external common-mode choke needed to meet
   radio-interference limits, or can on-chip common-mode feedback and
   termination replace it? What termination values suit four-pair cable
   without centre taps?
6. **Protection.** What external protection is needed for system-level
   discharge, surges and charged-cable events, and what charge must on-chip
   clamps absorb behind the coupling capacitors?
7. **Speeds.** Which speeds does the integrated transceiver support (not yet
   fixed, see :doc:`../overview`)? 100BASE-TX brings the 350 µH and 3°
   phase requirements; 1000BASE-T brings full-length capacitor coupling,
   which is not documented by any vendor.
8. **Detection capacitance.** How much capacitance do the coupling
   capacitors add to the powered-device signature in the actual grounding
   arrangement?
9. **Process options.** Is the 10 V LDMOS available in the wafer.space flow,
   and what are the breakdown voltages of the deep N-well and of the oxide
   between metal layers? These decide how much protection and common-mode
   range can move onto the chip.
10. **Conformance.** How will the port be tested against IEEE 802.3 where the
    standard assumes a transformer (the 350 µH inductance requirement)?

References
----------

.. [MAG-IEEE8023] IEEE Std 802.3-2022, *IEEE Standard for Ethernet*.
   https://standards.ieee.org/ieee/802.3/10422/
.. [MAG-WALKER] D. Walker and C. Bullock, *Summary of Isolation Requirements*
   (IEEE 802.3-2015, :clause:`126` and :clause:`145` draft 3.0), IEEE 802.3
   isolation ad hoc, 2017-08-17.
   https://www.ieee802.org/3/ad_hoc/isolation/public/Walker_1_08172017_rev_1.pdf
.. [MAG-INTERP0311] IEEE 802.3 interpretation request 2-03/11, *Isolation
   Criteria*, 2011-03-20. https://www.ieee802.org/3/interp/interp-2-0311.pdf
.. [MAG-INTERP1196] IEEE 802.3 interpretation 1, *10BASE-T Transmit Voltage
   Template* (:clause:`14.3.1.2.1`).
   https://www.ieee802.org/3/interp/interp-1-1196.pdf
.. [MAG-POTTERF] Potterf (Cisco), *802.3da Isolation Improvements*, IEEE
   P802.3da, 2025-01.
   https://grouper.ieee.org/groups/802/3/da/public/0125/SPMD_Potterf_Isolation_Improvements_2025-01-08_postmeeting.pdf
.. [MAG-LEWIS] J. Lewis (Dell EMC), *802.3 Proposed Baseline Text: 60950,
   60950-1 Where Used (IEEE 802.3-2018)*, IEEE P802.3cr, 2019-07-15.
   https://www.ieee802.org/3/cr/public/0719/Lewis_3cr_01a_0719.pdf
.. [MAG-HSTEWART] IEEE P802.3bt draft D1.5 baseline text (:clause:`33`,
   Environments A and B), 2016-01.
   https://www.ieee802.org/3/bt/public/jan16/hstewart_02_0116_baseline.pdf
.. [MAG-LAW] D. Law, *IEEE P802.3at Power via MDI enhancements, 350 µH ad
   hoc report*, 2008 (quotes ANSI X3.263-1995, section 9.1.7).
   https://www.ieee802.org/3/at/public/2008/06/law_1_0608.pdf
.. [MAG-TRACY] N. Tracy and E. Eminhizer (TE Connectivity), *Proposed
   Changes to IEEE Std 802.3* (:clause:`25.4.5`, :clause:`25.4.5.1 <25.4.5.1>`
   and :clause:`25.4.7 <25.4.7>`),
   2011. https://www.ieee802.org/3/maint/public/tracy_1_0911.pdf
.. [MAG-GARDNER14] A. Gardner (Linear Technology), *PoDL decoupling*, IEEE
   802.3bu, 2014-05.
   https://www.ieee802.org/3/bu/public/may14/gardner_3bu_1_0514.pdf
.. [MAG-UNH40] University of New Hampshire InterOperability Laboratory,
   *PMA Test Suite* for :clause:`40` physical medium attachment, version 1.1
   (tests 40.6.1.1, 40.6.1.2 and 40.8.3.1).
   https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/CL40_PMA/PMA_Test_Suite_v1.1.pdf
.. [MAG-UNH25] University of New Hampshire InterOperability Laboratory,
   *100BASE-TX PMD Test Suite*, version 3.5 (tests 25.1.1 and 25.1.7).
   https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/CL25_PMD/PMD_Test_Suite_v3.5.pdf
.. [MAG-UNHXO] M. Hersh, *Auto-Crossover White Paper*, University of New
   Hampshire InterOperability Laboratory, 2006.
   https://www.iol.unh.edu/sites/default/files/knowledgebase/ethernet/Auto-Crossover_White_Paper.pdf
.. [MAG-EA8023BT] Ethernet Alliance, *Overview of 802.3bt Power over
   Ethernet*, version 2.1, 2019-12 (Tables 15, 16 and 18; section 3).
   https://ethernetalliance.org/wp-content/uploads/2019/12/WP_EA_Overview8023bt_V2p1_FINAL.pdf
.. [MAG-SMITH] R. W. Smith, *Apparatus and method for terminating cables to
   minimize emissions and susceptibility*, US patent 5,321,372, 1994-06-14.
   https://patents.google.com/patent/US5321372A
.. [MAG-ENT98] Microchip (Microsemi), *Magnetics Guide*, ENT-AN0098,
   revision 2.2, 2018-06. Archived product page:
   https://web.archive.org/web/20250911203723/https://www.microchip.com/en-us/application-notes/entan0098magneticsguide
.. [MAG-ENT106] Microchip (Microsemi), *SimpliPHY Architecture Advantages*,
   ENT-AN0106, revision 1.1.
.. [MAG-ENT114] Microchip (Microsemi), *SimpliPHY Transformerless Ethernet
   Designs*, ENT-AN0114, revision 2.0, 2018-06.
.. [MAG-SNLA088] Texas Instruments, *AN-1519 DP83848 PHYTER Transformerless
   Ethernet Operation*, SNLA088A, 2013-04.
   https://www.ti.com/lit/pdf/snla088
.. [MAG-SNLA387] Texas Instruments, *Ethernet PHY PCB Design Layout
   Checklist*, SNLA387, 2021-06. https://www.ti.com/lit/an/snla387/snla387.pdf
.. [MAG-SDAA089] Texas Instruments, *DP83848 to DP83826A Hardware Rollover
   Document*, SDAA089. https://www.ti.com/lit/pdf/sdaa089
.. [MAG-SLVAF59] Texas Instruments, *PoE PD Schematic Review Guidelines*,
   SLVAF59, 2021-04. https://www.ti.com/lit/an/slvaf59/slvaf59.pdf
.. [MAG-SLVA711] Texas Instruments, *IEC 61000-4-x Tests for TI's Protection
   Devices*, SLVA711, 2015-06. https://www.ti.com/lit/pdf/slva711
.. [MAG-POMMERENKE] D. Pommerenke, *Charged cable event*, contribution to
   IEEE 802.3, 2001-02-23.
.. [MAG-SNLA087] Texas Instruments, *AN-1511 Cable Discharge Event*,
   SNLA087A. https://www.ti.com/lit/pdf/snla087
.. [MAG-DEATHERAGE] J. Deatherage and D. Jones (Intel), "Multiple factors
   trigger cable discharge events in Ethernet LANs", *Electronic Design*,
   2000-12-04.
.. [MAG-ESDA] EOS/ESD Association, *EOS/ESD Fundamentals Part 5: Device
   Sensitivity and Testing* (human-body model 100 pF, 1.5 kΩ).
   https://www.esda.org/esd-overview/esd-fundamentals/part-5-device-sensitivity-and-testing/
.. [MAG-SSZY028] Texas Instruments, *Enabling high voltage signal isolation
   quality and reliability*, SSZY028, 2017-03.
   https://www.ti.com/lit/pdf/sszy028
.. [MAG-SSZY024] Texas Instruments, *High-voltage isolation quality and
   reliability for AMC130x*, SSZY024. https://www.ti.com/lit/pdf/sszy024
.. [MAG-KAERIYAMA] S. Kaeriyama et al., "A 2.5 kV Isolation 35 kV/µs CMR
   250 Mbps Digital Isolator in Standard CMOS With a Small Transformer
   Driving Technique", *IEEE Journal of Solid-State Circuits*, 47(2), 2012,
   doi:10.1109/JSSC.2011.2170775 (abstract only consulted).
.. [MAG-GF180] GlobalFoundries and Google, *gf180mcu PDK documentation*:
   electrical specifications (sections 1, 3, 5.4, 5.5, 6.2 and 8),
   inter-layer specifications, and design rule manual section 14.1.
   https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs.html
.. [MAG-GFIO] GlobalFoundries and Google, *gf180mcu_fd_io I/O library*,
   ESD protection targets (docs/specs/16_ESD_Protection.csv) and analog
   pads (docs/analog.rst).
   https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_io
.. [MAG-KSZ9031] Microchip, *KSZ9031RNX Gigabit Ethernet Transceiver with
   RGMII Support*, DS00002117F (Table 3-1; section 12).
   https://ww1.microchip.com/downloads/en/DeviceDoc/00002117F.pdf
.. [MAG-DP83867] Texas Instruments, *DP83867IR/CR 10/100/1000 Ethernet PHY
   Layer Transceiver*, SNLS484 (section 9.2).
   https://www.ti.com/lit/ds/symlink/dp83867ir.pdf
.. [MAG-TPS2376H] Texas Instruments, *TPS2376-H*, SLVS646B (sections 9.2.1.2
   and 9.2.1.3). https://www.ti.com/lit/ds/symlink/tps2376-h.pdf
.. [MAG-DP83TC811] Texas Instruments, *DP83TC811-Q1 100BASE-T1 Automotive
   Ethernet PHY*, SNLS742A (Table 8-1).
   https://www.ti.com/lit/ds/symlink/dp83tc811-q1.pdf
.. [MAG-DP83TD510E] Texas Instruments, *DP83TD510E 10BASE-T1L Ethernet PHY*,
   SNLS656D (Tables 7-2 and 7-3).
   https://www.ti.com/lit/ds/symlink/dp83td510e.pdf
.. [MAG-OA100T1] OPEN Alliance, *100BASE-T1 System Implementation
   Specification*, version 1.0, 2017-12 (Figure 1).
   https://opensig.org/wp-content/uploads/2024/01/OA-100BASE-T1-system-implementation-specification_D1.0_final-1.pdf
.. [MAG-TDKSPE] TDK Electronics, *Inductors for 10BASE-T1L Power over Data
   Lines* (presentation).
   https://www.tdk-electronics.tdk.com/download/3260192/b438406d129a91cd76ebd99fb612b98e/download-presentation.pdf
.. [MAG-TCAN1044] Texas Instruments, *TCAN1044A-Q1 CAN FD transceiver*.
   https://www.ti.com/lit/ds/symlink/tcan1044a-q1.pdf
.. [MAG-THVD2450] Texas Instruments, *THVD2410/THVD2450 RS-485
   transceivers*. https://www.ti.com/lit/ds/symlink/thvd2450.pdf
.. [MAG-KTA1552] Kinetic Technologies, *KTA1552 Quad Channel Active EMI &
   ESD Suppressor for Ethernet*.
   https://www.kinet-ic.com/uploads/web/KTA1552/KTA1552-04b.pdf
.. [MAG-KEMET1812] KEMET, *C1812C103KGRACTU* specification sheet (10 nF,
   2000 V DC, 1812).
   https://search.kemet.com/component-documentation/download/specsheet/C1812C103KGRACTU
.. [MAG-KEMETCAS] KEMET (Yageo), *Safety-certified surface-mount MLCC, CAS
   series*, C1100.
   https://yageogroup.com/content/datasheet/asset/file/KEM_C1100_CAS_SMD
.. [MAG-US8132027] US patent 8,132,027, *Transformerless power over Ethernet
   system* (Agere), 2012-03-06. https://patents.google.com/patent/US8132027
.. [MAG-US7851938] US patent 7,851,938, *Midspan powering without the use of
   data transformers* (Broadcom), 2010.
   https://patents.google.com/patent/US7851938
.. [MAG-US9189036] US patent 9,189,036, *Ethernet module* (Akros Silicon).
   https://patents.google.com/patent/US9189036
.. [MAG-US7965480] US patent 7,965,480 (Akros Silicon), active common-mode
   choke. https://patents.google.com/patent/US7965480
.. [MAG-US11038490] US patent 11,038,490, *Active gyrator circuit in
   one-pair Ethernet with PoDL* (Analog Devices), 2021-06-15.
   https://patents.google.com/patent/US11038490
.. [MAG-US11394315] US patent 11,394,315 (published as US 2021/0104953),
   *PoDL powered device with active rectifier bridge*, (Analog Devices),
   2022-07-19. https://patents.google.com/patent/US20210104953A1
.. [MAG-US6538500] US patent 6,538,500 (Texas Instruments), active
   impedance termination in a line driver.
   https://patents.google.com/patent/US6538500
.. [MAG-PULSE] Pulse Electronics, *1000BASE-T Magnetics Module* (H5004NL,
   H5007NL), HC500.T, 2020-06. https://www.pulseelectronics.com/
.. [MAG-WURTH] Würth Elektronik, *WE-RJ45LAN Transformer 10/100/1000Base-T*,
   7499111221A, revision 005.000, 2020-10-07. Archived copy:
   https://web.archive.org/web/20250126113004/https://www.we-online.com/components/products/datasheet/7499111221A.pdf
.. [MAG-BEL] Bel Fuse, *gigabit MagJack 0826-1G1T-23-F*, drawing revision F.
   https://www.belfuse.com/media/drawings/products/magjack%20ICMs/dr-mag-0826-1g1t-23-f.pdf
