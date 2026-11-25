.. _usbpd-attach:

Attach and detach
=================

How a :term:`dual-role port` finds the device at the other end of a USB
Type-C cable, settles on the source or sink role, and starts again after an
error.

The :std:`USB Type-C specification <usb-type-c>` describes attach as a
:wikipedia:`finite-state machine <Finite-state_machine>` for each kind of
port (:typec:`Section 4.5.2.2`). This page follows the one for a dual-role
port. The states depend on what each CC pin sees: SRC.Rd, SRC.Ra or SRC.Open
while the port presents :term:`Rp`, and SNK.Rp or SNK.Open while it presents
:term:`Rd` (:ref:`usbpd-cc-states`).

.. _usbpd-toggling:

Toggling between Rp and Rd
--------------------------

When nothing is attached, a dual-role port alternates between presenting Rd
on both CC pins (state Unattached.SNK) and presenting Rp on both CC pins
(state Unattached.SRC). A source finds it while it presents Rd, and a sink
finds it while it presents Rp (:typec:`Section 4.5.1.3.3`;
:numref:`fig-usbpd-toggle`). One Rp and Rd cycle takes tDRP, Rp is
presented for the share dcSRC.DRP of it, and each change between Rp and Rd
takes at most tDRPTransition (:numref:`tab-usbpd-toggle`).

.. list-table:: Toggling limits (:typec:`Table 4-33`)
   :name: tab-usbpd-toggle
   :header-rows: 1
   :widths: 40 20 20 20

   * - Name
     - Min
     - Max
     - Unit
   * - tDRP
     - 50
     - 100
     - ms
   * - dcSRC.DRP
     - 30
     - 70
     - %
   * - tDRPTransition
     - 0
     - 1
     - ms

.. wavedrom::
   :caption: Toggling while unattached, drawn with a 50 % duty cycle.
   :name: fig-usbpd-toggle
   :alt: Timing diagram: both CC pins alternate between Rp and Rd. Rp is
         presented for dcSRC.DRP × tDRP, and one Rp phase plus one Rd phase
         make one period tDRP.

   {"signal": [
     {"name": "CC1, CC2", "wave": "=...=...=...", "data": ["Rp", "Rd", "Rp"]},
     {"name": "Rp time", "wave": "=...x.......", "data": ["dcSRC.DRP × tDRP"]},
     {"name": "period", "wave": "=.......x...", "data": ["tDRP"]}
   ],
   "config": {"hscale": 1.2}}

The specification recommends that the timer for tDRP and the
:wikipedia:`duty cycle <Duty_cycle>` dcSRC.DRP do not come from a precise
source such as a :wikipedia:`crystal <Crystal_oscillator>`
(:typec:`Section 4.11.2`). Two dual-role ports with the same precise period
could stay in step, each presenting Rp while the other does, and never find
each other. In software, a random variation of the period and duty cycle
within the limits gives the same protection.

The time to notice a connection depends on how many of the two ends toggle
(:numref:`tab-usbpd-connect-times`).

.. list-table:: Longest time to detect a connection (:typec:`Table 4-34`)
   :name: tab-usbpd-connect-times
   :header-rows: 1
   :widths: 40 30 30

   * - Ends that toggle
     - Name
     - Maximum (ms)
   * - Neither
     - tNoToggleConnect
     - 5
   * - One
     - tOnePortToggleConnect
     - 80
   * - Both
     - tTwoPortToggleConnect
     - 510

.. _usbpd-attach-sequence:

Attach sequence
---------------

:numref:`fig-usbpd-drp-states` shows the states a dual-role port passes
through. It leaves out the accessory and debug states and the return to the
unattached states on detach. The timing limits are in
:numref:`tab-usbpd-attach-timing`.

