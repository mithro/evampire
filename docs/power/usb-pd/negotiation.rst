.. _usbpd-negotiation:

Contract negotiation
====================

A power :term:`contract` between a :term:`source` and a :term:`sink` is set
up by a message exchange, in which each message is acknowledged and both
ends must meet time limits.

Message sequence
----------------

:numref:`fig-usbpd-negotiation` shows a complete negotiation. After attach,
the source turns :term:`VBUS` on at 5 V and the two ends exchange four
messages:

#. Source_Capabilities: the source lists what it can supply, as
   :ref:`power data objects <usbpd-pdo>`.
#. Request: the sink picks one item and states the current it will draw
   (:ref:`usbpd-rdo`).
#. Accept: the source agrees. It can also answer Reject, or Wait if it can
   meet the request later (:pd:`Section 7.9.2`).
#. PS_RDY: the source has changed VBUS to the new voltage, and the contract
   is in place.

The receiver of each message answers it with a :term:`GoodCRC` message
(:ref:`usbpd-goodcrc`). Either end can be a board built around evampire.

.. graphviz:: negotiation.dot
   :name: fig-usbpd-negotiation
   :caption: A source and a sink negotiating a fixed 9 V supply, with the
             time limit on each step.
   :alt: Message sequence chart with a source on the left and a sink on the
         right, time running downwards. The sink presents Rd; the source
         turns VBUS on at 5 V; then Source_Capabilities, GoodCRC, Request
         for 9 V at 2 A, GoodCRC, Accept, GoodCRC, PS_RDY with VBUS at 9 V,
         and GoodCRC. Each GoodCRC is sent within 195 µs; each answer within
         15 ms; PS_RDY at least 25 ms and at most 325 ms after Accept.
   :align: center

The voltages and currents a source can offer are on
:doc:`power-levels`, and what each end does around these messages is on
:doc:`source-sink`.

.. _usbpd-goodcrc:

GoodCRC acknowledgement
-----------------------

Every correctly received message addressed to the port is answered with
GoodCRC. The first preamble bit of the GoodCRC must start at least 25 µs
and at most 195 µs after the last bit of the received message
(:numref:`fig-usbpd-goodcrc`). The 25 µs is the minimum gap before any
transmission (*tInterFrameGap*, :pd:`Section 5.3.4.9`, :pd:`Table 5.10`).
The 195 µs is *tTransmit* (:pd:`Section 7.31.1`, :pd:`Table 7.10`). A
message with a wrong checksum is discarded without an answer. The GoodCRC
carries the MessageID of the message it acknowledges
(:pd:`Section 6.1.2`).

.. wavedrom::
   :caption: Acknowledgement timing, not to scale.
   :name: fig-usbpd-goodcrc
   :alt: Timing diagram: a message from the sender, a gap, then a GoodCRC
         from the receiver. One row marks the minimum gap of 25 µs and
         another the latest start of the GoodCRC, 195 µs after the end of
         the message.

   {"signal": [
     {"name": "sender", "wave": "z=....z.......", "data": ["message"]},
     {"name": "receiver", "wave": "z.....z..=...z", "data": ["GoodCRC"]},
     {"name": "minimum gap", "wave": "x.....=..x....", "data": ["25 µs"]},
     {"name": "deadline", "wave": "x.....=.....x.", "data": ["195 µs"]}
   ],
   "config": {"hscale": 1}}

The 195 µs deadline is the tightest time limit in USB Power Delivery. The
other pages link here for it. What it means for software on the processor is
on :ref:`usbpd-goodcrc-deadline`.

Retries and resets
------------------

The sender waits *tReceive* (0.9 ms to 1.1 ms) for the GoodCRC. If none
arrives, it sends the same message again, with the same MessageID, starting
within *tRetry* (195 µs) of the timeout (:pd:`Section 7.31.1`). It retries
at most *nRetryCount* times, which is 2 (:pd:`Section 7.32.2`,
:pd:`Table 7.12`). A message is therefore sent at most three times. A
receiver that sees the same MessageID again acknowledges it and discards the
copy (:pd:`Section 7.32.1.2`).

