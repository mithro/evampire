Ports with magnetics
====================

In a standard Ethernet port, coupling transformers connect the transceiver
to the RJ45 socket.

:doc:`cable`
   The four twisted pairs of an Ethernet cable, the RJ45 pins they use, and
   the two pin assignments, MDI and MDI-X.
:doc:`standard-port`
   The parts of a standard port: a transformer and a common-mode choke on
   each pair, centre taps and a common-mode termination.
:doc:`functions`
   Each job the magnetics do, with the IEEE 802.3 requirement it meets.
:doc:`matching-and-droop`
   Matching the 100 Ω cable, and passing the low frequencies of the signal:
   return loss, droop and the 350 µH inductance.
:doc:`poe`
   How Power over Ethernet current passes through the centre taps, and how
   the transformer keeps the data circuits out of detection.
:doc:`first-version`
   Choosing and placing standard magnetics on a first-version board.

.. toctree::
   :hidden:

   cable
   standard-port
   functions
   matching-and-droop
   poe
   first-version