.. graphviz:: drp-states.dot
   :name: fig-usbpd-drp-states
   :caption: Attach states of a dual-role port that prefers the source role
             (:typec:`Section 4.5.2.2`, :typec:`Figure 4-16`).
   :alt: State diagram. Unattached.SNK and Unattached.SRC toggle between
         each other. Unattached.SNK goes to AttachWait.SNK when Rp is seen;
         Unattached.SRC goes to AttachWait.SRC when Rd is seen.
         AttachWait.SNK goes to Attached.SNK when Rp is stable and VBUS is on,
         or to Try.SRC if the port prefers the source role. AttachWait.SRC
         goes to Attached.SRC when Rd is stable and VBUS is at 0 V. Try.SRC
         goes to Attached.SRC if Rd is seen, otherwise to TryWait.SNK, which
         goes to Attached.SNK when VBUS is on. Attached.SNK and Attached.SRC
         are linked by PR_Swap. Any state can be directed to ErrorRecovery,
         which returns to Unattached.SRC after tErrorRecovery.
   :align: center

.. list-table:: Attach and detach time limits
   :name: tab-usbpd-attach-timing
   :header-rows: 1
   :widths: 30 15 15 40

   * - Name
     - Min (ms)
     - Max (ms)
     - Meaning
   * - tCCDebounce
     - 100
     - 200
     - Time a CC state must be stable before attach (:typec:`Table 4-34`)
   * - tVBUSON
     - 0
     - 275
     - From Attached.SRC to VBUS at vSafe5V (:typec:`Table 4-32`)
   * - tVsafe0V
     - 0
     - 650
     - Time to discharge VBUS in AttachWait.SRC (:typec:`Table 4-32`)
   * - tSRCDisconnect
     - 0
     - 20
     - Time for a source to see the sink leave (:typec:`Table 4-34`)
   * - tVBUSOFF
     - 0
     - 650
     - From detach to VBUS at vSafe0V (:typec:`Table 4-32`)
   * - tSinkDisconnect
     - none
     - 40
     - Time for a sink to see VBUS fall (:typec:`Table 4-3`)

VBUS counts as off at vSafe0V, 0 V to 0.8 V (:pd:`Table 4.9`). A sink
attached at 5 V counts VBUS as gone below vSinkDisconnect, at most 3.67 V
(:typec:`Table 4-3`).

Attaching to a source
^^^^^^^^^^^^^^^^^^^^^

A source such as a charger finds the port while it presents Rd
(:typec:`Section 4.5.2.2.4`, :typec:`Section 4.5.2.2.5`):

#. The port sees SNK.Rp on one CC pin and enters AttachWait.SNK, keeping Rd
   on both pins.
#. The source sees Rd for tCCDebounce, enters Attached.SRC and turns VBUS
   on within tVBUSON.
#. The port waits until exactly one CC pin has shown SNK.Rp for
   tCCDebounce and VBUS is present. It then enters Attached.SNK, or Try.SRC
   if it prefers the source role (:ref:`usbpd-try`).

The CC pin that shows SNK.Rp is the one that meets the CC wire.
:numref:`fig-usbpd-attach-to-source` shows the sequence in time.

.. wavedrom::
   :caption: evampire attaching as the sink to a charger, schematic and not
            to scale; tCCDebounce is 100 ms to 200 ms and tVBUSON at most
            275 ms.
   :name: fig-usbpd-attach-to-source
   :alt: Timing diagram. The charger presents Rp and evampire presents Rd
         throughout. The charger goes from Unattached.SRC to AttachWait.SRC,
         waits tCCDebounce of 100 to 200 ms, enters Attached.SRC and turns
         VBUS on within tVBUSON, at most 275 ms. evampire goes from
         Unattached.SNK to AttachWait.SNK and enters Attached.SNK once VBUS
         is present.

   {"signal": [
     {"name": "charger CC", "wave": "=.............", "data": ["Rp"]},
     {"name": "charger state", "wave": "=...=...=.....", "data": ["Unattached.SRC", "AttachWait.SRC", "Attached.SRC"]},
     {"name": "charger timer", "wave": "x...=...=..x..", "data": ["tCCDebounce", "tVBUSON"]},
     {"name": "VBUS", "wave": "0..........1.."},
     {"name": "evampire CC", "wave": "=.............", "data": ["Rd"]},
     {"name": "evampire state", "wave": "=...=......=..", "data": ["Unattached.SNK", "AttachWait.SNK", "Attached.SNK"]}
   ],
   "config": {"hscale": 1}}

