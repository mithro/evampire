Magnetics and the RJ45 socket
=============================

This page explains how an Ethernet transceiver is connected to the RJ45
socket, what the coupling transformers between them (the "magnetics") do,
and how those jobs can be done without transformers.

The requirements for evampire are (see :ref:`requirements`):

* **First version:** each Ethernet port uses an external transceiver chip
  with an RGMII interface (see :doc:`rgmii`), and standard magnetics between
  that transceiver and the RJ45 socket.
* **Every port, in both versions:** gigabit Ethernet (1000BASE-T,
  :clause:`40`). All four pairs carry signals in both directions at once, at
  125 million symbols per second on each pair, each symbol one of five
  voltage levels (*PAM-5*, five-level pulse amplitude modulation; see
  :doc:`phy-electrical`). Whether 10 Mbit/s and 100 Mbit/s are also
  supported is not yet decided, so their requirements appear on this page
  only as secondary values.
* **Full design:** the transceiver is integrated on evampire, and the cable
  connects to the board *without coupling transformers*. Every job the
  transformers normally do is done instead by active analog circuits on
  evampire together with a small number of external passive components.
  Ports can also receive or supply Power over Ethernet (see
  :ref:`power-roles` and :doc:`../power/poe`); in the full design either
  Ethernet port can take either role (:ref:`power-board-configs`). All Power
  over Ethernet types are documented; the maximum power the board supports
  is not yet fixed.

The transformer is therefore the reference point. The first half of this
page explains each job it does and the numbers the Ethernet standard sets.
The second half works through how each job can be done without it, what that
means for a chip made in the `gf180mcu <https://gf180mcu-pdk.readthedocs.io/>`_
process, and which questions are still open. How the transceiver itself
works, and what the integrated transceiver must do, is covered in
:doc:`phy-electrical`.

The Ethernet standard is IEEE 802.3 [MAG-IEEE8023]_; the clauses used here
are listed on :doc:`../standards`. The parts that matter here are
:clause:`14` (10 Mbit/s over twisted-pair cable, called *10BASE-T*),
:clause:`25` (100 Mbit/s, *100BASE-TX*), :clause:`40` (1000 Mbit/s,
*1000BASE-T*), and :clause:`Clauses 33 <33>` and :clause:`145 <145>` (Power
over Ethernet). The connection between the transceiver and the cable is
called the *MDI*, short for "medium dependent interface": the eight wires of
the RJ45 socket and the electrical requirements on them. In this page the
*front end* of a port means everything between the transceiver's converters
and the RJ45 socket: the line driver and receiver, the coupling parts (a
transformer or its replacement), protection and termination.

The cable and the RJ45 socket
-----------------------------

An Ethernet cable contains four *twisted pairs*: four pairs of wires, the two
wires of each pair twisted around each other. Each pair is a balanced
transmission line with a characteristic impedance of 100 Ω, allowed to vary
by ±15 % [MAG-UNH40]_. A signal is sent as a voltage *difference* between the
two wires of a pair, and the receiver looks only at that difference.
Interference from outside reaches both wires of a pair nearly equally and
does not change the difference.

The RJ45 plug and socket have eight contacts, numbered 1 to 8. One pair uses
pins 3 and 6, which sit on either side of the pair on pins 4 and 5.
:numref:`tbl-magnetics-rj45` shows which pins form which pair.

.. list-table:: RJ45 pin use. The 1000BASE-T names are those of IEEE 802.3
                :clause:`40`; "BI" means the pair carries data in both
                directions at once [MAG-KSZ9031]_.
   :name: tbl-magnetics-rj45
   :header-rows: 1
   :widths: 12 18 25 25 20

   * - Pins
     - Pair (1000BASE-T)
     - 1000BASE-T, MDI
     - 10/100 Mbit/s, MDI
     - 10/100 Mbit/s, MDI-X
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

At 10 and 100 Mbit/s two pairs are used, one in each direction. At
1000 Mbit/s all four pairs carry data in both directions at the same time.

.. _magnetics-f12:

At 10 and 100 Mbit/s a transmitter at one end must reach the receiver at the
other end. With a "straight-through" cable (pin 1 to pin 1 and so on) this
works only if the two ends use opposite pin assignments, called *MDI* and
*MDI-X* (:numref:`fig-magnetics-crossover`). At 1000 Mbit/s, MDI-X swaps
pair A with B and pair C with D [MAG-KSZ9031]_. IEEE 802.3 :clause:`40.4.4`
defines *automatic MDI/MDI-X configuration*: while there is no link, a port
switches between the two assignments at pseudo-random times (a sample timer
of 62 ms ± 2 ms) until it hears the other end [MAG-UNHXO]_. Because either
pair can end up carrying either direction, all channels of the front end must
be identical (function F12 in :numref:`tbl-magnetics-functions`).

.. graphviz:: magnetics/crossover.dot
   :name: fig-magnetics-crossover
   :caption: MDI and MDI-X at 10 and 100 Mbit/s. With a straight-through
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

.. graphviz:: magnetics/one-pair.dot
   :name: fig-magnetics-one-pair
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

.. graphviz:: magnetics/four-pairs.dot
   :name: fig-magnetics-four-pairs
   :caption: All four pairs of a standard port. Each yellow block is one
             channel of the magnetics: a transformer followed, on the cable
             side, by a common-mode choke. The 75 Ω resistors from the four
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
winding. These parts are described in :ref:`magnetics-functions`.

.. _magnetics-functions:

What the magnetics do
---------------------

The transformer, the common-mode choke, the centre-tap connections and the
cable-side termination together do the jobs listed in
:numref:`tbl-magnetics-functions`. IEEE 802.3 does not require a
transformer; it sets electrical requirements on the MDI, and a 1:1
transformer per pair is "the most commonly used method" of meeting them
[MAG-ENT98]_.

.. list-table:: Functions of the magnetics, and the requirement each one
                meets
   :name: tbl-magnetics-functions
   :header-rows: 1
   :widths: 5 24 18 53

   * - #
     - Function
     - Done by
     - Requirement (source)
   * - :ref:`F1 <magnetics-f1>`
     - Galvanic isolation between the cable and the equipment
     - transformer
     - Withstand 1500 V rms at 50–60 Hz for 60 s, *or* 2250 V DC for 60 s,
       *or* ten 2400 V impulses (1500 V with Power over Ethernet); at least
       2 MΩ at 500 V afterwards (:clause:`Clauses 14.3.1.1 <14.3.1.1>`,
       :clause:`25.4.6 <25.4.6>`, :clause:`40.6.1.1 <40.6.1.1>`,
       :clause:`33.4.1 <33.4.1>`, :clause:`145.4.1 <145.4.1>`)
       [MAG-WALKER]_.
   * - :ref:`F2 <magnetics-f2>`
     - Rejecting common-mode voltage, and letting each side sit at its own
       voltage level
     - transformer, choke
     - No direct limit in IEEE 802.3. Typical magnetics reject 30 dB to
       43 dB [MAG-PULSE]_ [MAG-BEL]_.
   * - :ref:`F3 <magnetics-f3>`
     - Blocking DC between the cable and the transceiver
     - transformer
     - Needed for F1 and for Power over Ethernet (up to 57 V on the cable)
       [MAG-EA8023BT]_.
   * - :ref:`F4 <magnetics-f4>`
     - Matching the 100 Ω cable
     - 1:1 transformer
     - 1000BASE-T return loss ≥ 16 dB from 1 MHz to 40 MHz, against 85 Ω to
       115 Ω (:clause:`40.8.3.1`) [MAG-UNH40]_.
   * - :ref:`F5 <magnetics-f5>`
     - Passing low frequencies (limiting droop and baseline wander)
     - transformer inductance
     - 1000BASE-T: more than 73.1 % of the voltage left 500 ns after a step
       (:clause:`40.6.1.2.2`) [MAG-UNH40]_. Only if 100BASE-TX is supported:
       at least 350 µH with 0 mA to 8 mA DC bias (section 9.1.7 of
       ANSI X3.263, the twisted-pair physical layer standard of FDDI, an
       older 100 Mbit/s network, which :clause:`25` adopts) [MAG-LAW]_.
   * - :ref:`F6 <magnetics-f6>`
     - Terminating common-mode signals on the cable (lower emissions and
       better immunity)
     - 75 Ω resistors, 1000 pF capacitor
     - No IEEE limit. About 10 dB improvement reported [MAG-SMITH]_.
   * - :ref:`F7 <magnetics-f7>`
     - Filtering common-mode noise to and from the cable
     - choke
     - Radio-interference limits for the equipment, for example FCC Part 15
       [MAG-FCC15]_ [MAG-ENT106]_.
   * - :ref:`F8 <magnetics-f8>`
     - Withstanding surges and electrostatic discharge
     - transformer, plus protection diodes
     - No IEEE limit beyond F1. Equipment standards set test levels
       (:numref:`tbl-magnetics-cable-events`).
   * - :ref:`F9 <magnetics-f9>`
     - Supplying or biasing the transceiver's line driver
     - circuit-side centre tap
     - Set by the transceiver design [MAG-SDAA089]_ [MAG-KSZ9031]_.
   * - :ref:`F10 <magnetics-f10>`
     - Carrying Power over Ethernet current
     - cable-side centre taps
     - Up to 938 mA in one pair (Class 8) [MAG-EA8023BT]_.
   * - :ref:`F11 <magnetics-f11>`
     - Keeping the data circuits invisible to Power over Ethernet detection
       and classification
     - transformer
     - Powered device signature 23.7 kΩ to 26.3 kΩ, 50 nF to 120 nF, and
       less than 100 µH in series [MAG-EA8023BT]_.
   * - :ref:`F12 <magnetics-f12>`
     - Identical channels, so any pair can carry any direction
     - four identical channels
     - Automatic MDI/MDI-X (:clause:`40.4.4`) [MAG-KSZ9031]_.

.. _magnetics-f1:

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
the equipment, including its frame ground (the metal frame or enclosure),
and to pass at least one of the tests in :numref:`tbl-magnetics-hipot`. The
isolation clauses, as quoted in IEEE 802.3 working documents, contain no
exception for equipment inside one enclosure [MAG-POTTERF]_. A test like this
is commonly called a *hipot test* ("high potential").

.. list-table:: Isolation tests in IEEE 802.3. A port must pass at least
                one [MAG-WALKER]_ [MAG-INTERP0311]_.
   :name: tbl-magnetics-hipot
   :header-rows: 1
   :widths: 30 70

   * - Test
     - Requirement
   * - AC voltage
     - 1500 V rms at 50 Hz to 60 Hz for 60 s (2121 V peak)
   * - DC voltage
     - 2250 V DC for 60 s
   * - Impulses, port without Power over Ethernet
     - Ten 2400 V impulses of alternating polarity, at least 1 s apart. Each
       rises in 1.2 µs and falls to half its peak in 50 µs ("1.2/50 µs").
   * - Impulses, port with Power over Ethernet
     - Ten 1500 V impulses with a 10/700 µs shape
   * - Pass condition
     - No insulation breakdown, and at least 2 MΩ measured at 500 V DC
       afterwards

The AC and DC tests are applied as described in the product safety standard
IEC 60950-1, or its successor IEC 62368-1 [MAG-IEC62368]_ in newer text
[MAG-WALKER]_. Interpretation request 2-03/11 to the IEEE 802.3 working
group states that earlier interpretations treated the test as protection of
the interface against common-mode voltages rather than as a safety test, and
notes that protection diodes connected to ground defeat isolation
[MAG-INTERP0311]_.

For Power over Ethernet, :clause:`33` also distinguishes *Environment A* (a
network inside one building and one low-voltage power distribution system)
from *Environment B* (a network that crosses between buildings or power
systems). Environment A relaxes only the isolation *between the power
circuits of different ports*; it does not relax the isolation between the
MDI and the transceiver circuits [MAG-HSTEWART]_.

Magnetics data sheets give the isolation the part withstands, usually
1500 V rms for 60 s [MAG-PULSE]_ [MAG-WURTH]_ [MAG-BEL]_.

