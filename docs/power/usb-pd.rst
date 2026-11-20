USB Power Delivery
==================

This page describes the analog circuits needed for the RISC-V processor to
carry out the USB Power Delivery negotiation in software, by directly driving
and sampling the configuration channel.

A board built around evampire can take its power from a USB Type-C
connector. In USB terms the board is a *sink*: it only receives power. The
page first explains how a USB Type-C power source and sink find each other
and agree on a voltage, then describes the signal on the wire in enough
detail to build a receiver and transmitter for it, then the time limits that
the processor has to meet, and finally the analog blocks that are needed and
which of them can be built on the gf180mcu process.

Two specifications are quoted throughout. Both are free to download from
usb.org (see `References`_):

* **Type-C** means the *USB Type-C Cable and Connector Specification*,
  Release 2.5, March 2026.
* **PD** means the *USB Power Delivery Specification*, Revision 3.3,
  Version 1.0, October 2026.

Section and table numbers given in brackets, such as (PD Table 5.10), refer to
these documents.

.. contents:: On this page
   :local:
   :depth: 2

Terms
-----

Source
   The device that supplies power, for example a mains charger or a laptop
   port.

Sink
   The device that receives power. A board built around evampire is a sink.

VBUS
   The power wire of the USB cable. It carries 5 V by default and, after a
   USB Power Delivery agreement, up to 20 V (or up to 48 V in the extended
   range described below).

CC (configuration channel)
   A signal wire in the USB Type-C cable used first to detect that a cable
   is plugged in and which way round, and then to carry the USB Power
   Delivery messages.

Rp and Rd
   *Rp* is a pull-up resistor (or current source) that a source connects to
   its CC pins. *Rd* is a 5.1 kΩ pull-down resistor that a sink connects to
   its CC pins. The voltage that results on the CC wire tells each side what
   is at the other end.

VCONN
   A 3.0 V to 5.5 V supply that a source can put on its unused CC pin to
   power small chips inside the cable plug. A sink does not normally need it
   (see `VCONN`_).

BMC (biphase mark coding)
   The way bits are turned into voltage changes on the CC wire. See
   `Biphase mark coding`_.

UI (unit interval)
   The duration of one bit on the wire, about 3.3 µs.

SOP (start of packet)
   A fixed 20-bit pattern at the start of each message that marks the
   beginning of the message and says who it is addressed to.

PDO (power data object)
   A 32-bit word in which the source describes one supply it can provide,
   for example "9 V at up to 3 A".

RDO (request data object)
   A 32-bit word in which the sink asks for one of the offered PDOs.

GoodCRC
   A short acknowledgement message. Every received message whose checksum is
   correct must be acknowledged with a GoodCRC message within 195 µs.

Contract
   The agreement between source and sink about voltage and current. Before
   any message exchange, the sink may draw the current advertised by the
   source's Rp. After a USB Power Delivery agreement (an *explicit
   contract*), it may draw the current it requested.

The connector and the CC wire
-----------------------------

A USB Type-C receptacle has 24 contacts, but a sink that only takes power
uses four kinds of them (Type-C Table 3-4 and Section 4.2):

.. list-table:: Type-C receptacle contacts used by a power-only sink
   :header-rows: 1
   :widths: 15 25 60

   * - Signal
     - Contacts
     - Use
   * - VBUS
     - A4, A9, B4, B9
     - Power from the source. Absent until the source detects a sink.
   * - GND
     - A1, A12, B1, B12
     - Power return.
   * - CC1
     - A5
     - Configuration channel, first position.
   * - CC2
     - B5
     - Configuration channel, second position.

The remaining contacts carry USB data (USB 2.0 and the faster SuperSpeed
pairs) and sideband signals. A board that does not use USB data can leave
them unconnected.

**Why there are two CC pins.** The plug can be inserted either way up. The
cable has only one CC wire, which in each plug is connected to contact A5.
Contact B5 of each plug is called VCONN and is not carried through to the
other end of the cable (Type-C Section 2.5; Table 3-10). Each receptacle
therefore has a CC contact in both positions (CC1 on A5 and CC2 on B5), and
only one of them meets the CC wire. Which one tells each side which way round
the plug was inserted (Type-C Section 2.3.2). A power-only sink does not
care about the orientation itself, but it must find out which CC pin carries
the CC wire, because that is where the messages arrive.

.. _fig-usbpd-cc-wiring:

.. graphviz:: usb-pd/cc-wiring.dot
   :caption: The single CC wire through a USB Type-C cable. In this example
             the plug at the sink end is turned over, so the source's CC1
             meets the sink's CC2. The sink's other CC pin meets the plug's
             VCONN contact, which is not connected to the source.
   :align: center

Two layers of power negotiation
-------------------------------

A sink can learn how much power is available in two ways, and uses them in
order.

1. **Resistor advertisement ("USB Type-C Current").** The source's Rp value
   says how much current the sink may draw at 5 V: the default USB amount,
   1.5 A or 3.0 A. The sink measures the voltage on its CC pin to find out.
   No messages are exchanged. This works even with no protocol logic at
   all.
2. **USB Power Delivery messages.** Source and sink exchange messages on the
   CC wire. The source lists the voltages and currents it can provide and
   the sink asks for one. This is the only way to get more than 5 V.

Layer 1: the resistor advertisement
-----------------------------------

The source pulls each of its CC pins up with Rp, and the sink pulls each of
its CC pins down with Rd. When a cable joins them, the CC wire forms a
voltage divider between Rp and Rd.

.. list-table:: Source pull-up (Rp) choices (Type-C Table 4-27)
   :header-rows: 1
   :widths: 25 25 25 25

   * - Advertised current
     - Current source to 1.7-5.5 V
     - Resistor to 4.75-5.5 V
     - Resistor to 3.3 V ± 5 %
   * - Default USB power
     - 80 µA ± 20 %
     - 56 kΩ ± 20 %
     - 36 kΩ ± 20 %
   * - 1.5 A at 5 V
     - 180 µA ± 8 %
     - 22 kΩ ± 5 %
     - 12 kΩ ± 5 %
   * - 3.0 A at 5 V
     - 330 µA ± 8 %
     - 10 kΩ ± 5 %
     - 4.7 kΩ ± 5 %

"Default USB power" means 500 mA for a USB 2.0 port and 900 mA for a
single-lane USB 3.2 port (Type-C Table 4-20).

The sink's Rd is 5.1 kΩ to ground. It may be accurate to ± 10 %, which lets
the sink tell the three current levels apart, or ± 20 %, which only lets the
sink detect that a source is present (Type-C Table 4-28). A sink can also use
a voltage clamp of 1.1 V ± 20 % instead of a resistor, which is useful while
it has no power (see `Rd while unpowered ("dead battery")`_), but a clamp
prevents USB Power Delivery communication.

With nominal values, the CC voltage seen by the sink is:

.. math::

   V_\mathrm{CC} = V_\mathrm{pull\text{-}up} \cdot \frac{R_d}{R_p + R_d}
   \qquad\text{or}\qquad V_\mathrm{CC} = I_p \cdot R_d

.. math::

   \begin{aligned}
   \text{Default:}\quad & 5\,\mathrm{V} \cdot \frac{5.1}{56 + 5.1} = 0.42\,\mathrm{V},
     & 80\,\mu\mathrm{A} \cdot 5.1\,\mathrm{k\Omega} = 0.41\,\mathrm{V} \\
   \text{1.5 A:}\quad & 5\,\mathrm{V} \cdot \frac{5.1}{22 + 5.1} = 0.94\,\mathrm{V},
     & 180\,\mu\mathrm{A} \cdot 5.1\,\mathrm{k\Omega} = 0.92\,\mathrm{V} \\
   \text{3.0 A:}\quad & 5\,\mathrm{V} \cdot \frac{5.1}{10 + 5.1} = 1.69\,\mathrm{V},
     & 330\,\mu\mathrm{A} \cdot 5.1\,\mathrm{k\Omega} = 1.68\,\mathrm{V}
   \end{aligned}

Type-C Section 4.11.3.1 gives the method for working out the full ranges,
including resistor tolerances and up to 250 mV of ground offset caused by
current flowing in the cable. For an Rd of ± 10 % the result is
(Type-C Table 4-36):

