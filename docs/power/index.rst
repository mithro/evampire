Power bridging
==============

A board built around evampire moves power between its Ethernet ports and its
:wikipedia:`USB Type-C <USB-C>` ports. It can be powered from an Ethernet
cable (:wikipedia:`Power over Ethernet <Power_over_Ethernet>`, :doc:`poe`) and supply power to a USB device, or be powered from a
USB Type-C charger (:wikipedia:`USB Power Delivery <USB_Power_Delivery>`,
:doc:`usb-pd`) and supply power to an
Ethernet device.

Both standards require the two ends of a cable to agree before full power is
applied. The end that supplies power first checks that a compatible device
is connected, then the two ends agree how much power may flow. evampire takes
part in this exchange on every port, in whichever role that port has.

.. _power-roles:

Roles
-----

Each standard has its own names for the two ends of a cable.

.. list-table:: Names for the two ends of a powered cable
   :header-rows: 1
   :widths: 30 35 35

   * - Standard
     - End that supplies power
     - End that receives power
   * - Power over Ethernet
     - Power sourcing equipment
     - Powered device
   * - USB Power Delivery
     - Source
     - Sink

A USB Type-C port that can act as either a source or a sink is called a
*dual-role* port. When two dual-role ports are connected, the roles are
decided when the cable is plugged in, and the two ends can later exchange
messages to swap roles without unplugging the cable (see :doc:`usb-pd`).

A Power over Ethernet port has a fixed role while it is connected. Supplying
and receiving power need different circuits on the board, so a port that can
take either role has both sets of circuits and selects one before a cable is
connected (see :doc:`poe`).

.. _power-modes:

Operating modes
---------------

Ethernet in, USB out
   An Ethernet port receives power as a powered device. The USB Type-C port
   acts as a source and offers power to the attached device.

USB in, Ethernet out
   The USB Type-C port acts as a sink and requests power from the attached
   charger. An Ethernet port supplies power as power sourcing equipment.

Ethernet in, Ethernet out
   One Ethernet port receives power and the other supplies it.

.. _power-budget:

In every mode the processor keeps a power budget. The power it offers on
the output ports never exceeds the power granted on the input port, minus the
power the board itself uses and the losses in the voltage converters. When
the granted input power changes, for example after a USB role swap, the
processor lowers the power offered on the outputs first.

.. _power-board-configs:

Board configurations
--------------------

.. list-table:: Port roles in each board configuration
   :header-rows: 1
   :widths: 25 25 25 25

   * - Configuration
     - Ethernet port A
     - Ethernet port B
     - USB Type-C ports
   * - First version
     - Receives power
     - Supplies power
     - One, dual-role
   * - Full design
     - Either role
     - Either role
     - Two, each dual-role

.. _power-flow:

Power flow
----------

.. graphviz:: index/power-flow.dot
   :caption: Power flow on the first-version board. Bold arrows carry power.
             Dashed arrows carry control and status.
   :align: center

All power passes through an internal power bus on the board.

* The **powered device front end** on port A corrects the polarity of the
  cable voltage, presents the signature that tells the far end a powered
  device is connected, and limits the current while the input capacitors
  charge. The input voltage converter brings the 37 V to 57 V from the
  cable down to the bus voltage (:clause:`33`, :clause:`145`; see
  :doc:`poe`).
* The **USB power path** connects the USB Type-C port to the bus. As a sink
  it is a switch that connects the negotiated USB supply voltage to the bus.
  As a source it is an adjustable voltage converter (a
  :wikipedia:`buck-boost converter <Buck%E2%80%93boost_converter>`) that produces the
  negotiated USB supply voltage (5 V to 20 V, or up to 48 V in the extended
  range; see :doc:`usb-pd`) from the bus.
* The **high-voltage converter** (a
  :wikipedia:`boost converter <Boost_converter>`) raises the bus voltage to the 44 V to 57 V
  needed on an Ethernet cable (:clause:`145`), and the **power sourcing
  equipment switch** checks for a valid powered device on port B, measures
  its class (the power level the device asks for), and then connects the
  voltage with a current limit (see :doc:`poe`).

evampire carries out the negotiation in every case: it reads the power
granted on port A, drives and senses the USB configuration channel wires
(the two wires of a USB Type-C connector that carry the power negotiation),
sets the USB output voltage, and enables and monitors the power sourcing
equipment switch.

evampire also controls the three voltage converters: the input converter,
the USB converter and the high-voltage converter. In the first version the
power transistors and their gate drivers are external parts and evampire
provides the control; :doc:`converters` explains how these converters work
and how more of each can move onto the chip.

Many of these circuits handle voltages (up to 57 V on an Ethernet cable and
up to 48 V on USB) far above the continuous ratings of the standard
transistors in the `gf180mcu <https://gf180mcu-pdk.readthedocs.io/>`_
process. The standard parts of the process do
not set the limit of what can be built on the chip: custom structures, such
as transistors stacked in isolated wells, drain-extended transistors, and
high-voltage capacitors, can extend what is possible. Which functions are
built on evampire and which use external parts is a design choice made per
function, and the following pages analyse it for each standard.

.. toctree::
   :maxdepth: 2

   poe
   usb-pd
   converters
