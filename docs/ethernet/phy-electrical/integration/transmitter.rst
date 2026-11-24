.. _phy-int-transmitter:

Transmitter
===========

This page works out what the integrated transmitter needs: the linearity
and swing of the DAC and line driver, the power it delivers into the cable,
the termination impedance, and how the pins reach the cable without
transformers.

.. _phy-int-linearity:

DAC and driver linearity
------------------------

The peak distortion in test mode 4 must stay below 10 mV
(:clause:`40.6.1.2.4`). An ideal
:wikipedia:`digital-to-analogue converter <Digital-to-analog_converter>`
(DAC) of :math:`N` bits spanning :math:`\pm V_\text{pk}` has steps of
:math:`2V_\text{pk}/2^N`, and its largest rounding error is half a step:

.. math::

   e_\text{max} = \frac{V_\text{pk}}{2^N}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`e_\text{max}`
     - Largest rounding error of an ideal DAC
     - V
   * - :math:`V_\text{pk}`
     - Peak output voltage
     - V
   * - :math:`N`
     - Resolution of the DAC
     - bit

This counts rounding error only. With :math:`V_\text{pk} = 0.745` V, the
middle of the 0.67 V to 0.82 V range (:clause:`40.6.1.2.1`), and
:math:`e_\text{max} < 10` mV:

.. math::

   2^N &> \frac{0.745}{0.010} = 74.5 \\
   N &> \log_2 74.5 = 6.2

so the DAC and driver need at least 7 bits of linearity (estimate). With
7 bits, :math:`e_\text{max} = 0.745/128 = 5.8` mV, which leaves about 4 mV
for every other error. The 17 levels of the
:ref:`transmit shaping filter <phy-shaping>` need at
least 5 bits of resolution, so linearity, not the number of levels, sets
the DAC. A segmented current-steering DAC that drives the line directly,
or a DAC followed by a linear amplifier, can meet it
(:ref:`phy-driver-levels`).

.. _phy-int-swing:

Driver swing
------------

A driver whose output impedance matches the 100 Ω line forms a
:wikipedia:`voltage divider <Voltage_divider>` with the line, so half of
its internal voltage reaches the line (:numref:`fig-phy-int-driver`):

.. math::

   V_\text{src} = 2\,V_\text{line}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`V_\text{src}`
     - Peak differential voltage the driver generates behind its source
       resistance
     - V
   * - :math:`V_\text{line}`
     - Peak differential voltage on the line
     - V

.. graphviz:: driver.dot
   :name: fig-phy-int-driver
   :caption: A matched voltage-mode driver puts half of its internal voltage
             onto the 100 Ω line.
   :alt: The DAC and amplifier, with internal voltage Vsrc, connect through
         a 100 ohm differential source resistance to the 100 ohm pair and
         cable. A label shows Vline equals Vsrc divided by 2.
   :align: center

The 802.3ab tutorial's design point launches 2 V peak-to-peak
([PHY-TUT98]_ slide 51), so :math:`V_\text{line} = 1` V and
:math:`V_\text{src} = 2` V. A differential driver whose two outputs each
swing between 0 V and its supply :math:`V_\text{DD}` can produce up to
:math:`\pm V_\text{DD}` differentially, so a 3.3 V supply leaves 1.3 V of
headroom for the output transistors (estimate). The gf180mcu 3.3 V
transistors (:numref:`tab-phy-int-devices`) can therefore drive the
gigabit swing.

.. _phy-int-driver-power:

Driver power
------------

Assume the five PAM-5 levels are equally likely. Scrambling makes the
symbols look random, but the trellis code and idle patterns make the
levels not exactly equally likely. With level 2 at 1 V, the mean square
level is :math:`(4 + 1 + 0 + 1 + 4)/5 = 2` in units of
:math:`(0.5\ \text{V})^2`, so

.. math::

   V_\text{rms} = 0.5\ \text{V} \times \sqrt{2} = 0.71\ \text{V}

   P_\text{line} = \frac{V_\text{rms}^2}{R_\text{L}}
   = \frac{(0.71\ \text{V})^2}{100\ \Omega} = 5.0\ \text{mW}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`V_\text{rms}`
     - :wikipedia:`Root mean square <Root_mean_square>` voltage on the line
     - V
   * - :math:`P_\text{line}`
     - Power delivered into the line
     - W
   * - :math:`R_\text{L}`
     - Line impedance, 100 Ω
     - Ω