.. list-table:: CC voltage measured by the sink (Rd ± 10 %, Type-C Table 4-36)
   :header-rows: 1
   :widths: 50 25 25

   * - Condition
     - Minimum
     - Maximum
   * - Default USB power (vRd-USB)
     - 0.277 V
     - 0.612 V
   * - 1.5 A (vRd-1.5)
     - 0.746 V
     - 1.164 V
   * - 3.0 A (vRd-3.0)
     - 1.369 V
     - 2.042 V
   * - Threshold between default and 1.5 A
     - 0.613 V
     - 0.745 V
   * - Threshold between 1.5 A and 3.0 A
     - 1.165 V
     - 1.368 V
   * - Threshold for "nothing connected"
     - below 0.276 V
     -

A sink therefore needs, on each CC pin, a way of comparing the voltage with
about three thresholds: roughly 0.28 V (connected or not), 0.68 V and
1.27 V (centres of the allowed threshold windows). With Rd of ± 20 % only
the first threshold is meaningful (0.248 V, Type-C Table 4-35).

**Attach.** The steps for a sink are set out in the Type-C connection state
machine (Type-C Section 4.5.2.2.3 to 4.5.2.2.5):

#. With nothing attached, the sink presents Rd on both CC pins and waits.
#. The source sees Rd on one of its CC pins, waits for it to stay stable
   for *tCCDebounce*, 100 ms to 200 ms (Type-C Table 4-34), and then turns
   VBUS on, reaching 5 V within *tVBUSON*, at most 275 ms
   (Type-C Table 4-32).
#. On the sink side, when one CC pin rises above the "nothing connected"
   threshold, the sink waits for the CC state to stay stable for
   tCCDebounce and for VBUS to be present. It is then attached.
#. The CC pin that shows Rp is the one connected through the cable. This is
   how the orientation is found. The other CC pin stays near 0 V.

A sink that is powered only from VBUS cannot start this process until VBUS
is present, so it must show Rd before it has any power (see
`Rd while unpowered ("dead battery")`_). It then completes its own debounce
after it has powered up.

**Detach.** The sink treats the cable as removed when VBUS falls below
*vSinkDisconnect* (3.67 V at 5 V operation) and must react within
*tSinkDisconnect*, 40 ms (Type-C Table 4-3). It may also watch the CC voltage
fall below the vRd-USB range for *tPDDebounce*, 10 ms to 20 ms.

**Following a change of Rp.** A sink that uses 1.5 A or 3.0 A must keep
watching the CC voltage and reduce its current within *tSinkAdj*, 60 ms, if
the source lowers its advertisement (Type-C Section 4.6.2.1). During a USB
Power Delivery contract this no longer applies, and the source reuses its Rp
value for a different purpose: an Rp of the 3.0 A value means "the sink may
start a message exchange", the 1.5 A value means "it may not" (PD Section
5.2.2, Table 5.1). A sink that starts exchanges of its own must therefore
still be able to tell those two levels apart.

Layer 2: USB Power Delivery
---------------------------

Once VBUS is present, the source sends a list of what it can supply, and the
sink picks one item from the list.

**Standard Power Range (SPR).** The fixed voltages are 5 V, 9 V, 15 V and
20 V. Which of them a source must offer depends on its power rating: a source
of more than 15 W must offer 9 V, more than 27 W must add 15 V, and more than
45 W must add 20 V, at up to 3 A, or 5 A at 20 V with a suitable cable
(PD Section 3.2.4, Table 3.1 and Figure 3.1). Fixed supplies have a voltage
tolerance of ± 5 % (PD Section 3.2.5.1). The SPR maximum is 100 W.

**Extended Power Range (EPR).** Sources rated above 100 W and up to 240 W
can also offer 28 V, 36 V and 48 V (PD Section 3.2.5.3, Table 3.6). The sink
must first ask to enter "EPR mode" with a separate message exchange, the cable
must be marked as EPR-capable, and in EPR mode the sink must send a
keep-alive message whenever there has been no other traffic for
*tSinkEPRKeepAlive*, 250 ms to 500 ms. A source that sees no traffic for
*tSourceEPRKeepAlive*, 750 ms to 1000 ms, sends Hard Reset (PD Sections
7.31.18.2 and 7.31.18.3, Table 7.10). Any part of the
cable assembly powered from VBUS must tolerate up to 50.9 V (48 V + 5 % +
500 mV) in EPR operation (Type-C Section 4.6.2).

**Programmable Power Supply (PPS).** A source may also offer a supply whose
voltage the sink adjusts in 20 mV steps, within 5 V to 11 V, 5 V to 16 V or
5 V to 21 V depending on the range (PD Table 4.2, Table 6.21), with a current
limit set by the sink. This is aimed at charging batteries directly. A sink
using it must repeat its request at least every *tPPSRequest*, 10 s (PD
Section 7.31.16.1). A board that only needs a fixed supply has no use for
it. A related "adjustable voltage supply" (AVS) mode exists for 9 V to 20 V
and, in EPR, 15 V to 48 V (PD Tables 4.3 and 4.4).

Before any message exchange, the source supplies 5 V. A sink that never
sends a message still gets 5 V at the current set by Rp, which may be enough
for a board in a low-power mode.

Signalling on the CC wire
-------------------------

Every USB Power Delivery message is sent on the same CC wire that carries
the Rp/Rd voltage. Communication is half-duplex: only one side transmits at
a time (PD Section 5.1).

Biphase mark coding
~~~~~~~~~~~~~~~~~~~

Bits are sent using *biphase mark coding* (BMC), a form of Manchester coding
(PD Section 5.3.3). The rules are:

* the line changes level at the start of every bit;
* for a ``1``, the line also changes level in the middle of the bit;
* for a ``0``, there is no change in the middle.

Only the presence or absence of the middle transition carries the data; the
absolute level does not matter. A receiver therefore does not care which
way round the signal is, and a long run of ``0`` or ``1`` still has at least
one transition per bit, which lets the receiver follow the transmitter's
clock. Over any two ``0`` bits or any one ``1`` bit, the signal spends equal
time high and low, so the average level stays almost constant (PD Section
5.3.3).

.. wavedrom::

   {"signal": [
     {"name": "data bit", "wave": "=.=.=.=.=.=.=.=.=.",
      "data": ["0", "1", "1", "0", "1", "0", "0", "1", "0"]},
     {"name": "CC (BMC)", "wave": "0.10101.010.1.010."}
   ],
   "head": {"text": "Biphase mark coding: an edge at every bit boundary, and a second edge in the middle of each 1"},
   "config": {"hscale": 2}}

A receiver measures the time between successive edges. An interval of about
one UI means a ``0``. Two intervals of about half a UI in a row mean a
``1``.

Bit rate
~~~~~~~~

The bit rate *fBitRate* is 300 kbit/s nominal, with a permitted range of
270 kbit/s to 330 kbit/s (PD Table 5.9). This wide range lets a source or
sink use an inaccurate on-chip oscillator. Within one message the rate must
stay much more constant: after the first part of the message (the preamble,
see below), the rate may differ from the rate measured over the last 32 bits
of the preamble by no more than *pBitRate* = 0.25 % (PD Section 5.3.4.8,
Table 5.10). A receiver can therefore measure the bit time on the preamble
and use it for the rest of the message.

.. math::

   \mathrm{UI} = \frac{1}{f_\mathrm{BitRate}}:\quad
   \frac{1}{330\,\mathrm{kbit/s}} = 3.03\,\mu\mathrm{s},\quad
   \frac{1}{300\,\mathrm{kbit/s}} = 3.33\,\mu\mathrm{s},\quad
   \frac{1}{270\,\mathrm{kbit/s}} = 3.70\,\mu\mathrm{s}

The shortest time between edges is half a UI, 1.52 µs at the highest
permitted rate.

Transmitter levels, output impedance and edge rate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The transmitter is a tri-state driver: it drives the CC wire between 0 V and
*vSwing* while sending, and lets go of the wire (high impedance) at all other
times (PD Section 5.3.4, Table 5.10):

.. list-table:: BMC transmitter requirements (PD Table 5.10)
   :header-rows: 1
   :widths: 25 45 30

   * - Parameter
     - Meaning
     - Value
   * - vSwing
     - Driven high level (low level is 0 V)
     - 1.05 V to 1.20 V, nominal 1.125 V
   * - zDriver
     - Output impedance while driving, measured at 750 kHz
     - 33 Ω to 75 Ω
   * - tRise, tFall
     - 10 % to 90 % edge time, unloaded
     - at least 300 ns
   * - tStartDrive
     - When the driver may switch on, relative to the first preamble bit
     - -1 µs to +1 µs
   * - tHoldLowBMC
     - Time the driver keeps the line low after the last falling edge
     - at least 1 µs
   * - tEndDriveBMC
     - Time after the last bit by which the driver must have let go
     - at most 23 µs
   * - tInterFrameGap
     - Gap from the end of one message to the start of the next
     - at least 25 µs