**Rating rule for parts across the isolation barrier.** Any part connected
between the cable side and the equipment side (a capacitor to chassis, a
coupling capacitor, a resistor between grounds) must withstand the voltage
of the isolation test that the port is qualified with. This page takes a
part as suitable when its maker specifies a withstand (test) voltage at
least as high as that test voltage: 2121 V peak for the AC test, or 2250 V
for the DC test. Its rated working voltage may be lower. The same rule is
applied to the 1000 pF capacitor in standard magnetics (:ref:`F6
<magnetics-f6>`), which is rated 2 kV, and to the coupling capacitors of a
transformer-free port (:ref:`isolation with available parts <magnetics-isolation-parts>`). Standard
magnetics are tested as a whole: Bel tests every part to the IEEE 802.3
isolation requirement [MAG-BEL]_.

.. _magnetics-f2:
.. _magnetics-f3:

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
frequencies, which is why a choke is added (:ref:`F7 <magnetics-f7>`).
Magnetics data sheets give the rejection as "common-mode rejection" or
"differential to common-mode rejection": for example 33 dB to 43 dB from
30 MHz to 100 MHz for the Pulse H5007NL [MAG-PULSE]_, and 30 dB to 35 dB
for the Bel 0826-1G1T-23-F [MAG-BEL]_.

.. _magnetics-f4:

F4: impedance matching and return loss
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ethernet transceivers drive and terminate a 100 Ω differential load
directly [MAG-KSZ9031]_ [MAG-DP83867]_, so the transformer ratio is 1:1 and
the 100 Ω cable appears as 100 Ω at the transceiver. How closely a port
matches 100 Ω is measured by its *return loss*: how much weaker the reflected
signal is than the signal arriving at the port.

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
* :math:`Z_0` is the impedance of the cable, nominally 100 Ω, allowed to be
  85 Ω to 115 Ω [MAG-UNH40]_;
* :math:`\text{RL}` is the return loss, in dB.

IEEE 802.3 :clause:`40.8.3.1` requires a 1000BASE-T port to have a return
loss of at least 16 dB from 1 MHz to 40 MHz [MAG-UNH40]_. To see what that
means for the port impedance, solve for :math:`\lvert\Gamma\rvert` and then
for a purely resistive :math:`Z` with :math:`Z_0 = 100\ \Omega`:

.. math::

   \lvert\Gamma\rvert_\text{max} = 10^{-16/20} = 0.158

.. math::

   Z_\text{max} = Z_0 \frac{1 + 0.158}{1 - 0.158} = 137.7\ \Omega
   \qquad
   Z_\text{min} = Z_0 \frac{1 - 0.158}{1 + 0.158} = 72.6\ \Omega

So the port only needs to be within roughly 73 Ω to 138 Ω of a 100 Ω cable,
but the transceiver and everything between it and the cable share that
budget. Microchip recommends magnetics with at least 2 dB of margin on this
limit [MAG-ENT98]_. From 40 MHz to 100 MHz, the same subclause
(:clause:`40.8.3.1`) lets the limit fall with frequency [MAG-UNH40]_:

.. math::

   \text{RL}_\text{min}(f) = 10 - 20 \log_{10} \frac{f}{80\ \text{MHz}}\ \text{dB}

At :math:`f = 100\ \text{MHz}`:

.. math::

   \text{RL}_\text{min} = 10 - 20 \times \log_{10} 1.25
   = 10 - 20 \times 0.0969 = 8.1\ \text{dB}

The *insertion loss* is the signal lost passing through the magnetics.
Gigabit magnetics specify at most 1 dB from 1 MHz to 100 MHz
[MAG-PULSE]_ [MAG-WURTH]_, an amplitude ratio of
:math:`10^{-1/20} = 0.891`: at most 11 % of the signal amplitude is lost.

Only if 100BASE-TX is supported: ANSI X3.263 also requires the port
impedance to be "nominally resistive with a phase angle less than 3°" from
2 MHz to 80 MHz [MAG-SNLA088]_. This matters for capacitor coupling (see
:ref:`magnetics-cap-size`).

.. _magnetics-f5:

F5: low-frequency response, droop and baseline wander
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A transformer cannot pass DC and passes low frequencies poorly. The reason
is its *magnetising inductance*: the inductance of one winding with the other
left open, given in data sheets as the *open-circuit inductance* (OCL). This
inductance sits in parallel with the signal path and shunts low frequencies
away. If the transmitter holds a constant voltage, the voltage on the cable
side decays towards zero; this is called *droop*. Long stretches of data
whose average is not zero make the received signal's average level drift;
this is called *baseline wander* (see :doc:`phy-electrical`).

**Model.** Treat the transformer as an ideal 1:1 transformer with the
inductance :math:`L` in parallel. Seen from :math:`L`, the 100 Ω source and
the 100 Ω cable are in parallel. The circuit is then a first-order high-pass
filter, and droop is an exponential decay with time constant :math:`\tau`:

.. math::

   R_\text{p} = \frac{R_\text{s} R_\text{L}}{R_\text{s} + R_\text{L}}
   \qquad
   \tau = \frac{L}{R_\text{p}}
   \qquad
   f_\text{c} = \frac{1}{2\pi\tau} = \frac{R_\text{p}}{2\pi L}

where:

* :math:`R_\text{s}` is the transceiver's output resistance, 100 Ω (it
  terminates the line);
* :math:`R_\text{L}` is the cable impedance, 100 Ω;
* :math:`R_\text{p}` is their parallel combination, in Ω;
* :math:`L` is the magnetising inductance, in H;
* :math:`\tau` is the time constant of the droop, in s;
* :math:`f_\text{c}` is the corner frequency of the high-pass filter, in Hz.

This model ignores the leakage inductance and the winding capacitance, which
matter only at high frequencies.

**Corner frequency with 350 µH.** With
:math:`R_\text{p} = 100 \times 100 / 200 = 50\ \Omega` and
:math:`L = 350\ \mu\text{H}` (the usual data-sheet value [MAG-KSZ9031]_
[MAG-WURTH]_):

.. math::

   f_\text{c} = \frac{50\ \Omega}{2\pi \times 350\ \mu\text{H}}
   = \frac{50}{2.199 \times 10^{-3}}\ \text{Hz}
   = 22.7\ \text{kHz}

Signals below about 23 kHz are attenuated. Ethernet signals have little
energy that low, but long runs of the same symbol do.

**Minimum inductance for 1000BASE-T.** :clause:`40.6.1.2.2` requires that,
500 ns after the start of a constant level in a test pattern, more than
73.1 % of the voltage remains [MAG-UNH40]_. In the model the remaining
fraction is :math:`e^{-t/\tau}`, so:

.. math::

   e^{-t/\tau} \ge k
   \quad\Rightarrow\quad
   \tau \ge \frac{t}{\ln(1/k)}
   \quad\Rightarrow\quad
   L \ge \tau R_\text{p}

where:

* :math:`t` is the time after the step, 500 ns [MAG-UNH40]_;
* :math:`k` is the fraction that must remain, 0.731 [MAG-UNH40]_.

Substituting:

.. math::

   \ln(1/0.731) = 0.313
   \qquad
   \tau \ge \frac{500\ \text{ns}}{0.313} = 1.60\ \mu\text{s}
   \qquad
   L \ge 1.60\ \mu\text{s} \times 50\ \Omega = 80\ \mu\text{H}

The same result appears in an IEEE 802.3 maintenance proposal [MAG-TRACY]_
and in work for IEEE 802.3bu, power over a single pair [MAG-8023BU]_
[MAG-GARDNER14]_. With 350 µH:

.. math::

   \tau = \frac{350\ \mu\text{H}}{50\ \Omega} = 7.0\ \mu\text{s}
   \qquad
   e^{-0.5/7.0} = 0.931

93 % remains, a large margin over 73.1 %.

**Why 350 µH.** Gigabit magnetics are specified at 350 µH because the same
parts also serve 100BASE-TX. The figure comes from ANSI X3.263 section 9.1.7,
which requires at least 350 µH at the transmitter "with any DC bias current
between 0 mA and +8 mA" to limit baseline wander, and notes that DC bias can
change the inductance by about 2:1 [MAG-LAW]_. Data sheets therefore quote
the inductance at 100 kHz, 100 mV and 8 mA of DC bias [MAG-KSZ9031]_.
IEEE 802.3at [MAG-8023AT]_, now part of :clause:`33`, added an alternative
droop test for transmitters in equipment that supplies or takes more than
13 W of Power over Ethernet [MAG-TRACY]_.

For a design without a transformer, two time constants become the targets
for whatever replaces the transformer:

* :math:`\tau_\text{min} = 1.6\ \mu\text{s}`, the 1000BASE-T droop
  requirement; and
* :math:`\tau_\text{mag} = 7.0\ \mu\text{s}`, the behaviour of standard
  350 µH magnetics. That 1000BASE-T link partners are designed and tested
  with magnetics of this kind is an *assumption* (it is what their data
  sheets ask for [MAG-KSZ9031]_ [MAG-DP83867]_).

.. _magnetics-f6:

F6: common-mode termination of the cable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each pair, taken as a whole, also forms a transmission line with every other
pair. Common-mode currents travel along these lines and, if their ends are
left open, reflect back and forth and radiate. Each cable-side centre tap
therefore goes through a 75 Ω resistor to a node shared by the four pairs.
Between any two pairs there are then two resistors in series, 150 Ω, close
to the roughly 145 Ω pair-to-pair impedance of
`Category 5 <https://en.wikipedia.org/wiki/Category_5_cable>`_ cable (a
common grade of Ethernet cable) [MAG-SMITH]_, so the energy is absorbed in
the resistors instead of radiated. The patent that describes it reports
"upwards of approximately 10 dB improvement in emissions and susceptibility"
[MAG-SMITH]_. This network is widely called the *Bob Smith termination*,
after its inventor, Robert W. Smith [MAG-SMITH]_.

The shared node goes to chassis ground through one capacitor, usually
1000 pF rated 2 kV [MAG-KSZ9031]_ [MAG-WURTH]_ [MAG-BEL]_. Microchip notes
that the capacitor is not part of the patent [MAG-ENT98]_. Its impedance
shows why a capacitor is used:

.. math::

   \lvert Z_C \rvert = \frac{1}{2\pi f C}

where :math:`f` is the frequency in Hz, :math:`C = 1000\ \text{pF}`, and
:math:`2\pi f C` is the capacitor's admittance, in siemens (S). At 50 Hz and
at 30 MHz:

.. math::

   2\pi \times 50 \times 10^{-9} = 3.14 \times 10^{-7}\ \text{S}
   \quad\Rightarrow\quad
   \lvert Z_C \rvert = 3.2\ \text{M}\Omega

.. math::

   2\pi \times 3 \times 10^{7} \times 10^{-9} = 0.189\ \text{S}
   \quad\Rightarrow\quad
   \lvert Z_C \rvert = 5.3\ \Omega

The termination works at signal frequencies, but at mains frequencies the
capacitor is nearly an open circuit and does not undo the isolation. It sits
across the isolation barrier, so it must meet the rating rule in
:ref:`F1 <magnetics-f1>`.

.. _magnetics-f7:

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
radiation is what fails radio-interference limits such as FCC Part 15
[MAG-FCC15]_. In the other direction, the cable picks up common-mode noise
from its surroundings; the choke and transformer keep it from the receiver
("electromagnetic immunity") [MAG-ENT98]_.

Microchip recommends the choke on the cable side of the transformer, and
reports less margin in the transmit waveform tests with it on the
transceiver side [MAG-ENT98]_. Some magnetics add a third part per pair, an
*autotransformer* (one centre-tapped winding across the pair) that gives
common-mode current a low-impedance path to the termination; parts with a
transformer, choke and autotransformer per pair are sold as "12-core", those
without as "8-core" [MAG-ENT98]_.

.. _magnetics-f8:

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
:numref:`tbl-magnetics-cable-events`.

.. _magnetics-f9:

F9: biasing the line driver through the circuit-side centre tap
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

How the circuit-side centre tap is connected depends on the transceiver's
line driver (:numref:`fig-magnetics-centre-tap-bias`; see also
:doc:`phy-electrical`):

