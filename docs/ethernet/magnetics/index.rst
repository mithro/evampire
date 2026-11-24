Magnetics and the RJ45 socket
=============================

These pages explain how an :term:`Ethernet transceiver` connects to the
:term:`RJ45` socket, what the coupling transformers between them, the
:term:`magnetics`, do, and how a port can do the same jobs without them.
Which board configuration uses which kind of port is given in
:ref:`board configurations <tab-power-board-configs>`.

:doc:`with-magnetics`
   The cable, a standard port with magnetics, what each part does, matching
   and droop, Power over Ethernet through the centre taps, and choosing
   magnetics for the first version.
:doc:`without-magnetics`
   The events a port must survive, coupling capacitors, each job done
   without a transformer, isolation, candidate front ends, and the risks for
   gigabit Ethernet.
:doc:`references`
   The documents cited on these pages.

.. toctree::
   :hidden:

   with-magnetics
   without-magnetics
   references
