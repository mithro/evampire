Software cost and hardware assistance
=====================================

This page works out what the processor has to do to run a full-speed USB
device in software: how many instructions per bit, how many samples per
second and how short a reply deadline. It then adds hardware helpers one at
a time and states what each one removes from those needs. The
:ref:`requirement <requirements>` is that the USB protocol runs mostly in
software, with built-in hardware where the timing needs it.

The processor core, its clock and its cycles per instruction are open
(see `Open questions`_). The needs are therefore given as instruction rates
and deadlines. A core with clock :math:`f_\text{clk}` and an average of
:math:`\text{CPI}` clock cycles per instruction meets an instruction rate
:math:`R` when:

.. math::

   \frac{f_\text{clk}}{\text{CPI}} \ge R

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`f_\text{clk}`
     - Processor clock frequency
     - Hz
   * - :math:`\text{CPI}`
     - Average clock cycles per instruction for the code concerned
       (:wikipedia:`cycles per instruction <Cycles_per_instruction>`)
     - cycles
   * - :math:`R`
     - Instruction rate the task needs
     - instructions/s

The instruction counts below are estimates for hand-written assembly in
RV32I, the 32-bit base RISC-V instruction set, not measurements. The
:doc:`/power/usb-pd/software` page uses the same method for the
configuration channel.

Software-only baseline
----------------------

The minimum hardware is the analogue front end of :doc:`analogue` connected
to plain processor-visible bits: D+ and D− receiver outputs as inputs; and
driver enable, D+ level, D− level and pull-up enable as outputs. Everything
else is software (:numref:`fig-usbser-baseline`).

.. graphviz:: software-cost/baseline.dot
   :name: fig-usbser-baseline
   :caption: The software-only baseline: the analogue front end wired to
             processor input and output bits.
   :alt: Block diagram: the analogue front end, with the driver, receivers
         and pull-up, connects to the processor through plain bits. Two
         input bits carry the D+ and D− receiver outputs to the processor.
         Four output bits carry driver enable, D+ level, D− level and
         pull-up enable from the processor. All USB work is in software.
   :align: center

Reception
~~~~~~~~~

For each bit the software has to take a sample at the right moment, undo
NRZI, remove stuffed bits, watch for the end of packet, and build bytes; for
each byte it stores the byte and updates the CRC16
(:numref:`tab-usbser-rx-instr`).

.. list-table:: Estimated instructions to receive one bit in software
   :name: tab-usbser-rx-instr
   :header-rows: 1
   :widths: 46 18 18 18

   * - Work
     - Instructions each
     - Times per bit
     - Instructions per bit
   * - Read the input word
     - 1
     - 1
     - 1
   * - NRZI decode: compare with the previous sample
     - 2
     - 1
     - 2
   * - Count ones, drop a stuffed bit
     - 3
     - 1
     - 3
   * - Shift the bit into the byte
     - 1
     - 1
     - 1
   * - Check for SE0
     - 1
     - 1
     - 1
   * - Loop branch
     - 1
     - 1
     - 1
   * - Store byte, advance pointer, count
     - 3
     - 1/8
     - 0.375
   * - CRC16 update from a 256-entry table
     - 7
     - 1/8
     - 0.875
   * - Total
     -
     -
     - 10.25

The instruction rate needed while a packet arrives is:

.. math::

   R_\text{rx} &= N_\text{rx} \cdot f_\text{bit} \\
               &= 10.25 \times 12 \times 10^{6}\ \text{s}^{-1} \\
               &= 123 \times 10^{6}\ \text{instructions/s}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`R_\text{rx}`
     - Instruction rate needed to receive
     - instructions/s
   * - :math:`N_\text{rx}`
     - Instructions per bit, 10.25 (estimate, :numref:`tab-usbser-rx-instr`)
     - instructions
   * - :math:`f_\text{bit}`
     - Bit rate, 12 Mbit/s
     - bit/s

Three further needs come with it:

* *Sample timing.* Each sample has to land within ± 23.2 ns of the middle of
  its bit (:numref:`fig-usbser-bit-cell`), and the sampling instant has to
  be corrected from the edges, at least every 7 bit times. The loop
  therefore has to have a fixed, known duration of exactly one bit time, or
  measure edge times from a counter.
* *Sample rate.* One sample per bit is 12 million samples per second, if the
  sampling instant is kept centred. A receiver that finds the edges by
  oversampling four times per bit needs 48 million samples per second
  ([USBSER-USB2]_ section 7.1.15.1).
