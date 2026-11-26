.. _hvt-catalogue:

Structure catalogue
===================

Each of the 73 structures on the test die has an entry that states the one
question it answers, how it works, what it is compared with, how it is
measured, what the simulation predicts and what it cannot show. The entries
are grouped by what the structures vary.

:doc:`catalogue/plain`
   The plain wells have nothing drawn between the well and the P+ ring.

:doc:`catalogue/p-well`
   A drawn P-well stands in for the P-well that the foundry may generate, at
   a distance that the layout sets.

:doc:`catalogue/nat`
   The NAT layer marks where a native transistor keeps the bare substrate as
   its channel.

:doc:`catalogue/field-plates`
   A field plate is a conductor joined to the well that extends over the
   oxide beyond the well's edge.

:doc:`catalogue/floating-rings`
   Floating rings are N-well rings round the well that connect to nothing.

:doc:`catalogue/gated-diodes`
   A gated diode has a plate over the well edge that is not joined to the
   well and has its own pad.

:doc:`catalogue/deep-n-well`
   The deep N-well structures are a reference group.

:doc:`catalogue/capacitance-wells`
   Five wells are large enough for their capacitance to be measured

Every figure, parameter, position and predicted value of an entry is
generated from the layout's own data, so the entries follow the layout.
:numref:`tab-hvt-index` lists every structure in the order of the floor plan
(:numref:`fig-hvt-floorplan`).