When all three attempts fail, the sender sends Soft_Reset
(:pd:`Section 7.32.2`). Soft_Reset is a control message that resets the
message counters and protocol state of both ends without changing VBUS;
the two ends then negotiate the contract again (:pd:`Section 7.1.1`). If
Soft_Reset also fails, the port sends a :ref:`Hard Reset <usbpd-hard-reset>`,
which does change VBUS (:pd:`Section 7.1.1`). One missed
GoodCRC therefore costs only a repeated message.
:numref:`fig-usbpd-retries` shows the whole sequence.

.. graphviz:: retries.dot
   :name: fig-usbpd-retries
   :caption: A message whose GoodCRC never arrives: two retries, then
             Soft_Reset, then Hard Reset only if that fails too.
   :alt: Sequence diagram between a sender and a receiver, time downwards.
         The sender sends a message with MessageID n, which is lost; after
         tReceive, 0.9 to 1.1 ms, with no GoodCRC, it sends the same message
         with the same MessageID within tRetry, 195 µs. That is lost, and
         so is a second retry, the last one since nRetryCount is 2. The
         sender then sends Soft_Reset, which resets the protocol without
         changing VBUS. Only if Soft_Reset fails does it send Hard Reset,
         which changes VBUS.

.. _usbpd-timing:

Time limits
-----------

:numref:`tab-usbpd-timing-ack` lists the limits on acknowledging a message,
:numref:`tab-usbpd-timing-msg` the limits on answering one, and
:numref:`tab-usbpd-timing-contract` the limits on setting up and changing a
contract. Each row gives the specification's name for the limit and what it
measures. Values are from :pd:`Table 7.10` unless another source is given;
"none" means the specification sets no limit.

.. list-table:: Time limits on acknowledging a message
   :name: tab-usbpd-timing-ack
   :header-rows: 1
   :widths: 64 18 18

   * - Limit
     - Min (µs)
     - Max (µs)
   * - *tInterFrameGap*: gap before any transmission (:pd:`Table 5.10`)
     - 25
     - none
   * - *tTransmit*: end of a message to the start of its GoodCRC
     - none
     - 195
   * - *tRetry*: timeout to the start of the repeated message
     - none
     - 195

.. list-table:: Time limits on answering a message
   :name: tab-usbpd-timing-msg
   :header-rows: 1
   :widths: 64 18 18

   * - Limit
     - Min (ms)
     - Max (ms)
   * - *tReceive*: sender's wait for GoodCRC
     - 0.9
     - 1.1
   * - *tReceiverResponse*: GoodCRC of a message that needs an answer to
       the start of the answer
     - none
     - 15
   * - *tSenderResponse*: asking side's wait for the answer
     - 27
     - 50

.. list-table:: Time limits on setting up and changing a contract
   :name: tab-usbpd-timing-contract
   :header-rows: 1
   :widths: 64 18 18

   * - Limit
     - Min (ms)
     - Max (ms)
   * - *tFirstSourceCap*: source, VBUS at 5 V to the first
       Source_Capabilities
     - none
     - 250
   * - *tTypeCSendSourceCap*: source, interval between repeats of
       Source_Capabilities
     - 100
     - 200
   * - *tTypeCSinkWaitCap*: sink, wait for Source_Capabilities before it
       may send Hard Reset
     - 310
     - 620
   * - *tSrcTransition*: source, wait after Accept before changing VBUS
       (:pd:`Table 4.7`)
     - 25
     - none
   * - *tSrcTransReq*: source in SPR, GoodCRC of Accept to the start of
       PS_RDY (:pd:`Table 4.7`)
     - none
     - 325
   * - *tSnkStdby*: sink, recommended time to cut its current to 500 mA
       after Accept (:pd:`Table 4.8`)
     - none
     - 15
   * - *tPSTransition*: sink in SPR, wait for PS_RDY before it sends Hard
       Reset
     - 450
     - 550
   * - *tSinkTx*: source, wait after reserving the line with Rp before it
       starts a message exchange (:ref:`usbpd-switchable-rp`)
     - 16
     - 20

The source repeats an unacknowledged Source_Capabilities up to
*nCapsCount*, 50 times (:pd:`Section 7.32.4`, :pd:`Table 7.12`). The
extended power range has longer limits for tSrcTransReq (760 ms,
:pd:`Table 4.7`) and tPSTransition (830 ms to 1020 ms, :pd:`Table 7.10`).
