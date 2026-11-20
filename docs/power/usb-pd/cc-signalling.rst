The signal on the configuration channel
=======================================

The electrical signal that carries USB Power Delivery messages.

Signalling on the CC wire
-------------------------

Every USB Power Delivery message is sent on the same CC wire that carries the
Rp/Rd voltage. Communication is half-duplex: only one side transmits at a
time (:pd:`Section 5.1`). Source and sink use exactly the same signalling.

Biphase mark coding
~~~~~~~~~~~~~~~~~~~

Bits are sent using *biphase mark coding* (BMC), a form of Manchester coding
(:pd:`Section 5.3.3`). The rules are:

* the line changes level at the start of every bit;
* for a ``1``, the line also changes level in the middle of the bit;
* for a ``0``, there is no change in the middle.

Only the presence or absence of the middle transition carries the data. A
receiver does not care which way round the signal is, and every bit has at
least one transition, which lets the receiver follow the transmitter's clock.
:numref:`fig-usbpd-bmc` shows an example.

.. wavedrom::
   :caption: Biphase mark coding: an edge at every bit boundary, and a
             second edge in the middle of each ``1``.
   :name: fig-usbpd-bmc
   :alt: Timing diagram of the bits 0 1 1 0 1 0 0 and the BMC line level,
         which changes at every bit boundary and also in the middle of each
         1 bit.

   {"signal": [
     {"name": "data bit", "wave": "=.=.=.=.=.=.=.",
      "data": ["0", "1", "1", "0", "1", "0", "0"]},
     {"name": "CC (BMC)", "wave": "0.10101.010.1."}
   ],
   "config": {"hscale": 1}}

A receiver measures the time between successive edges. An interval of about
one UI means a ``0``; two intervals of about half a UI in a row mean a ``1``.

Bit rate
~~~~~~~~

The bit rate *fBitRate* is 300 kbit/s nominal, within 270 kbit/s to
330 kbit/s (:pd:`Table 5.9`). Within one message the rate may differ by no more
than *pBitRate* = 0.25 % from the rate measured over the last 32 bits of the
preamble (:pd:`Section 5.3.4.8`, :pd:`Table 5.10 <x>`), so a receiver can measure the bit
time on the preamble and use it for the rest of the message.

The bit time (UI) sets every software timing on this page, so it is worth
calculating at the extremes (:numref:`tab-usbpd-ui`):

.. math::

   T_\text{UI} = \frac{1}{f_\text{bit}}

where :math:`T_\text{UI}` is the unit interval in seconds and
:math:`f_\text{bit}` is the bit rate in bit/s (:pd:`Table 5.9`).

.. list-table:: Unit interval at the bit-rate limits
   :name: tab-usbpd-ui
   :header-rows: 1
   :widths: 30 35 35

   * - Bit rate
     - UI
     - Half UI
   * - 330 kbit/s (fastest)
     - 1 / 330 000 = 3.030 µs
     - 1.515 µs
   * - 300 kbit/s (nominal)
     - 1 / 300 000 = 3.333 µs
     - 1.667 µs
   * - 270 kbit/s (slowest)
     - 1 / 270 000 = 3.704 µs
     - 1.852 µs

The shortest time between two edges is half a UI at the fastest rate,
1.515 µs. Any receiver, in hardware or software, must be able to measure
intervals this short.

Transmitter levels, output impedance and edge rate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The transmitter is a tri-state driver: it drives the CC wire between 0 V and
*vSwing* while sending and lets go of the wire (high impedance) at all other
times (:pd:`Section 5.3.4`, :pd:`Table 5.10 <x>`; :numref:`tab-usbpd-tx`):

