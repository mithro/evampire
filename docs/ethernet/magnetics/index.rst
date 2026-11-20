Magnetics and the RJ45 socket
=============================

These pages explain how an :term:`Ethernet transceiver` connects to the
:term:`RJ45` socket, what the coupling transformers between them, the
:term:`magnetics`, do, and how a port can do the same jobs without them.
Which board configuration uses which kind of port is given in
:ref:`board configurations <tab-power-board-configs>`.

How a port with magnetics works
-------------------------------

:doc:`cable`
   The four twisted pairs of an Ethernet cable, the RJ45 pins they use, and
   the two pin assignments, MDI and MDI-X.
:doc:`standard-port`
   The parts of a standard port: a transformer and a common-mode choke on
   each pair, centre taps and a common-mode termination.
:doc:`functions`
   Each job the magnetics do, with the IEEE 802.3 requirement it meets.
:doc:`matching-and-droop`
   Matching the 100 Ω cable, and passing the low frequencies of the
   signal: return loss, droop and the 350 µH inductance.
:doc:`poe`
   How Power over Ethernet current passes through the centre taps, and how
   the transformer keeps the data circuits out of detection.

Without coupling transformers
-----------------------------

:doc:`events`
   The voltages, currents and energies that reach an Ethernet port, which
   any replacement for the transformer must survive.
:doc:`coupling-capacitors`
   Ports that already work without transformers, and the size of the
   capacitors that replace the transformer in the data path.
:doc:`without-transformer`
   The options for each job of the magnetics when there is no transformer.
:doc:`isolation`
   The three routes to electrical isolation without a transformer, and the
   voltages the gf180mcu process can hold.
:doc:`front-ends`
   Two candidate transformer-free ports, the specifications they set for
   the circuits on evampire, and the IEEE 802.3 requirements they meet.
:doc:`gigabit-risk`
   What can limit capacitor-coupled gigabit Ethernet over a long
   cable, as a function of cable reach, and how to find out.

Reference
---------

:doc:`first-version`
   Choosing and placing standard magnetics on a first-version board.
:doc:`references`
   The documents cited on these pages.

.. toctree::
   :hidden:

   cable
   standard-port
   functions
   matching-and-droop
   poe
   events
   coupling-capacitors
   without-transformer
   isolation
   front-ends
   gigabit-risk
   first-version
   references
