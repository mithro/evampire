USB Power Delivery messages and power levels
============================================

The power levels USB Power Delivery offers, and the messages that carry the offers and requests.

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
