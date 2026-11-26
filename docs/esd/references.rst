References
==========

The standards' summaries, foundry documents, netlists and tools cited on
the ESD pages. Each citation in the text gives the section, figure, table or
line within the source.

ESD tests
---------

.. [ESD-ESDA-P5] EOS/ESD Association, `Fundamentals of Electrostatic
   Discharge, Part Five: Device Sensitivity and Testing
   <https://www.esda.org/esd-overview/esd-fundamentals/part-5-device-sensitivity-and-testing/>`__,
   2024.

.. [ESD-TB505] Renesas, `TB505 Understanding the Difference between HBM and
   IEC 61000-4-2 ESD Immunity
   <https://www.renesas.com/us/en/document/oth/tb505-understanding-difference-between-hbm-and-iec-61000-4-2-esd-immunity>`__,
   Rev 0.00, 2016-07-29.

.. [ESD-TND410] ON Semiconductor, `TND410/D Human Body Model (HBM) vs.
   IEC 61000-4-2 <https://www.onsemi.com/pub/Collateral/TND410-D.PDF>`__,
   Rev. 0, 2010-09.

Reference parts
---------------

.. [ESD-TRS3232E] Texas Instruments, `TRS3232E 3V to 5.5V Multichannel
   RS-232 Line Driver and Receiver With ±15kV IEC ESD Protection
   <https://www.ti.com/lit/ds/symlink/trs3232e.pdf>`__, SLLS790E, revised
   2024-12.

.. [ESD-SN65HVD1781] Texas Instruments, `SN65HVD178x Fault-Protected
   RS-485 Transceivers With 3.3-V to 5-V Operation
   <https://www.ti.com/lit/ds/symlink/sn65hvd1781.pdf>`__,
   SLLS877H, revised 2017-03.

.. [ESD-TPD1E10B06] Texas Instruments, `TPD1E10B06 Single-Channel ESD
   Protection Diode <https://www.ti.com/lit/ds/symlink/tpd1e10b06.pdf>`__,
   SLLSEB1G, revised 2024-08.

gf180mcu foundry documents
--------------------------

.. [ESD-GF180-IO] GlobalFoundries, `gf180mcu_fd_io 5 V I/O library
   <https://gf180mcu-pdk.readthedocs.io/en/latest/IPs/IO/gf180mcu_fd_io/index.html>`__:
   ESD protection and latch-up immunity pages.

.. [ESD-GF180-DRM-14-4] GlobalFoundries, `gf180mcu design manual, section
   14.4, ESD Layout Guidelines
   <https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_14_4.html>`__.

.. [ESD-GF180-DRM-14-5-5] GlobalFoundries, `gf180mcu design manual, section
   14.5.5, ESD Performance from 5V/6V NMOS transistor
   <https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_14_5_5.html>`__.

.. [ESD-GF180-DRM-14-5-6] GlobalFoundries, `gf180mcu design manual, section
   14.5.6, ESD Performance from 5V/6V PMOS transistor
   <https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_14_5_6.html>`__.

.. [ESD-GF180-DRM-14-5-7] GlobalFoundries, `gf180mcu design manual, section
   14.5.7, ESD Performance from 5V/6V HV N+/PWELL diode
   <https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_14_5_7.html>`__.

.. [ESD-GF180-DRM-14-5-8] GlobalFoundries, `gf180mcu design manual, section
   14.5.8, ESD Performance from 5V/6V HV P+/NWELL diode
   <https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_14_5_8.html>`__.

.. [ESD-GF180-EP-OX] GlobalFoundries, `gf180mcu electrical parameters,
   section 5.4, Oxide Breakdown Voltage
   <https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs_5_4.html>`__.

.. [ESD-GF180-EP-JN] GlobalFoundries, `gf180mcu electrical parameters,
   section 5.5, Junction Breakdown Voltage
   <https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs_5_5.html>`__.

Netlists and models
-------------------

.. [ESD-GF180-IO-SRC] GlobalFoundries and Google, `gf180mcu_fd_io library
   source, commit 2aeec51
   <https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_io/tree/2aeec51ea2824b6cc0b396acfc39f4535f40b23a>`__:
   the cell netlists in ``cells/*/*.cdl`` and the layouts in
   ``cells/*/*.gds``.

.. [ESD-BI-T-CDL] `gf180mcu_fd_io__bi_t.cdl
   <https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_io/blob/2aeec51ea2824b6cc0b396acfc39f4535f40b23a/cells/bi_t/gf180mcu_fd_io__bi_t.cdl>`__,
   the netlist of the bidirectional pad, in [ESD-GF180-IO-SRC]_.