Attaching to a sink
^^^^^^^^^^^^^^^^^^^

A sink such as a phone finds the port while it presents Rp
(:typec:`Section 4.5.2.2.8`, :typec:`Section 4.5.2.2.9`):

#. The port sees SRC.Rd on one CC pin and enters AttachWait.SRC.
#. It makes sure VBUS is at vSafe0V, loading VBUS to discharge it within
   tVsafe0V if a voltage is left on it.
#. It waits until exactly one CC pin has shown SRC.Rd for tCCDebounce, and
   enters Attached.SRC.
#. It turns VBUS on within tVBUSON.

:numref:`fig-usbpd-attach-to-sink` shows the sequence in time.

.. wavedrom::
   :caption: evampire attaching as the source to a phone, schematic and not
            to scale; tVsafe0V is at most 650 ms, tCCDebounce 100 ms to
            200 ms and tVBUSON at most 275 ms.
   :name: fig-usbpd-attach-to-sink
   :alt: Timing diagram. evampire presents Rp and the phone presents Rd.
         evampire goes from Unattached.SRC to AttachWait.SRC, where it
         discharges any voltage left on VBUS to vSafe0V within tVsafe0V, at
         most 650 ms, and waits tCCDebounce, 100 to 200 ms. It then enters
         Attached.SRC and turns VBUS on within tVBUSON, at most 275 ms. The
         phone enters Attached.SNK once VBUS is present.

   {"signal": [
     {"name": "evampire CC", "wave": "=..............", "data": ["Rp"]},
     {"name": "evampire", "wave": "=...=.....=....", "data": ["Unattached.SRC", "AttachWait.SRC", "Attached.SRC"]},
     {"name": "discharge", "wave": "x...=..x.......", "data": ["tVsafe0V"]},
     {"name": "debounce", "wave": "x...=....=..x..", "data": ["tCCDebounce", "tVBUSON"]},
     {"name": "VBUS", "wave": "=......0....1..", "data": ["left over"]},
     {"name": "phone CC", "wave": "=..............", "data": ["Rd"]},
     {"name": "phone", "wave": "=...=.......=..", "data": ["Unattached.SNK", "AttachWait.SNK", "Attached.SNK"]}
   ],
   "config": {"hscale": 1}}

Attaching to another dual-role port
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When both ends toggle, the end that happens to present Rp while the other
presents Rd becomes the source. Without a preference mechanism, the outcome
is random (:typec:`Section 4.5.2.2.7.2`; :typec:`Section 2.3.3`).
:numref:`fig-usbpd-drp-meet` shows two toggling ports meeting.

.. wavedrom::
   :caption: Two toggling dual-role ports meeting, schematic and not to
             scale: port A presents Rp while port B presents Rd, so A
             becomes the source.
   :name: fig-usbpd-drp-meet
   :alt: Timing diagram. Port A toggles Rp, Rd, Rp; port B presents Rp and
         then Rd. While both present Rp, or both Rd, neither sees the other.
         When A presents Rp and B presents Rd, A sees SRC.Rd and B sees
         SNK.Rp, and both stop toggling: A goes on as the source and B as
         the sink. Each toggle period tDRP is 50 to 100 ms, with Rp for 30 to
         70 % of it.

   {"signal": [
     {"name": "port A CC", "wave": "=.=.=........", "data": ["Rp", "Rd", "Rp, held"]},
     {"name": "port B CC", "wave": "=.=..........", "data": ["Rp", "Rd, held"]},
     {"name": "seen", "wave": "x...=........", "data": ["A sees SRC.Rd, B sees SNK.Rp: A is the source"]},
     {"name": "A period", "wave": "=...x........", "data": ["tDRP 50–100 ms"]}
   ],
   "config": {"hscale": 1}}

Detaching
^^^^^^^^^

