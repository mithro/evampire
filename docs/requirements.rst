.. _requirements:

Requirements
============

This page lists every requirement that the evampire design meets, grouped
by function, and ends with the questions that are still open. The two board
configurations, the first version and the full design, are described in
:numref:`tab-power-board-configs`. Each term is described in the
:doc:`glossary`.

.. _req-transceivers:

Every port runs gigabit Ethernet through an Ethernet transceiver
----------------------------------------------------------------

* Each external port uses an :term:`Ethernet transceiver`. The transceiver
  is an external chip or is integrated on evampire, depending on the board
  configuration (:numref:`tab-power-board-configs`).
* An external transceiver connects to evampire over an :term:`RGMII`
  interface. See :doc:`ethernet/rgmii/index`.
* An integrated transceiver includes the line driver and receiver, and the
  analogue-to-digital and digital-to-analogue converters. See
  :doc:`ethernet/phy-electrical/index`.
* An integrated transceiver also includes the signal processing that removes
  :wikipedia:`echo <Echo_suppression_and_cancellation>`,
  :wikipedia:`crosstalk <Crosstalk>` and cable loss, together with
  :wikipedia:`clock recovery <Clock_recovery>`,
  :wikipedia:`line coding <Line_code>` and
  :wikipedia:`automatic speed negotiation <Autonegotiation>`.
* The :term:`forwarding logic` connects to an integrated transceiver through
  the same one-byte-per-clock interface that it uses with an RGMII
  interface.
* Every port supports gigabit Ethernet (1000BASE-T, 1000 Mbit/s over four
  pairs, :clause:`40`) in both board configurations. An integrated
  transceiver therefore implements 1000BASE-T.

.. _req-cable:

Each port connects to its RJ45 socket with or without transformers
------------------------------------------------------------------

* Each Ethernet port connects to its :term:`RJ45` socket either through
  coupling transformers, the :term:`magnetics`, or without them, depending
  on the board configuration (:numref:`tab-power-board-configs`).
* Without coupling transformers, the board still does the transformers'
  jobs: electrical isolation, rejecting the voltage that is common to both
  wires of a pair, and giving a path for Power over Ethernet current (see
  :doc:`power/poe/index`). How the isolation is made is an open question
  (:ref:`requirements-open-questions`). See :doc:`ethernet/magnetics/index`.

.. _req-forwarding:

Ports A and B forward every frame to each other, except LLDP frames
-------------------------------------------------------------------

* Every :term:`frame` received on port A is transmitted on port B, and every
  frame received on port B is transmitted on port A, except the frames
  described in the next item.
* :term:`LLDP` frames (:std:`IEEE 802.1AB <802.1AB>`), sent to the
  destination address ``01-80-C2-00-00-0E``, are not forwarded. They carry
  the Power over Ethernet power negotiation between the two ends of one
  cable (:clause:`79`, see :doc:`power/poe/index`). Forwarding them would let a
  device on one port negotiate power with the device on the other port.
  They are delivered only to the internal processor, which handles the power
  negotiation for its own port.
* Forwarding is :term:`cut-through <cut-through forwarding>`. The delay
  through the chip is a small fixed number of clock cycles, not a whole
  frame.
* Cut-through forwarding needs both ports to run at the same link speed.
  :doc:`ethernet/rgmii/index` explains why.
* Forwarded frames are passed on unchanged.
* No whole frame is stored on the forwarding path. The longest frame that
  can be forwarded is set by the slack in the rate-matching buffer, as
  described below.

The receive and transmit clocks of a forwarding path differ by up to
200 parts per million, because Gigabit Ethernet allows each end of a cable
to be up to 100 parts per million from 125 MHz (:clause:`40`). Over one
frame, the rate-matching buffer between them fills or empties by that
fraction of the frame's length. The longest frame is the one that uses up
the buffer's slack:

.. math::

   L_\text{max} \approx \frac{S}{\Delta f / f}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`L_\text{max}`
     - Longest frame that can be forwarded
     - byte
   * - :math:`S`
     - Slack of the rate-matching buffer: the number of bytes it can gain
       or lose from its centre point
     - byte
   * - :math:`\Delta f / f`
     - Largest fractional difference between the receive and transmit
       clocks, :math:`200 \times 10^{-6}`
     - none

For example, a slack of 2 bytes gives
:math:`L_\text{max} \approx 2 / (200 \times 10^{-6}) = 10\,000` bytes,
which is longer than a 9000-byte jumbo frame.

.. _req-processor-delivery:

The processor receives the frames that match its address filter
---------------------------------------------------------------

