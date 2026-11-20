.. _poe-dual-role:

Ports that take either role
===========================

This page describes an Ethernet port that can be either a powered device
or power sourcing equipment, how its role can be chosen, and the safety
rules that any choice must keep.

Power over Ethernet has no role swap
------------------------------------

In the full design either Ethernet port can take either role
(:ref:`board configurations <tab-power-board-configs>`). Power over
Ethernet has no exchange in which the two ends of a cable agree to swap
roles, unlike USB Type-C (:ref:`power-roles`). A port therefore keeps one
role for as long as the cable stays connected. :numref:`fig-poe-dual-role`
shows such a port.

.. _fig-poe-dual-role:

.. graphviz:: dual-role.dot
   :caption: An Ethernet port that can take either role, with one disconnect
             switch on each power path.
   :alt: Block diagram. The RJ45 socket and cable-side power path connect
         through one disconnect switch to the powered-device blocks, the
         input converter and the internal power bus, and through another
         disconnect switch to the power sourcing equipment channels, which
         the high-voltage converter feeds from the bus. evampire selects one
         of the two switches, sequences the power sourcing equipment
         channels and reads status from the powered-device blocks.
   :align: center

The port has both sets of blocks on the same cable-side power path: the
bridges, signature, class circuit and isolation switch of a powered device
(:doc:`pd-controller`), and the channels of power sourcing equipment, two
for 4-pair power (:doc:`pse-sequencing`). The full design has no coupling
transformers, so this power path is the one its transformer-free front end
provides (:doc:`../../ethernet/magnetics/index`).

The two sets must not both be connected
---------------------------------------

The powered-device signature would appear in parallel with the remote
powered device, so the port's own power sourcing equipment would measure
the wrong resistance during detection.

The power sourcing equipment circuit can also load the port while it is
off. For reference, with a TPS23881-style power sourcing equipment, 80 kΩ to
190 kΩ connects each channel's drain pin to its supply whenever the channel
is neither detecting nor powered [POE-TPS23881]_ (Electrical
Characteristics). That resistance would appear in parallel with the port's
own signature:

.. math::

   R_\text{seen} &= \frac{R_\text{sig} \times R_\text{drain}}
     {R_\text{sig} + R_\text{drain}} \\
   &= \frac{24.9\ \text{k}\Omega \times 80\ \text{k}\Omega}
       {104.9\ \text{k}\Omega} \\
   &= 19.0\ \text{k}\Omega

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`R_\text{sig}`
     - Signature resistor of the powered-device path
     - kΩ
   * - :math:`R_\text{drain}`
     - Idle load of the power sourcing path, the TPS23881 lowest value
     - kΩ
   * - :math:`R_\text{seen}`
     - Resistance the upstream power sourcing equipment measures
     - kΩ

With 190 kΩ the result is 22.0 kΩ. Both are below the 23.7 kΩ minimum of
:clause:`Table 145-21 <145>`, so the port would fail detection as a powered
device. The calculation assumes the idle load is across the same two
conductors as the signature. evampire's own power sourcing circuit could be
designed without such an idle load, which would remove this reason for a
switch; the first reason remains.

Each path therefore has a disconnect switch rated for the cable voltage and
surges, turned on only for the selected role.

The role can be fixed or chosen automatically
---------------------------------------------

Two ways of choosing the role are possible:

Fixed by the board
   The software sets the role from the board's configuration before a cable
   is connected, and sets the switches before enabling either path.

Chosen automatically
   The port first presents a powered-device signature. If no power arrives
   within a set time, it switches to the power sourcing role and runs
   detection. If two such ports are connected together, both may time out
   at once and then both detect power sourcing equipment and power
   nothing. A random waiting time before each switch, as USB Type-C
   dual-role ports use when toggling, would separate them.

Which method is used is an open question. Either must keep the safety
rules below.

Safety rules that any role choice keeps
---------------------------------------

Never apply power without a valid detection
   This rule applies to every pair set separately (:clause:`145.2.6`). In
   the powered-device role, the port's own power sourcing equipment
   channels are off and disconnected.

Two power sourcing equipment ports connected together
   Each sees the other's detection source instead of a 25 kΩ signature,
   so neither detects a valid powered device and neither applies power.
   Each detection circuit must survive being driven by the other: power
   sourcing equipment must withstand 5 mA fed back into it over its
   detection voltage range (:clause:`145.2.6.1`). It also presents an
   invalid signature when probed by another power sourcing equipment.

Two powered-device ports connected together
   Neither supplies a voltage, so nothing happens.

A port connected to equipment without Power over Ethernet
   As power sourcing equipment, detection fails and no power is applied
   (:doc:`power-sourcing`). As a powered device, no voltage arrives and the
   board runs from another source.

Open questions
--------------

* Whether the role is fixed by the board or chosen automatically, and the
  waiting times of the automatic method.
* The type of disconnect switch on each path, and whether evampire's power
  sourcing circuit has an idle load.
