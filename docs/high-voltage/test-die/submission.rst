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
:ref:`hv-test-structures` are drawn from. ``flow.py`` then runs three
steps inside the wafer.space precheck container, which holds the layout
tool and the process files [HV-WS-PRECHECK]_:

.. code-block:: sh

   uv run --with klayout python silicon/hvtest/chip.py raw.gds manifest.json
   uv run python silicon/hvtest/flow.py raw.gds WORKDIR

.. figure:: hvt-build.svg
   :name: fig-hvt-build
   :alt: Flow of five steps. 1, chip.py writes raw.gds with the
         structures, pads and buses, and manifest.json. 2, the seal-ring
         script of the process files adds the ring at the die size of
         1936 µm by 2531 µm. 3, the fill script adds dummy fill, with
         Metal4 fill allowed under Metal5. 4, the wafer.space precheck
         runs its checks for slot 0p5x0p5. 5, hvtest.oas is the file to
         submit, with top cell hvtest.

   Steps from the layout generator to the submitted file.

The seal ring comes from the script in the process files. The fill script
of the same files adds the dummy shapes that the density rules need,
outside the fill blocks of the structures (:numref:`tab-hvt-rules`). Dummy
Metal4 is allowed under Metal5 for this die. The pads are Metal5 and cover
about 15 % of the die, and with no Metal4 beneath them the Metal4 density
is 28.0 %, below the 30 % minimum.

Checks
------

The precheck is the set of checks that wafer.space runs on every
submission (:numref:`tab-hvt-precheck`). The results are those of a run of
the whole die before Metal4 fill was allowed under the pads. The density
check failed on Metal4 alone in that run.

.. list-table:: Precheck results, image version 1.7.3
   :name: tab-hvt-precheck
   :header-rows: 1
   :widths: 40 60

   * - Check
     - Result
   * - One top cell with the expected name
     - Pass
   * - Die size, origin and database unit; seal ring present
     - Pass
   * - Zero-area polygons
     - Pass
   * - Antenna rules
     - Pass
   * - Magic design rules, advisory
     - Pass
   * - KLayout design rules
     - Pass
   * - Density
     - Fail: Metal4 at 28.0 % against a minimum of 30 %. Run before Metal4
       fill was allowed under the pads; not yet repeated

Passing these checks means the foundry can make the die. It says nothing
about any structure holding its voltage, since no rule is written for more
than 6 V.

Submitted file
--------------

The file to submit is ``silicon/hvtest/hvtest.oas``, with the single top
cell ``hvtest``. It is the output of the precheck step, which writes the
checked layout back out.

The dies arrive bare [HV-WS-SITE]_. They are measured on a probe station,
or wire-bonded by the user to a carrier of their own. The chip-on-board
option of wafer.space needs the library's pad ring at its standard
positions, which this die does not have.

Open questions
--------------

* Does the die pass the density check with Metal4 fill under the pads?
  :numref:`tab-hvt-precheck` holds the last full run, from before that
  change.
* Does the Metal4 fill under a pad change what the pad holds at 150 V? The
  fill floats, 0.9 µm below the pad.
