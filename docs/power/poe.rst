Power over Ethernet
===================

This page explains how power is carried over an Ethernet cable, the
exchange of signals that comes before it, and the analog circuits needed at
both ends of the cable. A board built around evampire uses both ends:

* as a *powered device*, it takes power from the cable plugged into an
  Ethernet port;
* as *power sourcing equipment*, it supplies power to a device plugged into
  an Ethernet port.

On the first-version board, Ethernet port A is a powered device and Ethernet
port B is power sourcing equipment. In the full design either Ethernet port
can take either role. Power received on one port can be passed on through
the other port, or through a USB Type-C port (see :doc:`index` and
:doc:`usb-pd`).

The rules come from the IEEE 802.3 Ethernet standard [PoE-IEEE802.3]_. The
numbers on this page are taken from published summaries of the standard,
from a conformance test plan, and from controller data sheets, each cited
where it is used.

Terms used on this page
-----------------------

Power sourcing equipment
   The equipment that puts power onto the cable: an Ethernet switch with
   power outputs, an *injector* (a box placed in the cable between an
   ordinary switch and the powered device), or port B of an evampire board.
   The standard abbreviates it as PSE.

Powered device
   The equipment at the other end of the cable that takes power from it,
   for example port A of an evampire board. The standard abbreviates it as
   PD.

Pair and pair set
   An Ethernet cable has 8 wires twisted into 4 pairs. Both wires of a pair
   always carry the same DC voltage. Two pairs, one positive and one
   negative, form a *pair set* that carries current out and back.

Alternative A, Alternative B, Mode A, Mode B
   The names of the two pair sets. The power sourcing equipment end calls
   them Alternative A and Alternative B; the powered device end calls them
   Mode A and Mode B.

Channel
   One switched and current-limited power output of a power sourcing
   equipment controller. A port that powers one pair set needs one channel;
   a port that powers both pair sets needs two.

Type
   A set of rules that power sourcing equipment or a powered device
   follows. Type 1 comes from IEEE 802.3af, Type 2 from IEEE 802.3at, and
   Types 3 and 4 from IEEE 802.3bt.

Class
   A number from 0 to 8 that stands for a maximum power level. The powered
   device *requests* a class, and the power sourcing equipment *assigns* a
   class, which may be lower.

Signature
   A defined electrical behaviour (a resistance, a current) that the
   powered device shows when the power sourcing equipment applies a test
   voltage. The power sourcing equipment measures the signature to decide
   what is connected.

Maintain power signature
   The minimum current the powered device must keep drawing after power is
   on. If it stops, the power sourcing equipment assumes the cable has been
   unplugged and turns the power off.

Overview
--------

.. _fig-poe-system:

.. graphviz:: poe/system.dot
   :caption: Power over Ethernet on a first-version board. Port A receives
             power from upstream power sourcing equipment; port B supplies
             power to a downstream powered device. Bold arrows carry power,
             thin arrows carry data, dashed arrows carry control.
   :align: center

The power sourcing equipment applies a DC voltage between two pairs of the
cable. Because both wires of each pair are at the same voltage, the DC
voltage appears as a *common-mode* voltage on the pairs and does not
disturb the data signals, which are differential. At both ends the DC
voltage is connected to the centre taps of the cable-side windings of the
Ethernet transformers (the "magnetics"). The transformers pass the data
signals and keep the DC away from the Ethernet transceivers. See
:doc:`../ethernet/magnetics` for how the transformers and their centre taps
are connected.

Which pairs carry power
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Pair sets used for power
   :header-rows: 1
   :widths: 28 22 25 25

   * - Pair set
     - RJ45 pins
     - Cable colours (T568B wiring)
     - Polarity used by power sourcing equipment
   * - Alternative A / Mode A
     - 1 and 2, 3 and 6
     - green and orange
     - either pair may be positive
   * - Alternative B / Mode B
     - 4 and 5, 7 and 8
     - blue and brown
     - 4-5 positive, 7-8 negative (Types 1 and 2)

Sources: [EA-bt]_; Type 1 and 2 polarities from IEEE 802.3-2005 Table 33-1
as reproduced in [UNH-PSE]_. Type 3 power sourcing equipment may use any of
the four polarity combinations of the two pair sets, and Type 4 power
sourcing equipment uses one fixed combination [EA-bt]_.

Type 1 and Type 2 power sourcing equipment uses one pair set at a time.
Type 3 and Type 4 power sourcing equipment may use one pair set or both
for classes 1 to 4, and may switch between the two while powering; when it
assigns class 5 or higher it must use both pair sets ("4-pair power")
[EA-bt]_. In gigabit Ethernet all four pairs carry data, so both pair sets
pass through transformers and power is applied and taken at the centre
taps in both cases.

Voltage range
~~~~~~~~~~~~~

The power sourcing equipment output is between 44 V and 57 V for Type 1,
between 50 V and 57 V for Types 2 and 3, and between 52 V and 57 V for
Type 4 [EA-bt]_. The cable resistance lowers the voltage at the powered
device, which must work down to 37 V (Type 1 rules) or about 42 V (higher
power types); see the tables below.

Types and classes
-----------------

.. list-table:: Device types
   :header-rows: 1
   :widths: 10 18 14 14 14 15 15

   * - Type
     - Standard
     - Pairs powered
     - Power sourcing equipment voltage
     - Lowest voltage at powered device
     - Power sourcing equipment output, maximum
     - Power at powered device, maximum
   * - 1
     - IEEE 802.3af (2003), Clause 33
     - 2
     - 44–57 V
     - 37 V
     - 15.4 W
     - 13 W
   * - 2
     - IEEE 802.3at (2009), Clause 33
     - 2
     - 50–57 V
     - 42.5 V
     - 30 W
     - 25.5 W
   * - 3
     - IEEE 802.3bt (2018), Clause 145
     - 2 or 4 (4 for classes 5 and 6)
     - 50–57 V
     - 42.5 V
     - 60 W
     - 51 W
   * - 4
     - IEEE 802.3bt (2018), Clause 145
     - 2 or 4 (4 for classes 5 to 8)
     - 52–57 V
     - 41.2 V
     - 90 W
     - 71.3 W

Sources: power sourcing equipment voltages and powers from [EA-bt]_; lowest
powered-device voltages from [TPS2372]_, Table 6.

.. list-table:: Classes
   :header-rows: 1
   :widths: 8 14 14 14 18 16 16

   * - Class
     - Power at powered device (average)
     - Peak power at powered device
     - Power sourcing equipment must supply
     - Class signature, events 1 and 2 / events 3 to 5
     - Class events needed to grant it
     - Powered device type
   * - 0
     - 13 W
     - —
     - 15.4 W
     - 0 / —
     - 1
     - 1 only
   * - 1
     - 3.84 W
     - 5.00 W
     - 4.00 W
     - 1 / 1
     - 1
     - 1 or 3
   * - 2
     - 6.49 W
     - 8.36 W
     - 6.70 W
     - 2 / 2
     - 1
     - 1 or 3
   * - 3
     - 13.0 W
     - 14.4 W
     - 14.0 W
     - 3 / 3
     - 1
     - 1 or 3
   * - 4
     - 25.5 W
     - 28.3 W
     - 30.0 W
     - 4 / 4
     - 2 or 3
     - 2 or 3
   * - 5
     - 40.0 W
     - 42.0 W
     - 45.0 W
     - 4 / 0
     - 4
     - 3
   * - 6
     - 51.0 W
     - 53.5 W
     - 60.0 W
     - 4 / 1
     - 4
     - 3
   * - 7
     - 62.0 W
     - 65.1 W
     - 75.0 W
     - 4 / 2
     - 5
     - 4
   * - 8
     - 71.3 W
     - 74.9 W
     - 90.0 W
     - 4 / 3
     - 5
     - 4

Classes 1 to 8, peak powers and power sourcing equipment powers are from
the Clause 145 tables summarised in [EA-bt]_ (Tables 6, 7 and 14). Class 0
exists only in Clause 33 and is treated as class 3 by Type 3 and Type 4
power sourcing equipment. Under the Clause 33 rules (Types 1 and 2, with a
20 Ω cable allowance for Type 1) the power sourcing equipment supplies
4.0 W, 7.0 W and 15.4 W for classes 1, 2 and 3 [EA-bt]_. A powered device
may draw more than its average limit, up to the peak power, for at most
50 ms in any 1 s window [EA-bt]_.

Power lost in the cable
~~~~~~~~~~~~~~~~~~~~~~~

The power sourcing equipment output and the power at the powered device
differ by the power lost in the cable. This calculation shows where the
two power columns of the type and class tables come from, and so how much
power a board must budget on its power sourcing equipment port to deliver
a given power at the far end.

The model treats the cable as a fixed resistance in the current loop (out
on one pair, back on the other) and assumes the power sourcing equipment
supplies its full power at its lowest allowed voltage. The loss in the
cable is then

.. math::

   I = \frac{P_\text{PSE}}{V_\text{PSE}}, \qquad
   P_\text{cable} = I^2 \, R_\text{loop}, \qquad
   P_\text{PD} = P_\text{PSE} - P_\text{cable}

where:

* :math:`P_\text{PSE}` is the power at the power sourcing equipment
  output, in W (type table above);
* :math:`V_\text{PSE}` is the lowest allowed power sourcing equipment
  output voltage, in V (type table above, from [EA-bt]_);
* :math:`I` is the current in the loop, in A;
* :math:`R_\text{loop}` is the worst-case loop resistance of the cable,
  in Ω: 20 Ω for Type 1, 12.5 Ω for one pair set of the higher types, and
  6.25 Ω when both pair sets share the current [TPS2372]_ [EA-bt]_;
* :math:`P_\text{cable}` is the power lost in the cable and
  :math:`P_\text{PD}` the power left at the powered device, both in W.

.. list-table:: Cable loss at full power and minimum voltage
   :header-rows: 1
   :widths: 20 12 12 12 14 14 16

   * - Case
     - :math:`P_\text{PSE}`
     - :math:`V_\text{PSE}`
     - :math:`R_\text{loop}`
     - :math:`I = P_\text{PSE} / V_\text{PSE}`
     - :math:`P_\text{cable} = I^2 R_\text{loop}`
     - :math:`P_\text{PD}`
   * - Type 1
     - 15.4 W
     - 44 V
     - 20 Ω
     - 0.350 A
     - 0.1225 × 20 = 2.45 W
     - 12.95 W
   * - Type 2
     - 30 W
     - 50 V
     - 12.5 Ω
     - 0.600 A
     - 0.36 × 12.5 = 4.50 W
     - 25.50 W
   * - Type 3, both pair sets
     - 60 W
     - 50 V
     - 6.25 Ω
     - 1.200 A
     - 1.44 × 6.25 = 9.00 W
     - 51.00 W
   * - Type 4, both pair sets
     - 90 W
     - 52 V
     - 6.25 Ω
     - 1.731 A
     - 2.996 × 6.25 = 18.72 W
     - 71.28 W

Each result matches the powered-device power in the type table (13 W,
25.5 W, 51 W and 71.3 W after rounding), so the class powers already
include the worst-case cable. A shorter or thicker cable loses less; the
model does not hold when the two pair sets carry unequal currents, which
the standard handles with separate per-pair-set limits [EA-bt]_.

The lowest voltage the powered device must work at follows from the same
model: it is the voltage left after the cable drop when the powered device
draws its full power from power sourcing equipment at its lowest voltage.
This sets the powered device's turn-off threshold and the input range of
its converter. The powered device draws :math:`P_\text{PD} = V_\text{PD}
\, I` and the cable drops :math:`V_\text{PSE} - V_\text{PD} = I \,
R_\text{loop}`. Eliminating :math:`I` gives a quadratic in
:math:`V_\text{PD}`, whose higher root is the operating point:

.. math::

   D = V_\text{PSE}^2 - 4 \, R_\text{loop} \, P_\text{PD}, \qquad
   V_\text{PD} = \frac{V_\text{PSE} + \sqrt{D}}{2}

where :math:`V_\text{PD}` is the voltage at the powered device input in V,
:math:`D` is an intermediate quantity in V², and the other symbols are as
above with :math:`P_\text{PD}` the maximum power at the powered device
from the type table.

.. list-table:: Lowest voltage at the powered device
   :header-rows: 1
   :widths: 22 12 12 12 16 10 16

   * - Case
     - :math:`V_\text{PSE}`
     - :math:`R_\text{loop}`
     - :math:`P_\text{PD}`
     - :math:`D`
     - :math:`\sqrt{D}`
     - :math:`V_\text{PD}`
   * - Type 1
     - 44 V
     - 20 Ω
     - 13 W
     - 1936 − 1040 = 896
     - 29.93
     - 36.97 V
   * - Type 2
     - 50 V
     - 12.5 Ω
     - 25.5 W
     - 2500 − 1275 = 1225
     - 35.00
     - 42.50 V
   * - Type 3, both pair sets
     - 50 V
     - 6.25 Ω
     - 51 W
     - 2500 − 1275 = 1225
     - 35.00
     - 42.50 V
   * - Type 4, both pair sets
     - 52 V
     - 6.25 Ω
     - 71.3 W
     - 2704 − 1782.5 = 921.5
     - 30.36
     - 41.18 V

So a Type 1 powered device must work down to 37 V, and higher-power
powered devices down to about 42 V, which agrees with [TPS2372]_ Table 6
(37 V, 42.5 V and 41.2 V). The Ethernet Alliance summary of Clause 145
lists 43.0 V for class 8 on Type 4 power sourcing equipment [EA-bt]_; this
difference from the simple model has not been resolved here, and a design
should take the value from the standard itself.

The power-up sequence
---------------------