The low level must be within ± 75 mV of ground, and the whole waveform must
fit a *transmit mask* when driving a model of the worst cable and receiver
(PD Section 5.3.4.1, Figures 5.12 and 5.13, Tables 5.6 and 5.7; the load
model is in Section 5.3.4.3). The mask has an outer limit of -75 mV to
1.2 V and an inner "eye" that the waveform must stay out of. Reading the
mask coordinates gives a feel for how precise the edges must be:

* the inner eye touches the mid-level (0.5625 V) at 0.015 UI and 0.985 UI,
  and, for a ``1``, again at 0.485 UI and 0.515 UI. Each edge must therefore
  cross the mid-level within about ± 0.015 UI (± 50 ns at 300 kbit/s) of
  its ideal time;
* by 0.07 UI after the ideal edge time the signal must be below 0.325 V or
  above 0.80 V, and by 0.25 UI it must be below 0.075 V or above 1.04 V.

**Why the edges are slowed down.** The 300 ns minimum rise and fall time is
there to limit coupling from the CC wire into neighbouring wires in the
cable, in particular the USB 2.0 data pair (PD Section 5.3.4, item 1). The
specification allows the slope to be set either by the design of the driver
or by an RC filter at its output. The inner mask sets the other limit: the
edges may not be so slow that they eat into the eye. For an RC-shaped edge
with a 10 %-90 % time of 300 ns the time constant is

.. math::

   \tau = \frac{t_{10\text{-}90}}{\ln 9} = \frac{300\,\mathrm{ns}}{2.197}
   \approx 137\,\mathrm{ns},

and an edge starting from 0 V passes 1.04 V (the inner mask limit, 92 % of
1.125 V) after
:math:`\tau \ln\bigl(1.125 / (1.125 - 1.04)\bigr) \approx 2.6\,\tau \approx 350\,\mathrm{ns}`,
inside the 0.25 UI (760 ns at 330 kbit/s) that the mask allows. A driver
with a minimum edge time of 300 ns therefore has margin, but one with edges
much slower than about 600 ns would not.

The output impedance limit (*zDriver*) is defined as
:math:`z_\mathrm{Driver} = r_\mathrm{Output} / (1 + s\,r_\mathrm{Output}\,c_\mathrm{Shunt})`
(PD Section 5.3.4.7). It bounds how much noise picked up along the cable
reaches the receiver, since a low-impedance driver holds the line firmly at
its level. Any extra capacitance used for edge shaping must be disconnected
again within *tInterFrameGap* after the message, so that the port presents
only its normal receive capacitance (PD Section 5.3.4.6).

The DC level the signal starts and ends on
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When neither side is transmitting, the CC wire sits at the level set by the
source's Rp and the sink's Rd: about 0.4 V, 0.9 V or 1.7 V for the three Rp
values, as calculated above. The transmitter does not add its signal on top
of this level. It overdrives the wire with its low output impedance
(33 Ω to 75 Ω against kilohms of Rp and Rd), so while it transmits the wire
swings between 0 V and vSwing, and when it lets go the wire returns to the
Rp/Rd level. A message therefore starts with a step from the idle level to
0 V and ends with a return from 0 V to the idle level:

* the transmitter starts by driving low (PD Section 5.3.4, item 2);
* the receiver must tolerate losing the first edge, because depending on the
  idle level the step into the first bit may be small or in the wrong
  direction (PD Section 5.3.4, item 3);
* the last bit is followed by one more edge so that the receiver can time
  the last bit. If that edge goes low, the transmitter holds the line low
  for at least *tHoldLowBMC* (1 µs) and then lets go. If it goes high, the
  transmitter holds it high for 1 UI, then low for at least 1 µs, then lets
  go. In either case it must have let go within *tEndDriveBMC* (23 µs) of
  the end of the last bit (PD Section 5.3.4, items 4 to 6; Figures 5.8 to
  5.11).

.. wavedrom::

   {"signal": [
     {"name": "field", "wave": "x.=.......|=.......=.........=.........",
      "data": ["preamble (64 bits)", "preamble (end)", "Sync-1", "Sync-1"]},
     {"name": "data bit", "wave": "x.=.=.=.=.|=.=.=.=.=.=.=.=.=.=.=.=.=.=.",
      "data": ["0", "1", "0", "1", "0", "1", "0", "1", "0", "0", "0", "1", "1", "0", "0", "0", "1", "1"]},
     {"name": "CC", "wave": "z.0.101.01|0.101.010.1.0.10101.0.1.0101"}
   ],
   "head": {"text": "Start of a message: idle at the Rp/Rd level (drawn mid-level), then the preamble from a low level, then the start-of-packet pattern"},
   "config": {"hscale": 1}}

.. wavedrom::

   {"signal": [
     {"name": "field", "wave": "=.........=.........x.......",
      "data": ["last CRC symbol (end)", "EOP"]},
     {"name": "data bit", "wave": "=.=.=.=.=.=.=.x.............",
      "data": ["0", "1", "1", "0", "1", "1", "0"]},
     {"name": "CC", "wave": "1.01010.10101.0...z.........",
      "node": "..............A...B........."},
     {"name": "", "wave": "", "node": "..............C............D"}
   ],
   "edge": ["A<->B hold low ≥ 1 µs, release by 23 µs", "C<->D tInterFrameGap ≥ 25 µs before the next preamble"],
   "head": {"text": "End of a message: a final edge after the last bit, a short low hold, then release to the Rp/Rd level"},
   "config": {"hscale": 1}}

The idle level also shifts with current. Up to 250 mV can be lost in the
cable's ground wire at full current (*vIRDropGNDC*, PD Table 5.11), which
moves the received signal down at the sink and up at the source. The receive
requirements below allow for this.

Receiver thresholds, filtering and noise
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The PD specification does not fix the receiver's switching thresholds.
Instead it gives *receive masks*: regions the received signal will stay out
of, after noise and ground offset, which the receiver must decode correctly
(PD Section 5.3.4.2, Figures 5.14 to 5.19, Table 5.8). For a sink the centre
of the receive eye is at 0.4375 V and the eye spans 0.2325 V to 0.6425 V
(0.4375 V ± 0.205 V). For comparison, the eye centre is 0.5625 V when no
current flows and 0.6875 V at a source. The outer limits are -0.3325 V and
1.5325 V. Horizontally, the eye of a ``1`` is open from 0.07 UI to 0.43 UI
and from 0.57 UI to 0.93 UI, and the eye of a ``0`` from 0.07 UI to
0.93 UI, so a receiver must accept edges displaced by up to about 0.07 UI
from their ideal times.

.. list-table:: BMC receiver requirements (PD Table 5.11)
   :header-rows: 1
   :widths: 25 45 30

   * - Parameter
     - Meaning
     - Value
   * - tRxFilter
     - Time constant of a single-pole filter (analog or digital) in front of
       the decision, to reject broadband noise
     - at least 100 ns
   * - vNoiseActive
     - Peak-to-peak noise from VBUS, USB 2.0 and SBU lines, after that
       filter, while a message is being received
     - up to 165 mV
   * - vNoiseIdle
     - The same while no message is sent. Anything smaller must be ignored
     - up to 300 mV
   * - vIRDropGNDC
     - Ground offset from current in the cable
     - up to 250 mV
   * - cReceiver
     - Capacitance on the CC pin while not transmitting
     - 200 pF to 600 pF
   * - rBmcRx
     - Receiver input resistance (Rd excluded)
     - at least 1 MΩ
   * - nTransitionCount, tTransitionWindow
     - The line counts as busy after 3 transitions within 12 µs to 20 µs
     - 3; 12 µs to 20 µs

In practice a sink receiver is a low-pass filter followed by a comparator
with hysteresis. As an example, TI's TPS25750 uses a rising threshold of
499 mV to 551 mV and a falling threshold of 230 mV to 270 mV in sink mode,
and 784 mV to 866 mV rising / 523 mV to 578 mV falling in source mode
(TPS25750 datasheet, Section 7.14). These thresholds sit either side of the
sink eye centre, and the hysteresis of about 275 mV is larger than the
165 mV of active noise. Note that the falling threshold is close to the
lowest idle level (about 0.3 V with a default-power Rp and full ground
offset), so the receiver must also rely on edge timing, not only on the
level, to decide whether a message is present.

