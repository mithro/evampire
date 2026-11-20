What USB Power Delivery needs from software and hardware
========================================================

What the processor must do to send and receive messages in software, and which hardware helpers reduce that.

Implementing USB Power Delivery in software
-------------------------------------------

The :ref:`requirement <requirements>` is that USB Power Delivery runs mostly
in software on the RISC-V processor, with dedicated digital hardware only
where software cannot meet the timing. This section starts from the absolute
minimum hardware, works out what software then has to do and how fast, and
adds a helper only where the numbers show software is not enough.

Baseline: analog front end and plain input and output bits
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The minimum hardware per port is the analog front end described in
`Analog blocks`_ (:numref:`fig-usbpd-port-blocks`: switchable Rp, Rd and
dead-battery Rd, VCONN switch, comparators, BMC driver) connected to plain
processor-visible bits:

* outputs: Rp level and enable, Rd enable, VCONN enable per CC pin, driver
  enable and driver data, comparator threshold selection;
* inputs: the comparator outputs.

Everything else is firmware: BMC encoding and decoding, 4b5b, CRC-32, SOP
detection, GoodCRC generation, retries, all timers, the Type-C attach,
toggling, Try.SRC and Try.SNK state machines, and the PD protocol and policy
including power role swap, source capabilities and cable discovery.

The time scales are very different (:numref:`tab-usbpd-timescales`):

.. list-table:: Time scales of the work
   :name: tab-usbpd-timescales
   :header-rows: 1
   :widths: 30 25 45

   * - Task
     - Time scale
     - Difficulty in software
   * - Bit timing (receive and transmit)
     - 1.5 µs between edges; ± 50 ns edge placement
     - Hard; analysed below
   * - GoodCRC reply
     - 25 µs to 195 µs after a message
     - Moderate; analysed below
   * - FRS detection (if supported)
     - 30 µs to 50 µs
     - Moderate
   * - Protocol replies, attach, toggling, swaps
     - 15 ms and longer
     - Easy

The processor clock
~~~~~~~~~~~~~~~~~~~

The numbers below depend on the processor's clock and on how many clock
cycles it needs per instruction (*CPI*). Neither is fixed yet, so two cases
are used:

* a **multi-cycle core** such as PicoRV32, with an average CPI of about 4
  (load 5 cycles, taken branch 5 to 6, simple ALU 3; [USBPD-PICORV32]_, CPI
  table);
* a **pipelined core**, assumed here to reach a CPI of about 1.3 on this kind
  of code (an assumption, not a measured value).

For the clock, evampire already has a 125 MHz reference
(:ref:`clock <arch-clock>`), so 31.25 MHz (÷ 4) and 62.5 MHz (÷ 2) are
natural choices. The gf180mcu 7-track standard cell library, at its typical
corner (5 V, 25 °C), gives a D flip-flop clock-to-output delay of 0.676 ns
(with the minimum load) and a setup time of 0.229 ns ([USBPD-GF180-SC]_, cell
gf180mcu_fd_sc_mcu7t5v0__dffq_1 and databook conditions page). At 50 MHz that
leaves :math:`20\ \text{ns} - (0.676 + 0.229)\ \text{ns} = 19.1\ \text{ns}`
per clock for logic and wiring. How many gate levels fit in that depends on
the core and the layout and is not derived here; as an order of magnitude,
the PicoRV32-based "Raven" chip, made in a different 180 nm process (X-FAB
XH018), was reported to run at 100 MHz [USBPD-RAVEN]_. This page uses
**50 MHz as a working assumption** and shows how the results change with the
clock.

Receive by polling
~~~~~~~~~~~~~~~~~~

With only a plain input bit, the processor reads the comparator in a loop,
notes the time of each change with the cycle counter, and decodes as it
goes.

