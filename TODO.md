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
