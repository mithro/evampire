Management interface (MDIO)
===========================

How evampire reads the status of each Ethernet transceiver and changes its
settings over the two-wire management interface, and which registers it
uses. The interface and its standard registers are defined in
:clause:`22`.

.. _rgmii-mdio-wires:

MDC and MDIO wires
------------------

Each transceiver has a few dozen 16-bit registers. They report its status,
such as whether a cable is connected and at what speed, and control its
settings, such as reset, speed and clock delays. The registers are read and
written over the :term:`MDIO` interface
(:wikipedia:`management data input/output <Management_Data_Input/Output>`):

MDC
   Management clock, driven by evampire (:clause:`22.2.2.13`).
MDIO
   Management data, in both directions (:clause:`22.2.2.14`). evampire drives
   it, except during the data part of a read, when the transceiver drives
   it. Both ends use three-state drivers, and a
   :wikipedia:`pull-up resistor <Pull-up_resistor>` holds the line high when
   neither drives it. The DP83867 asks for 2.2 kΩ [RGMII-DP83867]_
   section 7.4.2 and the KSZ9031RNX for 1.0 kΩ to 4.7 kΩ [RGMII-KSZ9031]_
   section 2, pin 37.

Several transceivers can share one MDC and MDIO pair. Each management frame
carries a 5-bit transceiver address, so one pair can reach up to 32
transceivers (:clause:`22.2.4.5.5`). Each transceiver takes its address from
pins sampled at power-up [RGMII-DP83867]_ section 7.4.2,
[RGMII-KSZ9031]_ section 3.10. evampire drives both of its transceivers from
one pair of pins, with the two transceivers set to different addresses.

:numref:`fig-rgmii-mdio-bus` shows the two wires shared by evampire's two
transceivers.

.. graphviz:: mdio-bus.dot
   :name: fig-rgmii-mdio-bus
   :caption: MDC and MDIO shared by the transceivers of ports A and B, with
             the pull-up resistor on MDIO.
   :alt: evampire on the left drives MDC, in blue, to transceiver A and
         transceiver B on the right. MDIO, in red, joins evampire's
         three-state driver to the three-state MDIO pin of each
         transceiver, and a pull-up resistor connects it to VDDIO: 2.2 kΩ
         for the DP83867, 1.0 kΩ to 4.7 kΩ for the KSZ9031RNX. Each
         transceiver takes its address from strap pins; one pair of wires
         reaches up to 32 transceivers.
   :align: center

.. _rgmii-mdc-rate:

MDC clock rate
--------------

MDC has a minimum period of 400 ns, that is at most 2.5 MHz, and minimum
high and low times of 160 ns each (:clause:`22.2.2.13`). It has no maximum
high or low time, so it does not need to run continuously. The KSZ9031RNX
datasheet gives 2.5 MHz, a 400 ns period, as the typical rate
[RGMII-KSZ9031]_ section 7.

When evampire drives MDIO, it gives at least 10 ns of setup and hold time
around the rising edge of MDC. When the transceiver drives MDIO, its data
appears 0 ns to 300 ns after the rising edge, and evampire samples it at
the next rising edge (:clause:`22.3.4`).

Many transceivers accept a faster MDC. The DP83867 accepts up to 25 MHz
[RGMII-DP83867]_ section 6.8, and the KSZ9031RNX has been tested up to
8.33 MHz [RGMII-KSZ9031]_ section 7. evampire keeps to 2.5 MHz or less, so
that any transceiver that meets :clause:`22` works.

One register access takes 64 MDC cycles (see the next section):

.. math::

   t_\text{acc} = N \times T_\text{MDC}

.. list-table::
   :header-rows: 1
   :widths: 15 70 15

   * - Symbol
     - Meaning
     - Unit
   * - :math:`t_\text{acc}`
     - Time for one register access
     - µs
   * - :math:`N`
     - Number of MDC cycles in one access, 64 with a full preamble
     - none
   * - :math:`T_\text{MDC}`
     - MDC period, at least 0.4 µs
     - µs

