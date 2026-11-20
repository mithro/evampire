Coupling capacitors in place of a transformer
=============================================

This page describes the ports that already connect to twisted-pair cable
without a transformer, and works out the size of the capacitors that carry
the data in their place. :doc:`without-transformer` covers the other jobs
of the transformer, and :doc:`isolation` covers isolation.

Several kinds of port already work without transformers
-------------------------------------------------------

These ports are reference examples of the techniques. Each was built in
another process or product; whether the same works for evampire is
established only by building it.

Capacitor-coupled 10 and 100 Mbit/s
   Texas Instruments documents its DP83848 transceiver connected through a
   33 nF capacitor in each wire ([MAG-SNLA088]_, figure 5). Its bit-error
   tests ran without errors over cables up to 100 m at 10 and 100 Mbit/s.
   Some IEEE 802.3 compliance tests did not pass, and the note asks for
   connections longer than 1 m to be verified in the application
   ([MAG-SNLA088]_, sections 2 and 7).
Backplanes
   Microchip documents its voltage-mode transceivers connected directly
   through blocking capacitors, on one board or over a backplane
   ([MAG-ENT114]_).
Single-pair automotive and industrial Ethernet
   100BASE-T1 (:clause:`96`), 1000BASE-T1 (:clause:`97`) and 10BASE-T1L
   (:clause:`146`) ports use 100 nF blocking capacitors, a common-mode
   choke, and a common-mode termination of two 1 kΩ resistors and a 4.7 nF
   capacitor, with no transformer ([MAG-DP83TC811]_, MDI table;
   [MAG-OA100T1]_, figure 1). These clauses set no isolation test for the
   cable (:clause:`96.9.1`, :clause:`97.9.1`, :clause:`146.9.1`).
Power over one pair
   IEEE 802.3bu ([MAG-8023BU]_) and 802.3cg ([MAG-8023CG]_) put power on
   a single pair through inductors, and keep it out of the data path with
   capacitors ([MAG-GARDNER14]_; [MAG-DP83TD510E]_, power coupling
   section; [MAG-TDKSPE]_).
Power over Ethernet without data transformers
   Patents describe four-pair Power over Ethernet with inductors or active
   circuits for the power and high-voltage capacitors for the data
   ([MAG-US8132027]_, [MAG-US7851938]_, [MAG-US9189036]_).
Capacitor-coupled 1000BASE-T
   Analog Devices documents its ADIN1300 gigabit transceiver connected
   through a 33 nF capacitor in each wire. It reports no packet loss, and
   signal quality comparable to transformers, over cables from 2 m to 100 m
   ([MAG-ADIWIKI]_). The same page recommends a common-mode choke for
   cables longer than 1 m, and does not state the link speed of the long
   tests.

Capacitor coupling is therefore shown for gigabit Ethernet over a full
cable in one vendor report. :doc:`gigabit-risk` works through what else
can limit it.

The data path becomes a capacitor in each wire
----------------------------------------------

Replacing the transformer with a capacitor in each wire turns the data path
into a series capacitor instead of a parallel inductor.
:numref:`fig-magnetics-cap-model` shows the model used below: the
transceiver as a 100 Ω source, the cable as a 100 Ω load, and one
capacitor :math:`C_\text{w}` in each wire. The two capacitors are in series
around the loop, so the pair sees half the capacitance of one:

.. graphviz:: cap-model.dot
   :name: fig-magnetics-cap-model
   :caption: The model used to size the coupling capacitors.
   :alt: A transceiver drawn as a 100 ohm source connects to the cable,
         drawn as a 100 ohm load, through two wires, each with a coupling
         capacitor C_w in series.
   :align: center

.. math::

   C_\text{pair} = \frac{C_\text{w}}{2}

.. list-table::
   :header-rows: 1
   :widths: 18 62 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`C_\text{w}`
     - Coupling capacitor in each wire
     - F
   * - :math:`C_\text{pair}`
     - Capacitance in series with the pair
     - F

The model leaves out the capacitance from each wire to ground, which
:doc:`gigabit-risk` treats separately.

Return loss needs at least 9.9 nF
---------------------------------

A 1000BASE-T port must have at least 16 dB of return loss from 1 MHz
(:doc:`matching-and-droop`). The capacitors add a reactance in series with
an otherwise perfect 100 Ω port, so the port impedance is
:math:`Z = Z_0 - jX`, where :math:`j` is the imaginary unit. From the
reflection coefficient of :doc:`matching-and-droop`:

.. math::

   \lvert\Gamma\rvert = \frac{X}{\sqrt{(2 Z_0)^2 + X^2}}

   X_\text{max} = \frac{2 Z_0 \lvert\Gamma\rvert_\text{max}}
   {\sqrt{1 - \lvert\Gamma\rvert_\text{max}^2}}

   C_\text{pair} \ge \frac{1}{2\pi f X_\text{max}}

.. list-table::
   :header-rows: 1
   :widths: 18 62 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`X`
     - Reactance of the coupling capacitors, :math:`1/(2\pi f C_\text{pair})`
     - Ω
   * - :math:`X_\text{max}`
     - Largest reactance that meets the return loss limit
     - Ω
   * - :math:`\lvert\Gamma\rvert_\text{max}`
     - Largest reflection coefficient allowed, 0.1585 for 16 dB
     - none
   * - :math:`f`
     - Lowest frequency of the limit, 1 MHz
     - Hz

With :math:`Z_0 = 100\ \Omega`:

.. math::

   X_\text{max} = \frac{200\ \Omega \times 0.1585}{\sqrt{1 - 0.1585^2}}
   = \frac{31.7}{0.987}\ \Omega = 32.1\ \Omega

   C_\text{pair} \ge \frac{1}{2\pi \times 1\ \text{MHz} \times 32.1\ \Omega}
   = 4.96\ \text{nF}

   C_\text{w} \ge 9.9\ \text{nF}

The capacitors alone then use the whole 16 dB budget, so real
capacitors must be larger.

Droop needs at least 16 nF
--------------------------

The series capacitor forms a high-pass filter with the source and load
resistances in series:

.. math::

   \tau = (R_\text{s} + Z_0)\, C_\text{pair}

   C_\text{w} = \frac{2\tau}{R_\text{s} + Z_0}

The symbols are those of :doc:`matching-and-droop`, with
:math:`R_\text{s} + Z_0 = 200\ \Omega`. For the 1000BASE-T droop limit,
:math:`\tau_\text{min} = 1.6\ \mu\text{s}`, and to match standard
magnetics, :math:`\tau_\text{mag} = 7.0\ \mu\text{s}`:

.. math::

   C_\text{w} \ge \frac{2 \times 1.6\ \mu\text{s}}{200\ \Omega} = 16\ \text{nF}

   C_\text{w} = \frac{2 \times 7.0\ \mu\text{s}}{200\ \Omega} = 70\ \text{nF}

At exactly 16 nF the port meets the droop limit with no margin: 73.2 % of
the voltage is left after 500 ns, against 73.1 % required. Its high-pass
corner is 99.5 kHz, at the edge of the 1 Hz to 100 kHz range that the
transmit templates assume (:clause:`40.6.1.2.3`, note 1).

100BASE-TX sets a phase limit
-----------------------------

If 100BASE-TX is supported, its transmitter must look resistive within a
phase angle of 3° from 2 MHz to 80 MHz (:std:`ANSI X3.263 <X3.263>`, as
quoted in [MAG-SNLA088]_, appendix A). The reactance must then be below
:math:`Z_0 \tan 3^\circ`:

.. math::

   X \le 100\ \Omega \times \tan 3^\circ = 5.24\ \Omega

   C_\text{pair} \ge \frac{1}{2\pi \times 2\ \text{MHz} \times 5.24\ \Omega}
   = 15.2\ \text{nF}

   C_\text{w} \ge 30.4\ \text{nF}

Texas Instruments calculates 30.42 nF and uses 33 nF ([MAG-SNLA088]_,
appendix A), as does Analog Devices for its gigabit transceiver
([MAG-ADIWIKI]_).

A 100BASE-TX transmitter in a Type 3 or Type 4 Power over Ethernet port
can instead meet an equivalent time constant above 2.4 µs
(:clause:`25.4.5.1`, :doc:`matching-and-droop`). In the model this needs
:math:`C_\text{w} \ge 2 \times 2.4\ \mu\text{s} / 200\ \Omega = 24\ \text{nF}`.
Whether a port without a transformer can use this route in place of the
inductance requirement is an open question below.

The results give a working range
--------------------------------

:numref:`tbl-magnetics-cap-size` collects the limits.