*How often it must sample.* The decoder tells a ``0`` (an interval of 1 UI)
from half of a ``1`` (0.5 UI) by comparing each interval with 0.75 UI. Each
edge can be up to 0.07 UI from its ideal time (receive mask, :pd:`Table 5.8`),
so an interval can be off by up to :math:`2 \times 0.07 = 0.14` UI. That
leaves a margin of :math:`0.25 - 0.14 = 0.11` UI, which at the fastest rate
(`Bit rate`_) is :math:`0.11 \times 3.030\ \mu\text{s} = 333\ \text{ns}`. The
sampling period adds up to one period of error to each interval, so it must
be shorter than about 333 ns. This page uses :math:`T_\text{poll}` = 250 ns,
4 million samples per second. The number of samples per bit is then:

.. math::

   N_\text{poll} = \frac{T_\text{UI,min}}{T_\text{poll}}
                 = \frac{3.030\ \mu\text{s}}{0.250\ \mu\text{s}}
                 = 12.1 \approx 12

*How many instructions per bit.* These counts
(:numref:`tab-usbpd-poll-instr`) are **estimates** for hand-written RV32I
assembly (RV32I is the 32-bit base RISC-V instruction set), not
measurements. The poll itself is two instructions: a load of the input word
and a compare-and-branch back to the load while the value is unchanged.

.. list-table:: Estimated instructions for receiving one bit by polling
   :name: tab-usbpd-poll-instr
   :header-rows: 1
   :widths: 40 15 15 30

   * - Work
     - Instructions each
     - Times per bit
     - Instructions per bit
   * - Poll: load input, compare-and-branch
     - 2
     - 12
     - 24
   * - Edge: read cycle counter, subtract, compare with 0.75 UI, update state
     - 10
     - 2 (worst case, a ``1``)
     - 20
   * - Bit: shift into symbol, count
     - 4
     - 1
     - 4
   * - Symbol: 4b5b table lookup and CRC-32 nibble update
     - 16
     - 1/5
     - 3.2
   * - **Total**
     -
     -
     - **51.2**

The instruction rate and clock needed are then:

.. math::

   R_\text{instr} &= N_\text{instr/bit} \cdot f_\text{bit,max} \\
                  &= 51.2 \times 330\,000\ \text{s}^{-1}
                   = 16.9 \times 10^{6}\ \text{s}^{-1}

.. math::

   f_\text{clk} = R_\text{instr} \cdot \text{CPI}

where :math:`R_\text{instr}` is the instruction rate,
:math:`N_\text{instr/bit}` = 51.2 (estimate above), :math:`f_\text{bit,max}`
= 330 kbit/s (:pd:`Table 5.9`) and CPI is cycles per instruction. With CPI
1.3, :math:`f_\text{clk} = 16.9 \times 1.3 = 22` MHz; with CPI 4,
:math:`16.9 \times 4 = 68` MHz.

Polling also has a fixed cost per sample regardless of edges: a multi-cycle
core needs about 10 cycles per poll iteration (load 5 + taken branch 5,
[USBPD-PICORV32]_), so 4 million polls per second alone take 40 MHz; a
pipelined core needing about 4 cycles per iteration (an estimate) takes
16 MHz.

*What this means.* On a pipelined core at 50 MHz, polled receive fits, using
about :math:`22 / 50 = 44\ \%` of the processor while a message is on the
wire. On a multi-cycle core at 62.5 MHz or below it does not fit (68 MHz
needed). In both cases interrupts must be off for the whole message, because
any interrupt longer than about 333 ns corrupts the timing.

Receive by interrupt on each edge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An interrupt per comparator edge avoids polling between edges. The worst case
is a run of ``1`` bits, two edges per UI:
:math:`2 \times 330\,000 = 660\,000` edges per second. If entering and
leaving the interrupt and handling the edge costs 40 to 60 cycles (an
**estimate** for saving and restoring a few registers on a small core), the
load is :math:`660\,000 \times 40 = 26.4` to
:math:`660\,000 \times 60 = 39.6` million cycles per second, and the timestamp
is only as accurate as the interrupt latency. This is worse than polling and
is not considered further.