.. list-table:: BMC transmitter requirements (:pd:`Table 5.10`)
   :name: tab-usbpd-tx
   :header-rows: 1
   :widths: 25 45 30

   * - Parameter
     - Meaning
     - Value
   * - vSwing
     - Driven high level (low level is 0 V ± 75 mV)
     - 1.05 V to 1.20 V, nominal 1.125 V
   * - zDriver
     - Output impedance while driving, measured at 750 kHz
     - 33 Ω to 75 Ω
   * - tRise, tFall
     - 10 % to 90 % edge time, unloaded
     - at least 300 ns
   * - tStartDrive
     - When the driver may switch on, relative to the first preamble bit
     - -1 µs to +1 µs
   * - tHoldLowBMC
     - Time the driver keeps the line low after the last falling edge
     - at least 1 µs
   * - tEndDriveBMC
     - Time after the last bit by which the driver must have let go
     - at most 23 µs
   * - tInterFrameGap
     - Gap from the end of one message to the start of the next
     - at least 25 µs

The waveform must also fit a *transmit mask* when driving a model of the
worst cable and receiver (:pd:`Section 5.3.4.1`, :pd:`Figures 5.12 <x>` and
:pd:`5.13 <x>`, :pd:`Tables 5.6 <x>` and :pd:`5.7 <x>`). The mask has an
outer limit of -75 mV to 1.2 V and an inner "eye" that the waveform must
stay out of. Its coordinates give the edge
precision:

* the inner eye touches the mid-level (0.5625 V) at 0.015 UI and 0.985 UI,
  and, for a ``1``, again at 0.485 UI and 0.515 UI. Read strictly, each edge
  must therefore cross the mid-level within about ± 0.015 UI of its ideal
  time, which is ± 50 ns at 300 kbit/s (0.015 × 3.333 µs). This is a
  reading of the mask, not a number stated in the specification;
* by 0.07 UI after the ideal edge time the signal must be below 0.325 V or
  above 0.80 V, and by 0.25 UI below 0.075 V or above 1.04 V.

**Why the edges are slowed down.** The 300 ns minimum rise and fall time
limits coupling from the CC wire into neighbouring wires in the cable, in
particular the USB 2.0 data pair (:pd:`Section 5.3.4`, item 1). The slope may be
set by the driver design or by an RC filter at its output.

The inner mask sets the opposite limit: edges must not be so slow that they
eat into the eye. To see how much room there is, model the edge as a single
RC time constant. *Assumption:* the driver output behaves like a step through
a first-order RC filter; real drivers are close to this when the slope is
set by an RC network. For such an edge, the 10 %-90 % time is
:math:`\tau \ln 9`, so the time constant that gives the minimum allowed edge
time is:

.. math::

   \tau = \frac{t_{10\text{-}90}}{\ln 9}
        = \frac{300\ \text{ns}}{2.197}
        = 136.5\ \text{ns}

where :math:`\tau` is the RC time constant and :math:`t_{10\text{-}90}` is
the 10 %-90 % edge time, 300 ns (:pd:`Table 5.10`).

Next, the time for a rising edge to reach the inner-mask limit of 1.04 V
(:pd:`Table 5.7`, *Y8Tx*) from 0 V, with a final level of 1.125 V:

.. math::

   t_\text{mask} &= \tau \ln\frac{V_\text{swing}}{V_\text{swing} - V_\text{Y8}} \\
                 &= 136.5\ \text{ns} \times \ln\frac{1.125}{1.125 - 1.04} \\
                 &= 136.5\ \text{ns} \times \ln 13.24
                  = 136.5\ \text{ns} \times 2.583
                  = 353\ \text{ns}

where :math:`V_\text{swing}` = 1.125 V (nominal *vSwing*, :pd:`Table 5.10`) and
:math:`V_\text{Y8}` = 1.04 V (:pd:`Table 5.7`). The mask requires this level by
0.25 UI, which at the fastest bit rate is
:math:`0.25 \times 3.030\ \mu\text{s} = 758\ \text{ns}`. Turning this around,
the slowest RC edge that still passes is
:math:`\tau_\text{max} = 758\ \text{ns} / 2.583 = 293\ \text{ns}`, a 10 %-90 %
time of :math:`293\ \text{ns} \times 2.197 = 644\ \text{ns}`. So a driver
with a 10 %-90 % edge time between 300 ns and about 640 ns meets both limits
(an estimate under the RC assumption).

