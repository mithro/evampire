References
==========

The specifications, datasheets and projects cited on the USB serial port
pages. Each citation in the text gives the section, table or file within
the source.

Specifications
--------------

.. [USBSER-USB2] USB Implementers Forum, `Universal Serial Bus
   Specification, Revision 2.0
   <https://www.usb.org/document-library/usb-20-specification>`__,
   2000-04-27, with its errata and engineering change notices (download
   ``usb_20_20250603.zip``, file ``usb_20.pdf``).

.. [USBSER-CDC] USB Implementers Forum, `Class Definitions for
   Communications Devices, Revision 1.2
   <https://www.usb.org/document-library/class-definitions-communication-devices-12>`__,
   with errata and engineering change notices through 2025-04-03 (download
   ``CDC1.2_WMC1.1_012011_0.zip``, file
   ``CDC120_with_Errata_and_ECN_through_Apr_3_2025.pdf``).

.. [USBSER-PSTN] USB Implementers Forum, `Universal Serial Bus
   Communications Class Subclass Specification for PSTN Devices,
   Revision 1.2
   <https://www.usb.org/document-library/class-definitions-communication-devices-12>`__,
   2007-02-09 (in the same download as [USBSER-CDC]_, file
   ``PSTN120.pdf``).

The USB Type-C and USB Power Delivery specifications are listed on the
:doc:`standards page </standards>`.

Operating system drivers
------------------------

.. [USBSER-WIN-USBSER] Microsoft, `USB serial driver (Usbser.sys)
   <https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/usb-driver-installation-based-on-compatible-ids>`__,
   Windows hardware developer documentation.

.. [USBSER-WIN-CLASSES] Microsoft, `USB device class drivers included in
   Windows
   <https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/supported-usb-classes>`__,
   Windows hardware developer documentation.

.. [USBSER-LINUX-ACM] The Linux kernel documentation, `Linux ACM driver
   <https://docs.kernel.org/usb/acm.html>`__.

.. [USBSER-APPLE-CDC] Apple, `AppleUSBCDCDriver source
   <https://github.com/apple-oss-distributions/AppleUSBCDCDriver>`__,
   tag AppleUSBCDCDriver-4303.2.1.

USB device implementations
--------------------------

.. [USBSER-VUSB] Objective Development, `V-USB
   <https://www.obdev.at/products/vusb/index.html>`__, software-only
   low-speed USB device for AVR microcontrollers; `source
   <https://github.com/obdev/v-usb>`__.

.. [USBSER-AVRCDC] O. Tamura, `AVR-CDC
   <http://www.recursion.jp/prose/avrcdc/>`__, a CDC-ACM serial port built
   on V-USB.

.. [USBSER-RV003USB] C. Lohr, `rv003usb
   <https://github.com/cnlohr/rv003usb>`__, software USB low-speed device
   for the CH32V003 RISC-V microcontroller.

.. [USBSER-PICO-PIO-USB] sekigon-gonnoc, `Pico-PIO-USB
   <https://github.com/sekigon-gonnoc/Pico-PIO-USB>`__, USB host and device
   using the programmable I/O of the RP2040 and RP2350.

.. [USBSER-VALENTYUSB] im-tomu, `ValentyUSB
   <https://github.com/im-tomu/valentyusb>`__, full-speed USB device core
   written in Migen and LiteX.

.. [USBSER-FOBOOT] im-tomu, `Foboot <https://github.com/im-tomu/foboot>`__,
   the bootloader of the Fomu iCE40UP5K FPGA board, built with ValentyUSB.

.. [USBSER-TINYFPGA] TinyFPGA, `TinyFPGA bootloader
   <https://github.com/tinyfpga/TinyFPGA-Bootloader>`__, a USB serial port
   to SPI flash bridge in FPGA logic.

.. [USBSER-ULIXXE] ulixxe, `usb_cdc
   <https://github.com/ulixxe/usb_cdc>`__, Verilog full-speed USB CDC-ACM
   device.

.. [USBSER-TTGF130] Tiny Tapeout, `GF 0.2 project 130: USB CDC (Serial)
   Device <https://tinytapeout.com/chips/ttgf0p2/130>`__, made in gf180mcu
   through wafer.space; `source <https://github.com/urish/tt-usbcdc-device>`__.

.. [USBSER-TT04-USBCDC] Tiny Tapeout, `TT04 project 101: USB CDC (Serial)
   <https://tinytapeout.com/runs/tt04/101>`__, made in SkyWater 130 nm.

gf180mcu process data
---------------------

.. [USBSER-GF180-SC] GlobalFoundries, `gf180mcu_fd_sc_mcu7t5v0 standard
   cell library
   <https://gf180mcu-pdk.readthedocs.io/en/latest/digital/standard_cells/gf180mcu_fd_sc_mcu7t5v0/index.html>`__:
   cell gf180mcu_fd_sc_mcu7t5v0__dffq_1, and the `databook conditions
   <https://gf180mcu-pdk.readthedocs.io/en/latest/digital/standard_cells/gf180mcu_fd_sc_mcu7t5v0/setup.html>`__
   (typical corner, 5.00 V, 25 °C).

.. [USBSER-GF180-IO] GlobalFoundries, `gf180mcu_fd_io 5 V I/O library
   <https://gf180mcu-pdk.readthedocs.io/en/latest/IPs/IO/gf180mcu_fd_io/index.html>`__:
   cell list, operating conditions, electrical characteristics, control
   pins and ESD protection pages.

.. [USBSER-GF180-IO-LIB] GlobalFoundries, `gf180mcu_fd_io library source
   <https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_io>`__:
   liberty file ``cells/bi_t/gf180mcu_fd_io__bi_t__tt_025C_3v30.lib``.

.. [USBSER-GF180-ELEC] GlobalFoundries, `GF180MCU electrical parameters
   specification
   <https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs.html>`__.