When a powered device is plugged in, the power sourcing equipment runs
through a fixed sequence before it applies full voltage. Each step uses a
different voltage range, so the powered device can tell the steps apart
only by measuring its own input voltage. This section gives the sequence;
the two sections after it describe what each end must do.

.. _fig-poe-voltage-timeline:

.. figure:: poe/voltage-timeline.svg
   :alt: Voltage at the powered device input against time, showing two
         detection steps, four class events separated by mark events, and
         the rise to full voltage.
   :align: center
   :width: 100%

   Voltage at the powered device input while Type 3 power sourcing
   equipment detects a powered device, runs four class events (granting
   class 6) and turns the power on. Shaded bands are the voltage windows
   the powered device must recognise. Time is not to scale.

.. list-table:: Start-up timeline
   :header-rows: 1
   :widths: 16 30 18 36

   * - Step
     - Power sourcing equipment applies
     - Powered device sees
     - Powered device must
   * - Detection
     - At least two test points between 2.8 V and 10 V, at least 1 V apart
       and at least 2 ms apart; whole detection within 500 ms. Never more
       than 30 V or 5 mA.
     - 2.7–10.1 V
     - Present a 23.7–26.3 kΩ incremental resistance, 50–120 nF.
   * - Class event 1
     - 15.5–20.5 V. Lasts 6–75 ms (Type 1), 6–30 ms (Type 2) or
       88–105 ms (Types 3 and 4).
     - 14.5–20.5 V
     - Draw its class signature current within 5 ms.
   * - Mark event
     - 7–10 V
     - 6.9–10.1 V
     - Draw 0.25–4 mA and present an invalid (below 12 kΩ) signature.
   * - Class events 2 to 5
     - 15.5–20.5 V, at most 20 ms each (Types 3 and 4).
     - 14.5–20.5 V
     - Draw the signature for that event; count the events.
   * - Power on
     - Within 400 ms of detection, rises to the operating voltage.
       Limits its current for 50–75 ms.
     - Turns on between 30 and 42 V
     - Charge its input capacitor slowly; stay below 13 W until 80 ms
       after turn-on.
   * - Operation
     - Watches the current; removes power on overload or when the
       current disappears.
     - Above 30 V
     - Keep drawing the maintain power signature current.

Values from [EA-bt]_, [Sifos-PD]_, [UNH-PSE]_ and [TPS2372]_.

.. _fig-poe-states:

.. wavedrom::
   :caption: What each end does during a two-event classification. The top
             three rows are the power sourcing equipment (port voltage,
             what it measures, its current limit); the rows below the gap
             are the powered device (signature resistor, class current,
             mark-event load, class events counted, isolation switch,
             power good).
   :alt: Timing diagram. The power sourcing equipment port goes from 0 V
         to detection, class event 1, a mark event, class event 2, a mark
         event, inrush and full voltage, measuring resistance during
         detection, class current during class events and current while
         powered. The powered device connects its signature resistor during
         detection and mark events, draws class current during class
         events, counts two class events, turns on its isolation switch
         with a current limit and then fully, and finally asserts power
         good.

   { "signal": [
         { "name": "Port", "wave": "2.3.4.54.56.7.",
           "data": ["0 V", "detect", "class 1", "mark", "class 2", "mark",
                    "inrush", "44–57 V"] },
         { "name": "Measures", "wave": "x.3.4.x4.xx.5.",
           "data": ["resistance", "current", "current", "current"] },
         { "name": "Limit", "wave": "0.........3.4.",
           "data": ["inrush", "operating"] },
         {},
         { "name": "Signature", "wave": "1...0.10.10..." },
         { "name": "Class load", "wave": "0...1.01.0...." },
         { "name": "Mark load", "wave": "0.....10.10..." },
         { "name": "Count", "wave": "2.....3..4....",
           "data": ["0", "1", "2"] },
         { "name": "Switch", "wave": "0.........3.1.",
           "data": ["limited"] },
         { "name": "Power good", "wave": "0...........1." }
     ]
   }

Powered device side
-------------------

This section describes what a powered device (port A on the first-version
board) must do in each step.

Polarity bridges
~~~~~~~~~~~~~~~~

The powered device cannot know in advance which pair set will carry
power, or which pair of a set will be positive, so the standard requires
every powered device to accept any polarity on either pair set
[EA-bt]_. The usual solution is two full-wave bridge rectifiers, one per
pair set, whose outputs are connected together.

The bridges are either ordinary diodes or MOSFETs used as switches. A
diode bridge loses two diode drops, which matters at high power. Schottky
diodes reduce the loss by about 30 % but leak more current, which makes it
harder to meet the limit on the voltage a powered device may feed back
onto the unused pair set (at most 2.8 V across a 100 kΩ test resistor)
[TPS2372]_ [EA-bt]_. The bridge also adds series resistance during
detection; the Analog Devices LT4275 data sheet allows up to 1.1 kΩ for it
[LT4275]_. MOSFET bridges such as the Microchip PD70224 replace the diodes
with low-resistance transistors [PD70224]_; they must stay off during
detection and classification, because a conducting transistor lets
current flow in both directions and spoils the signature [EA-bt]_.

Detection signature
~~~~~~~~~~~~~~~~~~~

A powered device shows a valid signature when, over the whole 2.7–10.1 V
range at its input:

* the incremental resistance is between 23.7 kΩ and 26.3 kΩ,
* the voltage offset is at most 1.9 V,
* the input capacitance is between 50 nF and 120 nF, and
* the series inductance is below 100 µH [EA-bt]_.

To make sure it is *not* detected (for example during a mark event, or
when it wants to refuse power), a powered device shows below 12 kΩ or above
45 kΩ [EA-bt]_.

The signature is normally a resistor of about 25 kΩ across the bridge
output. The valid window of 23.7–26.3 kΩ is roughly 25 kΩ ± 5 %, which
sets the total error budget for the resistor, the bridge and the
controller's own leakage:

.. math::

   R_\text{nom} \times (1 - 0.05) = 25 \,\text{k}\Omega \times 0.95
     = 23.75 \,\text{k}\Omega, \qquad
   R_\text{nom} \times (1 + 0.05) = 25 \,\text{k}\Omega \times 1.05
     = 26.25 \,\text{k}\Omega

where :math:`R_\text{nom} = 25\,\text{k}\Omega` is the nominal signature
resistance. The standard's window (23.7–26.3 kΩ [EA-bt]_) is these values
rounded outwards.

The bridge adds series resistance and the controller adds leakage, so
controller makers choose a value slightly below 25 kΩ. Texas Instruments
recommends an external 24.9 kΩ ±1 % resistor [TPS2378]_, which stays
between 24.65 kΩ and 25.15 kΩ. Analog Devices builds a
temperature-compensated 24.4 kΩ resistor into the LT4275 and allows up to
1.1 kΩ for the bridge [LT4275]_. The worst case seen by the power sourcing
equipment is then

.. math::

   R_\text{det,max} = R_\text{int,max} + R_\text{bridge,max}
     = 25.2 \,\text{k}\Omega + 1.1 \,\text{k}\Omega = 26.3 \,\text{k}\Omega

where :math:`R_\text{int,max} = 25.2\,\text{k}\Omega` is the LT4275's
highest internal signature resistance over temperature and
:math:`R_\text{bridge,max} = 1.1\,\text{k}\Omega` the largest bridge
resistance it allows for (both from [LT4275]_). The sum lands exactly on
the 26.3 kΩ limit, so the LT4275 meets the window with any bridge within
that allowance.

The resistor sees very little power, so a small part is enough. The
highest power is at the top of the detection range:

.. math::

   P_\text{det} = \frac{V_\text{det,max}^2}{R_\text{det}}
     = \frac{(10.1 \,\text{V})^2}{24.9 \,\text{k}\Omega}
     = \frac{102.01 \,\text{V}^2}{24\,900 \,\Omega}
     = 4.1 \,\text{mW}

where :math:`V_\text{det,max} = 10.1\,\text{V}` is the highest voltage the
powered device sees during detection [EA-bt]_ and :math:`R_\text{det} =
24.9\,\text{k}\Omega` the TI recommended resistor [TPS2378]_. TI quotes
about 5 mW for this resistor [TPS2378]_.

The capacitance requirement is usually met with a 0.1 µF, 100 V ceramic
capacitor across the controller input [TPS2372]_. The large capacitor that
feeds the DC-DC converter must not be visible during detection, which is
one reason for the isolation switch described below.

Class signature
~~~~~~~~~~~~~~~

During each class event the powered device draws one of five *class
signature* currents:

.. list-table:: Class signature currents (powered device)
   :header-rows: 1
   :widths: 20 25 25 30

   * - Class signature
     - Current drawn
     - Example resistor (TPS2372, 2.5 V)
     - Typical current with that resistor
   * - 0
     - 1–4 mA
     - 1210 Ω
     - 2.5 mA
   * - 1
     - 9–12 mA
     - 249 Ω
     - 10.6 mA
   * - 2
     - 17–20 mA
     - 140 Ω
     - 18.6 mA
   * - 3
     - 26–30 mA
     - 90.9 Ω
     - 27.9 mA
   * - 4
     - 36–44 mA
     - 63.4 Ω
     - 39.9 mA

Current ranges from [Sifos-PD]_ and [EA-bt]_ (IEEE 802.3bt Table 145-24);
resistor values and typical currents from [TPS2372]_.

The powered device recognises 14.5–20.5 V at its input as the class range,
which allows for the bridge drop and the cable. The current must reach its
final value within 5 ms of the input passing 15.5 V [Sifos-PD]_ [EA-bt]_.

Mark events
   Between class events the voltage drops into 6.9–10.1 V at the powered
   device. This overlaps the detection range, so the powered device must
   *not* look like a valid 25 kΩ signature here; it draws 0.25–4 mA and
   presents less than 12 kΩ [EA-bt]_. The TI TPS2378 presents 6–12 kΩ
   [TPS2378]_ and the LT4275 less than 11 kΩ [LT4275]_. The powered device
   counts a class event when the voltage falls from the class range into
   the mark range [EA-bt]_. Between the two ranges (10.1 V to 14.5 V) it
   may draw either current.

Changing the signature from event 3
   Powered devices that request class 5 to 8 show class signature 4 in
   the first two events (so that older power sourcing equipment sees a
   class 4 device) and switch to signature 0, 1, 2 or 3 from the third
   event on [EA-bt]_. Controllers do this with two class resistors, one
   for events 1 and 2 and one for later events (pins CLSA and CLSB on the
   TPS2372) [TPS2372]_.

Long first class event
   Type 3 and Type 4 power sourcing equipment makes the first class event
   88–105 ms long; Type 1 and Type 2 make it 6–75 ms and 6–30 ms. A powered
   device that measures the first event can tell the newer types from the
   older ones, which decides which maintain power signature timing it may
   use [EA-bt]_.

Reset
   When the voltage stays below 2.8 V for at least 15 ms, the powered
   device forgets the events it has counted [EA-bt]_. Controllers do this
   with a *mark reset* comparator: 3–5 V on the TPS2372 [TPS2372]_,
   2.6–5.6 V on the LT4275 [LT4275]_.

Autoclass
   An optional Type 3 and Type 4 feature: the powered device drops to class
   signature 0 about 81 ms into the first class event, and then draws its
   highest power during the first seconds after power-up so that the power
   sourcing equipment can measure it and reserve only what is really
   needed [EA-bt]_ [TPS2372]_.

The classification current flows through the controller's regulator,
which drops most of the input voltage. This decides the controller's
thermal design and is one reason class events are kept short. In the
worst case (highest class voltage, highest class signature current, TI
regulator voltage):

.. math::

   P_\text{class} = V_\text{class,max} \, I_\text{class,max}
     = 20.5 \,\text{V} \times 0.044 \,\text{A} = 0.902 \,\text{W}

.. math::

   P_\text{reg} = (V_\text{class,max} - V_\text{CLS}) \, I_\text{class,max}
     = (20.5 \,\text{V} - 2.5 \,\text{V}) \times 0.044 \,\text{A}
     = 0.792 \,\text{W}

where :math:`V_\text{class,max} = 20.5\,\text{V}` is the top of the
powered device's class range and :math:`I_\text{class,max} = 44\,\text{mA}`
the top of class signature 4 (both [EA-bt]_), :math:`V_\text{CLS} =
2.5\,\text{V}` is the voltage the TI regulator holds across the class
resistor [TPS2378]_, :math:`P_\text{class}` is the total power drawn and
:math:`P_\text{reg}` the part dissipated in the controller (the rest,
0.11 W, is in the class resistor). So the controller must absorb about
0.8 W for the length of each class event. The LT4275 data sheet quotes up
to 1.5 W during classification and relies on thermal protection if the
condition lasts abnormally long [LT4275]_; the reason for its higher
figure is not given there.

Turn-on and inrush
~~~~~~~~~~~~~~~~~~

The powered device must stay off (draw no load current) until its input
passes a *turn-on* voltage, which may be anywhere from 30 V to 42 V, and
must turn off again when its input falls below 30 V [Sifos-PD]_
[EA-bt]_. A gap between turn-on and turn-off (hysteresis) keeps the
voltage drop caused by switching on the load from switching it off again.

.. list-table:: Turn-on and turn-off thresholds of example powered-device controllers
   :header-rows: 1
   :widths: 30 35 35

   * - Controller
     - Turn on (rising)
     - Turn off (falling)
   * - Standard limit
     - between 30 V and 42 V
     - not below 30 V
   * - TI TPS2372 and TPS2378
     - 36.3 V to 40 V (38.1 V typical)
     - 30.5 V to 33.6 V (32 V typical)
   * - Analog Devices LT4275
     - 35 V typical, 37 V maximum
     - 30 V minimum, 31 V typical