A source detects that the sink has left when the CC pin it monitors reads
SRC.Open, within tSRCDisconnect. It then removes VBUS within tVBUSOFF
(:typec:`Section 4.5.2.2.9.2`). A dual-role port that prefers the source
role goes from Attached.SRC to TryWait.SNK rather than Unattached.SNK, so
that two ports that both prefer the source role do not swap back and forth
without end. A sink detects detach when VBUS falls below vSinkDisconnect,
within tSinkDisconnect (:typec:`Section 4.5.2.2.5.2`).
:numref:`fig-usbpd-detach` shows both cases.

.. wavedrom::
   :caption: Detach seen by evampire as the source and as the sink, schematic
            and not to scale; tSRCDisconnect is at most 20 ms, tVBUSOFF at
            most 650 ms and tSinkDisconnect at most 40 ms.
   :name: fig-usbpd-detach
   :alt: Timing diagram in two parts. As the source: the sink's Rd goes
         open; within tSRCDisconnect, at most 20 ms, evampire sees SRC.Open
         and leaves Attached.SRC; VBUS falls to vSafe0V, 0 to 0.8 V, within
         tVBUSOFF, at most 650 ms. As the sink: the charger's VBUS falls;
         once it is below vSinkDisconnect, at most 3.67 V, evampire leaves
         Attached.SNK within tSinkDisconnect, at most 40 ms.

   {"signal": [
     ["as source",
      {"name": "far-end CC", "wave": "=.=...........", "data": ["Rd", "open"]},
      {"name": "state", "wave": "=.....=.......", "data": ["Attached.SRC", "Unattached.SNK or TryWait.SNK"]},
      {"name": "detect", "wave": "x.=...x.......", "data": ["tSRCDisconnect"]},
      {"name": "VBUS off", "wave": "x.=......x....", "data": ["tVBUSOFF"]},
      {"name": "VBUS", "wave": "1........0...."}
     ],
     {},
     ["as sink",
      {"name": "VBUS", "wave": "1.=..=........", "data": ["falling", "below vSinkDisconnect"]},
      {"name": "detect", "wave": "x....=...x....", "data": ["tSinkDisconnect"]},
      {"name": "state", "wave": "=........=....", "data": ["Attached.SNK", "unattached"]}
     ]
   ],
   "config": {"hscale": 1}}

.. _usbpd-try:

Try.SRC and Try.SNK
-------------------

A dual-role port can bias the outcome with one of two optional mechanisms.
Only one of them may be enabled at a time (:typec:`Section 4.5.1.4.1`,
:typec:`Section 4.5.2.2.10`).

Try.SRC, for a port that prefers to be the source
   When the port is about to enter Attached.SNK, it presents Rp instead
   (state Try.SRC). If the other end shows Rd for tTryCCDebounce, the port
   becomes the source. If not, after tDRPTry it returns to presenting Rd
   (state TryWait.SNK) and attaches as the sink
   (:typec:`Section 4.5.2.2.10` and :typec:`4.5.2.2.11 <Section 4.5.2.2.11>`).
Try.SNK, for a port that prefers to be the sink
   When the port is about to enter Attached.SRC, it presents Rd instead
   (state Try.SNK). After tDRPTry it looks for Rp. If the other end shows Rp
   for tTryCCDebounce and VBUS appears, the port becomes the sink. If not,
   it returns to presenting Rp (state TryWait.SRC) and attaches as the
   source (:typec:`Section 4.5.2.2.12` and
   :typec:`4.5.2.2.13 <Section 4.5.2.2.13>`).

.. list-table:: Try.SRC and Try.SNK limits (:typec:`Table 4-33`, :typec:`Table 4-34`)
   :name: tab-usbpd-try-timing
   :header-rows: 1
   :widths: 30 20 20 30

   * - Name
     - Min (ms)
     - Max (ms)
     - Meaning
   * - tDRPTry
     - 75
     - 150
     - Wait in Try.SRC or Try.SNK
   * - tTryCCDebounce
     - 10
     - 20
     - Time the partner's termination must be stable
   * - tTryTimeout
     - 550
     - 1100
     - Longest time in Try.SRC

:numref:`tab-usbpd-try-timing` gives the limits, and
:numref:`fig-usbpd-try` shows each mechanism when it succeeds. Both
mechanisms act only during attach.

