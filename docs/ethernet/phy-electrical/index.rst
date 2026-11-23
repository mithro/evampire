Ethernet transceivers
=====================

These pages explain how an :term:`Ethernet transceiver` turns bytes into
the analogue signals on a twisted-pair Ethernet cable and back, and what
evampire needs in order to build the transceiver on the chip. They are
written for integrated circuit designers who have not worked on Ethernet.

Each board configuration either uses an external transceiver or integrates
it on evampire (:numref:`tab-power-board-configs`). Every port runs
1000BASE-T, gigabit Ethernet over four pairs, as well as 100BASE-TX and
10BASE-T, in both configurations (:ref:`the transceiver requirements <req-transceivers>`).

.. toctree::
   :maxdepth: 1
   :hidden:

   job
   10base-t
   100base-tx
   1000base-t-coding
   1000base-t-echo
   1000base-t-receiver
   autonegotiation
   line-drivers
   integration/index
   references

How a transceiver works, simplest speed first:

* :doc:`job`: where the transceiver sits, the three speeds, and the four
  ways the cable changes the signal.
* :doc:`10base-t`: 10 Mbit/s with two-level Manchester coding and link
  pulses.
* :doc:`100base-tx`: 100 Mbit/s with 4B5B coding, scrambling and
  three-level MLT-3 signalling.
* :doc:`1000base-t-coding`: 1000 Mbit/s on four pairs at once, five
  signal levels, the shaping filter, scrambling and the trellis code.
* :doc:`1000base-t-echo`: the channel limits, and how the hybrid and the
  echo and crosstalk cancellers let each pair carry both directions.
* :doc:`1000base-t-receiver`: equalisers, master and slave clocking, pair
  delays, the blocks of a gigabit transceiver and the arithmetic they do.
* :doc:`autonegotiation`: how two transceivers agree on speed, duplex and
  which end is master.
* :doc:`line-drivers`: current-mode and voltage-mode line drivers, and how
  each connects to the transformer centre tap.

Building the transceiver on evampire:

* :doc:`integration/index`: the integration study, from the requirements
  of each speed to area and power illustrations and the order of work.

Sources:

* :doc:`references`: the standard, test suites, datasheets and papers
  cited on these pages.