* A **current-mode driver** switches a current between the two pins of the
  pair, and its transistors only sink current. The current is supplied
  through the centre tap, which is tied to a supply. TI's
  `DP83848 <https://www.ti.com/product/DP83848C>`_ needs a 49.9 Ω resistor
  from each pin to the 3.3 V analog supply and the centre taps pulled up to
  the same supply [MAG-SDAA089]_. Microchip describes such a driver for
  1000BASE-T as about 40 mA per pair [MAG-ENT106]_.
* A **voltage-mode driver** drives each pin from a low impedance, sets its
  own common-mode voltage, and has its termination on the chip. The centre
  tap must not be tied to a supply; each centre tap goes to ground through
  its own 0.1 µF capacitor [MAG-KSZ9031]_ [MAG-DP83867]_. Microchip gives
  the peak current of such a driver as 10 mA [MAG-ENT106]_.

Only a voltage-mode driver can work without a transformer, since a
current-mode driver gets its supply through the transformer
[MAG-ENT114]_.

.. graphviz:: magnetics/centre-tap-bias.dot
   :name: fig-magnetics-centre-tap-bias
   :caption: Circuit-side centre tap for one pair. Top: a current-mode
             driver takes its current through the centre tap, which is tied
             to a supply and decoupled to ground. Bottom: a voltage-mode
             driver sets its own common-mode voltage; the centre tap only
             goes to ground through a capacitor.
   :alt: Two schematics. Top: transceiver with switched current sinks, each
         pin with a 49.9 ohm resistor to a supply rail, the transformer
         centre tap tied to the same rail and to a 0.1 microfarad capacitor.
         Bottom: transceiver with push-pull drivers, the transformer centre
         tap connected only to a 0.1 microfarad capacitor to signal ground.
   :align: center

.. _magnetics-f10:
.. _magnetics-f11:

F10 and F11: Power over Ethernet through the centre taps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Power over Ethernet (PoE, see :doc:`../power/poe`) sends DC power on the
data pairs. The *power sourcing equipment* (the end that supplies power, see
:ref:`power-roles`) puts one polarity on both wires of one pair and the
other polarity on both wires of another pair; a pair carries no differential
DC, so the data is unaffected. *Alternative A* uses the pairs on pins 1, 2
and 3, 6; *Alternative B* the pairs on pins 4, 5 and 7, 8 (both are
described on :doc:`../power/poe`); :clause:`145` (four-pair power) uses
both [MAG-SLVAF59]_. The *powered device* (the end that receives power)
must accept power on either set of pairs in either polarity, so it uses two
bridge rectifiers [MAG-TPS2376H]_ (:numref:`fig-magnetics-poe`).

In a transformer the current enters at the cable-side centre tap and splits
into the two halves of the winding, flowing outward in opposite directions.
Their magnetic fields cancel, so the core is not biased by the full current;
only the difference between the two wires' currents (caused by unequal wire
resistance) biases it [MAG-TPS2376H]_. :numref:`tbl-magnetics-poe-numbers`
lists the Power over Ethernet numbers that matter for the front end.

.. list-table:: Power over Ethernet numbers that constrain the front end
                [MAG-EA8023BT]_
   :name: tbl-magnetics-poe-numbers
   :header-rows: 1
   :widths: 40 60

   * - Quantity
     - Value
   * - Power sourcing equipment output voltage
     - Type 1: 44 V to 57 V; Type 2 and 3: 50 V to 57 V; Type 4: 52 V to
       57 V
   * - Maximum voltage at a powered device
     - 57 V
   * - Highest current in one pair (Class 8, with allowed unbalance)
     - 938 mA (865 mA with perfect balance)
   * - Powered device detection signature
     - 23.7 kΩ to 26.3 kΩ, measured with 2.7 V to 10.1 V
   * - Powered device input capacitance during detection
     - 50 nF to 120 nF
   * - Series inductance of the powered device input
     - less than 100 µH
   * - Classification voltage (power sourcing equipment)
     - 15.5 V to 20.5 V

The transformer also keeps the transceiver out of the way of detection and
classification (:ref:`F11 <magnetics-f11>`): at DC the transceiver is not
connected to the cable at all, so the power sourcing equipment sees only the
powered device's signature resistor and capacitor. Any replacement must keep
the data circuits within the signature limits in
:numref:`tbl-magnetics-poe-numbers`, including the capacitance and series
inductance limits.

.. graphviz:: magnetics/poe-centre-taps.dot
   :name: fig-magnetics-poe
   :caption: Taking Power over Ethernet from the cable-side centre taps
             ("CT") of standard magnetics in a powered device. The bridge
             rectifiers make the input independent of which pairs, and which
             polarity, the source uses. The powered-device interface and
             power converter are described on :doc:`../power/poe`.
   :alt: Block diagram: the transceiver connects to the circuit side of
         PoE-rated magnetics, whose cable side goes to the RJ45 pins. The
         four cable-side centre taps go in pairs to two bridge rectifiers,
         which both feed the powered-device interface and power converter.
         A 75 ohm termination through 10 nanofarad blocking capacitors also
         connects to the magnetics.
   :align: center

In PoE designs each 75 Ω termination resistor needs a series capacitor (about
10 nF) to block the DC [MAG-ENT98]_.

.. _magnetics-events:

Voltages and events at the cable
--------------------------------

Whatever replaces the transformer must survive the voltages in
:numref:`tbl-magnetics-cable-events` and keep the signal intact.

.. list-table:: Voltages and events at an Ethernet port
   :name: tbl-magnetics-cable-events
   :header-rows: 1
   :widths: 30 28 42

   * - Event
     - Size
     - Duration and source
   * - 1000BASE-T signal
     - 0.67 V to 0.82 V peak differential in the test pattern
     - continuous [MAG-UNH40]_
   * - 100BASE-TX signal (only if supported)
     - 0.95 V to 1.05 V peak differential
     - continuous [MAG-UNH25]_
   * - 10BASE-T signal (only if supported)
     - 2.2 V to 2.8 V peak differential
     - continuous [MAG-INTERP1196]_
   * - Power over Ethernet
     - up to 57 V DC between pairs; up to 938 mA per pair
     - continuous [MAG-EA8023BT]_
   * - Isolation test
     - 1500 V rms (2121 V peak), or 2250 V DC
     - 60 s [MAG-WALKER]_
   * - Isolation impulse test
     - 2400 V (1500 V with PoE)
     - 1.2/50 µs (10/700 µs with PoE), ten times [MAG-WALKER]_
   * - Human-body model discharge (chip handling)
     - 2 kV into 100 pF through 1.5 kΩ: 1.33 A peak, 0.2 mJ
     - about 200 ns [MAG-ESDA]_
   * - System-level discharge, IEC 61000‑4‑2 [MAG-IEC61000-4-2]_, contact,
       level 4
     - 8 kV from 150 pF through 330 Ω: 4.8 mJ
     - rise 0.7 ns to 1 ns [MAG-SLVA711]_ [MAG-POMMERENKE]_
   * - Fast transient bursts, IEC 61000‑4‑4 [MAG-IEC61000-4-4]_
     - 1 kV and 4 kV used in one vendor simulation
     - repeated fast pulses [MAG-ADIWIKI]_
   * - Surge, IEC 61000‑4‑5 [MAG-IEC61000-4-5]_, data line
     - 1 kV to 2 kV through 42 Ω: about 24 A to 48 A peak
     - 1.2/50 µs voltage, 8/20 µs current [MAG-SLVA711]_
   * - Charged cable discharge
     - "as high as a few thousand volts", low source impedance
     - tests with cables charged to 0.75 kV to 5 kV; events longer than
       600 ns [MAG-SNLA087]_ [MAG-DEATHERAGE]_

The energies in :numref:`tbl-magnetics-cable-events` are the energy stored
in the test capacitor:

.. math::

   E = \tfrac{1}{2} C V^2

where :math:`E` is the energy in J, :math:`C` the test capacitance in F and
:math:`V` the test voltage in V. For the human-body model and the
system-level test:

.. math::

   E_\text{HBM} = 0.5 \times 100\ \text{pF} \times (2000\ \text{V})^2
   = 0.2\ \text{mJ}

.. math::

   E_\text{IEC} = 0.5 \times 150\ \text{pF} \times (8000\ \text{V})^2
   = 4.8\ \text{mJ}

The peak currents are the test voltage divided by the source resistance:

.. math::

   I_\text{HBM} = \frac{2000\ \text{V}}{1500\ \Omega} = 1.33\ \text{A}
   \qquad
   I_\text{surge} = \frac{1000\ \text{V}}{42\ \Omega} = 23.8\ \text{A}

These events differ in kind, and that decides what can protect against
them:

* **Short, energy-limited events** such as the human-body model are what
  on-chip protection is designed for. The protection diodes and clamps in an
  I/O cell conduct for a few hundred nanoseconds and absorb a bounded
  charge. The gf180mcu I/O library targets 2000 V human-body model
  [MAG-GFIO]_. A system-level discharge carries about 24 times the energy
  (4.8 mJ against 0.2 mJ) and a peak current of tens of amps, so it is
  normally absorbed by an external protection diode [MAG-SLVA711]_.
* **Long or large events** (surges, charged cables) deliver tens of amps for
  microseconds. They need external protection sized for them.
* **Sustained voltages** (Power over Ethernet at 57 V, the 60 s isolation
  test at 1500 V rms) are not events at all: a clamp that conducted during
  them would be destroyed or would break the isolation. They must be held
  off by something that withstands the full voltage continuously.

.. _magnetics-gf180-limits:

Limits of the gf180mcu process
------------------------------

Whether a job can move onto the chip depends on three different kinds of
limit. (a) The ratings of the standard devices and cells are conservative
continuous operating limits. (b) The physical limits of the process layers
(oxide, junction and dielectric breakdown) cannot be exceeded by any layer
that sees the full voltage, although stacking devices can exceed (a). (c)
Custom structures (stacked transistors in isolated wells, drain-extended
transistors, series capacitor stacks, custom clamps, active inductors) need
design and characterisation but are not ruled out unless (b) rules them out.
:numref:`tbl-magnetics-gf180` gives the documented values that matter for the
cable connection. The PDK (process design kit: the foundry's device models,
rules and documentation) is the source [MAG-GF180]_.

.. list-table:: gf180mcu limits from the PDK documentation [MAG-GF180]_.
                "Not documented" means the PDK gives no value.
   :name: tbl-magnetics-gf180
   :header-rows: 1
   :widths: 34 33 33

   * - Item
     - Rated operation, limit kind (a)
     - Breakdown, limit kind (b)
   * - 3.3 V transistor
     - 3.3 V; maximum DC gate voltage 3.63 V
     - gate oxide at least 7 V; drain at least 7 V
   * - 5 V and 6 V transistor (6 V gate oxide)
     - 5 V or 6 V; maximum DC gate voltage 6.5 V
     - gate oxide at least 12 V; drain at least 8.5 V
   * - 10 V drain-extended transistor (LDMOS)
     - 10 V drain (separate 10 V high-voltage process models; its well is
       tied to the substrate)
     - drain at least 13.2 V
   * - N-well to substrate junction
     - —
     - at least 10 V
   * - Deep N-well to substrate junction
     - —
     - not documented (the SPICE model uses about 30 V)
   * - MIM (metal-insulator-metal) capacitor, 1.0 fF/µm²
     - 20 V
     - at least 20 V
   * - MIM capacitor, 1.5 fF/µm²
     - 10 V
     - at least 10 V
   * - MIM capacitor, 2.0 fF/µm²
     - 6.6 V
     - not documented
   * - Oxide between metal layers
     - —
     - not documented; 1.15 µm to 1.45 µm per layer, five metal layers in
       the wafer.space flow
   * - I/O cell protection
     - target 2000 V human-body model, 500 V charged-device model (a test
       in which the charged chip itself discharges through one pin)
     - —

The `wafer.space <https://wafer.space/>`_ flow uses the
`open_pdks <https://github.com/RTimothyEdwards/open_pdks>`_ "gf180mcuD"
variant, with five metal layers and a MIM capacitor; its documentation does
not say whether the 10 V LDMOS is offered.

What follows for the cable connection:

