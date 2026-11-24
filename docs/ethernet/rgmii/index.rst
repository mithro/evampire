RGMII interface
===============

How evampire connects to an external :term:`Ethernet transceiver` over
:term:`RGMII`, in the board configuration with external transceivers
(:numref:`tab-power-board-configs`). The pages are for a digital or analogue
chip designer who does not know Ethernet, and run from the interface itself
to evampire's design.

:doc:`interface`
   RGMII itself: signals, data, frames, timing, electrical levels and the
   management interface.
:doc:`design`
   evampire's RGMII pins and I/O cells, its port logic, and how it keeps
   both ports at the same speed.
:doc:`references`
   The datasheets, test suites and libraries cited on these pages.

.. toctree::
   :hidden:

   interface
   design
   references
