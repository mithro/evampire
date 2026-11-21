# To do: open items from the design review

Each item is a problem a review of the design pages found but did not fix,
because the right answer needs a design decision, a look at a standard, or
a simulation. "Where" gives the page. "Suggestion" is a starting point, not
a decision. Items marked *(from memory)* rest on a reviewer's recollection
of a standard and must be checked against it first.

## Forwarding and RGMII

### Inter-frame gap removed by each evampire

- **Where:** `docs/ethernet/rgmii/port-logic.rst` (rate-matching buffer), `docs/ethernet/rgmii/frames.rst` (gap), `docs/architecture/index.rst`
- **Issue:** No page works out how much inter-frame gap one unit can remove, or how many units can sit in series on a link. "Holds up to 7 bytes more" for the preamble suggests a delay that varies from frame to frame, which the requirements call fixed.
- **Suggestion:** Specify a constant delay measured from the start frame delimiter. Then publish the gap after N units, roughly 12 − N − floor(L × 200 ppm) bytes against the 8-byte receive limit, and state the largest N. Whether units are chained is undecided, so give the function.

### Longest forwarded frame ignores start uncertainty and overrun

- **Where:** `docs/requirements.rst` (longest-frame equation)
- **Issue:** The example takes a slack of 2 bytes to give 10,000 bytes. The read side starts with up to one clock cycle of uncertainty, which uses about one byte of that slack. No page says what happens when the buffer overruns or the source link drops mid-frame.
- **Suggestion:** Define the slack after the start uncertainty, total the buffer depth (slack both ways, pointer synchroniser lag, the LLDP delay), and state that an overrun ends the frame with an error.

### Pause frames and Energy-Efficient Ethernet

- **Where:** `docs/requirements.rst` (forwarding), `docs/ethernet/rgmii/mdio.rst`, `docs/ethernet/rgmii/data.rst`
- **Issue:** Neither is mentioned. Pause frames are forwarded, but processor frames ignore a pause received on that port. Low-power idle would have to pass through two transceivers and the buffer, and a transceiver may stop its receive clock during it.
- **Suggestion:** Decide and document: forward pause frames and advertise pause only if both link partners do; have software clear the Energy-Efficient Ethernet advertisement on both transceivers.

### "Hub" is not what the pages specify

- **Where:** `docs/overview.rst`, `README.md`, `CLAUDE.md`
- **Issue:** In IEEE 802.3 a hub is a half-duplex repeater. The pages specify a full-duplex cut-through relay with one filtered address and a processor tap. The closest standard device may be the IEEE 802.1Q Two-Port MAC Relay *(from memory)*.
- **Suggestion:** Check the Two-Port MAC Relay definition and its reserved-address table. It may answer the open question about which other frames not to forward. Then either rename the device or say how it differs from a hub.

### Block diagram does not show the LLDP block

- **Where:** `docs/architecture/block-diagram.dot`, `docs/architecture/index.rst`
- **Issue:** The text now describes an LLDP block that controls the forwarding paths, but the diagram and its alt text have no such block or control arrow.
- **Suggestion:** Add the block and dashed control arrows to both output selectors, update the alt text, and check the rendered diagram at both widths.

### 125 MHz clock source, reset and link-down behaviour

- **Where:** `docs/architecture/index.rst` (clock and reset), `docs/ethernet/rgmii/io-cells.rst`, `docs/ethernet/rgmii/port-logic.rst`
- **Issue:** The source of the 125 MHz clock, its duty cycle and its tolerance are not specified, and no page defines reset. A clock taken from a transceiver disappears when that transceiver is reset. Forwarding depends on software having booted and configured both transceivers.
- **Suggestion:** Add a clock and reset page: source options (oscillator, transceiver output, 25 MHz with an on-chip PLL, one oscillator shared with both transceivers), the duty cycle the source must meet, reset defaults (forwarding off), and how a buffer is flushed when its receive clock stops.

### Speed policy only steps down and does not check duplex

- **Where:** `docs/ethernet/rgmii/speed-policy.rst`
- **Issue:** After a link drops, only that port advertises every speed again; the other port stays restricted, so the pair may never return to 1000 Mbit/s. The policy compares speed only, so a partner detected as half duplex gives a duplex mismatch.
- **Suggestion:** Restore the advertisement on both ports when either link drops, compare duplex as well as speed, and state how fast software must react to a speed change.

