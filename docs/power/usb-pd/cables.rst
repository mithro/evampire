Cables and VCONN
================

How a port powers and queries the chip inside a marked cable.

Cables and VCONN
----------------

**Why the source checks the cable.** Every standard USB Type-C cable is
rated for at least 3 A at voltages above 5 V (:pd:`Section 8.6.1.2.2`).
Cables rated for more than 3 A, and all EPR cables, are electronically marked
(:typec:`Type-C Sections 3.4.1.1 <x>`, :typec:`3.4.2.1 <x>` and
:typec:`3.11.2 <x>`). A source that can offer more than 3 A must query the
cable and limit its offer to what the cable supports; an EPR source must
check that the cable supports EPR (:pd:`PD Sections 8.6.1.2.2 <x>` and
:pd:`8.6.1.2.3 <x>`). A port that can be a source offering more than 3 A must
therefore support the *Discover Identity* query (:pd:`Section 7.5`,
applicability table).

**How the query works.** The query is a Vendor_Defined message, *Discover
Identity*, sent with the SOP′ ordered set to the near cable plug. The
e-marker answers with its identity and a *cable VDO* (vendor data object), a
32-bit word whose fields
include the maximum VBUS voltage (20 V or 50 V) and the VBUS current
capability (3 A or 5 A) (:pd:`Table 6.45`). If there is no GoodCRC, the source
repeats the query every *tDiscoverIdentity* (40 ms to 50 ms) and gives up
after *nDiscoverIdentityCount* (20) attempts (:pd:`Section 7.31.12.4`;
:pd:`Tables 7.10 <x>` and :pd:`7.12 <x>`). Before a contract any source may
talk to the cable; after one, only the port supplying VCONN may
(:typec:`Section 4.9`).

**VCONN power.** The e-marker is powered by VCONN, which the source supplies
on the CC pin not connected to the CC wire (the pin showing Ra, or
unconditionally on the unused pin) within *tVCONNON* (2 ms) of VBUS reaching
5 V (:typec:`Section 4.5.2.2.9.1`; :typec:`Table 4-32 <x>`). How much VCONN
power is required depends on what the port does (:typec:`Table 4-4`;
:numref:`tab-usbpd-vconn`):

.. list-table:: VCONN requirements relevant to evampire
   (:typec:`Type-C Tables 4-4 <x>` to :typec:`4-6 <x>`)
   :name: tab-usbpd-vconn
   :header-rows: 1
   :widths: 40 60

   * - Situation
     - Requirement
   * - No USB data, offering 3 A or less
     - VCONN not required.
   * - No USB data, offering more than 3 A
     - Source at least 100 mW; may be switched off after reading the cable's
       rating.
   * - VCONN voltage
     - 3.0 V to 5.5 V (*vVCONNValid*).
   * - Load presented by a passive e-marked cable
     - At most 20 mW (75 mW briefly after VCONN is applied) and at most
       10 µF of inrush capacitance.
   * - Discharge after detach
     - Resistance *Rdch* of 30 Ω to 6120 Ω on the VCONN pin until it is
       below 0.8 V (:typec:`Section 4.5.2.2.6`; :typec:`Table 4-5 <x>`).

*How much current the VCONN switch must pass.* The switch has to charge the
cable's capacitance to the minimum valid VCONN voltage within tVCONNON.
Assuming a constant charging current (a current-limited switch behaves this
way), the current needed is:

.. math::

   I_\text{inrush} &= \frac{C_\text{cable} \cdot V_\text{min}}{t_\text{on}}
                    = \frac{10\ \mu\text{F} \times 3.0\ \text{V}}{2\ \text{ms}} \\
                   &= \frac{30\ \mu\text{C}}{2\ \text{ms}}
                    = 15\ \text{mA}

where :math:`C_\text{cable}` = 10 µF is the largest inrush capacitance a cable
may present (:typec:`Table 4-6`), :math:`V_\text{min}` = 3.0 V is the minimum
valid VCONN (:typec:`Table 4-5`) and :math:`t_\text{on}` = 2 ms is tVCONNON
(:typec:`Table 4-32`). The source must also be able to supply 100 mW
continuously (:typec:`Table 4-4`), which is
:math:`0.1\ \text{W} / 5\ \text{V} = 20\ \text{mA}` at 5 V, or
:math:`0.1\ \text{W} / 3.0\ \text{V} = 33\ \text{mA}` at the lowest valid
VCONN. A VCONN switch with a current limit of a few tens of milliamps
therefore meets the requirement for a port without USB data; commercial
controllers, which also serve USB data cables needing 1 W to 1.5 W
(:typec:`Tables 4-4 <x>` and :typec:`4-5 <x>`), have
limits of hundreds of milliamps (TPS65987D *ILIMPPCC* 0.6-0.9 A,
[USBPD-TPS65987D]_, Section 6.7; STUSB1602 programmable 100 mA to 600 mA,
[USBPD-STUSB1602]_, features; CCG5C over-current detection from 550 mA,
[USBPD-CCG5C]_, SID.DC.20VCONN.9).

**VCONN swap.** The two ports can exchange the VCONN duty with a VCONN_Swap
message exchange, done make-before-break (:typec:`Section 4.5.2.2.9.1`;
:pd:`Section 7.13`). A port that cannot supply VCONN answers Reject or
Not_Supported; the port currently supplying VCONN may not reject
(:pd:`Section 7.13`). After a power role swap, the port that was supplying
VCONN keeps supplying it, because a power role swap does not move VCONN
(:pd:`Section 7.10`; :typec:`Table 4-13`).
