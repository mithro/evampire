Two dual-role ports decide who supplies power
=============================================

How a dual-role port finds the other end and settles on a power role.

Attach for a dual-role port
---------------------------

The :ref:`Type-C specification <usb-type-c-specification>` describes attach
as a state machine for each kind of port (:typec:`Section 4.5.2.2`). A source
sees each CC pin as *SRC.Open*, *SRC.Rd* or *SRC.Ra*; a sink sees each CC pin
as *SNK.Rp* or *SNK.Open* (:typec:`Type-C Tables 4-16 <x>` and
:typec:`4-17 <x>`).

Toggling between Rp and Rd
~~~~~~~~~~~~~~~~~~~~~~~~~~

When nothing is attached, a dual-role port alternates between presenting Rd
on both CC pins (state Unattached.SNK) and presenting Rp on both CC pins
(Unattached.SRC), so that it can be found by a source, by a sink, or by
another dual-role port (:typec:`Section 4.5.1.3.3`; :numref:`fig-usbpd-toggle`
and :numref:`tab-usbpd-toggle`).

.. list-table:: Toggling timing (:typec:`Table 4-33`)
   :name: tab-usbpd-toggle
   :header-rows: 1
   :widths: 25 20 55

   * - Name
     - Value
     - Meaning
   * - tDRP
     - 50 ms to 100 ms
     - Period of one complete Rp and Rd cycle.
   * - dcSRC.DRP
     - 30 % to 70 %
     - Fraction of tDRP spent presenting Rp.
   * - tDRPTransition
     - at most 1 ms
     - Time allowed to change between Rp and Rd.

The clock that sets these times should *not* come from a precise source such
as a crystal, so that two dual-role ports do not stay locked in step and fail
to find each other (:typec:`Section 4.11.2`, text before
:typec:`Table 4-33 <x>`). In software this means adding a random variation
to the period and duty cycle.

.. wavedrom::
   :caption: Toggling while unattached, shown with a 50 % duty cycle. One
             period tDRP is 50 ms to 100 ms; Rp is presented for
             dcSRC.DRP × tDRP of it.
   :name: fig-usbpd-toggle
   :alt: Timing diagram: both CC pins alternate between Rp and Rd; one Rp
         phase plus one Rd phase make one period tDRP.

   {"signal": [
     {"name": "CC1, CC2", "wave": "=...=...=...", "data": ["Rp", "Rd", "Rp"]},
     {"name": "Rp time", "wave": "=...x.......", "data": ["dcSRC.DRP × tDRP"]},
     {"name": "period", "wave": "=.......x...", "data": ["tDRP"]}
   ],
   "config": {"hscale": 1.2}}

How long a connection takes to be noticed depends on who toggles: at most
*tNoToggleConnect* (5 ms) when neither side toggles, *tOnePortToggleConnect*
(80 ms) when one side toggles, and *tTwoPortToggleConnect* (510 ms) when both
do (:typec:`Table 4-34`).

The attach sequence
~~~~~~~~~~~~~~~~~~~

:numref:`fig-usbpd-drp-states` summarises the states described below.

.. _fig-usbpd-drp-states:

.. graphviz:: drp-states.dot
   :caption: Simplified attach state machine for a dual-role port that
             prefers the source role (:typec:`Section 4.5.2.2`,
             :typec:`Figure 4-16 <x>`). Accessory and debug states, and
             detach transitions back to the unattached states, are left out.
             "Stable" means unchanged for tCCDebounce (100 ms to 200 ms).
   :align: center

**Attaching to a source** (for example a charger). While presenting Rd, the
port sees Rp on one CC pin and enters AttachWait.SNK. When that pin has shown
Rp for *tCCDebounce* (100 ms to 200 ms, :typec:`Table 4-34`) and VBUS is
present, the port enters Attached.SNK, or Try.SRC if it prefers to be source
(see `Try.SRC and Try.SNK`_). The source meanwhile has debounced the Rd it
sees and turned VBUS on within *tVBUSON*, at most 275 ms
(:typec:`Table 4-32`; :typec:`Sections 4.5.2.2.4 <x>` and
:typec:`4.5.2.2.5 <x>`).

