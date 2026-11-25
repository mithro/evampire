# /// script
# requires-python = ">=3.10"
# ///
"""Write the graphs of BMC receiver levels and software timing for the USB
Power Delivery pages. Run with:

    uv run docs/power/usb-pd/graphs_signal.py

Writes:

rx-thresholds.svg
    The inner receive mask levels for each power role, the band they share,
    and a reference receiver's switching levels (cc-signalling.rst).
tx-edge.svg
    A counter wait loop placing a transmitted edge inside the +-50 ns
    window (software.rst).
busy-time.svg
    The time a polling processor is busy with one received message and
    its GoodCRC (software.rst).

Every number comes from the page that shows the figure.

SPDX-License-Identifier: Apache-2.0
"""

from svgfig import (CABLE, FILL, GREY, INK, SNK, SNK_INK, SRC, SRC_INK,
                    Plot, line, rect, svg, text, write)


def rx_thresholds():
    p = Plot(70, 20, 560, 300, (0, 3), (0, 1.0))
    body = [rect(p.left, p.y(0.6425), p.w, p.y(0.4825) - p.y(0.6425),
                 FILL, "none")]
    body.append(p.frame())
    body += p.yticks([0, 0.2325, 0.4825, 0.6425, 0.8925, 1.0],
                     "voltage (V)", fmt="{:g}", grid=False)
    eyes = [("sinking power", 0.2325, 0.4375, 0.6425, SNK),
            ("neither", 0.2325, 0.5625, 0.8925, CABLE),
            ("sourcing power", 0.4825, 0.6875, 0.8925, SRC)]
    for k, (name, lo, mid, hi, fill) in enumerate(eyes):
        xc = p.x(k + 0.5)
        body.append(rect(xc - 30, p.y(hi), 60, p.y(lo) - p.y(hi), fill))
        body.append(line(xc - 30, p.y(mid), xc + 30, p.y(mid), INK, 0.8,
                         "3,3"))
        body.append(text(xc, p.bottom + 18, name, 12, "middle"))
    body.append(text(p.left + p.w / 2, p.bottom + 36, "port's power role",
                     13, "middle"))
    for k, rise, fall, col, side in ((0, 0.525, 0.250, SNK_INK, 1),
                                     (2, 0.875, 0.600, SRC_INK, -1)):
        xc = p.x(k + 0.5) + side * 45
        body.append(line(xc, p.y(fall), xc, p.y(rise), col, 1.2,
                         arrow="both"))
        anc = "start" if side > 0 else "end"
        body.append(text(xc + side * 6, p.y(rise) + 4,
                         f"rising {rise * 1000:g} mV", 11, anc, fill=col))
        body.append(text(xc + side * 6, p.y(fall) + 4,
                         f"falling {fall * 1000:g} mV", 11, anc, fill=col))
    body.append(text(p.left - 60, p.bottom + 58, "Bars: the inner receive "
                     "mask (the eye). Grey band: 0.4825 to 0.6425 V, inside "
                     "every eye.", 12, fill=GREY))
    body.append(text(p.left - 60, p.bottom + 76, "Arrows: TPS65987D "
                     "switching levels, typical, a reference example.", 12,
                     fill=GREY))
    return svg(680, int(p.bottom + 88), body, "BMC receiver levels")


def tx_edge():
    p = Plot(60, 30, 590, 150, (-150, 150), (0, 1.25))
    body = [rect(p.x(-50), p.top, p.x(50) - p.x(-50), p.h, SNK, "none")]
    body.append(p.frame())
    body.append(text(p.x(0), p.top - 8, "window: ± 50 ns (± 0.015 UI)", 11,
                     "middle", fill=SNK_INK))
    for t in range(-150, 151, 100):
        body.append(line(p.x(t), p.bottom, p.x(t), p.bottom - 12, INK, 1.2))
    body.append(text(p.x(-150) + 4, p.bottom - 16, "wait-loop iterations, "
                     "100 ns apart", 10))
    body.append(line(p.x(-50), p.top, p.x(-50), p.bottom, INK, 1.4, "5,3"))
    body.append(text(p.x(-50) - 4, p.y(0.95), "target time", 11, "end"))
    body.append(text(p.x(-50) - 4, p.y(0.95) + 14, "from the counter", 11,
                     "end"))
    body.append(line(p.x(0), p.top, p.x(0), p.bottom, INK, 0.8, "2,3"))
    body.append(text(p.x(0) + 4, p.y(0.4), "ideal edge", 11))
    body.append(line(p.x(-50), p.y(0.75), p.x(50), p.y(0.75), SRC_INK, 2.0,
                     arrow="both"))
    body.append(text(p.x(54), p.y(0.75) - 4, "the edge lands up", 11,
                     fill=SRC_INK))
    body.append(text(p.x(54), p.y(0.75) + 12, "to one iteration late", 11,
                     fill=SRC_INK))
    body += p.xticks([-150, -100, -50, 0, 50, 100, 150],
                     "time from the ideal edge (ns)", grid=False)
    return svg(680, int(p.bottom + 48), body, "Transmit edge placement")


def busy_time():
    p = Plot(30, 60, 620, 50, (0, 2400), (0, 1))
    segs = [(0, 1589, CABLE, "received message, 1589 µs"),
            (1589, 1784, "#ffffff", ""),
            (1784, 2336, SRC, "GoodCRC, 552 µs")]
    body = []
    for a, b, fill, lab in segs:
        body.append(rect(p.x(a), p.top, p.x(b) - p.x(a), p.h, fill))
        if lab:
            body.append(text((p.x(a) + p.x(b)) / 2, p.top + 30, lab, 12,
                             "middle"))
    body.append(text(p.x(1686), p.top - 28, "gap", 11, "middle"))
    body.append(text(p.x(1686), p.top - 14, "≤ 195 µs", 11, "middle"))
    body.append(line(p.x(0), p.top - 40, p.x(2336), p.top - 40,
                     arrow="both"))
    body.append(text(p.x(800), p.top - 46, "interrupts off: 2336 µs", 12,
                     "middle"))
    body.append(text(p.x(0), p.bottom + 24, "Ethernet traffic arriving "
                     "meanwhile at 1 Mbit/s: about 292 bytes", 12))
    body.append(text(p.x(0), p.bottom + 44, "Decoding a stored message only "
                     "in the gap needs 69 × 10⁶ instructions/s instead.", 12,
                     fill=GREY))
    body.append(text(p.right, p.bottom + 64, "worst case: seven data "
                     "objects at 270 kbit/s", 11, "end", fill=GREY))
    return svg(680, int(p.bottom + 76), body, "Processor busy time")


if __name__ == "__main__":
    write("rx-thresholds.svg", rx_thresholds())
    write("tx-edge.svg", tx_edge())
    write("busy-time.svg", busy_time())
