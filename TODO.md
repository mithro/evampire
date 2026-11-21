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