* **Continuous 57 V on a chip pin.** Any node on the chip has some junction
  to the substrate that sees its full voltage. The highest documented
  junction breakdown is 10 V (N-well to substrate), and the highest value in
  the models is about 30 V (deep N-well, not a specification). Stacking
  transistors divides the voltage between their drains but not between a
  well and the substrate. Holding off 57 V (plus surges and the isolation
  test) on a pin connected directly to a cable wire is therefore ruled out by
  (b), unless a custom structure with a documented higher breakdown is
  characterised.
* **Isolation through on-chip dielectric.** The oxide between the first and
  fifth metal layers is four layers of 1.15 µm to 1.45 µm [MAG-GF180]_, so
  4.6 µm to 5.8 µm thick (5 µm is used below as the middle of that range).
  TI gives the short-term strength of silicon dioxide as about 500 V rms per
  µm [MAG-SSZY028]_, so the stack would break down at about
  4.6 × 500 = 2300 V rms to 5.8 × 500 = 2900 V rms in a short test, an
  *estimate*. That is above the 1500 V rms test level, but with no margin
  for a lifetime of use. Commercial capacitive isolators use at least
  13.5 µm of oxide with two capacitors in series [MAG-SSZY024]_, and a
  published digital isolator in standard CMOS reached 2.5 kV
  [MAG-KAERIYAMA]_. On-chip isolation is not ruled out by (b); it is a
  custom-structure option that is unproven in this process.
* **On-chip coupling capacitors.** The data needs tens of nanofarads per
  wire (:ref:`magnetics-cap-size`). The next estimate shows the area that
  takes.

**Area of an on-chip coupling capacitor (estimate).** The area needed is the
capacitance divided by the capacitance per area:

.. math::

   A = \frac{C}{c_\text{A}}

where:

* :math:`A` is the area, in µm²;
* :math:`C` is the capacitance needed, 16 nF per wire (the 1000BASE-T
  minimum from :ref:`magnetics-cap-size`);
* :math:`c_\text{A}` is the capacitance per area: 2.0 fF/µm² for the
  densest MIM capacitor (rated 6.6 V) [MAG-GF180]_, or, for a capacitor
  using the whole 5 µm oxide stack (silicon dioxide,
  :math:`\varepsilon_\text{r} = 3.9`):

.. math::

   c_\text{A} = \frac{\varepsilon_0 \varepsilon_\text{r}}{d}
   = \frac{8.854 \times 10^{-12} \times 3.9}{5 \times 10^{-6}}\
     \text{F/m}^2
   = 6.9 \times 10^{-6}\ \text{F/m}^2
   = 0.0069\ \text{fF/µm}^2

With the MIM capacitor and with the thick oxide stack:

.. math::

   A_\text{MIM} = \frac{16\ \text{nF}}{2.0\ \text{fF/µm}^2}
   = 8 \times 10^6\ \mu\text{m}^2 = 8\ \text{mm}^2

.. math::

   A_\text{oxide} = \frac{16\ \text{nF}}{0.0069\ \text{fF/µm}^2}
   \approx 2300\ \text{mm}^2

That is 64 mm² for the eight wires of one port with MIM capacitors rated
6.6 V, which would need several in series to hold the Power over Ethernet
voltage and so more area again, and an impractical area with the thick
oxide. On-chip capacitors are therefore a custom-structure option whose cost
is die area; capacitors small enough to fit can isolate only a signal that
has been converted to a high-frequency form (as digital isolators do), with
active circuits on both sides of the barrier. The choice is an open design
decision (:ref:`magnetics-open-questions`).

Doing each job without a transformer
------------------------------------

Several kinds of equipment already connect twisted-pair cables without
transformers, and they show which techniques are proven:

* **Capacitor-coupled 10/100 Mbit/s.** TI documents connecting its DP83848
  family through 33 nF capacitors per wire, for connections "shorter than
  1 meter", at forced 100 Mbit/s [MAG-SNLA088]_. Microchip documents
  direct connection of its voltage-mode transceivers through DC-blocking
  capacitors on one board or over a backplane [MAG-ENT114]_.
* **Single-pair automotive and industrial Ethernet** (100BASE-T1,
  :clause:`96`; 1000BASE-T1, :clause:`97`; 10BASE-T1L, :clause:`146`).
  These use 100 nF DC-blocking capacitors, a common-mode choke and a
  common-mode termination of two 1 kΩ resistors and a 4.7 nF capacitor, with
  no transformer [MAG-DP83TC811]_ [MAG-OA100T1]_. Their clauses list no
  isolation requirement for data-only ports [MAG-LEWIS]_ [MAG-POTTERF]_, and
  the capacitors are rated only 50 V to 100 V [MAG-OA100T1]_.
* **Power over a single pair** (IEEE 802.3bu [MAG-8023BU]_ and 802.3cg
  [MAG-8023CG]_). Power is put on the pair through inductors and taken off
  the data path by capacitors, with the inductor sized from the transmitter
  droop requirement [MAG-GARDNER14]_ [MAG-DP83TD510E]_ [MAG-TDKSPE]_.
* **Transformerless Power over Ethernet** is described in patents (per-wire
  inductors or active circuits for the power, high-voltage capacitors for
  the data) [MAG-US8132027]_ [MAG-US7851938]_ [MAG-US9189036]_; no product
  data sheet describing it is known.
* **Capacitor-coupled 1000BASE-T.** Analog Devices documents its ADIN1300
  gigabit transceiver connected through one 33 nF capacitor per wire, says it
  can operate "at all speeds" in this arrangement, and reports "no packet
  loss, no CRCs errors" with signal quality "comparable to transformer
  arrangement over a range of cable lengths (2 m to 100 m)" [MAG-ADIWIKI]_.
  The same page recommends capacitor coupling for cables "less than
  1 meter", warns that longer cables "might introduce some common-mode
  noise", and recommends a common-mode choke for them. It does not state
  which speed was used for the 2 m to 100 m test. Microchip's transformerless
  note covers gigabit transceivers on one board or a backplane, not cable
  [MAG-ENT114]_.

The Analog Devices report [MAG-ADIWIKI]_ is the only published account known
of capacitor-coupled 1000BASE-T over a full-length cable; the other vendor
documents cited here limit capacitor coupling to a backplane, one board, or
about 1 m of cable. This is the central risk of the full design, analysed in
:ref:`magnetics-central-risk`.

The rest of this section takes each function in turn. For each, it lists
options using external passive parts and options built on the chip, with
their requirements and risks. The choice between them is an open decision.

.. _magnetics-cap-size:

Coupling capacitor size
~~~~~~~~~~~~~~~~~~~~~~~

Replacing the transformer with a capacitor in each wire makes the data path a
series capacitor instead of a parallel inductor. Two 1000BASE-T requirements
set the smallest capacitor. In both the model is: the transceiver as a 100 Ω
source, the cable as a 100 Ω load, and one capacitor :math:`C_\text{w}` in
each of the two wires. The two capacitors are in series around the loop, so
the pair sees

.. math::

   C_\text{pair} = \frac{C_\text{w}}{2}

**1. Return loss.** A 1000BASE-T port must have at least 16 dB return loss
from 1 MHz (:ref:`F4 <magnetics-f4>`). A series capacitor adds a reactance
:math:`X = 1 / (2\pi f C_\text{pair})` in series with an otherwise perfect
100 Ω port, so the port impedance is :math:`Z = 100\ \Omega - jX` and, from
the reflection formula in :ref:`F4 <magnetics-f4>`:

.. math::

   \Gamma = \frac{(100\ \Omega - jX) - 100\ \Omega}
                 {(100\ \Omega - jX) + 100\ \Omega}
   = \frac{-jX}{200\ \Omega - jX}
   \qquad
   \lvert\Gamma\rvert = \frac{X}{\sqrt{(200\ \Omega)^2 + X^2}}

Setting :math:`\lvert\Gamma\rvert = 0.158` (16 dB, from
:ref:`F4 <magnetics-f4>`) and solving for :math:`X`:

.. math::

   X_\text{max} = \frac{200\ \Omega \times 0.158}{\sqrt{1 - 0.158^2}}
   = \frac{31.7}{0.987}\ \Omega = 32.1\ \Omega

At :math:`f = 1\ \text{MHz}`:

.. math::

   C_\text{pair} \ge \frac{1}{2\pi \times 10^6 \times 32.1}\ \text{F}
   = 4.96\ \text{nF}
   \qquad
   C_\text{w} \ge 9.9\ \text{nF}

This uses the whole 16 dB budget for the capacitors alone, so in practice
they must be larger.

**2. Droop.** The series capacitor forms a high-pass filter with the source
and load resistances in series, so its time constant is

.. math::

   \tau = (R_\text{s} + R_\text{L}) \, C_\text{pair}
   \qquad
   C_\text{w} = \frac{2\tau}{R_\text{s} + R_\text{L}}

where :math:`R_\text{s} + R_\text{L} = 200\ \Omega`. For the 1000BASE-T
droop limit, :math:`\tau_\text{min} = 1.6\ \mu\text{s}`, and to match
standard magnetics, :math:`\tau_\text{mag} = 7.0\ \mu\text{s}`
(:ref:`F5 <magnetics-f5>`):

.. math::

   C_\text{w} \ge \frac{2 \times 1.6\ \mu\text{s}}{200\ \Omega} = 16\ \text{nF}
   \qquad
   C_\text{w} = \frac{2 \times 7.0\ \mu\text{s}}{200\ \Omega} = 70\ \text{nF}

At exactly 16 nF the port meets the droop limit with no margin (73.2 % left
after 500 ns against 73.1 % required). :numref:`tbl-magnetics-cap-size`
collects the limits.

.. list-table:: Smallest coupling capacitor per wire
                (model in :ref:`magnetics-cap-size`)
   :name: tbl-magnetics-cap-size
   :header-rows: 1
   :widths: 50 25 25

   * - Requirement
     - Capacitor per wire
     - Source of the limit
   * - 1000BASE-T return loss at 1 MHz (no margin)
     - 9.9 nF
     - [MAG-UNH40]_
   * - 1000BASE-T droop, 500 ns (no margin)
     - 16 nF
     - [MAG-UNH40]_
   * - Same low-frequency corner as standard magnetics (350 µH)
     - 70 nF
     - [MAG-KSZ9031]_
   * - Only if 100BASE-TX is supported: phase angle under 3° at 2 MHz
     - 30.4 nF (33 nF used)
     - [MAG-SNLA088]_

The last row comes from the 100BASE-TX requirement that the port look
resistive within 3° from 2 MHz:

.. math::

   X \le 100\ \Omega \times \tan 3^\circ = 5.24\ \Omega
   \qquad
   C_\text{pair} \ge \frac{1}{2\pi \times 2 \times 10^6 \times 5.24}\ \text{F}
   = 15.2\ \text{nF}

so :math:`C_\text{w} \ge 30.4\ \text{nF}`. TI calculates 30.42 nF and uses
33 nF [MAG-SNLA088]_, as does Analog Devices for its gigabit transceiver
[MAG-ADIWIKI]_.

:ref:`magnetics-central-risk` shows what each value means for the received
signal. A value between 33 nF and 100 nF per wire is a reasonable
*estimate* of the working range: above the droop limit with margin, and at
or near the behaviour of standard magnetics. Reaching it with parts that
meet the isolation rating rule takes several high-voltage capacitors per
wire (:ref:`isolation with available parts <magnetics-isolation-parts>`).

.. _magnetics-central-risk:

The central risk: capacitor-coupled 1000BASE-T over 100 m
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Capacitor coupling is proven for short links and backplanes, and reported in
one vendor test for cables up to 100 m [MAG-ADIWIKI]_. This section works
through what could stop it working over a full 100 m link, and how to find
out.

**Low frequencies and the PAM-5 spectrum.** 1000BASE-T scrambles its data so
that the transmitted symbols are uncorrelated, on each pair and between
pairs, and shapes them with the filter
:math:`\tfrac{3}{4} + \tfrac{1}{4}z^{-1}` (the output is three quarters of
the present symbol plus one quarter of the previous one) to reduce energy
above 30 MHz [MAG-AB-TUTORIAL]_ (see :doc:`phy-electrical` for PAM-5 and
scrambling). That filter has a gain of 1 at zero frequency, and there is no
line code that removes the DC content, so the signal has energy right down
to DC. Any high-pass filter in the path, transformer or capacitor, removes
some of it. The receiver's signal processing corrects the resulting baseline
wander digitally; this was a design point of 1000BASE-T [MAG-AB-TUTORIAL]_.

