Transceiver operation
=====================

An Ethernet transceiver runs at 10, 100 and 1000 Mbit/s, each speed with
its own coding and signalling, and each adding techniques to the slower
one before it.

:doc:`job`
   Where the transceiver sits, the three speeds, and the four ways the cable
   changes the signal.
:doc:`10base-t`
   10 Mbit/s with two-level Manchester coding and link pulses.
:doc:`100base-tx`
   100 Mbit/s with 4B5B coding, scrambling and three-level MLT-3 signalling.
:doc:`1000base-t-coding`
   1000 Mbit/s on four pairs at once, five signal levels, the shaping
   filter, scrambling and the trellis code.
:doc:`1000base-t-echo`
   The channel limits, and how the hybrid and the echo and crosstalk
   cancellers let each pair carry both directions.
:doc:`1000base-t-receiver`
   Equalisers, master and slave clocking, pair delays, the blocks of a
   gigabit transceiver and the arithmetic they do.
:doc:`autonegotiation`
   How two transceivers agree on speed, duplex and which end is master.
:doc:`line-drivers`
   Current-mode and voltage-mode line drivers, and how each connects to the
   transformer centre tap.

.. toctree::
   :hidden:

   job
   10base-t
   100base-tx
   1000base-t-coding
   1000base-t-echo
   1000base-t-receiver
   autonegotiation
   line-drivers
