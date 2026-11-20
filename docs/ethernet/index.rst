Ethernet
========

These pages follow the path of the data from the chip's pins to the Ethernet
cable.

In the first version, evampire talks to an external Ethernet transceiver over
a digital interface (RGMII). The transceiver turns that digital data into the
analog signals on the cable, and coupling transformers (often called the
"magnetics") connect the transceiver to the RJ45 socket.

The full design integrates the transceiver on evampire and connects the
cable without coupling transformers. The pages on the transceiver and on the
magnetics therefore explain both how these parts work and what evampire needs
to do the same jobs itself.

.. toctree::
   :maxdepth: 2

   rgmii
   phy-electrical
   magnetics
