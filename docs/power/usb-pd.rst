USB Power Delivery
==================

This page describes how the `RISC-V <https://riscv.org/>`__
:ref:`processor <arch-microcontroller>` carries out the USB Power Delivery
negotiation in software, by directly driving and sampling the configuration
channel; which analog circuits it needs for that; and what the gf180mcu
process allows on the chip.

A board built around evampire bridges power between Ethernet and USB Type-C
in both directions (see :doc:`index`). Every USB Type-C port on the board is
therefore *dual-role*: it can supply power (act as a *source*) or receive
power (act as a *sink*), it settles on one of the two when a cable is plugged
in, and it can swap roles with the other end while the cable stays connected.
The first version of the board has one USB Type-C port; the
:ref:`full design <power-board-configs>` has two, each dual-role.

USB Power Delivery is implemented mostly in software on the RISC-V processor.
The dedicated hardware is kept to the minimum: the analog circuits that
connect to the configuration channel wires, and only those digital helpers
whose timing cannot be met in software (power bridging
:ref:`requirements`).

The page first explains how two USB Type-C ports find each other and decide
who supplies power, then how they agree on a voltage, then the signal on the
wire in enough detail to receive and send it in software, the source side,
cables, role changes, two ports, the cost of doing all of this in software,
the analog blocks, and the on-chip and external options for each of them on
the gf180mcu process (https://gf180mcu-pdk.readthedocs.io/; see
`Limits of the gf180mcu process`_).

