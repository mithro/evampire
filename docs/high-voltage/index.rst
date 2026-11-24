High voltage above the substrate
================================

These pages explain how a circuit on a bulk silicon chip can sit tens of
volts above the chip's substrate, which is the question behind every
evampire circuit that connects to an Ethernet cable or a USB Type-C port
at its full voltage. They cover the physics of each route, from simplest
to most involved. The voltage limits of the gf180mcu process are listed on
:ref:`poe-limits`.

:doc:`substrate`
   Why splitting a voltage across a series stack does not protect a chip:
   every node also faces the shared substrate.
:doc:`junctions`
   How a reverse-biased junction holds voltage, why doping sets the limit,
   and why the edges of a well break down first.
:doc:`grading`
   Ways to spread a voltage gradually across the surface of the substrate,
   so that no single edge holds all of it.
:doc:`dielectric`
   Replacing the junction to the substrate with an insulator.
:doc:`metal-gate`
   Transistors whose gate is a metal layer, which sense a high-voltage node
   with only insulator between it and the silicon.
:doc:`routes`
   The routes side by side, and the measurements that would decide between
   them.
:doc:`references`
   The sources cited on these pages.

.. toctree::
   :hidden:

   substrate
   junctions
   grading
   dielectric
   metal-gate
   routes
   references
