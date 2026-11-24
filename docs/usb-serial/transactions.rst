Transactions and enumeration
============================

This page describes how the packets of :doc:`signalling` combine into
transactions and transfers, how the host recognises and configures a newly
attached device, and which descriptors and endpoints a USB serial port
needs. Section and table numbers refer to the :std:`USB 2.0 specification <usb2>`
[USBSER-USB2]_, the CDC specification [USBSER-CDC]_ and its PSTN subclass
specification [USBSER-PSTN]_.

Transactions
------------

A *transaction* is one exchange of up to three packets: a token from the
host, then a data packet from whichever side sends data, then a handshake
from the side that received it ([USBSER-USB2]_ section 8.5).
:numref:`tab-usbser-transactions` lists the three kinds a serial port uses,
and :numref:`fig-usbser-transactions` draws them.

.. list-table:: Transactions of a full-speed device ([USBSER-USB2]_
   section 8.4.6, section 8.5)
   :name: tab-usbser-transactions
   :header-rows: 1
   :widths: 16 22 30 32

   * - Transaction
     - Token (host)
     - Data packet
     - Handshake
   * - SETUP
     - SETUP
     - DATA0 with an 8-byte request, from the host
     - ACK from the device, always
   * - OUT
     - OUT
     - DATA0 or DATA1, from the host
     - ACK, NAK or STALL from the device
   * - IN
     - IN
     - DATA0 or DATA1 from the device, or NAK or STALL in its place
     - ACK from the host

.. graphviz:: transactions/transactions.dot
   :name: fig-usbser-transactions
   :caption: The packets of SETUP, OUT and IN transactions between the host
             and the device.
   :alt: Sequence diagram with host and device lanes. SETUP transaction:
         the host sends a SETUP token and DATA0 with an 8-byte request; the
         device always answers ACK. OUT transaction: the host sends an OUT
         token and DATA0 or DATA1; the device answers ACK when it took the
         data, NAK when it has no room yet, or STALL when the endpoint is
         halted. IN transaction: the host sends an IN token; the device
         answers DATA0 or DATA1, or NAK when no data is ready, or STALL;
         after a data packet the host answers ACK.
   :align: center

The device's replies follow fixed rules ([USBSER-USB2]_ section 8.4.6):

* To a SETUP token it must accept the following data packet and answer ACK.
  It may not answer NAK or STALL ([USBSER-USB2]_ section 8.4.6.4), so the
  device always needs room for an 8-byte request.
* To an OUT data packet it answers ACK when it has taken the data, NAK when
  it has no room yet, and STALL when the endpoint is halted
  ([USBSER-USB2]_ section 8.4.6.3, Table 8‑6).
* To an IN token it sends a data packet when it has data ready, and NAK
  when it has none ([USBSER-USB2]_ section 8.4.6.1, Table 8‑4).
* To any packet with an error it sends nothing.

A NAK is not an error. The host tries the same transaction again later, as
often as needed. A missing reply, in contrast, counts as an error; after
three errors in a row the host gives up the transfer
([USBSER-USB2]_ section 10.2.6). All of these replies have a deadline of a
few bit times, given in :doc:`timing`.

Data packets alternate between DATA0 and DATA1 on each endpoint. The
receiver compares the PID with the one it expects, so that a data packet
resent after a lost ACK is recognised as a copy and not stored twice. A
SETUP transaction resets the sequence to DATA0 ([USBSER-USB2]_ section 8.6).
:numref:`fig-usbser-retry` shows a lost ACK and a packet with an error.

.. graphviz:: transactions/retry.dot
   :name: fig-usbser-retry
   :caption: A lost ACK, recovered with the DATA0/DATA1 sequence bit, and a
             packet with an error, which gets no reply.
   :alt: Sequence diagram. The host sends an OUT token and DATA1; the
         device, expecting DATA1, stores the data and now expects DATA0. Its
         ACK is lost. The host repeats the OUT token and DATA1; the device
         sees DATA1 again, recognises a copy, does not store it twice, and
         answers ACK. Below, the host sends an IN token with a bad CRC; the
         device sends nothing, the host counts an error and retries, and
         after three errors in a row it gives up the transfer.
   :align: center

Transfer types and packet sizes
-------------------------------

Transactions are grouped into *transfers* of one of four types
([USBSER-USB2]_ chapter 5). A serial port uses three:

* *Control* transfers on endpoint 0, which every device has. A control
  transfer is a SETUP transaction with a request, optional IN or OUT data
  transactions, and a final status transaction in the opposite direction
  ([USBSER-USB2]_ section 8.5.3). The maximum data packet size on
  endpoint 0 at full speed is 8, 16, 32 or 64 bytes
  ([USBSER-USB2]_ section 5.5.3).
* *Bulk* transfers, for data that may wait for free bus time. The maximum
  packet size at full speed is 8, 16, 32 or 64 bytes
  ([USBSER-USB2]_ section 5.8.3). With 64-byte packets a single device can
  move at most 1 216 000 bytes per second ([USBSER-USB2]_ section 5.8.4,
  Table 5‑9).
* *Interrupt* transfers, polled by the host at an interval the device
  chooses.

Frames
------

The host divides time into 1 ms *frames*. It starts each one with a
start-of-frame (SOF) token that carries an 11-bit frame number; the interval
is 1.000 ms ± 500 ns ([USBSER-USB2]_ section 7.1.12, section 8.4.3,
Table 7‑9). A device does not reply to SOF. A full-speed device that has no
use for timing may ignore the content, but the SOF traffic keeps it out of
suspend ([USBSER-USB2]_ section 7.1.7.6). Because the frame interval comes
from the host's accurate clock, a device can measure it to correct its own
clock (see :doc:`timing`).

