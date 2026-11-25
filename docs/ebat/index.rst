.. _ebat:

ebat
====

ebat is evampire with the Ethernet data functions removed. It keeps
evampire's Power over Ethernet and USB Type-C circuits and software, and
drops the transceivers, the forwarding between ports and the network
traffic, with their cost and complexity. ebat is its own die, but not a
separate design: its power side is evampire's, and any change to
evampire's power side applies to ebat. Like evampire, it is in design and
no silicon exists.

Everything ebat keeps is described once, on evampire's pages. ebat's
requirements, architecture and boards state only what removing the data
functions changes, and link to evampire's pages for the rest.

Functions kept and dropped
--------------------------

ebat drops the data functions and keeps the power functions.
:numref:`tab-ebat-compare` lists the functions of evampire and whether ebat
has each one.

.. list-table:: Functions of evampire and of ebat
   :name: tab-ebat-compare
   :header-rows: 1
   :widths: 40 30 30

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
     - Yes
   * - :ref:`Data Link Layer classification over LLDP <req-poe-classification>`
     - Yes
     - No
   * - Highest class allowed when receiving Power over Ethernet
     - 8
     - 3
   * - Highest class offered when supplying Power over Ethernet
     - 8
     - 8
   * - Changing the allocation of a powered device it supplies
     - Over LLDP, or by classifying again
     - Only by classifying again
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
functions. That makes the two changes on the power side in
:numref:`tab-ebat-compare`: the highest class when receiving power, and how
the allocation changes when supplying it (:ref:`req-ebat-no-lldp`).
:doc:`power-without-lldp` explains both.

The pages
---------

:doc:`requirements`
   The evampire requirements that ebat drops, and how it meets the
   classification requirement without LLDP.
:doc:`architecture`
   The evampire blocks and pins that ebat leaves out.
:doc:`power-without-lldp`
   Why ebat requests at most class 3 when it receives power, the power that
   remains, and how it changes an allocation when it supplies power.
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
