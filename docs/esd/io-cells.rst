.. _esd-io-cells:

ESD protection inside the gf180mcu I/O cells
============================================

This page describes the ESD protection built into the standard gf180mcu
I/O cells, with the device sizes taken from the cells' netlists, and the
limits of each protection device measured by the foundry.

The library is rated for 2 kV human body model
----------------------------------------------

The foundry I/O library, gf180mcu_fd_io, targets 2000 V
:term:`human body model <Human body model>`, 200 V machine model and 500 V
:term:`charged device model <Charged device model>` on every pad
([ESD-GF180-IO]_, ESD protection page). It also targets ±100 mA
:term:`latch-up` immunity ([ESD-GF180-IO]_, latch-up page). No
:std:`IEC 61000-4-2` level is given for the library.

The library ships a netlist of every cell ([ESD-GF180-IO-SRC]_). This page
uses three of them:

* ``gf180mcu_fd_io__bi_t``, the bidirectional digital pad. The input-only
  pads ``in_c`` and ``in_s`` contain the same protection.
* ``gf180mcu_fd_io__dvdd`` and ``gf180mcu_fd_io__dvss``, the pads that
  bring the I/O supply DVDD and its ground DVSS onto the chip. Each one
  contains a :term:`rail clamp`.
* ``gf180mcu_fd_io__asig_5p0``, the analogue pad, which has diodes only.

The protection has three parts
------------------------------

:numref:`fig-esd-io-cell` shows the protection of the bidirectional pad
and of the supply pads. Every pad sits on two rings of metal that run
round the chip: DVDD and DVSS.

.. figure:: figures/io-cell.svg
   :name: fig-esd-io-cell
   :alt: Schematic between a DVDD rail at the top and a DVSS rail at the
         bottom. On the left, the PAD connects to a diode up to DVDD,
         labelled drain diode of PMOS drivers 480 µm, and a diode up from
         DVSS, labelled drain diode of NMOS drivers 304 µm. A 110 ohm
         resistor, four 440 ohm resistors in parallel, leads to an inner
         node with two small 40 square micrometre diodes to the rails and
         the input buffer. On the right, a rail clamp: a 360 kilohm
         resistor from DVDD and a MOS capacitor to DVSS meet at a node that
         drives three inverters, which drive the gate of a 4000 µm NMOS
         transistor connected between DVDD and DVSS.
   :width: 100%

   The ESD protection of gf180mcu_fd_io__bi_t, and the rail clamp in each
   DVDD and DVSS pad.

The primary protection is the output driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The pad has no separate primary diodes. The output transistors are the
primary protection. Their drains connect to the pad, and each drain is a
diffusion in a well, so it forms a diode with that well:

* The PMOS drains (P+ in an N-well tied to DVDD) form a diode from the pad
  to DVDD. Four transistors of 80 µm and four of 40 µm give 480 µm of
  width ([ESD-BI-T-CDL]_, lines 42 to 72).
* The NMOS drains (N+ in a P-well tied to DVSS) form a diode from DVSS to
  the pad. Eight transistors of 38 µm give 304 µm of width (same lines).

These transistors are drawn as ESD devices. Their drains are silicide
blocked for 3.78 µm (NMOS) and 2.78 µm (PMOS), and the NMOS gates are
1.15 µm long, against 0.7 µm in the rest of the cell. The design manual
requires silicide blocking at the drain of a transistor that must survive
the turn-on of its :term:`parasitic bipolar transistor <Snapback>`
([ESD-GF180-DRM-14-4]_). The blocked silicide adds resistance that spreads
the current across the whole width.

The NMOS output transistors, with their gates held low, also act as a
grounded-gate NMOS. Above about 10.7 V the parasitic NPN transistor inside
each one turns on and :term:`snaps back <Snapback>` to about 6 V
(:ref:`esd-limits`).

