Integrating the transceiver on evampire
=======================================

Every Ethernet port of evampire must work at 1000 Mbit/s over four pairs
(1000BASE-T), in the first version through an external transceiver and in
the full design through a transceiver integrated on the chip. The full
design also connects to the cable without coupling transformers. Whether the
integrated transceiver also supports 100 Mbit/s (100BASE-TX) and 10 Mbit/s
(10BASE-T) is not yet fixed.

This page therefore treats the integrated 1000BASE-T transceiver as the main
design. It gives its block-level specification, works through each design
problem with the candidate approaches compared, estimates area and power on
the gf180mcu process, and then lists what 100BASE-TX and 10BASE-T would add.
It builds on the explanation in :doc:`../phy-electrical`. The circuits that
replace the coupling transformers are described in :doc:`../magnetics`;
where a result here depends on them, this page links there.

Three kinds of value appear on this page, and each is labelled:

Required
   A limit from the IEEE 802.3 standard, taken from the conformance test
   documents that quote it ([PHY-UNH14]_, [PHY-UNH25]_, [PHY-UNH40]_,
   [PHY-UNH28]_).

Published
   A measured or reported result from a paper, presentation or datasheet,
   with its source. Where only the paper's abstract was available, the
   number comes from the abstract.

Estimate
   A number calculated on this page from required or published values. Each
   estimate states its assumptions. Estimates are not requirements.

The interface to the forwarding logic
-------------------------------------

The forwarding logic exchanges one byte per clock cycle with each port, plus
a "frame in progress" flag and an "error" flag in each direction (see
:doc:`../../architecture/index`). An integrated transceiver presents exactly
this interface, so the forwarding logic is the same in the first version and
in the full design.

At 1000 Mbit/s a byte moves every 8 ns, one per cycle of a 125 MHz clock.
In the receive direction the bytes are timed by the clock recovered from the
cable, as they are with RGMII, and the existing rate-matching buffer moves
them onto evampire's own 125 MHz clock.

References
----------

Standards, conformance documents and datasheets cited on this page, such
as [PHY-8023]_, [PHY-UNH40]_ and [PHY-DP83867]_, are listed on
:doc:`../phy-electrical`.

.. [PHY-HARATSCH01] E. F. Haratsch, K. Azadet, "A 1-Gb/s joint equalizer
   and trellis decoder for 1000BASE-T Gigabit Ethernet", IEEE JSSC
   36(3):374-384, 2001. doi:10.1109/4.910476.

.. [PHY-HARATSCH01B] E. F. Haratsch, K. Azadet, "A pipelined 14-tap
   parallel decision-feedback decoder for 1000BASE-T Gigabit Ethernet",
   VLSI-TSA 2001, pp. 117-120. doi:10.1109/VTSA.2001.934497.

.. [PHY-AZADET-PAT] K. Azadet, E. F. Haratsch, "Method and apparatus for
   pipelined joint equalization and decoding for gigabit communications",
   US patent 7,000,175 B2. https://patents.google.com/patent/US7000175.
   Gate count and speed of a directly implemented 14-tap decoder.

.. [PHY-GU07] Y. Gu, K. K. Parhi, "Pipelined Parallel Decision-Feedback
   Decoders for High-Speed Ethernet Over Copper", IEEE Transactions on
   Signal Processing 55(2):707-715, 2007. doi:10.1109/TSP.2006.885776.

.. [PHY-ZHU07] Zhu Yue, Rong Mengtian, Mao Junfa, M-algorithm joint decoder
   and equalizer for 1000BASE-T, Journal of Shanghai Jiaotong University
   41(8):1358-1361, 2007.

.. [PHY-PARHI91] K. K. Parhi, "Pipelining in algorithms with quantizer
   loops", IEEE Transactions on Circuits and Systems 38(7):745-754, 1991.
   doi:10.1109/31.135746.

.. [PHY-QAM97] O. Agazzi, M. Hatamian, H. Samueli, "Update on QAM-Based
   1000BASE-T Transceiver", IEEE 802.3, May 1997.
   https://www.ieee802.org/3/z/public/presentations/may1997/mhQAMfld.pdf.
   Gives the 3.1 W 0.25 µm estimate as including the analog front end.

