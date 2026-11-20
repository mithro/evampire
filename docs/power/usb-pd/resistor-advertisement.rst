The source advertises its current with a pull-up
================================================

How the source's pull-up and the sink's pull-down tell each end what is attached and how much current is allowed.

Layer 1: the resistor advertisement
-----------------------------------

The source pulls each of its CC pins up with Rp, and the sink pulls each of
its CC pins down with Rd. When a cable joins them, the CC wire forms a
voltage divider (or, with a current-source Rp, a current flowing into Rd).
:numref:`tab-usbpd-rp` lists the allowed pull-ups.

.. list-table:: Source pull-up (Rp) choices (:typec:`Table 4-27`)
   :name: tab-usbpd-rp
   :header-rows: 1
   :widths: 25 25 25 25

   * - Advertised current
     - Current source to 1.7-5.5 V
     - Resistor to 4.75-5.5 V
     - Resistor to 3.3 V ± 5 %
   * - Default USB power
     - 80 µA ± 20 %
     - 56 kΩ ± 20 %
     - 36 kΩ ± 20 %
   * - 1.5 A at 5 V
     - 180 µA ± 8 %
     - 22 kΩ ± 5 %
     - 12 kΩ ± 5 %
   * - 3.0 A at 5 V
     - 330 µA ± 8 %
     - 10 kΩ ± 5 %
     - 4.7 kΩ ± 5 %

"Default USB power" means 500 mA for a USB 2.0 port
(https://www.usb.org/document-library/usb-20-specification) and 900 mA for a
single-lane USB 3.2 port
(https://www.usb.org/document-library/usb-32-revision-11-june-2022)
(:typec:`Table 4-20`).

The sink's Rd is 5.1 kΩ to ground. It may be accurate to ± 10 %, which lets
the sink tell the three current levels apart, or ± 20 %, which only lets it
detect that a source is present (:typec:`Table 4-28`). An unpowered sink may
instead present a 1.1 V ± 20 % clamp, which stops USB Power Delivery
communication until it switches to a real Rd (:typec:`Table 4-28`, note 1).

**The CC voltage for each Rp level.** Both ends decide what is attached by
measuring the CC voltage, so the circuit designer needs to know what voltage
each combination produces. With a resistor Rp the CC voltage is set by the
divider; with a current-source Rp it is the current times Rd:

.. math::

   V_\text{CC} = V_\text{pull} \cdot \frac{R_d}{R_p + R_d}
   \qquad\text{or}\qquad
   V_\text{CC} = I_p \cdot R_d

where:

* :math:`V_\text{CC}` is the voltage on the connected CC pin, in volts;
* :math:`V_\text{pull}` is the voltage the resistor Rp is connected to:
  5 V or 3.3 V (:typec:`Table 4-27`);
* :math:`R_p` is the source's pull-up resistor (:typec:`Table 4-27`);
* :math:`I_p` is the source's pull-up current (:typec:`Table 4-27`);
* :math:`R_d` is the sink's pull-down, 5.1 kΩ nominal (:typec:`Table 4-28`).

The model assumes nominal values, no current in the cable and a negligible
cable resistance (the same assumption :typec:`Section 4.11.3.1` makes). As an
example of the steps, for 22 kΩ to 5 V:
:math:`R_p + R_d = 22 + 5.1 = 27.1\ \text{k}\Omega`, and
:math:`5\ \text{V} \times 5.1 / 27.1 = 0.941\ \text{V}`. The same steps for
every level give :numref:`tab-usbpd-cc-nominal`:

.. list-table:: Nominal CC voltage with Rd = 5.1 kΩ
   :name: tab-usbpd-cc-nominal
   :header-rows: 1
   :widths: 25 25 25 25

   * - Advertised current
     - Resistor to 5 V
     - Resistor to 3.3 V
     - Current source
   * - Default USB power
     - 5 × 5.1 / 61.1 = 0.417 V
     - 3.3 × 5.1 / 41.1 = 0.409 V
     - 80 µA × 5.1 kΩ = 0.408 V
   * - 1.5 A
     - 5 × 5.1 / 27.1 = 0.941 V
     - 3.3 × 5.1 / 17.1 = 0.984 V
     - 180 µA × 5.1 kΩ = 0.918 V
   * - 3.0 A
     - 5 × 5.1 / 15.1 = 1.689 V
     - 3.3 × 5.1 / 9.8 = 1.717 V
     - 330 µA × 5.1 kΩ = 1.683 V

The three methods give nearly the same voltage for each level, which is what
lets a sink read the level without knowing how the source made it. The three
levels are about 0.4 V, 0.9 V and 1.7 V.

**What the sink measures.** :typec:`Section 4.11.3.1` gives the method for
including all tolerances and up to 250 mV of ground offset caused by current
in the cable. For an Rd of ± 10 % the result is :numref:`tab-usbpd-sink-thresholds`
(:typec:`Table 4-36`):

.. list-table:: CC voltage measured by a sink (Rd ± 10 %, :typec:`Table 4-36`)
   :name: tab-usbpd-sink-thresholds
   :header-rows: 1
   :widths: 50 25 25

   * - Condition
     - Minimum
     - Maximum
   * - Default USB power (vRd-USB)
     - 0.277 V
     - 0.612 V
   * - 1.5 A (vRd-1.5)
     - 0.746 V
     - 1.164 V
   * - 3.0 A (vRd-3.0)
     - 1.369 V
     - 2.042 V
   * - Threshold between default and 1.5 A
     - 0.613 V
     - 0.745 V
   * - Threshold between 1.5 A and 3.0 A
     - 1.165 V
     - 1.368 V
   * - Threshold for "nothing connected"
     - below 0.276 V
     -

**What the source measures.** A source uses its own CC voltage to tell an Rd
(a sink), an Ra (a cable plug with an e-marker) and nothing (an open pin)
apart. Because a source knows its own Rp, it has one set of thresholds per Rp
level. For a current-source Rp (the type that suits an integrated circuit,
see `Switchable Rp`_) the thresholds are in :numref:`tab-usbpd-src-thresholds`
(:typec:`Table 4-37`):

.. list-table:: CC voltage thresholds for a source with a current-source Rp (:typec:`Table 4-37`)
   :name: tab-usbpd-src-thresholds
   :header-rows: 1
   :widths: 25 25 25 25

   * - Rp level
     - Ra below, Rd above (window)
     - Rd range (vRd)
     - Open above (minimum)
   * - Default (80 µA)
     - 0.116 V to 0.260 V
     - 0.261 V to 1.32 V
     - 1.321 V
   * - 1.5 A (180 µA)
     - 0.234 V to 0.675 V
     - 0.676 V to 1.32 V
     - 1.441 V
   * - 3.0 A (330 µA)
     - 0.429 V to 0.879 V
     - 0.88 V to 2.181 V
     - 2.432 V

The "open" thresholds allow 250 mV of ground offset (:typec:`Table 4-37`,
note 1). A commercial example is the TI TPS65987D [USBPD-TPS65987D]_, which
as a source detects an Ra below 0.15-0.25 V, 0.35-0.45 V or 0.75-0.85 V and
an open pin above 1.5-1.65 V, 1.5-1.65 V or 2.45-2.615 V for the three Rp
levels (Section 6.8). A dual-role port therefore needs, per CC pin, three
thresholds as a sink (:numref:`tab-usbpd-sink-thresholds`: connected, and
the two boundaries between the Rp levels) and, as a source, two boundaries
for each Rp level it uses (Ra to Rd, and Rd to open;
:numref:`tab-usbpd-src-thresholds`).
