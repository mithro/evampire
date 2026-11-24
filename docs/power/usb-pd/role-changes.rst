.. _usbpd-role-changes:

Changing roles while connected
==============================

How two connected USB Type-C ports exchange the power role, the data role
and the VCONN supply without unplugging, and how a Hard Reset returns both
to their starting state.

Each swap changes one thing
---------------------------

When a cable is plugged in, the port that ends up with :term:`Rp` is the
:term:`source`, supplies :term:`VCONN` and is the USB host side; the port
with :term:`Rd` is the :term:`sink` and the device side
(:typec:`Section 4.5.1.4.1`). Afterwards three :term:`USB Power Delivery`
message exchanges can each change one of these roles
(:numref:`tab-usbpd-swaps`).

.. list-table:: What each swap changes (:typec:`Table 4-13`)
   :name: tab-usbpd-swaps
   :header-rows: 1
   :widths: 25 25 25 25

   * - Role
     - PR_Swap
     - DR_Swap
     - VCONN_​Swap
   * - VBUS supply
     - Swapped
     - Kept
     - Kept
   * - Rp and Rd
     - Swapped
     - Kept
     - Kept
   * - Data role
     - Kept
     - Swapped
     - Kept
   * - VCONN
     - Kept
     - Kept
     - Swapped

Either port may ask for any of the three. The other port answers Accept,
Reject or Wait (:pd:`PD Sections 7.10 <x>`, :pd:`7.12.1 <x>` and
:pd:`7.13 <x>`). Wait means "ask again later". A port in EPR mode must leave
it before it may send PR_Swap (:pd:`Section 7.10`).

.. _usbpd-power-role-swap:

A power role swap exchanges source and sink
-------------------------------------------

In a power role swap, the source turns VBUS off and changes its Rp to Rd,
and the sink then changes its Rd to Rp and turns VBUS on.
:numref:`fig-usbpd-prswap` shows the sequence and
:numref:`tab-usbpd-prswap` its time limits. The sequence after Accept is the
same whichever port asked (:pd:`Section 4.3.3`).

.. graphviz:: pr-swap.dot
   :name: fig-usbpd-prswap
   :caption: Power role swap asked for by the initial sink
             (:pd:`Section 4.3.3`, :pd:`Figure 4.14 <x>`).
   :alt: Sequence diagram between the initial source and the initial sink.
         The initial sink sends PR_Swap; the initial source answers GoodCRC
         within 195 microseconds and Accept within 15 ms, which the sink
         acknowledges with GoodCRC. The sink cuts its current to 2.5 mA
         within 15 ms. After at least 25 ms the source takes VBUS to 0.8 V
         within 650 ms, changes Rp to Rd, and starts PS_RDY within 690 ms;
         the sink waits up to 750 to 920 ms for it. The sink answers GoodCRC,
         changes Rd to Rp, turns VBUS on to 5 V, and starts its own PS_RDY
         within 280 ms; the new sink waits up to 390 to 480 ms. The new sink
         answers GoodCRC, and at least 20 ms later the new source sends
         Source_Capabilities.
   :align: center

.. list-table:: Power role swap time limits (:pd:`PD Tables 4.7 <x>`,
   :pd:`4.8 <x>` and :pd:`7.10 <x>`)
   :name: tab-usbpd-prswap
   :header-rows: 1
   :widths: 30 13 13 44

   * - Name
     - Min (ms)
     - Max (ms)
     - Meaning
   * - tSnkSwapStdby
     - none
     - 15
     - Initial sink: time to cut its VBUS current
   * - tSrcTransition
     - 25
     - none
     - Initial source: wait before turning VBUS off
   * - tSrcSwapStdby
     - none
     - 650
     - Initial source: time to discharge VBUS to vSafe0V
   * - tSrcTransOff
     - none
     - 690
     - Initial source: from the GoodCRC for Accept to the start of its PS_RDY
   * - tPSSourceOff
     - 750
     - 920
     - Initial sink: gives up waiting for that PS_RDY
   * - tNewSrc
     - none
     - 275
     - Initial sink: time to start operating as a source
   * - tSrcTransOn
     - none
     - 280
     - New source: from the GoodCRC for the first PS_RDY to the start of its own PS_RDY
   * - tPSSourceOn
     - 390
     - 480
     - New sink: gives up waiting for that PS_RDY
   * - tSwapSourceStart
     - 20
     - none
     - New source: wait before it first sends its capabilities