### Transmit skew budget for the standard pad

- **Where:** `docs/ethernet/rgmii/io-cells.rst`, `docs/ethernet/rgmii/timing.rst`
- **Issue:** The page now gives the 0.27 ns rise and fall difference, but there is no full budget for TskewT with pad-to-pad mismatch and load differences, and the slow edges are not converted into threshold-crossing uncertainty at the transceiver.
- **Suggestion:** Write the budget with each term, evaluate the 24 mA pad cell, and decide whether the loopback calibration on the port-logic page is required for the first version. Needs a SPICE or board-level simulation.

### Pad count for the whole chip

- **Where:** `docs/ethernet/rgmii/io-cells.rst`, `docs/power/converters/first-version.rst`, `docs/power/usb-pd/analogue.rst`
- **Issue:** Only the RGMII signals (27) and the PWM outputs (8) are counted. Reviewers' estimates are about 33 to 37 for RGMII with resets and supplies, 23 to 35 for converter control and sensing, and 8 to 13 for each USB Type-C port.
- **Suggestion:** Add one table of pads per function for the first version, with supplies, and compare it with the pad ring of the wafer.space slot.

## Power over Ethernet

### Hardware timers behind each timed step of a port that supplies power

- **Where:** `docs/power/poe/pse-sequencing.rst`, `docs/power/poe/monitoring.rst`
- **Issue:** The requirement for a safe state now exists, but the limits table still has no row for the signature drop-out, class and mark events or inrush. The page asks for tens to hundreds of readings per second, while a powered device may hold its signature with pulses of about 7 ms *(the 6 ms minimum valid pulse is from memory)*.
- **Suggestion:** Add a row for each timed state with its hardware maximum. State the continuous sampling rate needed to see a short signature pulse. Consider a hardware state machine for the timed sequence with software setting policy only.

### Class steps in the translation tables

- **Where:** `docs/power/poe/translation.rst`, `docs/power/poe/sequence.rst`
- **Issue:** The tables say "class 5 fits" or "class 2 applies" as if the port could assign any class. The number of class events caps the result at class 3, 4, 6 or 8, and a device gets the class it asked for if that is within the cap. A device asking for class 6 cannot be given class 5 *(from memory)*.
- **Suggestion:** Check Table 145-11 and rework the tables by requested class: assigned if it fits, otherwise the next lower cap, otherwise no power.

### Inrush and peak power are not in the power budget

- **Where:** `docs/power/index.rst` (budget), `docs/power/poe/translation.rst`, `docs/power/poe/power-sourcing.rst`
- **Issue:** A port must supply at least 0.4 A during inrush, about 20 W for 50 to 75 ms, whatever the class. A 15 W USB input cannot. A powered device may also draw peak power above its class for 50 ms.
- **Suggestion:** Add inrush and peak terms to the budget, as bus hold-up energy or reserved headroom, and say which input levels cannot start a port at all.

### Where the budget formula subtracts the board's power

- **Where:** `docs/power/index.rst` (budget), `docs/power/poe/translation.rst`
- **Issue:** P_out = P_in × η − P_board subtracts the board's power after both converters, but the board supplies hang off the bus between them. The pass-through table also multiplies by 0.85 where the two efficiencies give 0.846.
- **Suggestion:** Split η per converter and subtract the board's power at the bus. Say whether bridge and switch losses are inside the input efficiency. Recompute the tables.

### What happens when the input side forces a reduction

- **Where:** `docs/power/poe/sharing.rst`, `docs/power/poe/lldp.rst`, `docs/power/index.rst`
- **Issue:** Lowering an Ethernet output over LLDP can take 10 s, and class 1 to 3 devices cannot be lowered. No page gives the time port A has to comply with a lowered allocation, or the sequence when the input collapses.
- **Suggestion:** Add a timeline for each input event (allocation lowered, input lost, role swap) with the response time and who acts, hardware or software. Look up the powered device's compliance time in the standard.

### Dual-role port: reverse path, unpowered state and self-loop

