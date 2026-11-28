.. _ebat:

ebat
====

ebat is evampire with the Ethernet data functions removed. It keeps
evampire's Power over Ethernet and USB Type-C circuits and their software,
except the power negotiation over LLDP. It drops the transceivers, the
forwarding between ports and the network traffic, with their cost and
complexity. ebat is its own die, but not a
separate design: its power circuits are evampire's, and any change to
evampire's power side applies to ebat. Like evampire, it is in design and
no silicon exists.

The power negotiation over LLDP goes with the data functions, because LLDP
needs Ethernet frames. The rest of ebat's power side is specified on
evampire's pages.

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
   * - :ref:`Frames to the processor <req-processor-delivery>`
     - Yes
     - No
   * - :ref:`Frames from the processor <req-processor-transmit>`
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
   * - Highest class requested when receiving Power over Ethernet
     - Up to 8
     - Up to 3
   * - Highest class offered when supplying Power over Ethernet
     - 8
     - 8
   * - :ref:`Changing the allocation of a powered device it supplies <poe-allocation-changes>`
     - Over LLDP, or in the ways that need no LLDP
     - Only in the ways that need no LLDP
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

Without LLDP, ebat's power side behaves differently from evampire's in two
ways, shown in :numref:`tab-ebat-compare`: the highest class it requests
when receiving power, and how the allocation changes when it supplies power
(:ref:`req-ebat-no-lldp`). :doc:`power-without-lldp` explains both.

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