Until the new source has VBUS up, the initial sink draws at most
*iSnkSwapStdby* (2.5 mA, :pd:`Table 4.8`). vSafe0V is at most
0.8 V (:pd:`Table 4.9`).

Every message is acknowledged with a :term:`GoodCRC` within *tTransmit*
(195 µs), and Accept follows PR_Swap within *tReceiverResponse* (15 ms)
(:pd:`Table 7.10`).

VBUS may fall and rise faster than the normal slew-rate limit during a swap
(:pd:`Section 4.1.4`). VBUS falls below 5 V, but the initial sink does not
treat this as a detach (:pd:`Section 7.10`). The USB data connection stays
up through the swap (:pd:`Section 4.3`).

The initial sink must run from something other than VBUS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From tSnkSwapStdby until the new source has VBUS up, the initial sink may
draw at most 2.5 mA. A board built around evampire can therefore swap from
sink to source only while it is powered from another input, such as
:term:`Power over Ethernet`. That input is also what it then supplies VBUS
from.

A swap that fails ends in ErrorRecovery
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the expected PS_RDY does not arrive within tPSSourceOff or tPSSourceOn,
the waiting port goes to the Type-C ErrorRecovery state
(:pd:`PD Sections 7.31.5.2 <x>` and :pd:`7.31.5.3 <x>`). It removes its
terminations, both ports see a detach, and attach starts again (see
:ref:`usbpd-error-recovery`). A board that was running from VBUS at that
moment loses its power.

The power budget changes direction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After a swap the board's input and output change places. The software
updates the :ref:`power budget <power-budget>`. When the board becomes the
source, it offers only what its new input allows (see
:ref:`usbpd-building-offer`).

.. _usbpd-data-roles:

Data roles and DR_Swap
----------------------

A USB connection has a host and a device. On USB Type-C, the port that is
the host for data is the *downstream facing port*, :term:`DFP <Data role>`,
and the port that is the device is the *upstream facing port*,
:term:`UFP <Data role>`. This is the port's *data role*, and it is separate
from its power role. A port that can take either data role is a
*dual-role-data* port (:typec:`Section 2.3.3`).

At attach the data role follows the CC resistor. The port with Rp, the
source, starts as DFP, and the port with Rd, the sink, starts as UFP
(:typec:`Section 4.5.1.4.1`). Every message a port sends carries its present
data role in the Port Data Role bit of the header. A port that receives a
message whose bit claims the same role as its own goes to ErrorRecovery
(:pd:`Table 6.2`). The software keeps this bit correct after every change.

A DR_Swap message exchange swaps DFP and UFP and nothing else: VBUS, the CC
resistors and VCONN stay as they are (:pd:`PD Sections 6.3.9 <x>` and
:pd:`7.12.1 <x>`; :typec:`Table 4-13 <x>`). Either port may send DR_Swap,
and the other answers Accept, Reject or Wait. The swap counts as a detach
and re-attach for any USB data connection between the two ports
(:pd:`Section 7.12.1`). A Hard Reset returns the data roles to DFP for the
port with Rp and UFP for the port with Rd (:pd:`Section 7.1.3`).

evampire's USB serial port works only as UFP, so a board that supplies power
as source may need DR_Swap to become UFP. :doc:`/usb-serial/usb-pd-roles`
describes when the serial port needs it and what the board does if the other
end refuses.

.. _usbpd-vconn-swap:

VCONN_Swap moves the VCONN Source
---------------------------------

The *VCONN Source* is the port that supplies VCONN to the cable plugs (see
:ref:`usbpd-vconn`). After attach it is the source. A power role swap does
not move VCONN: the port that was supplying it keeps supplying it, now as
the sink (:pd:`Section 7.10`; :typec:`Table 4-13 <x>`). A port that must
talk to a cable plug, for example to send :term:`Discover Identity`, first
becomes the VCONN Source, with a VCONN_Swap if needed (:pd:`Section 7.13`).

A VCONN_Swap keeps VCONN on throughout, so that a cable powered from VCONN
never loses power. This order is called
:wikipedia:`make-before-break <Make_before_break>`: the new supply
is connected before the old one is disconnected. The steps are
(:pd:`Section 7.13`; :pd:`Table 7.10 <x>`):

#. Either port sends VCONN_Swap. The other answers Accept, Reject, Wait or
   Not_Supported. The port that is supplying VCONN must not answer Reject.
#. After Accept, the new VCONN Source turns VCONN on and sends PS_RDY
   within *tVconnSourceOn* (50 ms).
