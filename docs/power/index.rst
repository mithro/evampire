Power bridging
==============

A board built around evampire moves power between its Ethernet ports and its
:term:`USB Type-C` ports. It can be powered from an Ethernet cable
(:wikipedia:`Power over Ethernet <Power_over_Ethernet>`) and supply power to
a USB device, or be powered from a USB Type-C charger
(:wikipedia:`USB Power Delivery <USB_Power_Delivery>`) and supply power to
an Ethernet device. This page describes the roles, the operating modes, the
power budget and the board configurations.

The pages in this section explain each part of the power path:

:doc:`poe/index`
   The circuits that take part in Power over Ethernet detection and
   classification.
:doc:`usb-pd/index`
   The circuits that let the processor carry out the USB Power Delivery
   negotiation in software on the configuration channel.
:doc:`converters/index`
   How the switching voltage converters in the power path work, and what
   evampire needs to control them.

Both standards require the two ends of a cable to agree before full power is
applied. The end that supplies power first checks that a compatible device
is connected, then the two ends agree how much power may flow. evampire takes
part in this exchange on every port, in whichever role that port has.

.. _power-roles:

Each standard names the two ends of a powered cable
---------------------------------------------------

Each standard has its own names for the two ends of a cable, listed in
:numref:`tab-power-roles`.

.. list-table:: Names for the two ends of a powered cable
   :name: tab-power-roles
   :header-rows: 1
   :widths: 30 35 35

   * - Standard
     - End that supplies power
     - End that receives power
   * - Power over Ethernet
     - :term:`Power sourcing equipment`
     - :term:`Powered device`
   * - USB Power Delivery
     - :term:`Source`
     - :term:`Sink`

A USB Type-C port that can act as either a source or a sink is called a
:term:`dual-role port`. When two dual-role ports are connected, the roles are
decided when the cable is plugged in. The two ends can later exchange
messages to swap roles without unplugging the cable (see :doc:`usb-pd/index`).

A Power over Ethernet port has a fixed role while it is connected. Supplying
and receiving power need different circuits on the board, so a port that can
take either role has both sets of circuits and selects one before a cable is
connected (see :doc:`poe/index`).

.. _power-modes:

The board works in three modes
------------------------------

Ethernet in, USB out
   An Ethernet port receives power as a powered device. The USB Type-C port
   acts as a source and offers power to the attached device.

USB in, Ethernet out
   The USB Type-C port acts as a sink and requests power from the attached
   charger. An Ethernet port supplies power as power sourcing equipment.

Ethernet in, Ethernet out
   One Ethernet port receives power and the other supplies it.

.. _power-budget:

In every mode the processor keeps a :term:`power budget`. The power it
offers on the output ports never exceeds the power granted on the input
port, minus the power the board itself uses and the losses in the voltage
converters. When the granted input power changes, for example after a USB
role swap, the processor lowers the power offered on the outputs first.

.. _power-translation:

The software translates power between the standards
---------------------------------------------------

The two standards describe power differently. Power over Ethernet grants
power in fixed steps called :term:`classes <class>`, each with a maximum
power at the powered device. USB Power Delivery describes power as a list of
offers, each a supply voltage with a maximum current. When power comes in
through one standard and goes out through the other, the software on
evampire translates between them.

The software first works out the power left for the outputs:

.. math::

   P_\text{out} = P_\text{in} \times \eta - P_\text{board}

where :math:`P_\text{in}` is the power granted on the input port,
:math:`\eta` is the efficiency of the voltage converters (see
:doc:`converters/index`), and :math:`P_\text{board}` is the power the board itself
uses. All three are in watts, except :math:`\eta`, which is a fraction.

It then builds the offer for each output port:

Ethernet in, USB out
   The USB Type-C port offers the set of voltage and current combinations
   whose power does not exceed :math:`P_\text{out}` and which the USB Power
   Delivery rules allow for a source of that power. :doc:`usb-pd/index` explains
   these rules and gives worked examples for each Power over Ethernet class.

USB in, Ethernet out
   The Ethernet port that supplies power advertises the highest Power over
   Ethernet type and class whose power at the power sourcing equipment does
   not exceed :math:`P_\text{out}`. :doc:`poe/translation` explains how the class is
   advertised and gives worked examples for each USB Power Delivery offer.

Ethernet in, Ethernet out
   The supplying Ethernet port advertises the highest class that fits, in
   the same way.

When the input changes, for example when the USB charger offers a different
power or a role swap moves the input to another port, the software first
reduces the offers on the outputs to fit the new budget. It then accepts the
new input.

.. _power-sharing:

The software shares the budget between output ports
---------------------------------------------------

On a board with more than one port that can supply power (see
:numref:`tab-power-board-configs`), several ports can supply power at the
same time. These are both USB Type-C ports, a USB Type-C port and an
Ethernet port, or both Ethernet ports when the board is powered from USB.
The software then shares :math:`P_\text{out}` between those ports, so that
the sum of the power offered on all of them never exceeds it:

.. math::

   \sum_i P_{\text{offer},i} \le P_\text{out}

where :math:`P_{\text{offer},i}` is the maximum power offered on output
port :math:`i`, in watts.

Each port starts with a share of the budget. A USB Power Delivery source can
change its offer while a device is connected, by sending a new list of
offers. Power sourcing equipment can change the power it allocates to a
powered device through :term:`LLDP` (:clause:`145.5`, :clause:`79`), when
the powered device supports it. :doc:`poe/sharing` gives which powered
devices do, and the alternative for those that don't.

The software uses these changes to move power between ports. When a device
on one port is unplugged or uses less than its share, the software raises
the offer on another port. When a new device is plugged in, the software
first lowers the offers on the other ports to make room. :doc:`usb-pd/index` and
:doc:`poe/sharing` describe how the budget is divided, and how a port's offer is
reduced safely while a device is using it.

