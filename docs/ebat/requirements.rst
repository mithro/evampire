.. _ebat-requirements:

ebat requirements
=================

This page lists every requirement on ebat. Where ebat keeps an evampire
requirement unchanged, the page links to it rather than repeating it. The
page ends with the questions still open.

.. _req-ebat-no-data:

ebat has no Ethernet data path
------------------------------

* ebat has no :term:`Ethernet transceiver`, integrated or external, and no
  :term:`RGMII` interface. It does not receive, forward or send Ethernet
  :term:`frames <frame>`.
* None of the evampire requirements on Ethernet data apply:
  :ref:`req-transceivers`, :ref:`req-cable`, :ref:`req-forwarding`,
  :ref:`req-processor-delivery`, :ref:`req-processor-transmit` and
  :ref:`req-memory`.
* ebat has no :term:`MDIO` interface and needs no 125 MHz reference clock
  (:doc:`architecture`).
* A board can pass Ethernet data between two RJ45 sockets, on wiring
  that does not pass through ebat. :doc:`boards` describes such boards and
  the precautions they need.

.. _req-ebat-ports:

ebat has the same power ports as evampire
-----------------------------------------

* Ethernet port A receives power as a :term:`powered device`. Ethernet
  port B supplies power as :term:`power sourcing equipment`.
* Each USB Type-C port is a :term:`dual-role port` that negotiates power
  with :term:`USB Power Delivery`, as on evampire (:doc:`../power/usb-pd/index`).
* A board fits the ports it needs. :doc:`boards` lists the combinations.
* The number of USB Type-C ports, and whether an Ethernet port can take
  either role (:doc:`../power/poe/dual-role`), are open questions
  (:ref:`ebat-requirements-open-questions`).

.. _req-ebat-power-bridging:

Power moves between the ports as on evampire, without LLDP
----------------------------------------------------------

ebat keeps the :ref:`power bridging requirements <req-power-bridging>` of
evampire: the three operating modes, the power budget, the translation of
power between the standards and the sharing of the budget between output
ports. These differences follow from having no data path:

* As a powered device, port A requests at most class 3 on each
  :term:`pair set`. IEEE 802.3 requires a powered device that requests
  class 4 or higher to take part in power negotiation over :term:`LLDP`,
  which needs Ethernet frames (:clause:`145.3.6`). :doc:`power-without-lldp`
  gives the power this leaves.
* As power sourcing equipment, port B assigns a class by Physical Layer
  classification alone, up to class 8 (:doc:`../power/poe/power-sourcing`).
  Support for LLDP is optional for power sourcing equipment
  (:clause:`145.5`).
* The allocation on port B changes only by removing the power and
  classifying the powered device again (:doc:`../power/poe/sharing`).

.. _req-ebat-power-control:

Software makes every power decision, within hardware limits
-----------------------------------------------------------

ebat keeps :ref:`req-power-control` unchanged, apart from the negotiation
over LLDP, which it does not have. The software negotiates on every port and
keeps the budget. The built-in hardware measures, limits and switches off
each port on a fault, and the built-in start-up sequencer answers detection
and classification before the processor runs.

.. _req-ebat-converters:

ebat includes the functions of three voltage converters
-------------------------------------------------------

ebat keeps :ref:`req-converters` unchanged. Its converters are those of
:doc:`../power/converters/index`.

.. _req-ebat-usb-serial:

Each USB Type-C port carries a USB serial port
----------------------------------------------

ebat keeps :ref:`req-usb-serial` unchanged. Without Ethernet, the USB
serial port is the only data connection between ebat's processor and a
computer.

.. _req-ebat-processor:

A small RISC-V processor runs the power negotiation and the serial port
-----------------------------------------------------------------------

* The processor is a :wikipedia:`RISC-V` core with on-chip program and data
  memory, as on evampire (:ref:`req-processor`).
* It runs the Power over Ethernet and USB Power Delivery negotiation, the
  power budget and the USB serial port. It has no Ethernet traffic.
* As on evampire, each page states only what it needs from the processor,
  and no particular core, clock or core supply voltage is assumed.

.. _req-ebat-process:

ebat is built on gf180mcu, with custom devices where a function needs them
--------------------------------------------------------------------------

ebat keeps :ref:`req-process` unchanged.

.. _ebat-requirements-open-questions:

Open questions
--------------

* Whether ebat is a separate die, or an evampire die on a board that leaves
  the Ethernet data pins unused. A separate die is smaller. An evampire die
  keeps the option of LLDP on a board that fits transceivers.
* Whether port A presents one powered-device signature or two, one on each
  pair set (:ref:`ebat-dual-signature`).
* The number of USB Type-C ports, one or two.
* Whether an Ethernet port can take either role.
* Whether boards pass Ethernet data through, and how they handle the LLDP
  frames that then pass between the far ends (:ref:`ebat-pass-through-lldp`).
* The questions on power, converters, the processor and isolation that
  evampire leaves open apply to ebat in the same way
  (:ref:`requirements-open-questions`).