- **Where:** `docs/power/poe/dual-role.rst`
- **Issue:** The supply-side switch described blocks one direction only, so a remote source of the other polarity could charge the port's supply rail through the body diode. With no power the port must still show the signature. The port's own supply could also turn on its own powered-device path.
- **Suggestion:** State that the disconnect blocks in both directions, give the leakage allowed beside the signature resistor (about 615 kΩ by one estimate), define the unpowered default, and say how the self-loop is prevented.

### Port switch energy is quoted at the maximum

- **Where:** `docs/power/poe/monitoring.rst`, `docs/power/poe/hv-options.rst`
- **Issue:** "57 W for 75 ms" (4.3 J) is given as the switch requirement. The standard obliges only 6 ms or 10 ms of current limit, about a tenth of that energy, and the difference decides whether an on-chip switch is plausible.
- **Suggestion:** Give the energy as a range from the minimum obligation to the chosen maximum, apply the page's thermal estimate to each end, and treat foldback as a design choice.

### Stacked devices against the documented N-well limit

- **Where:** `docs/power/poe/hv-limits.rst`, `docs/power/poe/hv-options.rst`, `docs/power/poe/pd-controller.rst`
- **Issue:** The limits table gives N-well to substrate as 10 V minimum, yet the page says no documented limit rules stacking out. That value does rule out any stack whose wells are plain N-wells at up to 57 V. A low-side isolation switch also leaves the rest of the die up to 57 V above the substrate until it closes.
- **Suggestion:** Say which isolation structures remain (deep N-well, drift regions, devices on field oxide) and what each needs from the foundry. Compare low-side and high-side isolation switches.

### Start-up worst case and limits before software runs

- **Where:** `docs/power/poe/startup.rst`, `docs/power/poe/powered-device.rst`
- **Issue:** The energy example uses the long first class event. A source that classifies with a 6 ms event, or not at all, gives almost no energy before power-on. The page does not say that the board must stay within class 3 power until software reads the assigned class, or how accurate the sequencer's time base must be. The offset current uses 12 µA where the powered device's own limit may be 10 µA *(from memory)*.
- **Suggestion:** Add the zero-energy case, the boot power ceiling and the hardware that holds the outputs off, and the time base accuracy (about ±7 % to tell a long first event). Check the offset current in Table 145-21.

### Voltages above 57 V and the energy comparisons

- **Where:** `docs/power/poe/hv-limits.rst`, `docs/power/usb-pd/cc-protection.rst`
- **Issue:** The surge estimate assumes a clamp holding 90 V at 35 A, far above the rated pulse current of the example part. Cable ringing at turn-on is not treated. Both pages compare a clamp's energy with the 0.2 mJ of a human-body-model pulse, but almost all of that energy burns in the model's 1.5 kΩ resistor, so the true ratio is far larger.
- **Suggestion:** State the differential surge current assumed and the clamp voltage at that current. Add the ringing case. Compare with the energy the clamp itself absorbs in the human-body model (a few µJ).

### Which Power over Ethernet parts are external in the first version

- **Where:** `docs/power/index.rst` (board configurations), `docs/power/poe/hv-options.rst`
- **Issue:** The board configurations table fixes only the converter gate drivers and power transistors as external. The bridge, powered-device controller, port switch and surge suppressor are left open for both configurations.
- **Suggestion:** Add rows for these parts to the board configurations table, or say plainly that they are open for the first version.

## Converters

### Isolated topologies and the arrangement comparison

- **Where:** `docs/power/converters/buck-boost.rst`, `docs/power/converters/arrangement.rst`
- **Issue:** The pages now say one converter in each Ethernet-to-USB path must be isolated, but the flyback is the only isolated topology described, and the comparison tables still count switches and efficiency without a barrier.
- **Suggestion:** Add the alternatives (active-clamp forward or flyback, a fixed-ratio isolated bus converter followed by non-isolated regulation, a dual active bridge, a commercial controller supervised by evampire). Redo the tables with a barrier column and an isolated-stage efficiency row.

### Hardware over-voltage stop for each converter

- **Where:** `docs/power/converters/first-version.rst` (fault table)
- **Issue:** With peak-current control in hardware and the voltage loop in software, a stalled processor leaves the stage as a current source. Unplugging the load then raises the output at tens of volts per millisecond.
- **Suggestion:** Add an output over-voltage comparator per converter that stops switching, a row for it and for loss of loop updates in the fault table, and the reaction time as C × ΔV / I.

