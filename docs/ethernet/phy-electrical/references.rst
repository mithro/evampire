References
==========

The standards, tutorials, datasheets and papers cited on the Ethernet
transceiver pages. Each citation in the text gives the subclause, section,
slide, table or figure within the source.

Standards and conformance tests
-------------------------------

.. [PHY-8023] IEEE, *IEEE Std 802.3-2022, IEEE Standard for Ethernet*. Its
   clauses are listed, with links, on the :doc:`standards page
   </standards>`.

.. [PHY-X3263] ANSI, *ANSI X3.263-1995, Fibre Distributed Data Interface
   (FDDI) - Token Ring Twisted Pair Physical Layer Medium Dependent
   (TP-PMD)*, the twisted-pair signalling that :clause:`25` adopts. See
   :std:`ANSI X3.263 <x3-263>`.

.. [PHY-UNH25] University of New Hampshire InterOperability Laboratory,
   `100BASE-TX PMD Test Suite, version 3.4
   <https://www.iol.unh.edu/sites/default/files/testsuites/ethernet/CL25_PMD/PMD_Test_Suite_v3.4.pdf>`__.

.. [PHY-UNH10T] University of New Hampshire InterOperability Laboratory,
   `10BASE-T MAU overview
   <https://www.iol.unh.edu/sites/default/files/knowledgebase/ethernet/10basetmau.pdf>`__.

Tutorials and presentations
---------------------------

.. [PHY-TUT98] C. Mick, C. DiMinico, S. Raghavan, S. Rao, M. Hatamian,
   `802.3ab (1000BASE-T) Tutorial
   <https://www.ieee802.org/3/tutorial/march98/mick_170398.pdf>`__, IEEE
   802.3 plenary, 1998-03. Slide numbers are the pages of the PDF.

.. [PHY-QAM97] O. Agazzi, M. Hatamian, H. Samueli, `Update on QAM-Based
   1000BASE-T Transceiver
   <https://www.ieee802.org/3/z/public/presentations/may1997/mhQAMfld.pdf>`__,
   IEEE 802.3, 1997-05.

.. [PHY-OSCAR97] O. Agazzi, M. Hatamian, H. Samueli, `Jitter Specifications
   for 1000Base-T
   <https://grouper.ieee.org/groups/802/3/ab/public/sept97/oscar2.PDF>`__,
   IEEE 802.3ab, 1997-09.

.. [PHY-CAM96] R. Cam, `Scrambling and 4LZS with Run Substitution
   <https://grouper.ieee.org/groups/802/3/z/public/presentations/nov1996/BHgutp_f.pdf>`__,
   IEEE 802.3z, 1996-11.

.. [PHY-HEALEY] A. Healey, `1000BASE-T Technology Overview, Part 1: Design
   Challenges
   <https://www.iol.unh.edu/sites/default/files/knowledgebase/ge/1000tcable.pdf>`__,
   University of New Hampshire InterOperability Laboratory, 1998. Slide
   numbers are the pages of the PDF.

Datasheets
----------

.. [PHY-KSZ9031] Microchip, `KSZ9031RNX Gigabit Ethernet Transceiver with
   RGMII Support, DS00002117F
   <https://ww1.microchip.com/downloads/en/DeviceDoc/00002117F.pdf>`__.

.. [PHY-DP83867] Texas Instruments, `DP83867IR/CR Robust, High Immunity
   10/100/1000 Ethernet Physical Layer Transceiver, SNLS484
   <https://www.ti.com/lit/ds/symlink/dp83867ir.pdf>`__.

.. [PHY-DP83848] Texas Instruments, `DP83848 PHYTER Single Port 10/100 Mb/s
   Ethernet Physical Layer Transceiver, SNLS266
   <https://www.ti.com/lit/ds/symlink/dp83848c.pdf>`__.

.. [PHY-DP83822] Texas Instruments, `DP83822 Robust, Low Power 10/100 Mbps
   Ethernet Physical Layer Transceiver
   <https://www.ti.com/lit/ds/symlink/dp83822i.pdf>`__.

.. [PHY-VSC8244] Microchip (Vitesse), `VSC8244 Quad 10/100/1000BASE-T PHY,
   VMDS-10108 <https://ww1.microchip.com/downloads/en/DeviceDoc/VMDS-10108.pdf>`__.
   Process and power per port on page 1.