.. _power-board-configs:

The board comes in two configurations
-------------------------------------

:numref:`tab-power-board-configs` describes the two board configurations,
the first version and the full design.

.. list-table:: The two board configurations
   :name: tab-power-board-configs
   :header-rows: 1
   :widths: 40 30 30

   * - Feature
     - First version
     - Full design
   * - Ethernet transceivers
     - External chips, connected over RGMII
     - Integrated on evampire
   * - Connection to the cable
     - Coupling transformers
     - No coupling transformers
   * - Ethernet port A power role
     - Receives power
     - Either role
   * - Ethernet port B power role
     - Supplies power
     - Either role
   * - USB Type-C ports
     - 1
     - 2
   * - USB Type-C port power role
     - Dual-role
     - Dual-role
   * - Converter gate drivers and power transistors
     - External parts
     - On evampire, except possibly some high-voltage switches

Which high-voltage switches stay external in the full design, and how it
makes the isolation without coupling transformers, are listed in
:ref:`requirements-open-questions`.

.. _power-flow:

All power passes through an internal power bus
----------------------------------------------

:numref:`fig-power-flow` shows how power flows on the first-version board.
All power passes through an internal power bus on the board.

.. graphviz:: index/power-flow.dot
   :name: fig-power-flow
   :caption: Power flow on the first-version board, where bold arrows carry
             power and dashed arrows carry control and status.
   :alt: Power flow diagram. Power from Ethernet port A passes through the
         powered device front end and the input voltage converter to the
         internal power bus. The USB Type-C port connects to the bus in both
         directions through the USB power path. The bus feeds the board
         supplies and the high-voltage converter, which feeds the power
         sourcing equipment switch and Ethernet port B. evampire controls
         and monitors each of these blocks.
   :align: center

The blocks in :numref:`fig-power-flow` do the jobs below. The converter
types named here are those of the first-version board. Whether the converter
functions are separate converters is an open question
(:ref:`requirements-open-questions`).

Powered device front end
   Sits on port A. It corrects the polarity of the cable voltage and
   presents the signature that tells the far end a powered device is
   connected. It limits the current while the input capacitors charge.
Input voltage converter
   Brings the 37 V to 57 V from the cable down to the bus voltage
   (:clause:`33`, :clause:`145`; see :doc:`poe/index`).
USB power path
   Connects the USB Type-C port to the bus. As a sink it is a switch that
   connects the negotiated USB supply voltage to the bus. As a source it is
   an adjustable voltage converter, a
   :wikipedia:`buck-boost converter <Buck%E2%80%93boost_converter>`, that
   produces the negotiated USB supply voltage from the bus. That voltage is
   5 V to 20 V, or up to 48 V in the extended power range
   (:pd:`PD Sections 3.2.4 and 3.2.5.3 <3.2.4>`, see :doc:`usb-pd/index`).
High-voltage converter
   A :wikipedia:`boost converter <Boost_converter>` that raises the bus
   voltage to the 44 V to 57 V needed on an Ethernet cable (:clause:`145`).
   A boost converter needs a bus below 44 V. It does not apply when the bus
   sits at a 48 V USB extended power range voltage.
Power sourcing equipment switch
   Checks for a valid powered device on port B and measures its
   :term:`class`, the power level the device asks for. It then connects the
   voltage with a current limit (see :doc:`poe/index`).

evampire carries out the negotiation in every case. It reads the power
granted on port A, drives and senses the USB :term:`configuration channel`,
sets the USB output voltage, and enables and monitors the power sourcing
equipment switch.

The software on evampire's processor makes every power decision: it runs
the negotiation on every port and switches power on and off. evampire
measures the voltage and current of every power port and of the power bus.
It enforces the current and power limit that the software sets for each
port, and switches a port off by itself when a fault is too fast for the
software to react.

evampire also controls the voltage converters: the input converter, the USB
converter and the high-voltage converter. Which converter parts are external
in each board configuration is given in :numref:`tab-power-board-configs`.
:doc:`converters/index` explains how these converters work and how more of each
can move onto the chip.

Many of these circuits handle voltages of up to 57 V on an Ethernet cable
and up to 48 V on USB. The standard transistors of the
`gf180mcu <https://gf180mcu-pdk.readthedocs.io/>`_ process have nominal
supplies of 3.3 V, 5 V or 6 V, with at most 10 % overshoot.\ [#gf180-supply]_
Its LDMOS transistors are characterised with a 10 V drain and a 6 V
gate.\ [#gf180-ldmos]_

Custom structures, such as transistors stacked in isolated wells,
drain-extended transistors and high-voltage capacitors, extend the voltages
that circuits on the chip can handle (see :ref:`the process requirements <req-process>`). The
full design builds most of these functions on chip
(:numref:`tab-power-board-configs`). The pages on :doc:`poe/index`, :doc:`usb-pd/index` and :doc:`converters/index`
analyse the choice for each standard.

.. [#gf180-supply] `gf180mcu design manual, section 14.1, "Power supply
   voltage limits"
   <https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_14_1.html#power-supply-voltage-limits>`__,
   and the 3.3 V, 5 V and 6 V device sections of the
   `gf180mcu electrical specifications
   <https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs.html>`__.

.. [#gf180-ldmos] `gf180mcu electrical specifications, section 8, "High
   Voltage LDMOS Transistor (10.0V)"
   <https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs.html>`__,
   whose saturation current is measured at a 10 V drain and a 6 V gate.

.. toctree::
   :maxdepth: 2
   :hidden:

   poe/index
   usb-pd/index
   converters/index
