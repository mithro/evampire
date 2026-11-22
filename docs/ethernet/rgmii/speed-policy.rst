Keeping both ports at the same speed
====================================

How the processor sets up the two Ethernet transceivers so that ports A and
B run at the same speed in full duplex, which cut-through forwarding needs.
The registers it uses are on :doc:`mdio`.

.. _rgmii-same-speed:

Cut-through forwarding works only at equal speeds
-------------------------------------------------

evampire forwards frames
:term:`cut-through <cut-through forwarding>`: it sends each byte out of the
other port a few clock cycles after it arrives (see :ref:`req-forwarding`).
This works only if both ports run at the same speed.

A frame arriving at 1000 Mbit/s cannot leave at 100 Mbit/s without storing
almost all of it. A frame arriving at 100 Mbit/s cannot leave at
1000 Mbit/s, because the transmitter runs out of data after the first byte.
By requirement, evampire stores no full frame on the forwarding path (see
:ref:`req-memory`).

.. _rgmii-policy:

Both ports link at the highest speed they share, in full duplex
---------------------------------------------------------------

Every port supports 1000, 100 and 10 Mbit/s (see :ref:`the transceiver requirements <req-transceivers>`).
The processor sets up the transceivers as follows:

#. It sets both transceivers to advertise 1000 Mbit/s full duplex
   (register 9) and 100 and 10 Mbit/s full duplex (register 4), and no
   half-duplex mode. Half duplex needs the media access
   controller to detect collisions and send frames again (:clause:`4`),
   which a cut-through path without frame storage cannot do.
#. When both links are up, it reads the speed of each port. If both run at
   the same speed, it turns on forwarding between them.
#. When a link goes down, it turns forwarding off, and that port's
   transceiver advertises every speed that evampire supports again.

While forwarding is off, frames to and from the processor are still
received and sent on any port whose link is up.

.. _rgmii-slow-partner:

A slower partner brings both ports down to its speed
----------------------------------------------------

If the two ports come up at different speeds, forwarding stays off. The
processor removes the higher speeds from the faster port's advertisement
and restarts autonegotiation on that port. Both ports then run at the
slower speed, and forwarding resumes. A partner that offers only 10 or
100 Mbit/s on one port therefore sets the speed of both ports.

.. graphviz:: speed-policy.dot
   :name: fig-rgmii-speed-policy
   :caption: States of the two links and of forwarding.
   :alt: Three states. From "one or both links down", the second link
         coming up at the same speed leads to "both links up at the same
         speed, forwarding on". Coming up at a different speed leads to
         "different speeds, forwarding off", where the faster port is
         restricted and renegotiates, and then to the same-speed state. A
         link going down returns to the first state.
   :align: center

:numref:`fig-rgmii-speed-policy` shows these states.

.. _rgmii-error-forwarding:

A forwarded frame with an error is passed on marked as an error
---------------------------------------------------------------

A forwarded frame that arrives with RX_CTL showing an error is passed on
with TX_CTL showing an error on the same byte, that is high then low
(:std:`RGMII 2.0 <rgmii-2-0>` Table 3, :clause:`Table 35-1 <35>`). The
transceiver then sends an error on the cable, and the far end discards the
frame. The frame is already being sent when the error arrives, so it cannot
be dropped instead.
