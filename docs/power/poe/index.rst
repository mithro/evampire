Power over Ethernet
===================

These pages explain how an Ethernet cable carries power, the signals the two
ends exchange before the power is switched on, and what evampire needs at
each end of the cable.

:term:`Power over Ethernet` puts a DC voltage of up to 57 V on the pairs of
an Ethernet cable, alongside the data. The end that supplies the power
checks that a compatible device is connected, and learns how much power it
wants, before switching the voltage on. A board built around evampire can
take either end (:ref:`power-roles`), and the software on evampire's
processor makes every power decision once it is running
(:ref:`req-power-control`). The rules come from IEEE 802.3 :clause:`33` and
:clause:`145`.

The pages start with what Power over Ethernet is and build up to the choice
of what to build on the chip:

:doc:`basics`
   The two ends of the cable, which pairs carry the power, and the voltages.
:doc:`types-classes`
   The four types and nine classes, the power each class gives, and the
   power lost in the cable.
:doc:`sequence`
   The steps from plugging in to full power: detection, classification,
   power-on and the signature that keeps the power on.
:doc:`powered-device`
   What the end that receives power must do at each step.
:doc:`pd-controller`
   The circuit blocks that do it, with commercial controllers as reference
   examples.
:doc:`startup`
   The power available at each step to a board that starts from nothing,
   before its processor runs.
:doc:`power-sourcing`
   What the end that supplies power must do at each step.
:doc:`pse-sequencing`
   The circuit blocks that supply power, with detection and classification
   sequenced by evampire's software.
:doc:`monitoring`
   The measurements and limits the hardware provides to the software, and
   the response times each fault needs.
:doc:`lldp`
   How the two ends change the power allocation over LLDP after the link
   is up.
:doc:`classification`
   The two classification methods, which each type must implement, the
   power each combination gives, and how evampire uses both.
:doc:`translation`
   How the software chooses the class to offer from the power on the input
   port, from USB Power Delivery or from the other Ethernet port.
:doc:`sharing`
   How the software shares the power budget between several output ports.
:doc:`dual-role`
   A port that can take either role, how its role is chosen, and the
   safety rules.
:doc:`hv-limits`
   The voltages the gf180mcu process can hold, and the four kinds of
   electrical stress on a cable-side circuit.
:doc:`isolation`
   The isolation the standard requires and the three routes to provide it.
:doc:`hv-options`
   For each high-voltage function, the external and on-chip options and
   what decides between them.
:doc:`references`
   The data sheets, papers and other sources cited on these pages.

The voltage converters that the power passes through have their own pages
(:doc:`../converters/index`).

.. toctree::
   :maxdepth: 1
   :hidden:

   basics
   types-classes
   sequence
   powered-device
   pd-controller
   startup
   power-sourcing
   pse-sequencing
   monitoring
   lldp
   classification
   translation
   sharing
   dual-role
   hv-limits
   isolation
   hv-options
   references