.. [PHY-ED2000] Electronic Design, `Gigabit transceiver enables
   higher-port-density Ethernet switches
   <https://www.electronicdesign.com/technologies/industrial/boards/article/21782037/gigabit-transceiver-enables-higher-port-density-ethernet-switches>`__,
   2000-08-01. The Marvell Alaska 88E1000.

gf180mcu process and cells
--------------------------

.. [PHY-GF180PDK] GlobalFoundries and Google, `gf180mcu PDK documentation
   <https://gf180mcu-pdk.readthedocs.io/>`__: the electrical parameters
   specification and the design manual (source:
   `google/gf180mcu-pdk <https://github.com/google/gf180mcu-pdk>`__,
   ``docs/analog/spice/elec_specs`` and
   ``docs/physical_verification/design_manual``).

.. [PHY-GF180SC] GlobalFoundries, standard-cell libraries
   `gf180mcu_fd_sc_mcu7t5v0
   <https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_sc_mcu7t5v0>`__
   and `gf180mcu_fd_sc_mcu9t5v0
   <https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_sc_mcu9t5v0>`__:
   Liberty timing files ``cells/<cell>/<cell>__<corner>.lib`` for
   ``addf_1``, ``dffq_1`` and ``nand2_1``.

.. [PHY-OSU] Oklahoma State University, `gf180mcu_osu_sc standard cells
   <https://github.com/stineje/globalfoundries-pdk-libs-gf180mcu_osu_sc>`__:
   Liberty files ``gf180mcu_osu_sc_gp9t3v3/lib/gf180mcu_osu_sc_gp9t3v3_TT_25C.ccs.lib``
   and the 12-track equivalent.

.. [PHY-GF180IO] GlobalFoundries, `gf180mcu_fd_io I/O library
   <https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_io>`__.

Papers: line drivers, transceivers and clocks
---------------------------------------------

.. [PHY-PAN14] Pan and others, `A Full-Duplex Line Driver for Gigabit
   Ethernet With Rail-to-Rail Class-AB Output Stage in 28 nm CMOS
   <https://doi.org/10.1109/JSSC.2014.2353796>`__, IEEE Journal of
   Solid-State Circuits 49(12):3141-3155, 2014.

.. [PHY-BUHR18] S. Buhr, M. Kreißig, S. Protze, F. Ellinger, `Ultra Low
   Power Class-AB Voltage Mode Line Driver for Fast Ethernet
   <https://doi.org/10.1109/MWSCAS.2018.8623924>`__, IEEE MWSCAS 2018,
   pp. 17-20.

.. [PHY-RICHTER14] A. Richter, C. Tzschoppe, F. Ellinger, `Low power fast
   Ethernet line driver <https://doi.org/10.1109/ICECS.2014.7049919>`__,
   IEEE ICECS 2014, pp. 52-55.

.. [PHY-BUHR20B] S. Buhr, M. Kreißig, C. Matthus, S. Protze, F. Ellinger,
   `Low Power Class-AB Line Driver with Adaptive Digital Impedance Control
   for Fast Ethernet <https://doi.org/10.1109/NorCAS51424.2020.9265004>`__,
   IEEE NorCAS 2020.

.. [PHY-BABANEZHAD99] J. N. Babanezhad, `A 100-MHz, 50-Ω, -45-dB
   distortion, 3.3-V CMOS line driver for Ethernet and fast Ethernet
   networking applications <https://doi.org/10.1109/4.777101>`__, IEEE
   Journal of Solid-State Circuits 34(8):1044-1050, 1999.

.. [PHY-BUHR21] S. Buhr, `Energieeffiziente integrierte Schaltungen zur
   Basisbandsignalverarbeitung und Zeitsynchronisation für drahtgebundene
   Ethernet-Echtzeitkommunikation
   <https://tud.qucosa.de/api/qucosa%3A77692/attachment/ATT-0/>`__
   (energy-efficient integrated circuits for baseband signal processing and
   time synchronisation in wired real-time Ethernet), Dr.-Ing.
   dissertation, TU Dresden, 2021. A 180 nm 100BASE-TX transceiver.

.. [PHY-BUHR19] S. Buhr, X. Xu, M. Kreißig, F. Ellinger, `A Low Power Fast
   Ethernet Physical Layer Transceiver
   <https://doi.org/10.1109/ICECS46596.2019.8964920>`__, IEEE ICECS 2019,
   pp. 478-481.

.. [PHY-BUHR20A] S. Buhr, X. Xu, M. Kreißig, C. Matthus, F. Ellinger, `Low
   power analogue equaliser with adaptive digital tuning for fast ethernet
   <https://doi.org/10.1049/iet-cds.2019.0370>`__, IET Circuits, Devices
   and Systems 14(5):600-610, 2020.

