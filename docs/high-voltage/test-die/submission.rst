.. _hv-test-submission:

Die and submission
==================

The test die occupies the smallest slot of wafer.space run 3, 1936 µm by
2531 µm, in the gf180mcuD variant of the process with five metal layers.
It carries bare pads only: no protection against electrostatic discharge,
no pad ring, and no pads at the positions that chip-on-board assembly
needs.

Build steps
-----------

The layout is built by two scripts in ``silicon/hvtest``
(:numref:`fig-hvt-build`). ``chip.py`` draws the structures, pads and
buses, and writes the floor plan that the figures and tables of
:ref:`hv-test-structures` are drawn from. ``flow.py`` then checks the
connections and runs three steps inside the wafer.space precheck
container, which holds the layout tool and the process files
[HV-WS-PRECHECK]_:

.. code-block:: sh

   uv run --with klayout python silicon/hvtest/chip.py raw.gds manifest.json
   uv run python silicon/hvtest/flow.py raw.gds manifest.json WORKDIR

.. figure:: hvt-build.svg
   :name: fig-hvt-build
   :alt: Flow of six steps. 1, chip.py writes raw.gds with the
         structures, pads and buses, and manifest.json. 2, check_nets.py
         confirms that every pad reaches its own well, ring or plate. 3,
         the seal-ring script of the process files adds the ring at the
         die size of 1936 µm by 2531 µm. 4, the fill script adds dummy
         fill, with Metal4 fill allowed under Metal5. 5, the wafer.space
         precheck runs its checks for slot 0p5x0p5. 6, hvtest.oas is the
         file to submit, with top cell hvtest.

   Steps from the layout generator to the submitted file.

A design-rule check cannot see an open circuit or a wrong connection.
``check_nets.py`` therefore extracts the nets from the drawn shapes and
stops the build unless four things hold. Every well pad reaches the N+
ring of its own well. Every second pad reaches its ring or its plate. All
P+ rings and substrate pads are one net. No two pads share a net.

The seal ring comes from the script in the process files. The fill script
of the same files adds the dummy shapes that the density rules need,
outside the fill blocks of the structures (:numref:`tab-hvt-rules`). Dummy
Metal4 is allowed under Metal5 for this die. The pads are Metal5 and cover
about 15 % of the die, and with no Metal4 beneath them the Metal4 density
falls below the 30 % minimum.

Checks
------

The precheck is the set of checks that wafer.space runs on every
submission. The submitted file passes all of them
(:numref:`tab-hvt-precheck`), also when the precheck is run again on the
committed file itself. The table is drawn from the record of that run,
``silicon/hvtest/PRECHECK.txt``.

.. csv-table:: Precheck result of the submitted file
   :name: tab-hvt-precheck
   :file: hvt-tab-precheck.csv
   :header-rows: 1
   :widths: 45 55

Passing these checks means the foundry can make the die. It says nothing
about any structure holding its voltage, since no rule is written for more
than 6 V.

Submitted file
--------------

The file to submit is ``silicon/hvtest/hvtest.oas``, with the single top
cell ``hvtest``. It is the output of the precheck step, which writes the
checked layout back out. :numref:`tab-hvt-precheck` gives its checksum.

The dies arrive bare [HV-WS-SITE]_. They are measured on a probe station,
or wire-bonded by the user to a carrier of their own. The chip-on-board
option of wafer.space needs the library's pad ring at its standard
positions, which this die does not have.

Independent reviews
-------------------

Three reviews by readers who had not worked on the die were made before
submission: one of the layout, one of the physics, and a final one of the
layout and the method together. Each changed the die
(:numref:`tab-hvt-reviews`).

