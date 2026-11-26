.. _hv-test-die:

Test die
========

A gf180mcu test die measures how a well can be terminated to hold up to
57 V above the substrate, by breaking down wells with different edges and
comparing the results with device simulation.

:doc:`test-die/structures`
   The questions the die answers, the anatomy of a structure, each group
   of structures with its dimensions, and the floor plan with pad
   positions.
:doc:`test-die/method`
   The five measurement procedures, the order of work, and the table that
   turns the results into a conclusion about the process.
:doc:`test-die/predictions`
   How the breakdown voltage of each structure is simulated, the
   assumptions behind it, and the predicted values.

:doc:`test-die/submission`
   The slot, the build steps, the checks the layout passes and the file
   to submit.

.. toctree::
   :hidden:

   test-die/structures
   test-die/method
   test-die/predictions
   test-die/submission