Transmit by cycle-counted output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To transmit, the processor computes the next edge time, waits in a loop on
the cycle counter, and writes the output bit. The edge is late by up to one
loop iteration, so the timing uncertainty (peak to peak) is:

.. math::

   \Delta t_\text{edge} = \frac{N_\text{loop}}{f_\text{clk}}

where :math:`N_\text{loop}` is the number of cycles in one iteration of the
wait loop (read counter, compare-and-branch) and :math:`f_\text{clk}` is the
core clock. **Estimates** of :math:`N_\text{loop}`: about 4 cycles on a
pipelined core and about 12 on a multi-cycle core
(:numref:`tab-usbpd-tx-jitter`).

.. list-table:: Transmit edge uncertainty (peak to peak) against the ± 50 ns
   reading of the mask
   :name: tab-usbpd-tx-jitter
   :header-rows: 1
   :widths: 25 25 25 25

   * - Core clock
     - Pipelined (4 cycles)
     - Multi-cycle (12 cycles)
     - Meets ± 50 ns?
   * - 31.25 MHz
     - 4 / 31.25 MHz = 128 ns
     - 12 / 31.25 MHz = 384 ns
     - No / No
   * - 50 MHz
     - 80 ns
     - 240 ns
     - Yes, barely / No
   * - 62.5 MHz
     - 64 ns
     - 192 ns
     - Yes / No

Measuring edge time from the cycle counter, rather than counting loop
iterations, keeps the average bit rate exact, so the 0.25 % drift limit is not
a problem. The ± 50 ns edge placement is.

The GoodCRC deadline
~~~~~~~~~~~~~~~~~~~~

After the EOP of a received message the processor must start sending GoodCRC
between 25 µs and 195 µs later. With the CRC updated nibble by nibble during
reception (included in the receive estimate above), checking it at the EOP is
one comparison with the fixed remainder. The GoodCRC packet for each of the
eight MessageID values, including its own CRC, can be prepared in advance. So
the work after the EOP is a few tens of instructions, about 1 µs, plus the
25 µs wait. The deadline is met as long as interrupts stay off from the start
of the message to the end of the GoodCRC. As source and as sink the deadline
is the same; no source-side timing is tighter than this (the next tightest is
`Fast role swap`_ detection, 30 µs to 50 µs, and then the millisecond
limits).

What the processor cannot do during a message
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With polled receive and cycle-counted transmit, the processor is fully busy
from the first preamble edge of a received message to the end of its
GoodCRC. The worst case is a seven-object message at the slowest bit rate:

.. math::

   t_\text{busy} &= t_\text{msg} + t_\text{gap} + t_\text{GoodCRC} \\
                 &= 1589\ \mu\text{s} + 195\ \mu\text{s} + 552\ \mu\text{s}
                  = 2336\ \mu\text{s}

where :math:`t_\text{msg}` = 429 bits × 3.704 µs
(:numref:`tab-usbpd-duration`), :math:`t_\text{gap}` = 195 µs is the longest
allowed gap (tTransmit, :pd:`Section 7.31.1`) and :math:`t_\text{GoodCRC}` =
149 bits × 3.704 µs.

During those 2.3 ms the processor cannot service the Ethernet frame buffers
or the transceiver :ref:`configuration interface <arch-config-interface>`
(the management interface of :clause:`22`). The forwarding path between the
Ethernet ports is entirely hardware and is not affected (see
:doc:`../architecture/index`). Frames for the processor wait in the receive
buffer, which holds one or two frames; at the processor's expected traffic of
well below 1 Mbit/s (:ref:`requirements`), a full-size 1522-byte frame
arrives on average no more often than every
:math:`1522 \times 8\ \text{bit} / 1\ \text{Mbit/s} = 12.2\ \text{ms}`, so a
2.3 ms pause rarely loses a frame, and a lost frame is resent by higher-level
protocols. A burst of frames during a USB message can be lost.

Two ports in software
~~~~~~~~~~~~~~~~~~~~~

