RGMII interface
===============

How evampire connects to an external :term:`Ethernet transceiver` over
:term:`RGMII`, in the board configuration with external transceivers
(:numref:`tab-power-board-configs`). The pages are for a digital or analogue
chip designer who does not know Ethernet, and run from the interface itself
to evampire's design.

The interface
-------------

:doc:`signals`
   What RGMII is, its six signals in each direction, and how it relates to
   MII and GMII.
:doc:`data`
   How bytes travel at 1000, 100 and 10 Mbit/s, the control signal coding,
   and the link status sent between frames.
:doc:`frames`
   The fields of an Ethernet frame, the preamble and start frame delimiter,
   and the gap between frames.
:doc:`timing`
   Why the clock is delayed by 2 ns, where the delay is added, and the
   timing limits.
:doc:`electrical`
   Logic levels in the specifications and in transceivers, and the board
   layout rules.
:doc:`mdio`
   The two-wire management interface and the transceiver registers evampire
   uses.

evampire's design
-----------------

:doc:`io-cells`
   The pins, the I/O supply, the timing of the gf180mcu pad cells, and the
   choice of standard or custom I/O cells and of RGMII or GMII.
:doc:`port-logic`
   The double-data-rate stages, the source of the 2 ns delay, the interface
   to the forwarding logic and the clock domains.
:doc:`speed-policy`
   How the processor keeps both ports at the same speed.
:doc:`references`
   The datasheets, test suites and libraries cited on these pages.

.. toctree::
   :hidden:

   signals
   data
   frames
   timing
   electrical
   mdio
   io-cells
   port-logic
   speed-policy
   references
