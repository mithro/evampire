# /// script
# requires-python = ">=3.10"
# ///
"""Write the graphs of VBUS voltage and current for the USB Power Delivery
pages. Run with:

    uv run docs/power/usb-pd/graphs_power.py

Writes:

vbus-transition.svg
    VBUS and the sink current during a change from 5 V to 9 V
    (source-sink.rst; PD Tables 4.7 and 4.8, PD Table 7.10).
current-limit.svg
    A source's current-limit setting and the sink current when a contract
    is lowered and raised (monitoring.rst).
pps-limit.svg
    VBUS against current for a PPS source in current limit
    (monitoring.rst; PD Table 4.7).

Every limit comes from the page that shows the figure. Event times that
the specification leaves free inside a limit are example values, and the
figures say so.

SPDX-License-Identifier: Apache-2.0
"""

from svgfig import (FILL, GREY, INK, SNK, SNK_INK, SRC, SRC_INK, Plot, line,
                    polyline, rect, svg, text, write)


def band(p, x0, x1, lo, hi, fill, stroke="none", dash=None):
    return rect(p.x(x0), p.y(hi), p.x(x1) - p.x(x0), p.y(lo) - p.y(hi), fill,
                stroke, 0.8, dash)


def vline(p, x, label, y_text, anchor="start", dash="4,3"):
    out = [line(p.x(x), p.top, p.x(x), p.bottom, INK, 1.0, dash)]
    dx = 4 if anchor == "start" else -4
    out.append(text(p.x(x) + dx, y_text, label, 11, anchor))
    return out


def vbus_transition():
    t_step, t_psrdy = 40, 140        # example event times (ms)
    pv = Plot(60, 40, 600, 220, (-100, 600), (0, 11))
    pi = Plot(60, 320, 600, 130, (-100, 600), (0, 2.5))
    body = []
    # Sink gives up: tPSTransition 450 to 550 ms after Accept.
    body.append(band(pv, 450, 550, 0, 11, "#f2f2f2"))
    body.append(band(pi, 450, 550, 0, 2.5, "#f2f2f2"))
    # VBUS bands: +-5 % (vSrcNew) and a further 0.5 V (vSrcValid).
    for x0, x1, v in ((-100, t_step, 5.0), (t_step, 600, 9.0)):
        body.append(band(pv, x0, x1, v * 0.95 - 0.5, v * 1.05 + 0.5, FILL))
        body.append(band(pv, x0, x1, v * 0.95, v * 1.05, SRC))
    body.append(pv.frame())
    body += pv.yticks([0, 5, 9], "VBUS (V)")
    vb = [(-100, 5), (t_step, 5), (t_step + 0.5, 9), (600, 9)]
    body.append(polyline(pv.pts(vb), SRC_INK, 2.2))
    body += vline(pv, 0, "Accept", pv.top - 6, "middle", dash=None)
    body += vline(pv, 25, "", 0)
    body += vline(pv, t_psrdy, "PS_RDY", pv.top - 6, "middle", dash=None)
    body += vline(pv, 325, "", 0)
    body.append(text(pv.x(25) + 4, pv.y(2.2), "tSrcTransition ≥ 25 ms:",
                     11))
    body.append(text(pv.x(25) + 4, pv.y(2.2) + 14,
                     "no change before this", 11))
    body.append(text(pv.x(325) + 4, pv.y(2.2), "tSrcTransReq:", 11))
    body.append(text(pv.x(325) + 4, pv.y(2.2) + 14, "PS_RDY by 325 ms", 11))
    body.append(text(pv.x(500), pv.y(2.2), "tPSTransition", 11, "middle"))
    body.append(text(pv.x(500), pv.y(2.2) + 14, "450–550 ms:", 11,
                     "middle"))
    body.append(text(pv.x(500), pv.y(2.2) + 28, "sink sends Hard Reset", 11,
                     "middle"))
    body.append(text(pv.x(t_step) + 6, pv.y(7.0), "≤ 30 mV/µs", 11))
    body.append(text(pv.x(160), pv.y(10.4),
                     "9 V ± 5 %, and a further 0.5 V while settling", 11))
    # Sink current.
    body.append(pi.frame())
    body += pi.yticks([0, 0.5], "sink current (A)")
    body.append(line(pi.left, pi.y(0.5), pi.right, pi.y(0.5), SNK_INK, 1.0,
                     "6,3"))
    cur = [(-100, 1.5), (10, 1.5), (12, 0.4), (t_psrdy + 5, 0.4),
           (t_psrdy + 8, 2.0), (600, 2.0)]
    body.append(polyline(pi.pts(cur), SNK_INK, 2.2))
    body += vline(pi, 0, "", 0, dash=None)
    body += vline(pi, 15, "", 0)
    body += vline(pi, t_psrdy, "", 0, dash=None)
    body.append(text(pi.x(-96), pi.y(1.5) - 6, "old contract", 11))
    body.append(text(pi.x(20), pi.y(0.5) - 20,
                     "iSnkStdby ≤ 0.5 A, recommended within", 11))
    body.append(text(pi.x(20), pi.y(0.5) - 6, "tSnkStdby, 15 ms", 11))
    body.append(text(pi.x(t_psrdy) + 14, pi.y(2.0) - 6, "new contract", 11))
    body += pi.xticks([0, 100, 200, 300, 400, 500, 600],
                      "time after Accept (ms)", grid=False)
    # Legend.
    ly = pi.bottom + 64
    body.append(rect(pi.left, ly - 10, 22, 12, SRC))
    body.append(text(pi.left + 30, ly, "± 5 % of the offered voltage", 12))
    body.append(rect(pi.left + 250, ly - 10, 22, 12, FILL))
    body.append(text(pi.left + 280, ly, "further 0.5 V while settling", 12))
    body.append(text(pi.left, ly + 20, "Event times are examples; currents "
                     "other than 0.5 A are schematic.", 12, fill=GREY))
    return svg(680, int(ly + 32), body, "VBUS during a change to 9 V")


