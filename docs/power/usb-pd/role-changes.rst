.. _usbpd-role-changes:

Changing roles while connected
==============================

How two connected USB Type-C ports exchange the power role, the data role
and the VCONN supply without unplugging, and how a Hard Reset returns both
to their starting state.

Each swap changes one thing
---------------------------

When a cable is plugged in, the port that ends up with :term:`Rp` is the
:term:`source`, supplies :term:`VCONN` and is the USB host side; the port
with :term:`Rd` is the :term:`sink` and the device side
(:typec:`Section 4.5.1.4.1`). Afterwards three :term:`USB Power Delivery`
message exchanges can each change one of these roles
(:numref:`tab-usbpd-swaps`).

.. list-table:: What each swap changes (:typec:`Table 4-13`)
   :name: tab-usbpd-swaps
   :header-rows: 1
   :widths: 25 25 25 25

   * - Role
     - PR_Swap
     - DR_Swap
     - VCONN_​Swap
   * - VBUS supply
     - Swapped
     - Kept
     - Kept
   * - Rp and Rd
     - Swapped
     - Kept
     - Kept
   * - Data role
     - Kept
     - Swapped
     - Kept
   * - VCONN
     - Kept
     - Kept
     - Swapped

Either port may ask for any of the three. The other port answers Accept,
Reject or Wait (:pd:`PD Sections 7.10 <x>`, :pd:`7.12.1 <x>` and
:pd:`7.13 <x>`). Wait means "ask again later". A port in EPR mode must leave
it before it may send PR_Swap (:pd:`Section 7.10`).

.. _usbpd-power-role-swap:

A power role swap exchanges source and sink
-------------------------------------------

In a power role swap, the source turns VBUS off and changes its Rp to Rd,
and the sink then changes its Rd to Rp and turns VBUS on.
:numref:`fig-usbpd-prswap` shows the sequence and
:numref:`tab-usbpd-prswap` its time limits. The sequence after Accept is the
same whichever port asked (:pd:`Section 4.3.3`).

.. _fig-usbpd-prswap:

.. graphviz:: pr-swap.dot
   :caption: Power role swap asked for by the initial sink
             (:pd:`Section 4.3.3`, :pd:`Figure 4.14 <x>`).
   :alt: Sequence diagram between the initial source and the initial sink.
         The initial sink sends PR_Swap; the initial source answers GoodCRC
         within 195 microseconds and Accept within 15 ms, which the sink
         acknowledges with GoodCRC. The sink cuts its current to 2.5 mA
         within 15 ms. After at least 25 ms the source takes VBUS to 0.8 V
         within 650 ms, changes Rp to Rd, and starts PS_RDY within 690 ms;
         the sink waits up to 750 to 920 ms for it. The sink answers GoodCRC,
         changes Rd to Rp, turns VBUS on to 5 V, and starts its own PS_RDY
         within 280 ms; the new sink waits up to 390 to 480 ms. The new sink
         answers GoodCRC, and at least 20 ms later the new source sends
         Source_Capabilities.
   :align: center

.. list-table:: Power role swap time limits (:pd:`PD Tables 4.7 <x>`,
   :pd:`4.8 <x>` and :pd:`7.10 <x>`)
   :name: tab-usbpd-prswap
   :header-rows: 1
   :widths: 30 13 13 44

   * - Name
     - Min (ms)
     - Max (ms)
     - Meaning
   * - tSnkSwapStdby
     - none
     - 15
     - Initial sink: time to cut its VBUS current
   * - tSrcTransition
     - 25
     - none
     - Initial source: wait before turning VBUS off
   * - tSrcSwapStdby
     - none
     - 650
     - Initial source: time to discharge VBUS to vSafe0V
   * - tSrcTransOff
     - none
     - 690
     - Initial source: from the GoodCRC for Accept to the start of its PS_RDY
   * - tPSSourceOff
     - 750
     - 920
     - Initial sink: gives up waiting for that PS_RDY
   * - tNewSrc
     - none
     - 275
     - Initial sink: time to start operating as a source
   * - tSrcTransOn
     - none
     - 280
     - New source: from the GoodCRC for the first PS_RDY to the start of its own PS_RDY
   * - tPSSourceOn
     - 390
     - 480
     - New sink: gives up waiting for that PS_RDY
   * - tSwapSourceStart
     - 20
     - none
     - New source: wait before it first sends its capabilities

Until the new source has VBUS up, the initial sink draws at most
*iSnkSwapStdby* (2.5 mA, :pd:`Table 4.8`). vSafe0V is at most
0.8 V (:pd:`Table 4.9`).

Every message is acknowledged with a :term:`GoodCRC` within *tTransmit*
(195 µs), and Accept follows PR_Swap within *tReceiverResponse* (15 ms)
(:pd:`Table 7.10`).

