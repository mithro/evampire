On chip or external
===================

Which circuits can be built on gf180mcu, and the voltage limits that decide it.

Limits of the gf180mcu process
------------------------------

Three different kinds of limit matter, and they should not be confused.

**(a) Ratings of the standard devices.** These are conservative continuous
operating limits for the devices in the `PDK
<https://gf180mcu-pdk.readthedocs.io/>`__. The process is described as
"0.18 µm 3.3V/(5V)6V dual-gate MCU technology" ([USBPD-GF180-DRM]_, Section
1.0), with low-voltage devices at 3.3 V and high-voltage devices at 5 V or
6 V (Section 2.7), and the device list also contains LDMOS transistors rated
for 10 V (Appendix A; :numref:`tab-usbpd-pdk-ratings`).

.. list-table:: (a) Standard device operating voltages
   :name: tab-usbpd-pdk-ratings
   :header-rows: 1
   :widths: 40 60

   * - Device
     - Operating voltage
   * - nfet_03v3, pfet_03v3
     - 3.3 V
   * - nfet_05v0, pfet_05v0 (6 V devices with a 5 V marker layer)
     - 5 V
   * - nfet_06v0, pfet_06v0, nfet_06v0_nvt (native)
     - 6 V
   * - nfet_10v0_asym, pfet_10v0_asym (LDMOS)
     - 10 V drain, 6 V gate ([USBPD-GF180-ELEC]_, sections 8.1 and 8.2)
   * - MIM capacitor, 1.5 fF/µm² option
     - at most 10 V ([USBPD-GF180-ELEC]_, section 6.2)
   * - MIM capacitor, 1 fF/µm² option
     - "≤ 20 V application" ([USBPD-GF180-ELEC]_, section 6.2)

**(b) Physical limits of the layers.** Breakdown voltages measured on test
structures, where documented ([USBPD-GF180-ELEC]_, sections 1 to 8;
:numref:`tab-usbpd-pdk-breakdown`):

.. list-table:: (b) Documented breakdown limits
   :name: tab-usbpd-pdk-breakdown
   :header-rows: 1
   :widths: 50 25 25

   * - Structure
     - Minimum
     - Typical
   * - Gate oxide, 3.3 V devices
     - 7 V
     - 8.8-9 V
   * - Gate oxide, 6 V devices
     - 12 V
     - 16 V
   * - N+ to P-well junction, 6 V NMOS
     - 8.5 V
     - 11 V
   * - N-well to P-substrate junction
     - 10 V
     - 14 V
   * - LDMOS drain (BVDSS)
     - 13.2 V
     - 14.5 V
   * - Vertical PNP collector-emitter (BVCEO)
     - 10 V
     - 15 V
   * - MIM dielectric, 1.5 fF/µm²
     - 10 V
     - 30 V
   * - MIM dielectric, 1 fF/µm²
     - 20 V
     - 40 V
   * - Deep N-well to P-substrate junction
     - not documented
     -
   * - Field oxide under poly or metal, and between metal layers
     - not documented
     -

