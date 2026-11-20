.. _ebat:

ebat
====

ebat is a reduced variant of evampire that keeps the power side and leaves
out all of the Ethernet data side. It moves power between
:term:`Power over Ethernet` and :term:`USB Type-C` in the same ways as
evampire, but it has no Ethernet transceivers, no forwarding between ports
and no network traffic of its own. Like evampire, it is in design and no
silicon exists.

These pages describe only where ebat differs from evampire. Everything
ebat keeps is described once, on the evampire pages that the ebat pages
link to.

ebat keeps the power functions and drops the data functions
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
   * - :ref:`Power negotiation over LLDP <poe-lldp>`
     - Yes
     - No
   * - Highest class requested when receiving Power over Ethernet
     - 8
     - 3 on each pair set
   * - Highest class offered when supplying Power over Ethernet
     - 8
     - 8
   * - :ref:`USB Type-C dual-role ports with USB Power Delivery <usbpd-two-ports>`
     - Yes
     - Yes
   * - :ref:`USB serial port <req-usb-serial>`
     - Yes
     - Yes
   * - :ref:`Control of the three voltage converters <req-converters>`
     - Yes
     - Yes
   * - :ref:`Power monitoring, limiting and the start-up sequencer <req-power-control>`
     - Yes
     - Yes

The lower class limit when receiving power is the one change that the
missing data path forces on the power side. :doc:`power-without-lldp`
explains it.

The pages
---------

:doc:`requirements`
   Every requirement on ebat, as the evampire requirement it keeps or the
   way it differs, and the questions still open.
:doc:`architecture`
   The blocks inside ebat and the pins it no longer needs.
:doc:`power-without-lldp`
   Why a powered device without a data path can request at most class 3,
   and the power that leaves for each operating mode.
:doc:`boards`
   The kinds of board ebat suits, how the cable connects without a data
   path, and boards that pass Ethernet data through past ebat.

.. toctree::
   :maxdepth: 1
   :hidden:

   requirements
   architecture
   power-without-lldp
   boards
