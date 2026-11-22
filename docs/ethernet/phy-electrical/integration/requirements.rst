.. _phy-int-reqs-page:

What the integrated transceiver must do
=======================================

This page lists the interface, the blocks and the requirements of one
integrated 1000BASE-T port, and points to the limits of the slower
speeds.

.. _phy-int-interface:

The forwarding logic sees one byte per 8 ns in each direction
-------------------------------------------------------------

The :term:`forwarding logic` exchanges one byte per 8 ns with each port in
each direction, with a data-valid flag and an error flag: TX_EN and TX_ER
on transmit, RX_DV and RX_ER on receive, as on the gigabit media
independent interface (:clause:`35`). An external transceiver carries the
same signals over :term:`RGMII` (:ref:`arch-rgmii`), so the forwarding
logic is the same whether the transceiver is external or on the chip.

On receive, the bytes are timed by the clock recovered from the cable, and
the :ref:`rate-matching buffer <arch-rate-matching>` moves them onto
evampire's own clock, as with RGMII.

.. _phy-int-blocks:

One port has four analogue channels and shared logic
----------------------------------------------------

:numref:`tab-phy-int-blocks` lists the blocks of one port, with the number
of copies and the page that specifies each. :numref:`fig-phy-blocks` shows
how they connect.

.. list-table:: Blocks of one integrated 1000BASE-T port
   :name: tab-phy-int-blocks
   :header-rows: 1
   :widths: 50 15 35

   * - Block
     - Copies
     - Specified in
   * - DAC and line driver
     - 4
     - :doc:`transmitter`
   * - Termination and line protection
     - 4
     - :doc:`transmitter`
   * - Hybrid, optional analogue echo canceller, amplifier and ADC
     - 4
     - :doc:`receiver`
   * - Echo canceller, three crosstalk cancellers and two equalisers
     - 4
     - :doc:`signal-processing`
   * - Trellis decoder with decision feedback
     - 1
     - :doc:`signal-processing`
   * - Scrambler, encoder and delimiters
     - 1
     - :ref:`phy-1000base-t-coding`
   * - Clock synthesis and recovery
     - 1
     - :doc:`clock-recovery`
   * - Link pulses, autonegotiation and registers
     - 1
     - :doc:`control`

.. _phy-int-1000-reqs:

The 1000BASE-T requirements are set at the connector
----------------------------------------------------

The standard tests the transmitter with four fixed *test modes*, patterns
sent on command so that the output can be measured with no receiver
(:clause:`40.6.1.1.2`). :numref:`tab-phy-int-reqs` lists the requirements
that the analogue blocks must meet.

.. list-table:: 1000BASE-T requirements on one port
   :name: tab-phy-int-reqs
   :header-rows: 1
   :widths: 50 25 25

   * - Quantity
     - Limit
     - Subclause
   * - Peak output in test mode 1 (V)
     - 0.67 to 0.82
     - :clause:`40.6.1.2.1`
   * - Difference of each test-mode-1 peak from their average (%)
     - less than 1
     - :clause:`40.6.1.2.1`
   * - Output kept 500 ns after a peak, in test mode 1 (%)
     - more than 73.1
     - :clause:`40.6.1.2.2`
   * - Peak distortion in test mode 4 (mV)
     - less than 10
     - :clause:`40.6.1.2.4`
   * - Common-mode output, peak-to-peak (mV)
     - less than 50
     - :clause:`40.8.3.3`
   * - Return loss, 1 MHz to 40 MHz (dB)
     - at least 16
     - :clause:`40.8.3.1`
   * - Return loss, 40 MHz to 100 MHz (dB)
     - at least :math:`10 - 20\log_{10}(f/80)`, with :math:`f` in MHz
     - :clause:`40.8.3.1`
   * - Master clock jitter, peak-to-peak (ns)
     - less than 1.4
     - :clause:`40.6.1.2.5`
   * - Master jitter after a 5 kHz high-pass filter, peak-to-peak (ns)
     - less than 0.3
     - :clause:`40.6.1.2.5`
   * - Slave jitter after a 32 kHz high-pass filter, above the master's
       (ns)
     - at most 0.4
     - :clause:`40.6.1.2.5`
   * - Symbol rate error (parts per million)
     - within ±100
     - :clause:`40.6.1.2.6`
   * - Bit error ratio over a compliant link
     - below :math:`10^{-10}`
     - :clause:`40.6.1.3.1`

The return-loss limit falls from 16 dB at 40 MHz to
:math:`10 - 20\log_{10}(100/80) = 8.1` dB at 100 MHz. The slave's
unfiltered jitter, measured against the master's clock, is also less than
1.4 ns (:clause:`40.6.1.2.5`).

.. _phy-int-slower-reqs:

The slower speeds have their own limits
---------------------------------------

The integrated transceiver also supports the slower speeds, and meets
the limits of :numref:`tab-phy-100base-tx` for 100BASE-TX and
:numref:`tab-phy-10base-t` for 10BASE-T. :doc:`slower-speeds` lists the
blocks they add.
