.. _ebat-requirements:

ebat requirements
=================

This page lists the evampire requirements that ebat drops, the power
requirements it keeps unchanged, and the one that changes because LLDP
goes with the data path.

.. _req-ebat-no-data:

ebat has no Ethernet data path
------------------------------

* ebat is its own die, built from evampire's design without the Ethernet
  data circuits.
* ebat has no :term:`Ethernet transceiver`, integrated or external, and no
  :term:`RGMII` interface. It does not receive, forward or send Ethernet
  :term:`frames <frame>`.
* These evampire requirements do not apply: :ref:`req-transceivers`,
  :ref:`req-cable`, :ref:`req-forwarding`, :ref:`req-processor-delivery`,
  :ref:`req-processor-transmit` and :ref:`req-memory`.
* ebat has no :term:`MDIO` interface and needs no 125 MHz reference clock
  (:doc:`architecture`).
* A board can pass Ethernet data between two RJ45 sockets, on wiring
  that does not pass through ebat. :doc:`boards` describes such boards and
  the precautions they need.

.. _req-ebat-same-power:

Every power requirement of evampire applies unchanged
-----------------------------------------------------

ebat's power side is evampire's. These requirements apply to ebat as
written, except for the negotiation over LLDP (:ref:`req-ebat-no-lldp`):

* :ref:`req-power-bridging`: the ports, the operating modes, the power
  budget, the translation between the standards and the sharing between
  output ports;
* :ref:`req-power-control`;
* :ref:`req-poe-classification`, in its Physical Layer part;
* :ref:`req-converters`;
* :ref:`req-usb-serial`;
* :ref:`req-processor`, which on ebat runs no Ethernet traffic;
* :ref:`req-process`.

evampire's board configurations (:numref:`tab-power-board-configs`) apply
to ebat in every row except the transceiver and cable rows. A board fits
the ports it needs, as :doc:`boards` describes.

.. _req-ebat-no-lldp:

ebat negotiates Power over Ethernet without LLDP
------------------------------------------------

ebat does the Physical Layer part of :ref:`req-poe-classification` in
both roles, as evampire does, and none of the Data Link Layer part, which
needs :term:`LLDP` frames:

* As a :term:`powered device`, port A requests at most class 3. IEEE 802.3
  requires a powered device that requests class 4 or higher to implement
  Data Link Layer classification (:clause:`145.3.6`,
  :clause:`33.3.5`). :doc:`power-without-lldp` gives the power this
  leaves.
* As :term:`power sourcing equipment`, port B assigns a class by Physical
  Layer classification alone, up to class 8
  (:doc:`../power/poe/power-sourcing`). It does not answer LLDP power
  requests, which is optional for power sourcing equipment
  (:numref:`tab-poe-class-methods`).
* On a board without data pass-through, the allocation on port B changes
  only by removing the power and classifying the powered device again
  (:doc:`../power/poe/sharing`). With data pass-through, LLDP frames pass
  between the far ends (:ref:`ebat-pass-through-lldp`).

.. _ebat-requirements-open-questions:

Open questions
--------------

* The questions that evampire leaves open on its power side apply to ebat
  in the same way (:ref:`requirements-open-questions`).
* The questions on boards built around ebat are listed on :doc:`boards`.