At the shortest period, :math:`t_\text{acc} = 64 \times 0.4\ \mu\text{s}
= 25.6\ \mu\text{s}`. A transceiver's link status changes much more slowly
than that.

.. _rgmii-mdio-frame:

Management frame
----------------

Every access is one 64-bit frame with the fields of
:numref:`tab-rgmii-mdio-frame` (:clause:`22.2.4.5`,
:clause:`Table 22-12 <22>`). The bits are sent from left to right, and
each address and the data are sent most significant bit first
(:clause:`22.2.4.5.5` to :clause:`22.2.4.5.8`). The KSZ9031RNX datasheet
gives the same frame [RGMII-KSZ9031]_ section 3.10.

.. list-table:: Fields of an MDIO management frame
   :name: tab-rgmii-mdio-frame
   :header-rows: 1
   :widths: 30 15 55

   * - Field
     - Bits
     - Contents
   * - Preamble
     - 32
     - All ones
   * - Start
     - 2
     - 01
   * - Operation
     - 2
     - 10 for a read, 01 for a write
   * - Transceiver address
     - 5
     - Which transceiver on the shared pair
   * - Register address
     - 5
     - Which of the 32 registers
   * - Turnaround
     - 2
     - Read: released, then 0 from the transceiver. Write: 10
   * - Data
     - 16
     - Register value, bit 15 first

The preamble gives the transceiver a pattern to lock on to
(:clause:`22.2.4.5.2`). A transceiver that sets status bit 1.6 accepts
frames without it (:clause:`Table 22-8 <22>`). In the turnaround of a read,
neither end drives the line for the first bit, and the transceiver drives
a 0 for the second (:clause:`22.2.4.5.7`).
:numref:`fig-rgmii-mdio-read` and :numref:`fig-rgmii-mdio-read-2` show a
read.

.. wavedrom::
   :name: fig-rgmii-mdio-read
   :alt: Timing diagram, first part of an MDIO read: MDC clock, and MDIO
         driven by evampire with the end of the preamble, start bits 01,
         operation bits 10 and the 5-bit transceiver address.
   :caption: First part of an MDIO read, with each bit sampled at the rising
             edge of MDC.

   { "signal": [
       { "name": "MDC",       "wave": "p.|.........", "phase": -0.5 },
       { "name": "MDIO",      "wave": "1.|01.0=....",
         "data": ["PHYAD"] },
       { "name": "driven by", "wave": "3.|.........",
         "data": ["evampire"] },
       { "name": "field",     "wave": "2.|4.5.6....",
         "data": ["preamble", "ST", "OP", "PHYAD"] }
     ],
     "config": { "hscale": 1 }
   }

.. wavedrom::
   :name: fig-rgmii-mdio-read-2
   :alt: Timing diagram, second part of an MDIO read: evampire drives the
         5-bit register address, releases MDIO for one bit, then the
         transceiver drives a 0 followed by the 16 data bits.
   :caption: Second part of an MDIO read, where the transceiver drives the
             turnaround 0 and the 16 data bits.

   { "signal": [
       { "name": "MDC",       "wave": "p...........|..", "phase": -0.5 },
       { "name": "MDIO",      "wave": "=....z0=....|z.",
         "data": ["REGAD", "DATA (16 bits)"] },
       { "name": "driven by", "wave": "3....z4.....|z.",
         "data": ["evampire", "transceiver"] },
       { "name": "field",     "wave": "2....3.4....|x.",
         "data": ["REGAD", "TA", "DATA"] }
     ],
     "config": { "hscale": 1 }
   }

In the figures, PHYAD is the transceiver address, REGAD the register
address, ST the start bits, OP the operation and TA the turnaround. The
break marks bits that are not drawn.

.. _rgmii-mdio-software:

Software-driven MDIO
--------------------

