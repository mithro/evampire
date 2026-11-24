.. _ebat-boards:

Boards built around ebat
========================

This page lists the kinds of board that ebat suits, describes how a board
with no data path connects to the Ethernet cable, and describes boards that
pass Ethernet data from one socket to another on wiring that bypasses ebat.

Each board fits only the ports it needs
---------------------------------------

ebat has the power ports of evampire (:ref:`req-ebat-same-power`), and a board
fits the ones its job needs. :numref:`tab-ebat-boards` lists four kinds of
board. The operating modes are described on :ref:`power-modes`.

.. list-table:: Kinds of board built around ebat
   :name: tab-ebat-boards
   :header-rows: 1
   :widths: 28 15 15 17 25

   * - Board
     - Port A
     - Port B
     - USB Type-C ports
     - Operating modes
   * - Ethernet to USB adapter
     - Yes
     - No
     - 1
     - Ethernet in, USB out
   * - USB-powered injector
     - No
     - Yes
     - 1
     - USB in, Ethernet out
   * - Ethernet pass-through
     - Yes
     - Yes
     - 0
     - Ethernet in, Ethernet out
   * - All ports
     - Yes
     - Yes
     - 1 or 2
     - All three

An :term:`injector` is power sourcing equipment placed in the cable
between an Ethernet switch and the device it serves
(:doc:`../power/poe/basics`). A
USB-powered injector needs a data path past ebat, as described below,
because ebat does not carry the data itself.

Without data, the cable needs no magnetics
------------------------------------------

On an evampire board the :term:`magnetics` pass the data to the
transceiver and keep the direct voltage away from it, while the power
enters and leaves at the :term:`centre taps <centre tap>`
(:doc:`../ethernet/magnetics/poe`). A board with no data path has no
transceiver to protect. The two wires of each pair can be joined and taken
to the polarity bridges of the powered-device front end, or to the power
sourcing switch.

The power limits do not change. The front end still shows a detection
signature within the resistance, capacitance and inductance limits of
:numref:`tbl-magnetics-poe-numbers`. Joining the two wires of a pair puts
a short circuit across that pair for any data that a switch at the far end
sends.

Whether the wires are joined directly, or through a part on each
wire that keeps the pair's impedance high at data frequencies, is an open
question. A third choice is to keep standard magnetics, or an RJ45 socket
with magnetics built in, and use only their centre taps. That costs the
magnetics but presents each pair to the far end as on any Ethernet port.

The cable still needs isolation
-------------------------------

IEEE 802.3 requires isolation between the cable conductors and every
accessible conductor, such as a USB Type-C connector (:clause:`145.4.1`).
:doc:`../power/poe/isolation` gives the test voltages, the two isolation
environments and the three routes to a barrier, and all of it applies to
ebat. Without a data path, only the power and ebat's control and status
signals cross the barrier.

.. _ebat-pass-through:

A board can pass data through on its own wiring
-----------------------------------------------

A board can pass Ethernet data between two RJ45 sockets while ebat handles
only the power. :numref:`fig-ebat-pass-through` shows an Ethernet
pass-through board of this kind: power arrives on port A and leaves on port
B, and the data pairs run from one socket to the other.

.. graphviz:: pass-through.dot
   :name: fig-ebat-pass-through
   :caption: An Ethernet pass-through board on which the data, including
             LLDP frames, passes between the two cables without reaching
             ebat.
   :alt: Block diagram. Upstream power sourcing equipment connects by
         cable to port A, an RJ45 socket and magnetics. The data pairs run
         from the magnetics of port A to the magnetics of port B, labelled
         as including LLDP frames. Port B connects by cable to a downstream
         powered device. The centre taps of port A feed the powered-device
         front end. The power sourcing switch feeds the centre taps of
         port B. ebat exchanges class and status with the powered-device
         front end, and detection and class with the power sourcing switch.
         ebat is not on the data path.
   :align: center

Each cable carries its own direct voltage. The data path must therefore
pass the data and block direct current between the two cables. Two sets of
magnetics joined on their circuit sides do this, as in
:numref:`fig-ebat-pass-through`. Coupling capacitors are the alternative
that :doc:`../ethernet/magnetics/coupling-capacitors` analyses. The power
path between the two front ends is the one of :numref:`fig-power-flow`.

A USB-powered injector has the same data path, with an unpowered RJ45
socket for the switch in place of port A. IEEE 802.3 calls such equipment
a :term:`midspan` power sourcing equipment. It defines which Ethernet
speeds a midspan must pass (:clause:`145.2.3`), and sets limits on the
insertion loss, crosstalk and return loss that the midspan adds to the
data path (:clause:`145.4.9`). The pass-through board of
:numref:`fig-ebat-pass-through` sits in the middle of the link in the same
way, so the same limits are the reference for its data path.

.. _ebat-pass-through-lldp:

LLDP frames then pass between the far ends
------------------------------------------

evampire stops LLDP frames at its processor, so that each power exchange
stays on its own cable (:ref:`req-forwarding`, :doc:`../power/poe/lldp`).
On an ebat board with data pass-through, LLDP frames pass from one cable to
the other like any other frame. The downstream powered device and the
upstream equipment can then exchange power values with each other, past
ebat:

* After an LLDP exchange, a powered device's assigned class follows the
  value agreed in it (:clause:`145.3.6`). A downstream powered device can
  take a value agreed with the upstream equipment as its own allocation.
  If that value is higher than the class port B assigned, the device can
  draw more than port B allows.
* Power sourcing equipment may adjust its power allocation through LLDP
  (:clause:`145.2.8`), and may lower it at any time
  (:doc:`../power/poe/lldp`). Upstream power sourcing equipment can lower
  its allocation on the cable to port A to a value agreed with the
  downstream device, below what ebat draws.

In the first case, port B's built-in current and power limit
(:ref:`req-power-control`) switches the port off when the downstream
device draws too much. Port B then detects and classifies the device
again, the device can agree the same value over LLDP again, and the cycle
can repeat. The frames do not pass through ebat, so ebat cannot
prevent the second case.

In a USB-powered injector, the data side connects to a switch instead of
power sourcing equipment. If that switch answers the power exchange over
LLDP, the first case applies in the same way. Power negotiation
carried in other kinds of frame passes through in the same way as LLDP.

Open questions
--------------

* Whether the two wires of each pair are joined directly on a board with no
  data path.
* Whether ebat boards pass Ethernet data through, and if so how they deal
  with the LLDP frames that pass between the far ends. Offering only
  classes 1 to 3 on port B does not remove the problem, because LLDP is
  optional for those classes, not forbidden (:numref:`tab-ebat-lldp-needed`).
* Which Ethernet speeds a pass-through board supports, which sets the
  midspan variant it meets (:clause:`145.2.3`).
