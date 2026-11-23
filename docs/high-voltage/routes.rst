.. _hv-routes:

Choosing a route
================

This page sets the routes for holding a circuit above the substrate side by
side, and lists the measurements that would decide between them.

The routes side by side
-----------------------

Each route moves the voltage to the substrate onto a different structure
(:numref:`tab-hv-routes`). The well routes are explained on
:doc:`junctions`, the rings, plates, thin layer and resistor chain on
:doc:`grading`, the insulator routes on :doc:`dielectric`, and metal-gate sensing on
:doc:`metal-gate`. They combine: a high-voltage well can have a
field plate and floating rings, and polysilicon devices on the field oxide
can bias the rings.

.. list-table:: Routes for holding a circuit above the substrate
   :name: tab-hv-routes
   :header-rows: 1
   :widths: 22 26 26 26

   * - Route
     - Holds the voltage
     - Costs
     - Decided by
   * - Plain well
     - Well edge to substrate
     - Nothing beyond the well
     - Edge, which holds 10 V minimum
   * - Rounded, spaced well
     - Well edge to substrate
     - Area around the well
     - Tests on rounded wells
   * - Floating rings
     - Steps between rings
     - Area around the well
     - Ring spacing, from models and tests
   * - Field plates
     - Oxide and the surface beside the edge
     - Plates over the edge
     - Insulator thickness under each step
   * - Depleted thin layer
     - The whole layer, evenly
     - Area, and a layer of the right charge
     - Charge per area of the available N layers
   * - Resistor chain
     - Resistor over the surface
     - Steady current, resistor area
     - Strength of the oxide under it
   * - Devices on the oxide
     - Field oxide
     - Weaker devices than in the crystal
     - Strength of the field oxide
   * - Metal-gate sensing
     - Insulator under a metal plate
     - Measured, drifting threshold
     - Charge in the dielectrics
   * - Removing the substrate
     - Insulating carrier and oxide
     - Extra steps after the foundry
     - Process cost and yield
   * - Second die
     - Gap between dies
     - A second die and its package
     - The barrier between the dies

Test structures would answer most of the questions
--------------------------------------------------

Most of the open values are breakdown voltages and doping that a few test
structures on a gf180mcu run would measure directly:

* N-wells with square and rounded corners, at several spacings from each
  other and from P-type taps, swept to breakdown against the substrate.
* N-wells surrounded by floating rings at several spacings.
* An N-well with a stepped field plate of polysilicon and metal.
* A large N-well and a large deep N-well for capacitance measurements
  against voltage, which give the substrate's doping profile.
* Polysilicon strips over the field oxide, and metal plates over each
  dielectric, swept to breakdown against the substrate.
* Field transistors gated by polysilicon and by each metal layer, in both
  the 3.3 V and the 6 V areas, which give the doping under the field
  oxide.
* Metal-gate transistors with the gate on each metal layer, over field
  oxide and over active silicon, at several channel lengths, measured for
  threshold, current and drift over temperature and time.

Device simulation of the same structures, with the gf180mcu doping as an
input, would narrow the dimensions to put on the test run.

Open questions
--------------

* What is the doping profile of the gf180mcu substrate, and of the N-well
  and deep N-well? The models give estimates only (:doc:`junctions`).
* What sets the 14 V typical breakdown of the N-well to the substrate: the
  curvature of its edge, a more heavily doped layer at the surface, or
  something else? (:doc:`junctions`)
* What does the deep N-well hold to the substrate? Only the model's fitted
  value of about 30 V exists (:doc:`substrate`).
* What do the field oxide and the dielectrics above it hold to the
  substrate, continuously and as a short pulse?
* Does an available N layer have a charge per area close enough to the
  RESURF value? (:doc:`grading`)
* What threshold does a transistor gated by each metal layer have, in the
  3.3 V and the 6 V areas? Only the Metal1 value in the 6 V area is
  published, and the extrapolation to the other layers is untested
  (:doc:`metal-gate`).
* How much charge do the dielectrics hold, and how far does it drift with
  bias, temperature and time, and with moisture on the passivation?
  (:doc:`metal-gate`)
* How much gate voltage does the inversion layer need to climb the
  sidewalls of the field oxide to the source and drain?
  (:doc:`metal-gate`)
* How long must the channel of a metal-gate transistor be for the gate to
  control it, and how close may low-voltage metal sit beside a plate at
  57 V? (:doc:`metal-gate`)
* Can the silicon under a metal gate be left without source and drain
  doping and without polysilicon, for a channel over active silicon instead
  of field oxide? (:doc:`metal-gate`)
* Can wafers from a gf180mcu run be processed afterwards to remove the
  substrate, and at what cost? (:doc:`dielectric`)
