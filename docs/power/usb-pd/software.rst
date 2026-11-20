.. _usbpd-software:

What USB Power Delivery needs from the processor
================================================

The processor time, sampling rate, edge accuracy and reply deadlines that
sending and receiving :term:`USB Power Delivery` messages in software needs,
and the hardware helper that removes each need.

USB Power Delivery runs mostly in software on the RISC-V processor, with
digital helpers only where software cannot meet the timing
(:ref:`req-power-bridging`). The processor core and its clock are open
(:ref:`req-processor`), so each need is given as a function of its
parameters. A core meets an instruction rate when its clock frequency
divided by its average
:wikipedia:`cycles per instruction <Cycles_per_instruction>` on that code is
at least that rate. The USB serial port uses the same method for USB data
(:doc:`/usb-serial/software-cost`).

The instruction counts are estimates for hand-written
:wikipedia:`assembly <Assembly_language>` in RV32I, the 32-bit base RISC-V
instruction set (:std:`RISC-V ISA <riscv-unpriv>`), to be confirmed by
implementation.

Software does all the digital work in the simplest design
---------------------------------------------------------

The minimum hardware per port is the analogue front end
(:ref:`usbpd-analogue`), connected to plain bits that the processor reads and
writes:

* outputs: Rp level and enable, Rd enable, VCONN enable for each CC pin,
  driver enable, driver data and comparator threshold selection;
* inputs: the :term:`comparator` outputs.

Software does the rest: :term:`BMC` encoding and decoding
(:ref:`usbpd-bmc`), :wikipedia:`4B5B` coding, the CRC-32 and the start of
packet (:ref:`usbpd-packets`), the :term:`GoodCRC` reply, retries and all
timers, the attach state machines, and the protocol and policy. The time
limits of this work span five orders of magnitude
(:numref:`tab-usbpd-timescales`).

.. list-table:: The time limits that software has to meet
   :name: tab-usbpd-timescales
   :header-rows: 1
   :widths: 36 30 18 16

   * - Task
     - Spec name
     - Time (µs)
     - PD table
   * - Place a sent edge
     - X1Tx
     - 0.05
     - :pd:`5.6 <Table 5.6>`
   * - Time a received edge
     - X1Rx
     - 0.33
     - :pd:`5.8 <Table 5.8>`
   * - GoodCRC, earliest
     - tInterFrameGap
     - 25
     - :pd:`5.10 <Table 5.10>`
   * - GoodCRC, latest
     - tTransmit
     - 195
     - :pd:`7.10 <Table 7.10>`
   * - Fast role swap signal
     - tFRSwapRx
     - 30 to 50
     - :pd:`10.1 <Table 10.1>`

The first two times are derived from the masks in :ref:`usbpd-receive` and
:ref:`usbpd-transmit`. Fast role swap is described in
:ref:`usbpd-fast-role-swap`. Replies to protocol messages have 15 ms or
more, such as tReceiverResponse (:pd:`Table 7.10`).

.. _usbpd-receive:

Receiving needs each edge timed to within 333 ns
------------------------------------------------

The receiver measures the time between successive edges on the
configuration channel. An interval of about 1 :term:`UI` is a ``0``, and two
intervals of about 0.5 UI are a ``1`` (:ref:`usbpd-bmc`). The decoder
compares each interval with 0.75 UI.

Each received edge may be up to 0.07 UI from its ideal time
(:pd:`Table 5.8`, X1Rx), so an interval may be wrong by twice that. What is
left of the 0.25 UI margin is the largest error the timing may add, and so
the longest sampling period:

.. math::

   T_\text{s,max} = (0.25 - 2 \times x_\text{rx}) \times T_\text{UI,min}

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`T_\text{s,max}`
     - Longest sampling period, or largest timestamp error
     - s
   * - :math:`x_\text{rx}`
     - Edge displacement a receiver must accept, 0.07 (:pd:`Table 5.8`)
     - UI
   * - :math:`T_\text{UI,min}`
     - Shortest unit interval, 3.03 µs at 330 kbit/s (:pd:`Table 5.9`)
     - s

The relation neglects filter delay and noise. For the values above:

.. math::

   T_\text{s,max} = (0.25 - 2 \times 0.07) \times 3.03\ \mu\text{s}
                  = 333\ \text{ns}

