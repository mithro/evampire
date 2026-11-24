# /// script
# requires-python = ">=3.10"
# ///
"""Write the graphs of voltages on the CC pins for the USB Power Delivery
pages. Run with:

    uv run docs/power/usb-pd/graphs_cc.py

Writes:

cc-thresholds.svg
    The CC voltage ranges and threshold windows at a sink (Type-C
    Tables 4-35 and 4-36) and at a source with a current-source Rp
    (Type-C Table 4-37), as quoted on resistor-advertisement.rst.
packet.svg
    The parts of a packet, a Hard Reset, and the order in which the
    nibbles and symbols are sent (packets.rst).

Every number comes from the page that shows the figure.

SPDX-License-Identifier: Apache-2.0
"""

from svgfig import (CABLE, FILL, GREY, INK, SNK, Plot, line, rect, svg,
                    text, write)


def bar(p, xc, w, lo, hi, fill, labels=True, size=10, side="right"):
    """A vertical range bar from lo to hi volts, with its end values."""
    out = [rect(xc - w / 2, p.y(hi), w, p.y(lo) - p.y(hi), fill)]
    if labels:
        xt = xc + w / 2 + 4 if side == "right" else xc - w / 2 - 4
        a = "start" if side == "right" else "end"
        out.append(text(xt, p.y(hi) + 4, f"{hi:.3f}", size, a))
        if lo > 0:
            out.append(text(xt, p.y(lo) + 4, f"{lo:.3f}", size, a))
    return out


def cc_thresholds():
    p = Plot(58, 58, 600, 400, (0, 1), (0, 2.6))
    body = [p.frame()]
    body += p.yticks([0, 0.5, 1.0, 1.5, 2.0, 2.5], "CC voltage (V)",
                     fmt="{:.1f}")
    w = 26
    # Column centres.
    cols = [p.left + 90, p.left + 200, p.left + 335, p.left + 440,
            p.left + 545]
    heads = [("Sink", "Rd ± 10 %"), ("Sink", "Rd ± 20 %"),
             ("Source", "80 µA"), ("Source", "180 µA"), ("Source", "330 µA")]
    for xc, (a, b) in zip(cols, heads):
        body.append(text(xc + 18, p.top - 26, a, 12, "middle", "bold"))
        body.append(text(xc + 18, p.top - 10, b, 12, "middle"))
    sep = (cols[1] + cols[2]) / 2 + 12
    body.append(line(sep, p.top, sep, p.bottom, INK, 1.0, "5,3"))

    # Sink with Rd within +-10 % (Table 4-36).
    x = cols[0]
    body += bar(p, x, w, 0, 0.276, FILL, labels=False)
    body += bar(p, x, w, 0.277, 0.612, SNK)
    body += bar(p, x, w, 0.613, 0.745, FILL, labels=False)
    body += bar(p, x, w, 0.746, 1.164, SNK)
    body += bar(p, x, w, 1.165, 1.368, FILL, labels=False)
    body += bar(p, x, w, 1.369, 2.042, SNK)
    for lo, hi, name in ((0.277, 0.612, "default"), (0.746, 1.164, "1.5 A"),
                         (1.369, 2.042, "3.0 A")):
        body.append(text(x - w / 2 - 4, p.y((lo + hi) / 2) + 4, name, 10,
                         "end"))
    body.append(text(x - w / 2 - 4, p.y(0.138) + 4, "detach ≤ 0.276", 10,
                         "end"))
    for v in (0.42, 0.94, 1.7):
        body.append(f'<circle cx="{x:.1f}" cy="{p.y(v):.1f}" r="3.2" '
                    f'fill="{INK}"/>')

    # Sink with Rd within +-20 % (Table 4-35).
    x = cols[1]
    body += bar(p, x, w, 0, 0.248, FILL, labels=False)
    body += bar(p, x, w, 0.249, 2.181, SNK)
    body.append(text(x - w / 2 - 4, p.y(1.2) + 4, "attached", 10, "end"))
    body.append(text(x - w / 2 - 4, p.y(0.124) + 4, "detach ≤ 0.248", 10,
                         "end"))

    # Source with a current-source Rp (Table 4-37), at the nominal current.
    for x, i_ua, wlo, whi, vopen in (
            (cols[2], 80, 0.116, 0.260, 1.321),
            (cols[3], 180, 0.234, 0.675, 1.441),
            (cols[4], 330, 0.429, 0.879, 2.432)):
        i = i_ua * 1e-6
        ra = (0.8e3 * i, 1.2e3 * i)
        rd = (5.1e3 * 0.8 * i, 5.1e3 * 1.2 * i)
        body += bar(p, x, w, ra[0], ra[1], CABLE, labels=False)
        body += bar(p, x, w, wlo, whi, FILL, side="left")
        body += bar(p, x, w, rd[0], rd[1], SNK, labels=False)
        body.append(rect(x - w / 2, p.y(2.6), w, p.y(vopen) - p.y(2.6),
                         FILL))
        body.append(text(x - w / 2 - 4, p.y(vopen) + 4, f"{vopen:.3f}", 10,
                         "end"))
        body.append(text(x + w / 2 + 4, p.y(sum(ra) / 2) + 4, "Ra", 10))
        body.append(text(x + w / 2 + 4, p.y(sum(rd) / 2) + 4, "Rd", 10))
        body.append(text(x + w / 2 + 4, p.y((vopen + 2.6) / 2) + 4, "open",
                         10))

    # Legend.
    ly = p.bottom + 26
    items = [(SNK, "CC voltage with Rd (sink: per advertised level)"),
             (CABLE, "CC voltage with Ra, at the nominal Rp current"),
             (FILL, "window in which a threshold must lie")]
    for k, (fill, label) in enumerate(items):
        y = ly + 20 * k
        body.append(rect(p.left, y - 10, 22, 12, fill))
        body.append(text(p.left + 30, y, label, 12))
    y = ly + 20 * len(items)
    body.append(f'<circle cx="{p.left + 11:.1f}" cy="{y - 4:.1f}" r="3.2" '
                f'fill="{INK}"/>')
    body.append(text(p.left + 30, y, "nominal CC voltage: 0.42 V, 0.94 V "
                     "and 1.7 V", 12))
    body.append(text(p.left + 30, y + 20, "Source Rd range: 5.1 kΩ ± 20 % "
                     "at the nominal Rp current", 12, fill=GREY))
    height = int(y + 34)
    return svg(680, height, body, "CC voltage ranges and thresholds")


