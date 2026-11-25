Ethernet transceivers
=====================

An :term:`Ethernet transceiver` turns bytes into the analogue signals on a
twisted-pair Ethernet cable and back.

Each board configuration either uses an external transceiver or integrates
it on evampire (:numref:`tab-power-board-configs`). Every port runs
1000BASE-T, gigabit Ethernet over four pairs, as well as 100BASE-TX and
10BASE-T, in both configurations (:ref:`the transceiver requirements <req-transceivers>`).

:doc:`operation`
   How a transceiver works, simplest speed first: the job and the cable,
   10BASE-T, 100BASE-TX, 1000BASE-T, autonegotiation and line drivers.
:doc:`integration/index`
   Building the transceiver on evampire, from the requirements of each speed
   to area and power illustrations and the order of work.
:doc:`references`
   The standard, test suites, datasheets and papers cited for the
   transceivers.

.. toctree::
   :hidden:

   operation
   integration/index
   references
