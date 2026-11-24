USB serial port basics
======================

This page describes what a computer sees when evampire's processor is
attached as a USB serial port, and what the port is for. How the bits get
there is on the following pages.

The computer's view
-------------------

A :wikipedia:`serial port <Serial_port>` is a channel that carries a stream
of bytes in each direction between a computer and a device. On a computer it
appears as a named port, such as ``COM3`` on Windows or ``/dev/ttyACM0`` on
Linux, that a terminal program or a script can open, write to and read
from. The interface comes from the
:wikipedia:`UART <Universal_asynchronous_receiver-transmitter>`, a serial
line with its own connector; a USB device can present the same interface
to programs without any UART behind it (:numref:`fig-usbser-stack`).

.. graphviz:: what-it-is/stack.dot
   :name: fig-usbser-stack
   :caption: The layers between a terminal program and evampire's firmware,
             beside a UART serial line.
   :alt: Two columns of layers. USB serial port: terminal program or
         script, COM3 or /dev/ttyACM0, the operating system's CDC-ACM
         driver, the USB host controller, the USB cable with D+ and D−, and
         evampire's USB device and firmware. UART serial line: terminal
         program or script, COM1 or /dev/ttyS0, the operating system's
         serial driver, the computer's UART, the serial line with TX and
         RX, and the device's UART and firmware. A note says programs see
         the same interface.
   :align: center

Communications device class
---------------------------

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
endpoints in detail, and :numref:`fig-usbser-descriptors` shows how they
nest.

Operating system drivers
------------------------

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

Uses of the serial port
-----------------------

The serial port gives the firmware on evampire's processor a text channel
to a computer: a console for status and diagnostic messages, and a way to
read and change configuration, for example the power settings of the
:doc:`/power/index` pages. It needs no Ethernet network and no software on
the computer beyond a terminal program. The data rates involved are small
compared with the 12 Mbit/s of the link.

Open questions
--------------

* The commands and messages the firmware offers over the serial port.
