Buck-boost and isolated converters
==================================

This page explains converters whose output can be above or below their
input. Several of evampire's conversions need one, because their input and
output ranges cross (:doc:`arrangement`). It covers the inverting
buck-boost converter, the four-switch buck-boost converter used in most USB
Power Delivery sources, and the isolated flyback converter used in many
Power over Ethernet powered devices.

The inverting buck-boost converter
----------------------------------

The basic :wikipedia:`buck-boost converter <Buck%E2%80%93boost_converter>`
has one switch, one inductor and one diode. During the on time the switch
connects the inductor across the input and its current rises. During the off
time the inductor discharges through the diode into the output capacitor.
Because the inductor current then flows *out of* the output node, the output
is negative. Volt-second balance (:doc:`buck`) gives

.. math::

   V_\text{in} \, D = -V_\text{out} \, (1 - D),
   \qquad
   \frac{V_\text{out}}{V_\text{in}} = -\frac{D}{1 - D}

with the symbols in :numref:`tab-conv-sym-bb`, so the magnitude of the
output is below the input for :math:`D < 0.5` and above it for
:math:`D > 0.5`.

.. list-table:: Symbols for the buck-boost and flyback converters
   :name: tab-conv-sym-bb
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`V_\text{in}`, :math:`V_\text{out}`
     - Input and output voltage
     - V
   * - :math:`D`
     - Duty cycle
     - fraction
   * - :math:`V_\text{stress}`
     - Highest voltage across a switch while it is off
     - V
   * - :math:`N_p`, :math:`N_s`
     - Turns on the primary and secondary windings of a transformer
     - none
   * - :math:`M`
     - Conversion ratio, :math:`V_\text{out} / V_\text{in}`
     - none

Two properties keep it out of evampire's power path. Its output is negative
with respect to its input, and USB and Power over Ethernet both need a
positive supply on a shared ground. And its switch must block the sum of the
input and output voltages:

.. math::

   V_\text{stress} = V_\text{in} + |V_\text{out}| = 57 + 48 = 105 \ \text{V}

for a 57 V Power over Ethernet input and a 48 V USB output, nearly twice the
stress of the four-switch converter below.

The four-switch buck-boost converter
------------------------------------

.. graphviz:: four-switch.dot
   :name: fig-conv-four-switch
   :caption: Power stage of a four-switch buck-boost converter.
   :alt: Schematic: the input connects through S1 to node A; S2 connects
         node A to ground; the inductor L connects node A to node B; S3
         connects node B to ground; S4 connects node B to the output, where
         the capacitor C and the load connect to ground. S1 and S2 are
         labelled buck half bridge, S3 and S4 boost half bridge.
   :align: center

The four-switch buck-boost converter (:numref:`fig-conv-four-switch`) joins
a buck half bridge (S1 and S2, as in :doc:`buck`) and a boost half bridge
(S3 and S4, as in :doc:`boost`) with one inductor. Its output is positive,
and each switch only blocks its own side's voltage. It works in three
regions, chosen from the conversion ratio
:math:`M = V_\text{out} / V_\text{in}`:

Buck region, :math:`M` below 1
   S4 stays on and S3 off, so node B is the output. S1 and S2 switch as a
   buck converter with :math:`D_\text{buck} = M`.
Boost region, :math:`M` above 1
   S1 stays on and S2 off, so node A is the input. S3 and S4 switch as a
   boost converter with :math:`D_\text{boost} = 1 - 1/M`.
Buck-boost region, :math:`M` near 1
   Both half bridges switch, because neither alone can reach a ratio of
   exactly 1 with the duty-cycle limits of real switches. Controllers use
   different schemes here. The LT8390, for example, changes from peak
   buck to peak boost current control at a ratio of 0.98 and back at 1.02
   [CONV-LT8390]_ (Operation).

[CONV-SLVA535]_ (Equations 1 and 2) gives the duty cycles with the
efficiency included. :numref:`tab-conv-four-switch-modes` works out the
region for the "Ethernet in, USB out" mode (:ref:`power-modes`), from the
powered device input range to three USB output voltages.

.. list-table:: Four-switch buck-boost region from a Power over Ethernet input to USB outputs
   :name: tab-conv-four-switch-modes
   :header-rows: 1
   :widths: 18 18 18 22 24

   * - Input (V)
     - Output (V)
     - Ratio M
     - Region
     - Duty cycle
   * - 37
     - 5
     - 0.135
     - buck
     - 0.135
   * - 57
     - 5
     - 0.088
     - buck
     - 0.088
   * - 37
     - 20
     - 0.541
     - buck
     - 0.541
   * - 57
     - 20
     - 0.351
     - buck
     - 0.351
   * - 37
     - 48
     - 1.297
     - boost
     - 0.229
   * - 57
     - 48
     - 0.842
     - buck
     - 0.842