*Fraction of the signal power below the corner frequency (estimate).*
Model the symbol stream as uncorrelated symbols at rate :math:`1/T` with
square pulses. Its power spectrum is then proportional to
:math:`T\,\text{sinc}^2(fT)`, which is flat at low frequencies, and
whose integral from 0 to infinity is :math:`\tfrac{1}{2}` (in the same
units). Below a corner frequency :math:`f_\text{c}` far under :math:`1/T`,
the spectrum is close to its value at 0, so:

.. math::

   P_\text{below} \approx \frac{f_\text{c} T}{1/2} = 2 f_\text{c} T

where:

* :math:`P_\text{below}` is the fraction of the signal power below
  :math:`f_\text{c}` (no unit);
* :math:`T` is the symbol period, 8 ns (125 million symbols per second
  [MAG-AB-TUTORIAL]_);
* :math:`f_\text{c} = 1 / (2\pi\tau)` is the high-pass corner, with
  :math:`\tau` from the droop formula in :ref:`magnetics-cap-size`.

For :math:`C_\text{w} = 16\ \text{nF}`, :math:`\tau = 1.6\ \mu\text{s}`:

.. math::

   f_\text{c} = \frac{1}{2\pi \times 1.6\ \mu\text{s}} = 99.5\ \text{kHz}
   \qquad
   P_\text{below} = 2 \times 99.5\ \text{kHz} \times 8\ \text{ns} = 0.0016

or 0.16 % of the power. As a check, integrating
:math:`T\,\text{sinc}^2(fT)` from 0 to :math:`f_\text{c}` numerically (the
midpoint rule with 200 000 steps) and dividing by :math:`\tfrac{1}{2}` gives
0.159 %.

*Size of the baseline wander (estimate).* The part of the signal that the
high-pass filter removes is the signal passed through the matching low-pass
filter. For uncorrelated symbols of variance :math:`\sigma^2` and a filter
with time constant :math:`\tau \gg T`, the removed part has variance

.. math::

   \sigma_\text{w}^2 = \sigma^2 \sum_{k=0}^{\infty} h_k^2
   \qquad
   h_k = \frac{T}{\tau} e^{-kT/\tau}

The sum is a geometric series, and for :math:`T \ll \tau` its denominator is
close to :math:`2T/\tau`:

.. math::

   \sum_{k=0}^{\infty} h_k^2 = \frac{(T/\tau)^2}{1 - e^{-2T/\tau}}
   \approx \frac{(T/\tau)^2}{2T/\tau} = \frac{T}{2\tau}
   \qquad\Rightarrow\qquad
   \frac{\sigma_\text{w}}{\sigma} \approx \sqrt{\frac{T}{2\tau}}

where :math:`\sigma_\text{w}` is the root-mean-square (rms) baseline wander
and :math:`\sigma` the rms signal. With equally likely PAM-5 levels
:math:`\{-2, -1, 0, 1, 2\}`:

.. math::

   \sigma^2 = \frac{4 + 1 + 0 + 1 + 4}{5} = 2
   \qquad
   \sigma = 1.41\ \text{level steps}

and a symbol is decided wrongly when noise reaches half a step, 0.5. Real
1000BASE-T symbols are not equally likely; this is an assumption.
:numref:`tbl-magnetics-lowfreq` applies these formulas to four capacitor
values.

.. list-table:: Low-frequency effect of the coupling capacitor, per end of
                the link (estimates)
   :name: tbl-magnetics-lowfreq
   :header-rows: 1
   :widths: 16 14 14 14 14 14 14

   * - :math:`C_\text{w}`
     - :math:`\tau`
     - :math:`f_\text{c}`
     - left after 500 ns
     - power below :math:`f_\text{c}`
     - rms wander, share of half a step
     - tail length in symbols, :math:`\tau / T`
   * - 16 nF
     - 1.6 µs
     - 99.5 kHz
     - 73.2 %
     - 0.16 %
     - 14 %
     - 200
   * - 33 nF
     - 3.3 µs
     - 48.2 kHz
     - 85.9 %
     - 0.077 %
     - 9.8 %
     - 412
   * - 70 nF (as 350 µH magnetics)
     - 7.0 µs
     - 22.7 kHz
     - 93.1 %
     - 0.036 %
     - 6.8 %
     - 875
   * - 100 nF
     - 10 µs
     - 15.9 kHz
     - 95.1 %
     - 0.025 %
     - 5.7 %
     - 1250

For example, for 16 nF:

.. math::

   \sqrt{\frac{8\ \text{ns}}{2 \times 1.6\ \mu\text{s}}} = 0.050
   \qquad
   0.050 \times 1.41 = 0.071\ \text{level steps}
   = 14\ \%\ \text{of half a step}

