evampire's RGMII pins and I/O cells
===================================

The pins evampire uses for its two RGMII ports, the I/O supply they run
from, the timing of the standard gf180mcu pad cells, and the choice between
standard and custom I/O cells. The logic in front of the pads is on
:doc:`port-logic`.

.. _rgmii-pins:

Each port uses 12 pins, and the two ports 27 pins in all
--------------------------------------------------------

.. list-table:: RGMII and management pins of evampire
   :name: tab-rgmii-pins
   :header-rows: 1
   :widths: 50 15 35

   * - Signals
     - Pins
     - Pad type
   * - Port A: TXC, TX_CTL, TXD[3:0]
     - 6
     - Output
   * - Port A: RXC, RX_CTL, RXD[3:0]
     - 6
     - Input
   * - Port B: TXC, TX_CTL, TXD[3:0]
     - 6
     - Output
   * - Port B: RXC, RX_CTL, RXD[3:0]
     - 6
     - Input
   * - MDC, shared by both transceivers
     - 1
     - Output
   * - MDIO, shared by both transceivers
     - 1
     - Bidirectional
   * - 125 MHz reference clock
     - 1
     - Input

:numref:`tab-rgmii-pins` adds up to 27 pins. MDIO needs an external
pull-up resistor (see :doc:`mdio`).

The 125 MHz reference clock (see :ref:`clock and reset <arch-clock>`) can
come from an oscillator or from a transceiver. The DP83867 has a 25 MHz or
125 MHz clock output, CLK_OUT [RGMII-DP83867]_ sections 1 and 7.3. The
KSZ9031RNX has a 125 MHz reference clock output, CLK125_NDO
[RGMII-KSZ9031]_ section 3.9.

.. _rgmii-io-voltage:

The pins run at 3.3 V
---------------------

evampire runs its RGMII and MDIO pins at 3.3 V, which both example
transceivers accept (see :doc:`electrical`). 5 V signalling is outside
their ratings. With its 3.3 V I/O option the DP83867 allows at most 3.8 V
on its RGMII pins [RGMII-DP83867]_ section 6.1. The KSZ9031RNX allows at
most 5.0 V on any input [RGMII-KSZ9031]_ section 5.1, below the 5.5 V upper
limit of a 5 V supply.

The I/O supply affects the core supply only through the choice of pad
library:

gf180mcu_fd_io, the foundry library
   Offered by the wafer.space project template at 5 V or 3.3 V. Its I/O
   supply and core supply are connected together [RGMII-WAFERSPACE]_. The
   timing files of gf180mcu_fd_io__bi_t also cover a 2.5 V supply, in the
   2v25, 2v50 and 2v75 corners [RGMII-GF180IO]_.
gf180mcu_ocd_io, a community library
   Keeps the I/O supply and the core supply separate, with the I/O supply
   at least as high as the core supply [RGMII-WAFERSPACE]_
   [RGMII-OCDIO]_.
A custom I/O cell
   Can use any supply within the device ratings, as described below.

The gf180mcu_fd_io datasheet gives input thresholds of 0.8 V low and
2.0 V high, and output currents, for a 4.5 V to 5.5 V supply
([RGMII-GF180IO]_ "Electrical Characteristics"). The thresholds at 3.3 V
are listed under :ref:`rgmii-io-open-questions`.

.. _rgmii-pad-speed:

The standard pad cell takes 2 ns to 6 ns, depending on the corner
-----------------------------------------------------------------

Cell timing comes from *Liberty* files: text tables, in the format read by
synthesis and timing tools, that give each cell's delay and edge time for a
range of input edges and loads. Each file is for one
:wikipedia:`process corner <Process_corners>`: FF (fast transistors, high
supply voltage, cold), TT (typical) or SS (slow transistors, low supply
voltage, hot).

