References
==========

The datasheets, application notes, test suites and design libraries cited
on the RGMII pages. Standards, such as IEEE 802.3, the RGMII specification
and the JEDEC logic-level standards, are listed on the :doc:`standards page <../../standards>`.

Ethernet transceivers and controllers
-------------------------------------

.. [RGMII-DP83867] Texas Instruments, `DP83867IR/CR Robust, High Immunity
   10/100/1000 Ethernet Physical Layer Transceiver, datasheet SNLS484J
   <https://www.ti.com/lit/ds/symlink/dp83867ir.pdf>`__, 2015-02, revised
   2026-06.

.. [RGMII-SNLA243] Texas Instruments, `RGMII Interface Timing Budgets,
   application report SNLA243
   <https://www.ti.com/lit/an/snla243/snla243.pdf>`__, 2015-10.

.. [RGMII-KSZ9031] Microchip Technology, `KSZ9031RNX Gigabit Ethernet
   Transceiver with RGMII Support, datasheet DS00002117F
   <https://ww1.microchip.com/downloads/en/DeviceDoc/00002117F.pdf>`__,
   2016 to 2017.

.. [RGMII-LAN91C111] Microchip Technology, `LAN91C111 10/100 Non-PCI Ethernet
   Single Chip MAC + PHY, datasheet DS00002276A
   <https://ww1.microchip.com/downloads/en/DeviceDoc/00002276A.pdf>`__,
   2011 to 2016. A 10/100 Ethernet controller with a built-in transceiver.

.. [RGMII-ENC28J60] Microchip Technology, `ENC28J60 Stand-Alone Ethernet
   Controller with SPI Interface, datasheet DS39662E
   <https://ww1.microchip.com/downloads/en/DeviceDoc/39662e.pdf>`__,
   2006 to 2012.

Conformance test suites
-----------------------

These test suites quote the subclause numbers of the 2012 edition of
IEEE 802.3. They are used here as second sources for values given in
IEEE 802.3-2022.

.. [RGMII-IOL-MAC] University of New Hampshire InterOperability Laboratory,
   `MAC Test Suite, version 5.3
   <https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/MAC/MAC_Test_Suite_v5.3.pdf>`__,
   2015-06-04.

.. [RGMII-IOL-REG] University of New Hampshire InterOperability Laboratory,
   `Management Registers Test Suite, version 4.1
   <https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/Management_Register_Test_Suite/Management_Register_Test_Suite_v4.1.pdf>`__,
   2016-10-25.

gf180mcu libraries and designs
------------------------------

.. [RGMII-GF180IO] GlobalFoundries and Google, `gf180mcu_fd_io I/O cell
   library <https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_io>`__:
   datasheet and Liberty timing files of the cell gf180mcu_fd_io__bi_t.

.. [RGMII-GF180SC] GlobalFoundries and Google, `gf180mcu_fd_sc_mcu9t5v0
   standard-cell library
   <https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_sc_mcu9t5v0>`__:
   Liberty timing files of the cells buf_2 and dffq_1.

.. [RGMII-OCDIO] R. Timothy Edwards, `gf180mcu_ocd_io
   <https://github.com/RTimothyEdwards/gf180mcu_ocd_io>`__, a split-voltage
   version of the gf180mcu I/O library with a 5.0 V pad and a 3.3 V core.

.. [RGMII-OCDPADFRAME] R. Timothy Edwards, `gf180mcu_caravel_padframe
   <https://github.com/RTimothyEdwards/gf180mcu_caravel_padframe>`__, a
   padframe built from gf180mcu_ocd_io cells.

.. [RGMII-IORE] `gf180mcu_io_re <https://github.com/89Mods/gf180mcu_io_re>`__,
   schematics of the gf180mcu_fd_io__bi_24t pad cell reverse-engineered from
   its layout.

.. [RGMII-WAFERSPACE] wafer.space, `gf180mcu Project Template
   <https://github.com/wafer-space/gf180mcu-project-template>`__: the
   README sections on standard-cell and I/O pad libraries.

Delay elements in other devices
-------------------------------

.. [RGMII-UG953] AMD, `Vivado Design Suite 7 Series FPGA and Zynq 7000 SoC
   Libraries Guide (UG953), IDELAYE2 and IDELAYCTRL primitives
   <https://docs.amd.com/r/2022.2-English/ug953-vivado-7series-libraries/IDELAYE2>`__,
   2022.
