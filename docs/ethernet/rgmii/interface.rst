Interface specification
=======================

RGMII is defined by two versions of an industry specification and by the
datasheets of the transceivers that implement it.

:doc:`signals`
   What RGMII is, its six signals in each direction, and how it relates to
   MII and GMII.
:doc:`data`
   How bytes travel at 1000, 100 and 10 Mbit/s, the control signal coding,
   and the link status sent between frames.
:doc:`frames`
   The fields of an Ethernet frame, the preamble and start frame delimiter,
   and the gap between frames.
:doc:`timing`
   Why the clock is delayed by 2 ns, where the delay is added, and the
   timing limits.
:doc:`electrical`
   Logic levels in the specifications and in transceivers, and the board
   layout rules.
:doc:`mdio`
   The two-wire management interface and the transceiver registers evampire
   uses.

.. toctree::
   :hidden:

   signals
   data
   frames
   timing
   electrical
   mdio
