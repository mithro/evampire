Candidate front ends for a transformer-free port
================================================

This page describes two candidate front ends for a full-design port, which
connects to the cable without coupling transformers
(:ref:`board configurations <tab-power-board-configs>`). It gives the
specifications they set for the circuits on evampire, and the IEEE 802.3
requirements a port built this way meets. Both front ends use a
voltage-mode line driver on evampire, and differ in how much of the work
external passive parts do.

Both front ends use one of the isolation routes of :doc:`isolation`. The
figure shows the external-capacitor route; the other routes change only
where the barrier sits.

The passive front end uses external parts for power and filtering
-----------------------------------------------------------------

:numref:`fig-magnetics-arch-capacitor` shows one pair of the passive
front end. High-voltage capacitors carry the data and block direct
voltage. A centre-tapped inductor across the pair carries the Power over
Ethernet current to the power circuits (:doc:`../../power/poe/index`). An
optional common-mode choke and a cable-side termination handle common-mode
noise, and clamps protect the chip-side nodes. On evampire, the line
driver terminates the line, the receiver takes the signal, and a feedback
loop holds the common-mode voltage, followed by the converters and signal
processing of :doc:`../phy-electrical/index`.

.. graphviz:: arch-capacitor.dot
   :name: fig-magnetics-arch-capacitor
   :caption: One pair of the passive front end, with external high-voltage
             coupling capacitors.
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

:numref:`tbl-magnetics-passive-parts` lists the external parts for one
port of four pairs.

.. list-table:: External parts of the passive front end, for one port
   :name: tbl-magnetics-passive-parts
   :header-rows: 1
   :widths: 46 14 40

   * - Part
     - Number
     - Value
   * - High-voltage coupling capacitor paths
     - 8
     - 16 nF or more; 33 nF to 100 nF preferred (:doc:`coupling-capacitors`)
   * - Centre-tapped inductors, for four-pair Power over Ethernet
     - 4
     - 80 µH or more across the pair (:doc:`without-transformer`)
   * - Common-mode termination resistors
     - 8
     - open question (:doc:`without-transformer`)
   * - Common-mode termination capacitor to chassis
     - 1
     - withstands the isolation test
   * - Protection diodes
     - 8
     - open question
   * - Common-mode chokes (optional)
     - 4
     - open question

Each part of this front end is used in products in some form. Capacitor
coupling is used in automotive Ethernet ([MAG-DP83TC811]_,
[MAG-OA100T1]_) and on backplanes ([MAG-ENT114]_). Inductors carry power
over a single pair ([MAG-DP83TD510E]_, [MAG-TDKSPE]_), and centre-tapped
windings carry Power over Ethernet in standard magnetics ([MAG-ENT98]_,
section 3.9). The combination at 1000 Mbit/s over 100 m of cable is
reported in one vendor test, without a choke ([MAG-ADIWIKI]_).

The active front end moves work onto evampire
---------------------------------------------

The active front end has the same structure, with three changes:

* on-chip common-mode feedback and termination replace the common-mode
  choke (:doc:`without-transformer`);
* active inductors, external high-voltage transistors controlled by
  evampire, replace the centre-tapped inductors;
* custom clamps on evampire take over part of the protection from the
  external diodes.

This front end needs fewer and smaller external parts. Each change is
shown in patents or papers (:doc:`without-transformer`), and is to be
confirmed by implementation. Coupling capacitors on the die, or a second
die on the cable side, are further options described on
:doc:`coupling-capacitors` and :doc:`isolation`.

The front ends set specifications for the circuits on evampire
--------------------------------------------------------------

:numref:`tbl-magnetics-specs` collects the specifications that these pages
set for the circuits on evampire. Values marked "estimate" are derived on
these pages. The requirements of the integrated transceiver as a whole are
on :doc:`../phy-electrical/index`.