With 70 nF per wire the capacitors behave like standard magnetics, so a
receiver designed for transformers sees nothing new. With 16 nF the wander
is about twice as large (the ratio is :math:`\sqrt{7.0 / 1.6} = 2.1`), which
the receiver's correction must absorb. D. Dove wrote on an IEEE 802.3
reflector (the working group's mailing list) that the 1000BASE-T scrambler
makes it "essentially impossible to get baseline wander content sufficient
to cause a measureable bit error rate" [MAG-DOVE]_, but that was said of
links with transformers.

**Echo.** Each end transmits and receives on the same pair at the same time.
A *hybrid* subtracts most of the transmitted signal from the received one,
and adaptive *echo cancellers* remove the rest [MAG-AB-TUTORIAL]_ (see
:doc:`phy-electrical`). Without a transformer the hybrid works the same way,
because it is a circuit in the transceiver. What changes is the echo's
low-frequency tail: the coupling capacitors' high-pass filter gives the echo
a slowly decaying tail of :math:`\tau / T` symbols (the last column of
:numref:`tbl-magnetics-lowfreq`). Echo cancellers in published 1000BASE-T
designs span about 50 to 120 symbols [MAG-AB-TUTORIAL]_, much shorter, so
the tail must be removed by the baseline-wander correction instead, as it
already is for transformer tails [MAG-US6775529]_. The echo is up to 10 dB
stronger than the far-end signal, so its baseline wander matters more
[MAG-US7738567]_. With the capacitors at the near end and a transformer at
the far end, the echo passes through one high-pass filter and the far-end
signal through two; the correction must handle both (an inference).

**Common-mode noise.** :clause:`40.6.1.3.3` tests a 1000BASE-T receiver with
a common-mode signal of 1.0 V rms, swept from 1 MHz to 250 MHz, coupled onto
all four pairs of a 100 m cable by a clamp near the receiver; the receiver
must keep receiving correctly [MAG-CIBULA]_. A transformer and choke reject
this before the transceiver. Without them, the coupling capacitors pass it
almost completely at these frequencies (33 nF is 4.8 Ω at 1 MHz), so the
receiver itself, plus any external choke, must reject it. The IEEE 802.3ab
task force [MAG-8023AB]_, which wrote :clause:`40`, chose the 1.0 V rms
level to keep the converted differential noise below 30 mV peak to peak
[MAG-AB-MINUTES]_. Meeting that needs a rejection of at least

.. math::

   \text{CMRR} \ge 20 \log_{10} \frac{V_\text{cm}}{V_\text{dm}}
   = 20 \log_{10} \frac{2.83\ \text{V}}{0.030\ \text{V}} = 39.5\ \text{dB}

where :math:`V_\text{cm} = 2 \sqrt{2} \times 1.0\ \text{V} = 2.83\ \text{V}`
is the peak-to-peak common-mode voltage and
:math:`V_\text{dm} = 30\ \text{mV}` the allowed differential noise. This is
an *estimate* (it assumes the clamp puts the full 1.0 V rms on the pair at
the receiver), across all four pairs, from 1 MHz to 250 MHz. It is
consistent with the 30 dB to 43 dB that magnetics provide
(:ref:`F2 <magnetics-f2>`). Analog Devices recommends an external choke for
capacitor-coupled cables longer than about 1 m for this reason
[MAG-ADIWIKI]_.

**Return loss with protection and termination parasitics.** Everything on
the chip side of the capacitors adds capacitance across the line: the chip
pads, on-chip protection, external protection diodes and board traces. A
capacitance :math:`C_\text{d}` across a 100 Ω port gives

.. math::

   \lvert\Gamma\rvert = \frac{\omega R C_\text{d}}
                             {\sqrt{4 + (\omega R C_\text{d})^2}}

with :math:`\omega = 2\pi f` and :math:`R = 100\ \Omega`. Solving for the
largest :math:`C_\text{d}` that keeps the return loss limit:

.. math::

   \omega R C_\text{d} \le \frac{2 \lvert\Gamma\rvert_\text{max}}
   {\sqrt{1 - \lvert\Gamma\rvert_\text{max}^2}}

At 40 MHz, where the limit is still 16 dB
(:math:`\lvert\Gamma\rvert = 0.158`), the right-hand side is 0.321, so:

.. math::

   C_\text{d} \le \frac{0.321}{2\pi \times 40\ \text{MHz} \times 100\ \Omega}
   = 12.8\ \text{pF}

across the pair, or about 25 pF from each wire to ground (two in series). At
100 MHz (8.1 dB, :math:`\lvert\Gamma\rvert = 0.395`) the budget is 13.7 pF.
This is the whole budget, shared with the transceiver's own termination
error; it limits how large the protection devices on the chip side may be.

**Surges and electrostatic discharge.** Without a transformer, fast
common-mode events pass straight through the coupling capacitors. Analog
Devices simulated fast transient bursts (IEC 61000‑4‑4 [MAG-IEC61000-4-4]_,
1 kV and 4 kV) on a 2 m cable with 33 nF coupling capacitors: without a
protection diode, 100 V to 400 V appeared at the transceiver pins; with one,
less than 10 V [MAG-ADIWIKI]_. External protection diodes on the chip side
of the capacitors are therefore needed, and their capacitance counts against
the budget above.

.. _magnetics-isolation-parts:

**Isolation with available parts.** The largest suitable parts known are
10 nF ceramic capacitors rated 2000 V DC, with a 2400 V DC withstand test
[MAG-KEMET1812]_. Under the rating rule in :ref:`F1 <magnetics-f1>` (the
withstand voltage must be at least the 2250 V DC test voltage), one such part
per path is enough, and 20 nF per wire takes two in parallel:

.. math::

   C_\text{w} = 2 \times 10\ \text{nF} = 20\ \text{nF}
   \qquad
   N = 8\ \text{wires} \times 2 = 16\ \text{capacitors per port}

A stricter rule, requiring the *rated* voltage to be above the test voltage,
would put two in series per path (5 nF at a 4000 V rating) and four such
strings in parallel for 20 nF: 64 capacitors per port. Either way, 20 nF
meets the 16 nF droop limit with little margin; 33 nF to 100 nF per wire
needs more parts or larger high-voltage capacitors than these, or a decision
that the full IEEE 802.3 isolation is not required (open questions 2 and 3 in
:ref:`magnetics-open-questions`).

**Experiments that would settle it.**

1. *Board-level prototype with an external gigabit transceiver.* Connect a
   gigabit transceiver with a voltage-mode driver and on-chip termination
   (such as the KSZ9031RNX [MAG-KSZ9031]_ or ADIN1300 [MAG-ADIWIKI]_) through
   coupling capacitors to an RJ45 socket, with footprints for 16 nF to
   100 nF per wire, optional common-mode chokes, protection diodes and a
   standard-magnetics variant on the same board. Run 1000BASE-T against
   several commercial switches over 0 m, 1 m, 10 m and 100 m of Category 5e
   cable, at temperature extremes, and record frame errors, the
   transceiver's signal-quality readout and link drops. This directly tests
   the central risk with an existing gigabit receiver.
2. *Compliance tests on that board.* The :clause:`40` transmitter tests
   (output voltage, droop, waveform templates), MDI return loss
   (:clause:`40.8.3.1`), and the common-mode noise test
   (:clause:`40.6.1.3.3`), as implemented in the UNH-IOL test suite
   [MAG-UNH40]_; the 2250 V DC isolation test; IEC 61000‑4‑2
   [MAG-IEC61000-4-2]_ discharge and IEC 61000‑4‑5 [MAG-IEC61000-4-5]_
   surge; radiated emissions against FCC Part 15 [MAG-FCC15]_; and Power
   over Ethernet detection and classification against standard power
   sourcing equipment.
3. *Test structures on a gf180mcu run.* The line driver with its
   termination, the receiver input with common-mode feedback, and the pin
   protection, each connected through coupling capacitors to the cable, to
   measure common-mode range and rejection, return loss and clamp
   behaviour before the full transceiver exists.

F1 without a transformer: isolation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Options:

* **External high-voltage coupling capacitors** (described in patents and in
  TI's note, which says "high voltage multi-layer ceramic capacitors are
  readily available" [MAG-SNLA088]_ [MAG-US8132027]_). A capacitor blocks DC,
  so it passes the 2250 V DC test (the second of the three allowed tests in
  :numref:`tbl-magnetics-hipot`) if it meets the rating rule in
  :ref:`F1 <magnetics-f1>`. Ceramic capacitors of 10 nF with a 2400 V DC
  withstand test exist in a 4.5 mm × 3.2 mm package [MAG-KEMET1812]_; no
  33 nF to 100 nF part at that rating is known, so several are used in
  parallel (:ref:`isolation with available parts <magnetics-isolation-parts>`).
* **Safety-rated capacitors.** The surface-mount capacitors certified for
  bridging insulation (class Y2 under IEC 60384-14 [MAG-IEC60384-14]_) that
  are cited here go up to 4.7 nF [MAG-KEMETCAS]_, below the 16 nF needed.
  Whether the IEEE 802.3 isolation is a safety function for evampire boards
  (and so needs safety-rated parts) is decided by the product safety
  standard, IEC 62368-1 [MAG-IEC62368]_, and is open.
* **On-chip isolation** with a second, line-side circuit powered separately
  and a high-frequency link across an on-chip barrier. Not ruled out by the
  process limits, but unproven at 1500 V rms in this process
  (:ref:`magnetics-gf180-limits`), and it needs the line-side circuit to be
  on a separate die or an insulating substrate, because both sides would
  otherwise share the silicon substrate.
* **No isolation**, for boards used only inside one enclosure with a shared
  ground. This does not meet IEEE 802.3 (the quoted clauses have no
  exception for this case [MAG-POTTERF]_).

The AC test (1500 V rms) is hard to pass with capacitors because they
conduct at 50 Hz. The current is

.. math::

   I = 2\pi f C_\text{total} V
   \qquad
   C_\text{total} = 8 C_\text{w}

where :math:`f = 50\ \text{Hz}`, :math:`V = 1500\ \text{V}`, and
:math:`C_\text{total}` is all eight capacitors in parallel, because the test
is applied between all MDI wires together and the equipment.
:numref:`tbl-magnetics-ac-current` gives the result for four capacitor
values.

.. list-table:: Current through the coupling capacitors in the 1500 V rms,
                50 Hz test
   :name: tbl-magnetics-ac-current
   :header-rows: 1

   * - Capacitor per wire
     - Total capacitance
     - Test current
   * - 10 nF
     - 80 nF
     - 37.7 mA
   * - 20 nF
     - 160 nF
     - 75.4 mA
   * - 33 nF
     - 264 nF
     - 124 mA
   * - 100 nF
     - 800 nF
     - 377 mA

These currents are far above what a hipot tester normally allows before
deciding that the insulation has failed (an assumption; the trip current is
set by the tester and the safety standard, not by IEEE 802.3). A
capacitor-coupled port should therefore be designed for the DC test.

Isolation also has to hold in the power path. With capacitor-coupled data,
the Power over Ethernet circuits connect to the cable directly. The
transformerless Power over Ethernet patent [MAG-US8132027]_ isolates its
power converter; that an isolated converter is required for the port to pass
the test is an inference.

F2 without a transformer: common-mode rejection and level shifting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The coupling capacitors block DC and slow changes of common-mode voltage, so
the chip-side common-mode voltage is set by the chip, not by the cable. Fast
common-mode changes pass through the capacitors and must be handled on the
chip-side nodes.

**Common-mode at mains frequency (estimate).** This estimates how much of a
slow ground difference between the two ends of the cable reaches the chip.
Suppose the cable's common-mode voltage moves at 50 Hz relative to the chip
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
  the bias voltage, in Ω; 1 kΩ is *assumed* here;
* :math:`X_\text{cm}` is the reactance of the pair's two coupling capacitors
  in parallel, in Ω;
* :math:`f` is the frequency, 50 Hz;
* :math:`C_\text{w}` is the coupling capacitor per wire, 33 nF (from
  :ref:`magnetics-cap-size`).

Substituting:

.. math::

   X_\text{cm} = \frac{1}{2\pi \times 50 \times 66\ \text{nF}} = 48.2\ \text{kΩ}
   \qquad
   \frac{V_\text{chip}}{V_\text{cable}} = \frac{1}{\sqrt{1 + 48.2^2}} = 0.021

About 2 % of a mains-frequency ground difference reaches the chip. At signal
frequencies the capacitors pass common-mode noise almost completely, so
rejection there must come from the receiver and from a choke or termination.

Options:

* **External common-mode choke**, as in single-pair automotive Ethernet
  (proven; for example 200 µH chokes with 42 dB common-mode rejection from
  10 MHz to 100 MHz for 100BASE-T1 [MAG-DP83TC811]_).
* **On-chip receiver with a wide common-mode range and high rejection**, and
  a **common-mode feedback loop** that senses the pair's common-mode voltage
  and drives it back to the bias point. Integrated receivers for other
  twisted-pair buses show what is possible in high-voltage processes:
  receivers for CAN (Controller Area Network, the vehicle bus) with a ±12 V
  common-mode range and ±58 V fault protection [MAG-TCAN1044]_, and for
  RS-485 (a differential serial bus for industrial wiring) with a ±25 V
  range and ±70 V fault protection [MAG-THVD2450]_. In gf180mcu the range is
  limited to the supplies of the 5 V or 6 V devices unless a custom structure
  is used.
* **Active common-mode choke**: a circuit that senses and cancels
  common-mode current. A commercial part adds "up to 10dB" of common-mode
  suppression from 1 MHz to 125 MHz, but alongside a transformer, not instead
  of one [MAG-KTA1552]_; the patent behind it notes "a fundamental trade-off
  between loop stability and common mode rejection ratio" [MAG-US7965480]_.

The rejection a transformer gives (30 dB to 43 dB, :ref:`F2 <magnetics-f2>`)
and the 39.5 dB estimate in :ref:`magnetics-central-risk` give the target for
the combination of choke, capacitors and on-chip circuits.

F4 without a transformer: synthesised termination
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With a voltage-mode driver the 100 Ω termination is already on the chip
[MAG-KSZ9031]_ [MAG-DP83TC811]_, so impedance matching does not need the
transformer. The coupling capacitors add series reactance at low frequencies
(:ref:`magnetics-cap-size`). *Active termination* (also called synthesised
impedance), in which feedback in the driver sets the output impedance
instead of a resistor, saves transmit power and is used in line drivers for
telephone-line data links [MAG-US6538500]_; no published 1000BASE-T driver
using it is known. It could also compensate the coupling capacitors'
reactance; this is an idea, not a proven technique.

F5 without a transformer: low-frequency response
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The coupling capacitors set the droop (:ref:`magnetics-cap-size`). If Power
over Ethernet inductors are fitted across the pair, they also shunt low
frequencies, exactly as a transformer's magnetising inductance does, so the
same 80 µH minimum (1000BASE-T) applies to their inductance across the pair
[MAG-GARDNER14]_. The receiver's baseline-wander correction (see
:doc:`phy-electrical`) must absorb whatever the capacitors and inductors
remove; :ref:`magnetics-central-risk` estimates how much. Only if 100BASE-TX
is supported: whether IEEE 802.3 accepts a 100BASE-TX transmitter without a
350 µH inductance is not settled, because the requirement is written in
terms of inductance, with a droop alternative only for Power over Ethernet
equipment above 13 W [MAG-TRACY]_.

F6 and F7 without a transformer: common-mode termination and filtering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **External termination** on the cable side, as in the standard circuit
  (75 Ω per pair to a shared capacitor to chassis), with a DC-blocking
  capacitor per resistor when Power over Ethernet is present. Without the
  transformer the pair has no centre tap, so the termination needs two
  resistors per pair, one from each wire, to form one; single-pair
  automotive Ethernet does this with two 1 kΩ resistors and a 4.7 nF
  capacitor [MAG-OA100T1]_. No published values for four-pair BASE-T are
  known; the values are an open design question.
* **External choke**, as above.
* **On-chip active termination** of the common mode: the common-mode feedback
  loop described under F2 can present a defined impedance (for example
  75 Ω) to common-mode signals at the chip side of the capacitors. This is an
  idea, not a proven technique; its bandwidth must reach the frequencies
  where emissions are measured.

F8 without a transformer: surges and electrostatic discharge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Without a transformer, a common-mode surge is held off only by the coupling
capacitors' voltage rating, and the fast edge that passes through them must
be clamped on the chip side.

* **External protection diodes** between each chip-side node and signal
  ground, after the coupling capacitors. They do not break the isolation,
  because the capacitors are in series with them.
* **On-chip clamps.** The I/O cells target 2000 V human-body model
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
  Across the pair it must have at least 80 µH (:ref:`F5 <magnetics-f5>`).
  For the Power over Ethernet series-inductance limit (less than 100 µH,
  :ref:`F11 <magnetics-f11>`) only its leakage inductance counts, because the
  current flows through the two halves in opposite directions. Centre-tapped
  windings carry Power over Ethernet current in standard magnetics; no
  stand-alone part sold for this use is known.
* **Two separate inductors per pair.** Simple, but each inductor carries the
  full current of one wire without saturating, up to

  .. math::

     \frac{938\ \text{mA}}{2} = 469\ \text{mA}

  with equal sharing (Class 8 [MAG-EA8023BT]_), and the two together must
  still exceed 80 µH across the pair. Their series inductance on the power
  path is the full inductance, which conflicts with the 100 µH limit for a
  powered device. Coupled inductors sold for single-pair power have 56 µH to
  250 µH per winding, with saturation currents from 0.36 A to 2.1 A
  depending on size [MAG-TDKSPE]_.
* **Active inductor** (*gyrator*): a transistor circuit that passes DC with
  low resistance but presents a high impedance at signal frequencies.
  Patented for single-pair power, with a drop of about 2 V per device and an
  emulated inductance "on the order of millihenries", adequate "up to about
  100 Mbps" [MAG-US11038490]_ [MAG-US11394315]_; no product using it is
  known. The pass device must withstand 57 V and carry about 0.5 A, beyond
  any documented gf180mcu device (:numref:`tbl-magnetics-gf180`), so it would
  be an external transistor controlled from the chip. Its noise, linearity
  and loss (about 1 W at 0.5 A and 2 V, an estimate) are open questions.

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

With :math:`C_\text{w} = 33\ \text{nF}` this adds 33 nF to the 50 nF to
120 nF window of :numref:`tbl-magnetics-poe-numbers`; with 100 nF it adds
100 nF, which uses almost the whole window. The actual value depends on
where the chip ground sits relative to the powered device's input, and is an
open question.

When the port supplies power, the chip-side nodes of the capacitors must
also survive the detection, classification and power-on steps of the
power sourcing equipment (2.7 V to 57 V, see :doc:`../power/poe`); the
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

:numref:`fig-magnetics-arch-capacitor` shows one pair of front end 1.

.. graphviz:: magnetics/arch-capacitor.dot
   :name: fig-magnetics-arch-capacitor
   :caption: Front end 1, one pair shown. High-voltage capacitors carry the
             data and block DC; a centre-tapped inductor across the pair
             carries the Power over Ethernet current (circuits described on
             :doc:`../power/poe`); an optional common-mode choke and a
             cable-side termination handle common-mode noise; clamps protect
             the chip-side nodes; active circuits on evampire terminate the
             line, receive, and control the common-mode voltage, followed by
             the converters and signal processing described on
             :doc:`phy-electrical`.
   :alt: Block diagram. RJ45 pins 1 and 2 go through an optional
         common-mode choke and high-voltage coupling capacitors to the
         evampire pins. A centre-tapped inductor across the pair feeds the
         Power over Ethernet circuits. A common-mode termination to chassis
         connects at the socket. Surge and ESD clamps connect at the chip
         side of the capacitors. Inside evampire, the pins connect to a line
         driver with synthesised 100 ohm termination, a receiver with wide
         common-mode range, a common-mode sense and feedback block, and pin
         protection; converters and signal processing follow.
   :align: center

External parts per port (four pairs): eight coupling paths of high-voltage
capacitors (at least 16 nF each for 1000BASE-T, preferably 33 nF to 100 nF,
meeting the rating rule in :ref:`F1 <magnetics-f1>`), four centre-tapped
inductors (if the port carries Power over Ethernet on all pairs), protection
diodes, the common-mode termination (two resistors per pair to a capacitor
to chassis, values open), and optionally four common-mode chokes.

Every part of this front end is used in shipping products in some form:
capacitor coupling in automotive Ethernet [MAG-DP83TC811]_ [MAG-OA100T1]_
and backplane Ethernet [MAG-ENT114]_, inductors in power over a single pair
[MAG-DP83TD510E]_ [MAG-TDKSPE]_, centre-tapped windings in Power over
Ethernet magnetics [MAG-TPS2376H]_. The combination at 1000 Mbit/s over
100 m of cable is reported only in one vendor test, without a choke
[MAG-ADIWIKI]_.

Front end 2: more on the chip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The same structure, with these changes:

* the common-mode choke is replaced by on-chip common-mode feedback and
  termination (:ref:`F2 <magnetics-f2>`, :ref:`F6 <magnetics-f6>`,
  :ref:`F7 <magnetics-f7>`);
* the centre-tapped inductors are replaced by active inductors: external
  high-voltage transistors controlled by circuits on evampire
  (:ref:`F10 <magnetics-f10>`);
* the external protection diodes are reduced to what the coupling capacitors
  and custom on-chip clamps cannot handle (:ref:`F8 <magnetics-f8>`).

This front end needs fewer and smaller external parts, but each change is
proven only in patents or papers, not in products.

On-chip coupling capacitors are a further custom-structure option: their
cost is tens of square millimetres per port, and enough of them in series to
hold the Power over Ethernet voltage (:ref:`magnetics-gf180-limits`). Whether
to pursue them is an open decision (:ref:`magnetics-open-questions`).

Key circuit specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~

:numref:`tbl-magnetics-specs` collects the specifications that the analysis
above sets for the on-chip circuits. The requirements of the integrated
transceiver as a whole are on :doc:`phy-electrical`.

.. list-table:: Specifications for the on-chip circuits. Values marked
                "estimate" are derived on this page, not taken from a
                standard.
   :name: tbl-magnetics-specs
   :header-rows: 1
   :widths: 32 30 38

   * - Circuit
     - Specification
     - Basis
   * - Line driver
     - 1000BASE-T: 0.67 V to 0.82 V peak differential in the test pattern,
       PAM-5 at 125 million symbols per second on each of four pairs;
       100 Ω output impedance within the return loss budget. Only if
       10BASE-T is supported: up to 2.8 V peak.
     - [MAG-UNH40]_ [MAG-INTERP1196]_; :ref:`F4 <magnetics-f4>`
   * - Voltage at each chip pin
     - each pin carries about ±0.4 V of transmit signal (half the 0.82 V
       differential peak) plus the received signal, around the common-mode
       level; ±1.4 V of transmit signal only if 10BASE-T is supported
     - estimate; fits within 3.3 V or 5 V devices
   * - Total capacitance across each pair, chip side
     - at most about 12.8 pF, including pads, protection and traces
     - estimate; :ref:`magnetics-central-risk`
   * - Baseline-wander correction
     - tracks a high-pass time constant from 1.6 µs upwards, at both ends
       of the link, for the far-end signal and the echo
     - estimate; [MAG-US6775529]_ [MAG-US7738567]_
   * - Receiver common-mode rejection
     - at least about 40 dB from 1 MHz to 250 MHz on all four pairs,
       together with any external choke
     - estimate from :clause:`40.6.1.3.3`; magnetics give 30 dB to 43 dB
       [MAG-PULSE]_ [MAG-BEL]_
   * - Common-mode feedback
     - holds the pair's common-mode voltage within the receiver's range for
       fast common-mode steps passed by the capacitors; effective up to
       250 MHz (the :clause:`40.6.1.3.3` test range) if it replaces the
       choke
     - estimate
   * - Pin protection
     - survives the charge passed by :math:`C_\text{w}` during common-mode
       steps; human-body model 2000 V as a minimum
     - [MAG-GFIO]_; :ref:`F8 <magnetics-f8>`
   * - Active inductor control (front end 2)
     - high impedance across the pair down to about 23 kHz (equivalent to
       350 µH) or at least 80 µH; about 0.5 A per wire through an external
       transistor rated above 57 V
     - :ref:`F5 <magnetics-f5>`, :ref:`F10 <magnetics-f10>`

Which IEEE 802.3 requirements a transformer-free port can meet
--------------------------------------------------------------

:numref:`tbl-magnetics-ieee` lists the IEEE 802.3 requirements that the
transformer normally helps meet, and where front end 1 stands on each.

.. list-table:: IEEE 802.3 requirements for a port with front end 1
   :name: tbl-magnetics-ieee
   :header-rows: 1
   :widths: 30 15 55

   * - Requirement
     - Can meet?
     - How, and consequence
   * - Isolation, DC test (2250 V DC, 60 s)
     - Yes, with suitable parts
     - Coupling capacitors that meet the rating rule in
       :ref:`F1 <magnetics-f1>`, and an isolated Power over Ethernet power
       path.
   * - Isolation, AC test (1500 V rms, 60 s)
     - Unlikely
     - 38 mA to 377 mA flows through the capacitors
       (:numref:`tbl-magnetics-ac-current`); the port should be qualified
       with the DC test instead.
   * - Isolation, impulse test
     - Depends on the capacitors and clamps
     - The capacitors must hold 2400 V (1500 V with Power over Ethernet).
   * - Return loss (1000BASE-T)
     - Yes
     - Coupling capacitors of at least about 16 nF per wire, and at most
       about 12.8 pF across each pair on the chip side.
   * - Droop (1000BASE-T)
     - Yes
     - Capacitors and any inductors as calculated in
       :ref:`magnetics-cap-size`.
   * - Common-mode noise rejection (1000BASE-T)
     - Unproven
     - About 40 dB needed in the receiver and any choke; must be measured.
   * - Operation over a 100 m link (1000BASE-T)
     - Unproven
     - Reported in one vendor test only; see :ref:`magnetics-central-risk`.
   * - 350 µH inductance (only if 100BASE-TX is supported)
     - Not as written
     - Equivalent behaviour is possible; the requirement is written for an
       inductance.
   * - Power over Ethernet signature and classification
     - Yes, with care
     - Extra capacitance from the coupling capacitors must fit in the
       50 nF to 120 nF window; series inductance must stay under 100 µH.
   * - Radio interference limits
     - Unproven
     - Must be measured; a common-mode choke reduces the risk.

Consequences:

* A transformer-free port is intended to work with standard equipment: the
  signals on the cable are the same as those of a port with magnetics.
  Whether it does so over a full 100 m link is open question 1
  (:ref:`magnetics-open-questions`).
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
socket, with the 75 Ω resistors and the high-voltage capacitor as separate
parts) or built into an **RJ45 socket with integrated magnetics**, usually
including the termination and two LEDs driven by the transceiver. Integrated
sockets save space and screen the cable-side wiring in their metal shield;
their smaller cores can make crosstalk and common-mode rejection worse
[MAG-ENT98]_. TI recommends a discrete transformer for better
electromagnetic compatibility [MAG-DP83867]_.