* Each received frame's destination :term:`MAC address` is compared against
  a programmable address and mask pair. A frame matches when every bit set
  in the mask is equal in the destination address and the programmed
  address.
* Matching frames are copied into a receive buffer that the processor can
  read.
* The receive checksum, the :term:`frame check sequence`, is checked in
  hardware. A frame with a bad checksum is not given to the processor.

.. _req-processor-transmit:

The processor sends frames in the gaps between forwarded frames
---------------------------------------------------------------

* The processor writes a frame into a transmit buffer and requests that it
  be sent out of port A, port B or both.
* The chip adds the frame's :term:`start pattern` and checksum.
* Processor frames are sent only in the gaps between forwarded frames.

.. _req-memory:

Only the processor's frames are stored whole
--------------------------------------------

* The chip does not store full frames on the forwarding path.
* Frame storage for the processor holds one or two frames of up to
  1522 bytes in each direction. With two frames, the processor can work on
  one frame while the hardware fills or empties the other.
* The 1522 bytes are 1500 bytes of payload, the two 6-byte addresses, the
  2-byte type field, the 4-byte checksum and an optional 4-byte
  :term:`VLAN tag` (:std:`IEEE 802.1Q <802.1Q>`, :clause:`3`).
* Frames longer than the processor's buffer, for example
  :wikipedia:`jumbo frames <Jumbo_frame>` of up to about 9000 bytes, are
  still forwarded between ports A and B, but are not delivered to the
  processor.

.. _req-processor:

A small RISC-V processor handles low-rate traffic and control
-------------------------------------------------------------

* The processor is a :wikipedia:`RISC-V` core with on-chip program and data
  memory (:std:`RISC-V ISA <riscv-unpriv>`).
* The processor's network traffic is below 1 Mbit/s. The processor does not
  need to keep up with gigabit traffic.
* Each page states only what it needs from the processor, such as
  operations per second, latency or bits per cycle, and assumes no
  particular core, clock or core supply voltage.
* The processor controls the configuration interface of each external
  transceiver, the :term:`MDIO` interface (:clause:`22`, see
  :doc:`ethernet/rgmii/index`).

.. _req-power-bridging:

Power moves between Ethernet and USB Type-C in either direction
---------------------------------------------------------------

A board built around evampire takes its power from an Ethernet cable
(:term:`Power over Ethernet`, see :doc:`power/poe/index`) or from a
:term:`USB Type-C` connector (:term:`USB Power Delivery`, see
:doc:`power/usb-pd/index`). It passes that power on through the other kind of
port. The section on :ref:`power roles <power-roles>` explains the names of
the two ends of a powered cable, and :numref:`tab-power-board-configs` gives the role of each port in
each board configuration.

The board works in these modes:

Ethernet in, USB out
   evampire receives power from an Ethernet port as a
   :term:`powered device` and supplies power on a USB Type-C port as a USB
   Power Delivery :term:`source`.
USB in, Ethernet out
   evampire receives power from a USB Type-C port as a USB Power Delivery
   :term:`sink` and supplies power on an Ethernet port as Power over
   Ethernet :term:`power sourcing equipment`.
Ethernet in, Ethernet out
   evampire receives power on one Ethernet port and supplies it on the
   other.

The requirements on power bridging are:

* Each USB Type-C port is a :term:`dual-role port`: it can attach as either
  a source or a sink, and can swap roles while connected, without
  unplugging.
* The power levels are negotiated on every port.
* The processor keeps a :term:`power budget`. The power offered on the
  output ports never exceeds the power granted on the input port, minus the
  board's own consumption and conversion losses.
* The software translates the power available on the input port into a
  valid offer in the standard used by each output port, as described below.
* When the input power changes, the offers on the outputs are updated to
  match, and are reduced before the input power falls. See
  :ref:`translating power between the standards <power-translation>`.
* When more than one port supplies power at the same time, the software
  shares the output budget between them. It moves power from one port to
  another when a device needs less, asks for more, or is unplugged. See
  :ref:`sharing the budget <power-sharing>`.
* USB Power Delivery is implemented mostly in software on the RISC-V
  processor. The dedicated hardware is the analogue circuits that connect to
  the :term:`configuration channel` wires (see :doc:`power/usb-pd/index`), and only
  those digital helpers whose timing cannot be met in software.

The software builds the offer on each output port from the power on the
input port:

Ethernet in, USB out
   From the Power over Ethernet power granted to the board, the software
   works out the USB Power Delivery source offer that fits in the budget and
   follows the USB Power Delivery rules. The offer is a list of voltage and
   current combinations.
USB in, Ethernet out
   From the power that the USB Power Delivery source provides, the software
   chooses the Power over Ethernet type and :term:`class` whose power fits
   in the budget. The port advertises that class when it supplies power.