A sampled receiver therefore takes at least 3.0 million samples per second.
For reference, the Chromium OS EC firmware times edges with a 2.4 MHz counter,
417 ns per count ([USBPD-CROS-EC]_, ``pd_hw_init_rx()``). That is coarser than
this bound, which assumes both edges of an interval displaced by the full
0.07 UI.

Polling costs a fixed rate plus the work per edge
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With only a plain input bit, the processor reads the comparator in a
:wikipedia:`polling <Polling_(computer_science)>` loop, and the time of one
loop iteration is the sampling period. At each change it reads a counter,
classifies the interval and updates the decoder
(:numref:`tab-usbpd-poll-instr`).

.. list-table:: Estimated instructions for receiving in software
   :name: tab-usbpd-poll-instr
   :header-rows: 1
   :widths: 56 22 22

   * - Work
     - Instructions
     - Done once per
   * - Load the input word, compare and branch back
     - 2
     - sample
   * - Read the counter, subtract, compare with 0.75 UI, update state
     - 10
     - edge
   * - Shift the bit into the symbol, count bits
     - 4
     - bit
   * - Look up the 4B5B code, update the CRC-32
     - 16
     - symbol of 5 bits

The instruction rate needed while a message arrives is:

.. math::

   R_\text{poll} = \frac{k_\text{poll}}{T_\text{s}}
     + f_\text{edge} \times N_\text{edge}
     + f_\text{bit} \times N_\text{bit}

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`R_\text{poll}`
     - Instruction rate needed to receive by polling
     - instructions/s
   * - :math:`k_\text{poll}`
     - Instructions in one poll iteration, 2 (estimate)
     - instructions
   * - :math:`T_\text{s}`
     - Sampling period, at most :math:`T_\text{s,max}`
     - s
   * - :math:`f_\text{edge}`
     - Edge rate, at most twice the bit rate (all ``1`` bits)
     - edges/s
   * - :math:`N_\text{edge}`
     - Instructions per edge, 10 (estimate)
     - instructions
   * - :math:`f_\text{bit}`
     - Bit rate, at most 330 kbit/s (:pd:`Table 5.9`)
     - bit/s
   * - :math:`N_\text{bit}`
     - Instructions per bit, 4 plus 16 per 5-bit symbol, 7.2 (estimate)
     - instructions

The relation counts poll iterations during the edge work too, so it slightly
overestimates. For :math:`T_\text{s}` = 333 ns, :math:`f_\text{bit}` =
330 kbit/s and :math:`f_\text{edge}` = 660 000 edges/s:

.. math::

   R_\text{poll}
     &= \frac{2}{333\ \text{ns}} \\
     &\quad + 660\,000\ \text{s}^{-1} \times 10 \\
     &\quad + 330\,000\ \text{s}^{-1} \times 7.2 \\
     &= 15.0 \times 10^{6}\ \text{instructions/s}

That is 45.4 instructions per bit (estimate). Any pause in the loop adds to
the timing error, so :math:`T_\text{s}` plus the longest pause must stay
below 333 ns. Interrupts stay off from the first edge of a message to the end
of the GoodCRC reply (:ref:`usbpd-goodcrc-deadline`). For reference, PicoRV32
takes 5 clock cycles for a load and 5 for a taken branch
([USBPD-PICORV32]_, "Cycles per Instruction Performance"). Its poll iteration
of 10 cycles takes at most 333 ns with a clock of 30 MHz or more.

An interrupt on each edge trades polling for overhead
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An :wikipedia:`interrupt <Interrupt>` on each comparator edge removes the
polling between edges. Each edge then costs the interrupt entry and exit plus
the edge work:

.. math::

   R_\text{irq} = f_\text{edge} \times (N_\text{irq} + N_\text{edge})
     + f_\text{bit} \times N_\text{bit}

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`R_\text{irq}`
     - Instruction rate needed to receive with an interrupt per edge
     - instructions/s
   * - :math:`N_\text{irq}`
     - Instructions to enter and leave the interrupt handler, saving and
       restoring registers
     - instructions

For :math:`N_\text{irq}` = 30 (estimate), at the rates above:

.. math::

   R_\text{irq}
     &= 660\,000\ \text{s}^{-1} \times (30 + 10) \\
     &\quad + 330\,000\ \text{s}^{-1} \times 7.2 \\
     &= 28.8 \times 10^{6}\ \text{instructions/s}