### Loop latency and the right-half-plane zero

- **Where:** `docs/power/converters/first-version.rst` (loop needs table), `docs/power/converters/control.rst`
- **Issue:** The table pairs a 25 kHz crossover with a 4 µs latency, which by one estimate costs about 54° of phase. The right-half-plane zero is worked at one point (20 V, 30 W); at 5 V input it is several times lower.
- **Suggestion:** Give the latency as a phase budget and the zero over the input range. Needs a loop model or simulation to confirm.

### Minimum on-time and where a buck's current is sensed

- **Where:** `docs/power/converters/buck-boost.rst`, `docs/power/converters/first-version.rst`
- **Issue:** 57 V to 5 V has a duty cycle of 0.088, an on-time of 146 ns at 600 kHz, close to what a peak-current comparator with blanking can control. Low-side sensing in the ground return does not carry a buck's on-time current, so it cannot end the on-time at the peak.
- **Suggestion:** Add minimum on-time against frequency for each arrangement, and valley or emulated current-mode control as alternatives. State where the current is sensed for each converter.

### Bootstrap supply for switches that stay on

- **Where:** `docs/power/converters/control.rst`, `docs/power/converters/buck-boost.rst`
- **Issue:** A bootstrap capacitor is sized for one gate charge, but the four-switch stage, the pass-through switch and the USB sink switch hold a high-side switch on indefinitely.
- **Suggestion:** State the need for a charge pump, refresh pulses or p-channel switches for static paths, and carry it into the integration page.

### Port B's ripple and inrush from the high-voltage converter

- **Where:** `docs/power/converters/boost.rst`, `docs/power/poe/pse-sequencing.rst`
- **Issue:** The Power over Ethernet pages hand the ripple limit to the converter, but the boost page has no output-ripple equation. The converter must also supply the inrush current (see the budget item).
- **Suggestion:** Add the boost output-ripple equation with a worked example, and a row for inrush power against input power.

### USB source behaviour the converter must provide

- **Where:** `docs/power/converters/first-version.rst`, `docs/power/usb-pd/monitoring.rst`, `docs/power/usb-pd/source-sink.rst`
- **Issue:** A programmable supply must regulate current in current limit, which is a second control loop, not a trip. Voltage changes have a slew limit, and a downward change returns the output capacitor's energy to the bus. The converter pages cover none of these.
- **Suggestion:** Add the current-limit loop and its accuracy, a slewed reference, and a bleeder or the condition under which the bus absorbs the energy.

### Parts and losses left out of the arrangement comparison

- **Where:** `docs/power/converters/arrangement.rst`, `docs/power/converters/control.rst`
- **Issue:** The static switches and the board's own supply converter are not counted, and they differ per arrangement. The 90 % to 97 % range comes from 12 V to 20 V examples; at 57 V to 5 V the page's own loss formulas plus reverse recovery give about 88 % by one estimate.
- **Suggestion:** Count every switch and the board supply. Make the efficiency range depend on the conversion ratio, and add reverse-recovery and output-capacitance losses.

### Back-feed, two inputs present, and reversing a shared converter

- **Where:** `docs/power/converters/arrangement.rst`, `docs/power/index.rst`, `docs/power/usb-pd/two-ports.rst`, `docs/power/poe/dual-role.rst`
- **Issue:** No page says what happens when Power over Ethernet and a USB charger are both connected, or when two USB chargers are. In the shared-node arrangements the 54 V node could reach port A's cable through an active bridge. Reversing a shared converter is not described.
- **Suggestion:** Add an input-priority rule, the blocking each input path needs, and the steps and hold-up energy of a reversal.

### Integration: substrate injection and the area of a stacked switch

- **Where:** `docs/power/converters/integration.rst`
- **Issue:** An integrated low-side switch node goes below the substrate in every dead time and injects carriers, next to the transceiver's converters in the full design. The page gives the gate width of a stacked 100 mΩ switch but not its area (about 3 to 7 mm² by its own figures).
- **Suggestion:** Add substrate injection and noise coupling to the process needs and open questions, and give the area per switch.

### Start-up supply is sized from a commercial controller's current