Enumeration
-----------

*Enumeration* is the sequence in which the host finds out what a newly
attached device is and configures it ([USBSER-USB2]_ section 9.1,
section 9.2.6, section 7.1.7.3):

1. The device connects its D+ pull-up within 100 ms of VBUS being valid
   (*TSIGATT*, [USBSER-USB2]_ Table 7‑14).
2. The host waits at least 100 ms for the connection to settle (*TATTDB*),
   then holds SE0 for at least 10 ms as a reset (*TDRST*,
   [USBSER-USB2]_ section 7.1.7.5).
3. After a 10 ms recovery time (*TRSTRCY*) the host reads the first bytes of
   the device descriptor at address 0, to learn the packet size of
   endpoint 0.
4. The host assigns an address with a SET_ADDRESS request. The device must
   complete it within 50 ms and use the new address 2 ms later
   ([USBSER-USB2]_ section 9.2.6.3).
5. The host reads the full device descriptor, the configuration descriptor
   with everything attached to it, and string descriptors if any
   ([USBSER-USB2]_ section 9.4.3).
6. The host selects the configuration with SET_CONFIGURATION
   ([USBSER-USB2]_ section 9.4.7). The device's other endpoints then work.

:numref:`fig-usbser-enumeration` shows the sequence with its time limits.

.. graphviz:: transactions/enumeration.dot
   :name: fig-usbser-enumeration
   :caption: Enumeration of a full-speed device, with the time limits of
             each step (not to scale).
   :alt: Sequence diagram with host and device lanes. VBUS becomes valid;
         the device turns its D+ pull-up on within 100 ms (TSIGATT). The
         host waits at least 100 ms (TATTDB), then sends a reset of SE0 for
         at least 10 ms (TDRST) and waits a 10 ms recovery (TRSTRCY). It
         asks for the device descriptor at address 0 and the device returns
         the first bytes with the endpoint 0 packet size. The host sends
         SET_ADDRESS, which completes within 50 ms, with the new address
         used 2 ms later. The host reads the device, configuration and
         string descriptors, each data packet within 500 ms, then sends
         SET_CONFIGURATION, after which the other endpoints work.
   :align: center

A request without a data stage must complete within 50 ms. For a request
that returns data, each data packet must follow within 500 ms
([USBSER-USB2]_ section 9.2.6.4). These limits are far longer than the
packet-level deadlines of :doc:`timing`, so the request handling itself is
ordinary software.

Serial port descriptors
-----------------------

A USB serial port uses the communications device class with the abstract
control model subclass (CDC-ACM, see :doc:`what-it-is`).
:numref:`tab-usbser-cdc` lists what the device reports in its
configuration descriptor, and :numref:`fig-usbser-descriptors` shows how
the descriptors nest.

.. list-table:: Descriptors and endpoints of a CDC-ACM serial port
   :name: tab-usbser-cdc
   :header-rows: 1
   :widths: 30 34 36

   * - Item
     - Value
     - Source
   * - Device class code
     - 02h, communications device
     - [USBSER-CDC]_ section 5.1.1, Table 8
   * - Communications interface: class, subclass
     - 02h, 02h (abstract control model)
     - [USBSER-CDC]_ section 4.2, section 4.3
   * - Communications interface: protocol
     - 00h, no class-specific protocol
     - [USBSER-CDC]_ section 4.4, Table 5
   * - Functional descriptors of that interface
     - Header, Call Management, Abstract Control Management, Union
     - [USBSER-CDC]_ section 5.2.3; [USBSER-PSTN]_ section 5.3.1, section 5.3.2
   * - Notification endpoint
     - One interrupt IN endpoint
     - [USBSER-CDC]_ section 3.4.1
   * - Data interface: class
     - 0Ah, data interface
     - [USBSER-CDC]_ section 4.5, Table 6; section 5.1.3, Table 10
   * - Data endpoints
     - One bulk IN and one bulk OUT endpoint
     - [USBSER-CDC]_ section 3.4.2

.. graphviz:: transactions/descriptors.dot
   :name: fig-usbser-descriptors
   :caption: The descriptors of a CDC-ACM serial port as a tree, with
             endpoint 0 and the ACM requests it carries.
   :alt: Tree: the device descriptor, class 02h, contains the configuration
         descriptor. The configuration contains a communications interface,
         class 02h, subclass 02h for the abstract control model and protocol
         00h, with the Header, Call Management, Abstract Control Management
         and Union functional descriptors and an interrupt IN endpoint for
         notifications; and a data interface, class 0Ah, with a bulk IN
         endpoint for data to the host and a bulk OUT endpoint for data from
         the host. Beside the tree, endpoint 0, the control endpoint of every
         device, carries SET_LINE_CODING, GET_LINE_CODING and
         SET_CONTROL_LINE_STATE.
   :align: center

With endpoint 0, the device has four endpoints: control, interrupt IN, bulk
IN and bulk OUT. Through endpoint 0 the host also sends three ACM requests
([USBSER-PSTN]_ section 6.3.10 to section 6.3.12):

* SET_LINE_CODING and GET_LINE_CODING, with the baud rate, stop bits,
  parity and character size of the emulated serial line. A port with no real
  serial line behind it stores the values and returns them;
* SET_CONTROL_LINE_STATE, with the two modem control signals DTR and RTS.
  The firmware can use DTR to tell whether the host software has marked the
  port as open.

Open questions
--------------

* The maximum packet size of endpoint 0 and of the bulk endpoints (8 to 64
  bytes), which sets the buffer sizes in :doc:`software-cost`.
* Whether the serial port shares the device with other interfaces, for
  example a firmware update interface, which would need an interface
  association descriptor (defined in an engineering change notice included
  with [USBSER-USB2]_).
