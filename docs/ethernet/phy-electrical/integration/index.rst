.. _phy-int:

Integrating the transceiver on evampire
=======================================

These pages specify a 1000BASE-T :term:`Ethernet transceiver` built into
evampire on the gf180mcu process: what each speed requires, what each block
must do, the options for building it, and area and power illustrations.
They build on :doc:`../index`, which explains how a transceiver works.

The transceiver is integrated in the board configurations of
:numref:`tab-power-board-configs` that do not use an external one. Every
port runs 1000BASE-T; 100 Mbit/s and 10 Mbit/s are optional
(:ref:`req-transceivers`, :ref:`requirements-open-questions`). The cable
reach of the integrated transceiver is a parameter: results that depend on
it are given as functions of reach.

Three kinds of value appear on these pages:

Required
   A limit set by IEEE 802.3-2022 (:doc:`/standards`), cited by subclause.
Reference example
   A result published for another process or product. It shows that a
   function has been built and at what cost there; it is not a prediction
   for evampire.
Estimate
   A number worked out on these pages from required values, reference
   examples and stated assumptions. It is labelled as an estimate and is to
   be confirmed by implementation.

.. toctree::
   :maxdepth: 1
   :hidden:

   requirements
   transmitter
   receiver
   signal-processing
   clock-recovery
   control
   cells
   area-power
   slower-speeds
   risks

The pages, in the order of the signal and then of the design work:

* :doc:`requirements`: the interface to the forwarding logic, the blocks of
  one port and the requirements of each speed.
* :doc:`transmitter`: the DAC and line driver, the termination and the
  connection to the cable.
* :doc:`receiver`: the hybrid, echo removal and the ADC, as functions of
  cable reach.
* :doc:`signal-processing`: the adaptive filters, the work per symbol, and
  the 8 ns decision loop.
* :doc:`clock-recovery`: the reference clock, the sampling phase and jitter.
* :doc:`control`: link pulses, autonegotiation logic and the management
  registers.
* :doc:`cells`: the gf180mcu devices, the cell libraries and the supply
  options for the signal processing.
* :doc:`area-power`: area and power illustrations from published designs.
* :doc:`slower-speeds`: what 100BASE-TX and 10BASE-T add.
* :doc:`risks`: the main design risks, how each can be checked early, and
  the order of work.
