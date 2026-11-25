References
==========

The sources cited on the high-voltage pages, grouped by kind. Each citation
in the text gives the section, equation, table or slide used.

gf180mcu process data
---------------------

.. [HV-GF180-EP-1] GlobalFoundries, `gf180mcu electrical parameters,
   section 1.0, Low Voltage Devices (3.3V)
   <https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs_1.html>`__.

.. [HV-GF180-EP-2] GlobalFoundries, `gf180mcu electrical parameters,
   section 2.0, Medium Voltage Devices (6V)
   <https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs_2.html>`__.

.. [HV-GF180-EP-5] GlobalFoundries, `gf180mcu electrical parameters,
   section 5.5, Junction Breakdown Voltage
   <https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs_5_5.html>`__.

.. [HV-GF180-MODELS] GlobalFoundries and Google, `gf180mcu_fd_pr SPICE
   models, sm141064.ngspice, models nwp_3p3, nwp_6p0 and dnwps
   <https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_pr/blob/9f992d5a9186d1f7820c58f039c484ad35b2edea/models/ngspice/sm141064.ngspice#L38162-L38220>`__,
   commit 9f992d5, lines 38162–38220.

.. [HV-OPENPDKS-EXTRACT] R. T. Edwards and contributors, `open_pdks,
   gf180mcu/magic/gf180mcu-extract.tech
   <https://github.com/RTimothyEdwards/open_pdks/blob/bb8c82ecc7a9750faabeea98d5ca13e76e4ae744/gf180mcu/magic/gf180mcu-extract.tech#L464-L616>`__,
   commit bb8c82e, nominal capacitances, lines 464–616 (polysilicon at
   line 489, Metal2 over Metal1 at line 529); the file gives
   GlobalFoundries document PDS_035_03 as their source.

.. [HV-SIM-STACK] evampire, `Ten 5 V transistors in series as diodes, swept
   to 100 V
   <https://github.com/mithro/evampire/blob/00e975d3034ed3f7643006b8ee08d09eb0bf707c/sim/diode_stack/README.md>`__,
   commit 00e975d, ngspice simulation with the gf180mcu models.

Semiconductor physics
---------------------

.. [HV-PARK] J. M. Park, `Novel Power Devices for Smart Power Applications
   <https://www.iue.tuwien.ac.at/phd/park/>`__, PhD dissertation, TU Wien,
   2004-10.

.. [HV-SPIRITO] P. Spirito, `The Power Diode
   <https://www.docenti.unina.it/webdocenti-be/allegati/materiale-didattico/103605>`__,
   lecture notes for the course Power Semiconductor Devices, University of
   Naples Federico II.

.. [HV-MIT-6012] Massachusetts Institute of Technology, `6.012
   Microelectronic Devices and Circuits, Lecture 6: PN junction and MOS
   electrostatics (III)
   <https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/resources/lec6/>`__,
   OpenCourseWare, 2005.

.. [HV-MIT-6012-L7] Massachusetts Institute of Technology, `6.012
   Microelectronic Devices and Circuits, Lecture 7: PN junction and MOS
   electrostatics (IV)
   <https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/resources/lec7/>`__,
   OpenCourseWare, 2005.

.. [HV-MIT-6012-L8] Massachusetts Institute of Technology, `6.012
   Microelectronic Devices and Circuits, Lecture 8: PN junction and MOS
   electrostatics (V)
   <https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/resources/lec8/>`__,
   OpenCourseWare, 2005.

.. [HV-MIT-6012-L10] Massachusetts Institute of Technology, `6.012
   Microelectronic Devices and Circuits, Lecture 10: MOSFET (II)
   <https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2005/resources/lec10/>`__,
   OpenCourseWare, 2005.

.. [HV-IOFFE] Ioffe Institute, `Electrical properties of silicon
   <http://www.ioffe.ru/SVA/NSM/Semicond/Si/electric.html>`__, NSM
   semiconductor database, Basic Parameters.

.. [HV-NBS] W. R. Thurber, R. L. Mattis, Y. M. Liu and J. J. Filliben,
   `The relationship between resistivity and dopant density for phosphorus-
   and boron-doped silicon
   <https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nbsspecialpublication400-64.pdf>`__,
   NBS Special Publication 400-64, 1981-05,
   doi:10.6028/NBS.SP.400-64.

.. [HV-SZE-GIBBONS] S. M. Sze and G. Gibbons, `Effect of junction curvature
   on breakdown voltage in semiconductors
   <https://doi.org/10.1016/0038-1101(66)90033-5>`__, Solid-State
   Electronics 9 (1966), pp. 831–845.

.. [HV-BALIGA-GHANDHI] B. J. Baliga and S. K. Ghandhi, `Analytical
   solutions for the breakdown voltage of abrupt cylindrical and spherical
   junctions <https://doi.org/10.1016/0038-1101(76)90152-0>`__, Solid-State
   Electronics 19 (1976), pp. 739–744.

.. [HV-KAO-WOLLEY] Y. C. Kao and E. D. Wolley, `High-voltage planar p-n
   junctions <https://doi.org/10.1109/PROC.1967.5842>`__, Proceedings of
   the IEEE 55 (1967), pp. 1409–1414.

.. [HV-APPELS-VAES] J. A. Appels and H. M. J. Vaes, `High voltage thin layer
   devices (RESURF devices) <https://doi.org/10.1109/IEDM.1979.189589>`__,
   International Electron Devices Meeting, 1979, pp. 238–241.

Patents
-------

.. [HV-US6344676] C.-M. Yun, `Power semiconductor device with improved
   junction termination <https://patents.google.com/patent/US6344676B1/en>`__,
   US 6,344,676 B1.

.. [HV-US5912501] `US 5,912,501
   <https://patents.google.com/patent/US5912501A/en>`__, background
   section, description of FIG. 15.

.. [HV-US4573066] `US 4,573,066
   <https://patents.google.com/patent/US4573066A/en>`__, background
   section.

.. [HV-US5223919] `US 5,223,919
   <https://patents.google.com/patent/US5223919A/en>`__.

.. [HV-EP2779225] M. Yamaji, `EP 2 779 225 A1
   <https://patents.google.com/patent/EP2779225A1/en>`__, background
   section, on resistive field plates.

.. [HV-US10217861] M. Yamaji, `US 10,217,861 B2
   <https://patents.google.com/patent/US10217861B2/en>`__.

.. [HV-US4954189] `US 4,954,189
   <https://patents.google.com/patent/US4954189A/en>`__, gate-oxide test
   results.

Products and application notes
------------------------------

.. [HV-IR-AN978] International Rectifier, `HV floating MOS-gate driver ICs
   <https://www.infineon.com/assets/row/public/documents/24/42/infineon-hv-floating-mos-gate-drivers-applicationnotes-en.pdf>`__,
   application note AN-978, revision D.

.. [HV-INFINEON-SOI] S. Raghunath, `Advantages of Infineon's HVICs based on
   its SOI technology
   <https://www.infineon.com/assets/row/public/documents/24/42/infineon-advantages-of-high-voltage-gd-ics-applicationnotes-en.pdf>`__,
   Infineon application note AN2019-12, version 2.0, 2019-09-25.

.. [HV-ISO7741] Texas Instruments, `ISO774x quad-channel digital isolators
   <https://www.ti.com/product/ISO7741>`__, product page and datasheet
   SLLSEP4.
