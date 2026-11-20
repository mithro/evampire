.. _phy-int-control:

Control: link pulses, autonegotiation logic and registers
=========================================================

This page lists what a gigabit-only integrated transceiver needs for
:doc:`../autonegotiation` and for software control: the link pulse driver
and receiver, the state machines and timers, and the management registers.

.. _phy-int-autoneg:

Autonegotiation needs a pulse driver, a comparator and state machines
---------------------------------------------------------------------

1000BASE-T requires autonegotiation (:clause:`40.5.1`), so even a
gigabit-only transceiver needs:

Link pulse driver
   Fast link pulse bursts with the timing of :numref:`tab-phy-flp-timing`.
   Each pulse fits the 10BASE-T link test pulse template, with its peak
   between 585 mV and 3.1 V and a width of about 100 ns
   (:clause:`Figure 14-13 <14>`). The gigabit driver of
   :doc:`transmitter` reaches 1 V on the line, inside that range, so the
   link pulses need no higher-swing driver (estimate, to be confirmed by
   checking the whole template shape).
Link pulse receiver
   A comparator with a threshold, and timers that check the pulse spacing
   (:clause:`28.2.2.1`).
State machines
   The transmit, receive and arbitration state diagrams of
   :clause:`Figure 28-16 <28>`, :clause:`Figure 28-17 <28>` and
   :clause:`Figure 28-18 <28>`.
1000BASE-T next pages
   The message page and two unformatted pages of
   :clause:`Table 40-4 <40>`, with the port type, the master and slave
   configuration and an 11-bit seed, and the master and slave resolution of
   :clause:`40.5.2`. The seed comes from a random or pseudo-random source
   chosen by the implementer (:clause:`40.5.2`).
Timers
   The timers of :numref:`tab-phy-autoneg-timers`.

A counter that measures a time :math:`T_\text{max}` with a clock of
frequency :math:`f_\text{clk}` needs

.. math::

   N_\text{bits} = \left\lceil \log_2 (T_\text{max} \times f_\text{clk}) \right\rceil

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`N_\text{bits}`
     - Counter length; :math:`\lceil\,\rceil` rounds up
     - bit
   * - :math:`T_\text{max}`
     - Longest time the counter measures
     - s
   * - :math:`f_\text{clk}`
     - Frequency of the clock the counter counts
     - Hz

The longest timer, break_link_timer, runs to 1.5 s. Counted with the
transceiver's 25 MHz reference,
:math:`\log_2(1.5 \times 25 \times 10^{6}) = 25.2`, so it needs a 26-bit
counter (estimate). A prescaler shares one fast counter among all the
timers.

.. _phy-int-registers:

The standard registers let the same software drive both configurations
----------------------------------------------------------------------

:clause:`22.2.4` defines a set of 16-bit registers that every transceiver
provides, so the same software can control any of them. An integrated
transceiver presents them as on-chip registers that the processor reads
and writes directly. Keeping the standard layout lets one software driver
handle the external transceiver of one board configuration and the
integrated one of the other (:numref:`tab-phy-int-registers`).

.. list-table:: Standard transceiver registers (:clause:`Table 22-6 <22>`)
   :name: tab-phy-int-registers
   :header-rows: 1
   :widths: 18 82

   * - Address
     - Register
   * - 0
     - Control: reset, loopback, speed, enable and restart autonegotiation,
       power down
   * - 1
     - Status: link up, autonegotiation complete, abilities
   * - 2 and 3
     - Identifier of the maker and model
   * - 4
     - Autonegotiation advertisement, this end's base page
   * - 5
     - Link partner's base page
   * - 6
     - Autonegotiation expansion
   * - 7
     - Next page to transmit
   * - 8
     - Link partner's next page
   * - 9
     - 1000BASE-T control (master and slave configuration, abilities, test
       modes)
   * - 10
     - 1000BASE-T status (master and slave result, receiver status)
   * - 11 and 12
     - Power over Ethernet sourcing equipment control and status
   * - 13 and 14
     - Indirect access to further register banks (MMD access control and
       data)
   * - 15
     - Extended status (1000 Mbit/s abilities)
   * - 16 to 31
     - Specific to each maker

Bits 13 to 15 of register 9 select the transmitter test modes
(:clause:`40.6.1.1.2`, :clause:`Table 40-7 <40>`). A transceiver without a
GMII must still provide a way to enable them for conformance testing, so
the integrated transceiver provides them through register 9.

.. _phy-int-control-questions:

Open questions
--------------

* Which of registers 11 to 14 the integrated transceiver implements, and
  what it puts in the maker-specific registers 16 to 31.
* The source of randomness for the master and slave seed.