def current_limit():
    """Sink current and the source's limit over a fall and a rise."""
    p = Plot(60, 30, 600, 250, (-50, 400), (0, 4.0))
    body = []
    i_set = {3.0: 3.0 / 0.9, 1.5: 1.5 / 0.9}
    # Limit setting with its +-10 % tolerance band, piecewise in time.
    segs = [(-50, 30, 3.0), (30, 230, 1.5), (230, 400, 3.0)]
    for x0, x1, ic in segs:
        s = i_set[ic]
        body.append(band(p, x0, x1, s * 0.9, s * 1.1, FILL))
    body.append(p.frame())
    body += p.yticks([0, 1.5, 3.0], "current (A)", fmt="{:.1f}")
    lim = []
    for x0, x1, ic in segs:
        lim += [(x0, i_set[ic]), (x1, i_set[ic])]
    body.append(polyline(p.pts(lim), SRC_INK, 2.0, "6,3"))
    cur = [(-50, 3.0), (8, 3.0), (10, 1.5), (268, 1.5), (270, 3.0),
           (400, 3.0)]
    body.append(polyline(p.pts(cur), SNK_INK, 2.2))
    for x, lab in ((0, "Accept"), (60, "PS_RDY"), (200, "Accept"),
                   (255, "PS_RDY")):
        body += vline(p, x, lab, p.top - 6, "middle", dash=None)
    body += vline(p, 25, "", 0)
    body.append(text(p.x(-45), p.y(3.67) - 6, "3.3 A", 11))
    body.append(text(p.x(35), p.y(1.83) - 6, "I_set = 1.7 A, after "
                     "tSrcTransition (25 ms)", 11))
    body.append(text(p.x(262), p.y(3.67) - 6,
                     "I_set = 3.3 A, raised before PS_RDY", 11))
    body.append(text(p.x(65), p.y(0.8), "contract lowered", 11))
    body.append(text(p.x(65), p.y(0.8) + 14, "from 3 A to 1.5 A", 11))
    body.append(text(p.x(260), p.y(0.8), "contract raised", 11))
    body.append(text(p.x(260), p.y(0.8) + 14, "back to 3 A", 11))
    body += p.xticks([0, 100, 200, 300, 400], "time (ms)", grid=False)
    ly = p.bottom + 64
    body.append(line(p.left, ly - 4, p.left + 30, ly - 4, SNK_INK, 2.2))
    body.append(text(p.left + 38, ly, "sink current", 12))
    body.append(line(p.left + 160, ly - 4, p.left + 190, ly - 4, SRC_INK,
                     2.0, "6,3"))
    body.append(text(p.left + 198, ly, "limit setting, I_contract / 0.9",
                     12))
    body.append(rect(p.left + 420, ly - 10, 22, 12, FILL))
    body.append(text(p.left + 450, ly, "± 10 % tolerance", 12))
    body.append(text(p.left, ly + 20, "Event times are examples.", 12,
                     fill=GREY))
    return svg(680, int(ly + 32), body, "Source current limit")


def pps_limit():
    """VBUS against current for a PPS source in current limit."""
    p = Plot(60, 20, 600, 280, (0, 3.0), (0, 10))
    v_req, i_op = 9.0, 2.0
    body = [band(p, 0, 3.0, 5 * 0.85, 5 * 0.95, FILL),
            band(p, i_op - 0.15, i_op + 0.15, 5 * 0.85, v_req, SRC)]
    body.append(p.frame())
    body += p.yticks([0, 2, 4, 6, 8, 10], "VBUS (V)")
    curve = [(0, v_req), (i_op, v_req), (i_op, 5 * 0.9)]
    body.append(polyline(p.pts(curve), SRC_INK, 2.4))
    body.append(line(p.x(1.0), p.top, p.x(1.0), p.bottom, INK, 1.0, "4,3"))
    body.append(text(p.x(1.0) + 4, p.y(1.2), "iPpsCLMin = 1 A, lowest",
                     11))
    body.append(text(p.x(1.0) + 4, p.y(1.2) + 14, "setting; 50 mA steps",
                     11))
    body.append(text(p.x(0.1), p.y(v_req) - 8, "requested 9 V: voltage "
                     "held", 11))
    body.append(text(p.x(i_op + 0.2), p.y(7.5), "operating current 2 A:",
                     11))
    body.append(text(p.x(i_op + 0.2), p.y(7.5) + 14, "current held within",
                     11))
    body.append(text(p.x(i_op + 0.2), p.y(7.5) + 28, "± 150 mA (iPpsCLNew),",
                     11))
    body.append(text(p.x(i_op + 0.2), p.y(7.5) + 42, "voltage falls", 11))
    body.append(text(p.x(0.1), p.y(4.25) + 16, "vPpsShutdown, 85–95 % of "
                     "5 V: Hard Reset allowed below", 11))
    body += p.xticks([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0], "VBUS current (A)",
                     grid=False)
    body.append(text(p.left, p.bottom + 58, "Example: a 5 V to 11 V PPS "
                     "offer, with 9 V and 2 A requested.", 12, fill=GREY))
    return svg(680, int(p.bottom + 70), body, "PPS current limit")


if __name__ == "__main__":
    write("vbus-transition.svg", vbus_transition())
    write("current-limit.svg", current_limit())
    write("pps-limit.svg", pps_limit())
