What the source and the sink each do
====================================

The steps each end follows to set up and keep a power contract.

The source side
---------------

Switchable Rp
~~~~~~~~~~~~~

The level a source advertises with Rp is a promise about current at 5 V:

* **Before a contract**, the source must be able to supply the advertised
  current, and its first Source_Capabilities must offer at least that much at
  5 V (:typec:`Section 4.5.2.2.9.1`; :pd:`Section 3.2.1`, item 5). A board with
  little spare power advertises "default"; one that can spare 7.5 W or 15 W
  at 5 V advertises 1.5 A or 3.0 A.
* **During a contract**, the Rp value no longer means current. The source
  uses it to control who may start a message exchange: the 3.0 A value
  ("SinkTxOK") lets the sink start one, the 1.5 A value ("SinkTxNG") reserves
  the line for the source, which then waits *tSinkTx* (16 ms to 20 ms) before
  starting (:pd:`PD Sections 5.2.2 <x>`, :pd:`7.2 <x>` and
  :pd:`7.31.13.1 <x>`; :pd:`Table 5.1 <x>`).

A source therefore changes its Rp level during normal operation, and its Rp
circuit must provide at least the 1.5 A and 3.0 A levels whatever power it
offers. A current source suits an integrated circuit: the three currents
(80, 180 and 330 µA) can come from one reference and switchable current
mirrors, and the open-circuit voltage must rise above the 2.432 V "open"
threshold for the 3.0 A level. TI specifies its TPS65987D current sources as
73.6-86.4 µA, 165.6-194.4 µA and 303.6-356.4 µA, with the 3.0 A level valid
up to a CC voltage of 2.6 V ([USBPD-TPS65987D]_, Section 6.8).

Source sequence
~~~~~~~~~~~~~~~

After attach (Attached.SRC) the source:

#. turns VBUS on to *vSafe5V* (4.75 V to 5.5 V, :pd:`Table 4.9`) within
   tVBUSON (275 ms), supplies VCONN if needed (see `Cables and VCONN`_), and must not
   start messages until VBUS has reached vSafe5V
   (:typec:`Section 4.5.2.2.9.1`);
#. optionally queries the cable (required before offering more than 3 A or
   EPR voltages; see `Cables and VCONN`_);
#. sends Source_Capabilities within tFirstSourceCap (250 ms) and repeats it
   every 100 ms to 200 ms until it gets a GoodCRC (:pd:`Section 7.31.3`);
#. evaluates the Request (see below) and answers Accept or Reject within
   tReceiverResponse (15 ms);
#. after Accept, waits at least tSrcTransition (25 ms), changes the voltage
   at no more than 30 mV/µs (*vSrcSlewPos*, *vSrcSlewNeg*,
   :pd:`Table 4.7`), and sends PS_RDY within tSrcTransReq (325 ms in SPR) of
   the GoodCRC for Accept (:pd:`Section 4.5.1.1`; :pd:`Table 4.7 <x>`). The
   new voltage must be within ± 5 % of the offered value, plus 0.5 V while
   settling (*vSrcNew*, *vSrcValid*, :pd:`Table 4.7`).

The slew limit exists to limit the current that charges the sink's input
capacitors: :pd:`Table 4.7` states it is based on a 3 A connector rating
and at most 100 µF of sink capacitance. The source's own output capacitance
must be at least 10 µF (*cSrcBulk*, :pd:`Table 4.7`), while a dual-role port
that is not supplying VBUS may present at most 10 µF on VBUS
(:typec:`Table 4-2`), so the larger bulk capacitance has to sit behind the
source switch (see `Bidirectional VBUS power path and converter control`_).

Building the offer from the power budget
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The processor decides what to offer from the
:ref:`power budget <power-budget>`. The power it can offer on the USB port is
what the input grants, less what the board uses, less what the converter
loses:

.. math::

   P_\text{offer} = (P_\text{in} - P_\text{board}) \cdot \eta

where:

* :math:`P_\text{offer}` is the power offered on the USB port, in watts (the
  *Port Present PDP* in PD terms, :pd:`Section 3.2`);
* :math:`P_\text{in}` is the power granted on the input port, for example by
  Power over Ethernet (see :doc:`poe`);
* :math:`P_\text{board}` is the power the board itself uses;
* :math:`\eta` is the efficiency of the USB source converter.