.. [PHY-HE01] R. He, N. Nazari, S. Sutardja, `A DSP based receiver for
   1000BASE-T PHY <https://doi.org/10.1109/ISSCC.2001.912651>`__, IEEE
   ISSCC 2001, pp. 308-309.

.. [PHY-HATAMIAN98] M. Hatamian and others, `Design considerations for
   gigabit Ethernet 1000Base-T twisted pair transceivers
   <https://doi.org/10.1109/CICC.1998.694994>`__, IEEE CICC 1998,
   pp. 335-342.

Papers: echo cancelling and ADCs
--------------------------------

.. [PHY-LEE00] C. Lee, B. Razavi, `A 125-MHz mixed-signal echo canceller
   for Gigabit Ethernet on copper wire
   <https://doi.org/10.1109/CICC.2000.852708>`__, IEEE CICC 2000.

.. [PHY-LEE01] C. Lee, B. Razavi, `A 125-MHz mixed-signal echo canceller
   for Gigabit Ethernet on copper wire
   <https://doi.org/10.1109/4.910475>`__, IEEE Journal of Solid-State
   Circuits 36(3):366-373, 2001.

.. [PHY-HEO02] Heo, Jang, Park, Park, `An 8-bit 200 MS/s CMOS
   folding/interpolating ADC with a reduced number of preamplifiers using an
   averaging technique <https://doi.org/10.1109/ASIC.2002.1158035>`__,
   IEEE ASIC Conference 2002, pp. 80-83.

.. [PHY-YOON00] Yoon, Lee, Jeong, Kim, `An 8-bit 125 MS/s CMOS folding ADC
   for Gigabit Ethernet LSI <https://doi.org/10.1109/VLSIC.2000.852893>`__,
   Symposium on VLSI Circuits 2000, pp. 212-213.

.. [PHY-LIMOTYRAKIS05] S. Limotyrakis, S. D. Kulchycki, D. K. Su,
   B. A. Wooley, `A 150-MS/s 8-b 71-mW CMOS time-interleaved ADC
   <https://doi.org/10.1109/JSSC.2005.845992>`__, IEEE Journal of
   Solid-State Circuits 40(5):1057-1067, 2005.

.. [PHY-JIANG08] Jiang, Do, Yeo, Lim, `An 8-bit 200-MSample/s Pipelined ADC
   With Mixed-Mode Front-End S/H Circuit
   <https://doi.org/10.1109/TCSI.2008.916613>`__, IEEE Transactions on
   Circuits and Systems I 55(6):1430-1440, 2008.

.. [PHY-ZHANG10] Zhang, Yuan, Guo, Cheng, Zeng, `An 8-bit 100-MS/s
   pipelined ADC without dedicated sample-and-hold amplifier
   <https://doi.org/10.1088/1674-4926/31/7/075006>`__, Journal of
   Semiconductors 31(7):075006, 2010.

Papers: the decision loop
-------------------------

.. [PHY-HARATSCH01] E. F. Haratsch, K. Azadet, `A 1-Gb/s joint equalizer
   and trellis decoder for 1000BASE-T Gigabit Ethernet
   <https://doi.org/10.1109/4.910476>`__, IEEE Journal of Solid-State
   Circuits 36(3):374-384, 2001.

.. [PHY-HARATSCH01B] E. F. Haratsch, K. Azadet, `A pipelined 14-tap
   parallel decision-feedback decoder for 1000BASE-T Gigabit Ethernet
   <https://doi.org/10.1109/VTSA.2001.934497>`__, VLSI-TSA 2001,
   pp. 117-120.

.. [PHY-AZADET-PAT] K. Azadet, E. F. Haratsch, `Method and apparatus for
   pipelined joint equalization and decoding for gigabit communications,
   US patent 7,000,175 B2 <https://patents.google.com/patent/US7000175>`__.

.. [PHY-GU07] Y. Gu, K. K. Parhi, `Pipelined Parallel Decision-Feedback
   Decoders for High-Speed Ethernet Over Copper
   <https://doi.org/10.1109/TSP.2006.885776>`__, IEEE Transactions on
   Signal Processing 55(2):707-715, 2007.

.. [PHY-PARHI91] K. K. Parhi, `Pipelining in algorithms with quantizer
   loops <https://doi.org/10.1109/31.135746>`__, IEEE Transactions on
   Circuits and Systems 38(7):745-754, 1991.