.. wavedrom::
   :caption: Try.SRC and Try.SNK when the partner, a dual-role port, gives
            way, schematic and not to scale; tDRPTry is 75 ms to 150 ms
            and tTryCCDebounce 10 ms to 20 ms.
   :name: fig-usbpd-try
   :alt: Timing diagram in two parts. Try.SRC: the port leaves
         AttachWait.SNK for Try.SRC and changes its CC from Rd to Rp; the
         partner changes from Rp to Rd; after Rd has been stable for
         tTryCCDebounce, 10 to 20 ms, the port enters Attached.SRC. Try.SNK:
         the port leaves AttachWait.SRC for Try.SNK and changes from Rp to
         Rd; the partner changes from Rd to Rp; after tDRPTry, 75 to 150 ms,
         the port looks for Rp, and after tTryCCDebounce with VBUS present
         it enters Attached.SNK.

   {"signal": [
     ["Try.SRC",
      {"name": "port state", "wave": "=...=....=....", "data": ["AttachWait.SNK", "Try.SRC", "Attached.SRC"]},
      {"name": "port CC", "wave": "=...=.........", "data": ["Rd", "Rp"]},
      {"name": "partner CC", "wave": "=....=........", "data": ["Rp", "Rd"]},
      {"name": "timer", "wave": "x....=...x....", "data": ["tTryCCDebounce"]}
     ],
     {},
     ["Try.SNK",
      {"name": "port state", "wave": "=...=......=..", "data": ["AttachWait.SRC", "Try.SNK", "Attached.SNK"]},
      {"name": "port CC", "wave": "=...=.........", "data": ["Rp", "Rd"]},
      {"name": "partner CC", "wave": "=....=........", "data": ["Rd", "Rp"]},
      {"name": "timer", "wave": "x...=..=...x..", "data": ["tDRPTry", "tTryCCDebounce"]},
      {"name": "VBUS", "wave": "0..........1.."}
     ]
   ],
   "config": {"hscale": 1}}

After attach, two ports that support
:term:`USB Power Delivery` can swap the power role with messages, a
:ref:`power role swap <usbpd-power-role-swap>`.

.. _usbpd-initial-role:

Preferred initial role
----------------------

evampire's preferred role on a port follows from the input power it has and
its :ref:`power budget <power-budget>`, as set out for each
:ref:`operating mode <power-modes>`:

* With input power from Ethernet and power to spare for USB, the port
  prefers the source role and uses Try.SRC.
* With no other input, the board can only be a sink
  (:ref:`usbpd-dead-battery`).
* With input power but none to spare, the port prefers the sink role and
  uses Try.SNK.

The other end limits the choice. A charger, which can only be a source,
leaves evampire as the sink even with Try.SRC. A phone that can only be a
sink leaves it as the source even with Try.SNK. The software therefore
handles both roles on every attach.

The options for setting the role, and their costs, are:

Try.SRC or Try.SNK, chosen from the budget at each attach
   Gives the preferred role against another dual-role port that has no
   preference. It adds up to tDRPTry to the attach.
No Try mechanism, then a power role swap
   The outcome against another dual-role port is random, and a
   :ref:`power role swap <usbpd-power-role-swap>` with USB Power Delivery
   messages corrects it afterwards. It needs no Try state, but VBUS is off
   for a short time during the swap.
A fixed role on each port
   A source-only or sink-only port is the simplest, but it does not meet the
   dual-role requirement of :ref:`req-power-bridging`.

The data role also enters the choice. The source starts as the host (DFP)
and the sink as the device (UFP) (:typec:`Section 2.3.3`). The USB serial
port works only as UFP, so as a source evampire swaps the data role
afterwards (:ref:`usbpd-data-roles`; :doc:`/usb-serial/usb-pd-roles`).
:typec:`Table 4-12` recommends Try.SNK for a port that prefers the source
role but the UFP data role. That recommendation matters most against a port
that cannot swap data roles (:typec:`Section 4.5.1.4.1`).

.. _usbpd-dead-battery:

Rd on an unpowered board
------------------------

