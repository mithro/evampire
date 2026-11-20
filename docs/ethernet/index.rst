Ethernet
========

These pages follow the path of the data from the chip's pins to the Ethernet
cable. The chip talks to an external Ethernet transceiver over a digital
interface. The transceiver turns that digital data into the analog signals on
the cable. Coupling transformers (often called the "magnetics") then connect
the transceiver to the RJ45 socket.

.. toctree::
   :maxdepth: 2

   rgmii
   phy-electrical
   magnetics
