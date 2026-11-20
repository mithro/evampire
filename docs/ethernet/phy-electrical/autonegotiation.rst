.. _phy-autoneg:

Agreeing on speed, duplex and the clock master
==============================================

This page explains how two transceivers use :term:`autonegotiation`
(:clause:`28`) to agree, before any data flows, on the speed, on whether
both directions may send at once, and, for 1000BASE-T, on which end is the
clock master.

*Full duplex* means both ends may transmit at once, the normal case today;
*half duplex* means only one at a time, a mode kept for old shared-cable
networks. 1000BASE-T requires autonegotiation (:clause:`40.5.1`).

.. _phy-flp:

Bursts of link pulses carry 16-bit pages
----------------------------------------

A transceiver that autonegotiates replaces each single
:ref:`link test pulse <phy-link-pulses>` of 10BASE-T with a *fast link
pulse burst* (:clause:`28.2.1.1`). A burst holds 17 *clock pulses* 125 µs
apart. Halfway between each pair of clock pulses there is either a *data
pulse*, meaning 1, or no pulse, meaning 0. One burst therefore carries
16 bits in 17 to 33 pulses (:numref:`fig-phy-flp`).

.. wavedrom::
   :caption: The start of a fast link pulse burst carrying the bits 1, 0, 1,
             not to scale.
   :name: fig-phy-flp
   :alt: Timing diagram of a line with short pulses: a clock pulse, a data
         pulse, a clock pulse, a gap where the data pulse is absent, a clock
         pulse, a data pulse and a clock pulse.

   { "signal": [
       { "name": "line", "wave": "hlhlhl..hlhlhl" },
       { "name": "pulse", "wave": "=======", "data": ["clock","1","clock","0","clock","1","clock"], "period": 2 }
     ],
     "config": { "hscale": 1 }
   }

:numref:`tab-phy-flp-timing` gives the timing. Each pulse has the shape of
a 10BASE-T link test pulse (:clause:`Figure 14-13 <14>`).

.. list-table:: Fast link pulse burst timing (:clause:`Table 28-1 <28>`)
   :name: tab-phy-flp-timing
   :header-rows: 1
   :widths: 46 18 18 18

   * - Interval
     - Minimum
     - Typical
     - Maximum
   * - Clock pulse to clock pulse (µs)
     - 111
     - 125
     - 139
   * - Clock pulse to data pulse (µs)
     - 55.5
     - 62.5
     - 69.5
   * - Burst to burst (ms)
     - 8
     - 16
     - 24
   * - Pulse width (ns)
     -
     - 100
     -

.. _phy-base-page:

The base page names the abilities
---------------------------------

The 16 bits of a burst form a *page*. The first, the *base page*, has the
fields of :numref:`tab-phy-base-page` (:clause:`28.2.1.2`,
:clause:`Figure 28-7 <28>`).

.. list-table:: Fields of the base page
   :name: tab-phy-base-page
   :header-rows: 1
   :widths: 20 30 50

   * - Bits
     - Field
     - Meaning
   * - D0 to D4
     - Selector
     - ``00001`` for IEEE 802.3 Ethernet (:clause:`Annex 28A <28>`)
   * - D5 to D11
     - Technology abilities A0 to A6
     - The modes this end supports (:numref:`tab-phy-abilities`)
   * - D12
     - Extended next page
     - This end can send extended next pages
   * - D13
     - Remote fault
     - This end has detected a fault
   * - D14
     - Acknowledge
     - This end has received the partner's page
   * - D15
     - Next page
     - More pages follow

.. list-table:: Technology ability bits of the base page
   (:clause:`Table 28B-1 <28>`)
   :name: tab-phy-abilities
   :header-rows: 1
   :widths: 15 85

   * - Bit
     - Ability
   * - A0
     - 10BASE-T
   * - A1
     - 10BASE-T full duplex
   * - A2
     - 100BASE-TX
   * - A3
     - 100BASE-TX full duplex
   * - A4
     - 100BASE-T4, an older 100 Mbit/s mode over four pairs
   * - A5
     - Symmetric pause frames, for flow control in full duplex
   * - A6
     - Asymmetric pause frames

Each end repeats its page. Once it has received at least three
consecutive matching bursts from its partner, it sets the acknowledge bit
(:clause:`28.2.1.2.5`).

.. _phy-next-pages:

1000BASE-T abilities travel in next pages
-----------------------------------------

The base page has no bit for 1000BASE-T. A 1000BASE-T transceiver sets the
next page bit and sends three more pages: a message page with message code
8, then two unformatted pages (:clause:`40.5.1.2`,
:clause:`Table 40-4 <40>`). They carry:

* whether 1000BASE-T is supported in half and in full duplex;
* the port type, a single-port device such as a computer's network
  interface or a multiport device such as a switch;
* whether the end is configured by hand as master or as slave;
* an 11-bit random number, the *seed*.

.. _phy-resolution:

Both ends apply the same rules to the same information
------------------------------------------------------

Each end compares its own abilities with its partner's and picks the
highest mode both support (:clause:`28.2.3.3`). For the three speeds on
these pages the order, highest first, is 1000BASE-T full duplex,
1000BASE-T half duplex, 100BASE-TX full duplex, 100BASE-TX half duplex,
10BASE-T full duplex and 10BASE-T half duplex (:clause:`Annex 28B.3 <28>`). Both
ends reach the same answer because they apply the same rules to the same
pages.

For 1000BASE-T the master is chosen by these rules
(:clause:`40.5.2`, :clause:`Table 40-5 <40>`):

#. An end configured as master becomes master, and one configured as slave
   becomes slave. If both are configured to the same role, the link fails
   with a configuration fault.
#. Otherwise a multiport device becomes master over a single-port device.
   A switch is therefore normally master for the devices plugged into it.
#. Otherwise the end that sent the larger seed becomes master. With equal
   seeds both ends draw new seeds and negotiate again; after seven failed
   attempts a configuration fault is declared.

A partner that does not autonegotiate sends 10BASE-T link pulses or the
100BASE-TX idle signal instead of bursts. The transceiver recognises that
speed from the signal itself, which is called *parallel detection*
(:clause:`28.2.3.1`).

.. _phy-autoneg-timers:

Timers bound every step
-----------------------

:numref:`tab-phy-autoneg-timers` lists the main autonegotiation timers by
their names in the standard.

.. list-table:: Main autonegotiation timers (:clause:`Table 28-9 <28>`)
   :name: tab-phy-autoneg-timers
   :header-rows: 1
   :widths: 38 22 40

   * - Timer
     - Range (ms)
     - What it times
   * - link_fail_inhibit_timer
     - 750 to 1000
     - Time for the chosen mode to report a working link
   * - break_link_timer
     - 1200 to 1500
     - Silence before negotiation restarts
   * - autoneg_wait_timer
     - 500 to 1000
     - Wait before accepting a mode found by parallel detection
   * - nlp_test_max_timer
     - 50 to 150
     - Time without link pulses before the link is declared down
   * - transmit_link_burst_timer
     - 5.7 to 22.3
     - Interval between bursts, without extended next pages

Once the result is chosen, the selected mode must report a working link
before link_fail_inhibit_timer expires. Otherwise the transceiver stays
silent for break_link_timer and starts again (:clause:`28.3.2`). For
1000BASE-T, the training described in :ref:`phy-master-slave` must finish
inside that time. For reference, the TI DP83867 datasheet gives 2 s to 3 s
as the typical time for autonegotiation with next pages to complete
([PHY-DP83867]_ section 7.4.3.8).