.. list-table:: Specifications for the front-end circuits on evampire
   :name: tbl-magnetics-specs
   :header-rows: 1
   :widths: 28 44 28

   * - Circuit
     - Specification
     - Basis
   * - Line driver amplitude
     - 0.67 V to 0.82 V peak differential in the test pattern
     - :clause:`40.6.1.2.1`
   * - Line driver impedance
     - 100 Ω, within the return loss budget
     - :clause:`40.8.3.1`
   * - Signal at each pin
     - about ±0.4 V of transmit signal, plus the received signal, around
       the common-mode level
     - estimate
   * - Capacitance across each pair, chip side
     - at most about 12.8 pF, including pads, protection and traces
     - estimate, :doc:`gigabit-risk`
   * - Baseline-wander correction
     - tracks a high-pass time constant of 1.6 µs or more, for the far-end
       signal and the echo
     - estimate, :doc:`gigabit-risk`
   * - Receiver common-mode rejection
     - about 40 dB from 1 MHz to 250 MHz, together with any choke
     - estimate, :doc:`gigabit-risk`
   * - Common-mode feedback bandwidth
     - up to 250 MHz if it replaces the choke
     - :clause:`40.6.1.3.3` test range
   * - Pin protection
     - 2 kV human-body model or more, plus the charge passed by the
       capacitors
     - [MAG-GFIO]_, :doc:`without-transformer`
   * - Active inductor control
     - 80 µH or more across the pair, about 0.5 A per wire
     - :doc:`without-transformer`

For 10BASE-T the line driver also reaches 2.2 V to 2.8 V peak
(:clause:`14.3.1.2.1`), about ±1.4 V at each pin.

Which IEEE 802.3 requirements a transformer-free port meets
-----------------------------------------------------------

:numref:`tbl-magnetics-ieee` lists the IEEE 802.3 requirements that a
transformer helps meet, and where the passive front end stands on
each. The "Status" column uses three values: "met" where the analysis on
these pages shows a way, "conditional" where it depends on parts or
choices, and "open" where only a measurement answers it.

.. list-table:: IEEE 802.3 requirements for a port with the passive front
                end
   :name: tbl-magnetics-ieee
   :header-rows: 1
   :widths: 32 18 50

   * - Requirement
     - Status
     - How
   * - Isolation, direct-voltage test
     - conditional
     - Capacitors that withstand 2250 V, and an isolated power path
       (:doc:`isolation`).
   * - Isolation, alternating-voltage test
     - conditional
     - The tester must supply 38 mA to 377 mA of capacitive current
       (:doc:`isolation`).
   * - Isolation, impulse test
     - conditional
     - Capacitors and clamps that hold 2400 V, or 1500 V with Power over
       Ethernet.
   * - Return loss
     - met
     - At least 9.9 nF per wire, and at most about 12.8 pF across each pair
       on the chip side.
   * - Droop
     - met
     - At least 16 nF per wire, and 80 µH across the pair for any inductor.
   * - Impedance balance
     - open
     - Set by the matching of the capacitors and the chip-side circuits.
   * - Common-mode noise rejection
     - open
     - About 40 dB in the receiver and any choke; to be measured.
   * - Operation over a 100 m link
     - open
     - Reported in one vendor test; see :doc:`gigabit-risk`.
   * - Power over Ethernet signature
     - conditional
     - The coupling capacitors' capacitance fits in the 50 nF to 120 nF
       window.
   * - Radio-emission limits
     - open
     - To be measured; a common-mode choke reduces the risk.

The signals on the cable are the same as those of a port with magnetics,
so a transformer-free port works with standard link partners as far as the
open rows allow. :doc:`gigabit-risk` describes the measurements that close
them.

Open questions
--------------

* How will the port be tested against IEEE 802.3 where the standard is
  written for a transformer, for example the 350 µH inductance of
  100BASE-TX?
* Does the impedance balance of :clause:`40.8.3.2` hold with coupling
  capacitors of ordinary tolerance?
