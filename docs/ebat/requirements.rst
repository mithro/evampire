.. _ebat-requirements:

ebat requirements
=================

ebat drops evampire's requirements on the Ethernet data path, keeps its
power requirements, and meets the classification requirement without LLDP,
because LLDP needs Ethernet frames.

.. _req-ebat-no-data:

No Ethernet data path
---------------------

* ebat is its own die, built from evampire's design without the Ethernet
  data circuits.
* ebat has no :term:`Ethernet transceiver`, integrated or external, and no
  :term:`RGMII` interface. It does not receive, forward or send Ethernet
  :term:`frames <frame>`.
* These evampire requirements do not apply: :ref:`req-transceivers`,
  :ref:`req-forwarding`, :ref:`req-processor-delivery`,
  :ref:`req-processor-transmit` and :ref:`req-memory`.
* Of :ref:`req-cable`, only the electrical isolation and the path for
  Power over Ethernet current apply. The parts that serve the data do not
  (:ref:`ebat-boards-no-magnetics`, :ref:`ebat-boards-isolation`).
* Of :ref:`req-processor`, the item on the transceiver configuration
  interface does not apply, because ebat has no :term:`MDIO` interface
  (:ref:`ebat-left-out`).
* A board can pass Ethernet data between two RJ45 sockets, on wiring
  that does not pass through ebat. :ref:`ebat-pass-through` describes such
  boards and the precautions they need.

.. _req-ebat-same-power:

Unchanged power requirements
----------------------------

ebat's power side is evampire's. These requirements apply to ebat as
written, except where :ref:`req-ebat-no-lldp` states otherwise:

* :ref:`req-power-bridging`: the ports, the operating modes, the power
  budget, the translation between the standards and the sharing between
  output ports;
* :ref:`req-power-control`;
* :ref:`req-poe-classification`, in its Physical Layer part;
* :ref:`req-converters`;
* :ref:`req-usb-serial`;
* :ref:`req-processor`, except its item on the transceiver configuration
  interface;
* :ref:`req-process`.

Each Ethernet port takes the power role that evampire's board
configurations give it (:numref:`tab-power-board-configs`). In the first
version, port A receives power and port B supplies it. In the full design,
either port takes either role, and each statement about port A or port B
on ebat applies to whichever port has that role.

The rows of :numref:`tab-power-board-configs` on the transceivers and the
connection to the cable do not apply. A board fits only the ports it needs,
so it can have fewer Ethernet or USB Type-C ports than the table lists
(:ref:`ebat-boards-ports`).

.. _req-ebat-no-lldp:

Classification without LLDP
---------------------------

ebat does the Physical Layer part of :ref:`req-poe-classification` in
both roles, as evampire does, and none of the Data Link Layer part, which
needs :term:`LLDP` frames. :doc:`power-without-lldp` gives the reasons and
the power that results:

* As a :term:`powered device`, port A requests class 1, 2 or 3, and never
  class 4 or higher (:ref:`ebat-lldp-class-4`).
* As :term:`power sourcing equipment`, port B assigns a class by Physical
  Layer classification alone, up to class 8, and does not answer LLDP power
  requests.
* Port B changes the allocation of the powered device it supplies only by
  removing the power and classifying the device again. The sharing between
  output ports in :ref:`req-power-bridging` moves power to or from port B
  only in this way (:ref:`ebat-port-b-allocation`).
* With data pass-through on the board, LLDP frames pass between the far
  ends (:ref:`ebat-pass-through-lldp`).

.. _ebat-requirements-open-questions:

Open questions
--------------

* The questions that evampire leaves open on its power side apply to ebat
  in the same way (:ref:`requirements-open-questions`).
* Which class the start-up sequencer requests, which evampire leaves open
  (:doc:`../power/poe/startup`), on ebat chooses between classes 1, 2 and
  3.
* The questions on boards built around ebat are listed on :doc:`boards`.