*Example with assumed numbers* (none of them is a design value): with
:math:`P_\text{in}` = 25 W, :math:`P_\text{board}` = 5 W and
:math:`\eta` = 0.90,

.. math::

   P_\text{offer} &= (25\ \text{W} - 5\ \text{W}) \times 0.90 \\
                  &= 20\ \text{W} \times 0.90 = 18\ \text{W}

For a source rated between 15 W and 27 W, :pd:`Table 3.1` requires a 5 V
offer of 3 A and a 9 V offer of :math:`P_\text{offer} / 9\ \text{V}`; here
:math:`18\ \text{W} / 9\ \text{V} = 2.00\ \text{A}`. Currents are rounded
to 10 mA (:pd:`Section 3.2.1`, item 1). So the Source_Capabilities message
lists "5 V 3 A" and "9 V 2 A". Other rules shape the list: the first PDO is
always 5 V (:pd:`Section 6.4.1.1`); no fixed PDO may offer more power (its
voltage times its maximum current) than a fixed PDO of higher voltage in the
same list (:pd:`Section 3.2.1`, item 2); and currents above 3 A need a 5 A
cable (:pd:`Section 8.6.1.2.2`). A port with nothing to offer sends a single
"5 V 0 A" PDO (:pd:`Section 7.9.1.5`).

**Evaluating the request.** The source checks that the requested object
exists and that the requested current does not exceed the offered maximum,
then answers Accept, Reject or Wait (:pd:`Section 6.4.2`; :pd:`Table 6.19 <x>`).

**Changing the offer.** When the input power changes, the processor sends new
Source_Capabilities and the sink must request again. When lowering the offer,
the source should first send an Alert message, up to *tReducePowerAlert*
(2.0 s to 2.4 s) before the reduced capabilities (:pd:`Section 6.4.5.5`;
:pd:`Table 4.7 <x>`). If the input drops faster than that, the source's own
over-current protection (`Current limit and over-current response`_) or a
Hard Reset (`Hard Reset in each role`_) is the remaining option, so the
:ref:`power budget <power-budget>` should keep a margin.

Current limit and over-current response
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A source must have over-current protection that does not trip within the
contract, should send Hard Reset (and later an Alert) when it trips, and,
when it shuts down a port above 5 V, must bring VBUS down to vSafe5V within
*tSafe5V* (275 ms) and to vSafe0V within *tSafe0V* (650 ms)
(:pd:`Section 4.1.5.1`; :pd:`Table 4.9 <x>`). The current limit is part of
the source power path (see
`Bidirectional VBUS power path and converter control`_). For example, TPS65987D has a firmware-selectable over-current clamp with 20
settings from 1.267 A to 6.33 A (typical) and a fast-acting limit of about
10 A ([USBPD-TPS65987D]_, Section 6.7).

Discharging VBUS
~~~~~~~~~~~~~~~~

A source must bring VBUS to vSafe0V within tSafe0V (650 ms) after detach,
and to below vSafe5V (max) within tSafe5V (275 ms) (:pd:`Section 4.1.5.5`).
It must also discharge VBUS before attaching (AttachWait.SRC,
:typec:`Section 4.5.2.2.8.1`) and during a role swap. A switched load from
VBUS to ground, controlled by the processor, does this (see
`VBUS sensing and discharge`_).

The sink side
-------------

A sink presents Rd, waits for VBUS and Source_Capabilities, chooses a PDO,
sends Request within tReceiverResponse (15 ms), and after Accept cuts its
current to *iSnkStdby* (500 mA) within *tSnkStdby* (15 ms) until PS_RDY
arrives (:pd:`Section 4.5.1.1`; :pd:`Table 4.8 <x>`). A sink that uses the
1.5 A or 3.0 A Rp level before a contract must follow changes of Rp within *tSinkAdj*
(60 ms, :typec:`Table 4-32`). During a contract it must check the Rp level
before starting an exchange of its own (:pd:`Section 7.2`). A sink should
tolerate up to 24 V on VBUS without damage (*vSprMax*, :pd:`Table 4.8`).

A slow sink does not miss the negotiation: the source repeats
Source_Capabilities 50 times. The sink may send Hard Reset after
tTypeCSinkWaitCap to restart the source, but a board powered only from VBUS
should avoid this, because the source answers a Hard Reset by switching VBUS
off (see `Hard Reset in each role`_).