.. list-table:: gf180mcu_fd_io__bi_t at 3.3 V, 16 mA, fast slew (ns)
   :name: tab-gf180-pad-speed
   :header-rows: 1
   :widths: 40 20 20 20

   * - Quantity
     - FF
     - TT
     - SS
   * - Output delay, rising
     - 1.86
     - 3.04
     - 5.74
   * - Output delay, falling
     - 1.96
     - 3.20
     - 6.01
   * - Output edge time, rising
     - 0.63
     - 1.03
     - 1.89
   * - Output edge time, falling
     - 0.53
     - 0.89
     - 1.67
   * - Input delay, rising
     - 0.89
     - 1.44
     - 2.69
   * - Input delay, falling
     - 0.80
     - 1.39
     - 2.73

:numref:`tab-gf180-pad-speed` is taken from the Liberty files of the I/O
library [RGMII-GF180IO]_. The corners are FF at −40 °C and 3.63 V, TT at
25 °C and 3.30 V, and SS at 125 °C and 2.97 V. The drive setting is 16 mA
(PDRV1 = PDRV0 = 1) with fast slew (SL = 0), and the input edge is 0.08 ns.

The output load is the table point nearest 9 pF: 8.85 pF, 8.98 pF and
9.10 pF at the three corners. This load is an estimate for a short trace
and one transceiver input. The input delay is for a load of 0.04 pF on the
core side of the pad.

TXC goes through the same type of pad as TXD, and RXC through the same type
as RXD. The pad delay is common to clock and data only when both make the
same transition. A TXD bit that falls while TXC rises leaves its pad later
than TXC, by the difference between the falling and rising output delays:
0.10 ns at FF, 0.16 ns at TT and 0.27 ns at SS. At SS that is more than
half of the ±0.5 ns of TskewT (:numref:`tab-rgmii-timing`), before any
mismatch between pads, loads or traces is added.

.. _rgmii-pad-duty:

Unequal rising and falling delays change the TXC duty cycle
-----------------------------------------------------------

When the falling edge of a pad is delayed more than its rising edge, the
high time of TXC grows:

.. math::

   t_\text{hi} = \frac{T}{2} + t_\text{pf} - t_\text{pr}

   D = \frac{t_\text{hi}}{T}

.. list-table::
   :header-rows: 1
   :widths: 15 70 15

   * - Symbol
     - Meaning
     - Unit
   * - :math:`t_\text{hi}`
     - High time of TXC at the pin
     - ns
   * - :math:`T`
     - Clock period
     - ns
   * - :math:`t_\text{pf}`, :math:`t_\text{pr}`
     - Output delay of the pad for a falling and a rising edge
     - ns
   * - :math:`D`
     - Duty cycle
     - none

The equations assume a 50 % duty cycle inside evampire. At the SS corner,
:math:`T = 8.00` ns, :math:`t_\text{pf} = 6.01` ns and
:math:`t_\text{pr} = 5.74` ns give:

.. math::

   t_\text{hi} &= 4.00 + 6.01 - 5.74 \\
   &= 4.27\ \text{ns}

   D &= 4.27 / 8.00 \\
   &= 0.53

A 53 % duty cycle is inside the 45 % to 55 % limit (see :doc:`timing`), but
uses most of it before any imbalance of evampire's internal clock is added.

.. _rgmii-pad-edges:

The standard pad's edges are slower than RGMII's 0.75 ns limit
--------------------------------------------------------------

RGMII allows at most 0.75 ns from 20 % to 80 % of each edge (see
:doc:`timing`). The Liberty edge times in :numref:`tab-gf180-pad-speed` are
0.53 ns to 1.89 ns. At the SS corner the edges take a large part of the
4 ns half period. 10 and 100 Mbit/s are not affected.

evampire runs its RGMII ports at 1000 Mbit/s (see :ref:`req-transceivers`).
These limits belong to the standard gf180mcu_fd_io cells, which are
general-purpose 5 V pads, not to the gf180mcu process.

.. _rgmii-custom-io:

Standard or custom I/O cells are chosen by 1000 Mbit/s timing
--------------------------------------------------------------

Whether the RGMII pins use the standard pad cells or a custom I/O cell is
chosen by which one meets 1000 Mbit/s RGMII timing at every process,
voltage and temperature corner. Board-level simulation of the pad, trace and
transceiver input, and :wikipedia:`static timing analysis
<Static_timing_analysis>` (STA), must show:

