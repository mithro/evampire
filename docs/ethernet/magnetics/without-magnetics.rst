Ports without transformers
==========================

These pages explain how an Ethernet port can do the jobs of the magnetics without coupling transformers.

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
   Two candidate transformer-free ports, the specifications they set for the
   circuits on evampire, and the IEEE 802.3 requirements they meet.
:doc:`gigabit-risk`
   What can limit capacitor-coupled gigabit Ethernet over a long cable, as a
   function of cable reach, and how to find out.

.. toctree::
   :hidden:

   events
   coupling-capacitors
   without-transformer
   isolation
   front-ends
   gigabit-risk
