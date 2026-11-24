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
dc-level.svg
    The BMC signal starting and ending at the Rp/Rd level (cc-signalling.rst).
rx-margin.svg
    The measured BMC interval against the 0.75 UI decision point
    (software.rst).
dead-battery.svg
    The CC voltage of the dead-battery Rd path against the pull-up
    current (analogue.rst).
packet.svg
    The parts of a packet, a Hard Reset, and the order in which the
    nibbles and symbols are sent (packets.rst).

Every number comes from the page that shows the figure.

SPDX-License-Identifier: Apache-2.0
"""

from svgfig import (CABLE, CABLE_INK, FILL, GREY, INK, SNK, SNK_INK, Plot,
                    line, polyline, rect, svg, text, write)


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


UI = 1e6 / 300e3          # unit interval at 300 kbit/s, in µs
V_SWING = 1.125           # nominal vSwing (V)
T_EDGE = 0.3              # edge time drawn (µs), the 300 ns minimum


def bmc(t0, bits, level):
    """Points of a BMC waveform from t0 (µs), starting at level (0 or 1),
    with an edge at the start of every bit and in the middle of each 1."""
    pts, t, lv = [(t0, level)], t0, level
    for b in bits:
        for half in ((0, 1) if b else (0,)):
            th = t + half * UI / 2
            if not (th == t0):
                pts += [(th, lv), (th + T_EDGE, 1 - lv)]
                lv = 1 - lv
        t += UI
    return pts, t, lv


def dc_level():
    body = []
    yr = (-0.4, 2.1)
    ps = Plot(60, 40, 280, 240, (0, 20), yr)
    pe = Plot(380, 40, 280, 240, (0, 36), yr)
    idle = 1.7
    for p, title in ((ps, "Start of a packet"), (pe, "End of a packet")):
        body.append(text(p.left, p.top - 10, title, 13, weight="bold"))
        for v in (0.4, 0.9):
            body.append(line(p.left, p.y(v), p.right, p.y(v), GREY, 1.0,
                             "6,3"))
        body.append(line(p.left, p.y(V_SWING), p.right, p.y(V_SWING), GREY,
                         0.6, "2,2"))
        body.append(p.frame())
    body += ps.yticks([0, 0.4, 0.9, V_SWING, 1.7], "CC voltage (V)",
                      fmt="{:g}", grid=False)
    # Start: idle at the Rp/Rd level, then the preamble from a low level.
    t0 = 4.0
    pts, _, _ = bmc(t0, [0, 1, 0, 1, 0, 1], 0)
    wave = [(0, idle), (t0, idle), (t0 + T_EDGE, 0)] + [
        (t, V_SWING * lv) for t, lv in pts[1:] if t <= 20]
    wave.append((20, wave[-1][1]))
    body.append(polyline(ps.pts(wave), INK, 2.0))
    body.append(text(ps.x(0.3), ps.y(idle) - 8, "idle, 3.0 A level", 11))
    body.append(text(ps.x(t0) + 4, ps.y(-0.2) + 4, "driven low: preamble",
                     11))
    # End: last bits, final edge low, hold low, release.
    pts, t_end, lv = bmc(0, [1, 0, 1], 1)
    wave = [(t, V_SWING * v) for t, v in pts]
    wave += [(t_end, V_SWING * lv), (t_end + T_EDGE, 0)]
    t_rel = t_end + 4.0
    wave += [(t_rel, 0)]
    for k in range(1, 31):
        dt = k * 0.25
        wave.append((t_rel + dt, idle * (1 - 2.718281828 ** (-dt / 1.2))))
    wave.append((36, idle))
    body.append(polyline(pe.pts(wave), INK, 2.0))
    body.append(line(pe.x(t_end), pe.y(-0.3), pe.x(t_end + 23), pe.y(-0.3),
                     arrow="both"))
    body.append(text(pe.x(t_end + 11.5), pe.y(-0.3) - 5,
                     "release by 23 µs (tEndDriveBMC)", 11, "middle"))
    body.append(line(pe.x(t_end), pe.top, pe.x(t_end), pe.bottom, INK, 0.8,
                     "4,3"))
    body.append(text(pe.x(t_end) + 4, pe.y(0.6), "low ≥ 1 µs", 11))
    body.append(text(pe.x(t_end) + 4, pe.y(0.6) + 14, "(tHoldLowBMC),", 11))
    body.append(text(pe.x(t_end) + 4, pe.y(0.6) + 28, "then released", 11))
    body.append(text(pe.x(t_end) - 4, pe.top + 14, "end of", 11, "end"))
    body.append(text(pe.x(t_end) - 4, pe.top + 28, "last bit", 11, "end"))
    body += ps.xticks([0, 5, 10, 15, 20], "time (µs)", grid=False)
    body += pe.xticks([0, 10, 20, 30], "time (µs)", grid=False)
    for v, lab in ((0.9, "1.5 A idle level"), (0.4, "default idle level")):
        body.append(text(pe.right - 4, pe.y(v) - 4, lab, 10, "end",
                         fill=GREY))
    body.append(text(pe.right - 4, pe.y(V_SWING) - 4, "vSwing 1.125 V", 10,
                     "end", fill=GREY))
    y = ps.bottom + 62
    body.append(text(ps.left, y, "Shown at the 3.0 A level, idle 1.7 V. "
                     "The ground offset moves the received signal by up "
                     "to 250 mV:", 12))
    body.append(text(ps.left, y + 18, "down at the sink, up at the source. "
                     "The release slope is schematic.", 12))
    return svg(680, int(y + 30), body, "CC signal on its DC level")


def rx_margin():
    """Measured BMC interval: edge displacement and sampling error against
    the 0.75 UI decision point (software.rst)."""
    p = Plot(150, 30, 500, 130, (0.2, 1.3), (0, 2))
    x_rx, ts = 0.07, 0.11            # UI; 0.11 UI = 333 ns at 3.03 us
    body = [p.frame()]
    rows = [(1.45, 0.5, "half of a 1", "0.5 UI"),
            (0.55, 1.0, "a whole 0", "1 UI")]
    for y, nom, a, b in rows:
        lo, hi = nom - 2 * x_rx, nom + 2 * x_rx
        h = 0.5
        body.append(rect(p.x(lo - ts), p.y(y + h / 2), p.x(lo) - p.x(lo - ts),
                         p.y(y - h / 2) - p.y(y + h / 2), CABLE))
        body.append(rect(p.x(hi), p.y(y + h / 2), p.x(hi + ts) - p.x(hi),
                         p.y(y - h / 2) - p.y(y + h / 2), CABLE))
        body.append(rect(p.x(lo), p.y(y + h / 2), p.x(hi) - p.x(lo),
                         p.y(y - h / 2) - p.y(y + h / 2), FILL))
        body.append(line(p.x(nom), p.y(y + h / 2), p.x(nom), p.y(y - h / 2),
                         INK, 2.0))
        body.append(text(p.left - 8, p.y(y) - 2, a, 12, "end"))
        body.append(text(p.left - 8, p.y(y) + 13, b, 12, "end"))
    body.append(line(p.x(0.75), p.top - 6, p.x(0.75), p.bottom, INK, 1.6,
                     "6,3"))
    body.append(text(p.x(0.75), p.top - 10, "decision at 0.75 UI", 11,
                     "middle"))
    body += p.xticks([0.25, 0.36, 0.5, 0.64, 0.75, 0.86, 1.0, 1.14, 1.25],
                     "measured interval (UI)", fmt="{:g}", size=10,
                     grid=False)
    ly = p.bottom + 64
    body.append(rect(p.left, ly - 10, 22, 12, FILL))
    body.append(text(p.left + 30, ly, "two edges each up to 0.07 UI off: "
                     "± 0.14 UI", 12))
    body.append(rect(p.left, ly + 10, 22, 12, CABLE))
    body.append(text(p.left + 30, ly + 20, "sampling error up to T_s = "
                     "0.11 UI, 333 ns at 330 kbit/s", 12))
    return svg(680, int(ly + 34), body, "Receive timing margin")


def dead_battery():
    """CC voltage of the dead-battery Rd path against the source's pull-up
    current, V_CC = I_Rp x R_s + V_GS with the overdrive neglected, against
    the source's thresholds (analogue.rst; Type-C Table 4-37)."""
    p = Plot(60, 30, 590, 300, (0, 380), (0, 2.6))
    body = []
    # (current range, lower threshold, upper threshold, margin, name)
    levels = [(64, 96, 0.260, 1.321, 1.32, "default"),
              (165.6, 194.4, 0.675, 1.441, 1.32, "1.5 A"),
              (303.6, 356.4, 0.879, 2.432, 2.181, "3.0 A")]
    for lo, hi, vlo, vhi, vm, name in levels:
        body.append(rect(p.x(lo), p.y(vhi), p.x(hi) - p.x(lo),
                         p.y(vlo) - p.y(vhi), SNK, "none"))
        body.append(line(p.x(lo), p.y(vm), p.x(hi), p.y(vm), SNK_INK, 1.2,
                         "4,2"))
        body.append(text(p.x((lo + hi) / 2), p.top + 14, name, 11,
                         "middle"))
    body.append(p.frame())
    body += p.yticks([0, 0.5, 1.0, 1.5, 2.0, 2.5], "CC voltage (V)",
                     fmt="{:g}", grid=False)
    lines = [(2.0e3, 0.85, INK, None, "standard, Vt 0.85 V, 2.0 kΩ"),
             (2.0e3, 0.61, INK, "8,3,2,3", "standard, Vt 0.61 V, 2.0 kΩ"),
             (5.0e3, 0.0, CABLE_INK, "6,3", "native, 5.0 kΩ"),
             (2.0e3, 0.0, GREY, "2,3", "native, 2.0 kΩ: too low")]
    for r_s, vgs, col, dash, lab in lines:
        pts = [(i, i * 1e-6 * r_s + vgs) for i in (0, 380)]
        pts = [(i, v) for i, v in pts]
        if pts[-1][1] > 2.6:
            pts[-1] = ((2.6 - vgs) / (r_s * 1e-6), 2.6)
        body.append(polyline(p.pts(pts), col, 1.8, dash))
    body += p.xticks([0, 50, 100, 150, 200, 250, 300, 350],
                     "pull-up current I_Rp (µA)", grid=False)
    y = p.bottom + 58
    for k, (r_s, vgs, col, dash, lab) in enumerate(lines):
        x0 = p.left + 300 * (k % 2)
        yy = y + 18 * (k // 2)
        body.append(line(x0, yy - 4, x0 + 30, yy - 4, col, 1.8, dash))
        body.append(text(x0 + 36, yy, lab, 12))
    y += 40
    body.append(text(p.left, y, "Green: the window between the source's "
                     "Ra and open thresholds; dashed: the margin targets.",
                     12, fill=GREY))
    body.append(text(p.left, y + 18, "Native lines drawn with V_GS = 0; "
                     "overdrive neglected.", 12, fill=GREY))
    return svg(680, int(y + 30), body, "Dead-battery Rd voltage")

if __name__ == "__main__":
    write("cc-thresholds.svg", cc_thresholds())
    write("packet.svg", packet_layout())
    write("dc-level.svg", dc_level())
    write("rx-margin.svg", rx_margin())
    write("dead-battery.svg", dead_battery())
