.. _usbpd-resistor-advertisement:

The source advertises its current with a pull-up
================================================

How the source's pull-up and the sink's pull-down on the
:term:`configuration channel` tell each end what is attached and how much
current the sink may draw at 5 V, and the voltage thresholds each end
measures.

The specification calls this mechanism :term:`USB Type-C Current`
(:typec:`Section 4.6.2.1`). It needs no messages and no processor: a
resistor or :wikipedia:`current source <Current_source>` at one end, a
resistor at the other, and a voltage measurement. The CC wire and the two
ends are described on :doc:`type-c-power`.

.. _usbpd-cc-voltages:

The pull-up and pull-down form a divider whose voltage gives the level
----------------------------------------------------------------------

The source connects a :wikipedia:`pull-up <Pull-up_resistor>`, :term:`Rp`,
to each CC pin. The sink connects a pull-down, :term:`Rd`, to each of its CC
pins. When a cable joins them, Rp and Rd form a
:wikipedia:`voltage divider <Voltage_divider>` on the CC wire, and the
voltage across Rd tells the sink which of three current levels the source
offers.

Rp is a resistor to 5 V, a resistor to 3.3 V or a current source. Its value
sets the advertised level (:numref:`tab-usbpd-rp`).

.. list-table:: Nominal source pull-up (Rp) for each level (:typec:`Table 4-27`)
   :name: tab-usbpd-rp
   :header-rows: 1
   :widths: 28 24 24 24

   * - Advertised level
     - Current source (µA)
     - Resistor to 5 V (kΩ)
     - Resistor to 3.3 V (kΩ)
   * - Default USB power
     - 80
     - 56
     - 36
   * - 1.5 A at 5 V
     - 180
     - 22
     - 12
   * - 3.0 A at 5 V
     - 330
     - 10
     - 4.7

The tolerances and supply ranges in :numref:`tab-usbpd-rp-tolerance` apply
to the values in :numref:`tab-usbpd-rp`. Each value is the total current or
resistance into the source's CC pin, leakage included (:typec:`Table 4-27`,
note 2).

.. list-table:: Tolerance and supply of each kind of pull-up (:typec:`Table 4-27`)
   :name: tab-usbpd-rp-tolerance
   :header-rows: 1
   :widths: 28 24 24 24

   * - Pull-up
     - Supply (V)
     - Default tolerance (± %)
     - 1.5 A and 3.0 A tolerance (± %)
   * - Current source
     - 1.7 to 5.5
     - 20
     - 8
   * - Resistor to 5 V
     - 4.75 to 5.5
     - 20
     - 5
   * - Resistor to 3.3 V
     - 3.135 to 3.465
     - 20
     - 5

"Default USB power" is the current a USB host port supplies: 500 mA for a
USB 2.0 port, and 900 mA or 1500 mA for a USB 3.2 port in single-lane or
dual-lane operation (:typec:`Section 4.6.2.1`, :typec:`Table 4-20`).
:doc:`start-up` gives the power each level makes available.

Rd is 5.1 kΩ to ground (:typec:`Table 4-28`). A sink whose Rd is within
± 10 % can tell the three levels apart. A sink whose Rd is within ± 20 % can
only detect that a source is attached. A sink without power may present a
1.1 V ± 20 % voltage clamp instead, which also cannot tell the levels apart
and stops USB Power Delivery messages until the sink switches to a resistor
(:typec:`Table 4-28`, note 1; :ref:`usbpd-dead-battery`).

The CC voltage follows from the divider
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With a resistor Rp, the CC voltage is set by the divider. With a
current-source Rp, it is the current times Rd:

.. math::

   V_\text{CC} = V_\text{pull} \times \frac{R_d}{R_p + R_d}

   V_\text{CC} = I_p \times R_d

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`V_\text{CC}`
     - Voltage on the CC pin that meets the CC wire
     - V
   * - :math:`V_\text{pull}`
     - Supply that a resistor Rp is connected to, 5 V or 3.3 V
     - V
   * - :math:`R_p`
     - Source pull-up resistance (:numref:`tab-usbpd-rp`)
     - kΩ
   * - :math:`I_p`
     - Source pull-up current (:numref:`tab-usbpd-rp`)
     - µA
   * - :math:`R_d`
     - Sink pull-down resistance, 5.1 kΩ nominal
     - kΩ

The equations hold for nominal values with no current flowing on VBUS, so
that the two grounds are at the same voltage. The resistance of the CC wire
is neglected, as :typec:`Section 4.11.3.1` does. That section gives the same
equations with the tolerances and a ground offset added.

For example, a 22 kΩ resistor to 5 V with Rd of 5.1 kΩ gives:

.. math::

   V_\text{CC} = 5\ \text{V} \times
   \frac{5.1\ \text{k}\Omega}{22\ \text{k}\Omega + 5.1\ \text{k}\Omega}
   = 0.94\ \text{V}

The same steps for every level give :numref:`tab-usbpd-cc-nominal`.

