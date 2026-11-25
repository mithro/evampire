RGMII design in evampire
========================

evampire implements its two RGMII ports with gf180mcu pad cells,
double-data-rate port logic, and a processor policy that keeps both ports
at the same speed.

:doc:`io-cells`
   The pins, the I/O supply, the timing of the gf180mcu pad cells, and the
   choice of standard or custom I/O cells and of RGMII or GMII.
:doc:`port-logic`
   The double-data-rate stages, the source of the 2 ns delay, the interface
   to the forwarding logic and the clock domains.
:doc:`speed-policy`
   How the processor keeps both ports at the same speed.

.. toctree::
   :hidden:

   io-cells
   port-logic
   speed-policy
