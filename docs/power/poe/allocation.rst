Power allocation
================

evampire's software decides how much power each port receives or offers.

:doc:`lldp`
   How the two ends change the power allocation over LLDP after the link is up.
:doc:`classification`
   The two classification methods, which each type must implement, the
   power each combination gives, and how evampire uses both.
:doc:`translation`
   How the software chooses the class to offer from the power on the input
   port, from USB Power Delivery or from the other Ethernet port.
:doc:`sharing`
   How the software shares the power budget between several output ports.
:doc:`dual-role`
   A port that can take either role, how its role is chosen, and the safety
   rules.

.. toctree::
   :hidden:

   lldp
   classification
   translation
   sharing
   dual-role
