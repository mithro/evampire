Electrostatic discharge protection
==================================

The I/O cells of the gf180mcu process protect a chip against
electrostatic discharge (ESD) tests rated in thousands of volts, although
the process's transistors are rated for 5 V. Simulating the foundry's own
cells with the foundry's device models shows what limits that protection.

Every pad of the gf180mcu I/O library has ESD protection
(:doc:`io-cells`). The pins of evampire that are wired to connectors also
face the system-level ESD test of a finished product, which is much harsher
than the test a chip is rated by (:doc:`events`).

.. toctree::
   :maxdepth: 1
   :hidden:

   events
   cells
   discharges
   higher-levels
   references

* :doc:`events`: the ESD tests, their levels, and why a kilovolt test
  leaves only volts on the pin.
* :doc:`cells`: the protection inside the gf180mcu I/O cells, in their
  netlists and in their mask layouts.
* :doc:`discharges`: the simulation of the foundry's netlists and models,
  and the human body model and :std:`IEC 61000-4-2` discharges it gives.
* :doc:`higher-levels`: what a pin needs to survive the system-level test
  at 8 kV contact or 15 kV air discharge, and the ways to provide it.
* :doc:`references`: the documents, netlists and tools cited.