* *No interruptions.* An interruption longer than the 23.2 ns margin during
  a packet loses the packet. Interrupts stay off from the SYNC to the end of
  the reply.

Transmission
~~~~~~~~~~~~

To send, the software takes each bit, inserts a stuffed bit after six ones,
applies NRZI, and writes the output: an estimated 8 instructions per bit,
plus 2 per byte to fetch the next byte. The CRC16 of an IN data packet can
be computed in advance, before the IN token arrives, so it is not counted
here. This gives:

.. math::

   R_\text{tx} &= N_\text{tx} \cdot f_\text{bit} \\
               &= 8.25 \times 12 \times 10^{6}\ \text{s}^{-1} \\
               &= 99 \times 10^{6}\ \text{instructions/s}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`R_\text{tx}`
     - Instruction rate needed to transmit
     - instructions/s
   * - :math:`N_\text{tx}`
     - Instructions per bit, 8.25 (estimate)
     - instructions

The edges must also meet the ± 3.5 ns source jitter limit. A loop of fixed
length places them exactly only if :math:`f_\text{clk}` is a whole multiple
of 12 MHz, or at least 286 MHz (:ref:`usbser-placing-edges`).

Reply deadline
~~~~~~~~~~~~~~

After the end of each packet addressed to the device, the software has to
start the reply within :math:`t_\text{reply}`, at most 541.7 ns
(6.5 bit times) less the receiver and driver delays (:doc:`timing`). For an
OUT or SETUP data packet it compares the CRC16 register with the expected
remainder and picks ACK or NAK; for an IN token it checks the token and
picks a prepared data packet or NAK. With handshake packets prepared in
advance, this is an estimated :math:`N_\text{reply}` = 15 instructions,
which need an instruction rate during that interval of:

.. math::

   R_\text{reply} &= \frac{N_\text{reply}}{t_\text{reply}}
                   \ge \frac{15}{541.7\ \text{ns}} \\
                  &= 27.7 \times 10^{6}\ \text{instructions/s}

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Symbol
     - Meaning
     - Unit
   * - :math:`R_\text{reply}`
     - Instruction rate needed to reply in time
     - instructions/s
   * - :math:`N_\text{reply}`
     - Instructions from the end of packet to the start of the reply, 15
       (estimate)
     - instructions
   * - :math:`t_\text{reply}`
     - Time available, at most 541.7 ns (:doc:`timing`)
     - ns

The IN token can be checked without computing its CRC5. The device knows
its own address and endpoints, so it can prepare the 16 bits that follow
the PID (address, endpoint and CRC5) for each endpoint it serves, and
compare the received bits with that list.

Idle time between packets
~~~~~~~~~~~~~~~~~~~~~~~~~

The host may send a token at any moment, so software has to watch the line
continuously while it is connected. While a terminal program has the port
open, the host polls the bulk IN endpoint, and the device answers NAK each
time it has nothing to send. How often a host does this depends on its
controller.

The upper bound comes from the packet lengths: a token, 2 bit
times, a NAK and 2 bit times take 58 bit times, 4.83 µs, so at most 207
polls fit in a 1 ms frame (:numref:`fig-usbser-polls`). At that rate the
device spends essentially all its time receiving tokens and replying.

.. wavedrom::
   :caption: Repeated IN polls answered with NAK (not to scale).
   :name: fig-usbser-polls
   :alt: Timing diagram: the host sends an IN token, there is a gap of 2
         bit times, the device answers NAK, and after another 2 bit times
         the host sends the next IN token. One poll takes 58 bit times,
         4.83 µs, so up to 207 fit in a 1 ms frame.

   {"signal": [
     {"name": "host", "wave": "3...x.....3...x.....3...",
      "data": ["IN token", "IN token", "IN token"]},
     {"name": "device", "wave": "x.....5.x.........5.x...",
      "data": ["NAK", "NAK"]},
     {"name": "one poll", "wave": "4.........4.........4...",
      "data": ["58 bit times, 4.83 µs", "next poll", "next"]}
   ],
   "config": {"hscale": 1.2}}

Baseline summary
~~~~~~~~~~~~~~~~

With only input and output bits, the processor needs about
:math:`123 \times 10^{6}` instructions per second while receiving and about
:math:`99 \times 10^{6}` while transmitting. It samples once per bit with
edge-corrected timing, without interruption from the start of each packet
to the end of the reply, and transmits from a clock that is a multiple of
12 MHz.
When a bulk IN endpoint is being polled, this applies most of the time.

Hardware helpers
----------------

