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
:numref:`tab-usbser-transactions` lists the three kinds a serial port uses.

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
configuration descriptor.

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
