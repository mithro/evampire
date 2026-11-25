.. _ebat:

ebat
====

ebat is evampire with the Ethernet data functions removed. It keeps
evampire's Power over Ethernet and USB Type-C circuits and software
unchanged, and drops the transceivers, the forwarding between ports and
the network traffic, with their cost and complexity. ebat is its own die,
but not a separate design: its power side is evampire's, and any change to
evampire's power side applies to ebat. Like evampire, it is in design and
no silicon exists.

These pages describe only what removing the data functions changes.
Everything ebat keeps is described once, on the evampire pages that the
ebat pages link to.

ebat drops the data functions and keeps the power functions
-----------------------------------------------------------

:numref:`tab-ebat-compare` lists the functions of evampire and whether ebat
has each one.

.. list-table:: Functions of evampire and of ebat
   :name: tab-ebat-compare
   :header-rows: 1
   :widths: 50 25 25

   * - Function
     - evampire
     - ebat
   * - :ref:`Forwarding frames between ports A and B <req-forwarding>`
     - Yes
     - No
   * - :ref:`Ethernet transceivers or RGMII interfaces <req-transceivers>`
     - Yes
     - No
   * - :ref:`Frames to and from the processor <req-processor-delivery>`
     - Yes
     - No
   * - :ref:`Transceiver configuration interface <arch-config-interface>`
     - Yes
     - No
   * - :ref:`Physical Layer classification, in both roles <req-poe-classification>`
     - Yes
     - Yes, the same
   * - :ref:`Data Link Layer classification over LLDP <req-poe-classification>`
     - Yes
     - No
   * - Highest class requested when receiving Power over Ethernet
     - 8
     - 3
   * - Highest class offered when supplying Power over Ethernet
     - 8
     - 8
   * - :ref:`USB Type-C dual-role ports with USB Power Delivery <usbpd-two-ports>`
     - Yes
     - Yes, the same
   * - :ref:`USB serial port <req-usb-serial>`
     - Yes
     - Yes, the same
   * - :ref:`Control of the three voltage converters <req-converters>`
     - Yes
     - Yes, the same
   * - :ref:`Power monitoring, limiting and the start-up sequencer <req-power-control>`
     - Yes
     - Yes, the same

Power negotiation over LLDP needs Ethernet frames, so it goes with the data
functions. That lowers the highest class ebat can request when it receives
power, the one change on the power side. :doc:`power-without-lldp`
explains it.

The pages
---------

:doc:`requirements`
   The evampire requirements that ebat drops, and the one it changes.
:doc:`architecture`
   The evampire blocks and pins that ebat leaves out.
:doc:`power-without-lldp`
   Why ebat requests at most class 3 when it receives power, and the power
   that leaves.
:doc:`boards`
   How a board without a data path connects to the Ethernet cable, and
   boards that pass Ethernet data on wiring that bypasses ebat.

.. toctree::
   :maxdepth: 1
   :hidden:

   requirements
   architecture
   power-without-lldp
   boards