Sources: [TPS2372]_, [TPS2378]_, [LT4275]_.

The powered device's DC-DC converter has a large input capacitor. Between
50 ms and 80 ms after its turn-on the powered device must draw less than
the inrush current limit and no more than 13 W [EA-bt]_. Powered-device
controllers therefore limit their own current with their isolation switch:
140 mA on the TPS2378, 200 mA or 335 mA on the TPS2372-3 and -4
[TPS2378]_ [TPS2372]_, and about 100 mA set by an external capacitor on
the LT4275 [LT4275]_.

The bulk capacitor and the inrush limit together set how long the
powered device takes to start, which must fit the start-up timing above.
Charging a capacitor with a constant current takes

.. math::

   Q = C_\text{bulk} \, V_\text{max} = 100 \,\mu\text{F} \times 57 \,\text{V}
     = 5.7 \,\text{mC}, \qquad
   t_\text{charge} = \frac{Q}{I_\text{inrush}}
     = \frac{5.7 \,\text{mC}}{0.140 \,\text{A}} = 40.7 \,\text{ms}

where :math:`C_\text{bulk} = 100\,\mu\text{F}` is an example bulk
capacitance (the real value depends on the DC-DC converter),
:math:`V_\text{max} = 57\,\text{V}` the highest input voltage [EA-bt]_,
:math:`Q` the charge needed, :math:`I_\text{inrush} = 140\,\text{mA}` the
TPS2378 inrush limit [TPS2378]_, and :math:`t_\text{charge}` the charging
time. The model assumes the capacitor starts empty, the load is held off
(which the power-good signal ensures), and the current stays at the limit
throughout; it ignores the time the input spends rising to the turn-on
threshold. A 100 µF capacitor is therefore charged in about 41 ms, inside
the 50 ms during which the power sourcing equipment is still limiting its
own current.

Only when the capacitor is charged does the controller signal *power good*
and let the DC-DC converter start. The TPS2372 also waits at least
78–87 ms after the start of inrush before doing so [TPS2372]_.

Maintain power signature
~~~~~~~~~~~~~~~~~~~~~~~~

Once powered, the powered device must keep drawing a minimum current,
continuously or in pulses:

.. list-table:: Maintain power signature (powered device side)
   :header-rows: 1
   :widths: 18 16 16 16 16 18

   * - Powered device type
     - Assigned class
     - Power sourcing equipment type
     - Minimum current
     - Minimum on time
     - Maximum off time
   * - 1, 2
     - all
     - all
     - 10 mA
     - 75 ms
     - 250 ms
   * - 3, 4
     - 1 to 4
     - 1, 2
     - 10 mA
     - 75 ms
     - 250 ms
   * - 3, 4
     - 1 to 4
     - 3, 4
     - 10 mA
     - 7 ms
     - 310 ms
   * - 3, 4
     - 5 to 8
     - 3, 4
     - 16 mA
     - 7 ms
     - 310 ms

Source: [EA-bt]_, Table 19. Type 1 and Type 2 power sourcing equipment may
also check an AC impedance; for those the powered device must also present
less than 26.3 kΩ in parallel with 0.05 µF, which the bulk capacitor
normally does [TPS2378]_.

The following calculations tell whether the board needs any circuit for
this. A board that draws a constant power meets the requirement if its
current stays above the minimum even at the highest input voltage, where
the current for a given power is smallest:

.. math::

   P_\text{cont} = V_\text{max} \, I_\text{MPS}: \qquad
   57 \,\text{V} \times 10 \,\text{mA} = 0.57 \,\text{W}, \qquad
   57 \,\text{V} \times 16 \,\text{mA} = 0.91 \,\text{W}

where :math:`V_\text{max} = 57\,\text{V}` is the highest input voltage
and :math:`I_\text{MPS}` the minimum current from the table (10 mA for
classes 1–4, 16 mA for classes 5–8) [EA-bt]_. So a board that always
draws more than about 0.6 W (classes 1–4) or about 1 W (classes 5–8)
needs nothing special; [EA-bt]_ gives the same rounded figures.

A board with a deep sleep mode below that level must draw pulses. The
average power of the shortest allowed pulse pattern (Type 3/4 timing) is

.. math::

   d = \frac{t_\text{on}}{t_\text{on} + t_\text{off}}
     = \frac{7 \,\text{ms}}{7 \,\text{ms} + 310 \,\text{ms}} = 0.0221

.. math::

   P_\text{MPS} = V \, I_\text{MPS} \, d
     = 54 \,\text{V} \times 10 \,\text{mA} \times 0.0221 = 11.9 \,\text{mW}

where :math:`t_\text{on} = 7\,\text{ms}` and :math:`t_\text{off} =
310\,\text{ms}` are the minimum on time and maximum off time from the
table [EA-bt]_, :math:`d` is the resulting duty cycle, :math:`V =
54\,\text{V}` a typical operating voltage, and :math:`I_\text{MPS} =
10\,\text{mA}` (classes 1–4). The keep-alive pulses therefore cost about
12 mW, as [EA-bt]_ also states. The model assumes an ideal rectangular
pulse seen at the power sourcing equipment.

The power sourcing equipment only sees the pulse after the bulk capacitor
stops supplying it, so in practice the pulses are made longer than 7 ms.
The TPS2372 generates them automatically when its output current falls
below about 28 mA [TPS2372]_.

Power sourcing equipment side
-----------------------------

This section describes what power sourcing equipment (port B on the
first-version board) must do in each step. The rule that governs all of
it: power sourcing equipment must never apply power to a pair set that has
not shown a valid detection signature [EA-bt]_.

Detection
~~~~~~~~~

The power sourcing equipment applies small test voltages, or forces small
test currents, and measures the response. It takes at least two points
between 2.8 V and 10 V, at least 1 V apart. Seen from the cable, the
powered device behaves like a voltage offset (the bridge diodes) in series
with the signature resistance, so each point obeys :math:`V = V_\text{off}
+ I \, R_\text{det}`. Taking the difference of two points removes the
unknown offset and gives the *incremental* resistance that the decision
table below is applied to:

.. math::

   R_\text{det} = \frac{V_2 - V_1}{I_2 - I_1}

where :math:`(V_1, I_1)` and :math:`(V_2, I_2)` are the two measured
voltage and current points, :math:`V_\text{off}` is the powered device's
offset voltage (at most 1.9 V allowed at the powered device, at least 2 V
tolerated by the power sourcing equipment [EA-bt]_), and
:math:`R_\text{det}` the result in Ω. The model assumes the powered
device is linear between the two points; a capacitive or non-linear load
breaks it, which is why controllers wait for the voltage to settle and
some take more than two points. During detection the power
sourcing equipment may never produce more than 30 V or source more than
5 mA [EA-bt]_. Under the Clause 33 rules the test points must be at least
2 ms apart and the whole detection must take at most 500 ms [UNH-PSE]_.
Type 3 and Type 4 power sourcing equipment detects each pair set
separately before powering it [EA-bt]_.

.. list-table:: Detection decision (power sourcing equipment)
   :header-rows: 1
   :widths: 40 60

   * - Measured resistance
     - Decision
   * - 19 kΩ to 26.5 kΩ
     - must accept
   * - below 15 kΩ or above 33 kΩ
     - must reject
   * - 15–19 kΩ or 26.5–33 kΩ
     - may accept or reject

Source: [EA-bt]_, [UNH-PSE]_. The gaps give margin for measurement error.
The power sourcing equipment must also accept a voltage offset of up to
2 V and a current offset of up to 12 µA [EA-bt]_.

The TI TPS23881 is an example of the current-forcing method. It forces
160 µA, waits about 60 ms and measures the port voltage, then forces
270 µA, waits and measures again, and repeats the pair to get four points;
comparing all four rejects signatures that are not linear [TPS23881]_.
The following check shows that these two currents put the test points
inside the 2.8–10 V window for every signature the power sourcing
equipment must accept, which is what makes the method valid. For a
25 kΩ signature with the largest allowed offset:

.. math::

   V_1 = V_\text{off} + I_1 R_\text{det}
       = 1.9 \,\text{V} + 160 \,\mu\text{A} \times 25 \,\text{k}\Omega
       = 1.9 \,\text{V} + 4.0 \,\text{V} = 5.9 \,\text{V}

.. math::

   V_2 = V_\text{off} + I_2 R_\text{det}
       = 1.9 \,\text{V} + 270 \,\mu\text{A} \times 25 \,\text{k}\Omega
       = 1.9 \,\text{V} + 6.75 \,\text{V} = 8.65 \,\text{V}

.. math::

   R_\text{det} = \frac{V_2 - V_1}{I_2 - I_1}
     = \frac{8.65 \,\text{V} - 5.9 \,\text{V}}{270 \,\mu\text{A} - 160 \,\mu\text{A}}
     = \frac{2.75 \,\text{V}}{110 \,\mu\text{A}} = 25 \,\text{k}\Omega

where :math:`I_1 = 160\,\mu\text{A}` and :math:`I_2 = 270\,\mu\text{A}`
are the TPS23881 typical detection currents [TPS23881]_ and
:math:`V_\text{off} = 1.9\,\text{V}` the largest offset a powered device
may have [EA-bt]_. The offset cancels and the original 25 kΩ is
recovered. The two points are 2.75 V apart (more than the 1 V minimum).
At the edges of the accept range the points stay inside the window: the
highest point, for 26.5 kΩ with 1.9 V offset, is 1.9 V + 270 µA × 26.5 kΩ
= 9.06 V, below 10 V; the lowest, for 19 kΩ with no offset, is
160 µA × 19 kΩ = 3.04 V, above 2.8 V. The
TPS23881 accepts 19–26.5 kΩ, rejects 0.86–15 kΩ and 33–100 kΩ, reports a
short below 360 Ω and an open circuit above 400 kΩ, limits its open-circuit
detection voltage to 23.5–29 V, and takes 275–425 ms per detection
[TPS23881]_. It can also measure the port capacitance, for older powered
devices that show a large capacitor instead of a resistor.

If detection fails, the power sourcing equipment waits and tries again.
The TPS23881 pauses 300–500 ms between attempts [TPS23881]_. Under the
Clause 33 rules, power sourcing equipment that uses Alternative B must
wait at least 2 s after a failed detection, keeping the port below 2.8 V
[UNH-PSE]_.

Classification
~~~~~~~~~~~~~~

After a valid detection the power sourcing equipment raises the port to
15.5–20.5 V, limits the current (to at most 100 mA under the Clause 33
rules [UNH-PSE]_), and measures the class current. It decides the class
signature from fixed current bands:

.. list-table:: Class decision (power sourcing equipment)
   :header-rows: 1
   :widths: 35 65

   * - Measured class current
     - Decision
   * - 0–5 mA
     - class signature 0
   * - 8–13 mA
     - class signature 1
   * - 16–21 mA
     - class signature 2
   * - 25–31 mA
     - class signature 3
   * - 35–45 mA
     - class signature 4
   * - in a gap (5–8, 13–16, 21–25, 31–35, 45–51 mA)
     - either neighbouring signature, or class 0

Source: IEEE 802.3-2005 Table 33-4 as reproduced in [UNH-PSE]_. The TPS23881
places its thresholds inside these gaps (5–8, 13–16, 21–25, 31–35 and
45–51 mA) [TPS23881]_. The bands are wider than the powered device's
(for example 35–45 mA against 36–44 mA) to allow for measurement error.

For multi-event classification the power sourcing equipment drops the
port to the mark range (7–10 V) between class events and after the last
one. It chooses how many events to issue from two things:

* the class the powered device requests, learned from the signatures of
  the first events (signature 4 in events 1 and 2 followed by signature 0,
  1, 2 or 3 in event 3 means class 5, 6, 7 or 8), and
* the power it can afford to allocate to this port.

It issues no more events than are needed for the requested class, and
fewer if its power budget is short. The number of events sets the
assigned class [EA-bt]_:

.. list-table:: Number of class events and the power they grant
   :header-rows: 1
   :widths: 30 35 35

   * - Class events issued
     - Highest class assigned
     - Power sourcing equipment must supply
   * - 1
     - 3
     - 15.4 W
   * - 2 or 3
     - 4
     - 30 W
   * - 4
     - 6 (5 if 5 was requested)
     - 60 W (45 W)
   * - 5
     - 8 (7 if 7 was requested)
     - 90 W (75 W)

Sources: [EA-bt]_ Table 7; the TPS23881 data sheet states the same mapping
(1 event 15.4 W, 3 events 30 W, 4 events 60 W, 5 events 90 W) [TPS23881]_.
A Type 2 power sourcing equipment issues at most 2 events, Type 3 at most
4 and Type 4 at most 5. Power sourcing equipment may also *probe* the
requested class with up to three short events and then reset the powered
device by holding the port below 2.8 V for at least 15 ms, before
starting the real sequence [EA-bt]_.

The TPS23881 runs classification through the external power MOSFET in a
linear control loop that holds the port at 18.5 V, so the heat of the
class current is dissipated in the MOSFET rather than in the controller.
It limits the class current to 65–90 mA, makes the first event 95–105 ms
long and later events 6.5–12 ms, and makes mark events 6–12 ms long
[TPS23881]_.

Power on
~~~~~~~~

Under the Clause 33 rules the power sourcing equipment applies the
operating voltage within 400 ms of a valid detection (otherwise it must
detect again), with a rise time of at least 15 µs [UNH-PSE]_. For the
first 50–75 ms it limits the current so that the powered device's
capacitor charges gently:

.. list-table:: Inrush current limit (power sourcing equipment)
   :header-rows: 1
   :widths: 40 30 30

   * - Assigned class
     - Total current limit
     - Limit per pair set
   * - 1 to 4
     - 400–450 mA
     - 450 mA
   * - 5 and 6
     - 400–900 mA
     - 600 mA
   * - 7 and 8
     - 800–900 mA (needs both pair sets)
     - 600 mA

