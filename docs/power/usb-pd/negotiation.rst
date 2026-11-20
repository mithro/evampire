Negotiation and time limits
===========================

The message exchange that sets up a power contract, and its time limits.

Negotiation and time limits
---------------------------

:numref:`fig-usbpd-negotiation` shows a complete negotiation, and
:numref:`tab-usbpd-timing` lists the time limits that apply to both roles.

.. _fig-usbpd-negotiation:

.. graphviz:: negotiation.dot
   :caption: A source and a sink negotiating a fixed 9 V supply. Each
             message that has a correct CRC is answered with GoodCRC. Either
             end can be a board built around evampire.
   :align: center

.. list-table:: Timing values for both roles (:pd:`Table 7.10` unless
   another source is given)
   :name: tab-usbpd-timing
   :header-rows: 1
   :widths: 24 20 56

   * - Name
     - Value
     - Meaning
   * - tTransmit
     - at most 195 µs
     - From the end of a received message's EOP to the start of the
       GoodCRC preamble (:pd:`Section 7.31.1`, :pd:`Table 7.10 <x>`).
   * - tInterFrameGap
     - at least 25 µs
     - Minimum gap before any transmission (:pd:`Table 5.10`).
   * - tReceive
     - 0.9 ms to 1.1 ms
     - How long a sender waits for GoodCRC (:pd:`Section 7.31.1`).
   * - tRetry, nRetryCount
     - at most 195 µs; 2
     - A message without GoodCRC is repeated within tRetry, at most twice
       (:pd:`Section 7.31.1`, :pd:`Table 7.12 <x>`).
   * - tReceiverResponse
     - at most 15 ms
     - From the GoodCRC of a message that needs an answer to the start of
       the answer (:pd:`Section 7.31.2`).
   * - tSenderResponse
     - 27 ms to 50 ms
     - How long the asking side waits for the answer (:pd:`Table 7.10`).
   * - tFirstSourceCap
     - at most 250 ms
     - Source: from VBUS reaching 5 V to the first Source_Capabilities
       (:pd:`Section 7.31.3.3`).
   * - tTypeCSendSourceCap
     - 100 ms to 200 ms
     - Source: interval for repeating Source_Capabilities until it is
       acknowledged, for *nCapsCount* (50) attempts (:pd:`Section 7.31.3.1`;
       :pd:`Table 7.12 <x>`).
   * - tTypeCSinkWaitCap
     - 310 ms to 620 ms
     - Sink: may send Hard Reset if no Source_Capabilities arrives
       (:pd:`Section 7.31.3.2`).
   * - tSrcTransition
     - at least 25 ms
     - Source: wait after Accept before changing the voltage
       (:pd:`Table 4.7`).
   * - tSrcTransReq
     - at most 325 ms (SPR)
     - Source: from the GoodCRC of Accept to the start of PS_RDY
       (:pd:`Table 4.7`).
   * - tPSTransition
     - 450 ms to 550 ms (SPR)
     - Sink: how long it waits for PS_RDY before Hard Reset
       (:pd:`PD Sections 7.31.5.1 <x>` and :pd:`9.2.4.8 <x>`).
   * - tSinkTx
     - 16 ms to 20 ms
     - Source: wait after changing Rp to "sink may not transmit" before
       starting its own exchange (:pd:`Section 7.31.13.1`).
   * - tSnkStdby
     - at most 15 ms
     - Sink: time to cut its current to iSnkStdby (500 mA) before a voltage
       change (:pd:`Table 4.8`).

**Acknowledgement.** Every correctly received message addressed to the port
must be answered with GoodCRC so that its first preamble bit starts between
25 µs and 195 µs after the last bit of the received EOP
(:numref:`fig-usbpd-goodcrc`; *tInterFrameGap*, :pd:`Section 5.3.4.9`;
*tTransmit*, :pd:`Section 7.31.1 <x>`). If the CRC is wrong, the message is
discarded silently.

.. wavedrom::
   :caption: Acknowledgement timing (not to scale). The GoodCRC preamble
             starts at least 25 µs (tInterFrameGap) and at most 195 µs
             (tTransmit) after the end of the received message.
   :name: fig-usbpd-goodcrc
   :alt: Timing diagram: a message from the sender, a gap, then a GoodCRC
         from the receiver; one row marks the minimum gap and another the
         latest start of the GoodCRC.

   {"signal": [
     {"name": "sender", "wave": "z=....z.......", "data": ["message"]},
     {"name": "receiver", "wave": "z.....z..=...z", "data": ["GoodCRC"]},
     {"name": "minimum gap", "wave": "x.....=..x....", "data": ["25 µs"]},
     {"name": "deadline", "wave": "x.....=.....x.", "data": ["195 µs"]}
   ],
   "config": {"hscale": 1}}

**Retries.** A sender that has not received GoodCRC within tReceive sends the
same message again within tRetry, up to twice, so each message is sent at
most three times (:pd:`Section 7.31.1`). After that it sends Soft_Reset
(:pd:`Section 7.31.8.1`), and a failing Soft_Reset leads to Hard Reset
(:pd:`Section 7.1.1`). A missed GoodCRC is therefore recovered
automatically as long as it does not happen three times in a row.