Each helper below takes one part of the baseline into hardware, in the
order in which they are added, so each step removes the largest remaining
load.
:numref:`fig-usbser-blocks` shows them together and
:numref:`tab-usbser-split` summarises what remains for software after each
step.

.. _fig-usbser-blocks:

.. graphviz:: software-cost/blocks.dot
   :caption: Hardware helpers between the analogue front end and the
             processor, each of which removes one part of the software work.
   :alt: Block diagram: the analogue front end connects to a receive
         deserialiser and a transmit serialiser; the deserialiser feeds a
         CRC checker and a token decoder; a handshake block chooses ACK,
         NAK or STALL from endpoint buffer flags; packet buffers connect to
         the processor; a frame timer receives start-of-frame events and
         trims the clock.
   :align: center

Receive deserialiser
~~~~~~~~~~~~~~~~~~~~

The deserialiser samples D+ and D−, recovers the bit timing from the edges,
detects SYNC and end of packet, undoes NRZI, removes stuffed bits, flags
stuffing errors, and delivers whole bytes into a small first-in, first-out
buffer (:wikipedia:`FIFO <FIFO_(computing_and_electronics)>`).

* *Removes:* all per-bit work, the sample timing and the sample rate.
* *Leaves:* per-byte work, an estimated 12 instructions per byte with the
  CRC16 in software, so
  :math:`R = 12 \times 12 \times 10^{6} / 8 = 18 \times 10^{6}`
  instructions per second while receiving.
* *Latency budget:* a byte arrives every 8 bit times, 666.7 ns. A FIFO of
  :math:`D` bytes lets the software fall :math:`D \times 666.7` ns behind.

Two ways of recovering the bit timing are in use. Oversampling at four times
the bit rate, 48 MHz, with a small state machine that follows the edges, is
what the specification suggests and what the TinyFPGA bootloader,
ValentyUSB and the ulixxe ``usb_cdc`` core do ([USBSER-TINYFPGA]_,
``usb_fs_rx.v``; [USBSER-VALENTYUSB]_, ``rx/clock.py``;
[USBSER-ULIXXE]_). The alternative is one sample per bit at a phase set
from the SYNC and corrected at each edge, from a clock that is a multiple of
12 MHz; it needs fewer fast flip-flops but a finer phase adjustment.
:numref:`fig-usbser-sampling` compares the two.

.. wavedrom::
   :caption: Oversampling at four times the bit rate against one sample per
             bit (not to scale).
   :name: fig-usbser-sampling
   :alt: Timing diagram over four bits. A 48 MHz clock has four periods per
         bit; the oversampling receiver samples on every one and follows
         the edges with a state machine. The other receiver takes one
         sample per bit in the middle of each bit, at a phase set from the
         SYNC pattern and corrected at each edge.

   {"signal": [
     {"name": "line", "wave": "3...4...4...3...",
      "data": ["bit: J", "K", "K", "J"]},
     {"name": "48 MHz, 4 samples per bit", "wave": "pppppppppppppppp"},
     {"name": "one sample per bit", "wave": "0.10..10..10..10"}
   ],
   "config": {"hscale": 1}}

The sampling logic runs at 48 MHz or more in the oversampling case. On
gf180mcu, a D flip-flop of the 7-track standard cell library has a
clock-to-output delay of 0.676 ns and a setup time of 0.229 ns, at the
typical corner, 5 V and 25 °C ([USBSER-GF180-SC]_, cell
``gf180mcu_fd_sc_mcu7t5v0__dffq_1``). Together they take a small part of the
20.8 ns period of 48 MHz. Custom fast cells, for example
:wikipedia:`current-mode logic <Current-mode_logic>`, are an option for a
higher oversampling rate.

Transmit serialiser
~~~~~~~~~~~~~~~~~~~

The serialiser takes bytes from a FIFO, sends SYNC, inserts stuffed bits,
applies NRZI, drives J, K and SE0, and ends with the end of packet. It runs
from a clock that is a multiple of 12 MHz.

* *Removes:* all per-bit transmit work and the edge placement need.
* *Leaves:* an estimated 2 instructions per byte to fill the FIFO,
  :math:`3 \times 10^{6}` instructions per second while transmitting.
* *Latency budget:* the FIFO must not run empty during a packet:
  :math:`D \times 666.7` ns ahead for a FIFO of :math:`D` bytes, or the
  whole packet loaded before it starts.

Hardware CRC5 and CRC16
~~~~~~~~~~~~~~~~~~~~~~~