Sources: [EA-bt]_, [TPS2372]_. The full inrush current is required only
when the port voltage is above 30 V; between 10 V and 30 V at least 60 mA
must be available (Clause 33) [UNH-PSE]_ [EA-bt]_. This lets the power
MOSFET carry less current, and so dissipate less power, while most of the
supply voltage is across it.

Power sourcing equipment controllers measure the port current as the
voltage across a small sense resistor in series with the power MOSFET,
and specify their limits as sense voltages. Converting them to currents
shows that the limits match the standard's values, and gives the
currents used in the rest of this section:

.. math::

   I_\text{port} = \frac{V_\text{sense}}{R_\text{sense}}, \qquad
   \text{for example} \quad
   \frac{80 \,\text{mV}}{0.2 \,\Omega} = 400 \,\text{mA}

where :math:`V_\text{sense}` is the voltage across the sense resistor
specified in the data sheet and :math:`R_\text{sense} = 0.2\,\Omega` the
TPS23881 sense resistor [TPS23881]_. The conversion assumes the
resistor's own tolerance (1 % recommended [TPS23881]_) is small compared
with the threshold tolerance.

.. list-table:: TPS23881 thresholds as currents (0.2 Ω sense resistor)
   :header-rows: 1
   :widths: 46 27 27

   * - Threshold
     - Sense voltage
     - Port current
   * - Inrush limit, port above 30 V
     - 80–90 mV
     - 400–450 mA
   * - Inrush limit, port at 1–10 V
     - 19–41 mV
     - 95–205 mA
   * - Operating limit, high-power setting, low MOSFET voltage
     - 245–262 mV
     - 1.23–1.31 A
   * - Operating limit with 50 V across the MOSFET (foldback)
     - 23–37 mV
     - 115–185 mA
   * - Short-circuit trip
     - 205–245 mV
     - 1.03–1.23 A
   * - Disconnect threshold, default
     - 0.8–1.8 mV (1.3 mV typical)
     - 4–9 mA (6.5 mA typical)
   * - Disconnect threshold, low setting
     - 0.4–1.4 mV (0.9 mV typical)
     - 2–7 mA (4.5 mA typical)

Source of the sense voltages: [TPS23881]_, Electrical Characteristics.

The TPS23881 inrush limit of 400–450 mA above 30 V is exactly the
standard's range, and it holds the limit for 50–70 ms by default
[TPS23881]_. It reports *power good* when the voltage across the power
MOSFET (its drain voltage) has fallen below 1–3 V, meaning the switch is
fully on, and flags a shorted MOSFET if the drain voltage is 4–8 V when
the switch should be off [TPS23881]_.

Operation and overload protection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While the port is powered, the power sourcing equipment polices the
current against several limits:

Average power
   The powered device may exceed its class power only up to the peak
   power, for at most 50 ms in any 1 s window. Power sourcing equipment
   removes power when an overload lasts longer than 50–75 ms (the
   overload time limit) [EA-bt]_ [UNH-PSE]_.

Current limit
   Above the overload level, the power sourcing equipment actively limits
   the current. It must hold the limit for at least 10 ms (Type 3) or 6 ms
   (Type 4) so that the powered device can ride through a supply step, and
   must remove power after 75 ms in current limit [EA-bt]_. For Type 2
   and higher the current may peak at up to 50 A for 10 µs or 1.75 A for
   75 ms [TPS2378]_. A Type 4 power sourcing equipment may source up to
   1.3 A per pair set for up to 4 s, but not more than 99.9 W for longer
   than 4 s, so that it stays within the safety definition of a limited
   power source [EA-bt]_.

Foldback
   The current limit is lowered when the voltage across the power MOSFET
   is high, to keep the MOSFET's dissipation within its safe operating
   area. On the TPS23881 the normal limit (250 mV across 0.2 Ω, about
   1.25 A, in the high-power setting) folds back to 23–37 mV (115–185 mA)
   when 50 V is across the MOSFET [TPS23881]_.

Short circuit
   A fast comparator turns the MOSFET off without waiting for software.
   On the TPS23881 it trips at 205–245 mV across the sense resistor
   (about 1.0–1.2 A) and pulls the gate down within 0.9 µs [TPS23881]_.

Retry
   After an overload or short circuit the TPS23881 waits 0.8–1.2 s before
   trying again, keeping the port current duty cycle at or below 6.7 %
   [TPS23881]_.

Transients
   Power sourcing equipment must keep power on through supply transients
   shorter than 30 µs; between 30 µs and 250 µs it must keep the port
   above 45.3 V (Type 3) or 48.4 V (Type 4) [EA-bt]_.

The supply must also be quiet. Under the Clause 33 rules the ripple and
noise at the port must be below 0.5 V peak-to-peak below 500 Hz, 0.2 V
from 500 Hz to 150 kHz, 0.15 V from 150 kHz to 500 kHz, and 0.1 V from
500 kHz to 1 MHz [UNH-PSE]_.

Disconnect detection
~~~~~~~~~~~~~~~~~~~~

The power sourcing equipment watches for the maintain power signature and
removes power when it disappears:

* Clause 33 (Types 1 and 2): power must be removed when the current stays
  below 5 mA for longer than 300–400 ms; power must be kept while the
  current exceeds 10 mA for at least 60 ms in every 300–400 ms
  [UNH-PSE]_ [TPS23881]_. Once the decision is taken, the port must be
  below 2.8 V within 500 ms [UNH-PSE]_.
* Clause 145 (Types 3 and 4): a pulse counts if it lasts at least 6 ms;
  power must be removed when the current stays below 2 mA for more than
  400 ms, and may be removed when the signature has been missing for more
  than 300 ms [EA-bt]_.

The TPS23881 measures the voltage across its sense resistor for this: a
threshold of 0.8–1.8 mV (about 6.5 mA typical) or 0.4–1.4 mV (about
4.5 mA typical) across 0.2 Ω, a programmable drop-out time (320–400 ms by
default), and a minimum pulse length of 3 ms [TPS23881]_. Type 1 and Type
2 power sourcing equipment may instead watch an AC signal injected onto
the port; Type 3 and Type 4 power sourcing equipment uses only the DC
method [TPS2372]_.

Two pair sets: channels, 4-pair power and the alternatives
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A port that can supply power on both pair sets has two channels, each with
its own switch, current measurement and current limit, because the
standard limits the current on each pair set separately [TPS23881]_. A
common arrangement ties the positive pairs of both pair sets directly to
the 54 V supply and switches only the negative pairs [EA-bt]_
[TPS23881]_. With one channel off, current then flows out on both positive
pairs and back on one negative pair; the standard treats this as 2-pair
power [EA-bt]_.

Before applying power to both pair sets, the power sourcing equipment runs
a *connection check*: it finds out whether the two pair sets lead to one
powered-device controller (*single signature*) or to two separate ones
(*dual signature*). A single-signature powered device shows a valid
signature on one pair set only while the other pair set is left alone;
applying 3.7–57 V or more than 124 µA to the other pair set spoils it. A
dual-signature powered device shows a valid signature on each pair set
regardless of the other [EA-bt]_. The TPS23881 completes the connection
check within 400 ms of a valid detection [TPS23881]_. A dual-signature
powered device is detected and classified on each pair set separately,
and Type 3 power sourcing equipment may not assign more than 30 W to any
one pair set [TPS23881]_.

The powered device sees no difference between 2-pair and 4-pair power
apart from the lower cable loss (6.25 Ω instead of 12.5 Ω loop
resistance), because its two bridges join both pair sets onto one supply.

How power allocation is learned and offered
-------------------------------------------

The powered device must not draw more than it has been assigned, and the
power sourcing equipment must not assign more than it can supply. The
allocation is set in hardware during classification and can later be
changed in software.

In hardware: the number of class events
   The assigned class is the lower of the requested class and the class
   implied by the number of class events (table above). Power sourcing
   equipment that cannot afford the requested power issues fewer events;
   the powered device is then *demoted* and must either stay off or start
   in a reduced-power mode [EA-bt]_.

Indicator outputs of powered-device controllers
   The powered-device controller counts the events in hardware and
   reports the result on open-drain pins referenced to its return node.
   They are passed through optocouplers when the DC-DC converter is
   isolated [TPS2378]_ [TPS2372]_.

   * TI TPS2378: one pin, T2P, pulled low after a two-event classification
     [TPS2378]_.
   * TI TPS2372: three pins, TPH, TPL and BT, which together encode the
     type of the power sourcing equipment and the allocated power
     (12.95 W, 25.5 W, 40 W, 51 W, 62 W or 71 W), valid about 24 ms after
     power good [TPS2372]_.
   * Analog Devices LT4275: one pin, T2P, which floats for 13 W, is low
     for 25.5 W, and toggles at about 840 Hz for Analog Devices' own
     higher-power extension [LT4275]_.

Registers of power sourcing equipment controllers
   A power sourcing equipment controller reports the requested class and
   the assigned class of each port in registers that the host reads over
   I2C, and takes the per-port power allocation from a register that sets
   how many class events it issues [TPS23881]_.

In software: LLDP
   After power is on and the Ethernet link is up, the two ends can change
   the allocation by exchanging Ethernet messages of the *Link Layer
   Discovery Protocol* (LLDP, IEEE 802.1AB). These are small frames sent
   only to the next device on the cable, with destination MAC address
   01-80-C2-00-00-0E and type field 0x88CC [PoE-LLDP]_. IEEE 802.3
   Clause 79 defines a "Power via MDI" field carried in them. Its main
   entries are a *PD requested power value* sent by the powered device, a
   *PSE allocated power value* sent by the power sourcing equipment, and
   a *PSE maximum available power* hint; power values are in units of
   0.1 W, so 255 means 25.5 W [EA-bt]_.

   As a powered device, evampire's processor sends its requested power
   and watches the allocated value. It may lower its request to hand
   power back, or, after a demotion, ask again for up to the class it
   requested in hardware but never more [EA-bt]_. Powered devices of
   class 4 and above must support this exchange [EA-bt]_.

   As power sourcing equipment, evampire's processor reads the powered
   device's request, decides from its power budget how much to allocate,
   and answers with the allocated value; the new limit applies once both
   sides show the same value [EA-bt]_. Support for this exchange is
   optional for power sourcing equipment [EA-bt]_, but it is the only way
   to raise a powered device's allocation without removing power and
   classifying it again.

   On evampire both exchanges run on the RISC-V processor in software,
   using the internal Ethernet port to send and receive the frames.

LLDP frames on the forwarding path
   evampire forwards every frame between ports A and B unchanged. LLDP
   frames are addressed to 01-80-C2-00-00-0E, which normal bridges do not
   forward [PoE-LLDP]_. Forwarded unchanged, the LLDP frames of the
   powered device on port B would reach the power sourcing equipment on
   port A, and those of the upstream power sourcing equipment would reach
   the powered device on port B. Each end would then see two partners'
   power fields on one link, and the power exchanges on the two ports
   would interfere. evampire must itself answer as power sourcing
   equipment on port B and as powered device on port A. How the
   forwarding path handles these frames is an open design decision (see
   below).

Analog blocks in a powered-device controller
--------------------------------------------

All the powered-device functions work at the cable voltage, up to 57 V
plus surges. Commercial powered-device controller chips combine them on a
100 V process. All voltages inside the controller are measured from its
negative input (VSS), the negative output of the bridges.

.. _fig-poe-pd-controller:

.. graphviz:: poe/pd-controller.dot
   :caption: Blocks inside a typical powered-device controller. In the TI
             parts the isolation switch sits in the negative path, between
             the load return (RTN) and VSS.
   :align: center

Signature resistor and its switch
   A 24.9 kΩ resistor connected while the input is in the detection range.
   On the TPS2378 the resistor is external, between VDD and the DEN pin,
   and the controller connects it between about 1.4 V and 10.9 V and
   disconnects it above that range to save power. Pulling DEN low also
   turns the isolation switch off, so the same pin lets the board refuse
   or drop the power [TPS2378]_. The LT4275 integrates the resistor
   [LT4275]_. During mark events a second, lower resistance is connected
   to spoil the signature.

Classification current regulator
   A regulator that holds a fixed voltage across an external resistor
   while the input is in the class range, so that the current is set by
   the resistor. The designer picks the resistor from the class to be
   requested; this calculation checks that the chosen resistor lands in
   the right current window:

   .. math::

      I_\text{class} = \frac{V_\text{CLS}}{R_\text{CLS}} + I_\text{bias}

   where :math:`V_\text{CLS}` is the regulated voltage (about 2.5 V on
   the TI parts [TPS2378]_, 1.40 V on the LT4275 [LT4275]_),
   :math:`R_\text{CLS}` the external class resistor, and
   :math:`I_\text{bias}` the controller's own small supply current, which
   the data sheets fold into their resistor tables. For class signature 4,
   ignoring :math:`I_\text{bias}`:

   .. math::

      \text{TPS2378:} \quad \frac{2.5 \,\text{V}}{63.4 \,\Omega}
        = 39.4 \,\text{mA}, \qquad
      \text{LT4275:} \quad \frac{1.40 \,\text{V}}{34.8 \,\Omega}
        = 40.2 \,\text{mA}

   with 63.4 Ω and 34.8 Ω the class 4 resistors from [TPS2378]_ and
   [LT4275]_. Both land in the 36–44 mA window for class signature 4,
   leaving about 4 mA of margin for resistor tolerance, the regulator's
   accuracy and :math:`I_\text{bias}`. The regulator
   is turned off above the class range and during thermal shutdown to
   limit dissipation [TPS2378]_.

