.. _usbpd-two-ports:

Two ports and sharing the budget
================================

How a board with two USB Type-C ports uses them together, and how the
software moves power between them while devices stay connected. The number
of USB Type-C ports in each configuration is given in
:ref:`board configurations <tab-power-board-configs>`.

Two ports let the board bridge USB to USB
-----------------------------------------

Each USB Type-C port is a :term:`dual-role port`, so with two ports the
board can work in more ways than with one:

* one port as :term:`sink` and the other as :term:`source`, which makes the
  board a USB-to-USB power bridge as well as a USB-to-Ethernet one;
* both ports as sources, sharing the power from
  :term:`Power over Ethernet` or from the other input;
* both ports as sinks, for example two chargers feeding one Ethernet output.

Whenever two or more ports supply power at once, their offers together must
stay within the :ref:`power budget <power-budget>`. The rule and how the
software applies it on every kind of port are on
:ref:`sharing the budget <power-sharing>`. This page covers what USB Power
Delivery allows when the software changes a USB port's share.

.. _usbpd-sharing:

The software moves power by changing a source's offer
------------------------------------------------------

A source can change what it offers while a device is attached, by sending a
new Source_Capabilities message. The sink must then answer with a new
Request, because a Request always refers to the most recent offer
(:pd:`Section 7.9.2`). The new contract is set up with the same exchange as
the first one (see :ref:`usbpd-negotiation`).

A port whose offer can change is a Managed Capability Port
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

USB Power Delivery describes every source port by three powers
(:pd:`Section 3.2`; :pd:`Table 6.29 <x>`):

* the *Port Maximum PDP*, the most it will ever provide;
* the *Port Present PDP*, what it can provide at present;
* the power in its present Source_Capabilities, which may be less again.

A *Guaranteed Capability Port* always has Port Present PDP equal to Port
Maximum PDP, apart from faults and cable limits. A
:term:`Managed Capability Port` may set Port Present PDP lower, and may
change it during operation (:pd:`PD Sections 3.2.2 <x>` and :pd:`3.2.3 <x>`).
The port says which kind it is in the Port Type bit of its Source_Info
message (:pd:`Table 6.29`).

Ports that share one supply are Managed Capability Ports by definition
(:typec:`Section 4.8.6`). An evampire source port is one in every board
configuration, because its power depends on the input port and, on a
two-port board, on the other USB port.

A Managed Capability Port may offer less than its Port Present PDP. If the
sink sets the *Capability Mismatch* bit in its Request, asking for more,
the port must then offer the smaller of its Port Present PDP and what the
sink can take (:pd:`Section 3.2.3`, item 5). It must also provide at least
its *Port Guaranteed PDP* when a sink asks for it this way, and while a
contract for the Port Guaranteed PDP is in place it must not reduce its
offer (:pd:`Section 7.26.2.3`).

Lowering an offer while a device is attached
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When the software must take power from a port to give it to the other, the
steps on the port that gives it up are:

#. Send an Alert message whose extended event says that the source is about
   to reduce its capabilities, *tReducePowerAlert* (2.0 s to 2.4 s) before
   the new Source_Capabilities. The specification recommends this, so that
   the sink can prepare; if the time is not available, the Alert goes as
   early as possible (:pd:`Section 6.4.5.5`; :pd:`Tables 4.7 <x>` and
   :pd:`6.25 <x>`).
#. Send the reduced Source_Capabilities. The sink requests one of the new
   offers.
#. Accept the Request. If the new current is lower, the sink must reach it
   before the shortest *tSrcTransition* (25 ms) ends, and the source waits
   tSrcTransition before it lowers its current limit
   (:pd:`Section 4.5.1.3`; see :ref:`usbpd-limiting`).
#. Send PS_RDY. From here the port's share is the new, lower offer.

Without the Alert, the exchange takes at most about 355 ms: up to 15 ms each
for the Request and the Accept (*tReceiverResponse*), then up to
*tSrcTransReq* (325 ms) to the PS_RDY (:pd:`PD Tables 7.10 <x>` and
:pd:`4.7 <x>`; see :ref:`usbpd-timing`). With the Alert, about 2 s more. The
power freed on this port can go to the other port once the sink has lowered
its current, tSrcTransition after the Accept.

The GotoMin message, which told a sink to drop to a minimum current at
once, is deprecated in PD R3.3: a port that receives one answers
Not_Supported (:pd:`Section 6.3.2`). The
multi-port charger section of the USB Type-C specification still lists
GotoMin as a way to reclaim power (:typec:`Section 4.8.6.2`), but a source
cannot rely on a sink that follows R3.3 acting on it.

Raising an offer, and moving power when a device is unplugged
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Raising an offer needs no Alert: the source sends the larger
Source_Capabilities and the sink requests again. A sink that wants more
than it was offered sets Capability Mismatch, and the source then offers up
to its Port Present PDP. In a group of shared ports, every port must reach
its maximum or the sink's need within 3 s of such a request
(:typec:`Section 4.8.6.2`).

When a device is unplugged, the source sees the detach on CC and removes
VBUS, reaching vSafe0V within *tSafe0V* (650 ms) (:pd:`Section 4.1.5.5`).
Its share is free once VBUS is off. The software can then raise the offer
on the other port as above.

The USB Type-C specification gives two example sharing policies for groups
of shared ports: *highest-to-lowest*, which serves the first-connected port
first, and *balanced*, which splits the power equally between connected
ports (:typec:`Table 4-23`). It also requires that a shared port reclaiming
power for a newly attached device uses offers and renegotiation, not a Hard
Reset, ErrorRecovery or the Disabled state (:typec:`Section 4.8.6.1`).

Each port has its own circuits; the software is shared
-------------------------------------------------------

Each port needs its own CC circuits, because both ports must present their
terminations and detect attach at the same time, and messages on the two
ports arrive independently (see :ref:`usbpd-analogue`). Slow measurements,
such as attach levels and the VBUS voltage, can share one converter through a
multiplexer. Each port also needs its own power path and its own current
limit (see :ref:`usbpd-monitoring`).

The processor runs the negotiations on both ports, which can overlap. The
cost of that is worked out in :ref:`usbpd-software-two-ports`.

Open questions
--------------

* Whether a two-port board counts as a USB Type-C multi-port charger. Such a
  charger must offer at least 5 V at 1.5 A on every port, whatever the other
  ports draw (:typec:`Section 4.8.6.1`). Two such ports need 15 W of output
  between them.
* Which sharing policy the software uses between the two USB ports, and
  between a USB port and an Ethernet output.
* Whether the board sends the Alert before reducing an offer, which delays
  the move of power by about 2 s.
