What each part of the magnetics does
====================================

This page lists the jobs that the :term:`magnetics` of a standard port do,
which part does each job, and which requirement of IEEE 802.3 or of other
standards the job meets. The parts are shown on :doc:`standard-port`.

IEEE 802.3 does not require a transformer. It sets electrical requirements
at the :term:`MDI`, and a 1:1 transformer on each pair is the most common
way of meeting them ([MAG-ENT98]_, section 2.1).
:numref:`tbl-magnetics-functions` lists the jobs.

.. list-table:: The jobs of the magnetics
   :name: tbl-magnetics-functions
   :header-rows: 1
   :widths: 34 24 42

   * - Job
     - Done by
     - Requirement
   * - :ref:`Isolating the cable from the equipment <magnetics-isolation>`
     - transformer
     - isolation test of :std:`Annex J.1 <802.3>`
   * - :ref:`Rejecting common-mode voltage <magnetics-common-mode>`
     - transformer and choke
     - MDI impedance balance, :clause:`40.8.3.2`
   * - :ref:`Blocking DC <magnetics-common-mode>`
     - transformer
     - isolation, and Power over Ethernet at up to 57 V
   * - :ref:`Matching the 100 Ω cable <magnetics-return-loss>`
     - 1:1 transformer
     - MDI return loss, :clause:`40.8.3.1`
   * - :ref:`Passing low frequencies <magnetics-droop>`
     - transformer inductance
     - transmitter droop, :clause:`40.6.1.2.2`
   * - :ref:`Terminating common-mode signals <magnetics-cm-termination>`
     - 75 Ω resistors and a 1000 pF capacitor
     - radio-emission limits
   * - :ref:`Filtering common-mode noise <magnetics-choke>`
     - common-mode choke
     - radio-emission limits
   * - :ref:`Surviving surges and discharges <magnetics-surge>`
     - transformer and protection diodes
     - product immunity tests
   * - :ref:`Biasing the line driver <magnetics-driver-bias>`
     - circuit-side centre tap
     - the transceiver's data sheet
   * - :ref:`Carrying Power over Ethernet current <magnetics-poe-current>`
     - cable-side centre taps
     - :clause:`Table 145-16 <145>`
   * - :ref:`Hiding the data circuits from detection <magnetics-poe-detection>`
     - transformer
     - :clause:`Table 145-21 <145>`
   * - :ref:`Letting any pair carry any direction <magnetics-identical>`
     - four identical channels
     - automatic MDI/MDI-X, :clause:`40.4.4`

Matching and low frequencies are covered on :doc:`matching-and-droop`, and
Power over Ethernet on :doc:`poe`. The other jobs are described below.

.. _magnetics-isolation:

Isolation keeps ground differences off the transceiver
------------------------------------------------------

:term:`Galvanic isolation` means that no conducting path joins two
circuits: no direct current can flow between them, and a large voltage
between them does no harm up to a rated limit. The two ends of an Ethernet
cable can be in different buildings, powered from different parts of the
mains wiring. Their ground voltages can differ, by much more during a fault
or a nearby lightning strike. Without isolation, that difference would
drive current along the cable and through both transceivers.

Every twisted-pair Ethernet port must be isolated from the rest of the
equipment, including its frame ground (:clause:`14.3.1.1`,
:clause:`25.4.6`, :clause:`40.6.1.1`). A port that also carries Power over
Ethernet meets :clause:`33.4.1` or :clause:`145.4.1` instead. The isolation
must withstand at least one of the tests in
:numref:`tbl-magnetics-hipot`, from :std:`Annex J.1 <802.3>` of IEEE
802.3-2022. A test of this kind is often called a
:wikipedia:`hipot test <Hipot>`, short for high potential.

.. list-table:: The isolation tests of IEEE 802.3. A port passes at least
                one.
   :name: tbl-magnetics-hipot
   :header-rows: 1
   :widths: 34 22 22 22

   * - Test
     - Voltage (V)
     - Shape
     - Duration
   * - Alternating voltage
     - 1500 rms
     - 50 Hz to 60 Hz
     - 60 s
   * - Direct voltage
     - 2250
     - steady
     - 60 s
   * - Impulses, port without Power over Ethernet
     - 2400
     - 1.2/50 µs
     - ten impulses
   * - Impulses, port with Power over Ethernet
     - 1500
     - 10/700 µs
     - ten impulses

A 1.2/50 µs impulse rises in 1.2 µs and falls to half its peak in 50 µs.
The impulses of the first impulse test alternate in polarity, at least 1 s
apart (:std:`Annex J.1 <802.3>`). The impulses for a Power over Ethernet
port are 60 s apart (:clause:`145.4.1`). The 1500 V rms test has a peak of
2121 V.