Window comparators with hysteresis
   A set of comparators on the input voltage decides which step is in
   progress. Hysteresis gives each comparator memory, so that the state
   does not chatter on noise and so that falling and rising thresholds can
   be placed in the gaps between the standard's ranges:

   .. list-table:: TPS2372 input-voltage comparators
      :header-rows: 1
      :widths: 40 30 30

      * - Comparator
        - Threshold (typical)
        - Hysteresis (typical)
      * - Class lower (rising)
        - 12.5 V
        - 1.6 V
      * - Class upper (rising)
        - 22 V
        - 0.78 V
      * - Mark reset (falling)
        - 3.9 V
        - —
      * - Turn on (rising)
        - 38.1 V
        - 6.1 V

   Source: [TPS2372]_. A small state machine combines the comparator
   outputs, counts class events and latches the result for the indicator
   pins.

Reference
   The thresholds and the classification voltage need a reference that is
   accurate over −40 °C to 125 °C. The TPS2372 block diagram shows a 1.5 V
   reference on a REF pin with an external 49.9 kΩ resistor [TPS2372]_;
   the LT4275 block diagram shows internal voltage and current references
   [LT4275]_. A bandgap reference is the usual way to build this.

Isolation switch with current limit
   An N-channel MOSFET rated for 100 V that keeps the DC-DC converter and
   its large capacitor disconnected until the turn-on threshold is
   reached, then charges the capacitor with a limited current, and then
   stays fully on with a higher current limit as overload protection.
   Examples: TPS2378, 0.42 Ω, 140 mA inrush limit, 1 A limit; TPS2372-4,
   0.1 Ω, 335 mA inrush limit, 2.2 A limit [TPS2378]_ [TPS2372]_. If the
   load pulls the switch out of saturation for longer than a filter time
   (800 µs on the TPS2378, 1.65 ms on the TPS2372), the controller falls
   back to the inrush limit. The LT4275 drives an external MOSFET instead,
   from an internal charge pump, and sets the inrush current with a
   capacitor on the gate [LT4275]_.

Power-good output
   An open-drain output that tells the DC-DC converter it may start. It is
   held low while the bulk capacitor charges (TPS2372 PG, TPS2378 CDB,
   LT4275 PWRGD) [TPS2372]_ [TPS2378]_ [LT4275]_.

Thermal protection
   The isolation switch and the class regulator can overheat during a
   short circuit or a long class event. A temperature sensor turns them
   off and lets them restart after cooling: at 158 °C typical (140 °C
   minimum) with 20 °C hysteresis on the TPS2372, 145 °C typical on the
   TPS2378 [TPS2372]_ [TPS2378]_.

Input protection
   A transient-voltage suppressor (TI recommends an SMAJ58A) across the
   bridge output limits surges from the cable to below the controller's
   100 V rating [TPS2372]_ [LT4275]_.

.. list-table:: Example powered-device controller chips
   :header-rows: 1
   :widths: 18 14 22 22 24

   * - Part
     - Maker
     - Standard
     - Isolation switch
     - Notes
   * - TPS2378
     - Texas Instruments
     - 802.3at, Type 2 (up to 25.5 W)
     - Internal, 0.42 Ω
     - T2P indicator, converter enable output
   * - TPS2372-3 / -4
     - Texas Instruments
     - 802.3bt, Types 3 and 4 (51 W / 71.3 W)
     - Internal, 0.3 Ω / 0.1 Ω
     - TPH/TPL/BT indicators, automatic maintain power signature,
       autoclass
   * - TPS23753A
     - Texas Instruments
     - 802.3at, Type 1 (13 W)
     - Internal, 0.7 Ω
     - Includes a current-mode controller for an isolated DC-DC converter
   * - LT4275A / B / C
     - Analog Devices
     - 802.3bt-compatible (A, up to 90 W with a proprietary extension),
       802.3at (B), 802.3af (C)
     - External N-channel MOSFET
     - T2P indicator, power good, integrated signature resistor
   * - LTC4269-1
     - Analog Devices
     - 802.3at, Type 2
     - Internal, 0.7 Ω
     - Includes a synchronous flyback controller
   * - NCP1096
     - onsemi
     - 802.3bt (up to 90 W at the power sourcing equipment)
     - Internal
     - Power good output, auxiliary supply input
   * - PD70224
     - Microchip
     - 802.3af/at/bt
     - —
     - MOSFET bridge rectifier that replaces the diode bridges (listed as
       not recommended for new designs)

Sources: [TPS2378]_, [TPS2372]_, [TPS23753A]_, [LT4275]_, [LTC4269-1]_,
[NCP1096]_, [PD70224]_.

The input converter
~~~~~~~~~~~~~~~~~~~

After the isolation switch the board has a 37–57 V supply. A DC-DC
converter brings it down to the board's internal power bus.

Isolated flyback converter
   A transformer separates the cable side from the rest of the board,
   which keeps the cable electrically isolated from any other connector or
   metal part the user can touch. Parts such as the TPS23753A and the
   LTC4269-1 combine the powered-device controller with the flyback
   controller [TPS23753A]_ [LTC4269-1]_.

Non-isolated buck converter
   Simpler and smaller. Analog Devices notes that isolation is not needed
   when the powered device is a single unit with no other external
   connector, fully enclosed in plastic [ADI-PoE]_. A board built around
   evampire has other external connectors (the second Ethernet port and
   the USB Type-C ports). The isolation requirement and its exceptions are
   set by the standard and by safety rules; they have not been checked
   here against the text of IEEE 802.3.

Start-up follows the power-good signal. On the TPS23753A, the converter
stays off during inrush; an internal current source then charges the
converter's bias capacitor to about 9 V, the converter starts with a soft
start, and an auxiliary transformer winding must take over the bias supply
before the capacitor falls to about 5.5 V [TPS23753A]_.

Analog blocks in a power sourcing equipment controller
------------------------------------------------------

.. _fig-poe-pse-controller:

.. graphviz:: poe/pse-controller.dot
   :caption: One channel of a power sourcing equipment controller with a
             low-side switch, as in the TI TPS2388x family.
   :align: center

Commercial power sourcing equipment controllers handle four to eight
channels each, use external power MOSFETs and sense resistors, and are
controlled by a host processor over I2C. In the TI TPS23881 the positive
pairs connect straight to the 54 V supply and each channel switches the
negative pair through an external MOSFET in series with a 0.2 Ω sense
resistor to ground. The controller itself is referenced to that ground,
so its sense inputs see only millivolts [TPS23881]_.

Detection current sources and voltage measurement
   Current sources that force the detection currents (160 µA and 270 µA
   on the TPS23881) into the port while a voltage ADC measures the port
   voltage, averaged over 16 samples (about 16.6 ms) to reject 50 Hz and
   60 Hz interference [TPS23881]_.

Current and voltage ADCs
   The TPS23881 has a 14-bit integrating current ADC per channel, used for
   classification, power policing and disconnect detection (current
   averaged over about 100 ms when powered, 2–3 % accuracy), and two
   shared voltage ADCs for detection, port voltage, supply voltage, power
   good and temperature [TPS23881]_.

Gate driver and current-limit loop
   A gate driver (10–12.5 V gate drive, 50 µA to turn on, 100 mA to turn
   off on the TPS23881) inside a control loop that sets the MOSFET current
   from the sense voltage: the class voltage during classification, the
   inrush limit at turn-on, the operating limit with foldback afterwards
   [TPS23881]_.

Fast short-circuit comparator
   A comparator on the sense voltage that turns the MOSFET off within
   about 1 µs, independent of the slower loop and the ADCs [TPS23881]_.

Power MOSFET and sense resistor
   External parts. TI recommends a 100 V MOSFET with 50–150 mΩ on
   resistance and a safe operating area that covers the inrush and
   foldback curves, and a 0.2 Ω, 1 %, 0.25 W sense resistor [TPS23881]_.
   The Analog Devices LTC4291-1/LTC4292 pair uses 0.15 Ω sense resistors
   and MOSFETs of 30 mΩ or less [LTC4291]_.

State machine, timers and host interface
   Logic (a small processor in the TPS23881, with firmware that the host
   loads over I2C at start-up) runs the detection, classification, power-on
   and disconnect sequences and reports through registers. The controller
   can run each port automatically, run detection and classification but
   wait for the host before powering a port, or obey single commands from
   the host [TPS23881]_.

Thermal shutdown
   The TPS23881 shuts down at 135 °C minimum (146 °C typical) [TPS23881]_.

Isolation of the host interface
   When the 54 V circuit must be isolated from the logic, the I2C bus has
   to cross an isolation barrier. The Analog Devices LTC4291-1/LTC4292
   chipset splits the controller in two and carries the communication
   across a transformer, avoiding optocouplers and an isolated 3.3 V
   supply [LTC4291]_.

.. list-table:: Example power sourcing equipment controller chips
   :header-rows: 1
   :widths: 18 14 26 42

   * - Part
     - Maker
     - Standard and channels
     - Notes
   * - TPS23881
     - Texas Instruments
     - 802.3bt Types 3 and 4; 8 channels (8 two-pair or 4 four-pair ports)
     - External MOSFETs, 0.2 Ω sense, per-channel 14-bit current ADC,
       autoclass, I2C
   * - TPS2388
     - Texas Instruments
     - 802.3at; 8 channels
     - External MOSFETs, I2C
   * - TPS23861
     - Texas Instruments
     - 802.3at; 4 channels
     - External MOSFETs, I2C, can also run without a host
   * - LTC4291-1 / LTC4292
     - Analog Devices
     - 802.3bt Types 3 and 4; 4 ports
     - Two-chip set with transformer-isolated host link, 0.15 Ω sense
   * - LTC4279
     - Analog Devices
     - 802.3at Types 1 and 2, plus a proprietary extension up to 90 W;
       1 port
     - Runs without a host processor; external MOSFET and sense resistor
   * - PD69208M
     - Microchip
     - 802.3at/bt Type 3; 8 ports
     - Fully integrated power sourcing equipment manager with internal
       switches
   * - Si3474
     - Skyworks (formerly Silicon Labs)
     - 802.3af/at/bt; 8 channels (8 two-pair or 4 four-pair ports)
     - External MOSFETs, 0.2 Ω or 0.255 Ω sense, I2C or autonomous

Sources: [TPS23881]_, [TPS2388]_, [TPS23861]_, [LTC4291]_, [LTC4279]_,
[PD69208]_, [Si3474]_. The entries for the TPS2388, TPS23861, LTC4279 and
PD69208 come from their product summaries.

The 54 V supply
~~~~~~~~~~~~~~~

The power sourcing equipment needs a supply inside the output voltage
range of its type: 44–57 V (Type 1), 50–57 V (Types 2 and 3) or 52–57 V
(Type 4) [EA-bt]_ [TPS23881]_. A value near 54 V, as in the TI application
examples, leaves room above the minimum for the voltage drop in the
switch and sense resistor and below the 57 V maximum for tolerance
[TPS23881]_.

On an evampire board this supply is made from the internal power bus with
a boost converter. As an example of the scale, the TI PMP7979 reference
design is a two-phase LM5122 boost converter that makes 54 V at 4.8 A
(about 260 W) from 12–67 V [PMP7979]_. The converter must meet the ripple
limits given above, and its output needs:

* bulk capacitance rated for 100 V (TI suggests two 47 µF capacitors per
  TPS23881) and a transient-voltage suppressor with at least 58 V
  standoff, which together keep the supply below the controller's 70 V
  rating during a surge [TPS23881]_;
* per port, a 0.1 µF 100 V capacitor across the port, a port
  transient-voltage suppressor with at least 58 V standoff and under 95 V
  clamping at the expected surge current, and a slow-blow fuse rated for
  at least 60 V DC [TPS23881]_.

The standard limits the capacitance that power sourcing equipment
presents at its port to 520 nF [EA-bt]_. Ethernet ports also commonly
connect each transformer centre tap through about 75 Ω and 10 nF to a
common node that is bypassed to chassis ground with 1000–4700 pF rated
for 2 kV [TPS23881]_.

A port that can take either role
--------------------------------

In the full design either Ethernet port can be a powered device or power
sourcing equipment. Power over Ethernet has no exchange in which the two
ends of a cable agree to swap roles, so each port's role is fixed by the
board before a cable is attached, and stays fixed while the cable is
connected.

.. _fig-poe-dual-role:

.. graphviz:: poe/dual-role.dot
   :caption: An Ethernet port that can take either role: both sets of
             circuits share the centre taps, and only one is connected at a
             time.
   :align: center

Such a port needs both sets of circuits on the same transformer centre
taps: the bridges, signature, class circuit and isolation switch of a
powered device, and the channels of power sourcing equipment (two for
4-pair power). The two must not both be connected at once:

* The powered-device signature would appear in parallel with the remote
  powered device, so the port's own power sourcing equipment would measure
  the wrong resistance during detection.
* The power sourcing equipment circuit loads the port when it is off: the
  TPS23881 connects 80–190 kΩ from each channel's drain pin to its supply
  whenever the channel is neither detecting nor powered [TPS23881]_. This
  resistance appears in parallel with the port's own signature, so the
  upstream power sourcing equipment would measure

  .. math::

     R_\text{seen} = \frac{R_\text{det} \, R_\text{drain}}{R_\text{det} + R_\text{drain}}
       = \frac{24.9 \,\text{k}\Omega \times 80 \,\text{k}\Omega}
              {24.9 \,\text{k}\Omega + 80 \,\text{k}\Omega}
       = \frac{1992 \,\text{k}\Omega^2}{104.9 \,\text{k}\Omega}
       = 19.0 \,\text{k}\Omega

  where :math:`R_\text{det} = 24.9\,\text{k}\Omega` is the signature
  resistor [TPS2378]_ and :math:`R_\text{drain} = 80\,\text{k}\Omega` the
  lowest drain-pin resistance of the TPS23881 [TPS23881]_. With the
  highest value, 190 kΩ, the result is 22.0 kΩ. Both are below the
  23.7 kΩ minimum, so the port would fail detection in the
  powered-device role whatever the part-to-part spread. The calculation
  assumes the drain resistance is connected across the same two centre
  taps as the signature, which depends on how the two circuits are
  wired.