Chassis ground, shield and layout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:numref:`fig-magnetics-layout` shows the board areas around one port. Board
dimensions below are given in mil (one thousandth of an inch, 25.4 µm), as
in the cited guidance, with the metric value alongside.

.. graphviz:: magnetics/layout.dot
   :name: fig-magnetics-layout
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
* Join the two grounds through a resistor of 1 MΩ or more and a capacitor,
  with a keep-out of at least 20 mil (0.51 mm) on all layers
  [MAG-SNLA387]_. These parts bridge the isolation barrier and must meet the
  rating rule in :ref:`F1 <magnetics-f1>`.
* Route each pair as a 100 Ω ± 10 % differential pair over a continuous
  ground plane, under 2 inches (51 mm) long, with the two traces matched
  within 20 mil (0.51 mm) at 1000 Mbit/s and pairs at least 30 mil
  (0.76 mm) apart [MAG-SNLA387]_.
* Keep all copper away from under the magnetics on every layer
  [MAG-SNLA387]_ [MAG-DP83867]_.
* Place protection diodes on the transceiver side of the magnetics
  [MAG-SNLA387]_.

What to look for in a magnetics data sheet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:numref:`tbl-magnetics-checklist` lists what transceiver makers ask of the
magnetics, and :numref:`tbl-magnetics-parts` gives three examples. Data
sheets write the turns ratio as "1CT:1CT": one turn to one turn, with a
centre tap (CT) on both windings.

.. list-table:: Typical requirements for 10/100/1000 Mbit/s magnetics
                [MAG-KSZ9031]_ [MAG-DP83867]_ [MAG-ENT98]_
   :name: tbl-magnetics-checklist
   :header-rows: 1
   :widths: 35 65

   * - Parameter
     - Typical requirement
   * - Turns ratio
     - 1CT:1CT within ±2 % to ±3 %
   * - Open-circuit inductance
     - 350 µH minimum at 100 kHz, 100 mV, 8 mA DC bias
   * - Insertion loss
     - 1 dB maximum, 1 MHz to 100 MHz
   * - Return loss
     - at least about 18 dB, 2 dB better than the 16 dB the standard
       requires from 1 MHz to 40 MHz; data sheets state it over 1 MHz to
       30 MHz or 40 MHz (:numref:`tbl-magnetics-parts`)
   * - Common-mode rejection and crosstalk
     - 30 dB or more
   * - Isolation
     - 1500 V rms for 1 minute
   * - Centre taps
     - four separate circuit-side centre taps (for a voltage-mode
       transceiver); cable-side centre taps available for the termination
   * - Choke position
     - cable side
   * - Power over Ethernet
     - rated for the current, on the port that takes or supplies power

.. list-table:: Example gigabit magnetics, with values from the
                manufacturers' data sheets
   :name: tbl-magnetics-parts
   :header-rows: 1
   :widths: 25 20 55

   * - Part
     - Form
     - Key values
   * - Pulse H5007NL
     - discrete module
     - 1:1; insertion loss 1 dB max; return loss 18 dB (1–30 MHz and
       40 MHz), 16 dB (50 MHz), 12 dB (60–80 MHz), 10 dB (100 MHz);
       1500 V rms; inductance not listed [MAG-PULSE]_
   * - Würth Elektronik 7499111221A
     - RJ45 with magnetics, two LEDs
     - 350 µH min at 8 mA; 1500 V rms for 1 min; insertion loss 1 dB max;
       return loss 18 / 14 / 9 / 8 dB over 1–30 / 30–60 / 60–80 /
       80–100 MHz; four 75 Ω and 1000 pF, 2 kV inside; not for Power over
       Ethernet [MAG-WURTH]_
   * - Bel Fuse 0826-1G1T-23-F
     - RJ45 with magnetics, two LEDs, 12 cores
     - 1CT:1CT ±2 %; 350 µH min at 8 mA; return loss 18 dB (0.5–40 MHz);
       1500 V rms, every part tested; four 75 Ω and 1000 pF, 2 kV inside
       [MAG-BEL]_

First-version board, per port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each of ports A and B (see :ref:`requirements`) needs one external
transceiver with an RGMII interface (:doc:`rgmii`); one set of four-channel
magnetics for 1000BASE-T (discrete or in the socket); the circuit-side
centre-tap connection its data sheet asks for; the cable-side termination
unless it is in the socket; a shielded RJ45 socket on a chassis ground area;
and the resistor and capacitor joining the two grounds. The port that takes
or supplies Power over Ethernet (in the first version port A takes power and
port B supplies it, see :ref:`power-board-configs` and :ref:`power-flow`)
also needs PoE-rated magnetics, DC-blocking capacitors in the termination,
and the power circuits on the cable-side centre taps.