The port passes when there is no insulation breakdown during the test, and
the resistance afterwards is at least 2 MΩ, measured at 500 V. Annex J.1
counts as breakdown a current that rises rapidly and without control. A
steady current through a capacitor is therefore not breakdown, which
matters for ports coupled through capacitors (:doc:`isolation`).

IEEE 802.3-2022 removed its earlier references to the withdrawn safety
standard IEC 60950-1, and states that the tests need no other standard
(:std:`Annex J.1 <802.3>`, note 2). Product safety is left to standards
such as :std:`IEC 62368-1` (:std:`Annex J.2 <802.3>`).

Power over Ethernet adds two isolation environments (:clause:`33.4.1.1`).
Environment A is a network inside one building and one low-voltage power
system. Environment B crosses between buildings or power systems.
Environment A relaxes only the isolation between the power circuits of
different ports. It keeps the isolation between each port and the
equipment.

Parts across the barrier must withstand the test voltage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any part connected between the cable side and the equipment side bridges
the isolation. Examples are the capacitor to chassis in the common-mode
termination, a coupling capacitor, or a resistor between two grounds. Such
a part must withstand the voltage of the test that the port is qualified
with.

These pages take a part as suitable when its maker states a withstand
(test) voltage at least as high as that test voltage: 2121 V peak for the
alternating test, or 2250 V for the direct test. Its rated working voltage
can be lower. Magnetics data sheets state the isolation of the whole part,
most often 1500 V rms for 60 s ([MAG-PULSE]_, [MAG-WURTH]_, [MAG-BEL]_).

.. _magnetics-common-mode:

The transformer rejects common-mode voltage and blocks DC
---------------------------------------------------------

Any voltage on a pair has two parts. The :term:`differential-mode voltage`
is the difference between the two wires, and carries the data. The
:term:`common-mode voltage` is the average of the two wires, measured
against a ground, and carries no data.

A transformer couples only the voltage across a winding. It passes the
differential signal and blocks the common-mode voltage and direct current.
Each side of the transformer can therefore sit at its own voltage. The
transceiver stays near its own supply, and the cable sits wherever the far
end, a ground difference or Power over Ethernet puts it.

Real transformers pass some common-mode signal through the capacitance
between their windings at high frequencies, which is why a choke is added
(:ref:`magnetics-choke`). Data sheets give the rejection as "common-mode
rejection": for example 33 dB to 43 dB from 30 MHz to 100 MHz for the Pulse
H5007NL ([MAG-PULSE]_, electrical table), and 30 dB to 35 dB for the Bel
0826-1G1T-23-F ([MAG-BEL]_, electrical table).

IEEE 802.3 sets the related requirement at the MDI as an impedance balance
(:clause:`40.8.3.2`). A common-mode voltage applied to the pair must produce
only a small differential voltage: the ratio must exceed
:math:`34 - 19.2 \log_{10}(f / 50\ \text{MHz})` dB from 1 MHz to 100 MHz.
This is 66.6 dB at 1 MHz and 28.2 dB at 100 MHz.

.. _magnetics-cm-termination:

The termination absorbs common-mode currents
--------------------------------------------

Each pair, taken as a whole, also forms a transmission line with every
other pair. Common-mode currents travel along these lines. If the ends are
left open, the currents reflect back and forth and radiate.

Each cable-side centre tap therefore goes through a 75 Ω resistor to a node
shared by the four pairs. Between any two pairs there are then two
resistors in series, 150 Ω. This is close to the 145 Ω pair-to-pair
impedance of :wikipedia:`Category 5 <Category_5_cable>` cable, so the
energy is absorbed in the resistors instead of radiated. The patent that
describes the network reports about 10 dB less emission and susceptibility
[MAG-SMITH]_. The network is called the
:term:`Bob Smith termination` after its inventor.

The shared node goes to chassis ground through one capacitor, most often
1000 pF rated 2 kV ([MAG-KSZ9031]_, section 12; [MAG-WURTH]_;
[MAG-BEL]_). The capacitor is not part of the patent ([MAG-ENT98]_, section
3.2). Its impedance falls with frequency:

.. math::

   \lvert Z_C \rvert = \frac{1}{2\pi f C}

.. list-table::
   :header-rows: 1
   :widths: 18 62 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`\lvert Z_C \rvert`
     - Magnitude of the capacitor's impedance
     - Ω
   * - :math:`f`
     - Frequency
     - Hz
   * - :math:`C`
     - Capacitance
     - F

For :math:`C = 1000\ \text{pF}`, at 50 Hz and at 30 MHz:

.. math::

   \lvert Z_C \rvert_{50\ \text{Hz}} &= \frac{1}{2\pi \times 50 \times 10^{-9}}\ \Omega
   = 3.2\ \text{M}\Omega

   \lvert Z_C \rvert_{30\ \text{MHz}} &= \frac{1}{2\pi \times 3 \times 10^{7}
   \times 10^{-9}}\ \Omega = 5.3\ \Omega

The termination works at signal frequencies, while at mains frequency the
capacitor is nearly an open circuit and keeps the isolation. It sits across
the isolation barrier, so it must withstand the test voltage
(:ref:`magnetics-isolation`).

.. _magnetics-choke:

The choke filters common-mode noise
-----------------------------------

A :term:`common-mode choke` is two windings on one core, one in each wire
of a pair. The data current flows out on one wire and back on the other,
so the magnetic fields of the two windings cancel and the data sees almost
no inductance. A common-mode current flows the same way on both wires, the
fields add, and it sees a high impedance.

Noise from the board couples equally onto both traces of a pair and becomes
common-mode voltage, and so does any imbalance in the transmitter. An
unshielded twisted pair carrying common-mode current radiates, and that
radiation is what fails radio-emission limits such as
:std:`FCC Part 15 <fcc-part-15>`. In the other direction, the cable picks
up common-mode noise from its surroundings, and the choke and transformer
keep it from the receiver ([MAG-ENT98]_, section 2.1.2).

In most parts the choke sits on the cable side of the transformer. Microchip
reports less margin in the transmit waveform tests with the choke on the
transceiver side ([MAG-ENT98]_, section 3.5). Some magnetics add a third
part on each pair, an :wikipedia:`autotransformer <Autotransformer>`: one
centre-tapped winding across the pair, which gives common-mode current a
low-impedance path to the termination. Parts with a transformer, choke and
autotransformer on each pair are sold as "12-core", and those without the
autotransformer as "8-core" ([MAG-ENT98]_, sections 3.3 to 3.6).

.. _magnetics-surge:

Surges pass the transformer only as differential signals
--------------------------------------------------------

A common-mode surge raises the whole cable in voltage against the
equipment. It appears across the transformer's isolation, which holds it
off up to its rating, and the transceiver sees only what couples through
the winding capacitance. A differential surge, between the wires of a
pair, passes through the transformer like a signal and is clamped by
protection diodes.

Texas Instruments places these diodes on the transceiver side of the
magnetics, because on the cable side large common-mode voltages can make
them conduct and fail ([MAG-SNLA387]_, section 2, "ESD Device Selection and Layout"). The sizes of these
events are given on :doc:`events`.

.. _magnetics-driver-bias:

The circuit-side centre tap biases the line driver
--------------------------------------------------

How the circuit-side centre tap is connected depends on the kind of line
driver in the transceiver (:numref:`fig-magnetics-centre-tap-bias`, and
:doc:`../phy-electrical/index`):

Current-mode driver
   The driver switches a current between the two pins of the pair, and its
   transistors only sink current. The current is supplied through pull-up
   resistors and the centre tap, which are tied to a supply. Texas
   Instruments' DP83848 uses a 49.9 Ω resistor from each pin to the 3.3 V
   analogue supply, with the centre taps tied to the same supply
   ([MAG-SDAA089]_, section 3.2).
Voltage-mode driver
   The driver drives each pin from a low impedance, sets its own
   common-mode voltage, and has its termination on the chip. The centre tap
   is not tied to a supply: each centre tap goes to ground through its own
   0.1 µF capacitor ([MAG-KSZ9031]_, section 12; [MAG-DP83867]_,
   section 9.2).

Both kinds of driver also work with capacitors in place of the
transformer, as described on :doc:`without-transformer`.

.. graphviz:: centre-tap-bias.dot
   :name: fig-magnetics-centre-tap-bias
   :caption: The circuit-side centre tap of one pair, for a current-mode
             driver (top) and a voltage-mode driver (bottom).
   :alt: Two schematics. Top: transceiver with switched current sinks, each
         pin with a 49.9 ohm resistor to a supply rail, the transformer
         centre tap tied to the same rail and to a 0.1 microfarad capacitor.
         Bottom: transceiver with push-pull drivers, the transformer centre
         tap connected only to a 0.1 microfarad capacitor to signal ground.
   :align: center

.. _magnetics-identical:

Four identical channels let any pair carry any direction
--------------------------------------------------------

Automatic MDI/MDI-X configuration (:doc:`cable`) can swap pair A with pair
B and pair C with pair D. Each channel of the magnetics can therefore end up
carrying any signal in either direction, and all four channels are the
same.
