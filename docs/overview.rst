Overview
========

This page introduces what evampire does: how it passes Ethernet traffic
between its ports, what its processor does with that traffic, and how it
moves power between Ethernet and USB Type-C. :doc:`requirements` lists every
requirement in detail, and the :doc:`glossary` describes each term.

evampire is a three-port Ethernet hub on one chip
-------------------------------------------------

evampire is a three-port :wikipedia:`gigabit <Gigabit_Ethernet>`
:wikipedia:`Ethernet hub <Ethernet_hub>` on a single chip. It has two
external ports, called port A and port B, and one internal port.

Port A and port B
   Each external port connects to an Ethernet cable through an
   :term:`Ethernet transceiver`, the circuit that drives and receives the
   electrical signals on the cable (see :doc:`ethernet/phy-electrical/index`).
   Each port ends in an :term:`RJ45` socket (see :doc:`ethernet/magnetics/index`).
   The transceiver is a separate chip or part of evampire, depending on the
   board configuration (:numref:`tab-power-board-configs`).

The internal port
   The internal port connects to a small :wikipedia:`RISC-V` processor
   inside the chip.

Traffic passes between port A and port B as it arrives
------------------------------------------------------

Ethernet carries data in :term:`frames <frame>`, messages that are
normally up to 1522 bytes long and each start with the address of the device they are sent to.
A frame arriving on port A is sent out of port B, and a frame arriving on
port B is sent out of port A. The few exceptions are listed in
:ref:`the forwarding requirements <req-forwarding>`.

evampire does not wait for a whole frame to arrive before it starts sending
it on. Each byte is passed to the other side a few clock cycles after it
arrives. This is called :term:`cut-through forwarding`. It needs only a few
bytes of storage on each path, not a whole frame.

The processor receives selected frames and sends its own
--------------------------------------------------------

The processor sees a copy of the frames whose destination address matches a
filter that it sets. It can also send frames of its own, which evampire
sends in the gaps between the frames it forwards. The processor's network
traffic is below 1 Mbit/s, so it does not need to keep up with gigabit
traffic.

The processor moves power between Ethernet and USB Type-C
---------------------------------------------------------

The processor also manages power. A board built around evampire can be
powered from an Ethernet cable and supply power over USB Type-C, or be
powered from USB Type-C and supply power over an Ethernet cable. The
processor negotiates the role and the power level on each port (see
:doc:`power/index`).