.. [PHY-HEO02] Heo, Jang, Park, Park, "An 8-bit 200 MS/s CMOS
   folding/interpolating ADC with a reduced number of preamplifiers using an
   averaging technique", IEEE ASIC Conference 2002, pp. 80-83.
   doi:10.1109/ASIC.2002.1158035.

.. [PHY-LIMOTYRAKIS05] S. Limotyrakis, S. D. Kulchycki, D. K. Su,
   B. A. Wooley, "A 150-MS/s 8-b 71-mW CMOS time-interleaved ADC", IEEE
   JSSC 40(5):1057-1067, 2005. doi:10.1109/JSSC.2005.845992.

.. [PHY-ZHANG10] Zhang, Yuan, Guo, Cheng, Zeng, "An 8-bit 100-MS/s pipelined
   ADC without dedicated sample-and-hold amplifier", Journal of
   Semiconductors 31(7):075006, 2010.
   doi:10.1088/1674-4926/31/7/075006.

.. [PHY-PAN14] Pan et al., "A Full-Duplex Line Driver for Gigabit Ethernet
   With Rail-to-Rail Class-AB Output Stage in 28 nm CMOS", IEEE JSSC
   49(12):3141-3155, 2014, doi:10.1109/JSSC.2014.2353796; and the ISSCC
   2014 paper of the same title, doi:10.1109/ISSCC.2014.6757376.

.. [PHY-LEE00] C. Lee, B. Razavi, "A 125-MHz mixed-signal echo canceller
   for Gigabit Ethernet on copper wire", IEEE CICC 2000.
   doi:10.1109/CICC.2000.852708. Reduction of the digital cancellers by
   50 taps.

.. [PHY-EA-BT] L. Yseboodt, D. Abramson, *Overview of 802.3bt - Power over
   Ethernet standard*, Ethernet Alliance white paper, 2019-12.
   https://ethernetalliance.org/wp-content/uploads/2019/12/WP_EA_Overview8023bt_V2p1_FINAL.pdf.
   Powered-device power of each type and class.

.. [PHY-WAFERSPACE] "wafer.space lets you design your custom silicon just
   for $7 per die", CNX Software, 2025-10-07.
   https://www.cnx-software.com/2025/10/07/wafer-space-lets-you-design-your-custom-silicon-just-for-7-per-die/.
   Run 1 slot die area of 3.88 mm × 5.07 mm (19.67 mm²).

.. [PHY-BUHR21] S. Buhr, *Energieeffiziente integrierte Schaltungen zur
   Basisbandsignalverarbeitung und Zeitsynchronisation für drahtgebundene
   Ethernet-Echtzeitkommunikation* (energy-efficient integrated circuits
   for baseband signal processing and time synchronisation in wired
   real-time Ethernet), Dr.-Ing. dissertation, TU Dresden, 2021.
   https://tud.qucosa.de/api/qucosa%3A77692/attachment/ATT-0/. 180 nm
   100BASE-TX transceiver: die size, power, line drivers, equalizer,
   comparator receiver, PLL and phase interpolator.

.. [PHY-BUHR19] S. Buhr, X. Xu, M. Kreißig, F. Ellinger, "A Low Power Fast
   Ethernet Physical Layer Transceiver", IEEE ICECS 2019, pp. 478-481.
   doi:10.1109/ICECS46596.2019.8964920.

.. [PHY-BUHR20A] S. Buhr, X. Xu, M. Kreißig, C. Matthus, F. Ellinger, "Low
   power analogue equaliser with adaptive digital tuning for fast
   ethernet", IET Circuits, Devices & Systems 14(5):600-610, 2020.
   doi:10.1049/iet-cds.2019.0370.

.. [PHY-BUHR18] S. Buhr, M. Kreißig, S. Protze, F. Ellinger, "Ultra Low
   Power Class-AB Voltage Mode Line Driver for Fast Ethernet", IEEE MWSCAS
   2018, pp. 17-20. doi:10.1109/MWSCAS.2018.8623924.

.. [PHY-BUHR20B] S. Buhr, M. Kreißig, C. Matthus, S. Protze, F. Ellinger,
   "Low Power Class-AB Line Driver with Adaptive Digital Impedance Control
   for Fast Ethernet", IEEE NorCAS 2020.
   doi:10.1109/NorCAS51424.2020.9265004.