A 48 V USB output from a Power over Ethernet input can need either region,
so a single step-down converter cannot cover it.

The four-switch converter is symmetric: run with power flowing from the
output side to the input side, the boost half bridge acts as a buck and the
buck half bridge as a boost. A controller that supports this is
*bidirectional*. :doc:`arrangement` uses this to share one converter between
operating modes.

Commercial four-switch buck-boost controllers
---------------------------------------------

For reference, :numref:`tab-conv-four-switch-parts` lists four-switch
buck-boost controllers and one converter with built-in switches. They show
the voltage ranges and frequencies that such designs reach; they are not
evampire values.

.. list-table:: Four-switch buck-boost controllers and converters
   :name: tab-conv-four-switch-parts
   :header-rows: 1
   :widths: 28 24 24 24

   * - Part
     - Input (V)
     - Output (V)
     - Frequency (kHz)
   * - LM5176 [CONV-LM5176]_
     - 4.2 to 55
     - 0.8 to 55
     - 100 to 600
   * - LM5177 [CONV-LM5177]_
     - 3.5 to 60
     - 3.3 to 60
     - 100 to 600
   * - LT8390 [CONV-LT8390]_
     - 4 to 60
     - 0 to 60
     - 150 to 650
   * - LTC3780 [CONV-LTC3780]_
     - 4 to 36
     - 0.8 to 30
     - 200 to 400
   * - TPS55289 [CONV-TPS55289]_
     - 3 to 30
     - 0.8 to 22
     - 200 to 2200

Sources: LM5176 Features and Section 6.3; LM5177 Features and Section 5.3;
LT8390 Features; LTC3780 Features; TPS55289 Features.

* The LM5176 uses current-mode control and has 2 A gate drivers; USB
  Power Delivery is one of its listed applications.
* The LM5177 is bidirectional and drives its transistors from a 5 V
  supply; Power over Ethernet routers are one of its listed applications.
* The LT8390 uses peak buck and peak boost current-mode control and spreads
  its switching frequency.
* The LTC3780 controls the valley current in its buck region and the peak
  current in its boost region [CONV-LTC3780]_ (Applications Information).
* The TPS55289 has its switches on chip, sets its output over I²C in
  10 mV steps, and is made for USB Power Delivery programmable supplies.

Isolated converters
-------------------

An isolated converter passes power through a
:wikipedia:`transformer <Transformer>`, so that its output has no
conducting path to its input (:wikipedia:`galvanic isolation
<Galvanic_isolation>`). The simplest is the
:wikipedia:`flyback converter <Flyback_converter>`: an inverting buck-boost
converter whose inductor has a second winding. The switch charges the
transformer's magnetising inductance from the input; when it opens, the
energy leaves through the secondary winding and a rectifier. With turns
ratio :math:`N_p / N_s`,

.. math::

   \frac{V_\text{out}}{V_\text{in}} = \frac{N_s}{N_p} \, \frac{D}{1 - D},
   \qquad
   V_\text{stress} = V_\text{in} + \frac{N_p}{N_s} \, V_\text{out}

(symbols in :numref:`tab-conv-sym-bb`), where the stress neglects the extra
spike caused by the transformer's leakage inductance. For an illustrative
12 V output with :math:`N_p / N_s = 4`, the duty cycle is 0.565 at 37 V in and
0.457 at 57 V in, and the switch must block at least
:math:`57 + 4 \times 12 = 105` V.

Many powered devices use a flyback converter because the Power over
Ethernet standard asks for the cable to be isolated from the rest of the
equipment. :doc:`../poe` describes the isolation requirement and when a
non-isolated converter is allowed. For reference, the TPS23753A combines a
powered device interface with a controller "optimized for isolated
converters" and gives a flyback converter as its typical application
[CONV-TPS23753A]_ (Features, Section 9.2). Its controller uses peak
current-mode control with a maximum duty cycle of 76 % to 81 %
[CONV-TPS23753A]_ (Section 7.5).

Isolated and non-isolated input converters both remain options for
evampire. Three routes to the isolation are explored: external parts (a
transformer and an isolated feedback path), a second die on the cable side
(a custom gf180mcu die or a commercial part), and a barrier on the evampire
die itself. :doc:`../poe` discusses the requirement behind them, including
its effect on the power sourcing equipment port, whose output also goes onto
an Ethernet cable.

Other step-up and step-down topologies
--------------------------------------

The :wikipedia:`SEPIC <SEPIC>` and the :wikipedia:`Ćuk converter
<%C4%86uk_converter>` also step up or down with one switch, using a
coupling capacitor and a second inductor (or coupled windings). The SEPIC
output is positive; the Ćuk output is negative. Both put the sum of input
and output voltages across the switch, as the inverting buck-boost does
[CONV-ERICKSON]_ (Chapter 6). For reference, the LM5155 boost controller
also lists SEPIC and flyback applications [CONV-LM5155]_ (Features).
