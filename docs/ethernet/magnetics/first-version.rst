Magnetics for the first version
===============================

This page is for the designer of a first-version board, which uses an
external :term:`Ethernet transceiver` and standard :term:`magnetics` on
each port (:ref:`board configurations <tab-power-board-configs>`). It
covers the parts each port needs, the kinds of magnetics, board layout,
what to look for in a data sheet, and example parts.

Parts for each port
-------------------

Each of Ethernet ports A and B (:ref:`requirements`) needs:

* one external transceiver with an RGMII interface
  (:doc:`../rgmii/index`);
* one set of four-channel magnetics for 1000BASE-T, as a module or in the
  socket;
* the circuit-side centre-tap connection that the transceiver's data sheet
  asks for (:doc:`functions`);
* the cable-side common-mode termination, unless it is in the socket;
* a shielded RJ45 socket on a chassis ground area;
* a resistor and capacitor joining signal ground and chassis ground.

The port that takes or supplies Power over Ethernet also needs magnetics
rated for the current, blocking capacitors in the termination, and the
power circuits on the cable-side centre taps (:doc:`poe`). In the first
version, port A takes power and port B supplies it
(:ref:`board configurations <tab-power-board-configs>`,
:ref:`power-flow`).

Module or integrated socket
---------------------------

Magnetics come as a separate module or inside the RJ45 socket.

Discrete module
   All four channels in one surface-mount part, placed between the
   transceiver and an ordinary RJ45 socket. The 75 Ω resistors and the
   high-voltage capacitor are separate parts.
RJ45 socket with integrated magnetics
   The magnetics, in most parts the termination, and often two LEDs driven by
   the transceiver, inside the socket.

Integrated sockets save board area and screen the cable-side wiring inside
their metal shield. Their smaller cores can make crosstalk and common-mode
rejection worse ([MAG-ENT98]_, section 3.8). Texas Instruments recommends a
discrete transformer for better electromagnetic compatibility
([MAG-DP83867]_, section 9.2.1.1).

Board-embedded transformers
---------------------------

A transformer can also be built into the circuit board: ferrite cores are
embedded in the board and the windings are made from its copper layers and
vias. For reference, a four-layer embedded Ethernet filter with eight
transformer elements has been built ([MAG-QUILICI]_, figure 4), and
board-embedded transformers have coupled 1000BASE-T Ethernet
([MAG-BOWEN14]_). Racetrack-shaped embedded cores reached the 350 µH
inductance in some samples, with large variation in the ferrite's
permeability after machining ([MAG-BOWEN17]_).

Industry has kept wound parts. An embedded part needs a footprint 20 % to
50 % larger than a wound one, and its advantage is less hand labour
([MAG-QUILICI]_, design methodology), while wound magnetics are already
cheap. Those reasons apply to evampire's first version too. Embedding also
needs a board fabricator that places ferrite in the laminate. For the full
design, which connects without transformers, the option does not apply.

Board layout
------------

:numref:`fig-magnetics-layout` shows the board areas around one port. Board
dimensions are given in millimetres, with the mil (one thousandth of an
inch, 25.4 µm) of the cited guidance in brackets.

.. graphviz:: layout.dot
   :name: fig-magnetics-layout
   :caption: The board areas around one first-version port, seen from
             above.
   :alt: Top view with three areas: a signal ground plane holding the
         transceiver and centre-tap capacitors, a copper-free area under the
         transformer module, and a chassis ground island holding the RJ45
         socket and the 75 ohm and 1000 picofarad termination. A resistor
         and capacitor join signal ground and chassis ground.
   :align: center

* Use a metal shielded RJ45 socket with its shield on chassis ground, and
  keep chassis ground an isolated area that does not overlap the signal
  ground planes ([MAG-DP83867]_, section 9.2.2).
* Join the two grounds through a resistor of 1 MΩ or more and a capacitor,
  with a keep-out of at least 0.51 mm (20 mil) on all layers
  ([MAG-SNLA387]_, section 2). These parts bridge the isolation barrier, so
  they must withstand the isolation test voltage (:doc:`functions`).
* Route each pair as a 100 Ω ± 10 % differential pair over a continuous
  ground plane, under 51 mm (2 inches) long, with its two traces matched
  within 0.51 mm (20 mil) at 1000 Mbit/s, and pairs at least 0.76 mm
  (30 mil) apart ([MAG-SNLA387]_, section 2).
* Keep all copper away from under the magnetics on every layer
  ([MAG-SNLA387]_, section 2).
* Place protection diodes on the transceiver side of the magnetics
  ([MAG-SNLA387]_, section 2).

Data sheet checklist
--------------------

:numref:`tbl-magnetics-checklist` lists what transceiver makers ask of the
magnetics. Data sheets write the turns ratio as "1CT:1CT": one turn to one
turn, with a centre tap (CT) on both windings.

.. list-table:: Requirements for 10/100/1000 Mbit/s magnetics
   :name: tbl-magnetics-checklist
   :header-rows: 1
   :widths: 35 65

   * - Parameter
     - Requirement
   * - Turns ratio
     - 1CT:1CT, within ±2 % ([MAG-ENT98]_, section 3.1)
   * - Open-circuit inductance
     - 350 µH or more at 100 kHz, 100 mV and 8 mA bias ([MAG-KSZ9031]_, section 12)
   * - Insertion loss
     - 1 dB or less from 1 MHz to 100 MHz ([MAG-KSZ9031]_, section 12)
   * - Return loss
     - 18 dB or more from 1 MHz to 30 MHz, 2 dB inside the 16 dB limit
       ([MAG-ENT98]_, section 4.2)
   * - Isolation
     - 1500 V rms for 60 s ([MAG-KSZ9031]_, section 12)
   * - Circuit-side centre taps
     - four separate taps for a voltage-mode transceiver
       ([MAG-KSZ9031]_, section 12)
   * - Choke position
     - cable side ([MAG-ENT98]_, section 3.5)
   * - Power over Ethernet
     - rated for the current, on a port that takes or supplies power
       (:doc:`poe`)

:numref:`tbl-magnetics-parts` gives two examples, with values from the
makers' data sheets. The return loss column gives the value from 1 MHz to
30 MHz.

.. list-table:: Example gigabit magnetics
   :name: tbl-magnetics-parts
   :header-rows: 1
   :widths: 40 20 20 20

   * - Part
     - Inductance (µH)
     - Return loss (dB)
     - Isolation (V rms)
   * - Würth Elektronik 7499111221A socket [MAG-WURTH]_
     - 350
     - 18
     - 1500
   * - Bel Fuse 0826-1G1T-23-F socket [MAG-BEL]_
     - 350
     - 18
     - 1500

The Würth and Bel sockets include the four 75 Ω resistors and a 1000 pF,
2 kV capacitor. The Würth part is not for Power over Ethernet; the Bel part
has 12 cores and every part is tested for isolation.