Each path therefore needs a disconnect switch rated for the cable voltage
and surges, turned on only for the selected role. The processor selects
the role at start-up from the board configuration and sets the switches
before enabling either controller.

Safety rules
~~~~~~~~~~~~

Never apply power without a valid detection
   This is the rule that protects equipment not designed for Power over
   Ethernet. It applies to every pair set separately [EA-bt]_. In the
   powered-device role the board's own power sourcing equipment channels
   must be off and disconnected.

Two power sourcing equipment ports connected together
   Each sees the other's detection voltage source instead of a 25 kΩ
   signature, so neither detects a valid powered device and neither
   applies power. The detection circuits must survive being driven by the
   other end: under the Clause 33 rules power sourcing equipment must
   withstand a backdrive current of 5 mA at a voltage up to its operating
   voltage and still detect correctly afterwards [UNH-PSE]_. In the full
   design a cable between port A and port B of the same board, with both
   set as power sourcing equipment, is the same case.

Two powered-device ports connected together
   Neither supplies a voltage, so nothing happens.

Power sourcing equipment connected to equipment without Power over Ethernet
   Ordinary Ethernet equipment connects its centre taps only through
   capacitors, so at DC it looks like an open circuit; detection fails and
   no power is applied. The TPS23881 reports above 400 kΩ as open
   [TPS23881]_.

Powered device connected to equipment without Power over Ethernet
   No voltage arrives; the powered-device controller stays off and the
   board runs from another source.

Pass-through power
------------------

When power arrives on port A and leaves on port B (or a USB Type-C port),
the processor keeps a power budget: the power offered on the outputs must
not exceed the power granted on the input, minus the board's own use and
the conversion losses (see :doc:`index`).

The incoming voltage cannot simply be switched through to port B. At the
powered device it can be as low as 37 V (Type 1 rules) or about 42 V,
while power sourcing equipment must supply at least 44 V (Type 1) or 50 V
(Types 2 and 3) [EA-bt]_. So the power passes through the input converter
onto the internal bus and through the boost converter back up to about
54 V.

The following calculation decides which class the board can offer on
port B for a given input. It follows the power from the port A input,
through the input converter onto the bus, minus what the board itself
uses, and through the 54 V converter to the port B output:

.. math::

   P_\text{bus} = P_\text{in} \, \eta_\text{in}, \qquad
   P_\text{avail} = P_\text{bus} - P_\text{board}, \qquad
   P_\text{B} = P_\text{avail} \, \eta_\text{hv}

where:

* :math:`P_\text{in}` is the power granted at port A, equal to the class
  power at the powered device (class table above), in W;
* :math:`\eta_\text{in}` is the efficiency of the input converter
  (assumed 0.90 here);
* :math:`P_\text{bus}` is the power delivered onto the internal bus, in W;
* :math:`P_\text{board}` is the board's own consumption (evampire and the
  Ethernet transceivers; assumed 5 W here);
* :math:`P_\text{avail}` is the bus power left for port B, in W;
* :math:`\eta_\text{hv}` is the efficiency of the 54 V boost converter,
  including the power sourcing equipment switch and sense resistor
  (assumed 0.94 here);
* :math:`P_\text{B}` is the power available at the port B output, in W.

The class offered on port B must be one whose power sourcing equipment
power (the "must supply" column of the class table) is no more than
:math:`P_\text{B}`. That column already includes the worst-case loss in
the outgoing cable, so no separate cable term is needed. The
efficiencies and the board consumption are assumed values chosen only to
illustrate the method; the real ones depend on the converters chosen and
on the board power budget, which is not yet fixed. The model also
assumes the converters' efficiencies stay constant over load.

.. list-table:: Pass-through examples (assumed efficiencies 0.90 and 0.94, board use 5 W)
   :header-rows: 1
   :widths: 22 12 18 14 16 18

   * - Input on port A
     - :math:`P_\text{in}`
     - :math:`P_\text{bus} = P_\text{in} \times 0.90`
     - :math:`P_\text{avail} = P_\text{bus} - 5`
     - :math:`P_\text{B} = P_\text{avail} \times 0.94`
     - Highest class on port B
   * - Type 2, class 4
     - 25.5 W
     - 22.95 W
     - 17.95 W
     - 16.87 W
     - 3 (needs 15.4 W)
   * - Type 3, class 6
     - 51.0 W
     - 45.90 W
     - 40.90 W
     - 38.45 W
     - 4 (needs 30 W)
   * - Type 4, class 8
     - 71.3 W
     - 64.17 W
     - 59.17 W
     - 55.62 W
     - 5 (needs 45 W)

In words: with these assumptions, a Type 2 input lets port B offer
class 3 (13 W at the far powered device), because class 4 would need
30 W; a Type 3 class 6 input allows class 4 (25.5 W), because class 5
would need 45 W; and a Type 4 class 8 input allows class 5 (40 W),
because class 6 would need 60 W. Offering class 5 needs Type 3 or Type 4
power sourcing equipment with 4-pair power on port B.

The budgeting can be tightened in two ways. The class power of the
outgoing port assumes the worst-case cable; if the powered device on
port B uses autoclass, the power sourcing equipment can measure its real
draw and reserve only that plus a small margin [EA-bt]_. And the powered
device on port B may ask for less over LLDP. When the power granted on
port A falls (for example after an LLDP change), the processor must lower
the allocation on port B first: over LLDP if the powered device supports
it, otherwise by turning the port off and classifying it again with fewer
class events.

Building the high-voltage functions: on chip or external
--------------------------------------------------------

Every function described above handles voltages far above the continuous
ratings of the standard transistors in the gf180mcu process. That does not
by itself decide where each function is built: the absence of a ready-made
high-voltage device or cell means a custom design would be needed, not
that the function is impossible on chip. This section separates three
kinds of limit, describes the electrical stresses each function must
survive, and then sets out the on-chip and external options for each
function. Which option is used is an open design decision for every
function.

Three kinds of limit
~~~~~~~~~~~~~~~~~~~~

Ratings of the standard devices and cells
   The conservative continuous operating limits that the foundry
   guarantees for long life.

   .. list-table:: Continuous ratings of standard gf180mcu devices
      :header-rows: 1
      :widths: 35 30 35

      * - Device
        - Rating
        - Notes
      * - 3.3 V MOSFETs (thin gate oxide)
        - 3.3 V nominal, +10 %
        - Gate-to-any-node DC limit 3.63 V
      * - 5 V and 6 V MOSFETs (thick gate oxide)
        - 5 V or 6 V nominal, +10 %
        - Gate-to-any-node DC limit given as "6.5V/6V for 5V/6V process
          thick gate"
      * - 10 V LDNMOS and LDPMOS (optional)
        - 10 V
        - Drain extended; its well shares the substrate potential
      * - MIM capacitor, 1 fF/µm² option (optional)
        - 20 V maximum operating
        - The 1.5 fF/µm² and 2 fF/µm² options are for 6 V use

   Sources: [PoE-GF180-DRM-2]_ (process options: 3.3 V and 5 V or 6 V),
   [PoE-GF180-DRM-14]_ (supply and gate-oxide limits),
   [PoE-GF180-EP-8]_ and [PoE-GF180-LDMOS]_ (10 V LDMOS),
   [PoE-GF180-MIM]_ (MIM capacitors). Which optional layers (LDMOS, MIM
   option, high-resistance poly) are offered on wafer.space runs has not
   been checked.

Physical limits of the process layers
   The voltages and currents at which a layer is destroyed or wears out.
   These are higher than the ratings, but a design must stay below them
   with margin and its own reliability analysis.

   .. list-table:: Breakdown and current limits documented for gf180mcu
      :header-rows: 1
      :widths: 42 28 30

      * - Layer or junction
        - Documented limit
        - Source
      * - Gate oxide, 3.3 V transistors
        - 7 V minimum (8.8–9 V typical)
        - [PoE-GF180-EP-OX]_
      * - Gate oxide, 6 V transistors
        - 12 V minimum (16 V typical)
        - [PoE-GF180-EP-OX]_
      * - N+ to p-well junction (3.3 V / 6 V NMOS)
        - 7 V / 8.5 V minimum (11 V typical)
        - [PoE-GF180-EP-5]_
      * - P+ to n-well junction (3.3 V / 6 V PMOS)
        - 6.5 V / 8.5 V minimum (10.5 V typical)
        - [PoE-GF180-EP-5]_
      * - N-well to substrate junction
        - 10 V minimum (14 V typical)
        - [PoE-GF180-EP-5]_
      * - 10 V LDMOS drain to source
        - 13.2 V minimum (14.5 V typical)
        - [PoE-GF180-EP-8]_
      * - Vertical PNP, collector to emitter
        - 10 V minimum (15 V typical)
        - [PoE-GF180-EP-BJT]_
      * - MIM dielectric, 1 fF/µm² option
        - 20 V minimum (40 V typical) at 10 µA
        - [PoE-GF180-MIM]_
      * - MIM dielectric, 1.5 and 2 fF/µm² options
        - 10 V minimum (24–30 V typical)
        - [PoE-GF180-MIM]_
      * - Deep n-well to substrate junction
        - not documented
        - the layer exists ([PoE-GF180-DRM-4]_); no breakdown figure found
      * - Field oxide and inter-metal dielectric (poly or metal to
          substrate, metal to metal)
        - not documented
        - —
      * - Metal current density (electromigration, 85 °C)
        - 2.09 mA/µm (Metal 1 to top-1); 16.52 mA/µm (30 kÅ top metal)
        - [PoE-GF180-DRM-EM]_
      * - Contact and via current (85 °C)
        - 0.58 mA each
        - [PoE-GF180-DRM-EM]_

   For ESD, the PDK gives transmission-line-pulse data for a 5 V/6 V
   grounded-gate NMOS without ESD implant: it breaks down at about
   10.7 V, snaps back to about 6.2 V and fails at about 7 mA per µm of
   width [PoE-GF180-ESD]_.

What custom structures could reach
   Published work shows that low-voltage CMOS can switch or generate
   voltages several times its device rating:

   .. list-table:: Published high-voltage results in low-voltage CMOS
      :header-rows: 1
      :widths: 30 22 48

      * - Technique
        - Process
        - Reported result
      * - Drain-extended NMOS with shifted gate, no added masks
        - 0.5 µm bulk CMOS
        - Breakdown "of the order of 30 V" [DosSantos2003]_
      * - Drain-extended NMOS and PMOS, no process change
        - 1.5–1.8 V, 0.18 µm bulk CMOS
        - 5 V drain operation with the core gate oxide [Mitros2000]_
      * - Stacked low-voltage transistors (3 in series)
        - 65 nm bulk CMOS, 2.5 V devices
        - Driver working from 5.5 V [Pashmineh2016]_
      * - Stacked MOSFETs with capacitive voltage sharing
        - 0.35 µm SOI CMOS
        - 2 times the process rating at 20 MHz; scalable to n times
          [Mentze2006]_
      * - 20 stacked transistors with a resistive bias network
        - 65 nm SOI CMOS
        - 20 V DC and RF in the off state [Syroiezhin2023]_
      * - Charge pump with double-diode substrate isolation and field
          oxide isolation
        - 65 nm bulk CMOS
        - 36 V output, 3 times the about 12 V reachable with a single
          junction to substrate [Ismail2017]_
      * - Charge pump of polysilicon diodes on field oxide
        - 0.25 µm, 2.5 V bulk CMOS
        - 28.08 V output, above the about 18.9 V n-well to substrate
          breakdown of that process [Ker2007]_
      * - Charge pump of triple-well NMOS transistors
        - 0.18 µm bulk CMOS
        - Regulated output from about 13 V to 16.95 V [Li2019]_

   Two points limit how directly these carry over. Results on SOI rely on
   a buried oxide that isolates every transistor from the substrate; the
   gf180mcu process is bulk silicon. And in bulk silicon the highest node
   of a stack still sits at the full voltage relative to the substrate, so
   some junction or dielectric must hold that voltage continuously. The
   bulk results above did this by stacking two junctions between the
   circuit and the substrate, or by building devices in polysilicon on top
   of the field oxide, and reached 28–36 V [Ker2007]_ [Ismail2017]_. In
   gf180mcu the documented junction to substrate, n-well to substrate,
   breaks down at 10 V minimum, and the breakdown of the deep n-well and
   of the field oxide under poly and metal is not documented. Whether a
   gf180mcu structure can hold 57 V plus surge margin to the substrate is
   therefore not known from the documentation; it would need test
   structures or foundry data. No documented limit rules it out, and no
   documented structure shows it. All the published bulk results above are
   below 57 V.

The stresses a function must survive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Four different kinds of stress reach the cable-side circuits. They differ
by orders of magnitude in duration and energy, which decides whether a
clamp can absorb them or a structure must block them.

