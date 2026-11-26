Simulated ESD discharges
========================

A circuit simulation of the foundry's own pad netlists and device models
shows the voltage and current that each ESD test puts on a pad.

:doc:`simulation`
   How the simulation is built from the foundry's netlists and models, and
   how its models are checked against measurement.
:doc:`results-hbm`
   Simulated human body model discharges into the bidirectional pad, with
   and without the rail clamp.
:doc:`results-iec`
   Simulated :std:`IEC 61000-4-2` discharges, and every test level of both
   tests compared with the measured limits.

.. toctree::
   :hidden:

   simulation
   results-hbm
   results-iec
