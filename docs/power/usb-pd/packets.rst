Packets on the configuration channel
====================================

How a message is framed, coded and checked on the wire.

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
