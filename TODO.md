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