.. list-table:: Findings of the reviews and what changed
   :name: tab-hvt-reviews
   :header-rows: 1
   :widths: 12 44 44

   * - Review
     - Finding
     - Change
   * - Layout
     - The contact to ring 1 was open on two of the three ring-sense
       structures
     - Contacts placed explicitly; ``check_nets.py`` added to the build
   * - Layout
     - Grounded Metal1 of the P+ ring lay 0.6 µm below Metal2 leads that
       can be at the well's voltage
     - No Metal1 or contacts on the P+ ring for 8 µm under such a lead
   * - Layout
     - The P+ ring stood close enough to the last floating ring to limit
       some ring structures
     - P+ ring at least 15 µm beyond the last ring
   * - Layout
     - No structure showed the spread across the die or the effect of the
       Metal5 lead; labels were hard to read
     - Second copies NT20b, DT20b and NA0p6b; NT20L with a wide lead;
       larger labels; a seventh substrate pad
   * - Layout
     - The corner "radius" is one 45° cut, not an arc
     - Stated on :ref:`hv-test-structures`; corner predictions treated as
       upper bounds
   * - Physics
     - The polysilicon plate was not joined to the oxide under it in the
       simulation, so every polysilicon result was wrong
     - Corrected; a polysilicon plate raises the breakdown voltage
   * - Physics
     - The doping profiles fitted neither the deep N-well's capacitance
       nor its published breakdown voltage
     - Profiles refitted, with a deep P layer; deep N-well group treated
       as a reference
   * - Physics
     - Generated P-well was added on top of rings and of a drawn P-well
     - Removed
   * - Physics
     - Two other explanations of the published 14 V were untested: a P+
       region near the well, and the 6 V area
     - NT1 and NT20V added
   * - Final
     - Punch-through to a contacted ring was measured only at gaps of
       3 µm or less, far below the spacing a 57 V well needs
     - NR1S5, NR1S8 and NR1S12 added, with a contacted ring at 5 µm, 8 µm
       and 12 µm
   * - Final
     - The N-well under NAT had one size, so its edge capacitance could
       not be separated from that of its bottom
     - CVNA2 added, 200 µm across; CVN2 without a fill block, like CVN
   * - Final
     - Six deep N-well structures were predicted to give the same result
       as their neighbours
     - DT5, DT35, DC15, DW3, DW6, DM1_3 and CVD2 removed
   * - Final
     - A symmetric tolerance of 15 % did not fit predictions known to run
       high; the capacitance connection and the ring retrace test would
       not have worked as written
     - Ratio to a reference structure made the main comparison; the
       method corrected (:ref:`hv-test-method`)
   * - Final
     - No smoother corner existed as a reference
     - None possible: the rules allow only 45° edges on a well. The
       avalanche light is photographed on three structures instead

The final review also put numbers on its confidence, for the die and
method as they stood before the last four rows of the table
(:numref:`tab-hvt-confidence`). They are one reviewer's estimates, not
measurements, and the changes that followed were aimed at the lowest of
them.

.. list-table:: Confidence stated by the final review, before its own
               corrections were made
   :name: tab-hvt-confidence
   :header-rows: 1
   :widths: 60 40

   * - Statement
     - Probability
   * - The layout passes the wafer.space precheck
     - 85 %
   * - The breakdown measurements work as intended
     - 85 %
   * - The method gives patterns and ratios comparable with the simulation
     - 60 %
   * - The method gives absolute values within 15 % of the simulation
     - 35 %
   * - The set of structures is sufficient
     - 45 %

The review named four missing items behind the last figure: a smoother
corner, wider gaps to a contacted well, a 200 µm well under NAT, and
finished predictions for the multi-ring structures. The second and third
are now on the die, the first cannot be drawn, and the fourth is still
running.

The reviews left four things open. No simulation represents a vertex in
three dimensions. The effect of the Metal5 lead is bounded by NT20L for a
plain well only. The precheck container is one release of the process
files behind the one the wafer.space platform runs. No silicon has been
measured, so every prediction rests on public numbers alone.

Open questions
--------------

* Does the wafer.space platform, with its newer process files, pass the
  same file? The local precheck is one release behind.
* Does the Metal4 fill under a pad change what the pad holds at 150 V? The
  fill floats, 0.9 µm below the pad.