def seg_row(x, y, h, segs):
    """Boxes left to right: (width, fill, line 1, line 2)."""
    out, edges = [], [x]
    for w, fill, a, b in segs:
        out.append(rect(x, y, w, h, fill))
        out.append(text(x + w / 2, y + h / 2 - 3, a, 12, "middle"))
        out.append(text(x + w / 2, y + h / 2 + 13, b, 11, "middle"))
        x += w
        edges.append(x)
    return out, edges


def bracket(x0, x1, y, label):
    return [line(x0, y - 6, x0, y), line(x0, y, x1, y), line(x1, y, x1, y - 6),
            text((x0 + x1) / 2, y + 15, label, 11, "middle")]


def packet_layout():
    body = []
    pre, kc, dat = FILL, CABLE, "#ffffff"
    body.append(text(40, 24, "Message packet", 13, weight="bold"))
    row, e = seg_row(40, 34, 44, [
        (120, pre, "Preamble", "64 bits"),
        (80, kc, "SOP", "20 bits"),
        (90, dat, "Header", "20 bits"),
        (150, dat, "Data objects", "0 to 7 × 40 bits"),
        (90, dat, "CRC", "40 bits"),
        (70, kc, "EOP", "5 bits")])
    body += row
    body += bracket(e[1], e[6], 96, "5-bit symbols (4b5b and K-codes)")
    body += bracket(e[2], e[4], 130, "covered by the CRC")
    body.append(text(40, 182, "Hard Reset or Cable Reset", 13,
                     weight="bold"))
    row, e2 = seg_row(40, 192, 44, [
        (120, pre, "Preamble", "64 bits"),
        (80, kc, "4 K-codes", "20 bits")])
    body += row
    body.append(text(40, 276, "Order on the wire: header of GoodCRC, "
                     "bytes 41h 02h", 13, weight="bold"))
    row, e3 = seg_row(40, 286, 44, [
        (150, dat, "byte 0, low: 1h", "symbol 01001"),
        (150, dat, "byte 0, high: 4h", "symbol 01010"),
        (150, dat, "byte 1, low: 2h", "symbol 10100"),
        (150, dat, "byte 1, high: 0h", "symbol 11110")])
    body += row
    body.append(line(40, 346, 640, 346, arrow="end"))
    body.append(text(40, 362, "sent first", 11))
    body.append(text(640, 362, "sent last", 11, "end"))
    body.append(text(40, 386, "Symbols are written b4 to b0 and sent b0 "
                     "first: 01001 goes out as 1, 0, 0, 1, 0.", 12))
    return svg(680, 400, body, "USB PD packet layout")


if __name__ == "__main__":
    write("cc-thresholds.svg", cc_thresholds())
    write("packet.svg", packet_layout())