A CRC16 register on the receive and transmit byte streams, and a CRC5 check
on received tokens, is a few dozen flip-flops and exclusive-or gates.

* *Removes:* 7 of the 12 receive instructions per byte, leaving
  :math:`5 \times 12 \times 10^{6} / 8 = 7.5 \times 10^{6}` instructions per
  second; the CRC check moves out of the reply deadline.
* *Leaves:* the reply deadline itself.

Automatic handshakes
~~~~~~~~~~~~~~~~~~~~

Per endpoint, the software sets flags such as "buffer ready to receive",
"data ready to send" and "halted". A token decoder matches the address and
endpoint, and a small state machine replies by itself
([USBSER-USB2]_ section 8.4.6, :numref:`fig-usbser-handshake`):

* to OUT data with a good CRC and a ready buffer: ACK, and the buffer is
  marked full; with no ready buffer: NAK; when halted: STALL;
* to IN with data ready: the data packet, then wait for the host's ACK;
  with no data: NAK;
* to SETUP: always ACK, into a buffer reserved for the 8-byte request;
* the DATA0/DATA1 sequence bit per endpoint.

.. graphviz:: software-cost/handshake.dot
   :name: fig-usbser-handshake
   :caption: State machine of the automatic handshakes.
   :alt: State diagram: from idle, a token is decoded for address, endpoint
         and CRC5; a token not for this device is ignored. A SETUP token
         leads to receiving the 8-byte DATA0, always answered with ACK into
         the SETUP buffer, with DATA1 next. An OUT token leads to receiving
         DATA0 or DATA1: with a bad CRC no reply; when halted STALL; with no
         room NAK; with the same sequence bit as last time ACK and discard
         the copy; when ready ACK, mark the buffer full and toggle the bit.
         An IN token checks the endpoint flags: when halted STALL; with no
         data NAK; with data ready send DATA0 or DATA1, then wait for the
         host: on ACK toggle the bit and mark the buffer empty, with no ACK
         keep the data for a retry. Each branch returns to idle.
   :align: center

* *Removes:* the reply deadline and all per-packet work. Software is
  involved only when a buffer has been filled or emptied, and a late answer
  costs only a NAK and a retry by the host.
* *Leaves:* filling and emptying packet buffers at the rate of the data, and
  the requests of :doc:`transactions` on endpoint 0, with deadlines of
  50 ms and more.

This is the split of the eptri interface of ValentyUSB, which answers NAK
until the processor arms an endpoint's buffer and adds the CRC16 to IN
packets itself ([USBSER-VALENTYUSB]_, ``cpu/eptri.py``).

Frame timer
~~~~~~~~~~~

A counter that latches the local clock count at each start-of-frame token
lets software, or a small control loop, trim an oscillator against the
host (:doc:`timing`). It is needed only if the USB clock is not derived
from a crystal.

Packet buffers
~~~~~~~~~~~~~~

Once automatic handshakes are added, packets are held in buffers that the
processor reads and writes. A serial port with 64-byte packets needs one
64-byte buffer per direction of each bulk endpoint, or two, so that the
hardware fills one while the software works on the other. It also needs an
8-byte buffer for SETUP, and buffers of the chosen sizes for endpoint 0 and
the interrupt endpoint (:numref:`fig-usbser-buffers`).

.. graphviz:: software-cost/buffers.dot
   :name: fig-usbser-buffers
   :caption: Two 64-byte buffers per bulk direction and the SETUP buffer
             between the USB hardware and the processor.
   :alt: Block diagram: the deserialiser, serialiser and automatic
         handshakes fill bulk OUT buffer A while the processor reads bulk
         OUT buffer B; the hardware sends from bulk IN buffer A while the
         processor fills bulk IN buffer B; an 8-byte SETUP buffer passes
         from the hardware to the processor. The roles of A and B swap
         after each packet.
   :align: center

Summary of the helpers
----------------------

.. list-table:: What software has to do after each hardware step
   (instruction counts are estimates)
   :name: tab-usbser-split
   :header-rows: 1
   :widths: 30 22 22 26

   * - Hardware added
     - Receive (10\ :sup:`6` instr./s)
     - Transmit (10\ :sup:`6` instr./s)
     - Shortest deadline
   * - None
     - 123
     - 99
     - Each sample
   * - Deserialiser
     - 18
     - 99
     - Reply, 541.7 ns
   * - and serialiser
     - 18
     - 3
     - Reply, 541.7 ns
   * - and CRC
     - 7.5
     - 3
     - Reply, 541.7 ns
   * - and handshakes
     - Data rate
     - Data rate
     - Request, 50 ms