.. list-table:: Smallest coupling capacitor in each wire
   :name: tbl-magnetics-cap-size
   :header-rows: 1
   :widths: 60 18 22

   * - Requirement
     - :math:`C_\text{w}` (nF)
     - Source
   * - 1000BASE-T return loss at 1 MHz, no margin
     - 9.9
     - :clause:`40.8.3.1`
   * - 1000BASE-T droop, no margin
     - 16
     - :clause:`40.6.1.2.2`
   * - Same low-frequency corner as 350 µH magnetics
     - 70
     - :doc:`matching-and-droop`
   * - 100BASE-TX phase angle under 3° at 2 MHz
     - 30.4
     - :std:`X3.263`
   * - 100BASE-TX time constant above 2.4 µs, Power over Ethernet ports
     - 24
     - :clause:`25.4.5.1`

The last two rows apply only if 100BASE-TX is supported. A value from
33 nF to 100 nF in each wire is a reasonable estimate of the working range:
above the droop limit with margin, and near the behaviour of standard
magnetics. :doc:`gigabit-risk` shows what each value means for the
received signal, and :doc:`isolation` how many high-voltage parts it takes.

Capacitors on the chip cost area
--------------------------------

The capacitors can also be built on evampire, if they hold the voltages
of :doc:`events` or sit behind another isolation barrier
(:doc:`isolation`). The area of one capacitor is its capacitance divided
by the capacitance per area. A capacitor that must hold a voltage beyond
one device's rating can be built as :math:`N` devices in series. Each must
then be :math:`N` times larger, so the area grows as :math:`N^2`:

.. math::

   A = N^2 \frac{C}{c_\text{A}}

.. list-table::
   :header-rows: 1
   :widths: 18 62 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`A`
     - Die area of one coupling capacitor
     - mm²
   * - :math:`N`
     - Number of devices in series
     - none
   * - :math:`C`
     - Capacitance needed
     - F
   * - :math:`c_\text{A}`
     - Capacitance per area of one device
     - F/mm²

The densest gf180mcu metal-insulator-metal (MIM) capacitor gives
2.0 fF/µm², rated 6.6 V ([MAG-GF180]_, MIM capacitor table). For one device
(:math:`N = 1`) and :math:`C = 16\ \text{nF}`:

.. math::

   A = \frac{16\ \text{nF}}{2.0\ \text{fF/µm}^2}
   = 8.0 \times 10^6\ \mu\text{m}^2 = 8.0\ \text{mm}^2

:numref:`tbl-magnetics-cap-area` gives the area for one port, eight wires,
at the four capacitor values used on these pages. These are estimates;
the die area that evampire can give them is not fixed.

.. list-table:: Die area of the coupling capacitors for one port, with
                single 2.0 fF/µm² MIM devices (estimate)
   :name: tbl-magnetics-cap-area
   :header-rows: 1
   :widths: 50 50

   * - :math:`C_\text{w}` (nF)
     - Area for eight wires, :math:`N = 1` (mm²)
   * - 16
     - 64
   * - 33
     - 132
   * - 70
     - 280
   * - 100
     - 400

A capacitor that uses the whole stack of oxide between the metal layers,
about 5 µm thick (:doc:`isolation`), has a much lower capacitance per area:

.. math::

   c_\text{A} = \frac{\varepsilon_0 \varepsilon_\text{r}}{d}
   = \frac{8.854 \times 10^{-12} \times 3.9}{5 \times 10^{-6}}\
   \text{F/m}^2
   = 0.0069\ \text{fF/µm}^2

.. list-table::
   :header-rows: 1
   :widths: 18 62 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`\varepsilon_0`
     - :wikipedia:`Permittivity <Vacuum_permittivity>` of free space,
       :math:`8.854 \times 10^{-12}`
     - F/m
   * - :math:`\varepsilon_\text{r}`
     - Relative permittivity of silicon dioxide, 3.9
     - none
   * - :math:`d`
     - Thickness of the oxide
     - m

At that density a 16 nF capacitor takes about 2300 mm². Small on-chip
capacitors can instead isolate a signal that has first been turned into a
high-frequency form, as digital isolators (see :wikipedia:`Galvanic isolation <Galvanic_isolation>`)
do, with active circuits on both sides of the barrier. That is the
on-die route of :doc:`isolation`.

Open questions
--------------

* Does a capacitor-coupled 100BASE-TX transmitter in a Power over Ethernet
  port satisfy :clause:`25.4.5` through the 2.4 µs time constant, in place
  of the 350 µH inductance? This matters only if 100BASE-TX is supported.
* Which value in the 33 nF to 100 nF range gives the best balance between
  link margin, part count and detection capacitance? :doc:`gigabit-risk`
  describes the measurements that answer it.