The USB-IF publishes an informative white paper, *Alternate BMC Receiver
Design Examples* (Revision 1.1, 2026-01-01), with two receivers that are
insensitive to the DC offset: one compares the signal with a copy of itself
delayed by 300 ns to 500 ns (sampled every 50 ns), the other subtracts the
outputs of two low-pass filters with 200 ns and 300 ns time constants. Both
detect edges rather than levels.

The line is considered *idle* after *tTransitionWindow* without 3
transitions (PD Section 5.2.2.1). A transmitter must check that the line is
idle immediately before it starts (PD Section 5.2.2).

Packet structure
~~~~~~~~~~~~~~~~

A packet on the wire has five parts (PD Section 5.3.1.1, Figure 5.1):

.. list-table:: Parts of a packet
   :header-rows: 1
   :widths: 20 20 60

   * - Part
     - Length on the wire
     - Content
   * - Preamble
     - 64 bits
     - Alternating ``0`` and ``1``, starting with ``0`` and ending with
       ``1``. Not 4b5b coded. Lets the receiver settle and measure the bit
       rate (PD Section 5.3.1.1.1).
   * - SOP
     - 20 bits
     - Four 5-bit special symbols that mark the start and say who the
       message is for (see below).
   * - Message header and data
     - 20 bits per 16-bit header, 40 bits per 32-bit data object
     - 4b5b coded, least significant byte first and least significant
       nibble of each byte first.
   * - CRC
     - 40 bits
     - 32-bit checksum, 4b5b coded.
   * - EOP
     - 5 bits
     - One special "end of packet" symbol.

**4b5b coding.** Except for the preamble, the data is sent in 5-bit
*symbols*. Each 4-bit nibble is replaced by a 5-bit code from a fixed table,
and a few further 5-bit codes are reserved as special symbols (*K-codes*)
that never appear in data (PD Section 5.3.1.1.2, Table 5.2). Because the
special symbols cannot occur in data, a receiver can find the start and end
of a message without counting bits. Within each symbol, bit b0 is sent
first.

.. list-table:: 4b5b codes (PD Table 5.2), written b4 b3 b2 b1 b0
   :header-rows: 1
   :widths: 12 18 12 18 12 18 22

   * - Nibble
     - Symbol
     - Nibble
     - Symbol
     - Nibble
     - Symbol
     - Special symbols
   * - 0
     - 11110
     - 6
     - 01110
     - C
     - 11010
     - Sync-1: 11000
   * - 1
     - 01001
     - 7
     - 01111
     - D
     - 11011
     - Sync-2: 10001
   * - 2
     - 10100
     - 8
     - 10010
     - E
     - 11100
     - Sync-3: 00110
   * - 3
     - 10101
     - 9
     - 10011
     - F
     - 11101
     - RST-1: 00111
   * - 4
     - 01010
     - A
     - 10110
     -
     -
     - RST-2: 11001
   * - 5
     - 01011
     - B
     - 10111
     -
     -
     - EOP: 01101

All other 5-bit values are invalid. A receiver that sees one discards the
packet (PD Section 5.3.2.3).

**Start of packet (SOP).** The four K-codes after the preamble form an
*ordered set* that says who the message is for (PD Section 5.3.1.1.3, Table
5.3; resets in Table 5.4):

.. list-table:: Ordered sets (PD Tables 5.3 and 5.4)
   :header-rows: 1
   :widths: 25 15 15 15 15 15

   * - Name
     - 1st
     - 2nd
     - 3rd
     - 4th
     - Use
   * - SOP
     - Sync-1
     - Sync-1
     - Sync-1
     - Sync-2
     - Between source and sink
   * - SOP'
     - Sync-1
     - Sync-1
     - Sync-3
     - Sync-3
     - To the near cable plug
   * - SOP''
     - Sync-1
     - Sync-3
     - Sync-1
     - Sync-3
     - To the far cable plug
   * - Hard Reset
     - RST-1
     - RST-1
     - RST-1
     - RST-2
     - Reset signal (no data follows)
   * - Cable Reset
     - RST-1
     - Sync-1
     - RST-1
     - Sync-3
     - Resets the cable plugs