Ethernet in, Ethernet out
   The software chooses the class in the same way, from the power granted on
   the other Ethernet port.

.. _req-power-control:

Software makes every power decision, within hardware limits
-----------------------------------------------------------

* Software on the RISC-V processor makes every power decision once it is
  running. It carries out the negotiation on every port, keeps the power
  budget, and switches power on and off on each port. The negotiation is
  Power over Ethernet detection and classification in both roles, and USB
  Power Delivery.
* The only exception is the start-up sequencer described below, which works
  before the processor is running.
* evampire has built-in power monitoring. It measures the voltage and
  current of every power port and of the board's power bus, so that the
  software can read the power flowing through each of them at any time.
* A board powered only from one port starts from nothing. Before a Power
  over Ethernet power source has detected the board and switched its power
  on, the cable carries only small test voltages and currents, for limited
  times.
* evampire has a small built-in start-up sequencer, working without the
  processor, that answers the detection and classification steps and
  requests a power level. Once the processor is running, the software
  carries out any further negotiation, for example asking for more power.
* evampire has built-in power limiting. Each port has a current and power
  limit that the software sets.
* Built-in hardware enforces these limits. It switches a port off when a
  fault happens faster than software can react, for example a short
  circuit, and then reports the fault to the software.

.. _req-converters:

evampire includes the functions of three voltage converters
-----------------------------------------------------------

* evampire includes the functions of the three
  :wikipedia:`switching voltage converters <Switched-mode_power_supply>` in
  the power path. See :doc:`power/converters`. The three functions are:

  - bringing the Power over Ethernet input down to the board's power bus;
  - producing the USB Type-C output voltage when a USB port is a source;
  - producing the 44 V to 57 V needed to supply Power over Ethernet.

* evampire controls the converters. Which converter parts are external, in
  each board configuration, is given in :numref:`tab-power-board-configs`.

.. _req-usb-serial:

Each USB Type-C port carries a USB serial port
----------------------------------------------

* Each USB Type-C port can also carry a :std:`USB 2.0 <usb2>` full-speed
  (12 Mbit/s) data connection on its D+ and D− wires.
* Through this connection the RISC-V processor appears to a computer as a
  :wikipedia:`USB serial port <USB_communications_device_class>`, a device
  of the communications device class (:std:`USB CDC <usb-cdc>`).
* The USB data protocol is implemented mostly in software on the
  processor. Built-in hardware assists only where the timing of USB cannot
  be met in software. :doc:`usb-serial` analyses how the work is split
  between hardware and software.

.. _req-process:

evampire is built on gf180mcu, with custom devices where a function needs them
-------------------------------------------------------------------------------

* The chip targets the `gf180mcu <https://gf180mcu-pdk.readthedocs.io/>`_
  process through `wafer.space <https://wafer.space/>`_.
* The design uses custom device and cell designs beyond the standard devices
  and cells of the gf180mcu process design kit (PDK) wherever a function
  needs them. Examples are custom transistor layouts, standard cells using
  non-traditional logic styles, parasitic bipolar transistors, stacked or
  drain-extended devices, and custom I/O cells.
* A function for which the PDK has no standard device or cell is therefore
  not placed off-chip for that reason alone.

.. _requirements-open-questions:

Open questions
--------------

* Whether an integrated transceiver also supports 100 Mbit/s and 10 Mbit/s
  Ethernet, in addition to 1000BASE-T.
* The cable reach of the integrated gigabit transceiver. The pages treat it
  as a parameter and give their results as a function of reach.
* How the isolation is made without coupling transformers. Three routes
  are explored:

  - external high-voltage capacitors or other external parts;
  - a second die on the cable side, either a custom gf180mcu die or a
    commercial part;
  - an isolation barrier on the evampire die.

* The processor core, its clock frequency, its core supply voltage and the
  cell library it is built from.
* Whether any frames other than LLDP frames must not be forwarded, and for
  what reason.
* The maximum power that the board supports.
* How much power evampire and the rest of the board need, both to start and
  in normal operation, and so how much the start-up sequencer must do.
  :doc:`power/poe/index` gives the power available during Power over Ethernet
  detection and classification and at each class. :doc:`power/usb-pd/index` gives
  the power available from a USB Type-C charger at each basic current level
  before any USB Power Delivery negotiation.
* Whether the three converter functions are three separate converters, one
  converter whose connections change with the operating mode, or another
  arrangement. The input and output voltage ranges of USB Power Delivery and
  Power over Ethernet overlap, which makes sharing possible.
* Whether the full design moves the converters' gate drivers, and then their
  power transistors, onto evampire.
