.. _poe-pd-side:

What a powered device must do
=============================

This page lists what the end that receives power, port A on a
first-version board, must do at each step of the sequence on
:doc:`sequence`.

Accept either polarity on either pair set
-----------------------------------------

The powered device does not know which pair set will carry power or which
pair will be positive (:doc:`basics`). It therefore puts a
:wikipedia:`full-wave bridge rectifier <Diode_bridge>` on each pair set and
joins the two outputs. The joined outputs are the positive and negative
inputs of the rest of the circuit.

A bridge of ordinary diodes loses two diode drops. A bridge of
:wikipedia:`Schottky diodes <Schottky_diode>` loses less but leaks more
current backwards. The leakage matters because the powered device may put
at most 2.8 V onto an unpowered pair set (:clause:`Table 145-29 <145>`,
item 18, and :clause:`145.3.8.8`). A bridge of
:wikipedia:`MOSFETs <MOSFET>` switched on as rectifiers loses less again.

The bridge also adds series resistance and an offset voltage during
detection. For reference, the LT4275 controller data sheet allows up to
1.1 kΩ for the bridge [POE-LT4275]_ (Applications Information). A MOSFET
bridge must not conduct backwards during detection, because a
single-signature powered device must show an invalid signature on one
pair set while 3.7 V to 57 V is applied to the other (:clause:`145.3.5`).

Show a 25 kΩ detection signature
--------------------------------

Over the whole range of 2.7 V to 10.1 V at its input, a powered device
shows a valid :term:`detection signature` when (:clause:`Table 145-21 <145>`):

* the resistance measured between any two points at least 1 V apart is
  23.7 kΩ to 26.3 kΩ;
* the offset voltage is at most 1.9 V;
* the input capacitance is 0.05 µF to 0.12 µF;
* the series inductance is at most 100 µH.

To make sure it is not detected, for example during a mark event or when it
refuses power, the powered device shows less than 12 kΩ or more than 45 kΩ,
or more than 10 µF (:clause:`Table 145-22 <145>`).

The signature is usually a resistor across the bridge output. The valid
window is about 25 kΩ ± 5 %, which is the whole error budget for the
resistor, the bridge and the controller's leakage:

.. math::

   R_\text{low} &= R_\text{nom} \times (1 - 0.05) \\
   &= 23.75\ \text{k}\Omega \\
   R_\text{high} &= R_\text{nom} \times (1 + 0.05) \\
   &= 26.25\ \text{k}\Omega

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`R_\text{nom}`
     - Nominal signature resistance, 25 kΩ
     - kΩ
   * - :math:`R_\text{low}`, :math:`R_\text{high}`
     - Edges of a ± 5 % window around it
     - kΩ

The standard's window, 23.7 kΩ to 26.3 kΩ, is this window rounded outwards
to 0.1 kΩ.

Controller makers choose slightly below 25 kΩ to leave room for the bridge.
For reference, Texas Instruments recommends an external 24.9 kΩ, 1 %
resistor for the TPS2378 [POE-TPS2378]_ (Application and Implementation), and the LT4275
integrates a 24.4 kΩ resistor that stays within 23.7 kΩ to 25.2 kΩ
[POE-LT4275]_ (Electrical Characteristics). With the 1.1 kΩ bridge
allowance the LT4275's worst case is:

.. math::

   R_\text{sig,max} &= R_\text{int,max} + R_\text{bridge,max} \\
   &= 25.2\ \text{k}\Omega + 1.1\ \text{k}\Omega \\
   &= 26.3\ \text{k}\Omega

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`R_\text{int,max}`
     - Highest internal signature resistance of the LT4275
     - kΩ
   * - :math:`R_\text{bridge,max}`
     - Highest bridge resistance the LT4275 allows for
     - kΩ
   * - :math:`R_\text{sig,max}`
     - Highest signature seen by the power sourcing equipment
     - kΩ

The sum lands on the 26.3 kΩ limit. The signature resistor dissipates very
little; its highest power is at the top of the detection range:

.. math::

   P_\text{sig} &= \frac{V_\text{det,max}^2}{R_\text{sig}} \\
   &= \frac{(10.1\ \text{V})^2}{24.9\ \text{k}\Omega} \\
   &= 4.1\ \text{mW}

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`V_\text{det,max}`
     - Highest detection voltage at the powered device
     - V
   * - :math:`R_\text{sig}`
     - Signature resistance
     - kΩ
   * - :math:`P_\text{sig}`
     - Power in the signature resistor
     - mW

The input capacitor of the converter behind the powered device is far
larger than 0.12 µF, so it must stay disconnected during detection. The
:term:`isolation switch` does this (:doc:`pd-controller`).

.. _poe-class-signature:

Draw a class signature current during each class event
------------------------------------------------------