Two further debug ordered sets exist (SOP'_Debug, SOP''_Debug). A receiver
must accept an ordered set with all four K-codes correct, and may accept one
with three of the four correct (PD Section 5.3.2.2, Table 5.5). A sink only
acts on SOP messages and Hard Reset. Before a contract, a source may talk to
the cable with SOP' messages; the sink must ignore those and must not
acknowledge them.

**CRC.** The checksum is CRC-32 with polynomial 04C1 1DB7h, initial value
FFFF FFFFh, calculated bit 0 first over the header and data bytes, and
complemented before sending; a receiver that runs the CRC over data and
checksum together gets the fixed remainder C704 DD7Bh (PD Section
5.3.1.1.4). The specification states that it is the CRC used by USB 3. It is
also the Ethernet frame checksum: the worked example in PD Figure 5.1, a
GoodCRC message with bytes 41h 02h, has the checksum 46B5 0D97h, which is
exactly what a standard Ethernet/zlib CRC-32 routine returns for those two
bytes. evampire already checks this checksum on Ethernet frames (see
:doc:`../architecture/index`).

**End of packet (EOP).** A single EOP K-code. It is not covered by the CRC
(PD Section 5.3.1.1.5).

Message format
~~~~~~~~~~~~~~

Each message starts with a 16-bit header (PD Section 6.2.1, Table 6.2).
*Control* messages (for example GoodCRC, Accept, PS_RDY) consist of the
header alone. *Data* messages (for example Source_Capabilities, Request)
add one to seven 32-bit data objects (PD Section 6.1.1). A third kind,
*extended* messages, carries up to 260 bytes and is not needed for a basic
sink.

.. wavedrom::

   {"reg": [
     {"name": "Message type", "bits": 5, "attr": "e.g. 00001 GoodCRC"},
     {"name": "DR", "bits": 1, "attr": "0"},
     {"name": "Revision", "bits": 2, "attr": "10 = 3.x"},
     {"name": "PR", "bits": 1, "attr": "0"},
     {"name": "MessageID", "bits": 3},
     {"name": "Data objects", "bits": 3},
     {"name": "Ext", "bits": 1}
   ],
   "config": {"hspace": 900, "bits": 16, "lanes": 1}}

* **Message type** (bits 4 to 0): the meaning depends on whether there are
  data objects. Control messages used by a sink include GoodCRC (00001),
  Accept (00011), Reject (00100), PS_RDY (00110), Get_Source_Cap (00111),
  Wait (01100) and Soft_Reset (01101) (PD Table 6.4). Data messages include
  Source_Capabilities (00001) and Request (00010) (PD Table 6.5).
* **MessageID** (bits 11 to 9): a 3-bit counter kept by the sender of each
  message. A GoodCRC carries the MessageID of the message it acknowledges
  (PD Sections 6.1.2 and 6.3.1). A receiver uses it to recognise a message
  it has already received when the sender repeats it.
* **Number of data objects** (bits 14 to 12): zero for control messages.
* **Power role** (PR, bit 8), **data role** (DR, bit 5) and **specification
  revision** (bits 7 to 6): a sink sets the power role bit to 0. Before any
  data role swap, a sink is also the "upstream" side and sets the data role
  bit to 0. The revision is agreed
  from the first Source_Capabilities and Request (PD Section 6.1.3.1).

The two data objects a sink must understand are the *fixed supply PDO* in
Source_Capabilities and the *fixed supply RDO* in Request.

Fixed supply PDO (bits 31 to 30 are ``00`` for a fixed supply):

.. wavedrom::

   {"reg": [
     {"name": "Max current (10 mA units)", "bits": 10},
     {"name": "Voltage (50 mV units)", "bits": 10},
     {"name": "Peak", "bits": 2},
     {"name": "Flags (first PDO only)", "bits": 8},
     {"name": "00", "bits": 2}
   ],
   "config": {"hspace": 900, "bits": 32, "lanes": 1}}

Fixed supply RDO:

.. wavedrom::

   {"reg": [
     {"name": "Operating current (copy)", "bits": 10},
     {"name": "Operating current (10 mA units)", "bits": 10},
     {"name": "Resv", "bits": 2},
     {"name": "Flags", "bits": 6},
     {"name": "Object position", "bits": 4}
   ],
   "config": {"hspace": 900, "bits": 32, "lanes": 1}}

In a fixed PDO, bits 31 to 30 are ``00``, bits 19 to 10 give the voltage in
50 mV units and bits 9 to 0 the maximum current in 10 mA units (PD Tables
6.6, 6.8 and 6.10). The first PDO is always 5 V and its upper bits carry
flags about the source. In the RDO, bits 31 to 28 select a PDO by position
(1 = the first), bits 19 to 10 give the current the sink will draw, and bits
9 to 0 must repeat the same value (PD Table 6.19). For example, offered
"9 V, 3 A" is the PDO ``0002 D12Ch`` (voltage field 180, current field
300), and a request for 2 A from the second PDO is the RDO ``2003 20C8h``.

**Length of typical messages.** With the packet structure above, a packet
with *n* data objects is :math:`64 + 20 + 20 + 40n + 40 + 5 = 149 + 40n`
bits long:

.. list-table:: Packet duration
   :header-rows: 1
   :widths: 40 15 20 25

   * - Message
     - Bits
     - At 300 kbit/s
     - At 270 kbit/s
   * - GoodCRC, Accept, PS_RDY (no data objects)
     - 149
     - 497 µs
     - 552 µs
   * - Request (one data object)
     - 189
     - 630 µs
     - 700 µs
   * - Source_Capabilities with seven PDOs
     - 429
     - 1430 µs
     - 1589 µs

Time limits and the negotiation sequence
----------------------------------------

The timers below are the ones a sink has to meet or can rely on.

.. list-table:: Timing values relevant to a sink
   :header-rows: 1
   :widths: 25 20 55

   * - Name
     - Value
     - Meaning
   * - tTransmit
     - at most 195 µs
     - From the end of a received message's EOP to the start of the
       GoodCRC preamble (PD Section 7.31.1, Table 7.10).
   * - tInterFrameGap
     - at least 25 µs
     - Minimum gap before any transmission, including a GoodCRC (PD Section
       5.3.4.9, Table 5.10).
   * - tReceive
     - 0.9 ms to 1.1 ms
     - How long a sender waits for GoodCRC before deciding the message was
       lost (PD Section 7.31.1, Table 7.10).
   * - tRetry
     - at most 195 µs
     - From giving up waiting to starting the repeat (PD Section 7.31.1).
   * - nRetryCount
     - 2
     - Number of repeats after the first attempt (PD Table 7.12).
   * - tReceiverResponse
     - at most 15 ms
     - From the GoodCRC of a message that needs an answer to the start of
       the answer (PD Section 7.31.2).
   * - tSenderResponse
     - 27 ms to 50 ms
     - How long the asking side waits for the answer (PD Table 7.10).
   * - tFirstSourceCap
     - at most 250 ms
     - From VBUS reaching 5 V to the first Source_Capabilities (PD Section
       7.31.3.3).
   * - tTypeCSendSourceCap
     - 100 ms to 200 ms
     - Interval at which the source repeats Source_Capabilities until it is
       acknowledged (PD Section 7.31.3.1). After nCapsCount (50) attempts
       it may slow down.
   * - tTypeCSinkWaitCap
     - 310 ms to 620 ms
     - After this long without Source_Capabilities, the sink may send Hard
       Reset to make the source start again (PD Section 7.31.3.2).
   * - tPSTransition
     - 450 ms to 550 ms
     - How long the sink waits for PS_RDY after Accept (SPR; PD Table 7.10).
   * - tSinkTx
     - 16 ms to 20 ms
     - Time allowed for a source to change Rp for collision avoidance (PD
       Table 7.10).

**Acknowledgement.** Every correctly received SOP message must be answered
with GoodCRC so that its first preamble bit starts between 25 µs and 195 µs
after the last bit of the received EOP. If the CRC is wrong, the message is
discarded silently and no GoodCRC is sent.

.. wavedrom::

   {"signal": [
     {"name": "sender", "wave": "z=.....z.........", "data": ["message (0.5 ms to 1.6 ms)"]},
     {"name": "receiver", "wave": "z......z...=....z", "data": ["GoodCRC (0.5 ms)"]},
     {"name": "", "wave": "", "node": ".......A...B....."},
     {"name": "", "wave": "", "node": ".......C......D.."}
   ],
   "edge": ["A<->B gap ≥ 25 µs", "C<->D GoodCRC starts within 195 µs"],
   "head": {"text": "Acknowledgement timing (not to scale)"},
   "config": {"hscale": 2}}

**Retries.** A sender that has not received GoodCRC within tReceive
(0.9 ms to 1.1 ms after its EOP) sends the same message again, starting
within tRetry (195 µs), up to nRetryCount = 2 times, so each message is sent
at most three times (PD Section 7.31.1). The repeat has the same MessageID,
and the receiver acknowledges it again but does not act on it twice.

**What happens if the sink is too slow.** Before a contract, a missed
GoodCRC simply means the source keeps resending Source_Capabilities every
100 ms to 200 ms. After a contract, a message that fails to arrive or a
timeout is a *protocol error*, which leads to a Soft_Reset message exchange
or to *Hard Reset* (PD Section 7.1.1). A sink that does not receive PS_RDY
in time also sends Hard Reset (PD Section 9.2.4.8). On a Hard Reset, the
source switches VBUS off (to *vSafe0V*, at most 0.8 V), waits *tSrcRecover*
(0.66 s to 1.0 s in SPR) and then supplies 5 V again (PD Section 4.4; Tables
4.7 and 4.9). For a board that takes all of its power from VBUS, a Hard
Reset is a complete power cycle.

The negotiation sequence
~~~~~~~~~~~~~~~~~~~~~~~~

.. _fig-usbpd-negotiation:

.. graphviz:: usb-pd/negotiation.dot
   :caption: A sink negotiating a fixed 9 V supply. Each message that has a
             correct CRC is answered with GoodCRC. For 20 V the sequence is
             the same with a different object position in the Request.
   :align: center

After Accept, the sink must reduce its current to at most *iSnkStdby*
(500 mA) before the source starts changing the voltage (PD Section 4.5.1.1,
Table 4.8). After PS_RDY it may draw up to the current it
requested. The source decides whether to accept: it answers Reject if the
request is not possible, or Wait if it cannot do it now (the sink then waits
at least *tSinkRequest*, 100 ms, before asking again; PD Section 7.31.4.1).

A sink that boots slowly does not miss the negotiation: if it is not ready to
answer the first Source_Capabilities, the source keeps repeating it (50
times at 100 ms to 200 ms intervals, then possibly less often; PD Section
7.31.3.1). The sink may also send Hard Reset after tTypeCSinkWaitCap to make
the source start again, but a sink powered only from VBUS should avoid this,
because the source answers a Hard Reset by switching VBUS off.

What these timings mean for software
------------------------------------

The processor in evampire is a small 32-bit RISC-V core, which may run from a
clock derived from the 125 MHz reference (see :doc:`../architecture/index`).
The task divides into three parts with very different time scales:

* **Bit level** (microseconds): find edges, decode BMC, generate BMC with
  edges placed within about ± 50 ns.
* **Packet level** (hundreds of microseconds): 4b5b decode, SOP detection,
  CRC, and the GoodCRC reply within 195 µs.
* **Protocol and policy** (milliseconds to seconds): choose a PDO, send
  Request, wait for Accept and PS_RDY, handle Reject, Wait, Soft_Reset and
  Hard Reset. Everything here has a deadline of 15 ms or more and is easy
  in software.

Receive at the bit level
~~~~~~~~~~~~~~~~~~~~~~~~

The shortest interval between edges is 1.52 µs (half a UI at 330 kbit/s),
and the decision between "half UI" and "full UI" has to be made with edges
displaced by up to about 0.07 UI (230 ns). A practical decoder measures the
UI on the preamble and then classifies each interval against 0.75 UI.

*Pure software sampling.* The processor reads the receiver comparator in a
loop and looks for changes. To place each edge to within, say, one eighth of
the shortest interval needs a sample every 190 ns, about 5.3 million samples
per second. Each sample costs at least a load, a compare and a branch, so
the loop alone needs a core clock of several tens of MHz, with interrupts
disabled for the whole message (up to about 1.6 ms) and the core doing
nothing else. The processor would also have to watch the line continuously,
because a message can arrive at any time, or at least have an interrupt on
the first edge, which with a 64-bit preamble leaves time to start the loop.
This is possible in principle, but it ties up the core and any interrupt
latency from other work (for example Ethernet frame handling) corrupts the
message.

*Edge-time capture.* A free-running counter is latched into a small FIFO on
every comparator edge. With the counter clocked at 15.625 MHz (125 MHz / 8),
each timestamp has 64 ns resolution, enough to separate 0.5 UI from 1 UI by
a wide margin. The worst case is a run of ``1`` bits: two edges per UI, about
660 000 edges per second at 330 kbit/s. Taking one interrupt per edge is
not practical on a small core, but reading the FIFO in bursts is: a message
of up to 429 bits has at most about 860 edges. If classifying one interval
and shifting the result into a symbol takes 20 to 30 instructions (an
estimate, not a measurement), the core spends roughly 13 to 20 million
instructions per second while a message is arriving, which is a large but
manageable share of a core running at 50 MHz or more, for at most about
1.6 ms per message. With a FIFO of 16 to 32 entries, the processor needs to
empty the FIFO about every 20 µs to 40 µs during a message, which it can do
in a loop started by an interrupt on the first edge.

*Hardware BMC bit decoder.* A small state machine that does the
interval-classification itself and delivers decoded bits (or 5-bit symbols)
in a shift register cuts the software work to one action per 5-bit symbol,
about 60 000 per second. The logic is a counter, a comparator against a
programmable "0.75 UI" value and a few flip-flops.

Transmit at the bit level
~~~~~~~~~~~~~~~~~~~~~~~~~

Edges must land within about ± 50 ns of their ideal times, and the bit rate
must not drift by more than 0.25 % within a message. Toggling an output from
software in an interrupt routine cannot meet this. A cycle-counted loop with
interrupts disabled can, if the core's timing is fully predictable, but it
ties up the core for the whole message. A *timer-driven serializer* is the
robust option: software loads the bits (already 4b5b coded, or as nibbles if
the 4b5b table is in hardware) into a FIFO or shift register, and a counter
toggles the output every half UI according to the BMC rule, then performs
the end-of-message hold-low and release automatically. The analog driver
behind it sets the swing and the edge rate.

Packet level and the GoodCRC deadline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The 195 µs GoodCRC deadline is the tightest requirement above the bit level.
It is manageable in software because:

* the CRC can be calculated while the message arrives, a nibble or a byte at
  a time, so only the last few bytes remain when the EOP arrives. A
  table-driven CRC needs a 16-entry table per nibble or a 256-entry table per
  byte;
* a GoodCRC message from a sink differs only in its MessageID (and possibly
  the revision bits), so all eight possible GoodCRC packets, including their
  CRCs, can be prepared in advance;
* the transmitter must also wait at least 25 µs, so the useful window for
  software is about 25 µs to 150 µs after the EOP, allowing some margin.

The risk is interrupt latency from other tasks. If the Ethernet code can
hold off interrupts for more than about 100 µs, the GoodCRC deadline will be
missed. Commercial controllers such as the onsemi FUSB302B solve this by
sending GoodCRC and repeating unacknowledged messages in hardware
("Automatic GoodCRC Packet Response" and "Automatic Retries", FUSB302B
datasheet, features list), so that the processor only has to answer within
the millisecond-scale protocol deadlines.

A possible split
~~~~~~~~~~~~~~~~

.. list-table:: Hardware and software split options
   :header-rows: 1
   :widths: 22 38 40

   * - Option
     - Hardware
     - Software load and risk
   * - A. Software only
     - Comparator, driver, a plain input and output bit.
     - Core busy for every message; edges cannot be placed within ± 50 ns
       without a fully predictable cycle-counted loop; GoodCRC timing
       depends on interrupt latency. Fragile.
   * - B. Edge capture and serializer
     - As A, plus edge-timestamp capture with FIFO and a timer-driven BMC
       serializer with end-of-message handling.
     - Software decodes intervals, 4b5b, SOP and CRC. Moderate load during
       messages only. GoodCRC still a software deadline (195 µs).
   * - C. Bit-level PHY
     - As B, plus BMC bit decoder producing 5-bit symbols, and 4b5b
       encode/decode.
     - Software handles symbols, CRC and protocol. Light load.
   * - D. Packet-level PHY
     - As C, plus SOP detection, CRC-32 generation and checking, automatic
       GoodCRC and retries (as in FUSB302B).
     - Software only handles the protocol, with deadlines of 15 ms and
       above.

The recommended minimum is option B. It keeps the protocol in software, as
intended, and puts in hardware only the two things software cannot do
reliably: timing edges to tens of nanoseconds on receive, and placing edges
to ± 50 ns on transmit. If the worst-case interrupt latency of the rest of
the firmware cannot be kept well below 100 µs, the automatic GoodCRC reply
from option D can be added on its own. Option B is the smallest addition
that makes software decoding robust: a
counter, a timestamp FIFO, a half-UI timer and a shift register. Option D
removes all sub-millisecond deadlines from software at the cost of packet
buffers and more control logic; its CRC-32 logic is the same as the
Ethernet checksum logic.

Analog blocks
-------------

.. _fig-usbpd-blocks:

.. graphviz:: usb-pd/sink-blocks.dot
   :caption: Circuits for a USB Power Delivery sink controlled by the evampire
             processor. Solid arrows carry signals, bold arrows carry power,
             dashed arrows carry control and status.
   :align: center

Switchable Rd on each CC pin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Requirement.* 5.1 kΩ to ground on both CC1 and CC2, ± 10 % if the sink
wants to read the Rp level and ± 20 % otherwise (Type-C Table 4-28). The
value is the total resistance into the pin, including the switch
(Type-C Table 4-28, note 2). The sink must also be able to remove Rd and
present at least *zOPEN* = 126 kΩ when the Type-C state machine requires it
(Type-C Table 4-30).

*How it is normally done.* A resistor in series with a switch, often trimmed
during production. Examples: TPS25750 *RSNK* 4.6 kΩ to 5.6 kΩ after
trimming; onsemi FUSB302B *RDEVICE* 4.6 kΩ to 5.6 kΩ; Infineon CYPD3177
*Rd* 4.59 kΩ to 5.61 kΩ (datasheet Table 15).

*On gf180mcu.* The CC voltage with Rd connected is at most 2.18 V, and up
to 5.5 V if Rd is removed while the source's pull-up is still there (Type-C
Section 4.11.1 allows pull-up voltages up to 5.5 V). A poly resistor and a
5 V or 6 V MOS switch cover this.

