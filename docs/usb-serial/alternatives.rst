Alternative ways to provide a serial port
=========================================

This page lists other ways to give evampire's processor a serial channel to
a computer, including some that other projects avoid. For each it gives the
reason others avoid it and whether that reason applies to evampire. All of
them remain open (see `Open questions`_).

USB low speed instead of full speed
-----------------------------------

At low speed a bit lasts 666.7 ns instead of 83.33 ns, eight times longer,
so pure software needs an eighth of the instruction rate worked out in
:doc:`software-cost`. Small microcontrollers use this: V-USB runs a
low-speed device on an AVR at 12 MHz to 20 MHz with no USB hardware
([USBSER-VUSB]_, ``Readme.txt``), and rv003usb runs one on a 48 MHz
CH32V003 RISC-V microcontroller ([USBSER-RV003USB]_).

The USB 2.0 specification restricts low-speed devices:

* no bulk endpoints, which CDC-ACM uses for its data
  ([USBSER-USB2]_ section 5.8.3);
* interrupt endpoints of at most 8 bytes per packet, polled at most every
  10 ms ([USBSER-USB2]_ section 5.7.3, section 5.7.4), which is 800 bytes
  per second per direction.

The projects deal with this in different ways. V-USB offers bulk endpoints
anyway and notes that the specification forbids them ([USBSER-VUSB]_,
``usbdrv.h``). The AVR-CDC serial port built on it needs a patch driver on
older Windows. It does not work on Windows 8 or later, which load the
standard CDC driver without it ([USBSER-AVRCDC]_). rv003usb's CDC-ACM experiment uses
interrupt endpoints for the data and is marked as tested on Linux
([USBSER-RV003USB]_, ``testing/cdc_exp``).

For evampire, the specification limits apply as they do to everyone. A
low-speed device that is not CDC-ACM, for example a vendor-specific or human
interface device with a small program on the computer, stays within the
specification at the cost of the no-driver property of :doc:`what-it-is`.

Oversampling or clock recovery in the receiver
----------------------------------------------

Most hardware USB receivers oversample four times per bit
(:doc:`software-cost`). A receiver can instead take one sample per bit at a
phase set from each edge, or rely on a clock locked to the host's frames
(:doc:`timing`). The FPGA cores cited there oversample at 48 MHz and run the rest of their
logic at 12 MHz ([USBSER-FOBOOT]_, ``hw/foboot-bitstream.py``).
On a custom chip the choice is between more fast flip-flops and a finer
phase adjustment, and either is open.

A serial channel over the configuration channel
-----------------------------------------------

USB Power Delivery carries messages on the CC wire, which evampire's
software already drives and samples (:doc:`/power/usb-pd`). Its
*vendor-defined messages* can carry a vendor's own data: up to six 32-bit
data objects, 24 bytes, after a header that names the vendor
(:pd:`Section 6.4.12`). Data would therefore move without the D+ and D−
front end at all.

The rules limit this: unstructured vendor-defined messages may be sent only
after a power agreement, only the DFP may start them, only the UFP may
answer, and a port may start them only for an active alternate mode
(:pd:`Section 8.4`). The computer side also needs software that can send
such messages through its own USB Power Delivery controller, which no
standard serial driver does.

The channel is slow, at the 300 kbit/s of the
CC wire with a reply for each message. It suits a link between two boards
that both run evampire's software better than a link to a computer.

Debug accessory mode
--------------------

USB Type-C defines a *debug accessory mode*, entered when both CC pins see
the same termination, in which the connector's pins are reassigned for
debugging closed devices (:typec:`Section B.1`, :typec:`Section B.2`). The
transport on the reassigned pins is left to the vendor. It needs a special
debug cable or adapter at the computer, so it does not give a serial port on
an ordinary cable.

An external USB-to-serial bridge
--------------------------------

A separate USB-to-UART bridge chip on the board, connected to the
connector's D+ and D− and to a UART on evampire, gives a CDC or
vendor-driver serial port with no USB logic on evampire. It costs a board
part and a UART on the chip, and the bridge still has to follow the data
role rules of :doc:`usb-pd-roles`. It can serve the first version while the
on-chip serial port is developed.

A console over Ethernet
-----------------------

The processor already sends and receives Ethernet frames
(:doc:`/overview`). A console over the network needs no USB at all, but it
needs a working network and an address on it, which is what a configuration
console is often used to set up.

Open questions
--------------

* Full speed CDC-ACM as the default, with low speed, the configuration
  channel, an external bridge or an Ethernet console as alternatives or
  additions, especially for the first version.
* Oversampling or single-sample clock recovery in the receiver.
