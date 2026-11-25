Power over Ethernet
===================

These pages explain how an Ethernet cable carries power, the signals the two
ends exchange before the power is switched on, and what evampire needs at
each end of the cable.

:term:`Power over Ethernet` puts a DC voltage of up to 57 V on the pairs of
an Ethernet cable, alongside the data. The end that supplies the power
checks that a compatible device is connected, and learns how much power it
wants, before switching the voltage on. A board built around evampire can
take either end (:ref:`power-roles`), and the software on evampire's
processor makes every power decision once it is running
(:ref:`req-power-control`). The rules come from IEEE 802.3 :clause:`33` and
:clause:`145`.

:doc:`fundamentals`
   The two ends, the pairs and the voltages, types and classes, and the
   power-up sequence.
:doc:`receiving`
   What a powered device must do, the blocks of a powered-device controller,
   and start-up before the processor runs.
:doc:`supplying`
   What power sourcing equipment must do, supplying power sequenced in
   software, and monitoring and limiting power.
:doc:`allocation`
   Negotiating over LLDP, the two classification methods, choosing the
   class to offer, sharing the budget, and ports that take either role.
:doc:`high-voltage`
   The voltages the process can hold, isolation from the cable, and the
   on-chip and external options for each function.
:doc:`references`
   The data sheets, papers and other sources cited on these pages.

.. toctree::
   :hidden:

   fundamentals
   receiving
   supplying
   allocation
   high-voltage
   references