Rd while unpowered ("dead battery")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Requirement.* A source turns VBUS on only after it sees Rd. If the board's
only power comes from VBUS, evampire is unpowered at the moment of
connection, so Rd must be present without any supply (Type-C Section 4.8.5;
Type-C Section 4.5.2.2.3: "A port with a dead battery shall enter this state
while unpowered").

*How it is normally done.* Type-C Section 4.8.5 gives the standard
circuit: an Rd of ± 20 % in series with a MOS transistor whose gate is
weakly pulled up to the CC pin itself, with a threshold voltage below the
maximum clamp voltage (1.32 V). The source's pull-up then turns the
transistor on through its gate, the CC pin settles inside the allowed range,
and once the chip is powered it can switch this path off and use the trimmed
Rd instead. Switching between the two must keep the CC voltage inside the
band that indicates a connection (Type-C Section 4.11.1). Examples:

* TPS25750: "dead battery Rd clamp" *VCLAMP* of 0.25 V to 1.32 V, 0.65 V to
  1.32 V and 1.20 V to 2.18 V for the three Rp currents, measured with no
  supply (datasheet Section 7.12).
* STUSB4500: separate pins CC1DB and CC2DB, connected to CC1 and CC2 on the
  board, provide the pull-down when the chip is unpowered (datasheet DS12499
  Section 3.5).
* CYPD3177: *Rd_DB* of 4.08 kΩ to 6.12 kΩ with all supplies at 0 V
  (datasheet Table 15).
* TI TPD8S300A (a CC protection chip): integrated dead-battery resistors,
  4.1 kΩ to 6.1 kΩ in series with a FET whose threshold *VTH_DB* is 0.5 V to
  1.2 V (datasheet Section 7.6).
* TI TUSB320 (a Type-C detection chip without USB Power Delivery): CC pins
  default to 5.1 kΩ ± 20 % pull-downs when VDD is absent (datasheet Section
  7.4.3).

*On gf180mcu.* The PDK includes a 6 V native NMOS (*nfet_06v0_nvt*) with a
threshold voltage of -0.32 V to 0.08 V (PDK electrical specification
section 4.0). Its threshold is well below the 1.32 V limit, so it can serve
as the self-biased switch in series with a poly resistor. Its leakage when
"off" and the behaviour of the ESD structures on an unpowered pad must be
checked in simulation.

CC level comparators or ADC
~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Requirement.* On each CC pin, detect "nothing connected" (below about
0.28 V) and, when the Rp level is wanted, the two thresholds at about
0.68 V and 1.27 V (Type-C Table 4-36), with debouncing over 100 ms to
200 ms. The debouncing is easily done in software if the comparator outputs
are readable.

*How it is normally done.* FUSB302B has three fixed comparators with
thresholds of 0.15 V to 0.25 V, 0.61 V to 0.70 V and 1.16 V to 1.31 V and
20 mV of hysteresis, plus a 6-bit DAC with 42 mV steps and a comparator for
finer measurements (datasheet Table 10). CYPD3177 uses an 8-bit ADC with a
2.0 V reference (datasheet Table 23).

*On gf180mcu.* All voltages are below 2.2 V in normal operation. A resistor
ladder or small DAC with one comparator multiplexed between the two CC pins
and the VBUS divider output is enough, since none of these signals needs to
be measured faster than about once per millisecond. An accurate reference
voltage is needed; the open gf180mcu PDK lists no bandgap reference among its
IP blocks, so one has to be designed or the thresholds made ratiometric to a
supply that is accurate enough.

BMC transmitter
~~~~~~~~~~~~~~~

*Requirement.* Drive 0 V and 1.05 V to 1.20 V, output impedance 33 Ω to
75 Ω, 10 %-90 % edge time of at least 300 ns while still meeting the
transmit mask, high impedance when not sending, and tolerate being shorted
to ground (PD Section 5.3.4.10). One driver is connected to the active CC
pin (chosen after attach), or one driver per pin.

*How it is normally done.* TPS25750 drives 1.05 V to 1.2 V high, -75 mV to
75 mV low, with an output impedance of 33 Ω to 75 Ω (typically 54 Ω) and
rise and fall times of at least 300 ns unloaded, the maximum being set by
the transmit mask (datasheet Section 7.14). Its block diagram shows the
driver supplied from the chip's internal 3.3 V regulator, with level
shifters between the logic and the pins (datasheet Figure 9-7). FUSB302B
gives the same limits (datasheet Table 9).

*On gf180mcu.* The driver runs from a regulated rail of about 1.125 V
(± 6 %), which needs a small linear regulator and a reference. The edge rate
can be set by limiting the gate drive current of the output transistors or
by a series resistor and a switched capacitor that is disconnected after the
message. 3.3 V devices are adequate for the driver itself, but the pin must
withstand the CC voltages listed above (up to 5.5 V), which calls for 5 V or
6 V devices on the pad side or a protecting series switch.

BMC receiver
~~~~~~~~~~~~

*Requirement.* Decode signals that stay outside the receive masks (sink eye
0.2325 V to 0.6425 V), with a filter of at least 100 ns time constant,
ignoring up to 300 mV of noise when idle, input resistance of at least
1 MΩ, total pin capacitance of 200 pF to 600 pF (PD Tables 5.8 and 5.11).

*How it is normally done.* An RC or switched filter and a comparator with
hysteresis; see the TPS25750 thresholds above. The pin capacitance is
usually made up with an external capacitor, since the chip's own is much
lower (TPS25750 lists at most 120 pF and recommends adding capacitance
externally, datasheet Section 7.14; FUSB302B lists 50 pF typical).

*On gf180mcu.* A comparator with thresholds of about 0.25 V and 0.53 V and
an RC filter of about 100 ns to 150 ns. A digital glitch filter after the
comparator (for example rejecting pulses shorter than 300 ns) adds
robustness. The edge-detecting receivers of the USB-IF white paper are an
alternative if ground offset turns out to be a problem.

VBUS sensing
~~~~~~~~~~~~

*Requirement.* Detect that VBUS is present (for attach; *vSafe5V* is 4.75 V
to 5.5 V, PD Table 4.9) and that it has fallen below
*vSinkDisconnect* (3.67 V at 5 V; Type-C Table 4-3). After a voltage change,
checking the new voltage is good practice and protects the board against a
faulty source.

*How it is normally done.* A resistor divider into a comparator or ADC.
TUSB320 uses an external 887 kΩ resistor from VBUS to its VBUS_DET pin
(which tolerates at most 4 V) with an internal 95 kΩ pull-down, giving a
detection threshold of 2.95 V to 3.8 V at VBUS (datasheet Section 6.5).
STUSB4500 has VBUS sense pins rated to 28 V and a window comparator around
the expected voltage (datasheet Section 3.4.1). FUSB302B measures VBUS up to
20 V with 420 mV steps (datasheet Table 10).

*On gf180mcu.* VBUS is up to about 21 V in SPR (20 V + 5 %) and up to
50.9 V in EPR. The top resistor of the divider must be outside the chip; the
chip sees only the divided voltage.

Over-voltage protection on the CC pins
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Requirement.* In normal operation the CC pins see at most 5.5 V. But the CC
contact sits next to VBUS in the connector, and damaged or non-compliant
cables and debris can short the two. TI explains that twisting or sliding
the plug, debris or moisture can short 20 V VBUS onto CC (TPD8S300A
datasheet, Section 3). Infineon notes that such a short rings because of the
cable's inductance and capacitance and can reach about twice the VBUS
voltage, 44 V for 21.5 V, if nothing clamps it (CYPD3177 datasheet Section
1.1.3). The Type-C specification itself allows any port to clamp its CC pins
at 2.9 V or above to protect them (Type-C Table 4-40).

*How it is normally done.* Commercial controllers either make their CC pins
tolerate VBUS, or rely on an external protection chip:

.. list-table:: CC pin voltage ratings of commercial parts
   :header-rows: 1
   :widths: 25 35 40

   * - Part
     - CC pin rating
     - Source
   * - TI TPS25750 (PD controller)
     - -0.5 V to 26 V absolute maximum; disconnects its PD transmitter when
       CC exceeds 5.5 V to 8.5 V
     - Datasheet SLVSFR7A, Sections 7.1, 7.14, 9.3.5
   * - ST STUSB4500 (PD sink controller)
     - 22 V absolute maximum ("short-to-VBUS protections on CC pins")
     - Datasheet DS12499 Rev 3, Table 20
   * - Infineon CYPD3177 (PD sink controller)
     - 22 V absolute maximum; 17 V indefinitely, 17 V to 22 V for 1000 hours
     - Datasheet 002-25383 Rev. \*C, Section 1.1.3 and absolute maximum
       ratings
   * - onsemi FUSB302B (PD PHY)
     - -0.5 V to 6.0 V absolute maximum
     - Datasheet Rev. 5, Table 7
   * - TI TUSB320 (Type-C detection only)
     - -0.3 V to 6 V absolute maximum
     - Datasheet SLLSEN9F, Section 6.1
   * - TI TPD8S300A (external protector)
     - 24 V short-to-VBUS tolerance; series switches open when CC exceeds
       5.75 V to 6.2 V, typically within 70 ns
     - Datasheet SLVSEL9, Sections 7.6 and 7.7

The usual arrangement for a controller with low-voltage CC pins is the last
row: a high-voltage series switch on each CC line that opens when the voltage
rises above about 6 V, followed by the controller. The switch must pass the
BMC signal and the Rd current without noticeable resistance in normal
operation, and for a sink it must also keep the dead-battery Rd visible.

*On gf180mcu.* None of the PDK devices withstands 20 V (see below), so the
protection against a VBUS short has to be outside the chip. Protection
against electrostatic discharge at the connector, specified with the
IEC 61000-4-2 system-level test (as TPD8S300A and CYPD3177 do for their CC
pins), is also expected to be external.

Power path switch
~~~~~~~~~~~~~~~~~

*Requirement.* Connects VBUS to the board's load. A sink must limit its
current to the advertised value before a contract, to 500 mA (iSnkStdby)
during a voltage change, and must not be damaged by the highest voltage it
may receive.

*How it is normally done.* An external MOSFET switch driven by the
controller. CYPD3177 drives external P-channel MOSFETs with a soft start to
limit inrush current (datasheet Section 1.1.4). STUSB4500 has an output,
VBUS_EN_SNK, to enable the external switch (datasheet Section 3.5).
TPS25750 has gate drivers for external N-channel MOSFETs with over-voltage
and reverse-current protection (datasheet Section 9.3.3).

*On gf180mcu.* The switch itself is external. evampire can provide a logic
output; a 5 V or 6 V output (or an open-drain output tolerant to that
voltage) can drive an external gate driver or the gate of a P-channel MOSFET
through a level-shifting transistor. Because evampire itself is powered from
VBUS through the board's regulators, there are two possible arrangements:

* the regulators that feed evampire are always connected to VBUS and must
  accept the full range of voltages the sink may request, while only the
  rest of the load is switched; or
* everything is connected directly and the board draws little enough
  current at 5 V that no switch is needed before the contract.

VCONN
~~~~~

VCONN is a 3.0 V to 5.5 V supply of up to 1 W to 1.5 W (Type-C Table 4-5)
that the source puts on its CC pin that is *not* connected to the CC wire.
Through the plug's VCONN contact it powers small chips inside the cable
plugs, called *e-markers*, which report the cable's current rating and other
properties. Full-featured USB Type-C cables, cables rated for more than
3 A, and EPR cables all contain an e-marker (Type-C Sections 3.4.1.1,
3.4.2.1, 3.11.2 and 4.9). VCONN is isolated from the other end of the cable
(Type-C Section 2.5), so the source's VCONN never reaches the sink.

A sink does not supply VCONN when it attaches (Type-C Section 4.5.2.2.5.1:
"VCONN shall not be supplied in the Attached.SNK state"). VCONN is needed
by the side that talks to the cable, which is normally the source: for
example, a source may only operate in EPR with an EPR-capable cable (PD
Section 3.2.5.3, item 5), and the cable's 5 A rating decides whether more
than 3 A may be offered (PD Table 3.4, note 2). The two sides can exchange
the VCONN duty with a VCONN_Swap message exchange, but the receiving side
may answer Reject or Not_Supported (PD Section 7.13), so a sink that always
refuses needs no VCONN switch. Its unused
CC pin may see the e-marker's pull-down *Ra* (800 Ω to 1.2 kΩ, Type-C
Table 4-29) or nothing.