The matching resistance dissipates the same again, so an ideal matched
driver uses 10 mW per pair (estimate, ignoring the shaping filter). A real
driver uses more, because its output stage is biased for linearity. In a
28 nm gigabit transceiver the line driver is the largest consumer of power
([PHY-PAN14]_ abstract). For reference, published 180 nm drivers for the
same ±1 V swing at 100 Mbit/s use 24 mW ([PHY-BUHR18]_) to 38 mW
([PHY-RICHTER14]_); a gigabit driver has more levels and a wider band, so
these values are a lower reference, not a prediction.

.. _phy-int-termination:

Termination
-----------

Each pair must look like 100 Ω to the cable, with a return loss of at
least 16 dB from 1 MHz to 40 MHz (:clause:`40.8.3.1`). For a resistive
termination :math:`Z`, the size of the reflection is set by the
:wikipedia:`reflection coefficient <Reflection_coefficient>`:

.. math::

   |\Gamma| = 10^{-L_\text{RL}/20} = \frac{|Z - R_\text{L}|}{Z + R_\text{L}}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`\Gamma`
     - Reflection coefficient: reflected voltage divided by incident
       voltage
     - none
   * - :math:`L_\text{RL}`
     - Return loss
     - dB
   * - :math:`Z`
     - Termination impedance, assumed resistive
     - Ω

Solving for :math:`Z` with :math:`L_\text{RL} = 16` dB and
:math:`R_\text{L} = 100\ \Omega`:

.. math::

   |\Gamma| = 10^{-0.8} = 0.158

   Z_\text{min} = R_\text{L}\,\frac{1 - |\Gamma|}{1 + |\Gamma|} = 73\ \Omega

   Z_\text{max} = R_\text{L}\,\frac{1 + |\Gamma|}{1 - |\Gamma|} = 138\ \Omega

The termination must stay inside 73 Ω to 138 Ω across frequency,
temperature and process (estimate), with all other errors, such as
package and pad capacitance, inside the same window. The gf180mcu
unsalicided P+ polysilicon resistor varies ±20 % around its typical value
([PHY-GF180PDK]_ electrical parameters, resistors), so an untrimmed
100 Ω resistor spans 80 Ω to 120 Ω, inside the window.

Whether that leaves
enough of the window for the other errors depends on the error budget
(:ref:`phy-int-transmitter-questions`). Trimming the resistor, or an
active termination, are options if it does not. For reference, a 180 nm line driver with
digitally controlled output impedance covers 80 Ω to 130 Ω
([PHY-BUHR20B]_).

.. _phy-int-cable:

Connection to the cable
-----------------------

Besides the signal, the cable can carry voltage common to both wires of a
pair, surges, electrostatic discharge and, on boards that use it,
:term:`Power over Ethernet` (:doc:`/power/poe/index`). Without
transformers, the isolation and protection that the transformers gave come
from one of three routes, each open (:ref:`requirements-open-questions`):

* external high-voltage capacitors or other external parts between the
  pins and the cable;
* a second die on the cable side, either a custom gf180mcu die or a
  commercial part, with the isolation between the two dies;
* an isolation barrier on the evampire die itself.

:doc:`../../magnetics/index` analyses the circuits of each route and the
common-mode range they leave at the pins. The standard analogue pads of
gf180mcu contain only protection diodes ([PHY-GF180IO]_), sized for short
discharge events. The line driver and receiver are custom circuits, and can
use custom protection, stacked or drain-extended transistors, or the 5 V,
6 V and 10 V devices of :numref:`tab-phy-int-devices`.

.. _phy-int-transmitter-questions:

Open questions
--------------

* The error budget of the termination: package, pad and protection
  capacitance and the driver's own output impedance, and so whether the
  resistor needs trimming.
* Which isolation route the transformer-free connection uses, and so the
  common-mode range and surge level at the pins.
* The power of a gigabit line driver built in gf180mcu, which needs a
  design and a measurement with the transmitter test modes.
