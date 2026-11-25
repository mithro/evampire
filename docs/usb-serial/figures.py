# /// script
# requires-python = ">=3.10"
# ///
"""Write the USB serial packet-layout and analogue figures as SVG files:
signalling/packets.svg, analogue/driver-waveform.svg and
analogue/receiver-levels.svg. Run with:

    uv run docs/usb-serial/figures.py

SPDX-License-Identifier: Apache-2.0
"""

import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from svgplot import (Axes, Svg, BLUE, ORANGE, GREEN, RED, GREY, INK,  # noqa: E402
                     FILL_BLUE, FILL_ORANGE, FILL_GREEN, FILL_GREY)

HERE = pathlib.Path(__file__).parent


def packets():
    """Field layouts of the four packet kinds, in the order sent."""
    fills = {"SYNC": FILL_GREY, "PID": FILL_ORANGE, "EOP": FILL_GREY}
    rows = [
        ("Token: OUT, IN, SETUP", [("SYNC", 8), ("PID", 8), ("ADDR", 7),
                                   ("ENDP", 4), ("CRC5", 5), ("EOP", 3)]),
        ("Start of frame", [("SYNC", 8), ("PID", 8), ("frame number", 11),
                            ("CRC5", 5), ("EOP", 3)]),
        ("Data: DATA0, DATA1", [("SYNC", 8), ("PID", 8),
                                ("data: 0 to 1023 bytes", 24),
                                ("CRC16", 16), ("EOP", 3)]),
        ("Handshake: ACK, NAK, STALL", [("SYNC", 8), ("PID", 8),
                                        ("EOP", 3)]),
    ]
    s = Svg(600, 300)
    x0, scale = 20, 8.6
    y = 40
    s.text(x0, 16, "sent first →", size=12, anchor="start", fill=GREY)
    for name, fields in rows:
        s.text(x0, y, name, size=12, anchor="start", weight="bold")
        x = x0
        for label, bits in fields:
            w = max(bits, 5) * scale
            fill = fills.get(label, FILL_BLUE if "CRC" not in label
                             else FILL_GREEN)
            s.rect(x, y + 10, w, 30, fill=fill, stroke=INK)
            s.text(x + w / 2, y + 20, label, size=11)
            if label == "data: 0 to 1023 bytes":
                s.text(x + w / 2, y + 33, "0 to 8184 bits", size=10,
                       fill=GREY)
            elif label == "EOP":
                s.text(x + w / 2, y + 33, "3 bits", size=10, fill=GREY)
            else:
                s.text(x + w / 2, y + 33, f"{bits} bits", size=10,
                       fill=GREY)
            x += w
        y += 65
    s.save(HERE / "signalling" / "packets.svg")