ESD during handling
   The human body model used for chip ESD ratings is a 100 pF capacitor
   discharged through 1500 Ω, with a rise time of 2–10 ns and a peak
   current of 0.67 A per kV [ESDA-HBM]_. For the common 2 kV rating (the
   TPS23881 is rated ±2000 V [TPS23881]_):

   .. math::

      I_\text{peak} = \frac{V_\text{HBM}}{R_\text{HBM}}
        = \frac{2000 \,\text{V}}{1500 \,\Omega} = 1.33 \,\text{A}, \qquad
      \tau = R_\text{HBM} \, C_\text{HBM}
        = 1500 \,\Omega \times 100 \,\text{pF} = 150 \,\text{ns}

   .. math::

      Q = C_\text{HBM} \, V_\text{HBM} = 100 \,\text{pF} \times 2000 \,\text{V}
        = 200 \,\text{nC}

   .. math::

      E = \tfrac{1}{2} \, C_\text{HBM} \, V_\text{HBM}^2
        = \tfrac{1}{2} \times 100 \,\text{pF} \times (2000 \,\text{V})^2
        = 0.2 \,\text{mJ}

   where :math:`V_\text{HBM}` is the charging voltage,
   :math:`R_\text{HBM}` and :math:`C_\text{HBM}` the model's resistor and
   capacitor [ESDA-HBM]_, :math:`I_\text{peak}` the peak current,
   :math:`\tau` the decay time constant, :math:`Q` the charge and
   :math:`E` the stored energy. The 2 kV is the voltage on the tester's
   capacitor, not on the pin: an ESD clamp starts conducting at a few
   volts above the supply (about 10.7 V for the 6 V grounded-gate NMOS
   above) and carries 1.33 A peak for a few hundred nanoseconds. With
   7 mA/µm before failure, a 6 V grounded-gate NMOS of about
   1.33 A ÷ 7 mA/µm = 190 µm width would carry it (an estimate; real ESD
   design follows the PDK guidelines [PoE-GF180-ESD]_). This is why
   ordinary I/O cells survive kilovolt ratings.

Surge from the cable
   Lightning-induced surges on Ethernet ports are tested with a 10/700 µs
   generator (10 µs rise, 700 µs to half value in open circuit) whose
   effective output resistance is 40 Ω; it delivers 37.5 A peak into a
   short circuit at 1500 V, and the IEC 61000-4-5 test levels for
   symmetrical lines run from 500 V to 4000 V depending on the
   installation [TI-SLUA736]_. The energy a clamp at the cable has to
   absorb can be estimated, for a 1500 V surge into a clamp that holds
   90 V (below the 95 V limit TI gives for a power sourcing equipment port
   suppressor [TPS23881]_):

   .. math::

      I_\text{peak} = \frac{V_\text{surge} - V_\text{clamp}}{R_\text{gen}}
        = \frac{1500 \,\text{V} - 90 \,\text{V}}{40 \,\Omega} = 35.3 \,\text{A}

   .. math::

      \tau = \frac{t_\text{half}}{\ln 2} = \frac{320 \,\mu\text{s}}{0.693}
        = 462 \,\mu\text{s}, \qquad
      Q \approx I_\text{peak} \, \tau = 35.3 \,\text{A} \times 462 \,\mu\text{s}
        = 16.3 \,\text{mC}

   .. math::

      E \approx V_\text{clamp} \, Q = 90 \,\text{V} \times 16.3 \,\text{mC}
        = 1.5 \,\text{J}

   where :math:`V_\text{surge} = 1500\,\text{V}` and :math:`R_\text{gen} =
   40\,\Omega` are the generator settings, :math:`t_\text{half} =
   320\,\mu\text{s}` the time to half value of its short-circuit current
   [TI-SLUA736]_, :math:`V_\text{clamp} = 90\,\text{V}` an assumed clamp
   voltage, and :math:`\tau`, :math:`Q` and :math:`E` the decay time
   constant, charge and energy in the clamp. The estimate treats the
   current as a single exponential decay and ignores the 5 µs rise. It is
   about 7000 times the HBM energy and lasts thousands of times longer,
   so it is far outside the regime in which on-chip ESD structures are
   characterised. Commercial designs absorb it in external
   transient-voltage suppressors [TPS23881]_ [TI-SLUA736]_.

Isolation test
   Power over Ethernet ports must withstand one of: 1500 V rms at
   50–60 Hz for 60 s, 2250 V DC for 60 s, or ten 1500 V impulses of
   10/700 µs shape [TI-SLUA736]_. A task-force contribution to IEEE 802.3
   summarises that Clauses 33 and 145 require this isolation for all
   power sourcing equipment and powered devices [PoE-Iso]_ (the Analog
   Devices article cited above describes exceptions for fully enclosed
   devices [ADI-PoE]_; the text of the standard should decide). This
   stress must be *blocked*, not clamped: a clamp across the isolation
   barrier would fail the test. It acts between the cable conductors and
   other accessible conductors (other connectors, metal parts), not
   between the pins of the power circuit.

Continuous operation
   The cable voltage is 44–57 V for as long as the port is powered, and
   the power path carries up to 0.6 A (class 4: 25.5 W at 42.5 V) or
   1.73 A (class 8: 71.3 W at 41.2 V). A clamp cannot help here: every
   structure across the cable voltage must block it indefinitely, with
   reliability margin. Carrying the current on chip needs wide metal: at
   85 °C, 0.6 A needs 0.6 A ÷ 2.09 mA/µm = 287 µm of Metal 1, or
   0.6 A ÷ 16.52 mA/µm = 36 µm of 30 kÅ top metal, and about 1035
   contacts at 0.58 mA each [PoE-GF180-DRM-EM]_; 1.73 A needs 105 µm of
   that top metal.

So a clamp, on chip or off, can deal with ESD; surges need a clamp sized
for joules, which in practice means an external suppressor; the
isolation test needs a barrier that blocks kilovolts; and the operating
voltage needs structures that block 57 V continuously.

Where the isolation barrier sits
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The isolation requirement decides which circuits can share a ground with
evampire. Its Ethernet data already crosses the transformers, which are the
data isolation barrier. If evampire's ground is connected to other
accessible conductors (for example a USB Type-C connector), then every
circuit connected to the cable-side power must sit on the far side of an
isolation barrier from evampire: an isolated converter for power, and
optocouplers or isolators for signals. A cable-side function built on
evampire would then have to be on the same die as circuits on the other
side of the barrier, which would need an on-die barrier for 1500 V rms;
no gf180mcu structure is documented anywhere near that (the strongest
documented dielectric, the 1 fF/µm² MIM, is rated 20 V
[PoE-GF180-MIM]_).

The alternative is to place the barrier elsewhere: evampire's ground on
the cable side, and the isolation moved to the USB Type-C port and any
other accessible conductor. Then cable-side functions can share
evampire's die, and the USB power path, the configuration channel wires
and any metal parts need isolation instead. Where the barrier sits is an
open design decision that comes before the per-function choices below.
Commercial power sourcing equipment shares one 54 V supply among all its
ports (as in the TPS23881 examples [TPS23881]_), so the two Ethernet ports
of one board can share one cable-side domain; whether that is allowed
between a port that receives power and a port that supplies it has not
been checked against the standard.

Options for each function
~~~~~~~~~~~~~~~~~~~~~~~~~

For each high-voltage function, the conventional external option and the
on-chip custom option are listed with their requirements and risks. The
on-chip options assume evampire is on the cable side of the isolation
barrier; with the barrier between evampire and the cable side, only the
external options apply to the cable-side functions.

Polarity correction
   *External:* two diode bridges or a MOSFET bridge such as the PD70224
   [PD70224]_, rated 100 V and 3–5 A [TPS2372]_.

   *On chip:* an active bridge of stacked transistors. It must block 57 V
   plus surge in reverse, carry the full port current (0.6–1.73 A, which
   needs the metal widths above), and must stay off during detection and
   classification [EA-bt]_. Risks: the blocking voltage to substrate is
   not documented; the substrate itself has to be tied to the most
   negative rectified node, which changes with polarity.

Signature and classification
   *External:* a powered-device controller chip (TPS2372, LT4275 and
   others above).

   *On chip:* the signature, mark load and class current only operate
   below 22 V (the TPS2372 disables classification above that
   [TPS2372]_), and the class current is at most 44 mA. But the circuits
   stay connected while the input rises to 57 V, so they need an
   isolating switch, or a structure that blocks 57 V, ahead of them. The
   class regulator dissipates about 0.8 W during each event (calculated
   above). The comparator thresholds can come from an on-chip divider
   and reference. Risk: as for the bridge, the blocking voltage.

Powered-device pass switch (isolation switch)
   *External:* integrated in the controller, or an external 100 V MOSFET
   driven by the controller (LT4275 [LT4275]_).

   *On chip:* stacked or drain-extended transistors carrying 0.6–1.73 A
   continuously and the inrush current while most of the 57 V is across
   them (the TPS2378 limits inrush to 140 mA, about 8 W at 57 V for tens
   of ms [TPS2378]_). Risks: blocking voltage, safe operating area of a
   custom structure, and the die area for low on-resistance.
   *Mixed:* an external MOSFET with its gate driven from evampire. The
   gate needs about 10 V or more above the source (10–12.5 V from the
   TPS23881 [TPS23881]_, 10–18 V from the LT4275 [LT4275]_), above the
   6 V devices' rating, so it needs a stacked or bootstrapped driver or an
   external driver.

Voltage sensing
   *External divider, on-chip measurement:* a resistor divider scaling
   57 V to about 3 V (calculation below), measured by an on-chip
   comparator or analog-to-digital converter.

   *On-chip divider:* a high-resistance poly divider. With the
   2000 Ω/sq option, 1 MΩ is 500 squares, and at 57 V it dissipates
   57² ÷ 1 MΩ = 3.2 mW [PoE-GF180-EP-6]_. Risks: the top of the divider
   sits at 57 V over the field oxide, whose breakdown is not documented;
   the poly's voltage coefficient (−100 to −200 ppm/V, −150 ppm/V
   typical, for the 2000 Ω/sq option [PoE-GF180-EP-6]_) adds error. A capacitive divider of stacked
   MIM capacitors (at least three of the 20 V-rated type in series for
   57 V, five for a 95 V surge) is an alternative for AC or sampled
   measurement; its bottom-plate-to-substrate dielectric is not
   documented.

Power sourcing switch and current sensing
   *External:* a power sourcing equipment controller with an external
   100 V MOSFET and 0.2 Ω sense resistor per channel (TPS23881 and others
   above).

   *On chip, partly:* with the low-side arrangement the sense resistor,
   the gate driver and the controller sit at ground potential, and the
   sense voltages are millivolts (see the TPS23881 thresholds above), so
   the current measurement, the fast short-circuit comparator and the
   control logic could be on evampire at low voltage. The MOSFET drain
   reaches the full port voltage and stays external unless a custom
   structure blocks 57 V. The gate drive needs 10–12.5 V
   [TPS23881]_, beyond the 6 V devices, so it needs a stacked driver or
   an external driver. The short-circuit cut-off must act in about 1 µs
   [TPS23881]_, in hardware rather than software.

Detection and classification sourcing
   *External:* inside the power sourcing equipment controller.

   *On chip:* the detection currents (160 µA and 270 µA on the TPS23881
   [TPS23881]_) must be delivered into a port node that sits close to the
   54 V supply during detection, and classification needs the port held
   at 15.5–20.5 V with its current limited to at most 100 mA [UNH-PSE]_. Both need a
   high-voltage current source or a linear control of the power MOSFET
   (the TPS23881 classifies through its external MOSFET [TPS23881]_),
   with the measurement and sequencing in evampire. Risks: blocking
   voltage of the current-source structures; the timing rules above.

Converter control
   *External:* converter controller chips (the TPS23753A and LTC4269-1
   combine one with a powered-device controller [TPS23753A]_
   [LTC4269-1]_; the PMP7979 boost uses the LM5122 [PMP7979]_).

   *On chip:* the control loop, pulse-width modulation and protection
   logic are low-voltage functions; the power switches, their 10 V-class
   gate drives and any sensing at the switch node are high-voltage.
   Charge pumps or bootstrapped drivers (as in [Ismail2017]_) could
   generate the gate voltages. Risks: switching-node voltages of 57 V or
   more on chip; the reliability of stacked drivers under fast edges.

Surge and ESD protection
   *External:* transient-voltage suppressors at each port and on the
   54 V supply [TPS23881]_.

   *On chip:* ESD clamps following the PDK guidelines for every pin
   [PoE-GF180-ESD]_. The surge energy estimated above is not within the
   characterised range of on-chip structures, so surge protection stays
   external in every option.

Low-voltage interface and software
   On evampire in every option: status inputs and enable outputs, an I2C
   controller for an external power sourcing equipment controller,
   comparators or an analog-to-digital converter for divided voltages,
   and the software for the power budget and the LLDP exchanges on both
   ports.

The external divider for voltage sensing must bring the highest operating
voltage below the 3.63 V gate limit of evampire's 3.3 V inputs, while
drawing little current. For an example divider:

.. math::

   V_\text{out} = V_\text{in} \, \frac{R_2}{R_1 + R_2}
     = 57 \,\text{V} \times \frac{56 \,\text{k}\Omega}{1056 \,\text{k}\Omega}
     = 57 \,\text{V} \times 0.0530 = 3.02 \,\text{V}

.. math::

   I_\text{div} = \frac{V_\text{in}}{R_1 + R_2}
     = \frac{57 \,\text{V}}{1.056 \,\text{M}\Omega} = 54 \,\mu\text{A}

where :math:`V_\text{in} = 57\,\text{V}` is the highest operating voltage
[EA-bt]_, :math:`R_1 = 1\,\text{M}\Omega` and :math:`R_2 =
56\,\text{k}\Omega` are example resistor values, :math:`V_\text{out}` is
the voltage at evampire's input, and :math:`I_\text{div}` the current the
divider draws. So the input stays below 3.63 V [PoE-GF180-DRM-14]_ at 57 V
and the divider costs about 3 mW. The model ignores the input's leakage
and resistor tolerance, and does not cover surges, which go above 57 V; a
clamp at the divider output is needed for those. On the powered-device
side the divider must sit after the isolation switch, so that it is not
in parallel with the 25 kΩ signature during detection.

