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
vbus-discharge.svg
    An example VBUS discharge against tSafe5V and tSafe0V (source-sink.rst).
ovp-ramp.svg
    VBUS rising through the over-voltage threshold of a 20 V contract
    (monitoring.rst).
vconn-inrush.svg
    VCONN charging a marked cable, then its load current (cables.rst).
class-steps.svg
    The highest Power over Ethernet class for the power left from a USB
    contract (power-translation.rst).

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
    t_step, t_psrdy = 40, 210        # example event times (ms)
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
    for k, s in enumerate(("tSrcTransition", "≥ 25 ms: no", "change before")):
        body.append(text(pv.x(25) + 4, pv.y(3.2) + 16 * k, s, 11))
    for k, s in enumerate(("tSrcTransReq:", "PS_RDY by", "325 ms")):
        body.append(text(pv.x(325) + 4, pv.y(3.2) + 16 * k, s, 11))
    for k, s in enumerate(("tPSTransition", "450–550 ms:", "sink sends", "Hard Reset")):
        body.append(text(pv.x(500), pv.y(7.0) + 16 * k, s, 11, "middle"))
    body.append(text(pv.x(t_step) + 6, pv.y(7.0), "≤ 30 mV/µs", 11))
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
    for k, s in enumerate(("iSnkStdby ≤ 0.5 A,", "recommended within",
                           "tSnkStdby, 15 ms")):
        body.append(text(pi.x(20), pi.y(0.5) - 38 + 16 * k, s, 11))
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
    p = Plot(60, 30, 590, 250, (-50, 400), (0, 4.6))
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
    body.append(text(p.right - 4, p.y(3.67) - 22, "I_set = 3.3 A,", 11,
                     "end"))
    body.append(text(p.right - 4, p.y(3.67) - 6, "raised before PS_RDY", 11,
                     "end"))
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


def vbus_discharge():
    """An example VBUS discharge from 20 V against the two limits
    (source-sink.rst). The exponential is an example shape."""
    import math
    p = Plot(60, 20, 590, 260, (0, 800), (0, 22))
    body = [band(p, 275, 800, 5.5, 22, FILL), band(p, 650, 800, 0.8, 22,
                                                   "#bfbfbf")]
    body.append(p.frame())
    body += p.yticks([0.8, 5.5, 10, 15, 20], "VBUS (V)")
    pts = [(t_ms, 20 * math.exp(-t_ms / 150)) for t_ms in range(0, 801, 5)]
    body.append(polyline(p.pts(pts), SRC_INK, 2.2))
    body.append(text(p.x(285), p.y(14), "must be at or below vSafe5V, "
                     "5.5 V, from 275 ms (tSafe5V)", 11))
    body.append(text(p.x(660), p.y(9), "at or below", 11))
    body.append(text(p.x(660), p.y(9) + 14, "vSafe0V, 0.8 V,", 11))
    body.append(text(p.x(660), p.y(9) + 28, "from 650 ms", 11))
    body.append(text(p.x(660), p.y(9) + 42, "(tSafe0V)", 11))
    body += p.xticks([0, 100, 200, 275, 400, 500, 650, 800],
                     "time after detach (ms)", grid=False)
    body.append(text(p.left, p.bottom + 58, "Grey: where VBUS must not be. "
                     "The curve is an example discharge.", 12, fill=GREY))
    return svg(680, int(p.bottom + 70), body, "VBUS discharge after detach")


def ovp_ramp():
    """VBUS rising at 30 mV/us through the over-voltage threshold of a 20 V
    contract (monitoring.rst)."""
    p = Plot(60, 20, 590, 240, (-60, 120), (19.5, 25))
    body = [p.frame()]
    body += p.yticks([20, 21, 21.5, 24], "VBUS (V)", fmt="{:g}")
    for v, lab, x, anc in ((21.0, "21.0 V: 20 V + 5 % (vSrcNew)", 116, "end"),
                           (21.5, "21.5 V: the threshold must lie above",
                            116, "end"),
                           (24.0, "24 V: what an SPR sink tolerates", -56,
                            "start")):
        body.append(line(p.left, p.y(v), p.right, p.y(v), GREY, 1.0, "6,3"))
        body.append(text(p.x(x), p.y(v) - 5, lab, 11, anc))
    ramp = [(-60, 20 + 0.03 * 0), (-50, 20.0), (0, 21.5), (83.3, 24.0),
            (100, 24.5)]
    body.append(polyline(p.pts(ramp[1:]), SRC_INK, 2.2))
    body.append(line(p.x(-60), p.y(20), p.x(-50), p.y(20), SRC_INK, 2.2))
    body.append(line(p.x(0), p.y(20.6), p.x(83.3), p.y(20.6), arrow="both"))
    body.append(text(p.x(41.7), p.y(20.6) - 6, "83 µs to switch off", 11,
                     "middle"))
    for x in (0, 83.3):
        body.append(line(p.x(x), p.top, p.x(x), p.bottom, INK, 0.8, "4,3"))
    body.append(text(p.x(30) - 8, p.y(22.6), "30 mV/µs", 11, "end"))
    body += p.xticks([-50, 0, 50, 100], "time from crossing the threshold "
                     "(µs)", grid=False)
    return svg(680, int(p.bottom + 48), body, "Over-voltage time budget")