**Attaching to a sink** (for example a phone). While presenting Rp, the port
sees Rd on one CC pin and enters AttachWait.SRC. It makes sure VBUS is at
*vSafe0V* (at most 0.8 V, :pd:`Table 4.9`), loading VBUS if needed to
discharge it within *tVsafe0V* (650 ms, :typec:`Table 4-32`), waits until
exactly one CC pin has shown Rd for tCCDebounce, enters Attached.SRC and
turns VBUS on within tVBUSON (:typec:`Type-C Sections 4.5.2.2.8 <x>` and
:typec:`4.5.2.2.9 <x>`).

**Attaching to another dual-role port.** Both sides toggle; whichever happens
to present Rp when the other presents Rd becomes the source. The outcome is
random unless one side uses a preference mechanism
(:typec:`Section 4.5.2.2.7.2`, note).

**Detach.** A source detects that the sink has gone when the monitored CC pin
reads SRC.Open, within *tSRCDisconnect* (20 ms, :typec:`Table 4-34`), and
must then remove VBUS within *tVBUSOFF* (650 ms, :typec:`Table 4-32`). A sink
detects detach when VBUS falls below *vSinkDisconnect* (3.67 V at 5 V,
:typec:`Table 4-3`) within *tSinkDisconnect* (40 ms, same table).

Try.SRC and Try.SNK
~~~~~~~~~~~~~~~~~~~

A dual-role port can bias the outcome with one of two optional mechanisms;
only one may be enabled at a time (:typec:`Type-C Sections 4.5.1.4.1 <x>`,
:typec:`4.5.2.2.10 <x>` to :typec:`4.5.2.2.13 <x>`):

* **Try.SRC** (prefers to be source). When the port finds itself heading for
  Attached.SNK, it presents Rp instead (state Try.SRC) for up to *tDRPTry*
  (75 ms to 150 ms, :typec:`Table 4-33`). If the other side shows Rd for
  *tTryCCDebounce* (10 ms to 20 ms, :typec:`Table 4-34`), it becomes source;
  otherwise it goes back to presenting Rd (TryWait.SNK) and attaches as sink.
* **Try.SNK** (prefers to be sink). The mirror image: when heading for
  Attached.SRC it presents Rd for tDRPTry and waits for Rp.

These mechanisms work only once, at attach. After that, both sides can use
USB Power Delivery messages to swap roles (see `Role changes`_).
:typec:`Table 4-12` recommends Try.SRC for a port that prefers to be a source
and Try.SNK for one that prefers to be a sink.

Choosing the initial role
~~~~~~~~~~~~~~~~~~~~~~~~~

For evampire the preferred role follows from the
:ref:`power budget <power-budget>` and the :ref:`operating mode
<power-modes>`:

* If the board has input power from Ethernet and can spare power for USB, the
  port prefers to be a source and uses Try.SRC.
* If the board has no other input, it can only be a sink.
* If the board has input power but no spare power, it prefers to be a sink
  (Try.SNK), or attaches as a source offering no power and then asks for a
  role swap.

Even with Try.SRC, a port attached to a charger (which can only be a source)
ends up as a sink, and a port attached to a phone that only sinks ends up as
a source, so the processor has to handle both outcomes.

Unpowered board ("dead battery")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A board that has no power from Ethernet and is plugged into a USB charger is
completely unpowered at that moment. The charger turns VBUS on only after it
sees Rd. The port must therefore present Rd without any supply
(:typec:`Section 4.5.2.2.3`: "A port with a dead battery shall enter this
state while unpowered"; :typec:`Section 4.8.5 <x>`). This is a
:ref:`requirement <requirements>` for evampire, because in the "USB in,
Ethernet out" mode the board takes all of its power from USB Type-C. Once the board has powered up
from VBUS, the processor takes over the CC pins, keeping Rd present, and
continues as a sink in Attached.SNK.

ErrorRecovery
~~~~~~~~~~~~~

Every port that supports USB Power Delivery must support the *ErrorRecovery*
state, in which it removes all terminations and presents at least *zOPEN*
(126 kΩ) on both CC pins for *tErrorRecovery* (at least 25 ms, or 240 ms if
it was supplying VCONN), forcing the other side to see a detach
(:typec:`Type-C Section 4.5.2.2.2 <x>`, :typec:`Tables 4-30 <x>` and
:typec:`4-34 <x>`). A port enters it from any state when its policy directs
it to, for example after a failed power role swap, and afterwards returns to
Unattached.SNK. The Rp and Rd circuits must therefore both be switchable off.