- **Where:** `docs/power/converters/first-version.rst` (start-up)
- **Issue:** The hold-up example uses 0.58 mA from a reference part. evampire's own current before start is unknown and probably much larger; a linear path from 57 V dissipates (57 V − V_dd) × I.
- **Suggestion:** Give the start-up source and its dissipation as functions of the chip's pre-start current, and say what the PWM pads do before the supply is valid.

### Input range and the 48 V bus case

- **Where:** `docs/power/converters/buck.rst`, `docs/power/converters/arrangement.rst`, `docs/power/poe/pd-controller.rst`
- **Issue:** The converter pages use 37 V to 57 V at the input converter; the powered-device page gives 30 V to 57 V after the switch. With a 48 V bus nothing in the three-converter arrangement produces 50 V to 57 V for Type 2 to 4 ports.
- **Suggestion:** Use the converter's own input range after the bridge and switch, and add the 48 V bus case to the open questions or the mode table.

## USB Power Delivery and USB serial

### Instruction rate and timing budget of polled receive

- **Where:** `docs/power/usb-pd/software.rst`, `docs/power/usb-pd/calc.py`
- **Issue:** The 15 M instructions per second is an average. The work at one edge must finish before the next, which gives a peak of about 27 to 40 M by one estimate. The 333 ns budget assumes the bit rate has already been measured; with a fixed threshold the window is about ±118 ns.
- **Suggestion:** State the peak requirement, give both the fixed and adaptive threshold cases, and add the cost of measuring the bit rate on the preamble. Recheck the arithmetic before changing the page.

### One processor serving Power Delivery, USB and a second port

- **Where:** `docs/power/usb-pd/software.rst`, `docs/usb-serial/software-cost.rst`
- **Issue:** The Power Delivery page keeps "interrupts off for 2.3 ms" as an option, while a USB reply is due within about 540 ns. No page bounds how late the receive loop may be entered, and the helper list omits Hard Reset detection, bus-idle detection and the fast role swap path.
- **Suggestion:** State that software Power Delivery with interrupts off cannot coexist with software USB handshakes, complete the helper list, and estimate the size of a hardware receive and GoodCRC block.

### Processor demands are never added up

- **Where:** `docs/requirements.rst` (processor), all topic pages
- **Issue:** Each page states its own need: about 1 ms latency for Power over Ethernet, about 4 µs for a converter loop, tens of millions of instructions per second for Power Delivery receive, USB replies, transceiver adaptation. No page sums them for one core.
- **Suggestion:** Add a table of every demand on the processor (rate, latency, longest non-interruptible section) so that a core and the hardware helpers can be chosen against it.

### Two-port power path and start-up

- **Where:** `docs/power/usb-pd/two-ports.rst`, `docs/power/usb-pd/analogue.rst`
- **Issue:** Not covered: both ports on chargers from a dead start, keeping an unattached receptacle at 0 V while the other port sinks, two different contract voltages, and a start-up path that conducts with no control yet blocks 20 V later.
- **Suggestion:** Add a section with a default-on start-up path and a controlled back-to-back path per port, and say which port wins.

### On-chip crowbar: current path

- **Where:** `docs/power/usb-pd/cc-protection.rst`
- **Issue:** The crowbar's steady current of 3 A to 5 A flows through a CC contact the page rates at 0.5 A, then one pad and bond wire. The peak from the bulk capacitance is tens of amperes.
- **Suggestion:** Add the contact, pad and bond-wire current limits with arithmetic. They may rule this option out.

### USB suspend current

- **Where:** `docs/usb-serial/signalling.rst`, `docs/usb-serial/usb-pd-roles.rst`, `docs/power/usb-pd/start-up.rst`
- **Issue:** A suspended USB 2.0 device may draw only 2.5 mA on average *(from memory)*. A board powered from a computer's port cannot run on that when the computer suspends the bus.
- **Suggestion:** State the limit and its consequences, and check which Type-C current levels and Power Delivery contracts lift it.

### Comparators per CC pin and the missing debounce

- **Where:** `docs/power/usb-pd/analogue.rst`, `docs/power/usb-pd/attach.rst`
- **Issue:** One comparator is asked to slice BMC, detect detach, read the Rp level and detect fast role swap, at different thresholds, some of them continuously. The tPDDebounce time (10 to 20 ms, *from memory*) is on no page.
- **Suggestion:** Give the comparator count per pin as a function of the features kept, and add the debounce.