.. _magnetics-open-questions:

Open design questions
---------------------

1. **Gigabit over 100 m.** Does capacitor-coupled 1000BASE-T work reliably
   over a full 100 m link with standard link partners, and with which
   capacitor value and choke? See the experiments in
   :ref:`magnetics-central-risk`.
2. **Isolation.** Is the full design required to pass the IEEE 802.3
   isolation test, and is the DC test (2250 V) an acceptable way to do so?
   Are safety-rated capacitors required, and if so how is the 16 nF minimum
   met when the certified surface-mount parts cited stop at 4.7 nF?
3. **Coupling capacitors.** Which parts give 16 nF to 100 nF per wire with a
   withstand voltage of at least 2250 V DC, and at what size and cost for
   eight paths per port?
4. **Power path isolation.** Must the Power over Ethernet converter on each
   port be isolated, given that capacitor coupling puts the power circuits
   directly on the cable?
5. **Power separation.** Centre-tapped inductors, separate inductors, or
   active inductors? Can a centre-tapped inductor meet both the 80 µH data
   requirement and the 100 µH powered-device limit at 938 mA per pair?
6. **Common-mode noise.** Is an external common-mode choke needed to meet
   radio-interference limits, or can on-chip common-mode feedback and
   termination replace it? What termination values suit four-pair cable
   without centre taps?
7. **Protection.** What external protection is needed for system-level
   discharge, surges and charged-cable events, and what charge must on-chip
   clamps absorb behind the coupling capacitors?
8. **Detection capacitance.** How much capacitance do the coupling
   capacitors add to the powered-device signature in the actual grounding
   arrangement?
9. **Process options.** Is the 10 V LDMOS available in the wafer.space flow,
   and what are the breakdown voltages of the deep N-well and of the oxide
   between metal layers? These decide how much protection and common-mode
   range can move onto the chip, and whether on-chip coupling or isolation
   capacitors are worth pursuing.
10. **Conformance.** How will the port be tested against IEEE 802.3 where
    the standard assumes a transformer (the 350 µH inductance requirement,
    if 100BASE-TX is supported)?

References
----------

.. [MAG-IEEE8023] IEEE Std 802.3-2022, *IEEE Standard for Ethernet*.
   https://standards.ieee.org/ieee/802.3/10422/
.. [MAG-8023AB] IEEE 802.3ab task force (1000BASE-T).
   https://www.ieee802.org/3/ab/
.. [MAG-8023AT] IEEE 802.3at task force (Power over Ethernet, Type 2).
   https://www.ieee802.org/3/at/
.. [MAG-8023BU] IEEE 802.3bu task force (power over a single data pair).
   https://www.ieee802.org/3/bu/
.. [MAG-8023CG] IEEE 802.3cg task force (10 Mbit/s single-pair Ethernet).
   https://www.ieee802.org/3/cg/
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
   and :clause:`25.4.7 <25.4.7>`), 2011.
   https://www.ieee802.org/3/maint/public/tracy_1_0911.pdf
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
.. [MAG-ADIWIKI] Analog Devices, *ADIN1300 and ADIN1200 with Capacitive
   Coupling*, EngineerZone wiki, approved 2021-02-11.
   https://wiki.analog.com/resources/eval/user-guides/adin1300-and-adin1200/cap-coupling
.. [MAG-AB-TUTORIAL] IEEE 802.3ab task force, *1000BASE-T tutorial*, IEEE
   802 plenary, 1998-03.
   https://www.ieee802.org/3/tutorial/march98/mick_170398.pdf
.. [MAG-AB-MINUTES] IEEE 802.3ab task force, minutes of the interim meeting,
   Austin, 1998-09-03 to 1998-09-04.
   https://www.ieee802.org/3/ab/public/sept98/minutes_0998.pdf
.. [MAG-DOVE] D. Dove, message on the IEEE 802.3 Power over Ethernet Plus
   study group reflector (baseline wander in 1000BASE-T), 2008-01.
   https://grouper.ieee.org/groups/802/3/poep_study/email/msg00655.html
.. [MAG-CIBULA] Cibula (Intel), receiver common-mode noise rejection, IEEE
   802.3bq, 2014-07 (quotes :clause:`40.6.1.3.3`).
   https://www.ieee802.org/3/bq/public/jul14/cibula_3bq_02a_0714.pdf
.. [MAG-US6775529] US patent 6,775,529 (Marvell), 1000BASE-T transceiver
   with baseline-wander correction for transformer tails.
   https://patents.google.com/patent/US6775529
.. [MAG-US7738567] US patent 7,738,567 (Texas Instruments), baseline-wander
   correction for the far-end signal and the echo.
   https://patents.google.com/patent/US7738567
.. [MAG-UNHXO] M. Hersh, *Auto-Crossover White Paper*, University of New
   Hampshire InterOperability Laboratory, 2006.
   https://www.iol.unh.edu/sites/default/files/knowledgebase/ethernet/Auto-Crossover_White_Paper.pdf
.. [MAG-EA8023BT] Ethernet Alliance, *Overview of 802.3bt Power over
   Ethernet*, version 2.1, 2019-12 (white paper tables 15, 16 and 18, and
   its section 3).
   https://ethernetalliance.org/wp-content/uploads/2019/12/WP_EA_Overview8023bt_V2p1_FINAL.pdf
.. [MAG-SMITH] R. W. Smith, *Apparatus and method for terminating cables to
   minimize emissions and susceptibility*, US patent 5,321,372, 1994-06-14.
   https://patents.google.com/patent/US5321372A
.. [MAG-IEC61000-4-2] IEC 61000-4-2, *Electromagnetic compatibility –
   Testing and measurement techniques – Electrostatic discharge immunity
   test*. https://webstore.iec.ch/en/publication/4189
.. [MAG-IEC61000-4-4] IEC 61000-4-4:2012, *Electrical fast transient/burst
   immunity test*. https://webstore.iec.ch/publication/4222
.. [MAG-IEC61000-4-5] IEC 61000-4-5, *Surge immunity test*.
   https://webstore.iec.ch/en/publication/61166
.. [MAG-IEC62368] IEC 62368-1, *Audio/video, information and communication
   technology equipment – Safety requirements*.
   https://webstore.iec.ch/en/publication/27412
.. [MAG-IEC60384-14] IEC 60384-14:2023, *Fixed capacitors for
   electromagnetic interference suppression and connection to the supply
   mains*. https://webstore.iec.ch/publication/64361
.. [MAG-FCC15] US Code of Federal Regulations, title 47, part 15, *Radio
   frequency devices*.
   https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15
.. [MAG-ENT98] Microchip (Microsemi), *Magnetics Guide*, ENT-AN0098,
   revision 2.2, 2018-06. Archived product page:
   https://web.archive.org/web/20250911203723/https://www.microchip.com/en-us/application-notes/entan0098magneticsguide
.. [MAG-ENT106] Microchip (Microsemi), *SimpliPHY Architecture Advantages*,
   ENT-AN0106, revision 1.1. Available from Microchip's application-note
   library at https://www.microchip.com (search for ENT-AN0106).
.. [MAG-ENT114] Microchip (Microsemi), *SimpliPHY Transformerless Ethernet
   Designs*, ENT-AN0114, revision 2.0, 2018-06.
   https://www.microchip.com/en-us/application-notes/entan0114simpliphytransformerl
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
.. [MAG-POMMERENKE] D. Pommerenke, *Charged cable event*, IEEE 802.3 copper
   discharge ad hoc, 2001-02-23.
   https://www.ieee802.org/3/ad_hoc/copperdis/public/docs/charged_cable_event.pdf
.. [MAG-SNLA087] Texas Instruments, *AN-1511 Cable Discharge Event*,
   SNLA087A. https://www.ti.com/lit/pdf/snla087
.. [MAG-DEATHERAGE] J. Deatherage and D. Jones (Intel), "Multiple factors
   trigger cable discharge events in Ethernet LANs", *Electronic Design*,
   2000-12-04.
   https://www.electronicdesign.com/markets/energy/article/21768121/multiple-factors-trigger-cable-discharge-events-in-ethernet-lans
.. [MAG-ESDA] EOS/ESD Association, *EOS/ESD Fundamentals Part 5: Device
   Sensitivity and Testing* (human-body model 100 pF, 1.5 kΩ).
   https://www.esda.org/esd-overview/esd-fundamentals/part-5-device-sensitivity-and-testing/
.. [MAG-SSZY028] Texas Instruments, *Enabling high voltage signal isolation
   quality and reliability*, SSZY028, 2017-03.
   https://www.ti.com/lit/pdf/sszy028
.. [MAG-SSZY024] Texas Instruments, *High-voltage isolation quality and
   reliability for AMC130x*, SSZY024. https://www.ti.com/lit/pdf/sszy024
.. [MAG-KAERIYAMA] S. Kaeriyama et al., "A 2.5 kV Isolation 35 kV/µs CMR
   250 Mbps Digital Isolator in Standard CMOS With a Small Transformer
   Driving Technique", *IEEE Journal of Solid-State Circuits*, 47(2), 2012.
   https://doi.org/10.1109/JSSC.2011.2170775
.. [MAG-GF180] GlobalFoundries and Google, *gf180mcu PDK documentation*:
   electrical specifications (sections 1, 3, 5.4, 5.5, 6.2 and 8),
   inter-layer specifications (dielectric thicknesses), and design rule
   manual section 14.1.
   https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs.html
.. [MAG-GFIO] GlobalFoundries and Google, *gf180mcu_fd_io I/O library*,
   ESD protection targets (docs/specs/16_ESD_Protection.csv) and analog
   pads (docs/analog.rst).
   https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_io
.. [MAG-KSZ9031] Microchip, *KSZ9031RNX Gigabit Ethernet Transceiver with
   RGMII Support*, DS00002117F (MDI/MDI-X pin mapping, and section 12 on
   magnetics). https://ww1.microchip.com/downloads/en/DeviceDoc/00002117F.pdf
.. [MAG-DP83867] Texas Instruments, *DP83867IR/CR 10/100/1000 Ethernet PHY
   Layer Transceiver*, SNLS484 (section 9.2).
   https://www.ti.com/lit/ds/symlink/dp83867ir.pdf
.. [MAG-TPS2376H] Texas Instruments, *TPS2376-H*, SLVS646B (sections 9.2.1.2
   and 9.2.1.3). https://www.ti.com/lit/ds/symlink/tps2376-h.pdf
.. [MAG-DP83TC811] Texas Instruments, *DP83TC811-Q1 100BASE-T1 Automotive
   Ethernet PHY*, SNLS742A (MDI component table).
   https://www.ti.com/lit/ds/symlink/dp83tc811-q1.pdf
.. [MAG-DP83TD510E] Texas Instruments, *DP83TD510E 10BASE-T1L Ethernet PHY*,
   SNLS656D (power coupling inductor and choke tables).
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
   2000 V DC rated, 2400 V DC withstand, 1812).
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
   *PoDL powered device with active rectifier bridge* (Analog Devices),
   2022-07-19. https://patents.google.com/patent/US20210104953A1
.. [MAG-US6538500] US patent 6,538,500 (Texas Instruments), active
   impedance termination in a line driver.
   https://patents.google.com/patent/US6538500
.. [MAG-PULSE] Pulse Electronics, *1000BASE-T Magnetics Module* (H5004NL,
   H5007NL), HC500.T, 2020-06. Copy hosted by a distributor:
   https://static.chipdip.ru/lib/232/DOC012232653.pdf
.. [MAG-WURTH] Würth Elektronik, *WE-RJ45LAN Transformer 10/100/1000Base-T*,
   7499111221A, revision 005.000, 2020-10-07. Archived copy:
   https://web.archive.org/web/20250126113004/https://www.we-online.com/components/products/datasheet/7499111221A.pdf
.. [MAG-BEL] Bel Fuse, *gigabit MagJack 0826-1G1T-23-F*, drawing revision F.
   https://www.belfuse.com/media/drawings/products/magjack%20ICMs/dr-mag-0826-1g1t-23-f.pdf