A stack of transistors that shares a voltage equally needs enough devices
that each stays within its rating. As a first estimate, ignoring the
imbalance that any real stack has:

.. math::

   N \ge \frac{V_\text{block}}{V_\text{dev,max}}: \qquad
   \frac{57 \,\text{V}}{6.6 \,\text{V}} = 8.6 \;\rightarrow\; 9, \qquad
   \frac{95 \,\text{V}}{6.6 \,\text{V}} = 14.4 \;\rightarrow\; 15

where :math:`V_\text{block}` is the voltage to block (57 V operating, or
95 V as the highest clamping voltage TI allows for a port suppressor
[TPS23881]_), :math:`V_\text{dev,max} = 6.6\,\text{V}` the 6 V device
rating plus 10 % [PoE-GF180-DRM-14]_, and :math:`N` the number of devices.
With 3.3 V devices (3.63 V each) the counts are 16 and 27. This covers
only the drain-to-source sharing; the well-to-substrate voltage of the
top devices is the open question described above.

Open design decisions
~~~~~~~~~~~~~~~~~~~~~

The following choices are not yet made:

* **Where the isolation barrier sits:** between evampire and the
  cable-side circuits, or between evampire and the USB Type-C port and
  other accessible conductors. This comes first, because it decides
  whether any cable-side function can share evampire's die.
* **On chip or external, for each high-voltage function** listed above.
  An on-chip choice needs data the PDK documentation does not give
  (deep n-well and dielectric breakdown to the substrate) and test
  structures to confirm it.
* **Maximum power on each port.** All types and classes are documented
  above; the highest type and class the board supports on input and
  output are not fixed. They decide the controllers, whether port B needs
  two channels (4-pair power, required above class 4), and the size of
  the 54 V boost converter.
* **Board power budget and converter efficiencies.** The pass-through
  examples above use assumed values.
* **External power sourcing equipment controller over I2C, or sequencing
  in evampire software** with on-chip measurement and external or custom
  high-voltage parts.
* **Which measurement circuits the power negotiation interface includes:**
  comparators, an analog-to-digital converter, or only digital status
  inputs and I2C.
* **Handling of LLDP frames on the forwarding path:** whether evampire
  drops, or delivers only to the processor, frames addressed to
  01-80-C2-00-00-0E instead of forwarding them, so that the power
  exchanges on port A and port B stay separate.
* **Dual-role ports (full design):** the type of disconnect switch for
  each path, and how the role is configured.
* **Availability of optional PDK layers** (10 V LDMOS, MIM option,
  high-resistance poly) on wafer.space runs.

References
----------

.. [PoE-IEEE802.3] IEEE Std 802.3-2022, *IEEE Standard for Ethernet*,
   Clause 33 "Power over Ethernet over 2 pairs" (Types 1 and 2),
   Clause 145 "Power over Ethernet" (Types 3 and 4) and Clause 79
   (link-layer discovery power fields).
   https://standards.ieee.org/ieee/802.3/10422/ . The standard text was not
   accessible while writing this page; values are taken from the summaries,
   the test plan and the data sheets below, which cite the standard's
   tables.

.. [EA-bt] L. Yseboodt and D. Abramson, *Overview of 802.3bt — Power over
   Ethernet standard*, Ethernet Alliance white paper, 2019-12.
   https://ethernetalliance.org/wp-content/uploads/2019/12/WP_EA_Overview8023bt_V2p1_FINAL.pdf

.. [UNH-PSE] University of New Hampshire InterOperability Laboratory,
   Power over Ethernet Consortium, *Clause 33 PSE Parametric Test Suite*,
   version 2.2 (references IEEE Std 802.3-2005 Clause 33).
   https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/CL33_PSE/PSE_Test_Suite_v2.2.pdf

.. [Sifos-PD] Sifos Technologies, *802.3bt PD Conformance Test Suite
   Parameters*, report version 3.7, 2022-11-11.
   https://sifos.com/wp-content/uploads/PDA-604-802.3bt-Conformance-Test-PICS-Coverage.pdf

.. [TPS2372] Texas Instruments, *TPS2372 High-Power PoE PD Interface with
   Automatic MPS and Autoclass*, SLUSCM4B, revised 2018-11.
   https://www.ti.com/lit/ds/symlink/tps2372.pdf

.. [TPS2378] Texas Instruments, *TPS2378 IEEE 802.3at PoE Powered Device
   Controller*, SLVSB99C, revised 2015-07.
   https://www.ti.com/lit/ds/symlink/tps2378.pdf

.. [TPS23753A] Texas Instruments, *TPS23753A IEEE 802.3 PoE Interface and
   Converter Controller with Enhanced ESD Immunity*, SLVS933D, revised
   2020-12. https://www.ti.com/lit/ds/symlink/tps23753a.pdf

.. [TPS23881] Texas Instruments, *TPS23881 Type-4 4-Pair 8-Channel PoE 2
   PSE Controller with SRAM and 200 mΩ RSENSE*, SLVSF02E, revised 2023-05.
   https://www.ti.com/lit/ds/symlink/tps23881.pdf

.. [TPS2388] Texas Instruments, *TPS2388 8-Channel PoE PSE Controller for
   IEEE 802.3at*. https://www.ti.com/lit/ds/symlink/tps2388.pdf

.. [TPS23861] Texas Instruments, *TPS23861 IEEE 802.3at Quad Port Power
   over Ethernet PSE Controller*.
   https://www.ti.com/lit/ds/symlink/tps23861.pdf

.. [PMP7979] Texas Instruments, *PMP7979: 12Vin to 67Vin, 54Vout at 4.8A,
   260W Dual-Phase Boost Reference Design*.
   https://www.ti.com/tool/PMP7979

.. [LT4275] Analog Devices (Linear Technology), *LT4275 LTPoE++/PoE+/PoE PD
   Controller*, data sheet 4275f, linked from the product page.
   https://www.analog.com/en/products/lt4275.html

.. [LTC4269-1] Analog Devices (Linear Technology), *LTC4269-1 IEEE 802.3at
   High Power PD and Synchronous No-Opto Flyback Controller*, product page.
   https://www.analog.com/en/products/ltc4269-1.html

.. [LTC4291] Analog Devices, *LTC4291-1/LTC4292 4-Port IEEE 802.3bt PoE PSE
   Controller*, product page and data sheet.
   https://www.analog.com/en/products/ltc4291-1.html

.. [LTC4279] Analog Devices (Linear Technology), *LTC4279 Single Port
   PoE/PoE+/LTPoE++ PSE Controller*, data sheet 4279fa.
   https://www.analog.com/media/en/technical-documentation/data-sheets/4279fa.pdf

.. [NCP1096] onsemi, *NCP1096 PoE-PD Interface Controller*, data sheet
   NCP1096/D. https://www.onsemi.com/pdf/datasheet/ncp1096-d.pdf

.. [PD70224] Microchip, *PD70224 IdealBridge Dual MOSFET-Bridge Rectifier*,
   data sheet DS00003575D, product page (status: not recommended for new
   designs). https://www.microchip.com/en-us/product/pd70224

.. [PD69208] Microchip, *PD69208M: IEEE 802.3at/bt Type 3, 8 ports, fully
   integrated PSE manager*, product page.
   https://www.microchip.com/en-us/product/pd69208m

.. [Si3474] Skyworks Solutions, *Si3474 Data Sheet: Up to four 802.3bt or
   eight 802.3at Ethernet Port PoE PSE Controllers*, revision 0.5,
   2021-12-03.
   https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-sheets/si3474-datasheet.pdf

.. [ADI-PoE] Analog Devices, *Creating the Power Subsystem for Power over
   Ethernet Designs*, technical article.
   https://www.analog.com/en/resources/technical-articles/creating-the-power-subsystem-for-power-over-ethernet-designs.html

.. [PoE-LLDP] IEEE Std 802.1AB, *Station and Media Access Control
   Connectivity Discovery* (Link Layer Discovery Protocol).
   https://standards.ieee.org/ieee/802.1AB/6047/

.. [PoE-GF180-DRM-2] GlobalFoundries, gf180mcu PDK design manual, section
   2.0 "Scope".
   https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_02.html

.. [PoE-GF180-DRM-14] GlobalFoundries, gf180mcu PDK design manual, section
   14.1 "Chip Operating Conditions".
   https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_14_1.html

.. [PoE-GF180-EP-OX] GlobalFoundries, gf180mcu electrical parameters,
   section 5.4 "Oxide Breakdown Voltage".
   https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs_5_4.html

.. [PoE-GF180-EP-BJT] GlobalFoundries, gf180mcu electrical parameters,
   section 5.8 "Vertical BJT Transistors".
   https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs_5_8.html

.. [PoE-GF180-EP-6] GlobalFoundries, gf180mcu electrical parameters,
   section 6.1B "2000 ohm/sq High Poly Resistor".
   https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs_6_2.html

.. [PoE-GF180-MIM] GlobalFoundries, gf180mcu electrical parameters,
   section 6.2 "MIM Capacitor".
   https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs_6_4.html

.. [PoE-GF180-DRM-4] GlobalFoundries, gf180mcu PDK design manual, section
   4.1 "Drawn layer definition and abbreviation" (lists the deep n-well
   layer). https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_04_1.html

.. [PoE-GF180-DRM-EM] GlobalFoundries, gf180mcu PDK design manual, section
   14.2 "Electro-migration".
   https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_14_2.html

.. [PoE-GF180-LDMOS] GlobalFoundries, gf180mcu PDK design manual, section
   10.12.1 "10V LDNMOS rules".
   https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_10_12_1.html

.. [PoE-GF180-ESD] GlobalFoundries, gf180mcu PDK design manual, section
   14.5.5 "ESD Performance from 5V/6V NMOS transistor" (and the ESD layout
   guidelines in section 14.4).
   https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_14_5_5.html

.. [DosSantos2003] P. M. dos Santos, H. Quaresma, A. P. Silva and
   M. Lança, "Design of high-voltage devices in a fully implanted twin-well
   CMOS process", European Solid-State Device Research Conference
   (ESSDERC), 2003. https://doi.org/10.1109/ESSDERC.2003.1256884

.. [Mitros2000] J. C. Mitros et al., "High-Voltage Drain Extended MOS
   Transistors for 0.18 µm Logic CMOS Process", European Solid-State
   Device Research Conference (ESSDERC), 2000.
   https://doi.org/10.1109/ESSDERC.2000.194793

.. [Pashmineh2016] S. Pashmineh and D. Killat, "A high-voltage driver
   based on stacked low-voltage transistors with minimized on-resistance
   for a buck converter in 65 nm CMOS", IEEE Canadian Conference on
   Electrical and Computer Engineering (CCECE), 2016.
   https://doi.org/10.1109/CCECE.2016.7726692

.. [Mentze2006] E. J. Mentze, H. L. Hess, K. M. Buck and T. G. Windley,
   "A Scalable High-Voltage Output Driver for Low-Voltage CMOS
   Technologies", IEEE Transactions on VLSI Systems, 2006.
   https://doi.org/10.1109/TVLSI.2006.887812

.. [Syroiezhin2023] S. Syroiezhin, R. Weigel and V. Solomko,
   "High-Voltage MOSFET-Based Stacked RF Switch With Extended Bandwidth
   Down to DC", IEEE Solid-State Circuits Letters, 2023.
   https://doi.org/10.1109/LSSC.2023.3268089

.. [Ismail2017] Y. Ismail, H. Lee, S. Pamarti and C.-K. K. Yang, "A 36-V
   49% Efficient Hybrid Charge Pump in Nanometer-Scale Bulk CMOS
   Technology", IEEE Journal of Solid-State Circuits, vol. 52, no. 3,
   2017. https://doi.org/10.1109/JSSC.2016.2636876

.. [Ker2007] M.-D. Ker and S.-L. Chen, "Ultra-High-Voltage Charge Pump
   Circuit in Low-Voltage Bulk CMOS Processes With Polysilicon Diodes",
   IEEE Transactions on Circuits and Systems II, 2007.
   https://doi.org/10.1109/TCSII.2006.882854

.. [Li2019] X. Li et al., "A Regulated Temperature-Insensitive
   High-Voltage Charge Pump in Standard CMOS Process for Micromachined
   Gyroscopes", Sensors, vol. 19, 2019.
   https://doi.org/10.3390/s19194149

.. [ESDA-HBM] ESD Association, *Fundamentals of Electrostatic Discharge,
   Part Five: Device Sensitivity and Testing*.
   https://esda.org/assets/Documents/Fundamentals-of-ESD-Part-5-Device-Sensitivity-and-Testing.pdf

.. [TI-SLUA736] D. V. Comiskey, *Lightning Surge Considerations for PoE
   Powered Devices*, Texas Instruments application report SLUA736,
   2015-03. https://www.ti.com/lit/pdf/slua736

.. [PoE-Iso] J. Potterf, *Isolation Proposals*, contribution to the IEEE
   P802.3da task force, revised 2025-03-13 (quotes the IEEE 802.3-2022
   Annex J isolation tests).
   https://www.ieee802.org/3/da/public/032025/SPMD_Potterf_Isolation_Proposals_Expanded_AllMarkup_v03.pdf

.. [PoE-GF180-EP-5] GlobalFoundries, gf180mcu electrical parameters,
   section 5.5 "Junction Breakdown Voltage".
   https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs_5_5.html

.. [PoE-GF180-EP-8] GlobalFoundries, gf180mcu electrical parameters,
   section 8 "High Voltage LDMOS Transistor (10.0V)".
   https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs_8_1.html
