USB full-speed device
=====================

These pages explain what a USB full-speed serial device is and how it talks to a computer.

:doc:`what-it-is`
   What a computer sees, the communications device class and why no custom
   driver is needed.
:doc:`signalling`
   Host and device, the D+ and D− wires, speeds, line states, coding, and
   the parts of a packet.
:doc:`transactions`
   How packets combine into transfers, frames, how a device is recognised,
   and the descriptors a serial port needs.
:doc:`timing`
   The bit time, the reply deadline, the end of a packet and clock accuracy.

.. toctree::
   :hidden:

   what-it-is
   signalling
   transactions
   timing