.. [ESD-DVDD-CDL] `gf180mcu_fd_io__dvdd.cdl
   <https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_io/blob/2aeec51ea2824b6cc0b396acfc39f4535f40b23a/cells/dvdd/gf180mcu_fd_io__dvdd.cdl#L16-L52>`__,
   the netlist of the DVDD supply pad, lines 16 to 52, in
   [ESD-GF180-IO-SRC]_. The DVSS pad has the same clamp.

.. [ESD-ASIG-CDL] `gf180mcu_fd_io__asig_5p0.cdl
   <https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_io/blob/2aeec51ea2824b6cc0b396acfc39f4535f40b23a/cells/asig_5p0/gf180mcu_fd_io__asig_5p0.cdl#L15-L20>`__,
   the netlist of the analogue pad, lines 15 to 20, in
   [ESD-GF180-IO-SRC]_.

.. [ESD-BI-T-GDS] `gf180mcu_fd_io__bi_t_5lm.gds
   <https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_io/blob/2aeec51ea2824b6cc0b396acfc39f4535f40b23a/cells/bi_t/gf180mcu_fd_io__bi_t_5lm.gds>`__,
   the layout of the bidirectional pad for five metal layers, in
   [ESD-GF180-IO-SRC]_.

.. [ESD-DVDD-GDS] `gf180mcu_fd_io__dvdd_5lm.gds
   <https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_io/blob/2aeec51ea2824b6cc0b396acfc39f4535f40b23a/cells/dvdd/gf180mcu_fd_io__dvdd_5lm.gds>`__,
   the layout of the DVDD supply pad for five metal layers, in
   [ESD-GF180-IO-SRC]_.

.. [ESD-DVSS-GDS] `gf180mcu_fd_io__dvss_5lm.gds
   <https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_io/blob/2aeec51ea2824b6cc0b396acfc39f4535f40b23a/cells/dvss/gf180mcu_fd_io__dvss_5lm.gds>`__,
   the layout of the DVSS supply pad for five metal layers, in
   [ESD-GF180-IO-SRC]_.

.. [ESD-GF180-DRM-4-1] GlobalFoundries, `gf180mcu design manual, section
   4.1, Drawn layer definition and abbreviation
   <https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_04_1.html>`__:
   the GDS layer and datatype numbers of each mask layer.

.. [ESD-GF180-DRM-4-3] GlobalFoundries, `gf180mcu design manual, section
   4.3, Mask Layer Numbering
   <https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_04_3.html>`__:
   the table lists the P-well mask, LVPWELL, as drawn and generated.

.. [ESD-GDSTK] L. H. Gabrielli, `gdstk, a library for creation and
   manipulation of GDSII and OASIS files
   <https://heitzmann.github.io/gdstk/>`__.

.. [ESD-GF180-MODELS] GlobalFoundries and Google, `gf180mcu ngspice models,
   sm141064.ngspice, commit 9f992d5
   <https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_pr/blob/9f992d5a9186d1f7820c58f039c484ad35b2edea/models/ngspice/sm141064.ngspice#L37537-L37538>`__:
   the 6 V NMOS model, lines 37537 and 37538 for the oxide.

.. [ESD-GF180-MODELS-SAB] GlobalFoundries and Google, `gf180mcu ngspice
   models, sm141064.ngspice, commit 9f992d5, typical corner
   <https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_pr/blob/9f992d5a9186d1f7820c58f039c484ad35b2edea/models/ngspice/sm141064.ngspice#L108-L109>`__:
   the sheet resistance of the unsalicided N+ and P+ diffusions, lines
   108 and 109.

.. [ESD-GF180-MODELS-DIODE] GlobalFoundries and Google, `gf180mcu ngspice
   models, sm141064.ngspice, commit 9f992d5, 6 V diode models
   <https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_pr/blob/9f992d5a9186d1f7820c58f039c484ad35b2edea/models/ngspice/sm141064.ngspice#L38141-L38161>`__:
   ``np_6p0`` and ``pn_6p0``, lines 38141 to 38161, with their junction
   capacitance (``cj``, ``cjp``, ``cjsw``) and series resistance (``rs``).

.. [ESD-NGSPICE] `ngspice <https://ngspice.sourceforge.io/>`__, the open
   source circuit simulator.
