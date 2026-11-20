The analogue front end on gf180mcu
==================================

This page lists the electrical requirements of a full-speed device's D+ and
D− connection from the USB 2.0 specification [USBSER-USB2]_, and compares
them with the standard I/O cells of the gf180mcu process. Where no standard
cell meets a requirement, it describes the custom options.

:numref:`fig-usbser-frontend` shows the blocks of the front end for one
port.

.. _fig-usbser-frontend:

.. graphviz:: analogue/frontend.dot
   :caption: The analogue front end of one USB port, between the digital
             logic and the D+, D− and VBUS pins.
   :alt: Block diagram: the digital logic drives a pull-up switch and a
         full-speed driver, which connect to the D+ and D− pins; the pins
         feed a differential receiver and single-ended receivers with an
         SE0 filter, which report to the digital logic; a VBUS comparator
         reports whether VBUS is present.
   :align: center

The full-speed driver
---------------------

:numref:`tab-usbser-driver` lists the driver requirements.

.. list-table:: Full-speed driver requirements ([USBSER-USB2]_ section
   7.1.1, section 7.1.2.1, Table 7‑7, Table 7‑9)
   :name: tab-usbser-driver
   :header-rows: 1
   :widths: 40 15 15 15 15

   * - Parameter
     - Symbol
     - Minimum
     - Maximum
     - Unit
   * - Output low voltage, 1.5 kΩ load to 3.6 V
     - VOL
     - 0.0
     - 0.3
     - V
   * - Output high voltage, 15 kΩ load to ground
     - VOH
     - 2.8
     - 3.6
     - V
   * - Crossover voltage of D+ and D−
     - VCRS
     - 1.3
     - 2.0
     - V
   * - Rise and fall time, 10 % to 90 %, 50 pF load
     - TFR, TFF
     - 4
     - 20
     - ns
   * - Rise time divided by fall time
     - TFRFM
     - 90
     - 111.11
     - %
   * - Output impedance of each driver, series resistor included
     - ZDRV
     - 28
     - 44
     - Ω

The driver also has to:

* switch off both outputs (tri-state) between packets, because the same two
  wires carry both directions ([USBSER-USB2]_ section 7.1.1);
* never drive both lines high at once (SE1);
* change monotonically, with its edge rate controlled to limit radio
  emissions ([USBSER-USB2]_ section 7.1.1, section 7.1.2.1);
* survive the stresses of :ref:`usbser-protection`.

The specification shows the impedance made of a CMOS output stage with a
lower impedance plus an external series resistor *RS*
([USBSER-USB2]_ section 7.1.1.1, Figure 7‑3).

A driver that is only a resistance charging the 50 pF test load gives an
edge of:

.. math::

   t_{10\text{–}90} = \ln 9 \cdot Z_\text{DRV} \cdot C_\text{L}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`t_{10\text{–}90}`
     - Time to move from 10 % to 90 % of the swing
     - ns
   * - :math:`Z_\text{DRV}`
     - Driver output impedance, 28 Ω to 44 Ω
     - Ω
   * - :math:`C_\text{L}`
     - Test load, 50 pF ([USBSER-USB2]_ Figure 7‑9)
     - pF

At 28 Ω, :math:`t_{10\text{–}90} = 2.197 \times 28\ \Omega \times
50\ \text{pF} = 3.08\ \text{ns}`, below the 4 ns minimum; at 44 Ω it is
4.83 ns. A driver at the low end of the impedance range therefore needs its
own slew-rate control, which the specification requires in any case.

The receivers
-------------

A full-speed device has three receivers ([USBSER-USB2]_ section 7.1.4.1,
Figure 7‑24):

* A *differential receiver*, which decides J or K. It must resolve a
  difference of 200 mV (*VDI*) with both inputs anywhere from 0.8 V to
  2.5 V (*VCM*).
* Two *single-ended receivers*, one per line, with a switching threshold
  between 0.8 V and 2.0 V, recommended with
  :wikipedia:`hysteresis <Schmitt_trigger>`. Together they detect SE0.
* The SE0 decision needs a filter: both lines can be low together for up to
  14 ns during a normal transition (:doc:`timing`).

Each line, without its pull-up or pull-down, must present more than
300 kΩ (*ZINP*). An upstream port with a detachable cable may have at most
100 pF on D+ or D−, of which up to 75 pF at the transceiver and connector,
and D+ and D− must match within 10 % ([USBSER-USB2]_ section 7.1.6.1,
Table 7‑7).

The pull-up resistor
--------------------