### Values to check against the specifications

- **Where:** `docs/power/usb-pd/cc-signalling.rst`, `docs/power/usb-pd/negotiation.rst`, `docs/power/usb-pd/cables.rst`, `docs/power/usb-pd/masks.py`
- **Issue:** A reviewer's recollection differs from the pages on: the 1.2 V row of the slowest-edge table (344 ns expected for a falling edge at any swing), the receive mask for a port that is neither sourcing nor sinking, and the upper limits of tSenderResponse and tVDMSenderResponse. The reviewer knew older releases than the pages cite.
- **Suggestion:** Check each against the cited release. Nothing here should change without the specification open.

### Smaller USB items

- **Where:** `docs/power/usb-pd/power-translation.rst`, `docs/usb-serial/timing.rst`, `docs/power/usb-pd/calc.py`
- **Issue:** The USB to Ethernet translation uses nominal contract power, not the lowest voltage at the sink after cable drop (54.8 W, not 60 W, for 20 V at 3 A). "At least 286 MHz" for USB edge placement is sufficient but not necessary; the calculator shows 250 MHz inside the limit with 0.17 ns of margin. The calculator does not compute the class tables or the dead-battery example.
- **Suggestion:** Give input power as a range, qualify the 286 MHz claim, and extend the calculator to every number the pages quote.

## Magnetics and isolation

### Capacitor and inductor minima cannot be used together

- **Where:** `docs/ethernet/magnetics/front-ends.rst`, `docs/ethernet/magnetics/without-transformer.rst`
- **Issue:** The droop row is marked as met with 16 nF per wire and 80 µH across the pair, each a minimum taken alone. A reviewer's simulation of the two together leaves 47 % at 500 ns against the 73 % needed; 33 nF needs about 182 µH.
- **Suggestion:** Reproduce the second-order step response in a script, replace the two minima with a joint constraint, and mark the row conditional.

### Two separate inductors against the 100 µH limit

- **Where:** `docs/ethernet/magnetics/without-transformer.rst`
- **Issue:** The page says two separate inductors conflict with the 100 µH limit on the power path. For 80 µH across the pair, each is 40 µH; in parallel within a pair and with two pairs in the loop that is 40 µH, under the limit.
- **Suggestion:** Redo the arithmetic and state the range of inductance that satisfies both limits. Add the DC current at which the inductance must hold.

### Impedance balance with coupling capacitors

- **Where:** `docs/ethernet/magnetics/front-ends.rst`, `docs/ethernet/magnetics/functions.rst`
- **Issue:** Balance is left open. A 10 % mismatch between two 33 nF capacitors with about 50 Ω to ground on the chip side gives roughly −40 dB of conversion at 1 MHz, against a limit of 66.6 dB.
- **Suggestion:** Work the estimate into the page. It probably makes a common-mode choke or a high-impedance common-mode node mandatory.

### Common-mode termination without a transformer

- **Where:** `docs/ethernet/magnetics/without-transformer.rst`, `docs/ethernet/magnetics/front-ends.rst`
- **Issue:** A 75 Ω common-mode termination from two resistors per pair puts 300 Ω across the pair and uses the whole return-loss budget. The page says a pair has no centre tap without a transformer, yet the passive front end has a centre-tapped inductor on every pair.
- **Suggestion:** Correct the centre-tap statement for the passive front end and give the return loss of each termination option.

### What passes through a capacitor barrier

- **Where:** `docs/ethernet/magnetics/without-transformer.rst`, `docs/ethernet/magnetics/front-ends.rst`, `docs/ethernet/magnetics/events.rst`
- **Issue:** The barrier is checked only against the isolation test voltage. The charge it passes (about 74 µC per wire at 2250 V with 33 nF) is hundreds of times an electrostatic discharge, a 4 kV surge charges the capacitor past its 2 kV rating, and the AC test drives about 31 mA into the chip side for 60 s.
- **Suggestion:** Add a table of charge and current per event and per capacitor value, and the surge level at which the capacitor survives.

### Touch current through the barrier at mains frequency

