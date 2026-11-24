.. _phy-int-risks:

Risks and order of work
=======================

This page lists the main risks of the integrated 1000BASE-T transceiver,
how each can be checked before the whole transceiver exists, the
alternatives to each usual approach, and an order of work in which each
block can be checked on its own.

.. _phy-int-risk-table:

Risks and early checks
----------------------

An :wikipedia:`FPGA <Field-programmable_gate_array>` (field-programmable
gate array), a reprogrammable logic chip, can run the signal processing on
real cable samples before it is built in silicon.
:numref:`tab-phy-int-risks` lists the risks.

.. list-table:: Main risks and early checks
   :name: tab-phy-int-risks
   :header-rows: 1
   :widths: 25 40 35

   * - Risk
     - Approaches
     - Early check
   * - Signal-processing area and power (:doc:`signal-processing`)
     - Shift-and-add cancellers, look-ahead decoder, tap counts for the
       chosen reach, choice of cells and supply
     - Synthesis and power estimation for gf180mcu; FPGA run on captured
       cable samples
   * - The 8 ns decision loop (:ref:`phy-int-decision-loop`)
     - Look-ahead, pipelined decoder, faster cells for the loop only
     - Static timing of the loop at the slow corner after synthesis and
       layout
   * - Four ADCs of about 7 effective bits (:ref:`phy-int-adc`)
     - Folding, pipelined, time-interleaved or successive-approximation;
       fewer bits with analogue echo cancelling or shorter reach
     - A test chip with one ADC, measured at 125 MS/s
   * - Hybrid without transformers (:ref:`phy-int-echo`)
     - Replica hybrid on the coupled pins, analogue echo canceller
     - Echo measured on a test chip with a real cable and the chosen
       isolation route
   * - Clock recovery and training time (:doc:`clock-recovery`)
     - PLL and phase interpolator; digital timing recovery
     - Jitter of a test-chip PLL; timing recovery on an FPGA
   * - Line driver linearity and swing (:doc:`transmitter`)
     - Current-steering DAC or matched voltage-mode driver
     - The transmitter test modes, which need no receiver

.. _phy-int-alternatives:

Alternatives to the usual approaches
------------------------------------

:numref:`tab-phy-int-alternatives` lists approaches that the reference
designs did not use, why, and whether the reason applies to evampire.

.. list-table:: Alternatives to the usual approaches
   :name: tab-phy-int-alternatives
   :header-rows: 1
   :widths: 30 35 35

   * - Alternative
     - Why the reference designs used another approach
     - For evampire
   * - Analogue FIR filters and decision-feedback equaliser
       (:ref:`phy-int-analogue-alternatives`)
     - Digital logic was cheaper in their 0.25 µm and smaller processes
     - gf180mcu logic uses 5 V transistors, so the reason is weaker; open
   * - Coefficient adaptation in slower hardware or software
       (:ref:`phy-int-adapt-split`)
     - The reference designs adapt in dedicated hardware
     - Open; depends on convergence within the maxwait_timer
   * - Driver and receiver merged into one circuit (:ref:`phy-int-echo`)
     - Published at 28 nm only
     - Open; needs a gf180mcu design
   * - OSU 3.3 V cells or custom cells (:ref:`phy-int-cell-options`)
     - The foundry libraries are the characterised default
     - Open; faster per stage, larger per gate

.. _phy-int-order:

Order of work
-------------

#. Reference clock and PLL, checked alone by measuring frequency and
   jitter.
#. Line interface, termination and the chosen isolation route, checked
   by measuring return loss.
#. DAC and line driver, checked with the transmitter test modes.
#. Link pulse driver and comparator, autonegotiation logic and registers,
   checked against a commercial transceiver, which reports what it
   receives.
#. Hybrid, amplifier and ADC, checked by capturing samples while
   transmitting into a real cable.
#. Signal processing, developed in simulation and on an FPGA with the
   samples from step 5, then synthesised for gf180mcu.
#. Byte interface to the forwarding logic, the same interface as the
   :ref:`RGMII block <arch-rgmii>`, checked with the forwarding logic.

The 100BASE-TX and 10BASE-T blocks of :doc:`slower-speeds` reuse
steps 3, 5 and 6. :numref:`fig-phy-int-test-bench` shows the bench for
steps 4 to 6.

.. graphviz:: test-bench.dot
   :name: fig-phy-int-test-bench
   :caption: The early-check bench: a test chip on a real cable to a
             commercial transceiver, with its ADC samples captured to an
             FPGA.
   :alt: A test chip with the DAC, driver, hybrid, ADC, link pulses and
         autonegotiation connects through
         a real cable to a commercial transceiver, which reports what it
         receives. The test chip's captured ADC samples go to an FPGA that
         runs the signal processing.
   :align: center