During each class event the powered device draws one of five class
signature currents (:clause:`Table 145-24 <145>`), listed in
:numref:`tab-poe-class-sig`. The current must settle within 5 ms of the
start of the event (:clause:`Table 145-25 <145>`, item 8).

.. list-table:: Class signature currents at the powered device
   :name: tab-poe-class-sig
   :header-rows: 1
   :widths: 25 25 25 25

   * - Class signature
     - Lowest (mA)
     - Highest (mA)
     - Example resistor (Ω)
   * - 0
     - 1
     - 4
     - 1210
   * - 1
     - 9
     - 12
     - 249
   * - 2
     - 17
     - 20
     - 140
   * - 3
     - 26
     - 30
     - 90.9
   * - 4
     - 36
     - 44
     - 63.4

The example resistors are those of the TPS2372 [POE-TPS2372]_
(Application and Implementation). :numref:`tab-poe-request` shows which signatures a powered
device shows for each class it requests (:clause:`Table 145-26 <145>`).
The first signature is used in class events 1 and 2, the second from class
event 3 on.

.. list-table:: Class signatures for each requested class
   :name: tab-poe-request
   :header-rows: 1
   :widths: 30 35 35

   * - Requested class
     - Events 1 and 2
     - Events 3 to 5
   * - 1
     - 1
     - 1
   * - 2
     - 2
     - 2
   * - 3
     - 3
     - 3
   * - 4
     - 4
     - 4
   * - 5
     - 4
     - 0
   * - 6
     - 4
     - 1
   * - 7
     - 4
     - 2
   * - 8
     - 4
     - 3

The current flows through the controller, which drops most of the input
voltage. With the highest class voltage and current, and a regulator that
holds 2.5 V across the class resistor (as the TPS2378 does
[POE-TPS2378]_, Detailed Description), the power is:

.. math::

   P_\text{class} &= V_\text{class,max} \times I_\text{class,max} \\
   &= 20.5\ \text{V} \times 44\ \text{mA} = 0.90\ \text{W} \\
   P_\text{reg} &= (V_\text{class,max} - V_\text{CLS}) \times I_\text{class,max} \\
   &= 18\ \text{V} \times 44\ \text{mA} = 0.79\ \text{W}

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`V_\text{class,max}`
     - Top of the class range at the powered device
     - V
   * - :math:`I_\text{class,max}`
     - Top of class signature 4
     - mA
   * - :math:`V_\text{CLS}`
     - Voltage held across the class resistor
     - V
   * - :math:`P_\text{class}`
     - Total power drawn during the event
     - W
   * - :math:`P_\text{reg}`
     - Part dissipated in the regulator
     - W

The rest, 0.11 W, is in the class resistor. The regulator dissipates about
0.8 W for the length of each class event, up to 105 ms for the first.

Recognise mark events and resets
--------------------------------

Between class events the voltage falls into the mark range, 6.9 V to
10.1 V at the powered device. The powered device then draws 0.25 mA to
4 mA and shows an invalid signature (:clause:`Table 145-25 <145>`,
:clause:`145.3.6.1.1`). It enters a class event when its input rises above
a threshold between 10.1 V and 14.5 V, and counts the event when the
voltage falls back to the mark range. For reference, the TPS2378 shows
6 kΩ to 12 kΩ in the mark state [POE-TPS2378]_ (Electrical
Characteristics).

When the input falls below a threshold between 2.81 V and 6.9 V, the
powered device forgets the events it has counted
(:clause:`Table 145-25 <145>`, item 5).

A first class event longer than 75.5 ms to 87.5 ms tells the powered
device that the power sourcing equipment is Type 3 or Type 4
(:clause:`145.3.7`). It may then use the shorter maintain power signature
pulses (:doc:`sequence`).

With the optional *autoclass*, a powered device drops to class signature 0
between 75.5 ms and 87.5 ms into the first class event. It then draws its
highest power from 1.35 s to at least 3.65 s after power-up, so that the
power sourcing equipment can measure it (:clause:`145.3.6.2`,
:clause:`Table 145-28 <145>`).

Turn on with hysteresis
-----------------------

The powered device draws no load current until its input passes a turn-on
voltage between 30 V and 42 V, and turns off again when the input falls
below a turn-off voltage of at least 30 V
(:clause:`Table 145-29 <145>`, items 16 and 17). The standard recommends
a gap between the two, :wikipedia:`hysteresis <Hysteresis>`, so that the
voltage drop caused by switching on the load does not switch it off again
(:clause:`145.3.8.1`). :numref:`tab-poe-turn-on` gives two reference
examples.

.. list-table:: Typical turn-on and turn-off voltages of two controllers
   :name: tab-poe-turn-on
   :header-rows: 1
   :widths: 40 30 30

   * - Controller
     - Turn on (V)
     - Turn off (V)
   * - TPS2372
     - 38.1
     - 32
   * - LT4275
     - 35
     - 31

