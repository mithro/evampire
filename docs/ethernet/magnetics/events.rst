Voltages and events at the cable
================================

This page lists the voltages, currents and energies that reach an Ethernet
port from its cable, from the data signal to lightning surges. A port
without a transformer must survive all of them and keep the signal intact.
It is a reference page; the jobs of the transformer are described on
:doc:`functions`.

The signals and Power over Ethernet are continuous
--------------------------------------------------

:numref:`tbl-magnetics-continuous` lists what is present on a working
link all the time.

.. list-table:: Continuous voltages at an Ethernet port
   :name: tbl-magnetics-continuous
   :header-rows: 1
   :widths: 40 15 15 30

   * - Quantity
     - Min (V)
     - Max (V)
     - Source
   * - 1000BASE-T transmit peak, differential
     - 0.67
     - 0.82
     - :clause:`40.6.1.2.1`
   * - 100BASE-TX transmit peak, differential
     - 0.95
     - 1.05
     - [MAG-UNH25]_, test 25.1.1
   * - 10BASE-T transmit peak, differential
     - 2.2
     - 2.8
     - :clause:`14.3.1.2.1`
   * - Power over Ethernet, between pairs
     -
     - 57
     - :clause:`Table 145-16 <145>`

Power over Ethernet also carries up to 0.948 A on each pair
(:doc:`poe`).

Tests and disturbances are short
--------------------------------

:numref:`tbl-magnetics-events` lists the tests and the disturbances that
the port meets from time to time. Each is described below the table.

.. list-table:: Tests and disturbances at an Ethernet port
   :name: tbl-magnetics-events
   :header-rows: 1
   :widths: 34 14 22 30

   * - Event
     - Peak (kV)
     - Duration
     - Source
   * - Isolation test, alternating
     - 2.1
     - 60 s
     - :std:`Annex J.1 <802.3>`
   * - Isolation test, direct
     - 2.25
     - 60 s
     - :std:`Annex J.1 <802.3>`
   * - Isolation impulse test
     - 2.4
     - 50 µs
     - :std:`Annex J.1 <802.3>`
   * - Human-body model discharge
     - 2
     - about 200 ns
     - [MAG-ESDA]_
   * - System-level discharge, contact, level 4
     - 8
     - rise 0.7 ns to 1 ns
     - :std:`IEC 61000-4-2`; [MAG-SLVA711]_, table 1
   * - Fast transient bursts, data lines, level 4
     - 2
     - 5/50 ns pulses
     - :std:`IEC 61000-4-4`; [MAG-SLVA711]_, table 2
   * - Surge, level 4
     - 4
     - 1.2/50 µs
     - :std:`IEC 61000-4-5`; [MAG-SLVA711]_, table 3
   * - Charged cable discharge
     - up to 5
     - longer than 600 ns
     - [MAG-SNLA087]_; [MAG-DEATHERAGE]_

Isolation tests
   The voltages of :doc:`functions` (:numref:`tbl-magnetics-hipot`). A
   Power over Ethernet port uses a 1500 V, 10/700 µs impulse instead of the
   2400 V impulse (:clause:`145.4.1`).
Human-body model
   The test that classifies a chip's pins by the discharge from a charged
   person handling it: 100 pF through 1.5 kΩ (:std:`JS-001`;
   [MAG-ESDA]_). It is a test of the chip, not of the finished product.
System-level discharge
   The test of the finished product against a discharge to its connectors:
   150 pF through 330 Ω ([MAG-SLVA711]_, section 1.2). Levels 1 to 4 are
   2 kV to 8 kV for a contact discharge.
Fast transient bursts
   Bursts of 5/50 ns pulses lasting 15 ms, coupled onto the cable by a
   clamp. Levels 1 to 4 are 0.25 kV to 2 kV for data lines
   ([MAG-SLVA711]_, section 2.2).
Surge
   A slow, high-energy pulse such as one caused by lightning: a 1.2/50 µs
   voltage and an 8/20 µs current. Levels 1 to 4 are 0.5 kV to 4 kV. On a
   data line the source impedance is 42 Ω ([MAG-SLVA711]_, section 3.3).
Charged cable discharge
   A long cable can hold charge, from static or from a power fault, and
   discharges into the port when it is plugged in. Tests have charged cables
   to between 0.75 kV and 5 kV ([MAG-DEATHERAGE]_), and a TI note describes
   events of "a few thousand volts" ([MAG-SNLA087]_).

Which level a product must pass is set by the product standard for its
market, not by IEEE 802.3. The tables give level 4, the highest
standard level, as the design limit.

The energy and current of each event
------------------------------------

The energy of a capacitor-discharge test is the energy stored in the test
capacitor, and its peak current is the test voltage divided by the source
resistance:

.. math::

   E = \tfrac{1}{2} C V^2

   I_\text{peak} = \frac{V}{R}

.. list-table::
   :header-rows: 1
   :widths: 18 62 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`E`
     - Energy stored in the test capacitor
     - J
   * - :math:`C`
     - Test capacitance
     - F
   * - :math:`V`
     - Test voltage
     - V
   * - :math:`I_\text{peak}`
     - Peak current, neglecting the inductance of the discharge path
     - A
   * - :math:`R`
     - Source resistance of the test
     - Ω

For the human-body model at 2 kV and the system-level discharge at 8 kV:

.. math::

   E_\text{HBM} &= 0.5 \times 100\ \text{pF} \times (2\ \text{kV})^2
   = 0.2\ \text{mJ}

   E_\text{IEC} &= 0.5 \times 150\ \text{pF} \times (8\ \text{kV})^2
   = 4.8\ \text{mJ}

.. math::

   I_\text{HBM} &= \frac{2\ \text{kV}}{1.5\ \text{k}\Omega} = 1.3\ \text{A}

   I_\text{IEC} &= \frac{8\ \text{kV}}{330\ \Omega} = 24\ \text{A}

The standard system-level current waveform at 8 kV has a first peak of
about 30 A, shaped by the generator rather than by this resistance alone
([MAG-SLVA711]_, figure 1). The surge at level 4 drives
:math:`4\ \text{kV} / 42\ \Omega = 96\ \text{A}` into a short circuit
([MAG-SLVA711]_, table 4).

The kind of event decides the protection
----------------------------------------

Short, low-energy events
   The human-body model is the kind of event that on-chip protection is
   designed for. The protection diodes and clamps in an I/O cell conduct
   for a few hundred nanoseconds and absorb a bounded charge. The gf180mcu
   I/O library targets 2 kV human-body model ([MAG-GFIO]_). A system-level
   discharge carries 24 times the energy (4.8 mJ against 0.2 mJ) and a peak
   current of tens of amperes.
Long or large events
   Surges and charged cables deliver tens of amperes for microseconds.
Sustained voltages
   Power over Ethernet at 57 V and the 60 s isolation test are not events
   at all. A clamp that conducted during them would be destroyed or would
   break the isolation. They must be held off by a part that withstands the
   full voltage continuously.

Conventional designs protect against system-level discharges and surges
with external protection devices ([MAG-SLVA711]_, sections 1.1 and 3.2). Which events evampire's
on-chip clamps can take is discussed on :doc:`without-transformer`.
