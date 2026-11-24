Power from a USB Type-C port
============================

These pages explain how a USB Type-C port supplies power before any USB Power Delivery message is sent.

:doc:`type-c-power`
   The source, the sink, the connector and the configuration channel wires.
:doc:`resistor-advertisement`
   How the source's pull-up tells the sink how much current it may draw at 5 V.
:doc:`attach`
   How two dual-role ports find each other and settle on who supplies power.
:doc:`start-up`
   The power a USB Type-C charger makes available before any negotiation.

.. toctree::
   :hidden:

   type-c-power
   resistor-advertisement
   attach
   start-up