The values are from [POE-TPS2372]_ and [POE-LT4275]_ (Electrical
Characteristics).

Limit the inrush current
------------------------

After turn-on the powered device charges its input capacitor. It draws less
than 0.4 A for classes 1 to 6, or 0.8 A for classes 7 and 8, until 80 ms
after turn-on (:clause:`Table 145-29 <145>`, items 4 and 7, and
:clause:`145.3.8.3`). A powered device of class 1, 2 or 3 must also be
within its class power 50 ms after turn-on.

Charging the capacitor at a constant current takes:

.. math::

   t_\text{charge} &= \frac{C_\text{bulk} \times V_\text{max}}{I_\text{inrush}} \\
   &= \frac{100\ \text{µF} \times 57\ \text{V}}{140\ \text{mA}} \\
   &= 41\ \text{ms}

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`C_\text{bulk}`
     - Input capacitance of the converter, an example value
     - µF
   * - :math:`V_\text{max}`
     - Highest input voltage
     - V
   * - :math:`I_\text{inrush}`
     - Charging current; 140 mA is the TPS2378 limit [POE-TPS2378]_
     - mA
   * - :math:`t_\text{charge}`
     - Charging time
     - ms

The model assumes the capacitor starts empty, the load stays off until the
capacitor is charged, and the current stays at the limit. It ignores the
time the input takes to rise to the turn-on voltage. A 100 µF capacitor is
then charged before the power sourcing equipment ends its inrush period,
50 ms at the earliest. Only then does the controller let the input converter
start (:doc:`pd-controller`).

Keep drawing the maintain power signature
-----------------------------------------

:doc:`sequence` gives the minimum current and pulse timing. A board that
always draws a steady power meets it if the current stays above the
minimum at the highest input voltage, where the current is smallest:

.. math::

   P_\text{steady} &= V_\text{max} \times I_\text{MPS} \\
   &= 57\ \text{V} \times 10\ \text{mA} = 0.57\ \text{W}

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`I_\text{MPS}`
     - Minimum current: 10 mA for classes 1 to 4, 16 mA for 5 to 8
     - mA
   * - :math:`P_\text{steady}`
     - Lowest steady power that meets the signature
     - W

For classes 5 to 8 the same calculation gives 0.91 W. A board that sleeps
below this power must draw pulses. With the shortest pulse and longest gap
allowed after a long first class event, 7 ms and 310 ms, the average power
at a 54 V supply is:

.. math::

   d &= \frac{t_\text{on}}{t_\text{on} + t_\text{off}}
     = \frac{7\ \text{ms}}{317\ \text{ms}} = 0.022 \\
   P_\text{pulse} &= V \times I_\text{MPS} \times d \\
   &= 54\ \text{V} \times 10\ \text{mA} \times 0.022 \\
   &= 12\ \text{mW}

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`t_\text{on}`, :math:`t_\text{off}`
     - Pulse length and gap
     - ms
   * - :math:`d`
     - :wikipedia:`Duty cycle <Duty_cycle>`
     - none
   * - :math:`V`
     - Supply voltage, a typical value
     - V
   * - :math:`P_\text{pulse}`
     - Average power of the pulses
     - mW

The model assumes rectangular pulses as seen at the power sourcing
equipment. The input capacitor delays the pulse seen at the cable, so a
real design makes the pulses longer than 7 ms.

Ask for more power over LLDP from class 4
-----------------------------------------

A single-signature powered device that requests class 4 or higher must
also support power negotiation over :term:`LLDP` once the link is up
(:clause:`145.3.6`). :doc:`lldp` describes it. A powered device assigned a
lower class than it requested must give the user an active indication if
it is underpowered (:clause:`145.3.6`).

An alternative: accept passive power as a fallback input
--------------------------------------------------------

Some equipment puts a fixed 24 V or 48 V on the cable with no detection or
classification, called
:wikipedia:`passive Power over Ethernet <Power_over_Ethernet#Passive>`. The
standard excludes it because the voltage reaches equipment that was not
designed for it. That reason concerns the end that supplies power. A powered
device that also accepts a passive input harms nothing.

A standard powered device never turns on from 24 V, because its turn-on
voltage is at least 30 V. Accepting 24 V needs a second input path with a
lower turn-on voltage. A passive source gives no class, so the software
cannot know the power available and would start from the lowest assumption.
Whether evampire accepts passive input is an open question.

Open questions
--------------

* Diode, Schottky or MOSFET bridges, which trades loss against leakage and
  complexity.
* Whether the powered-device port supports autoclass.
* Whether the powered-device port accepts a passive 24 V or 48 V input, and
  how the software then sets the power budget.
* How the board gives the active indication when it is underpowered.