- **Where:** `docs/ethernet/magnetics/isolation.rst`, `docs/ethernet/magnetics/functions.rst`
- **Issue:** Eight 33 nF capacitors are about 12 kΩ at 50 Hz and would pass about 21 mA with 250 V across the barrier. IEC 62368-1 touch-current limits are far lower *(from memory)*.
- **Suggestion:** Add touch current to the safety open question. It bounds the total barrier capacitance well below the droop minimum.

### Common-mode choke carries the Power over Ethernet current

- **Where:** `docs/ethernet/magnetics/arch-capacitor.dot`, `docs/ethernet/magnetics/front-ends.rst`, `docs/ethernet/magnetics/first-version.rst`
- **Issue:** The choke is drawn between the socket and the power tap, where the supply current flows the same way in both wires of a pair and would saturate a signal choke. Converter noise also reaches the cable through the taps.
- **Suggestion:** Move the choke to the chip side of the tap or wind it across a pair set, and add a filter for the power path.

### Is isolation required, and which parts bridge the barrier

- **Where:** `docs/requirements.rst` (cable), `docs/ethernet/magnetics/isolation.rst`, `docs/ethernet/magnetics/first-version.rst`
- **Issue:** The requirements say the board still provides isolation; the magnetics page has a section on partial isolation and asks whether the test must be passed. The first-version page says the resistor and capacitor between signal ground and chassis bridge the barrier, which looks wrong: both grounds are on the equipment side.
- **Suggestion:** Make the requirement and the open question agree. Check which parts bridge the barrier against the standard's definition.

### Smaller magnetics items

- **Where:** `docs/ethernet/magnetics/gigabit-risk.rst`, `docs/ethernet/magnetics/isolation.rst`
- **Issue:** Baseline wander is compared as an rms value against a peak criterion. The second-die route omits a serial link with a DC-balanced code, which needs only small high-voltage capacitors. The on-die barrier ignores clearance between pads and package leads. The insertion-loss formula may be 0.4/f, not 0.4/√f *(from memory)*.
- **Suggestion:** Convert the wander to a peak at the target error rate, add the serial-link alternative and the package clearance, and check the formula in Clause 40.

## Integrated transceiver (full design)

### Power and area of the signal processing

- **Where:** `docs/ethernet/phy-electrical/integration/cells.rst`, `docs/ethernet/phy-electrical/integration/area-power.rst`
- **Issue:** The energy per gate assumes three NAND input loads and no wire capacitance. Scaled from the page's own 0.25 µm reference chip, a reviewer gets 4 to 8 W per port against the page's 0.48 to 1.5 W. The 1.8 V row keeps the same area although that library needs parallel copies to meet 125 MHz.
- **Suggestion:** Calibrate the model against a reference chip, add wire and clock capacitance, give area as a function of parallelism, and present totals as lower bounds. A trial synthesis of one echo canceller would settle most of it.

### The 8 ns decision loop

- **Where:** `docs/ethernet/phy-electrical/integration/signal-processing.rst`, `docs/ethernet/phy-electrical/integration/decision-loop.dot`
- **Issue:** The page says look-ahead leaves the loop only a selection. The decoder's add, compare and select is itself a one-symbol recursion and stays in the loop *(from memory of the cited paper)*.
- **Suggestion:** Check the cited papers, state the smallest loop and its depth, and add a slicer-only receiver for short reach as an alternative.

### Converter resolution and examples

- **Where:** `docs/ethernet/phy-electrical/integration/receiver.rst`
- **Issue:** The bits-against-reach formula has no floor: at short reach the signal fills the range and no more bits are saved. The examples that reach 7 effective bits use 1.8 V thin-oxide devices that gf180mcu lacks.
- **Suggestion:** Add a floor of about 5 to 6 effective bits derived from the slicer's needs, and restrict the power range to 3.3 V-class examples.

### Transmit amplitude, reference and linearity

- **Where:** `docs/ethernet/phy-electrical/integration/transmitter.rst`
- **Issue:** An untrimmed ±20 % source resistor moves the line amplitude by +11 % and −9 %, outside the amplitude window, and no page has a bias or reference block. Linearity and headroom are worked without the far end's signal or the test fixture's disturber on the pins.
- **Suggestion:** Add an amplitude error budget and a reference block, and redo swing and linearity with the superimposed signals.
