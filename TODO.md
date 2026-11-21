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
