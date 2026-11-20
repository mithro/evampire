.. _phy-job:

What a transceiver does and what the cable does to the signal
=============================================================

This page describes the job of an :term:`Ethernet transceiver`, the three
speeds it handles, and the four ways a twisted-pair cable changes the signal
on its way.

.. _phy-position:

The transceiver sits between the forwarding logic and the cable
---------------------------------------------------------------

The IEEE 802.3 standard [PHY-8023]_ calls the logic that sends and receives
whole :term:`frames <frame>` the :term:`media access controller (MAC)
<media access controller>` (:clause:`4`). In evampire the
:term:`forwarding logic` and the processor share that role
(:doc:`/architecture/index`). The transceiver connects the forwarding logic
to the cable (:numref:`fig-phy-position`). Ethernet documentation calls it
the PHY, short for physical layer device.

.. graphviz:: position.dot
   :name: fig-phy-position
   :caption: The transceiver passes bytes between the forwarding logic and
             the analogue signals on the four pairs of the cable.
   :alt: Four boxes from left to right: forwarding logic, Ethernet
         transceiver, magnetics or transformer-free coupling, and the RJ45
         socket. The link between the first two carries bytes; the link
         from the transceiver to the coupling carries analogue voltages on
         four pairs.
   :align: center

The coupling between the transceiver and the :term:`RJ45` socket is either
a set of transformers, the :term:`magnetics`, or a transformer-free
connection (:doc:`../magnetics/index`). An external transceiver exchanges
bytes with evampire over :term:`RGMII` (:doc:`../rgmii/index`); an
integrated one uses an on-chip byte interface
(:doc:`integration/requirements`).

When a cable is plugged in, the transceivers at its two ends exchange a
short description of what each can do and choose the fastest speed both
support. This exchange is :term:`autonegotiation`
(:clause:`28`, see :doc:`autonegotiation`). After that, the transceiver:

* takes bytes from the forwarding logic, adds structure that lets the far
  end find its clock and the frame boundaries, and turns them into a
  sequence of voltage levels that suits the cable;
* receives the far end's voltage levels, which arrive smaller, spread out
  in time and mixed with interference, and turns them back into bytes;
* reports its state, such as link up and the speed chosen, in a set of
  16-bit registers (:clause:`22.2.4`, :clause:`Table 22-6 <22>`). An
  external transceiver makes them readable over the two-wire :term:`MDIO`
  interface, which evampire drives through its
  :ref:`configuration interface <arch-config-interface>`.

.. _phy-speeds:

A transceiver handles three speeds, each with its own coding
-------------------------------------------------------------

A gigabit transceiver for twisted-pair cable normally supports three
speeds, each defined in its own clauses of IEEE 802.3
(:numref:`tab-phy-speeds`). In each name, the number is the data rate in
Mbit/s, "BASE" means the levels are sent directly on the wire
(:wikipedia:`baseband <Baseband>`) rather than on a carrier, and "T" means
twisted pair.

.. list-table:: The three twisted-pair speeds
   :name: tab-phy-speeds
   :header-rows: 1
   :widths: 25 25 15 15 20

   * - Name
     - Clauses
     - Rate (Mbit/s)
     - Pairs used
     - Levels on the wire
   * - :doc:`10BASE-T <10base-t>`
     - :clause:`14`
     - 10
     - 2
     - 2
   * - :doc:`100BASE-TX <100base-tx>`
     - :clause:`24`, :clause:`25`
     - 100
     - 2
     - 3
   * - :doc:`1000BASE-T <1000base-t-coding>`
     - :clause:`40`
     - 1000
     - 4
     - 5

10BASE-T and 100BASE-TX use one pair for each direction. 1000BASE-T uses
all four pairs in both directions at once. These pages describe the speeds
in that order, because each one adds techniques to the one before.

Three terms are used on every page:

:term:`Symbol`
   One voltage level held on the wire for one fixed time slot. Depending on
   how many levels are allowed, a symbol carries less than one bit, one bit
   or several bits.
:term:`Symbol rate`
   The number of symbols sent per second on one pair, in baud (Bd). At
   125 MBd a symbol lasts :math:`1 / (125 \times 10^{6}\ \text{Bd}) = 8`
   ns.
Differential voltage
   Each pair carries the difference between the voltages of its two wires
   (:wikipedia:`differential signalling <Differential_signalling>`). Every
   amplitude on these pages is a differential voltage into the 100 Ω
   impedance of the cable.

.. _phy-cable:

The cable is four twisted pairs specified up to 100 MHz
-------------------------------------------------------

An Ethernet cable holds four pairs of copper wires. The two wires of each
pair are twisted around each other, which makes the pair a balanced
:wikipedia:`transmission line <Transmission_line>` of 100 Ω characteristic
impedance (:clause:`40.7.2.2`) and reduces the interference it picks up
and radiates (:wikipedia:`twisted pair <Twisted_pair>`).

1000BASE-T runs over Class D cabling built from Category 5 components, as
specified in :std:`ISO/IEC 11801 <iso-iec-11801>` and :std:`TIA-568`
(:clause:`40.7.1`, see :wikipedia:`Category 5 cable
<Category_5_cable>`). The link transmission parameters are specified for a
link segment of up to at least 100 m (:clause:`40.7.2`). The receiver must reach a
:wikipedia:`bit error ratio <Bit_error_rate>` below :math:`10^{-10}` over
such a link (:clause:`40.6.1.3.1`).

.. _phy-impairments:

The cable changes the signal in four ways
-----------------------------------------

Four effects of the cable set the design of every transceiver.
:doc:`1000base-t-echo` gives the size of each one for 1000BASE-T.

:term:`Insertion loss`
   The signal becomes smaller as it travels, and more so at high
   frequencies, because the current crowds towards the surface of each
   conductor (the :wikipedia:`skin effect <Skin_effect>`). A short pulse
   therefore arrives smaller and spread out in time, so that each symbol
   overlaps the next few. The overlap is called
   :wikipedia:`inter-symbol interference <Intersymbol_interference>`.
:term:`Return loss`
   A change of impedance, at a connector, a patch cord or the far end,
   reflects part of the signal back to the sender. Return loss is how many
   decibels weaker the reflection is than the signal that caused it.
Near-end :term:`crosstalk`
   A changing current in one pair induces a voltage in its neighbours. When
   the disturbing transmitter and the disturbed receiver are at the same
   end of the cable, the coupling is near-end crosstalk (NEXT). The
   disturbing signal has not been weakened by the cable, so NEXT is
   strong.
Far-end crosstalk
   The same coupling from a transmitter at the far end of the cable. The
   disturbing signal has crossed the whole cable, so far-end crosstalk
   (FEXT) is weaker than near-end crosstalk.

Losses are given in :wikipedia:`decibels <Decibel>` (dB). A loss of
:math:`L` dB multiplies a voltage by :math:`10^{-L/20}`: 6 dB halves it and
20 dB divides it by 10.