What can be built on gf180mcu
-----------------------------

The gf180mcu PDK documentation describes the process as "0.18 µm 3.3V/(5V)6V
dual-gate MCU technology" (PDK Design Manual, Section 1.0), with low-voltage
(LV) devices at 3.3 V and high-voltage (HV) devices at 5 V or 6 V (Section
2.7). The device list for models and layout-versus-schematic checking also
contains 10 V lateral double-diffused MOS (LDMOS) transistors (Appendix A).

.. list-table:: gf180mcu device voltage ratings from the PDK documentation
   :header-rows: 1
   :widths: 30 35 35

   * - Device
     - Operating voltage
     - Breakdown data
   * - nfet_03v3, pfet_03v3
     - 3.3 V
     - BVDSS at least 7 V (N) and 6.5 V (P); gate oxide breakdown at least
       7 V (electrical specification sections 1.0 and 5.4)
   * - nfet_05v0, pfet_05v0
     - 5 V (same devices as 6 V, with a 5 V marker layer)
     - BVDSS at least 8.5 V (section 3.0)
   * - nfet_06v0, pfet_06v0
     - 6 V
     - BVDSS at least 8.5 V; gate oxide breakdown at least 12 V
       (sections 2.0 and 5.4)
   * - nfet_06v0_nvt (native)
     - 6 V
     - Threshold -0.32 V to 0.08 V; BVDSS at least 8 V (section 4.0)
   * - nfet_10v0_asym, pfet_10v0_asym (LDMOS)
     - 10 V drain, 6 V gate
     - BVDSS at least 13.2 V (sections 8.1 and 8.2; layout rules in Design
       Manual Section 10.12)
   * - N-well to substrate junction
     -
     - Breakdown at least 10 V (section 5.5)