Which MIM option, and whether the LDMOS and deep N-well layers, are available
on the wafer.space (https://wafer.space/) shuttle has to be confirmed.

**(c) What custom structures could reach.** These are design possibilities
whose limits come from (b), not from (a):

* *Stacked transistors in isolated wells.* Each transistor holds a share of
  the voltage within its own rating; the stack is limited by the breakdown of
  the isolating well to the substrate (deep N-well: not documented) and by
  the gate oxide of each device relative to its own well. Published example:
  [USBPD-SERNEELS]_.
* *Custom drain-extended transistors.* A longer, lightly doped drain region
  drawn from existing layers, as described by [USBPD-BALLAN]_; the PDK's own
  LDMOS, rated for 10 V, breaks down at no less than 13.2 V.
* *Series capacitor stacks.* For coupling or sensing AC signals across a
  high voltage; with the 1 fF/µm² MIM option each capacitor withstands at
  least 20 V, but the bottom plate to substrate isolation is not documented.
* *High-resistance poly dividers.* 1 kΩ, 2 kΩ or 3 kΩ per square
  ([USBPD-GF180-ELEC]_, section 6.1); limited by the undocumented field oxide
  breakdown.
* *Custom clamps and references.* Clamps from the documented diodes and
  bipolar transistors; a bandgap reference from the vertical PNP.

Pin voltages and placement options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:numref:`tab-usbpd-placement` summarises the options.

.. list-table:: Where each function can be built
   :name: tab-usbpd-placement
   :header-rows: 1
   :widths: 22 24 27 27

   * - Function
     - Voltage
     - On chip
     - External
   * - Rp, Rd, comparators, BMC driver and receiver, VCONN switch
     - 0 V to 5.5 V
     - Standard 5 V / 6 V devices
     - Not needed
   * - Dead-battery Rd
     - at most 2.18 V, unpowered (:typec:`Table 4-28`)
     - Native NMOS and poly resistor
     - In the CC protector
   * - Reference
     - low voltage
     - Custom bandgap from vertical PNP
     - Reference IC
   * - CC protection against VBUS short
     - 21.5 V (SPR) or 50.9 V (EPR), plus ringing
     - Custom stacked switch; limit not documented; high risk
     - Protector (TPD8S300A, NX48P0407)
   * - VBUS sensing
     - up to 21.5 V or 50.9 V
     - Poly divider; field oxide limit not documented
     - External top resistor
   * - VBUS discharge
     - same
     - Needs a blocking switch as above
     - External transistor and load
   * - Power path switches and source converter
     - same, at 3 A to 5 A
     - Control and feedback on chip; power devices beyond documented limits
     - MOSFETs, inductor, gate drivers

The choice for each row is listed under `Open design decisions`_.

Open design decisions
---------------------

* **Processor core and clock** (`The processor clock`_). Multi-cycle or
  pipelined, and 31.25 MHz, 62.5 MHz or another clock. This decides whether
  the timer compare and capture channels are required
  (`Hardware helpers, in order of need`_).
* **Optional timer channels** (`Recommended split`_). With a pipelined core
  at 50 MHz or faster no digital helper is needed; adding a timer capture
  channel with a FIFO (and choosing its depth) and a compare output per port
  anyway would let interrupts stay enabled during messages instead of being
  disabled for up to 2.3 ms.
* **Behaviour with two ports at once** (`Two ports in software`_). Whether
  occasional message loss and retries on the second port are acceptable, or
  a helper per port is added.
* **Supported power levels** (`Layer 2: USB Power Delivery power levels`_).
  Whether the board offers and accepts only SPR fixed supplies, also 5 A
  (which requires VCONN and cable discovery as source), PPS/AVS, or EPR
  (48 V on VBUS and on the CC pins in a fault, and keep-alive messages).
* **Role preference policy** (`Choosing the initial role`_). When to use
  Try.SRC or Try.SNK, and when to ask for a power role swap, given the
  :ref:`power budget <power-budget>`.
* **Fast role swap** (`Fast role swap`_). Whether the board signals or
  accepts FRS; this needs a strong CC pull-down, hold-up energy, and a source
  converter kept running.
* **CC protection against a VBUS short**
  (`Over-voltage protection on the CC pins`_). A custom on-chip blocking
  switch (which first needs test structures to measure the deep N-well
  isolation limit) or an external protector; either must pass VCONN and keep
  the dead-battery Rd visible.
* **Dead-battery Rd** (`Switchable Rd and dead-battery Rd`_). On chip
  (native NMOS and poly resistor) or in an external protector.
* **VCONN switch** (`VCONN switch`_). On chip (standard 5 V / 6 V devices)
  or external.
* **Reference voltage** (`Reference voltage`_). A custom on-chip bandgap
  reference from the vertical PNP, shared with the Ethernet
  (:doc:`../ethernet/index`) and Power over Ethernet (:doc:`poe`) circuits,
  or an external reference.
* **VBUS sensing and discharge** (`VBUS sensing and discharge`_). An on-chip
  poly divider (field oxide limit to be established) or an external top
  resistor and discharge transistor.
* **Power path and converter**
  (`Bidirectional VBUS power path and converter control`_). Which parts of
  the control (modulation, feedback, reverse-current detection, gate drive)
  are on chip; the power switches themselves; and budget margins, including
  how fast the board can react when the Ethernet input is reduced or lost
  (see :ref:`power budget <power-budget>` and :doc:`poe`).
* **Process options** (`Limits of the gf180mcu process`_). Which MIM option
  and whether the LDMOS and deep N-well layers are available on the
  wafer.space (https://wafer.space/) shuttle.