VBUS may fall and rise faster than the normal slew-rate limit during a swap
(:pd:`Section 4.1.4`). VBUS falls below 5 V, but the initial sink does not
treat this as a detach (:pd:`Section 7.10`). The USB data connection stays
up through the swap (:pd:`Section 4.3`).

The initial sink must run from something other than VBUS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From tSnkSwapStdby until the new source has VBUS up, the initial sink may
draw at most 2.5 mA. A board built around evampire can therefore swap from
sink to source only while it is powered from another input, such as
:term:`Power over Ethernet`. That input is also what it then supplies VBUS
from.

A swap that fails ends in ErrorRecovery
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the expected PS_RDY does not arrive within tPSSourceOff or tPSSourceOn,
the waiting port goes to the Type-C ErrorRecovery state
(:pd:`PD Sections 7.31.5.2 <x>` and :pd:`7.31.5.3 <x>`). It removes its
terminations, both ports see a detach, and attach starts again (see
:ref:`usbpd-error-recovery`). A board that was running from VBUS at that
moment loses its power.

The power budget changes direction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After a swap the board's input and output change places. The software
updates the :ref:`power budget <power-budget>`. When the board becomes the
source, it offers only what its new input allows (see
:ref:`usbpd-building-offer`).

.. _usbpd-data-roles:

Data roles and DR_Swap
----------------------

A USB connection has a host and a device. On USB Type-C, the port that is
the host for data is the *downstream facing port*, :term:`DFP <Data role>`,
and the port that is the device is the *upstream facing port*,
:term:`UFP <Data role>`. This is the port's *data role*, and it is separate
from its power role. A port that can take either data role is a
*dual-role-data* port (:typec:`Section 2.3.3`).

At attach the data role follows the CC resistor. The port with Rp, the
source, starts as DFP, and the port with Rd, the sink, starts as UFP
(:typec:`Section 4.5.1.4.1`). Every message a port sends carries its present
data role in the Port Data Role bit of the header. A port that receives a
message whose bit claims the same role as its own goes to ErrorRecovery
(:pd:`Table 6.2`). The software keeps this bit correct after every change.

A DR_Swap message exchange swaps DFP and UFP and nothing else: VBUS, the CC
resistors and VCONN stay as they are (:pd:`PD Sections 6.3.9 <x>` and
:pd:`7.12.1 <x>`; :typec:`Table 4-13 <x>`). Either port may send DR_Swap,
and the other answers Accept, Reject or Wait. The swap counts as a detach
and re-attach for any USB data connection between the two ports
(:pd:`Section 7.12.1`). A Hard Reset returns the data roles to DFP for the
port with Rp and UFP for the port with Rd (:pd:`Section 7.1.3`).

evampire's USB serial port works only as UFP, so a board that supplies power
as source may need DR_Swap to become UFP. :doc:`/usb-serial/usb-pd-roles`
describes when the serial port needs it and what the board does if the other
end refuses.

.. _usbpd-vconn-swap:

VCONN_Swap moves the VCONN Source
---------------------------------

The *VCONN Source* is the port that supplies VCONN to the cable plugs (see
:ref:`usbpd-vconn`). After attach it is the source. A power role swap does
not move VCONN: the port that was supplying it keeps supplying it, now as
the sink (:pd:`Section 7.10`; :typec:`Table 4-13 <x>`). A port that must
talk to a cable plug, for example to send :term:`Discover Identity`, first
becomes the VCONN Source, with a VCONN_Swap if needed (:pd:`Section 7.13`).

A VCONN_Swap keeps VCONN on throughout, so that a cable powered from VCONN
never loses power. This order is called
:wikipedia:`make-before-break <Make_before_break>`: the new supply
is connected before the old one is disconnected. The steps are
(:pd:`Section 7.13`; :pd:`Table 7.10 <x>`):

#. Either port sends VCONN_Swap. The other answers Accept, Reject, Wait or
   Not_Supported. The port that is supplying VCONN must not answer Reject.
#. After Accept, the new VCONN Source turns VCONN on and sends PS_RDY
   within *tVconnSourceOn* (50 ms).
#. The old VCONN Source turns VCONN off within *tVconnSourceOff* (25 ms) of
   the end of that PS_RDY. For those 25 ms both ports supply VCONN.

A port that cannot supply VCONN answers Reject or Not_Supported. If the
port that sent VCONN_Swap is not the VCONN Source and gets Not_Supported, it
may become the VCONN Source anyway until the next Hard Reset or detach
(:pd:`Section 7.13`). A port that has given up VCONN waits at least
*tVconnSwapDelayDFP* (100 ms) as DFP, or *tVconnSwapDelayUFP* (500 ms) as
UFP, before asking for it back (:pd:`Table 7.10`).