#. The old VCONN Source turns VCONN off within *tVconnSourceOff* (25 ms) of
   the end of that PS_RDY. For those 25 ms both ports supply VCONN.

A port that cannot supply VCONN answers Reject or Not_Supported. If the
port that sent VCONN_Swap is not the VCONN Source and gets Not_Supported, it
may become the VCONN Source anyway until the next Hard Reset or detach
(:pd:`Section 7.13`). A port that has given up VCONN waits at least
*tVconnSwapDelayDFP* (100 ms) as DFP, or *tVconnSwapDelayUFP* (500 ms) as
UFP, before asking for it back (:pd:`Table 7.10`).

.. _usbpd-fast-role-swap:

A fast role swap keeps power flowing when the source loses its supply
---------------------------------------------------------------------

A :term:`fast role swap <Fast role swap>` (FRS) is a power role swap that
starts with a signal on the CC wire instead of an exchange of messages, so
that it completes within microseconds. It is made for *charge-through
accessories*: a hub that powers a laptop from a wall supply and itself
runs from the laptop when the wall supply is removed (:pd:`Section 10.1`).

The source signals by pulling CC low; the sink takes over VBUS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:numref:`fig-usbpd-frs` shows the signal and the hand-over of VBUS.

.. wavedrom::
   :caption: Fast role swap: the initial source pulls CC low and stops
             supplying VBUS, and the initial sink supplies VBUS within
             150 µs (:pd:`Figure 10.4`).
   :name: fig-usbpd-frs
   :alt: Timing diagram. The initial source loses its external supply,
         pulls CC low for 60 to 120 microseconds and stops supplying VBUS.
         The initial sink detects a low lasting 30 to 50 microseconds. VBUS
         falls, and within 150 microseconds of VBUS falling to vSafe5V the
         initial sink supplies VBUS at 5 V. After a gap, the FR_Swap,
         Accept, PS_RDY and PS_RDY messages follow on CC.

   {"signal": [
     {"name": "external supply", "wave": "1.0......|........"},
     {"name": "CC", "wave": "1.0..1...|=.=.=.=.", "node": "..A..B",
      "data": ["FR_Swap", "Accept", "PS_RDY", "PS_RDY"]},
     {"name": "low detected", "wave": "0...1....|........",
      "node": "....C"},
     {"name": "VBUS", "wave": "=.=....=.|........",
      "data": ["5 V", "falls", "5 V from new source"]},
     {"name": "initial source on", "wave": "1.0......|........"},
     {"name": "initial sink on", "wave": "0......1.|........",
      "node": "....D..E"}
   ],
   "edge": ["A<->B tFRSwapTx", "A<->C tFRSwapRx", "D<->E tSrcFRSwap"],
   "config": {"hscale": 1}}

The steps are (:pd:`PD Sections 10.4 <x>` and :pd:`10.4.1 <x>`;
:pd:`Table 10.2 <x>`):

#. On losing its external supply, the initial source pulls CC below
   *vFRSwapCableTx* (490 mV to 550 mV) through at most *rFRSwapTx* (5 Ω),
   for *tFRSwapTx* (60 µs to 120 µs). At the same moment it stops supplying
   VBUS and draws at most *iSnkStdby* (500 mA).
#. The initial sink treats a low lasting *tFRSwapRx* (30 µs to 50 µs) as
   the signal, stops drawing current, and supplies VBUS at 5 V within
   *tSrcFRSwap* (150 µs) of VBUS falling to vSafe5V.
#. The new source sends FR_Swap within *tFRSwapInit* (15 ms). Accept and a
   PS_RDY from each side follow, each within 15 ms.
#. After *tSnkFRSwap* (200 µs) the new sink may draw up to *iNewFrsSink*,
   the current it asked for in its Sink_Capabilities (Default USB, 1.5 A or
   3.0 A).

A low of 30 µs cannot be part of a message: no level of a
:term:`BMC <Biphase mark coding>` message lasts longer than one
:term:`unit interval <UI>` of about 3.7 µs (see :ref:`usbpd-bit-rate`).
During a contract the idle CC level is set by the 1.5 A or 3.0 A Rp, well
above vFRSwapCableTx (see :ref:`usbpd-cc-voltages`).

Fast role swap works only when the sink was prepared for it
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The initial sink responds to the signal only after it has an explicit
contract, has read the source's Sink_Capabilities, and found a fast role
swap current set in them. While prepared, it ignores VBUS-based detach
detection (:pd:`Section 10.2`). After the swap, the accessory must run at
5 V on 15 W or less (:pd:`Section 10.1`).

