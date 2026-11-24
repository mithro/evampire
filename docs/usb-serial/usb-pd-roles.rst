USB Power Delivery roles
========================

This page describes how the USB serial port fits with the power roles of a
USB Type-C port, the data role swap, boards with two ports, and the other
work the processor does. The USB Power Delivery negotiation itself is on
:doc:`/power/usb-pd/index`. Type-C and PD references link to the USB Type-C and
USB Power Delivery specifications on the :doc:`standards page
</standards>`.

Power and data roles
--------------------

A USB Type-C port has a *power role*, source or sink (:ref:`power-roles`),
and, when it carries USB data, a separate *data role*: DFP, the host side,
or UFP, the device side. A port that can take either data role is a
*dual-role-data* port (:typec:`Section 2.3.3`). When a cable is plugged in,
the source starts as DFP and the sink as UFP; USB Power Delivery can then
swap either role without changing the other (:typec:`Section 4.5.1.4`,
:typec:`Table 4-13`).

evampire's serial port works only when the port's data role is UFP, so that
the computer at the other end is the host. :numref:`tab-usbser-roles` lists
the cases.

.. list-table:: Initial roles and what the serial port needs
   :name: tab-usbser-roles
   :header-rows: 1
   :widths: 24 22 18 36

   * - Board situation
     - evampire power role
     - Initial data role
     - Serial port
   * - Powered from a computer's USB port
     - Sink
     - UFP
     - Works as attached
   * - Powered from Ethernet, supplying a laptop
     - Source
     - DFP
     - Needs a data role swap to UFP
   * - Powered from a charger with no USB data
     - Sink
     - UFP
     - No host to talk to; nothing happens

Data role swap
--------------

A data role swap is a USB Power Delivery message exchange, DR_Swap, that
exchanges DFP and UFP and nothing else: VBUS, the CC resistors and VCONN
stay as they are (:pd:`Section 6.3.9`; :typec:`Table 4-13`).
:numref:`fig-usbser-dr-swap` shows the exchange with evampire as source,
and :ref:`Data roles and DR_Swap <usbpd-data-roles>` describes the
message rules.

.. graphviz:: usb-pd-roles/dr-swap.dot
   :name: fig-usbser-dr-swap
   :caption: A data role swap with evampire as source: the data roles
             change and the power roles do not.
   :alt: Sequence diagram between evampire, the source and DFP, and a
         laptop, the sink and UFP. Before the swap evampire has its pull-up
         off and D+ and D− undriven. evampire sends DR_Swap, the laptop
         answers GoodCRC and then Accept (or Reject or Wait), and evampire
         answers GoodCRC. evampire is then UFP and turns its pull-up on when
         VBUS is present; the laptop is DFP, the USB host. VBUS, Rp and Rd,
         and VCONN are unchanged. On Reject, evampire stays DFP with D+ and
         D− undriven and its pull-up off.
   :align: center

The USB Type-C specification names a port that supplies power but cannot be
a USB host a *sourcing device*. Such a port must support USB Power Delivery
and DR_Swap, and if it ends up as DFP after reaching a power agreement as
source, it must send or accept a DR_Swap to become UFP
(:typec:`Section 4.8.4`). Its own example is the upstream port of a hub or
a monitor. While the serial port is enabled, evampire's port is a sourcing
device whenever it supplies power, so its USB Power Delivery software
follows this rule.

The USB Power Delivery capability messages also describe the data side. A
source's and a sink's fixed-supply power data objects each carry a *USB
Communications Capable* bit, set when the port can talk over D+ and D−, and
a *Dual-Role Data* bit, set when it accepts DR_Swap (:pd:`Table 6.8`,
:pd:`Table 6.9`; :pd:`Section 6.4.2.1.7`). Both bits are set while the
serial port is enabled.

If the other end refuses the swap, evampire stays DFP. It then leaves D+
and D− undriven and its pull-up off, because there is no host to answer.

Pull-up control
---------------

The device connects its D+ pull-up to announce itself and must not drive
current into D+ while VBUS is absent ([USBSER-USB2]_ section 7.1.5.1). On
evampire the pull-up is switched by software when three conditions hold
(:numref:`fig-usbser-pullup`):
the port is attached, its data role is UFP, and VBUS is present, whether
the other end or evampire supplies it.

Two USB Power Delivery events change VBUS while the cable stays attached:

* *Voltage changes.* After an agreement, VBUS moves between 5 V and higher
  voltages. D+ and D− and the pull-up supply do not depend on VBUS, so the
  data connection continues.
* *Power role swap.* VBUS falls below 5 V and rises again from the other
  end. The data roles do not change, the initial sink does not treat the
  low VBUS as a detach (:pd:`Section 6.3.10`), and all data connections are
  kept through the swap (:pd:`Section 1.4`). The software therefore keeps
  the pull-up connected through a swap.

A Hard Reset is different: VBUS goes to 0 V and the data roles return to
DFP for the port with Rp, the source, and UFP for the port with Rd, the
sink (:pd:`Section 7.1.3`). The USB connection ends and, after the reset, a sourcing evampire
swaps to UFP again. :numref:`fig-usbser-pullup` follows the pull-up
through these events.

.. wavedrom::
   :caption: VBUS, the roles and the pull-up of a sourcing evampire through
             a data role swap, a voltage change, a Hard Reset and a power
             role swap (not to scale).
   :name: fig-usbser-pullup
   :alt: Timing diagram. evampire attaches as source with VBUS at 5 V, as
         DFP and with its pull-up off. After DR_Swap it is UFP and turns
         the pull-up on. VBUS changes from 5 V to 20 V and the pull-up stays
         on. A Hard Reset takes VBUS to 0 V, returns evampire to DFP and
         turns the pull-up off. VBUS returns to 5 V, a new DR_Swap makes
         evampire UFP, and the pull-up turns on again. A power role swap
         dips VBUS and makes evampire the sink, and the pull-up stays on.

   {"signal": [
     {"name": "event", "wave": "3.4.x.5.6.x.4.x.7.",
      "data": ["attach", "DR_Swap", "5 V to 20 V", "Hard Reset",
               "DR_Swap", "PR_Swap"]},
     {"name": "VBUS", "wave": "=......==.=.....==",
      "data": ["5 V", "20 V", "0 V", "5 V", "dip", "5 V"]},
     {"name": "power role", "wave": "=................=",
      "data": ["source", "sink"]},
     {"name": "data role", "wave": "=..=....=....=....",
      "data": ["DFP", "UFP", "DFP", "UFP"]},
     {"name": "pull-up", "wave": "0...1...0.....1..."}
   ],
   "config": {"hscale": 1.3}}

Two USB Type-C ports
--------------------

The first version has one USB Type-C port and the full design two
(:ref:`power-board-configs`). Each port has its own D+ and D− pair, and two
computers may be attached at once, one on each port. The options are:

* a USB device and front end per port, giving two independent serial ports;
* one USB device with its front end switched to one port at a time, by an
  analogue switch on D+ and D− or by two front ends sharing one digital
  block;
* a serial port on one designated port only.

With the hardware split of :doc:`software-cost`, two USB devices double the
buffers and the per-byte work but add no packet-level deadline. With a
smaller split, each port's deadlines apply independently, and packets on
the two ports can arrive at the same time.

Processor sharing
-----------------

The processor also runs the USB Power Delivery negotiation on each USB
Type-C port, the Power over Ethernet negotiation, the power budget and the
Ethernet frame buffers (:ref:`requirements`). Their time needs differ:

* *USB Power Delivery* in software keeps the processor busy for the length
  of each configuration channel message, with interrupts off; the
  :doc:`/power/usb-pd/software` page works this out.
* *Ethernet* frames for the processor wait in the receive buffer, which
  holds one or two frames (:ref:`arch-microcontroller`).
* *USB*, with automatic handshakes in hardware, has no deadline shorter than
  the 50 ms of a control request ([USBSER-USB2]_ section 9.2.6), and a busy
  processor only causes NAKs, which the host retries.

Without automatic handshakes, a token that arrives while the processor is
busy with a USB Power Delivery message gets no reply. The host counts that
as an error and gives up the transfer after three in a row
([USBSER-USB2]_ section 10.2.6). The worst case is then a USB Power
Delivery message on each port and a USB packet arriving together, and
whether that is acceptable depends on how often it happens.

Open questions
--------------

* Whether the serial port is offered on one USB Type-C port or both, and,
  for both, two devices or one switched device.
* Whether evampire also tries to become UFP when it is a sink but the
  computer has swapped to UFP itself, and its policy on requesting and
  accepting DR_Swap.
* How the software gates the pull-up on VBUS during a power role swap and a
  Hard Reset.
