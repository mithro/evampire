Changing roles while connected
==============================

How the two ends swap power role, data role and VCONN, and recover with a Hard Reset.

Role changes
------------

Power role swap
~~~~~~~~~~~~~~~

Either port can ask to swap power roles with a PR_Swap message; the other
answers Accept, Reject or Wait (:pd:`Section 7.10`). Data roles and the VCONN
duty do not change (:typec:`Table 4-13`). :numref:`fig-usbpd-prswap` shows the
sequence and :numref:`tab-usbpd-prswap` its time limits.

.. _fig-usbpd-prswap:

.. graphviz:: pr-swap.dot
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