Chosen split
------------

The chosen split builds the first four helpers in hardware: the receive
deserialiser, the transmit serialiser, the CRC, and automatic handshakes
with packet buffers. Software does everything else: enumeration, the
descriptors, the CDC-ACM requests, moving the serial data, and the policy of
when to connect and disconnect. With this split, USB places no packet-level
deadline on the processor, so it can serve USB, USB Power Delivery and
Ethernet duties in any order (see :doc:`usb-pd-roles`).

Smaller splits remain options and depend on the processor. Without automatic
handshakes, the processor has to meet the reply deadline,
:math:`f_\text{clk}/\text{CPI} \ge N_\text{reply}/t_\text{reply}`, and be
free at the end of every packet for the device. Without the deserialiser and
serialiser, it needs the rates of the baseline. Another option is a small
programmable state machine in place of fixed logic for the deserialiser and
serialiser, as the RP2040's programmable I/O does in Pico-PIO-USB
([USBSER-PICO-PIO-USB]_).

Reference implementations
-------------------------

:numref:`tab-usbser-refs` lists implementations of USB devices that split
the work in different ways. They show what has been done elsewhere with
other hardware; the figures for evampire come from the analysis above.

.. list-table:: USB device implementations and their hardware
   :name: tab-usbser-refs
   :header-rows: 1
   :widths: 22 12 30 36

   * - Project
     - Speed
     - Hardware and clock
     - Done in hardware
   * - V-USB
     - Low
     - AVR, 12 MHz to 20 MHz
     - Nothing; one interrupt on an edge. CRC not checked, except at 18 MHz
   * - rv003usb
     - Low
     - CH32V003 RISC-V, 48 MHz
     - Nothing; a pin-change interrupt. CRC computed while receiving
   * - Pico-PIO-USB
     - Full
     - RP2040 I/O state machines, a multiple of 12 MHz
     - Receive edge detection, NRZI decode, end of packet; transmit line driving
   * - ValentyUSB with eptri
     - Full
     - iCE40UP5K FPGA (Fomu), 48 MHz and 12 MHz
     - Sampling at 4 times the bit rate, NRZI, stuffing, CRC, replies, endpoint buffers
   * - TinyFPGA bootloader
     - Full
     - FPGA, 48 MHz
     - The whole CDC-ACM serial port
   * - ``usb_cdc``
     - Full
     - FPGA, 48 MHz
     - The whole CDC-ACM serial port, in 1158 iCE40 logic cells
   * - Tiny Tapeout GF 0.2 project 130
     - Full
     - gf180mcu chip, standard digital I/O, 48 MHz
     - A CDC-ACM to UART bridge, based on the TinyFPGA design

The sources are: V-USB [USBSER-VUSB]_, ``usbdrv.h`` and ``Readme.txt``;
rv003usb [USBSER-RV003USB]_, ``README.md``; Pico-PIO-USB
[USBSER-PICO-PIO-USB]_, ``src/usb_rx.pio`` and ``src/pio_usb.c``, where
transmit bit stuffing, the CRC and the handshakes are in software;
ValentyUSB [USBSER-VALENTYUSB]_, ``cpu/eptri.py``, and the Fomu bootloader
[USBSER-FOBOOT]_; TinyFPGA [USBSER-TINYFPGA]_, ``usb_serial_ctrl_ep.v``;
``usb_cdc`` [USBSER-ULIXXE]_, ``README.md``; and the Tiny Tapeout project
page [USBSER-TTGF130]_.


The pure-software projects run at low speed, where a bit lasts 666.7 ns;
the low-speed limits they work around are discussed in :doc:`alternatives`.
The Tiny Tapeout GF 0.2 project shows a full-speed CDC-ACM device made in
gf180mcu and driven from the standard digital I/O; its project page records
that it enumerated and passed data ([USBSER-TTGF130]_).

Open questions
--------------

* The processor core, its clock :math:`f_\text{clk}` and its CPI, which set
  whether a smaller split than the first four helpers meets the deadlines.
* The measured instruction counts, by writing the receive, transmit and
  reply code and running it on the chosen core or an FPGA model of it.
* Fixed logic or a small programmable state machine for the serialiser and
  deserialiser.
* Oversampling or edge-corrected single sampling, and the sampling clock.
* Custom fast cells, such as current-mode logic, for a higher sampling rate.
* The FIFO depths and the number and size of the packet buffers.
* Whether the frame timer is needed, which depends on the clock source
  chosen in :doc:`timing`.
