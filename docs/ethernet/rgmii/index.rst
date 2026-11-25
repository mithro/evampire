RGMII interface
===============

In the board configuration with external transceivers
(:numref:`tab-power-board-configs`), evampire connects to each
:term:`Ethernet transceiver` over :term:`RGMII`, a digital interface with
six signals in each direction.

:doc:`interface`
   RGMII itself: signals, data, frames, timing, electrical levels and the
   management interface.
:doc:`design`
   evampire's RGMII pins and I/O cells, its port logic, and how it keeps
   both ports at the same speed.
:doc:`references`
   The datasheets, test suites and libraries cited for RGMII.

.. toctree::
   :hidden:

   interface
   design
   references
