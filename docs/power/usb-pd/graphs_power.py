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


if __name__ == "__main__":
    write("vbus-transition.svg", vbus_transition())
