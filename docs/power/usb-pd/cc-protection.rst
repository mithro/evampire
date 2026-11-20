Protecting the CC pins from a VBUS short
========================================

Why a short from VBUS to a CC pin differs from an ESD event, and the ways to protect against it.

Over-voltage protection on the CC pins
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Requirement.* In normal operation the CC pins see at most 5.5 V. But the CC
contact sits next to VBUS in the connector, and damaged or non-compliant
cables and debris can short them. TI explains that twisting or sliding the
plug, debris or moisture can short 20 V VBUS onto CC ([USBPD-TPD8S300A]_,
Section 3). Infineon notes that such a short rings and can reach about twice
the VBUS voltage, 44 V for 21.5 V, if nothing clamps it ([USBPD-CYPD3177]_,
Section 1.1.3); 21.5 V is also the SPR worst case used on this page. Type-C
allows a port to clamp its CC pins at 2.9 V or above
(:typec:`Table 4-40`), but a port that supplies VCONN needs up to 5.5 V on the
VCONN pin, so any clamp must sit above 5.5 V.

**Why ESD protection does not cover this.** Every I/O pad already has
protection against electrostatic discharge (ESD), and it survives thousands
of volts, so it is natural to ask why a 20 V short is a problem. The
difference is the amount of charge and how long it lasts. An ESD test pulse
is a small capacitor discharged through a resistor. For the human body model
(HBM, defined in ANSI/ESDA/JEDEC JS-001, https://www.esda.org/standards/)
used to rate chip pins, the charge delivered at the gf180mcu I/O
library's 2 kV target ([USBPD-GF180-IO]_) is:

.. math::

   Q_\text{HBM} = C_\text{HBM} \cdot V_\text{HBM}
                = 100\ \text{pF} \times 2000\ \text{V}
                = 200\ \text{nC}

where :math:`C_\text{HBM}` = 100 pF and the series resistance is 1.5 kΩ
(the HBM network, [USBPD-TB505]_), and :math:`V_\text{HBM}` = 2000 V. The
pulse decays with a time constant of
:math:`1.5\ \text{k}\Omega \times 100\ \text{pF} = 150\ \text{ns}` and peaks
at :math:`2000\ \text{V} / 1.5\ \text{k}\Omega = 1.33\ \text{A}`
([USBPD-TB505]_, Figure 2). The system-level test used for connector pins,
IEC 61000-4-2 (https://webstore.iec.ch/en/publication/4189), uses 150 pF and
330 Ω; at 8 kV the charge is
:math:`150\ \text{pF} \times 8\ \text{kV} = 1.2\ \mu\text{C}` and the first
current peak is 30 A, with a rise time below 1 ns ([USBPD-TB505]_). An ESD
clamp only has to carry this bounded charge for about 100 ns.

A VBUS short is a power supply. A source must not trip its over-current
protection for any current allowed by the contract (:pd:`Section 4.1.5.1`), so
it can keep delivering 3 A or more until the cable is pulled. *Assumption
for an order of magnitude:* the short lasts 1 s, the source delivers 3 A, and
an on-chip clamp holds the pin at 6 V. Then:

.. math::

   Q_\text{short} &= I \cdot t = 3\ \text{A} \times 1\ \text{s} = 3\ \text{C} \\
   E_\text{clamp} &= V_\text{clamp} \cdot I \cdot t
                   = 6\ \text{V} \times 3\ \text{A} \times 1\ \text{s}
                   = 18\ \text{J}

which is :math:`3\ \text{C} / 200\ \text{nC} = 1.5 \times 10^{7}` times the
HBM charge, and 18 W of continuous dissipation in the clamp. No clamp sized
for ESD can absorb this. A VBUS short must therefore be *blocked*: a series
element that holds off the full VBUS voltage (plus the ringing, unless a
clamp limits it) and opens quickly enough that the low-voltage circuits behind
it see only a brief overshoot, which an ordinary ESD-type clamp can then
absorb. TPD8S300A opens in typically 70 ns ([USBPD-TPD8S300A]_, Section 7.7);
NXP's NX48P0407, made for EPR, is specified for a short to 48 V VBUS with an
absolute maximum of 60 V on its CC pins and a response below 60 ns
[USBPD-NX48P0407]_. VBUS itself is protected against surges at board level,
for example with a transient voltage suppressor (TVS) diode
([USBPD-TPS25750]_, Section 10.2.3.2.2).

:numref:`tab-usbpd-cc-ratings` compares commercial parts.

.. list-table:: CC pin voltage ratings of commercial parts
   :name: tab-usbpd-cc-ratings
   :header-rows: 1
   :widths: 25 35 40

   * - Part
     - CC pin rating
     - Source
   * - TI TPS65987D (dual-role)
     - -0.5 V to 6 V absolute maximum
     - [USBPD-TPS65987D]_, Section 6.1
   * - TI TPS25750 (dual-role)
     - -0.5 V to 26 V absolute maximum
     - [USBPD-TPS25750]_, Section 7.1
   * - Infineon CCG5C (dual-role)
     - 24 V maximum
     - [USBPD-CCG5C]_, absolute maximum ratings
   * - ST STUSB1602 (dual-role)
     - 22 V short-to-VBUS protection; "designed in a 20 V technology"
     - [USBPD-STUSB1602]_, features and description
   * - onsemi FUSB302B (PHY, dual-role capable)
     - -0.5 V to 6.0 V absolute maximum
     - [USBPD-FUSB302B]_, Table 7
   * - TI TPD8S300A (external protector)
     - 24 V short-to-VBUS tolerance; switches open at 5.75 V to 6.2 V,
       typically within 70 ns
     - [USBPD-TPD8S300A]_, Sections 7.6 and 7.7
   * - NXP NX48P0407 (external protector, EPR)
     - CC shorted to 48 V VBUS; 60 V absolute maximum; response below 60 ns
     - [USBPD-NX48P0407]_

Controllers with 20 V-class CC pins are made in processes with high-voltage
devices (STUSB1602's description says so explicitly); controllers whose CC
pins are rated to 6 V (TPS65987D, FUSB302B) need an external protector
against a VBUS short.

*On-chip option.* A series blocking switch per CC pin, built from custom
high-voltage structures: transistors stacked in isolated wells so that each
holds part of the voltage, or custom drain-extended transistors. Stacking
low-voltage transistors to handle several times their rated voltage is
established in standard CMOS: Serneels and co-authors built an output driver
in a 2.5 V, 0.25 µm CMOS process that operates at three times the nominal
supply [USBPD-SERNEELS]_, and Ballan and Declercq describe high-voltage
devices built in standard CMOS without extra process steps
[USBPD-BALLAN]_. The switch must block 21.5 V for SPR and 50.9 V for EPR
(`Layer 2: USB Power Delivery power levels`_), plus the ringing unless a clamp behind it limits that, open within about 100 ns, pass
the BMC signal, Rp/Rd currents and VCONN with low resistance, and keep the
dead-battery Rd visible without power. The limit that decides feasibility is
the breakdown of the isolating well to the substrate, which is **not
documented** for deep N-well (`Limits of the gf180mcu process`_); the
documented N-well to substrate breakdown is at least 10 V. Feasibility therefore has to be established with
test structures, and the risk is high, especially for EPR.

*External option.* A protector such as TPD8S300A (SPR) or NX48P0407 (EPR) in
front of evampire's CC pins, which can then use standard 5 V or 6 V devices.