.. list-table:: Nominal CC voltage with Rd of 5.1 kΩ
   :name: tab-usbpd-cc-nominal
   :header-rows: 1
   :widths: 28 24 24 24

   * - Advertised level
     - Resistor to 5 V (V)
     - Resistor to 3.3 V (V)
     - Current source (V)
   * - Default USB power
     - 0.42
     - 0.41
     - 0.41
   * - 1.5 A
     - 0.94
     - 0.98
     - 0.92
   * - 3.0 A
     - 1.7
     - 1.7
     - 1.7

The three kinds of pull-up give nearly the same voltage for each level, so
a sink reads the level without knowing how the source made it: about 0.4 V,
0.9 V and 1.7 V.

.. _usbpd-cc-states:

Each end names what it sees on a CC pin
---------------------------------------

The attach rules on :doc:`attach` are written in terms of the state of each
CC pin (:numref:`tab-usbpd-cc-states`). A source sees a sink's Rd, nothing,
or :term:`Ra`. Ra is an 800 Ω to 1.2 kΩ pull-down inside a cable plug that
contains a chip, the :term:`e-marker`; it sits on the plug's VCONN contact
(:typec:`Table 4-29`; :ref:`usbpd-cables`).

.. list-table:: CC pin states (:typec:`Table 4-16`, :typec:`Table 4-17`)
   :name: tab-usbpd-cc-states
   :header-rows: 1
   :widths: 22 30 48

   * - State
     - Far end presents
     - CC voltage
   * - SRC.Rd
     - Rd
     - Within the vRd range
   * - SRC.Ra
     - Ra
     - Below the minimum of vRd
   * - SRC.Open
     - Nothing, or Rp
     - Above the maximum of vRd
   * - SNK.Rp
     - Rp
     - Above the minimum of vRd-connected
   * - SNK.Open
     - Nothing, Ra or Rd
     - Below the minimum of vRd-connected

A source asserts Rp and reads the SRC states. A sink asserts Rd and reads
the SNK states. The voltages that separate the states follow.

.. _usbpd-sink-thresholds:

The sink compares the CC voltage with three thresholds
------------------------------------------------------

The sink has to tell four ranges apart: no source, and the three advertised
levels. :typec:`Section 4.11.3.1.1` gives the method: work out the lowest
and highest CC voltage for each level from the tolerances of Rp and Rd and
up to 250 mV of ground offset caused by current in the cable. Its example
for an Rd within ± 10 % is :numref:`tab-usbpd-sink-thresholds`.

.. list-table:: CC voltage at a sink with Rd within ± 10 % (:typec:`Table 4-36`)
   :name: tab-usbpd-sink-thresholds
   :header-rows: 1
   :widths: 50 25 25

   * - Range
     - Minimum (V)
     - Maximum (V)
   * - Default USB power (vRd-USB)
     - 0.277
     - 0.612
   * - 1.5 A (vRd-1.5)
     - 0.746
     - 1.164
   * - 3.0 A (vRd-3.0)
     - 1.369
     - 2.042
   * - Any source attached (vRd-connected)
     - 0.277
     - 2.042
   * - Threshold between default and 1.5 A
     - 0.613
     - 0.745
   * - Threshold between 1.5 A and 3.0 A
     - 1.165
     - 1.368
   * - Threshold for detecting a detach
     - none
     - 0.276

Each "threshold" row gives the window in which the sink's threshold must
lie. A sink therefore needs, on each CC pin, one threshold for attach and
one for each of the two level boundaries. For an Rd within ± 20 %, the CC
voltage of an attached source is 0.249 V to 2.181 V, and the detach
threshold lies at or below 0.248 V (:typec:`Table 4-35`).

.. _usbpd-source-thresholds:

The source compares the CC voltage with two thresholds for each level
---------------------------------------------------------------------

The source has to tell Rd, Ra and an open pin apart. It knows which Rp it
is presenting, so it needs one pair of thresholds for each level it uses.
For a current-source Rp, the specification's example is
:numref:`tab-usbpd-src-thresholds`.

.. list-table:: Thresholds at a source with a current-source Rp (:typec:`Table 4-37`)
   :name: tab-usbpd-src-thresholds
   :header-rows: 1
   :widths: 25 25 25 25

   * - Rp current (µA)
     - Ra to Rd, minimum (V)
     - Ra to Rd, maximum (V)
     - Rd to open, minimum (V)
   * - 80
     - 0.116
     - 0.260
     - 1.321
   * - 180
     - 0.234
     - 0.675
     - 1.441
   * - 330
     - 0.429
     - 0.879
     - 2.432

The first two columns give the window for the threshold that separates Ra
from Rd. The last column is the lowest allowed threshold for an open pin,
which includes 250 mV of ground offset (:typec:`Table 4-37`, note 1).
:typec:`Table 4-38` and :typec:`Table 4-39` give the same thresholds for a
resistor Rp to 5 V and to 3.3 V.

A dual-role port therefore needs, on each CC pin, three thresholds as a sink
and two for each Rp level it uses as a source. They are made by
:wikipedia:`comparators <Comparator>` or by an
:term:`analogue-to-digital converter`; :ref:`usbpd-comparators` describes
evampire's circuit and :ref:`usbpd-rp-sources` its pull-up.