.. [PHY-RICHTER14] A. Richter, C. Tzschoppe, F. Ellinger, "Low power fast
   Ethernet line driver", IEEE ICECS 2014, pp. 52-55.
   doi:10.1109/ICECS.2014.7049919.

.. [PHY-BABANEZHAD99] J. N. Babanezhad, "A 100-MHz, 50-Ω, -45-dB
   distortion, 3.3-V CMOS line driver for Ethernet and fast Ethernet
   networking applications", IEEE JSSC 34(8):1044-1050, 1999.
   doi:10.1109/4.777101.

.. [PHY-HE01] R. He, N. Nazari, S. Sutardja, "A DSP based receiver for
   1000BASE-T PHY", IEEE ISSCC 2001, pp. 308-309.
   doi:10.1109/ISSCC.2001.912651.

.. [PHY-HATAMIAN98] M. Hatamian et al., "Design considerations for gigabit
   Ethernet 1000Base-T twisted pair transceivers", IEEE CICC 1998,
   pp. 335-342. doi:10.1109/CICC.1998.694994.

.. [PHY-LEE01] C. Lee, B. Razavi, "A 125-MHz mixed-signal echo canceller
   for Gigabit Ethernet on copper wire", IEEE JSSC 36(3):366-373, 2001.
   doi:10.1109/4.910475.

.. [PHY-YOON00] Yoon, Lee, Jeong, Kim, "An 8-bit 125 MS/s CMOS folding ADC
   for Gigabit Ethernet LSI", Symposium on VLSI Circuits 2000,
   pp. 212-213. doi:10.1109/VLSIC.2000.852893.

.. [PHY-JIANG08] Jiang, Do, Yeo, Lim, "An 8-bit 200-MSample/s Pipelined ADC
   With Mixed-Mode Front-End S/H Circuit", IEEE TCAS-I 55(6):1430-1440,
   2008. doi:10.1109/TCSI.2008.916613.

.. [PHY-NTU04] Lin, Chen, Lai, Wu, "1000BASE-T Gigabit Ethernet baseband
   DSP IC design", IEEE ISCAS 2004. doi:10.1109/ISCAS.2004.1329025.

.. [PHY-OSCAR97] O. Agazzi, M. Hatamian, H. Samueli, "Jitter Specifications
   for 1000Base-T", IEEE 802.3ab, September 1997.
   https://grouper.ieee.org/groups/802/3/ab/public/sept97/oscar2.PDF.

.. [PHY-ED2000] "Gigabit transceiver enables higher-port-density Ethernet
   switches", Electronic Design, 2000-08-01.
   https://www.electronicdesign.com/technologies/industrial/boards/article/21782037/gigabit-transceiver-enables-higher-port-density-ethernet-switches.
   Marvell Alaska 88E1000: 0.18 µm, 10/100/1000, 1.8 W from 3.3 V.

.. [PHY-VSC8244] Microchip (Vitesse), *VSC8244 Quad 10/100/1000BASE-T PHY*
   datasheet, VMDS-10108.
   https://ww1.microchip.com/downloads/en/DeviceDoc/VMDS-10108.pdf.
   0.13 µm, 640 mW per port; section 13 describes transformer-free
   operation with capacitor coupling on backplanes.

.. [PHY-GF180PDK] GlobalFoundries and Google, *gf180mcu PDK documentation*:
   electrical parameters specification and design manual.
   https://gf180mcu-pdk.readthedocs.io/ (source:
   https://github.com/google/gf180mcu-pdk, ``docs/analog/spice/elec_specs``
   and ``docs/physical_verification/design_manual``).

.. [PHY-GF180SC] GlobalFoundries, gf180mcu standard-cell libraries
   ``gf180mcu_fd_sc_mcu7t5v0`` and ``gf180mcu_fd_sc_mcu9t5v0``: cell
   netlists and Liberty timing files.
   https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_sc_mcu7t5v0
   and https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_sc_mcu9t5v0.

.. [PHY-GF180IO] GlobalFoundries, gf180mcu I/O library
   ``gf180mcu_fd_io`` documentation.
   https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_io.
