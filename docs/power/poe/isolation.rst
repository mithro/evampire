.. _poe-isolation:

Isolation from the cable
========================

This page gives the isolation that the standard requires between the cable
and the rest of the equipment, and sets out the three routes by which a
board built around evampire can provide it.

The standard requires isolation from accessible conductors
----------------------------------------------------------

Powered devices and power sourcing equipment must be isolated between all
the cable conductors and every accessible external conductor, including
frame ground (:clause:`145.4.1`, :clause:`33.4.1`). Accessibility follows
:std:`IEC 62368-1`. A connector that is not isolated from the cable
conductors, for example a USB Type-C connector sharing the board's ground,
must itself be isolated from the other accessible conductors.

The isolation must withstand one of three tests (Annex J of
:std:`IEEE 802.3 <802.3>`, as modified by :clause:`145.4.1`):

* 1500 V rms at 50 Hz to 60 Hz for 60 s;
* 2250 V DC for 60 s;
* ten 1500 V impulses of 10/700 µs shape, 60 s apart.

There must be no breakdown, and the insulation resistance afterwards must
be at least 2 MΩ at 500 V DC. Unlike a surge, this stress must be blocked;
a clamp across the barrier would fail the test (:doc:`hv-limits`).

The environment decides whether ports may share a ground
--------------------------------------------------------

The standard distinguishes two environments (:clause:`145.4.1.1`):

Environment A
   The network and all its equipment are within one low-voltage power
   distribution system and one building. Equipment with several ports needs
   isolation between each port and its protective ground, but not between
   the ports.
Environment B
   The network crosses separate power distribution systems or buildings.
   Each port must be isolated from every other port as well as from the
   protective ground.

In Environment A, ports A and B of one board may therefore share one
cable-side ground and supply. In Environment B they may not, and each
Ethernet port needs its own isolated domain. Which environment the board
targets is an open question.

The barrier can sit in two places
---------------------------------

Barrier between evampire and the cable
   evampire's ground is shared with the USB Type-C connectors and any other
   accessible conductor. Every circuit connected to the cable then sits
   across a barrier from evampire: an isolated input converter for power
   (:doc:`../converters/index`), and isolated links for the signals.

Barrier at the other connectors
   evampire's ground is on the cable side, and the isolation moves to the
   USB Type-C ports and any other accessible conductor. Cable-side
   functions can then share evampire's die. In Environment B this works for
   only one Ethernet port, because the two ports must be isolated from each
   other.

The first-version board's data already crosses the coupling transformers.
The full design has none, so the data path needs isolation too
(:doc:`../../ethernet/magnetics/index`).

Three routes provide the barrier
--------------------------------

External high-voltage parts
   High-voltage capacitors in the data path, an isolated converter for
   power, and digital isolators or
   :wikipedia:`opto-isolators <Opto-isolator>` for the status and control
   signals. This is the conventional route. The cable-side functions are
   then external parts, or a separate chip.

A second die on the cable side
   The cable-side functions, the powered-device blocks or the power
   sourcing channels, on a second die that sits on the cable side of the
   barrier. It can be a custom gf180mcu die, possibly the same design as
   evampire, or a commercial part. The two dies communicate across the
   barrier through isolated links, capacitive or magnetic, in the package or
   on the board.

A barrier on the evampire die
   Isolation capacitors built from the chip's own dielectrics, with both
   sides on one die. The substrate is shared silicon, so the cable-side
   circuits must also be isolated from the substrate, to the full test
   voltage. The magnetics pages analyse the dielectrics for the data path
   (:doc:`../../ethernet/magnetics/index`). The strongest dielectric in
   :numref:`tab-poe-gf180-ratings`, the 1 fF/µm² MIM capacitor, is rated
   for 20 V and breaks down at 20 V minimum, so a series stack would need
   more than :math:`1500\ \text{V} \times \sqrt{2} / 20\ \text{V} = 106`
   such capacitors for the peak of the 1500 V rms test, before any margin. Whether thicker inter-metal
   dielectrics reach the test voltage needs test structures.

Which route is used is an open question for each function
(:doc:`hv-options`, :ref:`requirements-open-questions`).

Open questions
--------------

* Which isolation environment, A or B, the board targets.
* Where the barrier sits, and which of the three routes provides it.
* The breakdown of gf180mcu inter-metal dielectrics, which decides whether
  a barrier on the evampire die can reach the test voltages.