The secondary protection guards the input gates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The input buffer's transistor gates are reached through four 440 Ω
polysilicon resistors in parallel, about 110 Ω, and two small diodes of
40 µm² junction area to DVDD and DVSS ([ESD-BI-T-CDL]_, lines 568 to 573).
The resistor limits the current that reaches the small diodes, so the
gates stay below the pad by the voltage across it. The difference grows
with the current: in the simulated +2 kV human body model discharge the pad
reaches 5.6 V and the gates 5.4 V, and in the +8 kV IEC discharge the pad
reaches 13.7 V and the gates 11.5 V (:numref:`tab-esd-events-voltage`).

The rail clamp shorts DVDD to DVSS during a fast event
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A positive discharge into the pad, with DVSS grounded, flows through the
PMOS drain diode onto the DVDD ring. Nothing on DVDD would then let it
reach DVSS, except breakdown. Each DVDD and DVSS pad therefore contains a
rail clamp ([ESD-DVDD-CDL]_):

#. Twelve 30 kΩ polysilicon resistors in series, 360 kΩ, charge eight
   10 µm × 25 µm MOS capacitors from DVDD.
#. When DVDD rises in nanoseconds, the capacitor voltage lags, so the
   timer node stays near DVSS.
#. Three inverters, powered from DVDD itself, invert that low level. The
   third drives the gate of an NMOS transistor 4000 µm wide (80 fingers of
   50 µm) between DVDD and DVSS.
#. The transistor turns on and conducts the discharge current from DVDD to
   DVSS at a few volts.

The clamp needs no supply. The discharge itself raises DVDD, which powers
the inverters. The timer's time constant decides which events turn it on:

.. math::

   \tau_\text{clamp} = R_\text{clamp} \times C_\text{clamp},
   \qquad
   C_\text{clamp} = \frac{\varepsilon_0 \times \varepsilon_\text{ox}}{t_\text{ox}}
   \times A_\text{clamp}

.. list-table::
   :header-rows: 1
   :widths: 18 52 16 14

   * - Symbol
     - Meaning
     - Value
     - Unit
   * - :math:`\tau_\text{clamp}`
     - Time constant of the clamp timer
     - result
     - s
   * - :math:`R_\text{clamp}`
     - Timer resistor, 12 × 30 kΩ ([ESD-DVDD-CDL]_)
     - 360
     - kΩ
   * - :math:`C_\text{clamp}`
     - Timer capacitance, with the MOS capacitors in inversion
     - result
     - F
   * - :math:`\varepsilon_0`
     - Permittivity of free space
     - 8.854 × 10⁻¹²
     - F/m
   * - :math:`\varepsilon_\text{ox}`
     - Relative permittivity of the gate oxide ([ESD-GF180-MODELS]_,
       ``epsrox``)
     - 3.9
     - none
   * - :math:`t_\text{ox}`
     - Thickness of the 6 V gate oxide ([ESD-GF180-MODELS]_, ``toxe``)
     - 15.2
     - nm
   * - :math:`A_\text{clamp}`
     - Total capacitor area, 8 × 10 µm × 25 µm
     - 2000
     - µm²

The oxide capacitance is
:math:`8.854 \times 10^{-12} \times 3.9 / 15.2\ \text{nm} = 2.27\ \text{fF/µm}^2`,
so :math:`C_\text{clamp} = 2.27\ \text{fF/µm}^2 \times 2000\ \text{µm}^2 =
4.5\ \text{pF}` and
:math:`\tau_\text{clamp} = 360\ \text{k}\Omega \times 4.5\ \text{pF} =
1.6\ \text{µs}`. The foundry's capacitor model gives 2.18 fF/µm² in
inversion, 4.35 pF in all, which agrees ([ESD-GF180-MODELS]_). This is a
hand estimate. The simulations on :doc:`results-hbm` use the transistor
models instead.

The estimate holds once the capacitors are in inversion. The timer node
starts at DVSS, where the capacitors are depleted and the model gives only
0.075 pF. The node therefore rises to about 0.7 V within some tens of
nanoseconds, and only then charges at the 1.6 µs rate. 0.7 V is below the
first inverter's switching voltage, so the clamp still turns on.