Two specifications are quoted throughout. Both are free to download from the
USB Implementers Forum (USB-IF) document library (https://www.usb.org/):

* **Type-C** means the :ref:`USB Type-C Cable and Connector Specification
  <usb-type-c-specification>`, Release 2.5, March 2026 [USBPD-TYPEC]_.
* **PD** means the :ref:`USB Power Delivery Specification
  <usb-pd-specification>`, Revision 3.3, Version 1.0, 2026-10-16
  [USBPD-PD]_.

Section and table numbers given in brackets, such as (:pd:`Table 5.10`),
refer to these documents and link to their entries on the
:doc:`standards page <../standards>`.

Terms
-----

See also :ref:`power-roles` for the names of the two ends of a powered cable.

Source
   The end of a cable that supplies power, for example a mains charger, or a
   board built around evampire when it is powered from Ethernet.

Sink
   The end that receives power, for example a phone, or a board built around
   evampire when it takes its power from USB.

Dual-role port
   A port that can act as either source or sink. The USB documents call it a
   *DRP* (dual-role power port).

VBUS
   The power wire of the USB cable. It carries 5 V by default and, after a
   USB Power Delivery agreement, up to 20 V, or up to 48 V in the extended
   range (see `Layer 2: USB Power Delivery power levels`_).

CC (configuration channel)
   A signal wire in the USB Type-C cable used first to detect that a cable is
   plugged in and which way round, and then to carry the USB Power Delivery
   messages.

Rp, Rd and Ra
   *Rp* is a pull-up (a resistor or a current source) that a source connects
   to its CC pins (:typec:`Table 4-27`). *Rd* is a 5.1 kΩ pull-down that a
   sink connects to its CC pins (:typec:`Table 4-28`). *Ra* is a pull-down of
   800 Ω to 1.2 kΩ found inside some cable plugs (:typec:`Table 4-29`). The
   voltage that results on a CC pin tells each side what is at the other end.

VCONN
   A supply that the source puts on its unused CC pin to power a small chip
   inside the cable plug; it is valid from 3.0 V to 5.5 V (*vVCONNValid*,
   :typec:`Table 4-5`). See `Cables and VCONN`_.

E-marker
   The chip inside an *electronically marked* cable plug that reports the
   cable's current and voltage rating when asked. See `Cables and VCONN`_.

BMC (biphase mark coding)
   The way bits are turned into voltage changes on the CC wire. See
   `Biphase mark coding`_.

UI (unit interval)
   The duration of one bit on the wire, about 3.3 µs (see `Bit rate`_).

SOP (start of packet)
   A fixed 20-bit pattern at the start of each message that marks its start
   and says who it is for: the other port (SOP) or a cable plug (SOP′ or
   SOP″). See `Packet structure`_.

PDO (power data object)
   A 32-bit word in which a source describes one supply it can provide, for
   example "9 V at up to 3 A" (:numref:`fig-usbpd-pdo`).

RDO (request data object)
   A 32-bit word in which a sink asks for one of the offered PDOs
   (:numref:`fig-usbpd-rdo`).

VDO (vendor data object)
   A 32-bit data word in a Vendor_Defined message; the cable's answer to the
   cable query is made of VDOs.

GoodCRC
   A short acknowledgement message. Every correctly received message must be
   acknowledged with a GoodCRC message within 195 µs (*tTransmit*,
   :pd:`Section 7.31.1`; see `Negotiation and time limits`_).

Hard Reset
   A special signal, not a message, that makes both ports return their power
   supplies to the default state and restart the negotiation
   (:pd:`Section 7.1.3`). As source, the port switches VBUS off and on again.
   See `Hard Reset in each role`_.

Contract
   The agreement between source and sink about voltage and current. Before
   any message exchange, the sink may draw the current advertised by the
   source's Rp (`Layer 1: the resistor advertisement`_). After a USB Power
   Delivery agreement (an *explicit contract*) it may draw the current it
   requested (`Layer 2: USB Power Delivery power levels`_).

DFP and UFP
   *Downstream facing port* (the USB host side for data) and *upstream facing
   port* (the device side). These are *data roles*. A port that attaches as
   a source starts as DFP and one that attaches as a sink starts as UFP. A
   board without USB data still has to carry these roles in its messages.

SBU (sideband use)
   Two contacts of the USB Type-C connector reserved for other signals, for
   example in alternate modes. Not used by evampire.

USB-IF
   The USB Implementers Forum, which publishes the USB specifications
   (https://www.usb.org/).

ESD (electrostatic discharge)
   A short high-voltage pulse from a charged person or object touching a
   pin. See `Over-voltage protection on the CC pins`_.

ADC, DAC
   Analog-to-digital and digital-to-analog converter.

FIFO
   A first-in, first-out buffer.

PDK
   The process design kit: the device models, layout rules and libraries
   published for a process.

NMOS, PMOS, FET, MOSFET
   N-channel and P-channel metal-oxide-semiconductor field-effect transistors
   (FET and MOSFET are general names for them).

LDMOS
   Laterally diffused MOS transistor: a transistor with an extended drain
   region that withstands a higher drain voltage than a standard transistor.

MIM capacitor
   A metal-insulator-metal capacitor built between two metal layers.

The connector and the CC wire
-----------------------------

A USB Type-C receptacle has 24 contacts. A port that only moves power uses
four kinds of them (:numref:`tab-usbpd-contacts`; :typec:`Table 3-4` and
:typec:`Section 4.2 <x>`):

.. list-table:: Type-C receptacle contacts used by a power-only port
   :name: tab-usbpd-contacts
   :header-rows: 1
   :widths: 15 25 60

   * - Signal
     - Contacts
     - Use
   * - VBUS
     - A4, A9, B4, B9
     - Power. Not driven by a source until it has detected a sink.
   * - GND
     - A1, A12, B1, B12
     - Power return.
   * - CC1
     - A5
     - Configuration channel, first position.
   * - CC2
     - B5
     - Configuration channel, second position.

The remaining contacts carry USB data and sideband signals. A board that does
not use USB data can leave them unconnected.

**Why there are two CC pins.** The plug can be inserted either way up. The
cable has only one CC wire, which in each plug is connected to contact A5.
Contact B5 of each plug is called VCONN and is not carried through to the
other end of the cable (:typec:`Section 2.5`; :typec:`Table 3-10 <x>`). Each
receptacle therefore has a CC contact in both positions, CC1 and CC2, and
only one of them meets the CC wire (:numref:`fig-usbpd-cc-wiring`). Which one
tells each side which way round the plug was inserted
(:typec:`Section 2.3.2`). A power-only port does not need the orientation
itself, but it must know which CC pin carries the CC wire, because that is
where messages arrive, and the source must know which pin is left over,
because that is where it supplies VCONN.

.. _fig-usbpd-cc-wiring:

.. graphviz:: usb-pd/cc-wiring.dot
   :caption: The single CC wire through a USB Type-C cable. In this example
             the plug at the sink end is turned over, so the source's CC1
             meets the sink's CC2. Each port's other CC pin meets the plug's
             VCONN contact, which is not connected to the far end.
   :align: center

Two layers of power negotiation
-------------------------------

1. **Resistor advertisement ("USB Type-C Current")**, described in
   `Layer 1: the resistor advertisement`_. The source's Rp value says how
   much current the sink may draw at 5 V: the default USB amount, 1.5 A or
   3.0 A. The sink measures the voltage on its CC pin. No messages are
   exchanged.
2. **USB Power Delivery messages**, described in
   `Layer 2: USB Power Delivery power levels`_ and the sections after it.
   Source and sink exchange messages on the CC wire. The source lists the
   voltages and currents it can supply and the sink asks for one. This is the
   only way to get more than 5 V or more than 3 A: the resistor
   advertisement stops at 3.0 A at 5 V, while USB Power Delivery goes up to
   48 V and 5 A (:typec:`Table 4-19`).

Layer 1: the resistor advertisement
-----------------------------------

The source pulls each of its CC pins up with Rp, and the sink pulls each of
its CC pins down with Rd. When a cable joins them, the CC wire forms a
voltage divider (or, with a current-source Rp, a current flowing into Rd).
:numref:`tab-usbpd-rp` lists the allowed pull-ups.

.. list-table:: Source pull-up (Rp) choices (:typec:`Table 4-27`)
   :name: tab-usbpd-rp
   :header-rows: 1
   :widths: 25 25 25 25

   * - Advertised current
     - Current source to 1.7-5.5 V
     - Resistor to 4.75-5.5 V
     - Resistor to 3.3 V ± 5 %
   * - Default USB power
     - 80 µA ± 20 %
     - 56 kΩ ± 20 %
     - 36 kΩ ± 20 %
   * - 1.5 A at 5 V
     - 180 µA ± 8 %
     - 22 kΩ ± 5 %
     - 12 kΩ ± 5 %
   * - 3.0 A at 5 V
     - 330 µA ± 8 %
     - 10 kΩ ± 5 %
     - 4.7 kΩ ± 5 %

"Default USB power" means 500 mA for a USB 2.0 port
(https://www.usb.org/document-library/usb-20-specification) and 900 mA for a
single-lane USB 3.2 port
(https://www.usb.org/document-library/usb-32-revision-11-june-2022)
(:typec:`Table 4-20`).

The sink's Rd is 5.1 kΩ to ground. It may be accurate to ± 10 %, which lets
the sink tell the three current levels apart, or ± 20 %, which only lets it
detect that a source is present (:typec:`Table 4-28`). An unpowered sink may
instead present a 1.1 V ± 20 % clamp, which stops USB Power Delivery
communication until it switches to a real Rd (:typec:`Table 4-28`, note 1).

**The CC voltage for each Rp level.** Both ends decide what is attached by
measuring the CC voltage, so the circuit designer needs to know what voltage
each combination produces. With a resistor Rp the CC voltage is set by the
divider; with a current-source Rp it is the current times Rd:

.. math::

   V_\text{CC} = V_\text{pull} \cdot \frac{R_d}{R_p + R_d}
   \qquad\text{or}\qquad
   V_\text{CC} = I_p \cdot R_d

where:

* :math:`V_\text{CC}` is the voltage on the connected CC pin, in volts;
* :math:`V_\text{pull}` is the voltage the resistor Rp is connected to:
  5 V or 3.3 V (:typec:`Table 4-27`);
* :math:`R_p` is the source's pull-up resistor (:typec:`Table 4-27`);
* :math:`I_p` is the source's pull-up current (:typec:`Table 4-27`);
* :math:`R_d` is the sink's pull-down, 5.1 kΩ nominal (:typec:`Table 4-28`).

The model assumes nominal values, no current in the cable and a negligible
cable resistance (the same assumption :typec:`Section 4.11.3.1` makes). As an
example of the steps, for 22 kΩ to 5 V:
:math:`R_p + R_d = 22 + 5.1 = 27.1\ \text{k}\Omega`, and
:math:`5\ \text{V} \times 5.1 / 27.1 = 0.941\ \text{V}`. The same steps for
every level give :numref:`tab-usbpd-cc-nominal`:

.. list-table:: Nominal CC voltage with Rd = 5.1 kΩ
   :name: tab-usbpd-cc-nominal
   :header-rows: 1
   :widths: 25 25 25 25

   * - Advertised current
     - Resistor to 5 V
     - Resistor to 3.3 V
     - Current source
   * - Default USB power
     - 5 × 5.1 / 61.1 = 0.417 V
     - 3.3 × 5.1 / 41.1 = 0.409 V
     - 80 µA × 5.1 kΩ = 0.408 V
   * - 1.5 A
     - 5 × 5.1 / 27.1 = 0.941 V
     - 3.3 × 5.1 / 17.1 = 0.984 V
     - 180 µA × 5.1 kΩ = 0.918 V
   * - 3.0 A
     - 5 × 5.1 / 15.1 = 1.689 V
     - 3.3 × 5.1 / 9.8 = 1.717 V
     - 330 µA × 5.1 kΩ = 1.683 V

The three methods give nearly the same voltage for each level, which is what
lets a sink read the level without knowing how the source made it. The three
levels are about 0.4 V, 0.9 V and 1.7 V.

**What the sink measures.** :typec:`Section 4.11.3.1` gives the method for
including all tolerances and up to 250 mV of ground offset caused by current
in the cable. For an Rd of ± 10 % the result is :numref:`tab-usbpd-sink-thresholds`
(:typec:`Table 4-36`):

.. list-table:: CC voltage measured by a sink (Rd ± 10 %, :typec:`Table 4-36`)
   :name: tab-usbpd-sink-thresholds
   :header-rows: 1
   :widths: 50 25 25

   * - Condition
     - Minimum
     - Maximum
   * - Default USB power (vRd-USB)
     - 0.277 V
     - 0.612 V
   * - 1.5 A (vRd-1.5)
     - 0.746 V
     - 1.164 V
   * - 3.0 A (vRd-3.0)
     - 1.369 V
     - 2.042 V
   * - Threshold between default and 1.5 A
     - 0.613 V
     - 0.745 V
   * - Threshold between 1.5 A and 3.0 A
     - 1.165 V
     - 1.368 V
   * - Threshold for "nothing connected"
     - below 0.276 V
     -

**What the source measures.** A source uses its own CC voltage to tell an Rd
(a sink), an Ra (a cable plug with an e-marker) and nothing (an open pin)
apart. Because a source knows its own Rp, it has one set of thresholds per Rp
level. For a current-source Rp (the type that suits an integrated circuit,
see `Switchable Rp`_) the thresholds are in :numref:`tab-usbpd-src-thresholds`
(:typec:`Table 4-37`):

.. list-table:: CC voltage thresholds for a source with a current-source Rp (:typec:`Table 4-37`)
   :name: tab-usbpd-src-thresholds
   :header-rows: 1
   :widths: 25 25 25 25

   * - Rp level
     - Ra below, Rd above (window)
     - Rd range (vRd)
     - Open above (minimum)
   * - Default (80 µA)
     - 0.116 V to 0.260 V
     - 0.261 V to 1.32 V
     - 1.321 V
   * - 1.5 A (180 µA)
     - 0.234 V to 0.675 V
     - 0.676 V to 1.32 V
     - 1.441 V
   * - 3.0 A (330 µA)
     - 0.429 V to 0.879 V
     - 0.88 V to 2.181 V
     - 2.432 V

The "open" thresholds allow 250 mV of ground offset (:typec:`Table 4-37`,
note 1). A commercial example is the TI TPS65987D [USBPD-TPS65987D]_, which
as a source detects an Ra below 0.15-0.25 V, 0.35-0.45 V or 0.75-0.85 V and
an open pin above 1.5-1.65 V, 1.5-1.65 V or 2.45-2.615 V for the three Rp
levels (Section 6.8). A dual-role port therefore needs, per CC pin, three
thresholds as a sink (:numref:`tab-usbpd-sink-thresholds`: connected, and
the two boundaries between the Rp levels) and, as a source, two boundaries
for each Rp level it uses (Ra to Rd, and Rd to open;
:numref:`tab-usbpd-src-thresholds`).

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

.. graphviz:: usb-pd/drp-states.dot
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

Layer 2: USB Power Delivery power levels
----------------------------------------

Once VBUS is present the source sends a list of what it can supply and the
sink picks one item. The board's supported maximum is not yet fixed, so all
power levels are listed here.

**Standard Power Range (SPR).** Fixed voltages of 5 V, 9 V, 15 V and 20 V.
Which ones a source must offer depends on its power rating: up to 15 W only
5 V; above 15 W also 9 V; above 27 W also 15 V; above 45 W also 20 V
(:pd:`Section 3.2.4`, :pd:`Table 3.1 <x>`). Currents are up to 3 A, and up to
5 A at 20 V (100 W) with a 5 A cable (:pd:`Table 3.1`, note 1;
:pd:`Section 8.6.1.2.2 <x>`). Fixed supplies have a tolerance of ± 5 %
(:pd:`Table 4.7`, *vSrcNew*). The highest voltage VBUS may then reach in SPR
is 21.5 V: the 20 V supply at its +5 % limit (21.0 V, *vSrcNew*) plus the
0.5 V allowed during transitions and load steps (*vSrcValid*, both
:pd:`Table 4.7`). This page uses 21.5 V as the SPR worst case. (The cable
field description in :pd:`Table 6.45` gives the same formula, *vSrcNew* max
plus *vSrcValid* max, but quotes 21.55 V as its result; the table values
give 21.5 V.)

**Extended Power Range (EPR).** Sources rated above 100 W and up to 240 W can
also offer 28 V, 36 V and 48 V at up to 5 A (:pd:`Section 3.2.5.3`,
:pd:`Table 3.6 <x>`). The sink must first ask to enter "EPR mode" with a
separate message exchange, the source must check that the cable is
EPR-capable (:pd:`Section 8.6.1.2.3`), and in EPR mode the sink sends a
keep-alive message whenever there has been no other traffic for
*tSinkEPRKeepAlive* (250 ms to 500 ms); a source that sees no traffic for
*tSourceEPRKeepAlive* (750 ms to 1000 ms) sends Hard Reset
(:pd:`PD Sections 7.31.18.2 <x>` and :pd:`7.31.18.3 <x>`,
:pd:`Table 7.10 <x>`). The EPR worst case is 50.9 V (48 V + 5 % + 0.5 V), the
voltage cable electronics powered from VBUS must tolerate
(:typec:`Section 4.6.2`). Power role swaps are not allowed in EPR mode; a
port must leave EPR mode first (:pd:`Section 7.10`).

**Programmable Power Supply (PPS).** A supply whose voltage the sink adjusts
in 20 mV steps (*vPpsStep*, :pd:`Table 4.7`) within 5 V to 11 V, 5 V to 16 V
or 5 V to 21 V (:pd:`Table 4.2`), with a current limit the sink sets in 50 mA
steps (*iPpsCLStep*, :pd:`Table 4.7`). It is aimed at charging batteries
directly. The sink repeats its request at least every *tPPSRequest*, 10 s
(:pd:`Section 7.31.16.1`). A source that offers PPS must also offer the
related *adjustable voltage supply* (AVS) mode (:pd:`Section 3.2.5.2`), which
covers 9 V to 20 V in SPR and 15 V to 48 V in EPR in 100 mV steps
(:pd:`PD Tables 4.3 <x>`, :pd:`4.4 <x>` and :pd:`4.7 <x>`).

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

The USB Implementers Forum (USB-IF, https://www.usb.org/) also publishes an
informative white paper, *Alternate BMC Receiver Design Examples* (Revision
1.1, 2026-01-01) [USBPD-BMCRX]_, with two receivers that detect edges rather
than levels and so ignore the DC offset: one compares the signal with a copy of itself delayed by 300 ns to 500 ns (sampled every 50 ns), the
other subtracts the outputs of two low-pass filters with 200 ns and 300 ns
time constants.

The line is *idle* after *tTransitionWindow* without 3 transitions
(:pd:`Section 5.2.2.1`). A transmitter must check that the line is idle
immediately before it starts (:pd:`Section 5.2.2`).

Packet structure
~~~~~~~~~~~~~~~~

A packet on the wire has five parts (:numref:`tab-usbpd-packet`):

.. list-table:: Parts of a packet (:pd:`Section 5.3.1.1`, :pd:`Figure 5.1 <x>`)
   :name: tab-usbpd-packet
   :header-rows: 1
   :widths: 20 20 60

   * - Part
     - Length on the wire
     - Content
   * - Preamble
     - 64 bits
     - Alternating ``0`` and ``1``, starting with ``0`` and ending with
       ``1``. Not 4b5b coded. Lets the receiver settle and measure the bit
       rate (:pd:`Section 5.3.1.1.1`).
   * - SOP
     - 20 bits
     - Four 5-bit special symbols that mark the start and say who the
       message is for.
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
that never appear in data (:pd:`Section 5.3.1.1.2`, :pd:`Table 5.2 <x>`;
:numref:`tab-usbpd-4b5b`). Because the special symbols cannot occur in data, a receiver can find the start and end
of a message without counting bits. Within each symbol, bit b0 is sent
first.

.. list-table:: 4b5b codes (:pd:`Table 5.2`), written b4 b3 b2 b1 b0
   :name: tab-usbpd-4b5b
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

All other 5-bit values are invalid; a receiver that sees one discards the
packet (:pd:`Section 5.3.2.3`).

**Start of packet (SOP).** The four K-codes after the preamble form an
*ordered set* that says who the message is for (:numref:`tab-usbpd-sop`;
:pd:`Section 5.3.1.1.3`, :pd:`Table 5.3 <x>`; resets in :pd:`Table 5.4 <x>`):

.. list-table:: Ordered sets (:pd:`PD Tables 5.3 <x>` and :pd:`5.4 <x>`)
   :name: tab-usbpd-sop
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
     - Between the two ports
   * - SOP′
     - Sync-1
     - Sync-1
     - Sync-3
     - Sync-3
     - To or from the near cable plug
   * - SOP″
     - Sync-1
     - Sync-3
     - Sync-1
     - Sync-3
     - To or from the far cable plug
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

A receiver must accept an ordered set with all four K-codes correct, and may
accept one with three of the four correct (:pd:`Section 5.3.2.2`,
:pd:`Table 5.5 <x>`). The source (more precisely, the port supplying VCONN)
talks to the cable with SOP′ messages (:typec:`Section 4.9`); a port that has
not configured itself to receive SOP′ ignores those packets and does not
acknowledge them (:pd:`Section 5.3.2`, item 5).

**CRC.** The checksum is CRC-32 with polynomial 04C1 1DB7h, initial value
FFFF FFFFh, calculated bit 0 first over the header and data, and complemented
before sending; a receiver that runs the CRC over data and checksum together
gets the fixed remainder C704 DD7Bh (:pd:`Section 5.3.1.1.4`). It is the
same CRC as the Ethernet frame check sequence (:clause:`3`): the worked
example in :pd:`Figure 5.1`, a GoodCRC message with bytes 41h 02h, has the
checksum 46B5 0D97h, which is what a standard Ethernet/zlib CRC-32 routine
returns for those two bytes (checked with
`calc.py <https://github.com/mithro/evampire/blob/main/docs/power/usb-pd/calc.py>`__).

**End of packet (EOP).** A single EOP K-code, not covered by the CRC
(:pd:`Section 5.3.1.1.5`).

Message format
~~~~~~~~~~~~~~

Each message starts with a 16-bit header (:pd:`Section 6.2.1`,
:pd:`Table 6.2 <x>`; :numref:`fig-usbpd-header`). *Control* messages (for
example GoodCRC, Accept, PS_RDY, PR_Swap) consist of the header alone.
*Data* messages (for example Source_Capabilities, Request) add one to seven
32-bit data objects. *Extended* messages carry 1 to 260 bytes of data and are
needed only for optional features (all :pd:`Section 6.1.1`).

.. wavedrom::
   :caption: The 16-bit message header (:pd:`Table 6.2`). Bit 0 is on the
             right. PR is the power role and DR the data role of the sender.
   :name: fig-usbpd-header
   :alt: Bit-field diagram of the message header: bits 4 to 0 message type,
         bit 5 data role, bits 7 to 6 revision, bit 8 power role, bits 11
         to 9 MessageID, bits 14 to 12 number of data objects, bit 15
         extended.

   {"reg": [
     {"name": "Message type", "bits": 5, "attr": "e.g. 00001 GoodCRC"},
     {"name": "DR", "bits": 1},
     {"name": "Revision", "bits": 2, "attr": "10 = 3.x"},
     {"name": "PR", "bits": 1},
     {"name": "MessageID", "bits": 3},
     {"name": "Data objects", "bits": 3},
     {"name": "Ext", "bits": 1}
   ],
   "config": {"hspace": 700, "bits": 16, "lanes": 1}}

* **Message type** (bits 4 to 0): control messages include GoodCRC (00001),
  Accept (00011), Reject (00100), PS_RDY (00110), Get_Source_Cap (00111),
  Get_Sink_Cap (01000), DR_Swap (01001), PR_Swap (01010), VCONN_Swap
  (01011), Wait (01100), Soft_Reset (01101), Not_Supported (10000) and
  FR_Swap (10011) (:pd:`Table 6.4`). Data messages include Source_Capabilities
  (00001), Request (00010), Sink_Capabilities (00100), Alert (00110) and
  Vendor_Defined (01111), which carries the cable query (:pd:`Table 6.5`;
  see `Cables and VCONN`_).
* **MessageID** (bits 11 to 9): a 3-bit counter kept by the sender. A
  GoodCRC carries the MessageID of the message it acknowledges, and a
  receiver uses it to recognise a repeated message
  (:pd:`PD Sections 6.1.2 <x>` and :pd:`6.3.1 <x>`).
* **Number of data objects** (bits 14 to 12): zero for control messages.
* **Power role** (PR, bit 8: 1 = source) and **data role** (DR, bit 5:
  1 = DFP) of the sender, and the **specification revision** (bits 7 to 6),
  agreed from the first Source_Capabilities and Request
  (:pd:`Section 6.1.3.1`).

.. wavedrom::
   :caption: Fixed supply PDO (:pd:`PD Tables 6.8 <x>` and :pd:`6.10 <x>`),
             drawn as two rows of 16 bits. Bits 31 to 30 are 00 for a fixed supply.
   :name: fig-usbpd-pdo
   :alt: Bit-field diagram of the fixed supply PDO: bits 9 to 0 maximum
         current in 10 mA units, bits 19 to 10 voltage in 50 mV units,
         bits 21 to 20 peak current, bits 29 to 22 flags, bits 31 to 30
         type 00.

   {"reg": [
     {"name": "Max current (10 mA)", "bits": 10},
     {"name": "Voltage (50 mV)", "bits": 10},
     {"name": "Peak", "bits": 2},
     {"name": "Flags", "bits": 8},
     {"name": "00", "bits": 2}
   ],
   "config": {"hspace": 700, "bits": 32, "lanes": 2}}

.. wavedrom::
   :caption: Fixed supply RDO (:pd:`Table 6.19`), drawn as two rows of 16
             bits.
   :name: fig-usbpd-rdo
   :alt: Bit-field diagram of the fixed supply RDO: bits 9 to 0 maximum
         operating current, bits 19 to 10 operating current, both in 10 mA
         units, bits 21 to 20 reserved, bits 27 to 22 flags, bits 31 to 28
         object position.

   {"reg": [
     {"name": "Max op. current", "bits": 10},
     {"name": "Op. current (10 mA)", "bits": 10},
     {"name": "Resv", "bits": 2},
     {"name": "Flags", "bits": 6},
     {"name": "Position", "bits": 4}
   ],
   "config": {"hspace": 700, "bits": 32, "lanes": 2}}

:numref:`fig-usbpd-pdo` and :numref:`fig-usbpd-rdo` show the two words.
The first PDO is always 5 V, and its upper bits carry flags about the port,
including *Dual-Role Power* (bit 29), *Unconstrained Power* (bit 27) and,
in a sink's list, the current it needs during a fast role swap (bits 24 to
23) (:pd:`PD Tables 6.8 <x>` and :pd:`6.9 <x>`). In the RDO, bits 31 to 28
select a PDO by position (1 = the first) and bits 19 to 10 give the
*Operating Current*, the most the sink will draw. Bits 9 to 0, *Maximum
Operating Current*, are deprecated: a sender always sets them equal to the
Operating Current, and a receiver ignores them (:pd:`Table 6.19`). For example, an offer
of 9 V at 3 A has voltage field 9 V / 50 mV = 180 and current field
3 A / 10 mA = 300, giving the PDO ``0002 D12Ch``; a request for 2 A from the
second PDO is the RDO ``2003 20C8h``.

**How long a message takes on the wire.** The software timing budget depends
on how long the CPU is busy with each message. The packet length in bits,
from the parts listed above, is:

.. math::

   N_\text{bits} &= N_\text{pre} + N_\text{SOP} + N_\text{hdr} + 40\,n + N_\text{CRC} + N_\text{EOP} \\
                 &= 64 + 20 + 20 + 40\,n + 40 + 5 \\
                 &= 149 + 40\,n

where :math:`n` is the number of 32-bit data objects (0 to 7),
:math:`N_\text{pre}` = 64 preamble bits, :math:`N_\text{SOP}` = 4 symbols ×
5 bits = 20, :math:`N_\text{hdr}` = 4 nibbles × 5 bits = 20, each data object
is 8 nibbles × 5 bits = 40, :math:`N_\text{CRC}` = 8 nibbles × 5 bits = 40
and :math:`N_\text{EOP}` = 5 (:pd:`Section 5.3.1.1`;
:numref:`tab-usbpd-packet`). The duration is
:math:`N_\text{bits} \times T_\text{UI}` (:numref:`tab-usbpd-duration`):

.. list-table:: Packet duration
   :name: tab-usbpd-duration
   :header-rows: 1
   :widths: 40 15 20 25

   * - Message
     - Bits
     - At 300 kbit/s
     - At 270 kbit/s
   * - GoodCRC, Accept, PS_RDY, PR_Swap (n = 0)
     - 149
     - 149 × 3.333 µs = 497 µs
     - 149 × 3.704 µs = 552 µs
   * - Request (n = 1)
     - 189
     - 630 µs
     - 700 µs
   * - Source_Capabilities with seven PDOs (n = 7)
     - 429
     - 1430 µs
     - 1589 µs

The longest message a port normally has to handle lasts about 1.6 ms.

Negotiation and time limits
---------------------------

:numref:`fig-usbpd-negotiation` shows a complete negotiation, and
:numref:`tab-usbpd-timing` lists the time limits that apply to both roles.

.. _fig-usbpd-negotiation:

.. graphviz:: usb-pd/negotiation.dot
   :caption: A source and a sink negotiating a fixed 9 V supply. Each
             message that has a correct CRC is answered with GoodCRC. Either
             end can be a board built around evampire.
   :align: center

.. list-table:: Timing values for both roles (:pd:`Table 7.10` unless
   another source is given)
   :name: tab-usbpd-timing
   :header-rows: 1
   :widths: 24 20 56

   * - Name
     - Value
     - Meaning
   * - tTransmit
     - at most 195 µs
     - From the end of a received message's EOP to the start of the
       GoodCRC preamble (:pd:`Section 7.31.1`, :pd:`Table 7.10 <x>`).
   * - tInterFrameGap
     - at least 25 µs
     - Minimum gap before any transmission (:pd:`Table 5.10`).
   * - tReceive
     - 0.9 ms to 1.1 ms
     - How long a sender waits for GoodCRC (:pd:`Section 7.31.1`).
   * - tRetry, nRetryCount
     - at most 195 µs; 2
     - A message without GoodCRC is repeated within tRetry, at most twice
       (:pd:`Section 7.31.1`, :pd:`Table 7.12 <x>`).
   * - tReceiverResponse
     - at most 15 ms
     - From the GoodCRC of a message that needs an answer to the start of
       the answer (:pd:`Section 7.31.2`).
   * - tSenderResponse
     - 27 ms to 50 ms
     - How long the asking side waits for the answer (:pd:`Table 7.10`).
   * - tFirstSourceCap
     - at most 250 ms
     - Source: from VBUS reaching 5 V to the first Source_Capabilities
       (:pd:`Section 7.31.3.3`).
   * - tTypeCSendSourceCap
     - 100 ms to 200 ms
     - Source: interval for repeating Source_Capabilities until it is
       acknowledged, for *nCapsCount* (50) attempts (:pd:`Section 7.31.3.1`;
       :pd:`Table 7.12 <x>`).
   * - tTypeCSinkWaitCap
     - 310 ms to 620 ms
     - Sink: may send Hard Reset if no Source_Capabilities arrives
       (:pd:`Section 7.31.3.2`).
   * - tSrcTransition
     - at least 25 ms
     - Source: wait after Accept before changing the voltage
       (:pd:`Table 4.7`).
   * - tSrcTransReq
     - at most 325 ms (SPR)
     - Source: from the GoodCRC of Accept to the start of PS_RDY
       (:pd:`Table 4.7`).
   * - tPSTransition
     - 450 ms to 550 ms (SPR)
     - Sink: how long it waits for PS_RDY before Hard Reset
       (:pd:`PD Sections 7.31.5.1 <x>` and :pd:`9.2.4.8 <x>`).
   * - tSinkTx
     - 16 ms to 20 ms
     - Source: wait after changing Rp to "sink may not transmit" before
       starting its own exchange (:pd:`Section 7.31.13.1`).
   * - tSnkStdby
     - at most 15 ms
     - Sink: time to cut its current to iSnkStdby (500 mA) before a voltage
       change (:pd:`Table 4.8`).

**Acknowledgement.** Every correctly received message addressed to the port
must be answered with GoodCRC so that its first preamble bit starts between
25 µs and 195 µs after the last bit of the received EOP
(:numref:`fig-usbpd-goodcrc`; *tInterFrameGap*, :pd:`Section 5.3.4.9`;
*tTransmit*, :pd:`Section 7.31.1 <x>`). If the CRC is wrong, the message is
discarded silently.

.. wavedrom::
   :caption: Acknowledgement timing (not to scale). The GoodCRC preamble
             starts at least 25 µs (tInterFrameGap) and at most 195 µs
             (tTransmit) after the end of the received message.
   :name: fig-usbpd-goodcrc
   :alt: Timing diagram: a message from the sender, a gap, then a GoodCRC
         from the receiver; one row marks the minimum gap and another the
         latest start of the GoodCRC.

   {"signal": [
     {"name": "sender", "wave": "z=....z.......", "data": ["message"]},
     {"name": "receiver", "wave": "z.....z..=...z", "data": ["GoodCRC"]},
     {"name": "minimum gap", "wave": "x.....=..x....", "data": ["25 µs"]},
     {"name": "deadline", "wave": "x.....=.....x.", "data": ["195 µs"]}
   ],
   "config": {"hscale": 1}}

**Retries.** A sender that has not received GoodCRC within tReceive sends the
same message again within tRetry, up to twice, so each message is sent at
most three times (:pd:`Section 7.31.1`). After that it sends Soft_Reset
(:pd:`Section 7.31.8.1`), and a failing Soft_Reset leads to Hard Reset
(:pd:`Section 7.1.1`). A missed GoodCRC is therefore recovered
automatically as long as it does not happen three times in a row.

The source side
---------------

Switchable Rp
~~~~~~~~~~~~~

The level a source advertises with Rp is a promise about current at 5 V:

* **Before a contract**, the source must be able to supply the advertised
  current, and its first Source_Capabilities must offer at least that much at
  5 V (:typec:`Section 4.5.2.2.9.1`; :pd:`Section 3.2.1`, item 5). A board with
  little spare power advertises "default"; one that can spare 7.5 W or 15 W
  at 5 V advertises 1.5 A or 3.0 A.
* **During a contract**, the Rp value no longer means current. The source
  uses it to control who may start a message exchange: the 3.0 A value
  ("SinkTxOK") lets the sink start one, the 1.5 A value ("SinkTxNG") reserves
  the line for the source, which then waits *tSinkTx* (16 ms to 20 ms) before
  starting (:pd:`PD Sections 5.2.2 <x>`, :pd:`7.2 <x>` and
  :pd:`7.31.13.1 <x>`; :pd:`Table 5.1 <x>`).

A source therefore changes its Rp level during normal operation, and its Rp
circuit must provide at least the 1.5 A and 3.0 A levels whatever power it
offers. A current source suits an integrated circuit: the three currents
(80, 180 and 330 µA) can come from one reference and switchable current
mirrors, and the open-circuit voltage must rise above the 2.432 V "open"
threshold for the 3.0 A level. TI specifies its TPS65987D current sources as
73.6-86.4 µA, 165.6-194.4 µA and 303.6-356.4 µA, with the 3.0 A level valid
up to a CC voltage of 2.6 V ([USBPD-TPS65987D]_, Section 6.8).

Source sequence
~~~~~~~~~~~~~~~

After attach (Attached.SRC) the source:

#. turns VBUS on to *vSafe5V* (4.75 V to 5.5 V, :pd:`Table 4.9`) within
   tVBUSON (275 ms), supplies VCONN if needed (see `Cables and VCONN`_), and must not
   start messages until VBUS has reached vSafe5V
   (:typec:`Section 4.5.2.2.9.1`);
#. optionally queries the cable (required before offering more than 3 A or
   EPR voltages; see `Cables and VCONN`_);
#. sends Source_Capabilities within tFirstSourceCap (250 ms) and repeats it
   every 100 ms to 200 ms until it gets a GoodCRC (:pd:`Section 7.31.3`);
#. evaluates the Request (see below) and answers Accept or Reject within
   tReceiverResponse (15 ms);
#. after Accept, waits at least tSrcTransition (25 ms), changes the voltage
   at no more than 30 mV/µs (*vSrcSlewPos*, *vSrcSlewNeg*,
   :pd:`Table 4.7`), and sends PS_RDY within tSrcTransReq (325 ms in SPR) of
   the GoodCRC for Accept (:pd:`Section 4.5.1.1`; :pd:`Table 4.7 <x>`). The
   new voltage must be within ± 5 % of the offered value, plus 0.5 V while
   settling (*vSrcNew*, *vSrcValid*, :pd:`Table 4.7`).

The slew limit exists to limit the current that charges the sink's input
capacitors: :pd:`Table 4.7` states it is based on a 3 A connector rating
and at most 100 µF of sink capacitance. The source's own output capacitance
must be at least 10 µF (*cSrcBulk*, :pd:`Table 4.7`), while a dual-role port
that is not supplying VBUS may present at most 10 µF on VBUS
(:typec:`Table 4-2`), so the larger bulk capacitance has to sit behind the
source switch (see `Bidirectional VBUS power path and converter control`_).

Building the offer from the power budget
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The processor decides what to offer from the
:ref:`power budget <power-budget>`. The power it can offer on the USB port is
what the input grants, less what the board uses, less what the converter
loses:

.. math::

   P_\text{offer} = (P_\text{in} - P_\text{board}) \cdot \eta

where:

* :math:`P_\text{offer}` is the power offered on the USB port, in watts (the
  *Port Present PDP* in PD terms, :pd:`Section 3.2`);
* :math:`P_\text{in}` is the power granted on the input port, for example by
  Power over Ethernet (see :doc:`poe`);
* :math:`P_\text{board}` is the power the board itself uses;
* :math:`\eta` is the efficiency of the USB source converter.

*Example with assumed numbers* (none of them is a design value): with
:math:`P_\text{in}` = 25 W, :math:`P_\text{board}` = 5 W and
:math:`\eta` = 0.90,

.. math::

   P_\text{offer} &= (25\ \text{W} - 5\ \text{W}) \times 0.90 \\
                  &= 20\ \text{W} \times 0.90 = 18\ \text{W}

For a source rated between 15 W and 27 W, :pd:`Table 3.1` requires a 5 V
offer of 3 A and a 9 V offer of :math:`P_\text{offer} / 9\ \text{V}`; here
:math:`18\ \text{W} / 9\ \text{V} = 2.00\ \text{A}`. Currents are rounded
to 10 mA (:pd:`Section 3.2.1`, item 1). So the Source_Capabilities message
lists "5 V 3 A" and "9 V 2 A". Other rules shape the list: the first PDO is
always 5 V (:pd:`Section 6.4.1.1`); no fixed PDO may offer more power (its
voltage times its maximum current) than a fixed PDO of higher voltage in the
same list (:pd:`Section 3.2.1`, item 2); and currents above 3 A need a 5 A
cable (:pd:`Section 8.6.1.2.2`). A port with nothing to offer sends a single
"5 V 0 A" PDO (:pd:`Section 7.9.1.5`).

**Evaluating the request.** The source checks that the requested object
exists and that the requested current does not exceed the offered maximum,
then answers Accept, Reject or Wait (:pd:`Section 6.4.2`; :pd:`Table 6.19 <x>`).

**Changing the offer.** When the input power changes, the processor sends new
Source_Capabilities and the sink must request again. When lowering the offer,
the source should first send an Alert message, up to *tReducePowerAlert*
(2.0 s to 2.4 s) before the reduced capabilities (:pd:`Section 6.4.5.5`;
:pd:`Table 4.7 <x>`). If the input drops faster than that, the source's own
over-current protection (`Current limit and over-current response`_) or a
Hard Reset (`Hard Reset in each role`_) is the remaining option, so the
:ref:`power budget <power-budget>` should keep a margin.

Current limit and over-current response
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A source must have over-current protection that does not trip within the
contract, should send Hard Reset (and later an Alert) when it trips, and,
when it shuts down a port above 5 V, must bring VBUS down to vSafe5V within
*tSafe5V* (275 ms) and to vSafe0V within *tSafe0V* (650 ms)
(:pd:`Section 4.1.5.1`; :pd:`Table 4.9 <x>`). The current limit is part of
the source power path (see
`Bidirectional VBUS power path and converter control`_). For example, TPS65987D has a firmware-selectable over-current clamp with 20
settings from 1.267 A to 6.33 A (typical) and a fast-acting limit of about
10 A ([USBPD-TPS65987D]_, Section 6.7).

Discharging VBUS
~~~~~~~~~~~~~~~~

A source must bring VBUS to vSafe0V within tSafe0V (650 ms) after detach,
and to below vSafe5V (max) within tSafe5V (275 ms) (:pd:`Section 4.1.5.5`).
It must also discharge VBUS before attaching (AttachWait.SRC,
:typec:`Section 4.5.2.2.8.1`) and during a role swap. A switched load from
VBUS to ground, controlled by the processor, does this (see
`VBUS sensing and discharge`_).

The sink side
-------------

A sink presents Rd, waits for VBUS and Source_Capabilities, chooses a PDO,
sends Request within tReceiverResponse (15 ms), and after Accept cuts its
current to *iSnkStdby* (500 mA) within *tSnkStdby* (15 ms) until PS_RDY
arrives (:pd:`Section 4.5.1.1`; :pd:`Table 4.8 <x>`). A sink that uses the
1.5 A or 3.0 A Rp level before a contract must follow changes of Rp within *tSinkAdj*
(60 ms, :typec:`Table 4-32`). During a contract it must check the Rp level
before starting an exchange of its own (:pd:`Section 7.2`). A sink should
tolerate up to 24 V on VBUS without damage (*vSprMax*, :pd:`Table 4.8`).

A slow sink does not miss the negotiation: the source repeats
Source_Capabilities 50 times. The sink may send Hard Reset after
tTypeCSinkWaitCap to restart the source, but a board powered only from VBUS
should avoid this, because the source answers a Hard Reset by switching VBUS
off (see `Hard Reset in each role`_).

Cables and VCONN
----------------

**Why the source checks the cable.** Every standard USB Type-C cable is
rated for at least 3 A at voltages above 5 V (:pd:`Section 8.6.1.2.2`).
Cables rated for more than 3 A, and all EPR cables, are electronically marked
(:typec:`Type-C Sections 3.4.1.1 <x>`, :typec:`3.4.2.1 <x>` and
:typec:`3.11.2 <x>`). A source that can offer more than 3 A must query the
cable and limit its offer to what the cable supports; an EPR source must
check that the cable supports EPR (:pd:`PD Sections 8.6.1.2.2 <x>` and
:pd:`8.6.1.2.3 <x>`). A port that can be a source offering more than 3 A must
therefore support the *Discover Identity* query (:pd:`Section 7.5`,
applicability table).

**How the query works.** The query is a Vendor_Defined message, *Discover
Identity*, sent with the SOP′ ordered set to the near cable plug. The
e-marker answers with its identity and a *cable VDO* (vendor data object), a
32-bit word whose fields
include the maximum VBUS voltage (20 V or 50 V) and the VBUS current
capability (3 A or 5 A) (:pd:`Table 6.45`). If there is no GoodCRC, the source
repeats the query every *tDiscoverIdentity* (40 ms to 50 ms) and gives up
after *nDiscoverIdentityCount* (20) attempts (:pd:`Section 7.31.12.4`;
:pd:`Tables 7.10 <x>` and :pd:`7.12 <x>`). Before a contract any source may
talk to the cable; after one, only the port supplying VCONN may
(:typec:`Section 4.9`).

**VCONN power.** The e-marker is powered by VCONN, which the source supplies
on the CC pin not connected to the CC wire (the pin showing Ra, or
unconditionally on the unused pin) within *tVCONNON* (2 ms) of VBUS reaching
5 V (:typec:`Section 4.5.2.2.9.1`; :typec:`Table 4-32 <x>`). How much VCONN
power is required depends on what the port does (:typec:`Table 4-4`;
:numref:`tab-usbpd-vconn`):

.. list-table:: VCONN requirements relevant to evampire
   (:typec:`Type-C Tables 4-4 <x>` to :typec:`4-6 <x>`)
   :name: tab-usbpd-vconn
   :header-rows: 1
   :widths: 40 60

   * - Situation
     - Requirement
   * - No USB data, offering 3 A or less
     - VCONN not required.
   * - No USB data, offering more than 3 A
     - Source at least 100 mW; may be switched off after reading the cable's
       rating.
   * - VCONN voltage
     - 3.0 V to 5.5 V (*vVCONNValid*).
   * - Load presented by a passive e-marked cable
     - At most 20 mW (75 mW briefly after VCONN is applied) and at most
       10 µF of inrush capacitance.
   * - Discharge after detach
     - Resistance *Rdch* of 30 Ω to 6120 Ω on the VCONN pin until it is
       below 0.8 V (:typec:`Section 4.5.2.2.6`; :typec:`Table 4-5 <x>`).

*How much current the VCONN switch must pass.* The switch has to charge the
cable's capacitance to the minimum valid VCONN voltage within tVCONNON.
Assuming a constant charging current (a current-limited switch behaves this
way), the current needed is:

.. math::

   I_\text{inrush} &= \frac{C_\text{cable} \cdot V_\text{min}}{t_\text{on}}
                    = \frac{10\ \mu\text{F} \times 3.0\ \text{V}}{2\ \text{ms}} \\
                   &= \frac{30\ \mu\text{C}}{2\ \text{ms}}
                    = 15\ \text{mA}

where :math:`C_\text{cable}` = 10 µF is the largest inrush capacitance a cable
may present (:typec:`Table 4-6`), :math:`V_\text{min}` = 3.0 V is the minimum
valid VCONN (:typec:`Table 4-5`) and :math:`t_\text{on}` = 2 ms is tVCONNON
(:typec:`Table 4-32`). The source must also be able to supply 100 mW
continuously (:typec:`Table 4-4`), which is
:math:`0.1\ \text{W} / 5\ \text{V} = 20\ \text{mA}` at 5 V, or
:math:`0.1\ \text{W} / 3.0\ \text{V} = 33\ \text{mA}` at the lowest valid
VCONN. A VCONN switch with a current limit of a few tens of milliamps
therefore meets the requirement for a port without USB data; commercial
controllers, which also serve USB data cables needing 1 W to 1.5 W
(:typec:`Tables 4-4 <x>` and :typec:`4-5 <x>`), have
limits of hundreds of milliamps (TPS65987D *ILIMPPCC* 0.6-0.9 A,
[USBPD-TPS65987D]_, Section 6.7; STUSB1602 programmable 100 mA to 600 mA,
[USBPD-STUSB1602]_, features; CCG5C over-current detection from 550 mA,
[USBPD-CCG5C]_, SID.DC.20VCONN.9).

**VCONN swap.** The two ports can exchange the VCONN duty with a VCONN_Swap
message exchange, done make-before-break (:typec:`Section 4.5.2.2.9.1`;
:pd:`Section 7.13`). A port that cannot supply VCONN answers Reject or
Not_Supported; the port currently supplying VCONN may not reject
(:pd:`Section 7.13`). After a power role swap, the port that was supplying
VCONN keeps supplying it, because a power role swap does not move VCONN
(:pd:`Section 7.10`; :typec:`Table 4-13`).

Role changes
------------

Power role swap
~~~~~~~~~~~~~~~

Either port can ask to swap power roles with a PR_Swap message; the other
answers Accept, Reject or Wait (:pd:`Section 7.10`). Data roles and the VCONN
duty do not change (:typec:`Table 4-13`). :numref:`fig-usbpd-prswap` shows the
sequence and :numref:`tab-usbpd-prswap` its time limits.

.. _fig-usbpd-prswap:

.. graphviz:: usb-pd/pr-swap.dot
   :caption: Power role swap (:pd:`Section 4.3.3`, :pd:`Figure 4.14 <x>`;
             :pd:`Section 7.10 <x>`). The initial sink asks in this example; the sequence after Accept
             is the same when the initial source asks.
   :align: center

.. list-table:: Power role swap timing (:pd:`PD Tables 4.7 <x>`,
   :pd:`4.8 <x>`, :pd:`7.10 <x>`)
   :name: tab-usbpd-prswap
   :header-rows: 1
   :widths: 25 20 55

   * - Name
     - Value
     - Meaning
   * - tSnkSwapStdby, iSnkSwapStdby
     - at most 15 ms; at most 2.5 mA
     - Initial sink: time to cut its VBUS current, and the current allowed
       until the new source has VBUS up.
   * - tSrcSwapStdby
     - at most 650 ms
     - Initial source: time to discharge VBUS to vSafe0V after
       tSrcTransition.
   * - tSrcTransOff
     - at most 690 ms
     - Initial source: from the GoodCRC for Accept to the start of its
       PS_RDY.
   * - tPSSourceOff
     - 750 ms to 920 ms
     - Initial sink: gives up waiting for that PS_RDY.
   * - tNewSrc
     - at most 275 ms
     - Initial sink: time to start operating as a source.
   * - tSrcTransOn
     - at most 280 ms
     - New source: from the GoodCRC of the first PS_RDY to the start of its
       own PS_RDY, with VBUS at vSafe5V.
   * - tPSSourceOn
     - 390 ms to 480 ms
     - New sink: gives up waiting for that PS_RDY.
   * - tSwapSourceStart
     - at least 20 ms
     - New source: wait before its first Source_Capabilities.

The VBUS slew-rate limit does not apply when VBUS is switched off or on as
part of a swap (:pd:`Section 4.1.4`). During the swap VBUS falls below 5 V
but the initial sink must not treat this as a detach (:pd:`Section 7.10`).

**When the swap fails.** If the expected PS_RDY does not arrive in time
(tPSSourceOff or tPSSourceOn), the port goes to Type-C `ErrorRecovery`_
(:pd:`PD Sections 7.31.5.2 <x>` and :pd:`7.31.5.3 <x>`): it removes its
terminations, both ports see a detach, and attach starts again. If the board was running from VBUS at that
moment it loses power.

**Effect on the power budget.** After a swap the board's input and output
change places. The processor must update the
:ref:`power budget <power-budget>`, and, if the board now sources power,
offer only what the new input allows (see
`Building the offer from the power budget`_).

Data role swap
~~~~~~~~~~~~~~

A DR_Swap message exchange swaps the data roles (DFP and UFP) and nothing
else: VBUS, Rp/Rd and VCONN stay as they are (:pd:`Section 7.12.1`;
:typec:`Table 4-13`). A board without USB data can answer Reject or
Not_Supported. Data role matters to evampire mainly because it decides which port may send certain
messages and because the data-role bit must be correct in every header.

Fast role swap
~~~~~~~~~~~~~~

A *fast role swap* (FRS) is a power role swap that happens without first
exchanging messages, to keep power flowing when the source suddenly loses
its own supply. It is designed for charge-through accessories, such as a hub
that powers a laptop from a wall supply and must let the laptop take over
when the wall supply is removed (:pd:`Section 10.1`).

*Signalling.* The initial source, on losing its supply, pulls the CC wire
below *vFRSwapCableTx* (490 mV to 550 mV) through at most *rFRSwapTx* (5 Ω)
for *tFRSwapTx* (60 µs to 120 µs). The initial sink recognises a low lasting
*tFRSwapRx* (30 µs to 50 µs), stops drawing current, and must be supplying
VBUS at vSafe5V within *tSrcFRSwap* (150 µs) of VBUS falling to vSafe5V; the
FR_Swap, Accept and PS_RDY messages follow (:pd:`PD Sections 10.4 <x>` and
:pd:`10.4.1 <x>`; :pd:`Table 10.2 <x>`). A BMC low never lasts longer than
1 UI (3.7 µs, see `Bit rate`_), so a low of
30 µs cannot be part of a message. During a contract the idle level is set by
the 1.5 A or 3.0 A Rp (about 0.9 V or 1.7 V), above the FRS threshold, so the
signal is unambiguous.

*Is it needed for evampire?* The case where it would apply is a board that
sources power to a laptop from Power over Ethernet and loses the Ethernet
supply. With FRS the laptop could take over and keep the board running. FRS
only works if the laptop supports it and was initialised for it after
reading the board's sink capabilities, and the board must then run on at most
15 W at 5 V (:pd:`Section 10.1`). Without FRS, the board loses power with its
Ethernet supply, which is acceptable if the board does not need to stay up.
This is an open decision (see `Open design decisions`_).

*Analog needs.* As the side that signals: a strong pull-down (at most 5 Ω) on
each CC pin and enough stored energy to keep the board alive for the swap
(*tSnkFRSwap*, 200 µs, :pd:`Table 10.2`, plus the message exchange). As the side that
receives: a comparator at about 0.52 V on the CC pin, a timer to measure the
30 µs low, and a source converter that can deliver 5 V within 150 µs, which
means it must already be running. TPS65987D, for example, specifies a VBUS
turn-on time of 150 µs for this case (*tON_FRS*, [USBPD-TPS65987D]_,
Section 6.7) and an FRS detection threshold of 490-550 mV (*VTH_FRS*,
Section 6.8).

Hard Reset in each role
~~~~~~~~~~~~~~~~~~~~~~~

A Hard Reset returns both power supplies to their default state; it does not
change Rp and Rd, so the power roles after a swap are kept, and it changes
data roles back to DFP for the Rp side and UFP for the Rd side
(:pd:`Section 7.1.3`).

* **As source:** the port drives VBUS to vSafe0V, starting *tPSHardReset*
  (25 ms to 35 ms) after the Hard Reset, waits *tSrcRecover* (0.66 s to
  1.0 s in SPR), then restores 5 V and VCONN (:pd:`Section 4.4`;
  :pd:`Tables 4.7 <x>` and :pd:`7.10 <x>`). If the board is powered from Ethernet it stays up; only the USB
  output is interrupted.
* **As sink:** VBUS goes to 0 V and back to 5 V. A sink powered only from
  VBUS loses power: a Hard Reset is a full power cycle of the board. It
  should draw no more than *iSafe0mA* (1 mA) while VBUS is at vSafe0V
  (:pd:`Table 4.8`).

Two ports
---------

In the :ref:`full design <power-board-configs>` the board has two dual-role
USB Type-C ports. This changes:

* **Roles.** One port can sink while the other sources, which makes the board
  a USB-to-USB power bridge as well as a USB-to-Ethernet one. The
  :ref:`power budget <power-budget>` then has two outputs sharing one input,
  or one USB input feeding a USB output and Ethernet.
* **Budget.** The offers on both outputs together must fit the budget. When
  a second device attaches, the processor may have to lower the first port's
  offer, with the Alert and new Source_Capabilities described in
  `Building the offer from the power budget`_. PD calls this a *Managed
  Capability Port* (:pd:`Section 3.2.3`).
* **Analog circuits.** Each port needs its own CC front end: both ports must
  present terminations and detect attach at the same time, and messages on
  the two ports arrive independently. Only slow measurements (attach levels,
  VBUS level) can share one comparator or ADC through a multiplexer.
* **Processor time.** Two negotiations can overlap. See
  `Two ports in software`_.

Implementing USB Power Delivery in software
-------------------------------------------

The :ref:`requirement <requirements>` is that USB Power Delivery runs mostly
in software on the RISC-V processor, with dedicated digital hardware only
where software cannot meet the timing. This section starts from the absolute
minimum hardware, works out what software then has to do and how fast, and
adds a helper only where the numbers show software is not enough.

Baseline: analog front end and plain input and output bits
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The minimum hardware per port is the analog front end described in
`Analog blocks`_ (:numref:`fig-usbpd-port-blocks`: switchable Rp, Rd and
dead-battery Rd, VCONN switch, comparators, BMC driver) connected to plain
processor-visible bits:

* outputs: Rp level and enable, Rd enable, VCONN enable per CC pin, driver
  enable and driver data, comparator threshold selection;
* inputs: the comparator outputs.

Everything else is firmware: BMC encoding and decoding, 4b5b, CRC-32, SOP
detection, GoodCRC generation, retries, all timers, the Type-C attach,
toggling, Try.SRC and Try.SNK state machines, and the PD protocol and policy
including power role swap, source capabilities and cable discovery.

The time scales are very different (:numref:`tab-usbpd-timescales`):

.. list-table:: Time scales of the work
   :name: tab-usbpd-timescales
   :header-rows: 1
   :widths: 30 25 45

   * - Task
     - Time scale
     - Difficulty in software
   * - Bit timing (receive and transmit)
     - 1.5 µs between edges; ± 50 ns edge placement
     - Hard; analysed below
   * - GoodCRC reply
     - 25 µs to 195 µs after a message
     - Moderate; analysed below
   * - FRS detection (if supported)
     - 30 µs to 50 µs
     - Moderate
   * - Protocol replies, attach, toggling, swaps
     - 15 ms and longer
     - Easy

The processor clock
~~~~~~~~~~~~~~~~~~~

The numbers below depend on the processor's clock and on how many clock
cycles it needs per instruction (*CPI*). Neither is fixed yet, so two cases
are used:

* a **multi-cycle core** such as PicoRV32, with an average CPI of about 4
  (load 5 cycles, taken branch 5 to 6, simple ALU 3; [USBPD-PICORV32]_, CPI
  table);
* a **pipelined core**, assumed here to reach a CPI of about 1.3 on this kind
  of code (an assumption, not a measured value).

For the clock, evampire already has a 125 MHz reference
(:ref:`clock <arch-clock>`), so 31.25 MHz (÷ 4) and 62.5 MHz (÷ 2) are
natural choices. The gf180mcu 7-track standard cell library, at its typical
corner (5 V, 25 °C), gives a D flip-flop clock-to-output delay of 0.676 ns
(with the minimum load) and a setup time of 0.229 ns ([USBPD-GF180-SC]_, cell
gf180mcu_fd_sc_mcu7t5v0__dffq_1 and databook conditions page). At 50 MHz that
leaves :math:`20\ \text{ns} - (0.676 + 0.229)\ \text{ns} = 19.1\ \text{ns}`
per clock for logic and wiring. How many gate levels fit in that depends on
the core and the layout and is not derived here; as an order of magnitude,
the PicoRV32-based "Raven" chip, made in a different 180 nm process (X-FAB
XH018), was reported to run at 100 MHz [USBPD-RAVEN]_. This page uses
**50 MHz as a working assumption** and shows how the results change with the
clock.

Receive by polling
~~~~~~~~~~~~~~~~~~

With only a plain input bit, the processor reads the comparator in a loop,
notes the time of each change with the cycle counter, and decodes as it
goes.

*How often it must sample.* The decoder tells a ``0`` (an interval of 1 UI)
from half of a ``1`` (0.5 UI) by comparing each interval with 0.75 UI. Each
edge can be up to 0.07 UI from its ideal time (receive mask, :pd:`Table 5.8`),
so an interval can be off by up to :math:`2 \times 0.07 = 0.14` UI. That
leaves a margin of :math:`0.25 - 0.14 = 0.11` UI, which at the fastest rate
(`Bit rate`_) is :math:`0.11 \times 3.030\ \mu\text{s} = 333\ \text{ns}`. The
sampling period adds up to one period of error to each interval, so it must
be shorter than about 333 ns. This page uses :math:`T_\text{poll}` = 250 ns,
4 million samples per second. The number of samples per bit is then:

.. math::

   N_\text{poll} = \frac{T_\text{UI,min}}{T_\text{poll}}
                 = \frac{3.030\ \mu\text{s}}{0.250\ \mu\text{s}}
                 = 12.1 \approx 12

*How many instructions per bit.* These counts
(:numref:`tab-usbpd-poll-instr`) are **estimates** for hand-written RV32I
assembly (RV32I is the 32-bit base RISC-V instruction set), not
measurements. The poll itself is two instructions: a load of the input word
and a compare-and-branch back to the load while the value is unchanged.

.. list-table:: Estimated instructions for receiving one bit by polling
   :name: tab-usbpd-poll-instr
   :header-rows: 1
   :widths: 40 15 15 30

   * - Work
     - Instructions each
     - Times per bit
     - Instructions per bit
   * - Poll: load input, compare-and-branch
     - 2
     - 12
     - 24
   * - Edge: read cycle counter, subtract, compare with 0.75 UI, update state
     - 10
     - 2 (worst case, a ``1``)
     - 20
   * - Bit: shift into symbol, count
     - 4
     - 1
     - 4
   * - Symbol: 4b5b table lookup and CRC-32 nibble update
     - 16
     - 1/5
     - 3.2
   * - **Total**
     -
     -
     - **51.2**

The instruction rate and clock needed are then:

.. math::

   R_\text{instr} &= N_\text{instr/bit} \cdot f_\text{bit,max} \\
                  &= 51.2 \times 330\,000\ \text{s}^{-1}
                   = 16.9 \times 10^{6}\ \text{s}^{-1}

.. math::

   f_\text{clk} = R_\text{instr} \cdot \text{CPI}

where :math:`R_\text{instr}` is the instruction rate,
:math:`N_\text{instr/bit}` = 51.2 (estimate above), :math:`f_\text{bit,max}`
= 330 kbit/s (:pd:`Table 5.9`) and CPI is cycles per instruction. With CPI
1.3, :math:`f_\text{clk} = 16.9 \times 1.3 = 22` MHz; with CPI 4,
:math:`16.9 \times 4 = 68` MHz.

Polling also has a fixed cost per sample regardless of edges: a multi-cycle
core needs about 10 cycles per poll iteration (load 5 + taken branch 5,
[USBPD-PICORV32]_), so 4 million polls per second alone take 40 MHz; a
pipelined core needing about 4 cycles per iteration (an estimate) takes
16 MHz.

*What this means.* On a pipelined core at 50 MHz, polled receive fits, using
about :math:`22 / 50 = 44\ \%` of the processor while a message is on the
wire. On a multi-cycle core at 62.5 MHz or below it does not fit (68 MHz
needed). In both cases interrupts must be off for the whole message, because
any interrupt longer than about 333 ns corrupts the timing.

Receive by interrupt on each edge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An interrupt per comparator edge avoids polling between edges. The worst case
is a run of ``1`` bits, two edges per UI:
:math:`2 \times 330\,000 = 660\,000` edges per second. If entering and
leaving the interrupt and handling the edge costs 40 to 60 cycles (an
**estimate** for saving and restoring a few registers on a small core), the
load is :math:`660\,000 \times 40 = 26.4` to
:math:`660\,000 \times 60 = 39.6` million cycles per second, and the timestamp
is only as accurate as the interrupt latency. This is worse than polling and
is not considered further.

Transmit by cycle-counted output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To transmit, the processor computes the next edge time, waits in a loop on
the cycle counter, and writes the output bit. The edge is late by up to one
loop iteration, so the timing uncertainty (peak to peak) is:

.. math::

   \Delta t_\text{edge} = \frac{N_\text{loop}}{f_\text{clk}}

where :math:`N_\text{loop}` is the number of cycles in one iteration of the
wait loop (read counter, compare-and-branch) and :math:`f_\text{clk}` is the
core clock. **Estimates** of :math:`N_\text{loop}`: about 4 cycles on a
pipelined core and about 12 on a multi-cycle core
(:numref:`tab-usbpd-tx-jitter`).

.. list-table:: Transmit edge uncertainty (peak to peak) against the ± 50 ns
   reading of the mask
   :name: tab-usbpd-tx-jitter
   :header-rows: 1
   :widths: 25 25 25 25

   * - Core clock
     - Pipelined (4 cycles)
     - Multi-cycle (12 cycles)
     - Meets ± 50 ns?
   * - 31.25 MHz
     - 4 / 31.25 MHz = 128 ns
     - 12 / 31.25 MHz = 384 ns
     - No / No
   * - 50 MHz
     - 80 ns
     - 240 ns
     - Yes, barely / No
   * - 62.5 MHz
     - 64 ns
     - 192 ns
     - Yes / No

Measuring edge time from the cycle counter, rather than counting loop
iterations, keeps the average bit rate exact, so the 0.25 % drift limit is not
a problem. The ± 50 ns edge placement is.

The GoodCRC deadline
~~~~~~~~~~~~~~~~~~~~

After the EOP of a received message the processor must start sending GoodCRC
between 25 µs and 195 µs later. With the CRC updated nibble by nibble during
reception (included in the receive estimate above), checking it at the EOP is
one comparison with the fixed remainder. The GoodCRC packet for each of the
eight MessageID values, including its own CRC, can be prepared in advance. So
the work after the EOP is a few tens of instructions, about 1 µs, plus the
25 µs wait. The deadline is met as long as interrupts stay off from the start
of the message to the end of the GoodCRC. As source and as sink the deadline
is the same; no source-side timing is tighter than this (the next tightest is
`Fast role swap`_ detection, 30 µs to 50 µs, and then the millisecond
limits).

What the processor cannot do during a message
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With polled receive and cycle-counted transmit, the processor is fully busy
from the first preamble edge of a received message to the end of its
GoodCRC. The worst case is a seven-object message at the slowest bit rate:

.. math::

   t_\text{busy} &= t_\text{msg} + t_\text{gap} + t_\text{GoodCRC} \\
                 &= 1589\ \mu\text{s} + 195\ \mu\text{s} + 552\ \mu\text{s}
                  = 2336\ \mu\text{s}

where :math:`t_\text{msg}` = 429 bits × 3.704 µs
(:numref:`tab-usbpd-duration`), :math:`t_\text{gap}` = 195 µs is the longest
allowed gap (tTransmit, :pd:`Section 7.31.1`) and :math:`t_\text{GoodCRC}` =
149 bits × 3.704 µs.

During those 2.3 ms the processor cannot service the Ethernet frame buffers
or the transceiver :ref:`configuration interface <arch-config-interface>`
(the management interface of :clause:`22`). The forwarding path between the
Ethernet ports is entirely hardware and is not affected (see
:doc:`../architecture/index`). Frames for the processor wait in the receive
buffer, which holds one or two frames; at the processor's expected traffic of
well below 1 Mbit/s (:ref:`requirements`), a full-size 1522-byte frame
arrives on average no more often than every
:math:`1522 \times 8\ \text{bit} / 1\ \text{Mbit/s} = 12.2\ \text{ms}`, so a
2.3 ms pause rarely loses a frame, and a lost frame is resent by higher-level
protocols. A burst of frames during a USB message can be lost.

Two ports in software
~~~~~~~~~~~~~~~~~~~~~

With two ports, messages on both can arrive at the same time: as a sink the
port cannot control when the other side transmits, and even as a source the
other side may transmit when Rp allows it. A single polling loop could read
both comparators in one input word, but the per-edge work doubles: the
24 poll instructions plus twice the 27.2 instructions of edge, bit and symbol
work, :math:`24 + 2 \times 27.2 = 78.4` instructions per bit, or
:math:`78.4 \times 330\,000 = 25.9` million instructions per second
(estimate). Transmitting on one port while receiving on the other is not
possible with a cycle-counted transmit loop. In practice software serves one
port at a time; a message lost on the other port is resent by its sender up
to twice (tReceive, then tRetry), so an occasional collision costs about
1 ms, and three losses in a row lead to a Soft_Reset.

Hardware helpers, in order of need
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From the numbers above, whether a digital helper is needed depends on the
processor core, which is not yet chosen:

1. **Transmit edge timing** cannot be met on a multi-cycle core at any clock
   up to 62.5 MHz, nor on a pipelined core below about 50 MHz
   (:numref:`tab-usbpd-tx-jitter`). A **timer compare output** (a counter, a
   compare register and an output bit that changes when they match) places
   each edge to one clock period (16 ns to 32 ns at 62.5 MHz to 31.25 MHz)
   whatever the processor is doing. Software loads the next edge time after
   each edge, 1.5 µs ahead. This is a generic microcontroller timer feature,
   not USB-specific.
2. **Receive timing** cannot be met by polling on a multi-cycle core at
   62.5 MHz or below. A **timer capture input** (the counter value latched
   into a small FIFO on each comparator edge) removes polling. Per bit,
   software then reads up to two timestamps (about 12 instructions each with
   the classification) plus the bit and symbol work:
   :math:`2 \times 12 + 4 + 3.2 = 31.2` instructions per bit, or
   :math:`31.2 \times 330\,000 = 10.3` million per second (estimate): 13 MHz
   at CPI 1.3, 41 MHz at CPI 4. Interrupts can stay on as long as the FIFO
   does not overflow: at one edge per 1.515 µs, a FIFO of 8, 16 or 32 entries
   gives :math:`8 \times 1.515 = 12.1`, 24.2 or 48.5 µs of tolerance to
   interrupt latency. This too is a generic timer feature.
3. **CRC-32** is not needed in hardware: a 16-entry table (64 bytes of
   read-only memory) and about 6 instructions per nibble are included in the
   estimates above. The RISC-V carry-less multiply instructions of the Zbc
   bit-manipulation extension (https://github.com/riscv/riscv-bitmanip) could
   speed it up but are not needed.
4. **USB-specific helpers** (a BMC decoder, automatic GoodCRC as in the onsemi
   FUSB302B [USBPD-FUSB302B]_, or a BMC transceiver as in the STUSB1602
   [USBPD-STUSB1602]_, which decodes BMC and hands the bits to a
   microcontroller over a serial interface) are not required by the numbers
   above for one port.

Recommended split
~~~~~~~~~~~~~~~~~

* **Hardware, per port:** the analog front end (switchable Rp, Rd and
  dead-battery Rd, VCONN switch with current limit, comparators with
  selectable thresholds, BMC driver with controlled edges), connected to
  plain processor-visible input and output bits.
* **Software:** everything else, including BMC, 4b5b, CRC, GoodCRC, retries,
  the attach and toggling state machines, the protocol, cable discovery,
  power role swap and the :ref:`power budget <power-budget>`.
* **Digital helpers:** none, if the processor is a pipelined core running at
  50 MHz or faster. If it is a multi-cycle core, or runs slower, the
  arithmetic above shows that one timer compare output (for transmit) and
  one timer capture input with a FIFO (for receive) per port are needed;
  both are generic timer features.

With no helper, interrupts are disabled for up to 2.3 ms per message, and two
ports rely on retries when their messages overlap. Adding the timer channels
anyway, to remove these limits, is listed as an option under
`Open design decisions`_.

Analog blocks
-------------

:numref:`fig-usbpd-port-blocks` shows the circuits for one port.

.. _fig-usbpd-port-blocks:

.. graphviz:: usb-pd/port-blocks.dot
   :caption: Circuits for one dual-role USB Type-C port with the minimum
             dedicated hardware. Solid arrows carry signals and dashed
             arrows carry control. The connector-side blocks may be on chip
             or on the board (see the sections below). The VBUS power
             connections, and the processor's control of the VBUS-side
             blocks, are not drawn.
   :align: center

Each block below lists the requirement, how commercial controllers implement
it, and the options for evampire. Everything is per port; the
:ref:`full design <power-board-configs>` has two of each. The commercial
examples are TI TPS65987D [USBPD-TPS65987D]_ (dual-role controller with
integrated power paths), TI TPS25750 [USBPD-TPS25750]_, onsemi FUSB302B
[USBPD-FUSB302B]_ (a physical-layer device, or PHY, see
:doc:`../overview`, controlled by an external processor, which can toggle as a dual-role port),
ST STUSB1602 [USBPD-STUSB1602]_ (source, sink or dual-role, with a BMC line
driver for an external microcontroller), Infineon CCG5C [USBPD-CCG5C]_
(dual-role controller with an Arm Cortex-M0) and Infineon CYPD3177
[USBPD-CYPD3177]_ (sink only).

Whether a block is built on evampire or with external parts is decided per
block. Where the standard gf180mcu devices are not rated for the voltage,
that means a custom structure is needed, not that the block cannot be on
chip; `Limits of the gf180mcu process`_ sets out what is documented.

Rp current sources
~~~~~~~~~~~~~~~~~~

*Requirement.* Per CC pin, a pull-up of 80 µA, 180 µA or 330 µA (or the
equivalent resistors), switchable off (:typec:`Table 4-27`).

*Commercial practice.* Current sources: TPS65987D 73.6-86.4 / 165.6-194.4 /
303.6-356.4 µA ([USBPD-TPS65987D]_, Section 6.8); FUSB302B 64-96 / 166-194 /
304-356 µA ([USBPD-FUSB302B]_, Table 10); CCG5C integrates current sources for
all three levels ([USBPD-CCG5C]_, features).

*On evampire.* Switchable current mirrors from a reference current, supplied
from 3.3 V or 5 V so that the open-circuit voltage exceeds the 2.432 V "open"
threshold of the 3.0 A level. The normal CC voltages (at most 5.5 V) are
within the rating of the `standard 5 V and 6 V devices <Limits of the gf180mcu process_>`_.

Switchable Rd and dead-battery Rd
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Requirement.* 5.1 kΩ to ground on both CC pins, ± 10 % to read the Rp
level, switchable off to at least 126 kΩ (:typec:`Type-C Tables 4-28 <x>`
and :typec:`4-30 <x>`), and present without any supply. Unpowered, the pin
may rise to at most 2.18 V with a ± 20 % Rd (:typec:`Table 4-28`): for
example the highest 3.0 A pull-up current, 356 µA, into the highest
± 20 % Rd, 6.12 kΩ, gives :math:`356\ \mu\text{A} \times
6.12\ \text{k}\Omega = 2.18\ \text{V}`.

*Commercial practice.* :typec:`Section 4.8.5` gives the standard dead-battery
circuit: an Rd of ± 20 % in series with a transistor whose gate is weakly
pulled up to the CC pin itself, with a threshold below the maximum clamp
voltage (1.32 V); the source's pull-up turns it on. Once the chip is powered
it switches this path off and uses the trimmed Rd, keeping the CC voltage in
the band that indicates a connection (:typec:`Section 4.11.1`). Examples:
TPS65987D *RD_CC* 4.59-5.61 kΩ powered and *RD_DB* 4.08-6.12 kΩ unpowered
([USBPD-TPS65987D]_, Section 6.8); CCG5C removes its dead-battery Rd after its
processor boots ([USBPD-CCG5C]_, block diagram notes); STUSB4500
[USBPD-STUSB4500]_ and STUSB1602 use separate CC1DB/CC2DB pins wired to the CC
pins; the TPD8S300A protection chip [USBPD-TPD8S300A]_ integrates
dead-battery resistors in series with a FET whose threshold is 0.5-1.2 V
(Section 7.6).

*On-chip option.* The PDK has a 6 V native NMOS (*nfet_06v0_nvt*) with a
threshold of -0.32 V to 0.08 V ([USBPD-GF180-ELEC]_, section 4.0), well below
1.32 V, which can serve as the self-biased switch in series with a poly
resistor. Because its threshold can be below zero, turning it off needs its
gate driven below its source, by about 0.5 V to reach the specified
off-state; the specification gives the off-state leakage, up to 50 µA/µm at
6.6 V, with the gate at the threshold minus 0.5 V. On a dual-role port the
path must be switched off when the port presents Rp, otherwise it loads the
Rp current source. Risk: the off-state leakage, the negative gate drive and
the behaviour of the pad's electrostatic discharge (ESD) protection with no
supply must be simulated.

*External option.* A protection chip with integrated dead-battery resistors
(TPD8S300A). If the CC protection is external, the dead-battery Rd must be
visible through it while the board is unpowered, which the external option
provides directly.

VCONN switch
~~~~~~~~~~~~

*Requirement.* Connect a 3.0 V to 5.5 V supply to either CC pin, with a
current limit, within 2 ms of VBUS; discharge the pin through 30 Ω to
6120 Ω after detach (see `Cables and VCONN`_). For a board without USB data,
tens of milliamps are enough.

*Commercial practice.* TPS65987D PP_CABLE switch 222-325 mΩ, current limit
0.6-0.9 A ([USBPD-TPS65987D]_, Section 6.7); STUSB1602 100-600 mA
programmable with over-current, over-voltage and thermal protection
([USBPD-STUSB1602]_, features); CCG5C over-current detection from 550 mA
([USBPD-CCG5C]_, SID.DC.20VCONN.9).

*On-chip option.* A 5 V or 6 V PMOS switch per CC pin from a 5 V supply,
with a current limit of a few tens of milliamps; 5.5 V is within the rating
of the `standard 5 V and 6 V devices <Limits of the gf180mcu process_>`_. The pin carrying VCONN is the one not used for
messages, so the switch and the BMC circuits are not active on the same pin
at the same time. The switch sits behind the CC protection, so a VBUS short
reaches it only if that protection is on chip as well.

*External option.* A load switch with current limit, or a protection chip
whose CC switches pass VCONN (TPD8S300A passes up to 600 mA,
[USBPD-TPD8S300A]_, Section 7.4).

CC comparators
~~~~~~~~~~~~~~

*Requirement.* Per CC pin: as a sink, three thresholds for attach and Rp
level, at about 0.28 V, 0.68 V and 1.27 V (the midpoints of the threshold
windows in :numref:`tab-usbpd-sink-thresholds`); as a source, two boundaries
per Rp level, Ra to Rd and Rd to open (:numref:`tab-usbpd-src-thresholds`);
for BMC receive, role-dependent thresholds with hysteresis (about
0.25/0.53 V as sink, 0.60/0.88 V as source, after TPS65987D); and, if FRS is
supported, about 0.52 V.

*Commercial practice.* TPS65987D lists all of these as fixed thresholds
([USBPD-TPS65987D]_, Sections 6.8 and 6.9); FUSB302B uses three fixed
comparators plus a 6-bit DAC (42 mV steps) and comparator
([USBPD-FUSB302B]_, Table 10).

*On evampire.* One fast comparator per CC pin with a low-pass filter (time
constant at least 100 ns) for BMC and FRS, its threshold selected by a small
DAC or resistor ladder; attach and Rp-level checks are slow and can use the
same comparator between messages, or a shared ADC. All voltages are within
the rating of the `standard 5 V and 6 V devices <Limits of the gf180mcu process_>`_.

BMC driver
~~~~~~~~~~

*Requirement.* Drive 0 V and 1.05-1.2 V with 33-75 Ω output impedance, edges
of 300 ns to about 640 ns (10 %-90 %, see
`Transmitter levels, output impedance and edge rate`_), high impedance
otherwise, survive a 120 µs short to ground (:pd:`Section 5.3.4.10`).

*Commercial practice.* TPS65987D: 1.05-1.2 V, 33-75 Ω, rise and fall at least
300 ns ([USBPD-TPS65987D]_, Section 6.9); STUSB1602 drives the line from bits
supplied by an external microcontroller ([USBPD-STUSB1602]_).

*On evampire.* A small linear regulator for the 1.125 V rail and a slew
controlled tri-state stage; the pad side must withstand 5.5 V, so 5 V or 6 V
devices at the pad.

Reference voltage
~~~~~~~~~~~~~~~~~

*Requirement.* The driver level (± 6.7 % around 1.125 V), the Rp currents
(± 8 %) and the thresholds need a reference that is stable over supply and
temperature.

*On-chip option.* The open gf180mcu PDK has no bandgap reference among its IP
blocks ([USBPD-GF180-IP]_), so one has to be designed. The PDK documents
vertical bipolar transistors, the usual basis of a bandgap reference: a
vertical PNP (P+ in N-well over the P substrate) with a base-emitter voltage
of 0.63-0.83 V and a current gain of 0.8-2.4, and vertical NPN devices in deep
N-well ([USBPD-GF180-ELEC]_, section 5.8; [USBPD-GF180-DRM]_, Appendix A).
Risk: design and characterisation effort; a reference is also needed by the
Ethernet (:doc:`../ethernet/index`) and Power over Ethernet (:doc:`poe`)
circuits, so one design can serve all.

*External option.* A reference IC on the board.

VBUS sensing and discharge
~~~~~~~~~~~~~~~~~~~~~~~~~~

*Requirement.* Detect VBUS presence (vSafe5V 4.75 V to 5.5 V), vSafe0V
(0.8 V) before attaching as source, vSinkDisconnect (3.67 V), and check the
voltage after each change; discharge VBUS on detach, role swap and Hard
Reset. VBUS reaches 21.5 V in SPR and 50.9 V in EPR (see
`Layer 2: USB Power Delivery power levels`_).

*Commercial practice.* A divider into an ADC or comparator. TPS65987D, CCG5C
and STUSB1602 bring VBUS onto the chip (TPS65987D VBUS pins are rated to 24 V,
[USBPD-TPS65987D]_, Section 6.1); TUSB320 uses an external 887 kΩ resistor
into a 4 V-tolerant pin [USBPD-TUSB320]_.

*On-chip option.* A divider made of high-resistance poly resistors, so the
pin current is small: with the 3 kΩ/square option ([USBPD-GF180-ELEC]_,
section 6.1C), 1 MΩ takes :math:`1\ \text{M}\Omega / 3\ \text{k}\Omega =
333` squares and draws
:math:`21.5\ \text{V} / 1\ \text{M}\Omega = 21.5\ \mu\text{A}` at 21.5 V. The resistor body sits on field oxide; the voltage it can hold to
the substrate and between resistor segments is **not documented** in the PDK
documentation, and the pad's ESD structure must also tolerate the full VBUS
voltage. A discharge load needs a switch that blocks VBUS, which is the same
problem as the CC protection below.

*External option.* An external top resistor (as in TUSB320), so the chip
sees only the divided voltage, and an external discharge transistor.

Bidirectional VBUS power path and converter control
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Requirement.* As a sink, a switch from VBUS to the board's power bus; as a
source, a converter from the bus to the negotiated voltage (5 V to 20 V, or
up to 48 V in EPR) with a current limit; neither may feed power backwards,
and VBUS capacitance when not sourcing is at most 10 µF (:typec:`Table 4-2`).
Currents are up to 3 A or 5 A.

*Commercial practice.* TPS65987D has two 5 A internal power paths with
reverse-current blocking that turns off at 3-6 mV (comparator mode) and
configurable soft start ([USBPD-TPS65987D]_, Section 6.7); CCG5C drives
external P-channel MOSFETs on separate "consumer" and "provider" paths, with
gate drivers tolerant to 24 V ([USBPD-CCG5C]_, features).

*On-chip option.* The control part: the converter's pulse-width modulation,
current and voltage feedback through ADC inputs, the reverse-current
comparator and soft start can be built on chip at low voltage, with gate
drive signals to external switches. Gate drivers whose output swings at VBUS
potential need the same high-voltage isolation as the CC protection. The
power switches themselves must block 21.5 V (SPR) to 50.9 V (EPR) and carry
3 A to 5 A; the highest-rated standard device is the LDMOS, rated for a
10 V drain with a breakdown of at least 13.2 V
(`Limits of the gf180mcu process`_), so on-chip power switches would need
custom stacked structures whose isolation limit is not documented, and a
large area for low resistance at 5 A.

*External option.* MOSFETs, inductor and gate drivers on the board, as in
the :ref:`power flow <power-flow>`.

Over-voltage protection on the CC pins
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Requirement.* In normal operation the CC pins see at most 5.5 V. But the CC
contact sits next to VBUS in the connector, and damaged or non-compliant
cables and debris can short them. TI explains that twisting or sliding the
plug, debris or moisture can short 20 V VBUS onto CC ([USBPD-TPD8S300A]_,
Section 3). Infineon notes that such a short rings and can reach about twice
the VBUS voltage, 44 V for 21.5 V, if nothing clamps it ([USBPD-CYPD3177]_,
Section 1.1.3); 21.5 V is also the SPR worst case used on this page. Type-C
allows a port to clamp its CC pins at 2.9 V or above
(:typec:`Table 4-40`), but a port that supplies VCONN needs up to 5.5 V on the
VCONN pin, so any clamp must sit above 5.5 V.

**Why ESD protection does not cover this.** Every I/O pad already has
protection against electrostatic discharge (ESD), and it survives thousands
of volts, so it is natural to ask why a 20 V short is a problem. The
difference is the amount of charge and how long it lasts. An ESD test pulse
is a small capacitor discharged through a resistor. For the human body model
(HBM, defined in ANSI/ESDA/JEDEC JS-001, https://www.esda.org/standards/)
used to rate chip pins, the charge delivered at the gf180mcu I/O
library's 2 kV target ([USBPD-GF180-IO]_) is:

.. math::

   Q_\text{HBM} = C_\text{HBM} \cdot V_\text{HBM}
                = 100\ \text{pF} \times 2000\ \text{V}
                = 200\ \text{nC}

where :math:`C_\text{HBM}` = 100 pF and the series resistance is 1.5 kΩ
(the HBM network, [USBPD-TB505]_), and :math:`V_\text{HBM}` = 2000 V. The
pulse decays with a time constant of
:math:`1.5\ \text{k}\Omega \times 100\ \text{pF} = 150\ \text{ns}` and peaks
at :math:`2000\ \text{V} / 1.5\ \text{k}\Omega = 1.33\ \text{A}`
([USBPD-TB505]_, Figure 2). The system-level test used for connector pins,
IEC 61000-4-2 (https://webstore.iec.ch/en/publication/4189), uses 150 pF and
330 Ω; at 8 kV the charge is
:math:`150\ \text{pF} \times 8\ \text{kV} = 1.2\ \mu\text{C}` and the first
current peak is 30 A, with a rise time below 1 ns ([USBPD-TB505]_). An ESD
clamp only has to carry this bounded charge for about 100 ns.

A VBUS short is a power supply. A source must not trip its over-current
protection for any current allowed by the contract (:pd:`Section 4.1.5.1`), so
it can keep delivering 3 A or more until the cable is pulled. *Assumption
for an order of magnitude:* the short lasts 1 s, the source delivers 3 A, and
an on-chip clamp holds the pin at 6 V. Then:

.. math::

   Q_\text{short} &= I \cdot t = 3\ \text{A} \times 1\ \text{s} = 3\ \text{C} \\
   E_\text{clamp} &= V_\text{clamp} \cdot I \cdot t
                   = 6\ \text{V} \times 3\ \text{A} \times 1\ \text{s}
                   = 18\ \text{J}

which is :math:`3\ \text{C} / 200\ \text{nC} = 1.5 \times 10^{7}` times the
HBM charge, and 18 W of continuous dissipation in the clamp. No clamp sized
for ESD can absorb this. A VBUS short must therefore be *blocked*: a series
element that holds off the full VBUS voltage (plus the ringing, unless a
clamp limits it) and opens quickly enough that the low-voltage circuits behind
it see only a brief overshoot, which an ordinary ESD-type clamp can then
absorb. TPD8S300A opens in typically 70 ns ([USBPD-TPD8S300A]_, Section 7.7);
NXP's NX48P0407, made for EPR, is specified for a short to 48 V VBUS with an
absolute maximum of 60 V on its CC pins and a response below 60 ns
[USBPD-NX48P0407]_. VBUS itself is protected against surges at board level,
for example with a transient voltage suppressor (TVS) diode
([USBPD-TPS25750]_, Section 10.2.3.2.2).

:numref:`tab-usbpd-cc-ratings` compares commercial parts.

.. list-table:: CC pin voltage ratings of commercial parts
   :name: tab-usbpd-cc-ratings
   :header-rows: 1
   :widths: 25 35 40

   * - Part
     - CC pin rating
     - Source
   * - TI TPS65987D (dual-role)
     - -0.5 V to 6 V absolute maximum
     - [USBPD-TPS65987D]_, Section 6.1
   * - TI TPS25750 (dual-role)
     - -0.5 V to 26 V absolute maximum
     - [USBPD-TPS25750]_, Section 7.1
   * - Infineon CCG5C (dual-role)
     - 24 V maximum
     - [USBPD-CCG5C]_, absolute maximum ratings
   * - ST STUSB1602 (dual-role)
     - 22 V short-to-VBUS protection; "designed in a 20 V technology"
     - [USBPD-STUSB1602]_, features and description
   * - onsemi FUSB302B (PHY, dual-role capable)
     - -0.5 V to 6.0 V absolute maximum
     - [USBPD-FUSB302B]_, Table 7
   * - TI TPD8S300A (external protector)
     - 24 V short-to-VBUS tolerance; switches open at 5.75 V to 6.2 V,
       typically within 70 ns
     - [USBPD-TPD8S300A]_, Sections 7.6 and 7.7
   * - NXP NX48P0407 (external protector, EPR)
     - CC shorted to 48 V VBUS; 60 V absolute maximum; response below 60 ns
     - [USBPD-NX48P0407]_

Controllers with 20 V-class CC pins are made in processes with high-voltage
devices (STUSB1602's description says so explicitly); controllers whose CC
pins are rated to 6 V (TPS65987D, FUSB302B) need an external protector
against a VBUS short.

*On-chip option.* A series blocking switch per CC pin, built from custom
high-voltage structures: transistors stacked in isolated wells so that each
holds part of the voltage, or custom drain-extended transistors. Stacking
low-voltage transistors to handle several times their rated voltage is
established in standard CMOS: Serneels and co-authors built an output driver
in a 2.5 V, 0.25 µm CMOS process that operates at three times the nominal
supply [USBPD-SERNEELS]_, and Ballan and Declercq describe high-voltage
devices built in standard CMOS without extra process steps
[USBPD-BALLAN]_. The switch must block 21.5 V for SPR and 50.9 V for EPR
(`Layer 2: USB Power Delivery power levels`_), plus the ringing unless a clamp behind it limits that, open within about 100 ns, pass
the BMC signal, Rp/Rd currents and VCONN with low resistance, and keep the
dead-battery Rd visible without power. The limit that decides feasibility is
the breakdown of the isolating well to the substrate, which is **not
documented** for deep N-well (`Limits of the gf180mcu process`_); the
documented N-well to substrate breakdown is at least 10 V. Feasibility therefore has to be established with
test structures, and the risk is high, especially for EPR.

*External option.* A protector such as TPD8S300A (SPR) or NX48P0407 (EPR) in
front of evampire's CC pins, which can then use standard 5 V or 6 V devices.

Limits of the gf180mcu process
------------------------------

Three different kinds of limit matter, and they should not be confused.

**(a) Ratings of the standard devices.** These are conservative continuous
operating limits for the devices in the PDK
(https://gf180mcu-pdk.readthedocs.io/). The process is described as
"0.18 µm 3.3V/(5V)6V dual-gate MCU technology" ([USBPD-GF180-DRM]_, Section
1.0), with low-voltage devices at 3.3 V and high-voltage devices at 5 V or
6 V (Section 2.7), and the device list also contains LDMOS transistors rated
for 10 V (Appendix A; :numref:`tab-usbpd-pdk-ratings`).

.. list-table:: (a) Standard device operating voltages
   :name: tab-usbpd-pdk-ratings
   :header-rows: 1
   :widths: 40 60

   * - Device
     - Operating voltage
   * - nfet_03v3, pfet_03v3
     - 3.3 V
   * - nfet_05v0, pfet_05v0 (6 V devices with a 5 V marker layer)
     - 5 V
   * - nfet_06v0, pfet_06v0, nfet_06v0_nvt (native)
     - 6 V
   * - nfet_10v0_asym, pfet_10v0_asym (LDMOS)
     - 10 V drain, 6 V gate ([USBPD-GF180-ELEC]_, sections 8.1 and 8.2)
   * - MIM capacitor, 1.5 fF/µm² option
     - at most 10 V ([USBPD-GF180-ELEC]_, section 6.2)
   * - MIM capacitor, 1 fF/µm² option
     - "≤ 20 V application" ([USBPD-GF180-ELEC]_, section 6.2)

**(b) Physical limits of the layers.** Breakdown voltages measured on test
structures, where documented ([USBPD-GF180-ELEC]_, sections 1 to 8;
:numref:`tab-usbpd-pdk-breakdown`):

.. list-table:: (b) Documented breakdown limits
   :name: tab-usbpd-pdk-breakdown
   :header-rows: 1
   :widths: 50 25 25

   * - Structure
     - Minimum
     - Typical
   * - Gate oxide, 3.3 V devices
     - 7 V
     - 8.8-9 V
   * - Gate oxide, 6 V devices
     - 12 V
     - 16 V
   * - N+ to P-well junction, 6 V NMOS
     - 8.5 V
     - 11 V
   * - N-well to P-substrate junction
     - 10 V
     - 14 V
   * - LDMOS drain (BVDSS)
     - 13.2 V
     - 14.5 V
   * - Vertical PNP collector-emitter (BVCEO)
     - 10 V
     - 15 V
   * - MIM dielectric, 1.5 fF/µm²
     - 10 V
     - 30 V
   * - MIM dielectric, 1 fF/µm²
     - 20 V
     - 40 V
   * - Deep N-well to P-substrate junction
     - not documented
     -
   * - Field oxide under poly or metal, and between metal layers
     - not documented
     -

Which MIM option, and whether the LDMOS and deep N-well layers, are available
on the wafer.space (https://wafer.space/) shuttle has to be confirmed.

**(c) What custom structures could reach.** These are design possibilities
whose limits come from (b), not from (a):

* *Stacked transistors in isolated wells.* Each transistor holds a share of
  the voltage within its own rating; the stack is limited by the breakdown of
  the isolating well to the substrate (deep N-well: not documented) and by
  the gate oxide of each device relative to its own well. Published example:
  [USBPD-SERNEELS]_.
* *Custom drain-extended transistors.* A longer, lightly doped drain region
  drawn from existing layers, as described by [USBPD-BALLAN]_; the PDK's own
  LDMOS, rated for 10 V, breaks down at no less than 13.2 V.
* *Series capacitor stacks.* For coupling or sensing AC signals across a
  high voltage; with the 1 fF/µm² MIM option each capacitor withstands at
  least 20 V, but the bottom plate to substrate isolation is not documented.
* *High-resistance poly dividers.* 1 kΩ, 2 kΩ or 3 kΩ per square
  ([USBPD-GF180-ELEC]_, section 6.1); limited by the undocumented field oxide
  breakdown.
* *Custom clamps and references.* Clamps from the documented diodes and
  bipolar transistors; a bandgap reference from the vertical PNP.

Pin voltages and placement options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:numref:`tab-usbpd-placement` summarises the options.

.. list-table:: Where each function can be built
   :name: tab-usbpd-placement
   :header-rows: 1
   :widths: 22 24 27 27

   * - Function
     - Voltage
     - On chip
     - External
   * - Rp, Rd, comparators, BMC driver and receiver, VCONN switch
     - 0 V to 5.5 V
     - Standard 5 V / 6 V devices
     - Not needed
   * - Dead-battery Rd
     - at most 2.18 V, unpowered (:typec:`Table 4-28`)
     - Native NMOS and poly resistor
     - In the CC protector
   * - Reference
     - low voltage
     - Custom bandgap from vertical PNP
     - Reference IC
   * - CC protection against VBUS short
     - 21.5 V (SPR) or 50.9 V (EPR), plus ringing
     - Custom stacked switch; limit not documented; high risk
     - Protector (TPD8S300A, NX48P0407)
   * - VBUS sensing
     - up to 21.5 V or 50.9 V
     - Poly divider; field oxide limit not documented
     - External top resistor
   * - VBUS discharge
     - same
     - Needs a blocking switch as above
     - External transistor and load
   * - Power path switches and source converter
     - same, at 3 A to 5 A
     - Control and feedback on chip; power devices beyond documented limits
     - MOSFETs, inductor, gate drivers

The choice for each row is listed under `Open design decisions`_.

Open design decisions
---------------------

* **Processor core and clock** (`The processor clock`_). Multi-cycle or
  pipelined, and 31.25 MHz, 62.5 MHz or another clock. This decides whether
  the timer compare and capture channels are required
  (`Hardware helpers, in order of need`_).
* **Optional timer channels** (`Recommended split`_). With a pipelined core
  at 50 MHz or faster no digital helper is needed; adding a timer capture
  channel with a FIFO (and choosing its depth) and a compare output per port
  anyway would let interrupts stay enabled during messages instead of being
  disabled for up to 2.3 ms.
* **Behaviour with two ports at once** (`Two ports in software`_). Whether
  occasional message loss and retries on the second port are acceptable, or
  a helper per port is added.
* **Supported power levels** (`Layer 2: USB Power Delivery power levels`_).
  Whether the board offers and accepts only SPR fixed supplies, also 5 A
  (which requires VCONN and cable discovery as source), PPS/AVS, or EPR
  (48 V on VBUS and on the CC pins in a fault, and keep-alive messages).
* **Role preference policy** (`Choosing the initial role`_). When to use
  Try.SRC or Try.SNK, and when to ask for a power role swap, given the
  :ref:`power budget <power-budget>`.
* **Fast role swap** (`Fast role swap`_). Whether the board signals or
  accepts FRS; this needs a strong CC pull-down, hold-up energy, and a source
  converter kept running.
* **CC protection against a VBUS short**
  (`Over-voltage protection on the CC pins`_). A custom on-chip blocking
  switch (which first needs test structures to measure the deep N-well
  isolation limit) or an external protector; either must pass VCONN and keep
  the dead-battery Rd visible.
* **Dead-battery Rd** (`Switchable Rd and dead-battery Rd`_). On chip
  (native NMOS and poly resistor) or in an external protector.
* **VCONN switch** (`VCONN switch`_). On chip (standard 5 V / 6 V devices)
  or external.
* **Reference voltage** (`Reference voltage`_). A custom on-chip bandgap
  reference from the vertical PNP, shared with the Ethernet
  (:doc:`../ethernet/index`) and Power over Ethernet (:doc:`poe`) circuits,
  or an external reference.
* **VBUS sensing and discharge** (`VBUS sensing and discharge`_). An on-chip
  poly divider (field oxide limit to be established) or an external top
  resistor and discharge transistor.
* **Power path and converter**
  (`Bidirectional VBUS power path and converter control`_). Which parts of
  the control (modulation, feedback, reverse-current detection, gate drive)
  are on chip; the power switches themselves; and budget margins, including
  how fast the board can react when the Ethernet input is reduced or lost
  (see :ref:`power budget <power-budget>` and :doc:`poe`).
* **Process options** (`Limits of the gf180mcu process`_). Which MIM option
  and whether the LDMOS and deep N-well layers are available on the
  wafer.space (https://wafer.space/) shuttle.

References
----------

.. [USBPD-TYPEC] USB Implementers Forum, *USB Type-C Cable and Connector
   Specification*, Release 2.5, March 2026 (download "USB Type-C 2.5 Release
   202603").
   https://www.usb.org/document-library/usb-type-cr-cable-and-connector-specification-release-25

.. [USBPD-PD] USB Implementers Forum, *USB Power Delivery Specification*,
   Revision 3.3, Version 1.0, 2026-10-16 (download USB_PD_R3.3_V1.0.zip).
   https://www.usb.org/document-library/usb-power-delivery

.. [USBPD-BMCRX] USB Implementers Forum, *Alternate BMC Receiver Design
   Examples*, informative white paper, Revision 1.1, 2026-01-01. Included in
   the [USBPD-PD]_ download.

.. [USBPD-TPS65987D] Texas Instruments, *TPS65987D USB Type-C and USB PD
   Controller with Integrated Source and Sink Power Path*, SLVSES1D, revised
   2022-10. https://www.ti.com/lit/ds/symlink/tps65987d.pdf

.. [USBPD-TPS25750] Texas Instruments, *TPS25750 USB Type-C and USB PD
   Controller with Integrated Power Switches*, SLVSFR7A, revised 2020-11.
   https://www.ti.com/lit/ds/symlink/tps25750.pdf

.. [USBPD-TPD8S300A] Texas Instruments, *TPD8S300A USB Type-C Port
   Protector: Short-to-VBUS Overvoltage and IEC ESD Protection*, SLVSEL9,
   2018-06. https://www.ti.com/lit/ds/symlink/tpd8s300a.pdf

.. [USBPD-TUSB320] Texas Instruments, *TUSB320 USB Type-C Configuration
   Channel Logic and Port Control*, SLLSEN9F, revised 2022-03.
   https://www.ti.com/lit/ds/symlink/tusb320.pdf

.. [USBPD-FUSB302B] onsemi, *FUSB302B Programmable USB Type-C Controller with
   PD*, Rev. 5, 2021-08.
   https://www.onsemi.com/download/data-sheet/pdf/fusb302b-d.pdf

.. [USBPD-STUSB1602] STMicroelectronics, *STUSB1602 USB Type-C controller
   with TX/RX line driver and BMC*, DocID028319 Rev 2, 2017-04. Copy used:
   https://datasheet.chipsmall.com/STUSB1602QTR/628546.pdf (st.com could not
   be reached when this page was written).

.. [USBPD-STUSB4500] STMicroelectronics, *STUSB4500 Standalone USB PD
   Controller (Sink)*, DS12499 Rev 3, 2019-12. Copy used:
   https://cdn.sparkfun.com/assets/b/6/e/8/9/DS-15801-STUSB4500.pdf

.. [USBPD-CCG5C] Infineon (Cypress), *EZ-PD CCG5C USB Type-C Port
   Controller*, 002-23803 Rev. \*D, 2019-02-18.
   https://www.infineon.com/assets/row/public/documents/24/49/infineon-ez-pd-ccg5c-usb-type-c-port-controller-datasheet-en.pdf

.. [USBPD-CYPD3177] Infineon, *EZ-PD BCR USB Type-C Port Controller for
   Power Sinks (CYPD3177)*, 002-25383 Rev. \*C, 2024-09-18.
   https://www.infineon.com/assets/row/public/documents/24/49/infineon-cypd3177-24lqxq-datasheet-en.pdf

.. [USBPD-NX48P0407] NXP Semiconductors, *NX48P0407 48 V USB Type-C CC/SBU
   Protection IC*, product page. https://www.nxp.com/products/NX48P0407

.. [USBPD-TB505] Renesas, *TB505 Understanding the Difference between HBM and
   IEC 61000-4-2 ESD Immunity*, Rev 0.00, 2016-07-29.
   https://www.renesas.com/us/en/document/oth/tb505-understanding-difference-between-hbm-and-iec-61000-4-2-esd-immunity

.. [USBPD-SERNEELS] B. Serneels, T. Piessens, M. Steyaert and W. Dehaene,
   "A high-voltage output driver in a 2.5-V 0.25-µm CMOS technology", *IEEE
   Journal of Solid-State Circuits*, vol. 40, no. 3, pp. 576-583, 2005-03.
   https://doi.org/10.1109/JSSC.2005.843599

.. [USBPD-BALLAN] H. Ballan and M. Declercq, *High Voltage Devices and
   Circuits in Standard CMOS Technologies*, Kluwer Academic Publishers, 1999.
   https://link.springer.com/book/9780792382348

.. [USBPD-PICORV32] YosysHQ, *PicoRV32 - A Size-Optimized RISC-V CPU*,
   README (cycles per instruction table). https://github.com/YosysHQ/picorv32

.. [USBPD-RAVEN] eeNews Europe, "X-FAB Silicon Foundries tapes out open
   source RISC-V MCU" (Raven, PicoRV32 in the X-FAB XH018 process).
   https://www.eenewseurope.com/news/x-fab-silicon-foundries-tapes-out-open-source-risc-v-mcu

.. [USBPD-GF180-DRM] GlobalFoundries, *GF180MCU PDK Design Manual*:
   Sections 1.0 and 2.7 (process and operating voltages), Section 10.12
   (10 V LDMOS rules), Appendix A (device list).
   https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_man.html

.. [USBPD-GF180-ELEC] GlobalFoundries, *GF180MCU Electrical Parameters
   Specification*, sections 1 to 8.
   https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs.html

.. [USBPD-GF180-SC] GlobalFoundries, *gf180mcu_fd_sc_mcu7t5v0 7-track
   standard cell library*: cell gf180mcu_fd_sc_mcu7t5v0__dffq_1 and databook
   conditions.
   https://gf180mcu-pdk.readthedocs.io/en/latest/digital/standard_cells/gf180mcu_fd_sc_mcu7t5v0/index.html

.. [USBPD-GF180-IO] GlobalFoundries, *gf180mcu_fd_io 5 V I/O library*, ESD
   protection targets.
   https://gf180mcu-pdk.readthedocs.io/en/latest/IPs/IO/gf180mcu_fd_io/esd.html

.. [USBPD-GF180-IP] GlobalFoundries, *GF180MCU PDK IPs and macros* (I/O and
   SRAM only). https://gf180mcu-pdk.readthedocs.io/en/latest/IPs/ips.html