That is 87.2 instructions per bit. Interrupts cost less than polling when the
overhead is below the polling cost per edge:

.. math::

   N_\text{irq} &< \frac{k_\text{poll}}{T_\text{s} \times f_\text{edge}} \\
     &= \frac{2}{333\ \text{ns} \times 660\,000\ \text{s}^{-1}} \\
     &= 9.1

On a core where the load and the branch of the poll loop take longer than
the average instruction, both sides are counted in clock cycles instead. For
reference, PicoRV32's 10-cycle poll iteration gives a break-even of 45 cycles
per edge.

The limit is accuracy rather than cost. The handler reads the counter after
the :wikipedia:`interrupt latency <Interrupt_latency>`, so the timestamp is
only as accurate as the variation in that latency. The variation has to stay
below 333 ns, so no other interrupt may run during a message. For reference,
V-USB receives low-speed USB in software with one edge-triggered interrupt
and no timer or input capture unit ([USBSER-VUSB]_, home page).

.. _usbpd-transmit:

Transmitting needs each edge within 50 ns of its time
-----------------------------------------------------

The transmit mask leaves 0.015 UI between the ideal edge time and the start
of the inner mask (:pd:`Table 5.6`, X1Tx). Read strictly, each edge has to
cross the mid-level within ± 0.015 UI, which is ± 50 ns at the nominal
300 kbit/s. This figure is a target derived from the mask, to be confirmed
by measuring a transmitter against it (:ref:`usbpd-transmitter`). Computing
each edge time from a counter, rather than counting loop iterations, keeps
the average bit rate within the 0.25 % pBitRate limit (:pd:`Table 5.10`).

A counter wait loop needs a short iteration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The processor computes the next edge time, waits in a
:wikipedia:`busy-wait <Busy_waiting>` loop until a counter reaches it, and
writes the output. The edge comes late by up to one loop iteration, so the
iteration must fit in the 100 ns window:

.. math::

   R_\text{wait} = \frac{k_\text{wait}}{2 \times x_\text{tx} \times T_\text{UI}}

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`R_\text{wait}`
     - Instruction rate the core must run the wait loop at
     - instructions/s
   * - :math:`k_\text{wait}`
     - Instructions in one wait iteration: read counter, compare, branch
     - instructions
   * - :math:`x_\text{tx}`
     - Edge placement target, 0.015 (:pd:`Table 5.6`)
     - UI
   * - :math:`T_\text{UI}`
     - Unit interval of the transmitter, 3.33 µs at 300 kbit/s
     - s

The relation leaves no allowance for other edge errors, such as variation in
the driver's delay. For :math:`k_\text{wait}` = 3 (estimate):

.. math::

   R_\text{wait} &= \frac{3}{2 \times 0.015 \times 3.33\ \mu\text{s}} \\
     &= 30 \times 10^{6}\ \text{instructions/s}

That is 100 instructions per bit at 300 kbit/s. The core is busy and
interrupts are off for the whole message, 1430 µs for the longest one
(:ref:`usbpd-durations`).

Cycle-exact code removes the loop jitter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On an in-order core whose instructions each take a fixed, known number of
clock cycles, straight-line code can place every edge an exact number of
cycles after the previous one. The edge error is then the clock's own
:wikipedia:`jitter <Jitter>`. This is :wikipedia:`bit banging <Bit_banging>`
with counted cycles. It needs:

* a half UI that is a whole number of clock cycles, giving a bit rate within
  270 kbit/s to 330 kbit/s (:pd:`Table 5.9`);
* both paths of every data-dependent branch padded to the same number of
  cycles;
* no :wikipedia:`cache <CPU_cache>` misses, memory wait states or interrupts
  during the message;
* the work of each half UI done within that half UI, about 15.2 instructions
  per bit in total (estimate).

At 300 kbit/s the useful work is :math:`4.6 \times 10^{6}` instructions/s,
but the core is occupied for the whole message. For reference, V-USB sends
and receives low-speed USB, 1.5 Mbit/s, in software on AVR microcontrollers
clocked at 12 MHz to 20 MHz ([USBSER-VUSB]_, home page). That is 8 to
13 clock cycles per bit.