def vconn_inrush():
    """VCONN charging the cable at constant current, then the cable load
    (cables.rst)."""
    pv = Plot(60, 20, 590, 150, (-0.5, 4), (0, 3.5))
    pi = Plot(60, 210, 590, 130, (-0.5, 4), (0, 40))
    body = [pv.frame(), pi.frame()]
    body += pv.yticks([0, 1, 2, 3], "VCONN (V)")
    body += pi.yticks([0, 6.7, 15, 25, 33], "current (mA)", fmt="{:g}")
    body.append(polyline(pv.pts([(-0.5, 0), (0, 0), (2, 3.0), (4, 3.0)]),
                         SRC_INK, 2.2))
    body.append(line(pi.left, pi.y(33), pi.right, pi.y(33), INK, 1.2,
                     "6,3"))
    body.append(polyline(pi.pts([(-0.5, 0), (0, 0), (0, 15), (2, 15),
                                 (2, 25), (3, 25), (3, 6.7), (4, 6.7)]),
                         SRC_INK, 2.2))
    for p in (pv, pi):
        body.append(line(p.x(2), p.top, p.x(2), p.bottom, INK, 0.8, "4,3"))
    body.append(text(pv.x(2) + 6, pv.y(3.0) + 18, "3.0 V, the lowest "
                     "valid VCONN,", 11))
    body.append(text(pv.x(2) + 6, pv.y(3.0) + 34, "by tVCONNON = 2 ms", 11))
    body.append(text(pi.x(0.1), pi.y(15) - 6, "15 mA charges 10 µF", 11))
    body.append(text(pi.x(-0.45), pi.y(33) - 5, "33 mA: the 100 mW the "
                     "source must be able to supply", 11))
    body.append(text(pi.x(2.05), pi.y(25) - 6, "cable: at most 75 mW", 11))
    body.append(text(pi.right - 4, pi.y(6.7) - 6, "then 20 mW", 11, "end"))
    body += pi.xticks([0, 1, 2, 3, 4], "time after VCONN is switched on (ms)",
                      grid=False)
    return svg(680, int(pi.bottom + 48), body, "VCONN switch current")


def class_steps():
    """Highest Power over Ethernet class against the power left for the
    Ethernet port (power-translation.rst; Table 145-11 values)."""
    p = Plot(60, 20, 590, 260, (0, 100), (0, 8.6))
    steps = [(4, 1), (6.7, 2), (14, 3), (30, 4), (45, 5), (60, 6), (75, 7),
             (90, 8)]
    pts, prev = [(0, 0)], 0
    for w, c in steps:
        pts += [(w, prev), (w, c)]
        prev = c
    pts.append((100, prev))
    body = [p.frame()]
    body += p.yticks(list(range(1, 9)), "highest class")
    body.append(text(p.left - 8, p.y(0) + 4, "none", 12, "end"))
    body.append(polyline(p.pts(pts), SNK_INK, 2.2))
    for w, c in steps:
        body.append(text(p.x(w) + 3, p.y(c) - 5, f"{w:g} W", 10))
    for w, c in ((21.2, 3), (50.9, 5), (86.9, 7)):
        body.append(f'<circle cx="{p.x(w):.1f}" cy="{p.y(c):.1f}" r="4" '
                    f'fill="{SRC_INK}"/>')
        body.append(text(p.x(w), p.y(c) + 18, f"{w:g} W", 11, "middle",
                         fill=SRC_INK))
    body += p.xticks([0, 20, 40, 60, 80, 100], "P_out, power left for the "
                     "Ethernet port (W)", grid=False)
    body.append(text(p.left, p.bottom + 58, "Dots: the worked examples for "
                     "9 V 3 A, 20 V 3 A and 20 V 5 A contracts.", 12,
                     fill=GREY))
    return svg(680, int(p.bottom + 70), body, "Class from a USB contract")


if __name__ == "__main__":
    write("vbus-transition.svg", vbus_transition())
    write("current-limit.svg", current_limit())
    write("pps-limit.svg", pps_limit())
    write("vbus-discharge.svg", vbus_discharge())
    write("ovp-ramp.svg", ovp_ramp())
    write("vconn-inrush.svg", vconn_inrush())
    write("class-steps.svg", class_steps())