What fast role swap would need on evampire
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The case for evampire is a board that supplies a laptop from Power over
Ethernet and loses the Ethernet supply. With FRS the laptop could take over
and keep the board running. Without FRS, the board loses its power with the
Ethernet supply. The needs, from the limits above, are:

As the port that signals (initial source):
   a pull-down of at most 5 Ω on each CC pin, and detection of the loss of
   the Ethernet supply. The board also needs stored energy to run from the
   loss until the laptop supplies VBUS, up to 150 µs after VBUS reaches
   vSafe5V. Until tSnkFRSwap it may draw at most 500 mA from VBUS.
As the port that responds (initial sink):
   a CC comparator at 490 mV to 550 mV; a timer that measures a low of
   30 µs to 50 µs; and a source converter that delivers 5 V within 150 µs,
   which means it is already running.

For reference, the TPS65987D turns its VBUS path on within 150 µs for a
fast role swap and has a 5 Ω pull-down and a 490 mV to 550 mV detection
threshold ([USBPD-TPS65987D]_, Sections 6.7 and 6.8).

.. _usbpd-hard-reset:

A Hard Reset returns both power supplies to their defaults
----------------------------------------------------------

A :term:`Hard Reset` is a special signal, not a message, that either port
sends when communication has failed (:pd:`PD Sections 4.4 <x>` and
:pd:`7.1.3 <x>`). It is not acknowledged with GoodCRC. Both ports return
their power supplies to the default state. :numref:`fig-usbpd-hard-reset`
shows the sequence.

.. graphviz:: hard-reset.dot
   :name: fig-usbpd-hard-reset
   :caption: Hard Reset sequence (:pd:`Section 4.4.1`, :pd:`Figure 4.16 <x>`).
   :alt: Sequence diagram between the source and the sink. Either side
         sends Hard Reset, with no GoodCRC. The sink prepares within 15 ms.
         25 to 35 ms after the Hard Reset the source turns VBUS and VCONN
         off, reaching 0.8 V within 650 ms; the sink draws at most 1 mA and
         the source waits 0.66 to 1.0 s. The source then turns VBUS on, from
         0 V to 5 V within 275 ms, turns VCONN on from the Rp side within
         2 ms of 5 V, and sends Source_Capabilities within 250 ms of 5 V.
   :align: center

The limits are *tPSHardReset* (25 ms to 35 ms), *tSafe0V* (650 ms),
*tSrcRecover* (0.66 s to 1.0 s in SPR), *tSrcTurnOn* (275 ms),
*tSnkHardResetPrepare* (15 ms) and *iSafe0mA* (1 mA)
(:pd:`PD Tables 4.7 <x>`, :pd:`4.8 <x>`, :pd:`4.9 <x>` and
:pd:`7.10 <x>`). The source sends Source_Capabilities within
*tFirstSourceCap* (250 ms) of VBUS reaching 5 V (:pd:`Section 7.31.3.3`).

A Hard Reset does not change Rp and Rd, so the power roles after a power
role swap are kept. It returns the data roles to DFP for the Rp side and UFP
for the Rd side, and VCONN to the Rp side (:pd:`Section 7.1.3`). If a
Hard Reset, repeated up to *nHardResetCount* (2) times, does not clear the
fault, the port uses ErrorRecovery (:pd:`Section 7.1.3`;
:pd:`Table 7.12 <x>`).

What a Hard Reset does to the board depends on its role:

As source:
   the USB output is off for at least 0.66 s. A board powered from Ethernet
   keeps running.
As sink:
   VBUS goes to 0 V and back to 5 V. A board powered only from VBUS loses
   its power: for it, a Hard Reset is a full power cycle. A board that is
   to keep running as sink needs another input, or stored energy for up to
   about 2.0 s, the sum of the longest tPSHardReset, tSafe0V, tSrcRecover
   and tSrcTurnOn.

Open questions
--------------

* When the board asks for a power role swap or a data role swap, and when
  it accepts one, given the :ref:`power budget <power-budget>` and the USB
  serial port. :typec:`Table 4-14` gives the swaps the USB Type-C
  specification recommends for each preferred pair of roles.
* Whether the board signals fast role swap, responds to it, or neither.
  Signalling needs stored energy for the hand-over; responding needs a
  source converter kept running while the board is a sink.