The device announces itself with 1.5 kΩ ± 5 % from D+ to a supply of
3.0 V to 3.6 V (*RPU*, *VTERM*). It must be able to pull D+ from 0 V to
2.0 V within 2.5 µs, and it must not supply current when VBUS is absent
([USBSER-USB2]_ section 7.1.5.1, Table 7‑7). With the host's 15 kΩ ± 5 %
pull-down, the idle voltage on D+ is:

.. math::

   V_\text{D+} = V_\text{TERM} \cdot \frac{R_\text{PD}}{R_\text{PU} + R_\text{PD}}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`V_\text{D+}`
     - Voltage on D+ when nobody drives
     - V
   * - :math:`V_\text{TERM}`
     - Pull-up supply, 3.0 V to 3.6 V
     - V
   * - :math:`R_\text{PU}`
     - Device pull-up, 1.425 kΩ to 1.575 kΩ
     - kΩ
   * - :math:`R_\text{PD}`
     - Host pull-down, 14.25 kΩ to 15.75 kΩ
     - kΩ

In the worst case, 3.0 V, 1.575 kΩ and 14.25 kΩ, this gives
:math:`3.0\ \text{V} \times 14.25 / 15.825 = 2.70\ \text{V}`, equal to the
2.7 V minimum idle level *VIHZ* ([USBSER-USB2]_ Table 7‑7). Any switch in
series with the resistor counts as part of *RPU*, so its resistance comes
out of the ± 5 % tolerance.

VBUS sensing
------------

Because the pull-up must be off when VBUS is absent, the device needs to
know whether VBUS is present. The specification gives 4.01 V as the level
at which VBUS is valid for the attach timing
([USBSER-USB2]_ section 7.1.7.3). On a USB Type-C port VBUS can be far
higher after a USB Power Delivery agreement, and the sensing input has to
withstand the highest VBUS the board allows.

evampire already measures the voltage of every power port
(:ref:`requirements`), and the same measurement can supply the "VBUS
present" decision. :doc:`usb-pd-roles` describes what
happens when VBUS changes or when evampire itself supplies VBUS.

.. _usbser-protection:

Protection: short circuits and electrostatic discharge
------------------------------------------------------

USB 2.0 asks a transceiver to withstand ([USBSER-USB2]_ section 7.1.1,
Figure 7‑2):

* a continuous short of D+ or D− to VBUS, ground, the other data line or the
  cable shield, for at least 24 hours, while transmitting half the time, at
  VBUS up to 5.25 V;
* a continuous waveform between 4.6 V and −1.0 V at 6 MHz with 4 ns to
  20 ns edges, from a 39 Ω source.

In the USB Type-C receptacle, Dp1 and Dn1 sit next to CC1 and SBU1, and Dp2
and Dn2 next to CC2 and SBU2 (:typec:`Table 3-4`). A short between
neighbouring contacts can therefore also bring the CC voltage, up to 5.5 V
when it carries VCONN, onto a data line. A short from VBUS above 5.25 V,
which USB Power Delivery allows, goes beyond the USB 2.0 requirement; the
analysis of such shorts for the CC pins on :doc:`/power/usb-pd` applies to
the data pins in the same way.

If the pad's output stage is supplied from 3.3 V, a short to 5.25 V
forward-biases the diode from the pad to its supply. The current is then
limited only by the series resistance:

.. math::

   I_\text{short} = \frac{V_\text{BUS} - V_\text{DD} - V_\text{D}}{R_\text{S}}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`I_\text{short}`
     - Current through the pad diode into the 3.3 V supply
     - mA
   * - :math:`V_\text{BUS}`
     - Short-circuit voltage, 5.25 V ([USBSER-USB2]_ section 7.1.1)
     - V
   * - :math:`V_\text{DD}`
     - Pad supply, 3.3 V (assumption)
     - V
   * - :math:`V_\text{D}`
     - Diode forward voltage, 0.6 V (assumption)
     - V
   * - :math:`R_\text{S}`
     - Total series resistance, 28 Ω to 44 Ω (*ZDRV*)
     - Ω

This gives :math:`(5.25 - 3.3 - 0.6)\ \text{V} / 44\ \Omega = 31\ \text{mA}`
to :math:`1.35\ \text{V} / 28\ \Omega = 48\ \text{mA}`, continuously for
24 hours. The pad, its diode and the 3.3 V supply all have to accept this
current, or the pad has to block it, for example with an output stage whose
wells follow the higher of the pad and supply voltages.

Electrostatic discharge reaches the connector pins from people and cables.
The gf180mcu I/O library targets 2000 V human body model, 200 V machine
model and 500 V charged device model ([USBSER-GF180-IO]_, ESD protection
page). These are ratings for handling a chip; a connector pin of a finished
product also faces the stronger system-level discharge test, which the