def driver_waveform():
    """D+ and D- edges of a resistive driver into 50 pF, with the levels."""
    s = Svg(600, 360)
    a = Axes(s, (70, 30, 580, 290), (0, 60), (0, 3.6))
    s.rect(a.x0, a.Y(2.0), a.x1 - a.x0, a.Y(1.3) - a.Y(2.0), fill=FILL_GREEN,
           stroke="none")
    s.rect(a.x0, a.Y(3.6), a.x1 - a.x0, a.Y(2.8) - a.Y(3.6), fill=FILL_BLUE,
           stroke="none")
    s.rect(a.x0, a.Y(0.3), a.x1 - a.x0, a.Y(0) - a.Y(0.3), fill=FILL_BLUE,
           stroke="none")
    a.frame(xticks=range(0, 61, 10), yticks=[0, 0.3, 1.3, 2.0, 2.8, 3.3, 3.6],
            xlabel="time (ns)", ylabel="voltage (V)", yfmt=lambda v: f"{v:g}")
    s.text(a.x1 - 4, a.Y(3.2), "VOH: 2.8 V to 3.6 V", size=11, anchor="end",
           fill=BLUE)
    s.text(a.x1 - 4, a.Y(0.45), "VOL: at most 0.3 V", size=11, anchor="end",
           fill=BLUE)
    s.text(a.x1 - 4, a.Y(1.65), "crossover VCRS: 1.3 V to 2.0 V", size=11,
           anchor="end", fill=GREEN)
    v = 3.3
    t0 = 10.0
    for z, col, dash in ((28, ORANGE, None), (44, RED, "6 4")):
        tau = z * 50e-12 * 1e9            # ns
        up, dn = [], []
        for k in range(301):
            t = k * 0.2
            if t < t0:
                up.append((t, 0.0))
                dn.append((t, v))
            else:
                e = math.exp(-(t - t0) / tau)
                up.append((t, v * (1 - e)))
                dn.append((t, v * e))
        s.poly(a.P(up), stroke=col, dash=dash)
        s.poly(a.P(dn), stroke=col, dash=dash)
    s.text(a.X(t0 + 22), a.Y(2.55), "28 Ω: 3.08 ns, 10 % to 90 %", size=11,
           anchor="start", fill=ORANGE)
    s.text(a.X(t0 + 22), a.Y(2.3), "44 Ω: 4.83 ns", size=11, anchor="start",
           fill=RED)
    s.text(a.X(t0) - 4, a.Y(3.45), "D−", size=12, anchor="end")
    s.text(a.X(t0) - 4, a.Y(0.15), "D+", size=12, anchor="end")
    s.text(325, 345, "required: 4 ns to 20 ns, 10 % to 90 %, into 50 pF; "
           "3.3 V swing assumed", size=11, fill=GREY)
    s.save(HERE / "analogue" / "driver-waveform.svg")


def receiver_levels():
    """Input voltage ranges of the differential and single-ended
    receivers."""
    s = Svg(600, 300)
    a = Axes(s, (70, 30, 580, 250), (0, 4), (0, 3.6))
    a.frame(yticks=[0, 0.8, 2.0, 2.5, 3.6], ylabel="input voltage (V)",
            yfmt=lambda v: f"{v:g}", grid=False)
    cols = [(0.3, 1.6, "Differential receiver"),
            (2.2, 3.5, "Single-ended receivers")]
    # Differential: common-mode range with a 200 mV difference.
    xa, xb = a.X(0.3), a.X(1.6)
    s.rect(xa, a.Y(2.5), xb - xa, a.Y(0.8) - a.Y(2.5), fill=FILL_BLUE,
           stroke=BLUE)
    s.text((xa + xb) / 2, a.Y(2.85), "both inputs within\n0.8 V to 2.5 V (VCM)",
           size=11, fill=BLUE)
    xm = (xa + xb) / 2
    s.line(xm - 18, a.Y(1.75), xm + 18, a.Y(1.75), stroke=INK, width=1.6)
    s.line(xm - 18, a.Y(1.55), xm + 18, a.Y(1.55), stroke=INK, width=1.6)
    s.line(xm + 26, a.Y(1.75), xm + 26, a.Y(1.55), arrow="both", width=1)
    s.text(xm + 32, a.Y(1.65), "200 mV\n(VDI)", size=11, anchor="start")
    s.text(xm, a.Y(0.4), "resolves J or K", size=11, fill=GREY)
    # Single-ended: threshold band.
    xa, xb = a.X(2.2), a.X(3.5)
    s.rect(xa, a.Y(2.0), xb - xa, a.Y(0.8) - a.Y(2.0), fill=FILL_ORANGE,
           stroke=ORANGE)
    s.text((xa + xb) / 2, a.Y(1.4), "switching threshold\nbetween 0.8 V\n"
           "and 2.0 V", size=11, fill=ORANGE)
    s.text((xa + xb) / 2, a.Y(2.4), "above: high", size=11, fill=GREY)
    s.text((xa + xb) / 2, a.Y(0.4), "below: low; both low = SE0,\n"
           "after a 14 ns to 82 ns filter", size=11, fill=GREY)
    for x0, x1, name in cols:
        s.text((a.X(x0) + a.X(x1)) / 2, 272, name, size=12, weight="bold")
    s.save(HERE / "analogue" / "receiver-levels.svg")


if __name__ == "__main__":
    packets()
    driver_waveform()
    receiver_levels()
