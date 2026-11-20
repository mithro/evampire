What a USB serial port is
=========================

This page describes what a computer sees when evampire's processor is
attached as a USB serial port, and what the port is for. How the bits get
there is on the following pages.

A serial port, seen from the computer
-------------------------------------

A :wikipedia:`serial port <Serial_port>` is a channel that carries a stream
of bytes in each direction between a computer and a device. On a computer it
appears as a named port, such as ``COM3`` on Windows or ``/dev/ttyACM0`` on
Linux, that a terminal program or a script can open, write to and read
from. The interface comes from the
:wikipedia:`UART <Universal_asynchronous_receiver-transmitter>`, a serial
line with its own connector; a USB device can present the same interface
to programs without any UART behind it.

The communications device class and the abstract control model
---------------------------------------------------------------

USB defines *device classes*: standard descriptions of a kind of device,
so that one driver in the operating system works with every device of that
kind. The *communications device class* (CDC) covers modems, network
adapters and similar devices [USBSER-CDC]_. Its *abstract control model*
(ACM) subclass was defined for modems controlled by
:wikipedia:`AT commands <Hayes_command_set>` ([USBSER-PSTN]_ section 3.2.2).
A device that is not a modem uses the same interface as a plain byte stream
in each direction (:wikipedia:`USB communications device class
<USB_communications_device_class>`). This combination is called CDC-ACM.

A CDC-ACM device has two interfaces: a communications interface, through
which the host sets the line parameters and receives status notifications,
and a data interface with one channel in each direction for the bytes
([USBSER-CDC]_ section 3.4). :doc:`transactions` lists the descriptors and
endpoints in detail.

Why no custom driver is needed
------------------------------

The common operating systems include a driver that binds to a CDC-ACM
interface by its class codes:

* Windows 10 and later load the built-in ``usbser.sys`` driver for a device
  with class 02h and subclass 02h ([USBSER-WIN-USBSER]_,
  [USBSER-WIN-CLASSES]_).
* Linux binds its ``cdc-acm`` driver and creates a ``/dev/ttyACM`` device
  ([USBSER-LINUX-ACM]_).
* macOS includes the AppleUSBCDCACM driver, which matches interface class 2,
  subclass 2 ([USBSER-APPLE-CDC]_, ``AppleUSBCDCACMControl-Info.plist``).

The device therefore appears as a serial port that any terminal program can
open. The class codes have to be exactly these: Windows does not load
``usbser.sys`` automatically when the subclass is not 02h
([USBSER-WIN-USBSER]_).

What the serial port is used for
--------------------------------

The serial port gives the firmware on evampire's processor a text channel
to a computer: a console for status and diagnostic messages, and a way to
read and change configuration, for example the power settings of the
:doc:`/power/index` pages. It needs no Ethernet network and no software on
the computer beyond a terminal program. The data rates involved are small
compared with the 12 Mbit/s of the link.

Open questions
--------------

* The commands and messages the firmware offers over the serial port.