The output impedance limit (*zDriver*) bounds how much noise picked up along
the cable reaches the receiver, since a low-impedance driver holds the line
firmly at its level (:pd:`Section 5.3.4.7`). Any extra capacitance used for edge
shaping must be disconnected within *tInterFrameGap* after the message
(:pd:`Section 5.3.4.6`). The transmitter must also survive its output being shorted
to ground for 120 µs, which happens when the other side signals a fast role
swap (:pd:`Section 5.3.4.10`).

The DC level the signal starts and ends on
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When neither side transmits, the CC wire sits at the level set by Rp and Rd:
about 0.4 V, 0.9 V or 1.7 V for the three Rp levels
(:numref:`tab-usbpd-cc-nominal`). The
transmitter does not add its signal on top of this level; it overdrives the
wire with its low output impedance (33 Ω to 75 Ω against kilohms of Rp and
Rd). While it transmits the wire swings between 0 V and vSwing, and when it
lets go the wire returns to the Rp/Rd level ([USBPD-TPS25750]_, Section
9.3.1.4). Therefore:

* the transmitter starts by driving low (:pd:`Section 5.3.4`, item 2);
* the receiver must tolerate losing the first edge (:pd:`Section 5.3.4`,
  item 3);
* the last bit is followed by one more edge. If that edge goes low, the
  transmitter holds the line low for at least *tHoldLowBMC* (1 µs) and then
  lets go; if it goes high, it holds high for 1 UI, then low for at least
  1 µs, then lets go. Either way it must have let go within *tEndDriveBMC*
  (23 µs) of the end of the last bit (:pd:`Section 5.3.4`, items 4 to 6;
  :pd:`Figures 5.8 <x>` to :pd:`5.11 <x>`).

:numref:`fig-usbpd-preamble-start`, :numref:`fig-usbpd-preamble-sop` and
:numref:`fig-usbpd-message-end` show the start and end of a message.

.. wavedrom::
   :caption: Start of a message. The line idles at the Rp/Rd level (drawn
             at mid-level), then the transmitter starts the preamble by
             driving low.
   :name: fig-usbpd-preamble-start
   :alt: Timing diagram: CC idle at mid-level, then the first preamble bits
         0 1 0 1 sent in BMC starting from a low level.

   {"signal": [
     {"name": "field", "wave": "x.=.......", "data": ["preamble"]},
     {"name": "data bit", "wave": "x.=.=.=.=.", "data": ["0", "1", "0", "1"]},
     {"name": "CC", "wave": "z.0.101.01"}
   ],
   "config": {"hscale": 1}}

.. wavedrom::
   :caption: End of the 64-bit preamble and the first Sync-1 symbol of the
             start-of-packet pattern. Sync-1 is 11000 written b4 to b0, and
             bit b0 is sent first (see `Packet structure`_), so it is sent as
             0 0 0 1 1.
   :name: fig-usbpd-preamble-sop
   :alt: Timing diagram: the last two preamble bits 0 1 followed by the
         Sync-1 bits 0 0 0 1 1 in BMC.

   {"signal": [
     {"name": "field", "wave": "=...=.........", "data": ["preamble", "Sync-1"]},
     {"name": "data bit", "wave": "=.=.=.=.=.=.=.", "data": ["0", "1", "0", "0", "0", "1", "1"]},
     {"name": "CC", "wave": "1.010.1.0.1010"}
   ],
   "config": {"hscale": 1}}

