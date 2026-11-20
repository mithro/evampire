Analogue circuits for one port
==============================

The analogue circuits that connect evampire to the configuration channel and VBUS.

Analog blocks
-------------

:numref:`fig-usbpd-port-blocks` shows the circuits for one port.

.. _fig-usbpd-port-blocks:

.. graphviz:: port-blocks.dot
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
