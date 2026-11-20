evampire
========

evampire is an integrated circuit for the `GlobalFoundries 180 nm MCU
(gf180mcu) <https://gf180mcu-pdk.readthedocs.io/>`_ process, manufactured
through `wafer.space <https://wafer.space/>`_.

It sits between two gigabit Ethernet connections and passes all traffic
straight through from one to the other. A small RISC-V processor inside the
chip can also receive selected frames from either side and send frames of its
own, and manages power: a board built around evampire can be powered over
Ethernet and supply power over USB Type-C, or the other way around.

This documentation describes what the chip does and explains, from first
principles, every piece of Ethernet and power-delivery knowledge needed to
build it. It is written for readers who are familiar with digital and analog
integrated circuit design but not with the Ethernet or USB Power Delivery
standards.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   overview
   architecture/index
   ethernet/index
   power/index