.. wavedrom::
   :caption: End of a message: a final edge after the last bit of the EOP
             symbol, the line held low for at least 1 µs and released by
             23 µs after the last bit, and at least 25 µs before the next
             preamble.
   :name: fig-usbpd-message-end
   :alt: Timing diagram: the EOP bits 1 0 1 1 0 in BMC, a final falling
         edge, a short low period, then the line released to mid-level.

   {"signal": [
     {"name": "field", "wave": "=.........x...", "data": ["EOP"]},
     {"name": "data bit", "wave": "=.=.=.=.=.x...", "data": ["1", "0", "1", "1", "0"]},
     {"name": "CC", "wave": "010.10101.0..z"},
     {"name": "driver", "wave": "x.........=..x", "data": ["hold low"]}
   ],
   "config": {"hscale": 1}}

Up to 250 mV can be lost in the cable's ground wire at full current
(*vIRDropGNDC*, :pd:`Table 5.11`). This moves the received signal down at the
sink and up at the source; the receive masks below allow for it.

Receiver thresholds, filtering and noise
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :ref:`PD specification <usb-pd-specification>` does not fix the
receiver's switching thresholds.
Instead it gives *receive masks*: regions the received signal will stay out
of, after noise and ground offset (:pd:`Section 5.3.4.2`,
:pd:`Figures 5.14 <x>` to :pd:`5.19 <x>`, :pd:`Table 5.8 <x>`). The centre of the receive eye is 0.4375 V for a sink, 0.5625 V
when no current flows and 0.6875 V for a source, and the eye extends
± 0.205 V around that centre for a sink or source (± 0.33 V with no
current). The outer limits are -0.3325 V and 1.5325 V. Horizontally the eye
of a ``1`` is open from 0.07 UI to 0.43 UI and from 0.57 UI to 0.93 UI, and
that of a ``0`` from 0.07 UI to 0.93 UI, so a receiver must accept edges
displaced by about 0.07 UI from their ideal times. A dual-role port therefore
needs receiver thresholds that change with its power role.
:numref:`tab-usbpd-rx` lists the other receiver requirements.

.. list-table:: BMC receiver requirements (:pd:`Table 5.11`)
   :name: tab-usbpd-rx
   :header-rows: 1
   :widths: 25 45 30

   * - Parameter
     - Meaning
     - Value
   * - tRxFilter
     - Time constant of a single-pole filter (analog or digital) in front
       of the decision, to reject broadband noise
     - at least 100 ns
   * - vNoiseActive
     - Peak-to-peak noise from VBUS, USB 2.0 and SBU (sideband use) lines,
       after that
       filter, while a message is being received
     - up to 165 mV
   * - vNoiseIdle
     - The same while no message is sent. Anything smaller must be ignored
     - up to 300 mV
   * - vIRDropGNDC
     - Ground offset from current in the cable
     - up to 250 mV
   * - cReceiver
     - Capacitance on the CC pin while not transmitting
     - 200 pF to 600 pF
   * - rBmcRx
     - Receiver input resistance (Rp or Rd excluded)
     - at least 1 MΩ
   * - nTransitionCount, tTransitionWindow
     - The line counts as busy after 3 transitions within 12 µs to 20 µs
     - 3; 12 µs to 20 µs

A receiver is a low-pass filter followed by a comparator with hysteresis.
TI's TPS65987D, a dual-role controller, switches thresholds with the role:
504-546 mV rising and 240-260 mV falling as a sink, 840-910 mV rising and
576-624 mV falling as a source ([USBPD-TPS65987D]_, Section 6.9). In both
roles the thresholds sit either side of the eye centre for that role, and the
hysteresis of about 275 mV is larger than the 165 mV of active noise.

The USB Implementers Forum (USB-IF) also publishes an
informative white paper, *Alternate BMC Receiver Design Examples* (Revision
1.1, 2026-01-01) [USBPD-BMCRX]_, with two receivers that detect edges rather
than levels and so ignore the DC offset: one compares the signal with a copy of itself delayed by 300 ns to 500 ns (sampled every 50 ns), the
other subtracts the outputs of two low-pass filters with 200 ns and 300 ns
time constants.

The line is *idle* after *tTransitionWindow* without 3 transitions
(:pd:`Section 5.2.2.1`). A transmitter must check that the line is idle
immediately before it starts (:pd:`Section 5.2.2`).
