.. _usbpd-start-up:

Power at start-up
=================

Before any :term:`USB Power Delivery` negotiation, a USB Type-C source
makes power available to evampire as a :term:`sink` at one of the
:term:`USB Type-C Current` levels.

A board that takes all its power from USB Type-C starts from nothing
(:ref:`req-power-control`). Until its processor is running, only the
resistor advertisement (:doc:`resistor-advertisement`) and the unpowered
attach (:ref:`usbpd-dead-battery`) are available. Whether this power is
enough depends on how much evampire and the rest of the board need, which
is an open question of the requirements (:ref:`requirements-open-questions`).

Default supply and current levels
---------------------------------

Before a USB Power Delivery contract, the source supplies VBUS at
vSafe5V, 4.75 V to 5.5 V at its receptacle (:pd:`Table 4.9`;
:typec:`Section 4.6.2.1`). The current the sink may draw is set by the
source's :term:`Rp` and, at the default level, by the USB specification the
sink follows (:typec:`Table 4-20`). The power at each level is the product
of the two:

.. math::

   P_\text{min} = V_\text{min} \times I_\text{max}

   P_\text{max} = V_\text{max} \times I_\text{max}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`P_\text{min}`, :math:`P_\text{max}`
     - Lowest and highest power available at the source's receptacle
     - W
   * - :math:`V_\text{min}`, :math:`V_\text{max}`
     - Lowest and highest voltage of vSafe5V, 4.75 V and 5.5 V
     - V
   * - :math:`I_\text{max}`
     - Highest current the sink may draw at that level
     - A

The two values bound the power at the source's receptacle when the sink
draws its full current. The cable lowers the voltage at the sink by up to
500 mV on VBUS and 250 mV on ground at the cable's rated current
(:typec:`Section 4.4.1`). The losses of the board's own converters are not
included (:ref:`conv-start-up`).

For example, at the 3.0 A level :math:`P_\text{min} = 4.75\ \text{V} \times
3.0\ \text{A} = 14.3\ \text{W}` and :math:`P_\text{max} = 5.5\ \text{V}
\times 3.0\ \text{A} = 16.5\ \text{W}`. :numref:`tab-usbpd-start-up-power`
gives every level.

.. list-table:: Power available at each level before a USB Power Delivery contract
   :name: tab-usbpd-start-up-power
   :header-rows: 1
   :widths: 36 16 16 16 16

   * - Level
     - Current (A)
     - Min (W)
     - Max (W)
     - Nominal (W)
   * - Default, USB 2.0 device not yet configured
     - 0.1
     - 0.475
     - 0.55
     - none
   * - Default, USB 2.0
     - 0.5
     - 2.38
     - 2.75
     - 2.5
   * - Default, USB 3.2 single-lane
     - 0.9
     - 4.28
     - 4.95
     - 4.5
   * - Default, USB 3.2 dual-lane
     - 1.5
     - 7.13
     - 8.25
     - 7.5
   * - 1.5 A
     - 1.5
     - 7.13
     - 8.25
     - 7.5
   * - 3.0 A
     - 3.0
     - 14.3
     - 16.5
     - 15

The nominal power is the specification's power equivalent at 5 V
(:typec:`Table 4-20`). The first row is the one unit load of 100 mA that a
USB 2.0 device may draw until the host configures it, and the second the
five unit loads it may draw afterwards (:std:`USB 2.0 Section 7.2.1 <usb2>`).

evampire's default level
------------------------

The default level depends on the sink as well as the source. evampire's
data connection is a USB 2.0 full-speed device (:ref:`req-usb-serial`), so
the USB 3.2 rows do not apply to it. Attached to a computer's port that
advertises the default level, it may draw 100 mA until the computer
configures its USB serial port, and 500 mA after that.

A dedicated charger has no USB host. The specification lets a sink that has
no USB data function, a *Power Sinking Device*, draw up to 500 mA at the
default level (:typec:`Section 4.6.2.1`). Chargers that offer more advertise
1.5 A or 3.0 A with Rp.

To use the 1.5 A or 3.0 A level, the sink measures the CC voltage, which
needs an Rd within ± 10 % (:typec:`Table 4-28`; :ref:`usbpd-sink-thresholds`).
A sink starts at the default level and moves up when it reads a higher one.
It must come back down within tSinkAdj, at most 60 ms, if the source lowers
its advertisement (:typec:`Section 4.5.2.3`, :typec:`Table 4-32`).

Start-up sequence
-----------------

:numref:`tab-usbpd-start-up-steps` follows a board without power from the
moment it is plugged into a charger, and :numref:`fig-usbpd-start-up`
draws the same steps against time. The attach steps are described on
:ref:`usbpd-attach-sequence`.

