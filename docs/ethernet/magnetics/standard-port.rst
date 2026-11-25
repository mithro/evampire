Port with standard magnetics
============================

A standard Ethernet port, the kind used on a first-version board
(:ref:`board configurations <tab-power-board-configs>`), has a transformer
and a common-mode choke on each pair, centre taps and a common-mode
termination. :doc:`functions` explains what each part does.

One pair
--------

:numref:`fig-magnetics-one-pair` shows one pair. The pair passes through
three parts on its way from the :term:`Ethernet transceiver` to the
:term:`RJ45` socket:

* a :wikipedia:`transformer <Transformer>`: two windings on one magnetic
  core, with no conducting path between them;
* a :term:`common-mode choke`: two windings on one core, one in each wire
  of the pair;
* the RJ45 contacts.

Both windings of the transformer have a :term:`centre tap`, a connection to
the middle of the winding. The circuit-side centre tap serves the
transceiver's line driver. The cable-side centre tap goes, through a 75 Ω
resistor and a high-voltage capacitor, to chassis ground: the metal frame or
case of the equipment, and the metal shield of the RJ45 socket.

.. graphviz:: one-pair.dot
   :name: fig-magnetics-one-pair
   :caption: One pair of a standard port, pair A on RJ45 contacts 1 and 2.
   :alt: Schematic of one pair: transceiver pins pair A plus and minus go to
         the circuit-side winding of a 1:1 transformer. The cable-side
         winding goes through a common-mode choke to RJ45 pins 1 and 2. The
         circuit-side centre tap goes through 0.1 microfarads to signal
         ground; the cable-side centre tap goes through 75 ohms and a shared
         1000 picofarad, 2 kilovolt capacitor to chassis ground, which also
         connects to the socket shield.
   :align: center

Four pairs and the termination
------------------------------

:numref:`fig-magnetics-four-pairs` shows all four pairs on the cable side.
Each block marked "transformer + choke" is one channel of the magnetics: a transformer followed,
on the cable side, by a common-mode choke. The 75 Ω resistors from the four
cable-side centre taps join at one node, which goes through one 1000 pF
capacitor rated 2 kV to chassis ground. The circuit-side centre taps are
wired as in :numref:`fig-magnetics-one-pair` and are left out of this
figure.

.. graphviz:: four-pairs.dot
   :name: fig-magnetics-four-pairs
   :caption: The cable side of all four pairs of a standard port, with the
             pins listed pair by pair rather than in contact order.
   :alt: Schematic of four channels, pairs A to D, between the transceiver
         and the RJ45 socket. Pair A goes to pins 1 and 2, B to 3 and 6, C
         to 4 and 5, D to 7 and 8. Each channel's cable-side centre tap has
         a 75 ohm resistor to a common line, which goes through a 1000
         picofarad, 2 kilovolt capacitor to chassis ground.
   :align: center

Magnetics are sold for all four pairs in one part, either as a separate
module or built into the RJ45 socket. :doc:`first-version` compares the two
and gives example parts.
