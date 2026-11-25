Ethernet
========

Between evampire's pins and the Ethernet cable, the data passes through an
Ethernet transceiver and coupling transformers. Which parts are on evampire
and which are separate depends on the board configuration (see
:numref:`tab-power-board-configs`).

An :term:`Ethernet transceiver`
(:wikipedia:`Ethernet physical layer <Ethernet_physical_layer>`) turns
digital data into the analogue signals on the cable. An external
transceiver talks to evampire over a digital interface,
:wikipedia:`RGMII <Media-independent_interface>`. Coupling
:wikipedia:`transformers <Transformer>`, often called the
:term:`magnetics`, connect the transceiver to the
:wikipedia:`RJ45 <8P8C>` socket. :doc:`phy-electrical/index` and
:doc:`magnetics/index` explain how these parts work and what evampire needs
to do the same jobs itself.

:numref:`fig-ethernet-path` shows the path and the pages that cover each
part.

.. graphviz:: path.dot
   :name: fig-ethernet-path
   :caption: The path of the data from evampire to the cable, and the pages
             that cover each part.
   :alt: A row of blocks joined by lines: evampire, the Ethernet
         transceiver (external or integrated), the magnetics, the RJ45
         socket and the cable. The link from evampire to an external
         transceiver is RGMII, digital; the link from the transceiver to
         the magnetics is analogue. Labels below name the transceiver pages
         and the magnetics pages.
   :align: center

:doc:`rgmii/index`
   The digital interface between evampire and an external Ethernet
   transceiver: signals, clocking, timing and electrical levels.
:doc:`phy-electrical/index`
   How an Ethernet transceiver turns digital data into the analogue signals
   on the cable, and back again.
:doc:`magnetics/index`
   How the transceiver connects to the RJ45 socket through coupling
   transformers, and the jobs those transformers do.

.. toctree::
   :maxdepth: 2
   :hidden:

   rgmii/index
   phy-electrical/index
   magnetics/index