MDC has no maximum period, so software can drive MDC and MDIO as
general-purpose pins (:wikipedia:`bit banging <Bit_banging>`) at any speed
up to 2.5 MHz. For each of the 64 bits of an access, the software sets MDC
low, sets MDIO or samples it, and sets MDC high. A hardware MDIO controller
does the same work without the processor.

.. _rgmii-registers:

Registers used by evampire
--------------------------

Registers 0 to 15 are defined by IEEE 802.3, and registers 16 to 31 are
specific to each manufacturer (:clause:`Table 22-6 <22>`).
:numref:`tab-rgmii-registers` lists the standard registers evampire uses.

:wikipedia:`Autonegotiation <Autonegotiation>` (:clause:`28`) is the
exchange, at link start-up, in which the two transceivers on a cable tell
each other which speeds and duplex modes they support. Both then pick the
best common one. :term:`1000BASE-T` is gigabit Ethernet over four twisted
pairs (:clause:`40`, see :doc:`../phy-electrical/index`).

.. list-table:: Standard transceiver registers used by evampire
   :name: tab-rgmii-registers
   :header-rows: 1
   :widths: 15 25 60

   * - Register
     - Name
     - Bits used
   * - 0
     - Control
     - 15 reset; 12 autonegotiation enable; 9 restart autonegotiation; 8
       duplex; 6 and 13 speed
   * - 1
     - Status
     - 2 link status; 5 autonegotiation complete
   * - 2 and 3
     - Transceiver identifier
     - All, to find the manufacturer and model
   * - 4
     - Autonegotiation advertisement
     - 8 and 7: 100 Mbit/s full and half duplex; 6 and 5: 10 Mbit/s full
       and half duplex
   * - 5
     - Link partner ability
     - The same bits as register 4, offered by the far end
   * - 9
     - 1000BASE-T control
     - 9 and 8: 1000 Mbit/s full and half duplex offered
   * - 10
     - 1000BASE-T status
     - 11 and 10: 1000 Mbit/s full and half duplex offered by the far end

The definitions are in :clause:`Table 22-7 <22>` (register 0),
:clause:`Table 22-8 <22>` (register 1), :clause:`22.2.4.3.1` (registers 2
and 3), :clause:`Table 28-2 <28>` with :clause:`Table 28B-1 <28>`
(registers 4 and 5) and :clause:`Table 40-3 <40>` (registers 9 and 10). The
DP83867 and KSZ9031RNX datasheets give the same bits [RGMII-DP83867]_
sections 8.1 to 8.13, [RGMII-KSZ9031]_ section 4.2, and the UNH-IOL
management register test suite tests them [RGMII-IOL-REG]_.

Register 0 bits 0.6 and 0.13 force the speed when autonegotiation is off:
10 for 1000 Mbit/s, 01 for 100 Mbit/s and 00 for 10 Mbit/s. The reset bit
reads 1 until the reset is complete. The link status bit 1.2 stays 0 after
a link failure until it is read, so software reads it twice to get the
present state (:clause:`22.2.4.2.13`). Register 4 bits 4:0 hold the value
00001, which selects IEEE 802.3 (:clause:`Table 28A-1 <28>`).

The result of autonegotiation is the highest-priority ability that both
ends offer, in the order of :clause:`Annex 28B.3 <28>`: higher speeds
first, and full duplex before half duplex. Transceivers also report the
result in a manufacturer-specific register. In the DP83867, register 0x11
gives the speed in bits 15:14, the duplex in bit 13 and the link in bit 10
[RGMII-DP83867]_ section 8.15.

Registers 16 to 31, and most of the extended registers reached through
registers 13 and 14 (:clause:`22.2.4.3.11`, :clause:`22.2.4.3.12`), differ
between transceivers. The clock delay settings of :doc:`timing` are among
them [RGMII-DP83867]_ section 8.12, [RGMII-KSZ9031]_ section 3.9.3. The
software reads registers 2 and 3 to find which transceiver is fitted.