With two ports, messages on both can arrive at the same time: as a sink the
port cannot control when the other side transmits, and even as a source the
other side may transmit when Rp allows it. A single polling loop could read
both comparators in one input word, but the per-edge work doubles: the
24 poll instructions plus twice the 27.2 instructions of edge, bit and symbol
work, :math:`24 + 2 \times 27.2 = 78.4` instructions per bit, or
:math:`78.4 \times 330\,000 = 25.9` million instructions per second
(estimate). Transmitting on one port while receiving on the other is not
possible with a cycle-counted transmit loop. In practice software serves one
port at a time; a message lost on the other port is resent by its sender up
to twice (tReceive, then tRetry), so an occasional collision costs about
1 ms, and three losses in a row lead to a Soft_Reset.

Hardware helpers, in order of need
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From the numbers above, whether a digital helper is needed depends on the
processor core, which is not yet chosen:

1. **Transmit edge timing** cannot be met on a multi-cycle core at any clock
   up to 62.5 MHz, nor on a pipelined core below about 50 MHz
   (:numref:`tab-usbpd-tx-jitter`). A **timer compare output** (a counter, a
   compare register and an output bit that changes when they match) places
   each edge to one clock period (16 ns to 32 ns at 62.5 MHz to 31.25 MHz)
   whatever the processor is doing. Software loads the next edge time after
   each edge, 1.5 µs ahead. This is a generic microcontroller timer feature,
   not USB-specific.
2. **Receive timing** cannot be met by polling on a multi-cycle core at
   62.5 MHz or below. A **timer capture input** (the counter value latched
   into a small FIFO on each comparator edge) removes polling. Per bit,
   software then reads up to two timestamps (about 12 instructions each with
   the classification) plus the bit and symbol work:
   :math:`2 \times 12 + 4 + 3.2 = 31.2` instructions per bit, or
   :math:`31.2 \times 330\,000 = 10.3` million per second (estimate): 13 MHz
   at CPI 1.3, 41 MHz at CPI 4. Interrupts can stay on as long as the FIFO
   does not overflow: at one edge per 1.515 µs, a FIFO of 8, 16 or 32 entries
   gives :math:`8 \times 1.515 = 12.1`, 24.2 or 48.5 µs of tolerance to
   interrupt latency. This too is a generic timer feature.
3. **CRC-32** is not needed in hardware: a 16-entry table (64 bytes of
   read-only memory) and about 6 instructions per nibble are included in the
   estimates above. The RISC-V carry-less multiply instructions of the Zbc
   bit-manipulation extension (https://github.com/riscv/riscv-bitmanip) could
   speed it up but are not needed.
4. **USB-specific helpers** (a BMC decoder, automatic GoodCRC as in the onsemi
   FUSB302B [USBPD-FUSB302B]_, or a BMC transceiver as in the STUSB1602
   [USBPD-STUSB1602]_, which decodes BMC and hands the bits to a
   microcontroller over a serial interface) are not required by the numbers
   above for one port.

Recommended split
~~~~~~~~~~~~~~~~~

* **Hardware, per port:** the analog front end (switchable Rp, Rd and
  dead-battery Rd, VCONN switch with current limit, comparators with
  selectable thresholds, BMC driver with controlled edges), connected to
  plain processor-visible input and output bits.
* **Software:** everything else, including BMC, 4b5b, CRC, GoodCRC, retries,
  the attach and toggling state machines, the protocol, cable discovery,
  power role swap and the :ref:`power budget <power-budget>`.
* **Digital helpers:** none, if the processor is a pipelined core running at
  50 MHz or faster. If it is a multi-cycle core, or runs slower, the
  arithmetic above shows that one timer compare output (for transmit) and
  one timer capture input with a FIFO (for receive) per port are needed;
  both are generic timer features.

With no helper, interrupts are disabled for up to 2.3 ms per message, and two
ports rely on retries when their messages overlap. Adding the timer channels
anyway, to remove these limits, is listed as an option under
`Open design decisions`_.
