Electrostatic discharge protection
==================================

These pages explain how the I/O cells of the gf180mcu process protect a
chip against electrostatic discharge (ESD): tests rated in thousands of
volts, in a process whose transistors are rated for 5 V. They simulate the
foundry's own cells with the foundry's device models, and show what limits
the protection. They are written for integrated circuit designers who have
not designed ESD protection.

Every pad of the gf180mcu I/O library has ESD protection
(:doc:`io-cells`). The pins of evampire that are wired to connectors also
face the system-level ESD test of a finished product, which is much harsher
than the test a chip is rated by (:doc:`events`).

.. toctree::
   :maxdepth: 1
   :hidden:

   events
   io-cells
   simulation
   results-hbm
   results-iec
   higher-levels
   references

What each page covers:

* :doc:`events`: the ESD tests, their levels, and why a kilovolt test
  leaves only volts on the pin.
* :doc:`io-cells`: the protection inside the gf180mcu I/O cells, and the
  limits of each device as the foundry measured them.
* :doc:`simulation`: how the simulation is built from the foundry's
  netlists and models, and how its models are checked against measurement.
* :doc:`results-hbm`: simulated human body model discharges into the
  bidirectional pad, with and without the rail clamp.
* :doc:`results-iec`: simulated :std:`IEC 61000-4-2` discharges, and every
  test level of both tests compared with the measured limits.
* :doc:`higher-levels`: what a pin needs to survive the system-level test
  at 8 kV contact or 15 kV air discharge, and the ways to provide it.
* :doc:`references`: the documents, netlists and tools cited.