* edges at the transceiver inputs that meet the 0.75 ns limit or, where they
  do not, setup and hold times that the transceiver still meets;
* a TXC duty cycle of 45 % to 55 %, including evampire's internal clock and
  the pad delays;
* TXC-to-TXD skew within ±0.5 ns at evampire's pins (TskewT,
  :numref:`tab-rgmii-timing`);
* positive setup and hold margins for the receive flip-flops, with data
  valid only 1.0 ns before and after each RXC edge (TsetupR, TholdR).

The standard cell gf180mcu_fd_io__bi_t is characterised and supported by
the wafer.space template. At 1000 Mbit/s its edge times and rise and fall
imbalance, in :numref:`tab-gf180-pad-speed`, leave little margin, so the
checks above decide whether it is enough.

A custom I/O cell is in scope for evampire (see :ref:`req-process`). It can
have a stronger or faster driver, or an output impedance of 50 Ω, which
removes the external series resistor (see :doc:`electrical`). It can signal
at 2.5 V or 1.8 V, which both transceivers in :numref:`tab-rgmii-phy-io`
support and which stays within the ratings of the 3.3 V transistors. It can
also balance the rising and falling delays, and match the input paths of
RXC and RXD.

Such a cell needs a defined drive strength or output impedance, a defined
edge rate at the expected load, and protection against
:wikipedia:`electrostatic discharge <Electrostatic_discharge>` (ESD) equal to
the standard pads. It also needs Liberty timing and a board-level model at
all corners. Open designs that a custom cell can start from:

* gf180mcu_ocd_io, a community pad library that wafer.space lists as
  silicon-verified [RGMII-WAFERSPACE]_ [RGMII-OCDIO]_, used in an open
  padframe design [RGMII-OCDPADFRAME]_;
* schematics of the gf180mcu_fd_io__bi_24t pad, reverse-engineered from its
  layout, which their author notes may contain errors [RGMII-IORE]_.

.. _rgmii-gmii-alternative:

GMII is an alternative with a wider data window and more pins
-------------------------------------------------------------

GMII (:clause:`35`) sends 8 bits at the rising edge of a 125 MHz clock, so
each bit is valid for a whole 8 ns period instead of 4 ns. Its receiver
needs 2.00 ns of setup and 0.00 ns of hold, and its clock edges may take up
to 1.00 ns between 0.70 V and 1.90 V (:clause:`Table 35-8 <35>`). Those
limits are looser than the RGMII ones in :numref:`tab-rgmii-timing`, and
GMII needs no 2 ns clock delay.

GMII needs more pins, which is why RGMII was defined
(:std:`RGMII 2.0 <rgmii-2-0>` section 1.0). :numref:`tab-rgmii-gmii-pins`
counts the data and clock pins for evampire's two full-duplex ports, which
need no CRS or COL.

.. list-table:: Data and clock pins for two full-duplex ports
   :name: tab-rgmii-gmii-pins
   :header-rows: 1
   :widths: 40 30 30

   * - Interface
     - Pins per port
     - Pins for two ports
   * - RGMII
     - 12
     - 24
   * - GMII at 1000 Mbit/s
     - 22
     - 44

A GMII port has 8 data bits, an enable or valid signal, an error signal and
a clock in each direction (:clause:`35.2.2`), 22 pins in all. Two ports
therefore need 20 pins more than RGMII. Not every transceiver offers GMII:
the DP83867 has GMII in its 64-pin QFP package but only RGMII in its QFN
package [RGMII-DP83867]_ section 3.

.. _rgmii-io-open-questions:

Open questions
--------------

* The input thresholds of gf180mcu_fd_io__bi_t at a 3.3 V supply, to compare
  with the transceiver's output levels in :numref:`tab-rgmii-phy-levels`.
* The output resistance of gf180mcu_fd_io__bi_t, which sets the series
  resistor on the board.
* The thresholds at which the Liberty files measure edge times.
* Whether the RGMII pins use gf180mcu_fd_io__bi_t or a custom I/O cell,
  decided by the checks in :ref:`rgmii-custom-io`.
* Whether the first board configuration uses GMII instead of RGMII, which
  depends on evampire's pin budget.