.. list-table:: Every structure on the die
   :name: tab-hvt-index
   :header-rows: 1
   :widths: 14 22 64

   * - Structure
     - Group
     - Purpose
   * - :ref:`NR1S2 <hvt-s-nr1s2>`
     - :doc:`Floating rings <catalogue/floating-rings>`
     - Measures the potential of a floating ring directly
   * - :ref:`NR1S3 <hvt-s-nr1s3>`
     - :doc:`Floating rings <catalogue/floating-rings>`
     - Measures the potential of a ring at a gap of 3 µm.
   * - :ref:`NR4S <hvt-s-nr4s>`
     - :doc:`Floating rings <catalogue/floating-rings>`
     - Measures the potential of ring 1 when three more rings stand outside it.
   * - :ref:`NR1S5 <hvt-s-nr1s5>`
     - :doc:`Floating rings <catalogue/floating-rings>`
     - Gives the spacing between two wells at different voltages
   * - :ref:`NR1S8 <hvt-s-nr1s8>`
     - :doc:`Floating rings <catalogue/floating-rings>`
     - The same measurement at a gap of 8 µm, wider than the depletion region of a plain well at its breakdown voltage.
   * - :ref:`NR1S12 <hvt-s-nr1s12>`
     - :doc:`Floating rings <catalogue/floating-rings>`
     - The widest gap, 12 µm
   * - :ref:`NGP4 <hvt-s-ngp4>`
     - :doc:`Gated diodes <catalogue/gated-diodes>`
     - A polysilicon plate on its own pad
   * - :ref:`NGM1 <hvt-s-ngm1>`
     - :doc:`Gated diodes <catalogue/gated-diodes>`
     - A Metal1 plate on its own pad beside a plain N-well
   * - :ref:`NAGM1 <hvt-s-nagm1>`
     - :doc:`Gated diodes <catalogue/gated-diodes>`
     - A Metal1 plate on its own pad over NAT
   * - :ref:`DGM1 <hvt-s-dgm1>`
     - :doc:`Gated diodes <catalogue/gated-diodes>`
     - A Metal1 plate on its own pad beside a deep N-well
   * - :ref:`DT20b <hvt-s-dt20b>`
     - :doc:`Deep N-wells <catalogue/deep-n-well>`
     - Gives the spread across the die for a deep N-well
   * - :ref:`NT1 <hvt-s-nt1>`
     - :doc:`Plain N-wells <catalogue/plain>`
     - Tests whether a P+ region 1 µm from an N-well, with no P-well, is enough to explain the published 14 V.
   * - :ref:`NT5 <hvt-s-nt5>`
     - :doc:`Plain N-wells <catalogue/plain>`
     - Finds whether a P+ ring 5 µm away already limits the well.
   * - :ref:`NT10 <hvt-s-nt10>`
     - :doc:`Plain N-wells <catalogue/plain>`
     - Shows whether the breakdown voltage has stopped rising by a ring distance of 10 µm.
   * - :ref:`NT20 <hvt-s-nt20>`
     - :doc:`Plain N-wells <catalogue/plain>`
     - The reference structure of the die
   * - :ref:`NT35 <hvt-s-nt35>`
     - :doc:`Plain N-wells <catalogue/plain>`
     - Shows whether a ring distance of 20 µm is far enough
   * - :ref:`NC0 <hvt-s-nc0>`
     - :doc:`Plain N-wells <catalogue/plain>`
     - Measures what a square corner costs against a corner cut at 45°.
   * - :ref:`NC15 <hvt-s-nc15>`
     - :doc:`Plain N-wells <catalogue/plain>`
     - Tells whether the length of the corner cut matters once the vertex is 135°.
   * - :ref:`NW0 <hvt-s-nw0>`
     - :doc:`Drawn P-well <catalogue/p-well>`
     - Reproduces on purpose the junction suspected of setting the published 14 V
   * - :ref:`NW1p5 <hvt-s-nw1p5>`
     - :doc:`Drawn P-well <catalogue/p-well>`
     - Tests whether 1.5 µm of clearance from a P-well is enough for an N-well.
   * - :ref:`NW3 <hvt-s-nw3>`
     - :doc:`Drawn P-well <catalogue/p-well>`
     - Locates the distance at which a P-well stops lowering the breakdown voltage.
   * - :ref:`NW6 <hvt-s-nw6>`
     - :doc:`Drawn P-well <catalogue/p-well>`
     - Confirms that a P-well 6 µm away no longer matters.
   * - :ref:`NA0p6 <hvt-s-na0p6>`
     - :doc:`NAT layer <catalogue/nat>`
     - The main test of the NAT layer
   * - :ref:`NA2 <hvt-s-na2>`
     - :doc:`NAT layer <catalogue/nat>`
     - Tests a strip of 2 µm between the well and NAT, wide enough for the foundry to fill with P-well.
   * - :ref:`NA0p6T10 <hvt-s-na0p6t10>`
     - :doc:`NAT layer <catalogue/nat>`
     - Repeats the ring-distance check under NAT with the P+ ring at 10 µm.
   * - :ref:`NA4 <hvt-s-na4>`
     - :doc:`NAT layer <catalogue/nat>`
     - The widest strip
   * - :ref:`NA0p6T35 <hvt-s-na0p6t35>`
     - :doc:`NAT layer <catalogue/nat>`
     - Repeats the ring-distance check under NAT with the P+ ring at 35 µm, the widest NAT region on the die.
   * - :ref:`NA0p6C0 <hvt-s-na0p6c0>`
     - :doc:`NAT layer <catalogue/nat>`
     - Measures the cost of a square corner when NAT, not P-well, lies beside the well.
   * - :ref:`NAM1_3 <hvt-s-nam1-3>`
     - :doc:`NAT layer <catalogue/nat>`
     - The shortest Metal1 plate over NAT
   * - :ref:`NAM1_6 <hvt-s-nam1-6>`
     - :doc:`NAT layer <catalogue/nat>`
     - The Metal1 plate of middle length over NAT.
   * - :ref:`NAM1_10 <hvt-s-nam1-10>`
     - :doc:`NAT layer <catalogue/nat>`
     - The longest Metal1 plate over NAT
   * - :ref:`NAM2_12 <hvt-s-nam2-12>`
     - :doc:`NAT layer <catalogue/nat>`
     - A Metal2 plate over NAT, 12 µm long
   * - :ref:`NP1 <hvt-s-np1>`
     - :doc:`Field plates <catalogue/field-plates>`
     - The shortest polysilicon plate
   * - :ref:`NP2 <hvt-s-np2>`
     - :doc:`Field plates <catalogue/field-plates>`
     - A polysilicon plate of 2 µm, the middle of the polysilicon series.
   * - :ref:`NP4 <hvt-s-np4>`
     - :doc:`Field plates <catalogue/field-plates>`
     - The longest polysilicon plate
   * - :ref:`NM1_3 <hvt-s-nm1-3>`
     - :doc:`Field plates <catalogue/field-plates>`
     - The shortest Metal1 plate
   * - :ref:`NM1_6 <hvt-s-nm1-6>`
     - :doc:`Field plates <catalogue/field-plates>`
     - The Metal1 plate of middle length, 6 µm
   * - :ref:`NM1_10 <hvt-s-nm1-10>`
     - :doc:`Field plates <catalogue/field-plates>`
     - The longest Metal1 plate, 10 µm
   * - :ref:`NM2_6 <hvt-s-nm2-6>`
     - :doc:`Field plates <catalogue/field-plates>`
     - A Metal2 plate of 6 µm
   * - :ref:`NM2_12 <hvt-s-nm2-12>`
     - :doc:`Field plates <catalogue/field-plates>`
     - A Metal2 plate of 12 µm
   * - :ref:`NPM12 <hvt-s-npm12>`
     - :doc:`Field plates <catalogue/field-plates>`
     - A stepped plate of three layers
   * - :ref:`NR1_1p4 <hvt-s-nr1-1p4>`
     - :doc:`Floating rings <catalogue/floating-rings>`
     - One ring at the smallest gap the rules allow, 1.4 µm.
   * - :ref:`NR1_2 <hvt-s-nr1-2>`
     - :doc:`Floating rings <catalogue/floating-rings>`
     - One ring at a gap of 2 µm
   * - :ref:`NR1_3 <hvt-s-nr1-3>`
     - :doc:`Floating rings <catalogue/floating-rings>`
     - One ring at a gap of 3 µm.
   * - :ref:`NR3_1p5 <hvt-s-nr3-1p5>`
     - :doc:`Floating rings <catalogue/floating-rings>`
     - Three rings with gaps of 1.5 µm, 2 µm and 2.5 µm.
   * - :ref:`NR3_2 <hvt-s-nr3-2>`
     - :doc:`Floating rings <catalogue/floating-rings>`
     - Three rings with gaps of 2 µm, 2.5 µm and 3 µm
   * - :ref:`NR3W1 <hvt-s-nr3w1>`
     - :doc:`Floating rings <catalogue/floating-rings>`
     - Three rings only 1 µm wide
   * - :ref:`NR3W3 <hvt-s-nr3w3>`
     - :doc:`Floating rings <catalogue/floating-rings>`
     - Three rings 3 µm wide
   * - :ref:`NR5_1p4 <hvt-s-nr5-1p4>`
     - :doc:`Floating rings <catalogue/floating-rings>`
     - Five rings from the smallest gap
   * - :ref:`NR5_2 <hvt-s-nr5-2>`
     - :doc:`Floating rings <catalogue/floating-rings>`
     - Five rings from a gap of 2 µm
   * - :ref:`NR3M1 <hvt-s-nr3m1>`
     - :doc:`Floating rings <catalogue/floating-rings>`
     - Three rings with a Metal1 plate over the first gap
   * - :ref:`DT2p6 <hvt-s-dt2p6>`
     - :doc:`Deep N-wells <catalogue/deep-n-well>`
     - A deep N-well with its P+ ring as close as the rules allow, 2.6 µm.
   * - :ref:`DT10 <hvt-s-dt10>`
     - :doc:`Deep N-wells <catalogue/deep-n-well>`
     - A deep N-well with the P+ ring at 10 µm.
   * - :ref:`DT20 <hvt-s-dt20>`
     - :doc:`Deep N-wells <catalogue/deep-n-well>`
     - The reference deep N-well
   * - :ref:`DC0 <hvt-s-dc0>`
     - :doc:`Deep N-wells <catalogue/deep-n-well>`
     - A deep N-well with square corners.
   * - :ref:`DW1p5 <hvt-s-dw1p5>`
     - :doc:`Deep N-wells <catalogue/deep-n-well>`
     - A deep N-well with a drawn P-well as close as the rules allow, 1.5 µm.
   * - :ref:`DM1_6 <hvt-s-dm1-6>`
     - :doc:`Field plates <catalogue/field-plates>`
     - A deep N-well with a Metal1 plate of 6 µm
   * - :ref:`DM1_10 <hvt-s-dm1-10>`
     - :doc:`Field plates <catalogue/field-plates>`
     - A deep N-well with a Metal1 plate of 10 µm.
   * - :ref:`DPM12 <hvt-s-dpm12>`
     - :doc:`Field plates <catalogue/field-plates>`
     - A deep N-well with the stepped plate of three layers.
   * - :ref:`DAo1 <hvt-s-dao1>`
     - :doc:`Deep N-wells <catalogue/deep-n-well>`
     - A deep N-well with NAT over its edge, so that no P-well can lie beside the junction.
   * - :ref:`DAo1T35 <hvt-s-dao1t35>`
     - :doc:`Deep N-wells <catalogue/deep-n-well>`
     - A deep N-well with NAT over its edge and the P+ ring at 35 µm.
   * - :ref:`DAo1C0 <hvt-s-dao1c0>`
     - :doc:`Deep N-wells <catalogue/deep-n-well>`
     - A deep N-well with NAT over its edge and square corners.
   * - :ref:`DAo1M1_6 <hvt-s-dao1m1-6>`
     - :doc:`Deep N-wells <catalogue/deep-n-well>`
     - A deep N-well with NAT over its edge and a Metal1 plate of 6 µm
   * - :ref:`OPEN <hvt-s-open>`
     - :doc:`Capacitance wells and open reference <catalogue/capacitance-wells>`
     - The part of every reading that is not the junction
   * - :ref:`NT20b <hvt-s-nt20b>`
     - :doc:`Plain N-wells <catalogue/plain>`
     - Gives the spread across one die
   * - :ref:`NA0p6b <hvt-s-na0p6b>`
     - :doc:`NAT layer <catalogue/nat>`
     - Gives the spread across the die for a well under NAT
   * - :ref:`NT20L <hvt-s-nt20l>`
     - :doc:`Plain N-wells <catalogue/plain>`
     - Shows whether the Metal5 lead changes the junction it crosses.
   * - :ref:`NT20V <hvt-s-nt20v>`
     - :doc:`Plain N-wells <catalogue/plain>`
     - Shows whether an N-well in the 6 V area breaks down differently from one in the 3.3 V area.
   * - :ref:`CVN <hvt-s-cvn>`
     - :doc:`Capacitance wells and open reference <catalogue/capacitance-wells>`
     - The large N-well
   * - :ref:`CVD <hvt-s-cvd>`
     - :doc:`Capacitance wells and open reference <catalogue/capacitance-wells>`
     - The large deep N-well
   * - :ref:`CVN2 <hvt-s-cvn2>`
     - :doc:`Capacitance wells and open reference <catalogue/capacitance-wells>`
     - The small N-well
   * - :ref:`CVNA <hvt-s-cvna>`
     - :doc:`Capacitance wells and open reference <catalogue/capacitance-wells>`
     - An N-well whose capacitance can be followed beyond the plain well's breakdown.
   * - :ref:`CVNA2 <hvt-s-cvna2>`
     - :doc:`Capacitance wells and open reference <catalogue/capacitance-wells>`
     - The large N-well with NAT

.. toctree::
   :hidden:

   catalogue/plain
   catalogue/p-well
   catalogue/nat
   catalogue/field-plates
   catalogue/floating-rings
   catalogue/gated-diodes
   catalogue/deep-n-well
   catalogue/capacitance-wells
