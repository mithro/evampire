High voltage and isolation
==========================

A cable-side circuit must hold up to 57 V plus surges, and each function
that handles the cable voltage can be built on the chip or from external
parts.

:doc:`hv-limits`
   The voltages the gf180mcu process can hold, and the four kinds of
   electrical stress on a cable-side circuit.
:doc:`isolation`
   The isolation the standard requires and the three routes to provide it.
:doc:`hv-options`
   For each high-voltage function, the external and on-chip options and what
   decides between them.

.. toctree::
   :hidden:

   hv-limits
   isolation
   hv-options