Comparing these with the voltages on the pins of a USB Type-C sink:

.. list-table:: Pin voltages and where each function can be built
   :header-rows: 1
   :widths: 22 30 48

   * - Node
     - Voltage
     - Placement
   * - CC1, CC2, normal operation
     - 0 V to 2.18 V with Rd; up to 5.5 V with Rd removed; BMC 0 V to
       1.2 V
     - On chip, with 5 V or 6 V devices at the pin. Rd, dead-battery Rd,
       comparators, receiver and transmitter can all be on chip.
   * - CC1, CC2, fault (shorted to VBUS)
     - Up to about 21 V (SPR), 50.9 V (EPR), with ringing up to about twice
       that
     - External series protection switch that opens above about 6 V, plus
       ESD protection. Not possible with PDK devices (10 V LDMOS is the
       highest rating).
   * - VBUS sense
     - 5 V to about 21 V (SPR) or 50.9 V (EPR)
     - External divider (at least the top resistor), on-chip comparator or
       ADC on the divided voltage.
   * - VBUS power path
     - Same as VBUS, at up to 3 A or 5 A
     - External switch and regulators; evampire provides a control output.
   * - VCONN
     - Not used by a sink
     -

Open design decisions
---------------------

The following choices are not yet made:

* **Hardware and software split** for the BMC physical layer: options B, C or
  D in the table above. This decides whether GoodCRC timing is a software
  deadline.
* **Requested voltage and power.** The total power the evampire board needs
  sets the minimum source rating it can work with at 5 V, and whether it
  should ask for 9 V, 15 V or 20 V. Staying in SPR (20 V or less) avoids
  EPR's 48 V and its keep-alive messages, and keeps the CC fault voltage
  lower. Whether to support only fixed supplies (the simplest case) is part
  of this decision.
* **Where the CC protection sits.** The proposal above uses an external
  protection chip. The alternative is a discrete high-voltage switch per CC
  line; either way the dead-battery Rd must stay visible through it.
* **Dead-battery Rd implementation.** On chip (native NMOS and poly
  resistor) or in the external protection chip, which some parts provide.
* **Reference voltage** for the BMC driver level and the CC thresholds:
  whether an on-chip bandgap reference is designed or an external reference
  is used.
* **Clock and timer resolution** available to the edge-capture and
  serializer logic, which depends on the clock chosen for the processor
  subsystem.
* **Power path arrangement**: which parts of the board are switched and
  whether the regulators feeding evampire must accept 20 V.
* **Interaction with Power over Ethernet** if a board supports both power
  inputs; see :doc:`poe`.

References
----------

Specifications (both free from usb.org):

* USB Implementers Forum, *USB Type-C Cable and Connector Specification*,
  Release 2.5, March 2026. Document library:
  https://www.usb.org/document-library/usb-type-cr-cable-and-connector-specification-release-24
  (download: "USB Type-C 2.5 Release 202603").
* USB Implementers Forum, *USB Power Delivery Specification*, Revision 3.3,
  Version 1.0, 2026-10-16. Document library:
  https://www.usb.org/document-library/usb-power-delivery
  (download: USB_PD_R3.3_V1.0.zip).
* USB Implementers Forum, *Alternate BMC Receiver Design Examples*,
  informative white paper, Revision 1.1, 2026-01-01. Included in the USB
  Power Delivery download above.

Datasheets:

* Texas Instruments, *TPS25750 USB Type-C and USB PD Controller with
  Integrated Power Switches*, SLVSFR7A, revised November 2020.
  https://www.ti.com/lit/ds/symlink/tps25750.pdf
* Texas Instruments, *TUSB320 USB Type-C Configuration Channel Logic and
  Port Control*, SLLSEN9F, revised March 2022.
  https://www.ti.com/lit/ds/symlink/tusb320.pdf
* Texas Instruments, *TPD8S300A USB Type-C Port Protector: Short-to-VBUS
  Overvoltage and IEC ESD Protection*, SLVSEL9, June 2018.
  https://www.ti.com/lit/ds/symlink/tpd8s300a.pdf
* STMicroelectronics, *STUSB4500 Standalone USB PD Controller (Sink)*,
  DS12499 Rev 3, December 2019.
  https://www.st.com/resource/en/datasheet/stusb4500.pdf
* onsemi, *FUSB302B Programmable USB Type-C Controller with PD*, Rev. 5,
  August 2021. https://www.onsemi.com/download/data-sheet/pdf/fusb302b-d.pdf
* Infineon, *EZ-PD BCR USB Type-C Port Controller for Power Sinks
  (CYPD3177)*, 002-25383 Rev. \*C, 2024-09-18.
  https://www.infineon.com/assets/row/public/documents/24/49/infineon-cypd3177-24lqxq-datasheet-en.pdf

gf180mcu process:

* GlobalFoundries GF180MCU PDK documentation:
  https://gf180mcu-pdk.readthedocs.io/
* Design Manual, Sections 1.0 and 2.0 (process and operating voltages):
  https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_02.html
* Design Manual, Appendix A (device list):
  https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_15.html
* Design Manual, Section 10.12 (10 V LDMOS rules):
  https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_10_12.html
* Electrical Parameters Specification (device voltages, breakdown):
  https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs.html