A board with no power from Ethernet that is plugged into a USB charger has
no supply at that moment. The charger turns VBUS on only after it sees Rd
(:typec:`Section 2.3.1`). The port must therefore present Rd on both CC pins
without any supply. The specification requires this: "A port with a dead
battery shall enter this state while unpowered", the state being
Unattached.SNK (:typec:`Section 4.5.2.2.3`; :typec:`Section 4.8.5`). For
evampire it is a requirement in the "USB in, Ethernet out" mode, where the
board takes all its power from USB Type-C (:ref:`req-power-bridging`).

The unpowered Rd needs to pull the CC voltage only into the range of the
1.1 V voltage clamp, at most 1.32 V (:typec:`Section 4.8.5`,
:typec:`Table 4-28`). The specification's example is a 5.1 kΩ ± 20 %
resistor in series with a transistor whose gate is weakly pulled to CC. It
turns on from the source's own pull-up and can be switched off once the
board is powered. :ref:`usbpd-rd-circuit` describes evampire's circuit, and
:numref:`fig-usbpd-rd-paths` draws it.

Once the board has power from VBUS, the processor takes over the CC pins,
keeps Rd present and continues as a sink in Attached.SNK. :doc:`start-up`
gives the power the charger makes available until then. Two unpowered
boards connected to each other both present Rd, and neither supplies power,
as for any two sink-only ports (:typec:`Table 4-9`).

.. _usbpd-error-recovery:

ErrorRecovery
-------------

Every port that supports USB Power Delivery must support the ErrorRecovery
state, and must enter it from any state when its software directs it to
(:typec:`Section 4.5.2.2.2`). In ErrorRecovery the port:

* stops driving VBUS and :term:`VCONN`;
* presents at least zOPEN, 126 kΩ, to ground on both CC pins
  (:typec:`Table 4-30`);
* stays there for tErrorRecovery: at least 25 ms, or at least 240 ms if it
  was supplying VCONN (:typec:`Table 4-34`).

The other end sees a detach. Afterwards a dual-role port with Try.SRC
returns to Unattached.SRC, and any other dual-role port to Unattached.SNK
(:typec:`Section 4.5.2.2.2`). USB Power Delivery uses it when a power role
swap stalls, with no PS_RDY message within tPSSourceOn
(:pd:`Section 7.31.5.3`), and when a :term:`Hard Reset` does not clear an
error (:pd:`Section 7.1.3`). :numref:`fig-usbpd-error-recovery` shows the
sequence.

.. wavedrom::
   :caption: ErrorRecovery forcing a detach and a fresh attach, schematic and
             not to scale; tErrorRecovery is at least 240 ms instead of 25 ms
             if the port was supplying VCONN.
   :name: fig-usbpd-error-recovery
   :alt: Timing diagram. The port leaves its attached state for
         ErrorRecovery: it stops driving VBUS and VCONN and its CC pins go
         open, at least 126 kΩ. It stays there for tErrorRecovery, at least
         25 ms, or 240 ms if it was supplying VCONN, while the partner sees
         a detach. It then returns to Unattached.SRC or Unattached.SNK and
         attach starts again.

   {"signal": [
     {"name": "port state", "wave": "=..=....=.....", "data": ["attached", "ErrorRecovery", "Unattached.SRC or .SNK"]},
     {"name": "port CC", "wave": "=..=....=.....", "data": ["Rp or Rd", "open, ≥ 126 kΩ", "toggling"]},
     {"name": "VBUS, VCONN", "wave": "=..0..........", "data": ["as before"]},
     {"name": "timer", "wave": "x..=....x.....", "data": ["tErrorRecovery ≥ 25 ms"]},
     {"name": "partner", "wave": "=...=.........", "data": ["attached", "sees a detach"]}
   ],
   "config": {"hscale": 1}}

ErrorRecovery is why both the Rp and the Rd circuits must be able to turn
off completely, including the unpowered Rd once the board has power.

Open questions
--------------

* The role preference policy: when each port uses Try.SRC, Try.SNK or
  neither, and when it asks for a power role swap, given the power budget
  and the data role the USB serial port needs.