.. list-table:: Power available to an unpowered board as it starts
   :name: tab-usbpd-start-up-steps
   :header-rows: 1
   :widths: 8 52 40

   * - Step
     - What happens
     - Current the board may draw
   * - 1
     - The board presents its unpowered Rd. The charger sees it for
       tCCDebounce, 100 ms to 200 ms (:typec:`Table 4-34`).
     - none
   * - 2
     - The charger turns VBUS on, reaching vSafe5V within tVBUSON, 275 ms
       (:typec:`Table 4-32`).
     - The default level
   * - 3
     - The board switches to an Rd within ± 10 % and reads the advertised
       level (:ref:`usbpd-sink-thresholds`).
     - Up to 1.5 A or 3.0 A, as advertised
   * - 4
     - The processor runs and carries out the USB Power Delivery
       negotiation (:ref:`req-power-control`, :ref:`usbpd-negotiation`).
     - The current of the contract (:ref:`usbpd-power-levels`)

.. wavedrom::
   :caption: An unpowered board plugged into a charger, with the current it
            may draw at each step of :numref:`tab-usbpd-start-up-steps`,
            schematic and not to scale; tCCDebounce is 100 ms to 200 ms
            and tVBUSON at most 275 ms.
   :name: fig-usbpd-start-up
   :alt: Timing diagram. The charger presents Rp throughout. In step 1 the
         board presents its unpowered Rd and the charger waits tCCDebounce,
         100 to 200 ms; the board may draw no current. In step 2 the charger
         turns VBUS on to vSafe5V within tVBUSON, at most 275 ms, and the
         board may draw the default level. In step 3 the board switches to
         an Rd within 10 % and may draw 1.5 A or 3.0 A as advertised. In
         step 4 the USB Power Delivery negotiation runs, and the board may
         then draw the contract current.

   {"signal": [
     {"name": "step", "wave": "=...=....=..=.=.", "data": ["1", "2", "3", "4", "contract"]},
     {"name": "charger CC", "wave": "=...............", "data": ["Rp"]},
     {"name": "timer", "wave": "=...=..x........", "data": ["tCCDebounce", "tVBUSON"]},
     {"name": "VBUS", "wave": "0......=......=.", "data": ["vSafe5V", "contract"]},
     {"name": "messages", "wave": "z...........=.z.", "data": ["negotiation"]},
     {"name": "board Rd", "wave": "=........=......", "data": ["unpowered Rd (± 20 % or clamp)", "Rd ± 10 %"]},
     {"name": "current", "wave": "=......=.=....=.", "data": ["none", "default", "1.5 or 3.0 A", "contract"]}
   ],
   "config": {"hscale": 1}}

An unpowered Rd, a resistor within ± 20 % or a voltage clamp, cannot tell
the levels apart (:typec:`Table 4-28`). Until step 3, the board can count
only on the default level. Whether the start-up sequencer or the processor
carries out step 3 is listed below.

Source_Capabilities timing
--------------------------

A USB Power Delivery source sends its first Source_Capabilities message
within tFirstSourceCap, 250 ms, of VBUS reaching vSafe5V
(:pd:`Section 7.31.3.3`, :pd:`Table 7.10`). It repeats it every
tTypeCSendSourceCap, 100 ms to 200 ms, until the sink acknowledges one with
:term:`GoodCRC`. A source may give up after nCapsCount messages and then
send one only every tTypeCSendSourceCapIdle, up to 5 s
(:pd:`Section 7.32.4`; :pd:`Table 7.10`, :pd:`Table 7.12`). The time before a source may give
up is:

.. math::

   t_\text{caps} = n_\text{CapsCount} \times t_\text{TypeCSendSourceCap}

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`t_\text{caps}`
     - Time from the first Source_Capabilities message until the source may
       stop repeating it
     - s
   * - :math:`n_\text{CapsCount}`
     - Number of unanswered messages after which it may stop, 50
     - none
   * - :math:`t_\text{TypeCSendSourceCap}`
     - Interval between the messages, 100 ms to 200 ms
     - s

With 50 messages at 0.10 s to 0.20 s apart, :math:`t_\text{caps}` is 5.0 s to
10 s. The source counts from its first message, about 0.25 s after VBUS is
on.

A sink that has seen no Source_Capabilities message may send
:term:`Hard Reset` to make the source start again, or may carry on at the
USB Type-C Current level (:pd:`Section 7.31.3.2`). A Hard Reset turns VBUS
off for a time, so a board powered only from VBUS loses its power
(:pd:`Section 4.4`; :ref:`usbpd-hard-reset`).

Open questions
--------------

* Whether evampire, which has a USB serial port, may draw the 500 mA of a
  Power Sinking Device from a charger at the default level, or only the
  100 mA of an unconfigured USB 2.0 device.
* Whether the start-up sequencer reads the USB Type-C Current level
  (step 3 of :numref:`tab-usbpd-start-up-steps`) before the processor runs,
  or the processor does.
