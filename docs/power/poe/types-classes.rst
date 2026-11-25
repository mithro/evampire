.. _poe-types-classes:

Types, classes and the cable
============================

This page lists the four types and nine classes of Power over Ethernet, the
power each class gives at each end of the cable, and how the cable's
resistance links the two.

The four types
--------------

A :term:`type <Type (Power over Ethernet)>` is a set of rules that power
sourcing equipment or a powered device follows. :numref:`tab-poe-types`
lists them. Types 1 and 2 are specified in :clause:`33` and Types 3 and 4
in :clause:`145`, which also covers how they work with Types 1 and 2.

.. list-table:: The four types
   :name: tab-poe-types
   :header-rows: 1
   :widths: 15 25 25 35

   * - Type
     - Defined in
     - Highest class
     - Pair sets powered
   * - 1
     - :clause:`33`
     - 3
     - 1
   * - 2
     - :clause:`33`
     - 4
     - 1
   * - 3
     - :clause:`145`
     - 6
     - 1 or 2
   * - 4
     - :clause:`145`
     - 8
     - 1 or 2

The highest classes come from :clause:`Table 145-11 <145>` and
:clause:`Table 33-7 <33>`, the pair sets from :clause:`145.1.3`. A Type 1
device that does no classification counts as class 0, which Types 3 and 4
treat as class 3 (:clause:`145.2.8`).

Class power
-----------

A :term:`class` is a number that stands for a maximum power. The powered
device asks for a class during classification (:doc:`sequence`), and the
power sourcing equipment *assigns* a class, which may be lower than the one
asked for (:ref:`poe-demotion`). :numref:`tab-poe-classes` gives the power of each class at both
ends of the cable.

.. list-table:: The power of each class
   :name: tab-poe-classes
   :header-rows: 1
   :widths: 16 28 28 28

   * - Class
     - At powered device (W)
     - At power sourcing equipment (W)
     - Peak at powered device (W)
   * - 0
     - 13
     - 15.4
     - 14.4
   * - 1
     - 3.84
     - 4
     - 5
   * - 2
     - 6.49
     - 6.7
     - 8.36
   * - 3
     - 13
     - 14
     - 14.4
   * - 4
     - 25.5
     - 30
     - 28.3
   * - 5
     - 40
     - 45
     - 42
   * - 6
     - 51
     - 60
     - 53.5
   * - 7
     - 62
     - 75
     - 65.1
   * - 8
     - 71.3
     - 90
     - 74.9

:numref:`tab-poe-types` gives the type each class needs. The powers at
the powered device come from :clause:`Table 145-29 <145>`
(items 8 and 10). The powers at the power sourcing equipment come from
:clause:`Table 145-11 <145>`, also summarised in [POE-EA-BT]_ (Tables 6, 7
and 14). Class 0 is from :clause:`Table 33-7 <33>` and
:clause:`Table 33-18 <33>`. Under the :clause:`33` rules, power sourcing
equipment supplies 7.00 W for class 2 and 15.4 W for class 3, because it
allows for a longer cable (:clause:`Table 33-7 <33>`).

A powered device may draw more than its class power, up to the peak power,
for no longer than 50 ms at a time and for no more than 5 % of a 1 s window
(:clause:`145.3.8.4`, with the 50 ms from :clause:`Table 145-16 <145>`).

.. _poe-cable-loss:

Power lost in the cable
-----------------------

The power at the power sourcing equipment and the power at the powered
device differ by the power lost in the cable. The calculation below shows
where that difference comes from. It treats the cable as one resistance in
the current loop, out on one pair and back on another, and assumes the
power sourcing equipment delivers its full power at its lowest voltage:

.. math::

   I &= \frac{P_\text{PSE}}{V_\text{PSE}} \\
   P_\text{cable} &= I^2 \times R_\text{loop} \\
   P_\text{PD} &= P_\text{PSE} - P_\text{cable}

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`P_\text{PSE}`
     - Power at the power sourcing equipment output
     - W
   * - :math:`V_\text{PSE}`
     - Lowest output voltage of the type (:numref:`tab-poe-pse-voltage`)
     - V
   * - :math:`I`
     - Current in the loop
     - A
   * - :math:`R_\text{loop}`
     - Highest loop resistance of the cable
     - Ω
   * - :math:`P_\text{cable}`
     - Power lost in the cable
     - W
   * - :math:`P_\text{PD}`
     - Power left at the powered device
     - W

The highest loop resistance is 20 Ω for Type 1 and 12.5 Ω for one pair set
of Types 2 to 4 (:clause:`Table 33-1 <33>`, :clause:`Table 145-1 <145>`).
With both pair sets sharing the current it is half that, 6.25 Ω
(:clause:`145.1.3`). The model holds when the two pair sets of a 4-pair
link carry equal currents; the standard limits the current of each pair set
separately to cover unequal currents (:clause:`145.2.10.6.1`).

For Type 4 with both pair sets:

.. math::

   I &= \frac{90\ \text{W}}{52\ \text{V}} = 1.73\ \text{A} \\
   P_\text{cable} &= (1.73\ \text{A})^2 \times 6.25\ \Omega = 18.7\ \text{W} \\
   P_\text{PD} &= 90\ \text{W} - 18.7\ \text{W} = 71.3\ \text{W}

:numref:`tab-poe-cable-loss` gives the result for each type at its highest
power. Each result matches the class power in :numref:`tab-poe-classes`, so
the class powers already include the worst-case cable.

.. list-table:: Cable loss at full power and the lowest voltage
   :name: tab-poe-cable-loss
   :header-rows: 1
   :widths: 20 20 20 20 20

   * - Case
     - :math:`P_\text{PSE}` (W)
     - :math:`R_\text{loop}` (Ω)
     - :math:`P_\text{cable}` (W)
     - :math:`P_\text{PD}` (W)
   * - Type 1
     - 15.4
     - 20
     - 2.45
     - 13.0
   * - Type 2
     - 30
     - 12.5
     - 4.50
     - 25.5
   * - Type 3
     - 60
     - 6.25
     - 9.00
     - 51.0
   * - Type 4
     - 90
     - 6.25
     - 18.7
     - 71.3

The voltages are those of :numref:`tab-poe-pse-voltage`: 44 V, 50 V, 50 V
and 52 V. A shorter or thicker cable loses less.

.. _poe-lowest-voltage:

Lowest voltage at the powered device
------------------------------------

The same model gives the lowest voltage at which the powered device must
still work. The powered device draws :math:`P_\text{PD}` at a voltage
:math:`V_\text{PD}`, and the cable drops :math:`V_\text{PSE} -
V_\text{PD}`. Eliminating the current gives a quadratic equation whose
higher root is the operating point:

.. math::

   P_\text{PD} &= V_\text{PD} \times I \\
   V_\text{PSE} - V_\text{PD} &= I \times R_\text{loop} \\
   D &= V_\text{PSE}^2 - 4 \times R_\text{loop} \times P_\text{PD} \\
   V_\text{PD} &= \frac{V_\text{PSE} + \sqrt{D}}{2}

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`V_\text{PD}`
     - Voltage at the powered device input
     - V
   * - :math:`P_\text{PD}`
     - Power of the class at the powered device (:numref:`tab-poe-classes`)
     - W
   * - :math:`D`
     - Discriminant of the quadratic equation
     - V²
   * - :math:`V_\text{PSE}`, :math:`R_\text{loop}`, :math:`I`
     - As in the cable loss model above
     - V, Ω, A

For class 8, with 52 V and 6.25 Ω:

.. math::

   D &= (52\ \text{V})^2 - 4 \times 6.25\ \Omega \times 71.3\ \text{W} \\
   &= 2704\ \text{V}^2 - 1782.5\ \text{V}^2 = 921.5\ \text{V}^2 \\
   V_\text{PD} &= \frac{52\ \text{V} + 30.36\ \text{V}}{2} = 41.2\ \text{V}

:numref:`tab-poe-lowest-voltage` gives the lowest voltage that the standard
requires each class of powered device to accept
(:clause:`Table 145-29 <145>`, item 1), next to the model. The standard's
values are the model's results rounded down to 0.1 V. For classes 4 to 8
the model uses the lowest voltage and the loop resistance of the lowest type
that can assign the class. For classes 1 to 3 the values match the model
with 44 V and 12.5 Ω.

.. list-table:: Lowest voltage at the powered device
   :name: tab-poe-lowest-voltage
   :header-rows: 1
   :widths: 16 21 21 21 21

   * - Class
     - :math:`V_\text{PSE}` (V)
     - :math:`R_\text{loop}` (Ω)
     - Model (V)
     - Standard (V)
   * - 1
     - 44
     - 12.5
     - 42.88
     - 42.8
   * - 2
     - 44
     - 12.5
     - 42.07
     - 42
   * - 3
     - 44
     - 12.5
     - 39.93
     - 39.9
   * - 4
     - 50
     - 12.5
     - 42.50
     - 42.5
   * - 5
     - 50
     - 6.25
     - 44.37
     - 44.3
   * - 6
     - 50
     - 6.25
     - 42.50
     - 42.5
   * - 7
     - 52
     - 6.25
     - 42.99
     - 42.9
   * - 8
     - 52
     - 6.25
     - 41.18
     - 41.1

Under the :clause:`33` rules, a Type 1 powered device must work from 37 V
and a Type 2 powered device from 42.5 V (:clause:`Table 33-18 <33>`). The
model gives 36.97 V for Type 1 (44 V, 20 Ω, 13 W) and 42.50 V for Type 2.
All powered devices must accept up to 57 V.

The lowest voltage sets the input range of the powered device's input
converter, from about 37 V to 57 V
(:doc:`../converters/index`).

Open questions
--------------

* The highest type and class that the board supports on each port
  (:ref:`requirements-open-questions`).
