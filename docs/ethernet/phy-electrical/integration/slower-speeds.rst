.. _phy-int-slower:

Slower speeds
=============

This page lists what the integrated gigabit transceiver needs in addition
to support 100BASE-TX and 10BASE-T, which every port supports
(:ref:`the transceiver requirements <req-transceivers>`). Their limits are in
:numref:`tab-phy-100base-tx` and :numref:`tab-phy-10base-t`.

.. _phy-int-100:

100BASE-TX blocks
-----------------

Coding
   4B5B, the 11-bit scrambler and MLT-3 (:doc:`../100base-tx`): digital
   logic at 125 MBd on one transmit pair.
Receiver
   One pair in each direction, so no echo or crosstalk cancelling. The
   gigabit ADC and equaliser of one pair can receive it. For reference, a
   180 nm 100BASE-TX transceiver instead uses an analogue equaliser and
   five comparators, with no ADC ([PHY-BUHR21]_; [PHY-BUHR20A]_), and
   measures 2.6 mm² and at most 69 mW with coupling transformers over
   100 m of Category 5 cable ([PHY-BUHR19]_).
Edge control
   A 10 % to 90 % rise and fall time of 3 ns to 5 ns, at ±1 V, the same
   swing as the gigabit driver.

For a single-pole (first-order) response with time constant
:math:`\tau`, the output reaches 10 % of its final value at
:math:`0.105\,\tau` and 90 % at :math:`2.303\,\tau`
(:numref:`fig-phy-100base-tx-edges`), so the
:wikipedia:`rise time <Rise_time>` is :math:`t_\text{r} = 2.2\,\tau`. The
:wikipedia:`cut-off frequency <Cutoff_frequency>` is
:math:`f_\text{3dB} = 1/(2\pi\tau)`, so

.. math::

   f_\text{3dB} = \frac{2.2}{2\pi\,t_\text{r}} = \frac{0.35}{t_\text{r}}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`t_\text{r}`
     - Rise time from 10 % to 90 %
     - s
   * - :math:`\tau`
     - Time constant of the single pole
     - s
   * - :math:`f_\text{3dB}`
     - Frequency at which the response is 3 dB down
     - Hz

For :math:`t_\text{r} = 5` ns, :math:`f_\text{3dB} = 0.35 / 5\ \text{ns}
= 70` MHz; for 3 ns, 117 MHz. A single-pole transmit filter therefore needs
a bandwidth between 70 MHz and 117 MHz in 100BASE-TX mode (estimate). The
802.3ab tutorial's gigabit transmitter has a single-pole RC filter
([PHY-TUT98]_ slide 51); if its bandwidth is set in that range, or
switched for 100BASE-TX, the gigabit driver produces the 100BASE-TX edges.

.. _phy-int-10:

10BASE-T blocks
---------------

Coding and receiver
   Manchester coding and decoding, and a comparator receiver for the
   input envelope of :clause:`14.3.1.3.1`: digital logic, with no ADC.
Driver
   2.2 V to 2.8 V peak into 100 Ω (:clause:`14.3.1.2.1`), more than twice
   the gigabit swing.

A driver with a matched resistive source needs
:math:`V_\text{src} = 2\,V_\text{line}` (:ref:`phy-int-swing`), that is
4.4 V to 5.6 V peak for 10BASE-T and 3.1 V to 3.9 V for 10BASE-Te. From a
3.3 V supply a differential driver reaches at most ±3.3 V, so a matched
resistive-source driver at 3.3 V cannot reach the 10BASE-T level (estimate,
from those numbers). Other options can:

* an active termination, whose output impedance is set by feedback rather
  than a series resistor, so that less of the supply is lost in the source
  resistance. For reference, a 180 nm class-AB driver with active
  termination produced a 10BASE-T signal of about 2.5 V amplitude from
  3.3 V at 62 mW ([PHY-BUHR21]_; [PHY-BUHR20B]_), and a 0.4 µm
  current-feedback driver delivered 5 V peak-to-peak into 50 Ω from 3.3 V
  ([PHY-BABANEZHAD99]_);
* an output stage on the gf180mcu 5 V, 6 V or 10 V transistors
  (:numref:`tab-phy-int-devices`), with a supply above 3.3 V;
* 10BASE-Te, at 1.54 V to 1.96 V, which interoperates with 10BASE-T when
  its cabling requirements are met (:clause:`14.1.1.1`).

The link pulses that autonegotiation needs do not need this driver
(:ref:`phy-int-autoneg`).

.. _phy-int-slower-questions:

Open questions
--------------

* How 100 Mbit/s and 10 Mbit/s bytes cross the byte interface: a
  byte-enable flag on the 8 ns byte clock, or a slower clock.
* Which 10BASE-T driver option is used.