A human body model discharge decays with a time constant of 150 ns, ten
times shorter than 1.6 µs, so the clamp stays on for the whole event. A
supply that rises much more slowly than 1.6 µs lets the timer node follow
DVDD, so the clamp stays off in normal use.

Each discharge mode uses a different path
-----------------------------------------

An ESD test applies each polarity between a pin and each supply pin. With
DVSS as the grounded pin, the paths are as in :numref:`tab-esd-paths`.

.. list-table:: Current paths through the bidirectional pad
   :name: tab-esd-paths
   :header-rows: 1
   :widths: 24 76

   * - Discharge
     - Path
   * - Positive, PAD to DVSS
     - PMOS drain diode onto DVDD, then the rail clamp to DVSS. Above
       10.7 V the output NMOS also snaps back, from the pad to DVSS
   * - Negative, PAD to DVSS
     - NMOS drain diode, forward biased, from DVSS to the pad
   * - Positive, PAD to DVDD
     - PMOS drain diode, forward biased, onto DVDD
   * - Negative, PAD to DVDD
     - The rail clamp from DVDD to DVSS, switched on as DVDD rises above
       DVSS, then the NMOS drain diode, forward biased, from DVSS to the
       pad. Above about 9.7 V the PMOS drain also conducts in avalanche,
       from DVDD to the pad

The analogue pad ``asig_5p0`` has the same two diode paths, with larger
dedicated diodes, each four 150 µm² parts (600 µm² in all), and no
series resistor
([ESD-ASIG-CDL]_). Its signal reaches the core directly, so the core
circuit connected to it sees the full pad voltage.

.. _esd-limits:

The foundry measured each device's limit with TLP
-------------------------------------------------

The gf180mcu design manual gives :term:`transmission line pulse <TLP>`
(TLP) measurements of each ESD device. A TLP tester applies rectangular
pulses 100 ns long with a 10 ns rise, at rising current, and measures the
voltage, and the leakage current after each one, which the figures plot
alongside ([ESD-GF180-DRM-14-4]_, [ESD-GF180-DRM-14-5-5]_). The current at
which the device fails, the :term:`second breakdown current`, scales with
the device's width, so the manual gives it per micrometre
(:numref:`tab-esd-limits`).

.. list-table:: TLP limits of 5 V and 6 V ESD devices
   :name: tab-esd-limits
   :header-rows: 1
   :widths: 34 22 22 22

   * - Device
     - Turn-on (V)
     - Failure current (mA/µm)
     - Voltage at failure (V)
   * - N+/P-well diode [ESD-GF180-DRM-14-5-7]_
     - about 1, forward
     - 30
     - 6.7
   * - P+/N-well diode [ESD-GF180-DRM-14-5-8]_
     - about 1, forward
     - 31
     - 6.9
   * - Grounded-gate NMOS [ESD-GF180-DRM-14-5-5]_
     - 10.7, snaps back to 6.2
     - 7
     - 8
   * - Grounded-gate PMOS [ESD-GF180-DRM-14-5-6]_
     - 9.7
     - 5.3
     - 14.1

The voltage that the protection reaches must stay below the limits of the
circuits it protects (:numref:`tab-esd-breakdown`).

.. list-table:: Breakdown voltages that bound the pad voltage
   :name: tab-esd-breakdown
   :header-rows: 1
   :widths: 50 25 25

   * - Breakdown
     - Minimum (V)
     - Typical (V)
   * - 6 V gate oxide [ESD-GF180-EP-OX]_
     - 12
     - 16
   * - N+ to P-well junction of a 6 V NMOS [ESD-GF180-EP-JN]_
     - 8.5
     - 11
   * - P+ to N-well junction of a 6 V PMOS [ESD-GF180-EP-JN]_
     - 8.5
     - 10.5

This section uses the minimum oxide breakdown as the limit for the input
transistors' gates. The design manual also warns that TLP results can
differ from human body model results, because the waveforms differ
([ESD-GF180-DRM-14-4]_).
