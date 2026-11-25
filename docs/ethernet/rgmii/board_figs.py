"""Board, clock and pad figures for the RGMII pages: clock-cycle,
meander-280, meander-86, pad-delay, pad-duty and pad-edges. Called from
figures.py. Values are those quoted on timing.rst, io-cells.rst and
port-logic.rst.

SPDX-License-Identifier: Apache-2.0
"""

from svgkit import (INK, GREY, CLOCK, DATA_FILL, ZONE, STABLE, ACCENT, svg,
                    text, line, rect)


def _poly(pts, stroke=CLOCK, width=1.8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="none" stroke="{stroke}" '
            f'stroke-width="{width}"{d}/>')


def _axis(xs, t0, t1, step, y, label):
    out = [line(xs(t0), y, xs(t1), y)]
    t = t0
    while t <= t1 + 1e-9:
        out.append(line(xs(t), y, xs(t), y + 5))
        out.append(text(xs(t), y + 18, f"{t:g}", anchor="middle", size=11))
        t += step
    out.append(text(xs(t0) - 10, y + 18, label, anchor="end", size=12))
    return out


# ---------------------------------------------------------------------------
# clock-cycle.svg: one annotated RGMII clock cycle.
# ---------------------------------------------------------------------------

def clock_cycle():
    w, h = 660, 290
    left, right, t0, t1 = 130, 640, -1.0, 10.0

    def xs(t):
        return left + (t - t0) / (t1 - t0) * (right - left)

    hi, lo = 60, 140
    edge = 0.6   # schematic edge time drawn, ns
    pts = [(xs(t0), lo), (xs(0), lo), (xs(edge), hi), (xs(4.0), hi),
           (xs(4.0 + edge), lo), (xs(8.0), lo), (xs(8.0 + edge), hi),
           (xs(t1), hi)]
    b = [text(left - 10, 104, "clock", anchor="end"), _poly(pts)]
    # Period.
    b.append(line(xs(0.3), 40, xs(8.3), 40, INK, 1.2, arrows=True))
    b.append(text(xs(4.3), 32, "period 7.2 ns to 8.8 ns, 8.0 ns typical",
                  anchor="middle", size=12))
    # High time band, 45 % to 55 % of 8.0 ns.
    b.append(rect(xs(3.6 + 0.3), hi - 4, xs(4.4 + 0.3) - xs(3.6 + 0.3),
                  lo - hi + 8, STABLE, opacity=0.6))
    b.append(line(xs(0.3), 160, xs(4.3), 160, INK, 1.2, arrows=True))
    b.append(text(xs(2.3), 178, "high time: 45 % to 55 % of the period",
                  anchor="middle", size=12))
    b.append(text(xs(2.3), 194, "3.6 ns to 4.4 ns at 8.0 ns",
                  anchor="middle", size=12, fill=GREY))
    # Edge time, 20 % to 80 %.
    y20, y80 = lo - 0.2 * (lo - hi), lo - 0.8 * (lo - hi)
    for yy, lab in ((y20, "20 %"), (y80, "80 %")):
        b.append(line(xs(7.2), yy, xs(9.6), yy, GREY, 0.8, dash="3,3"))
        b.append(text(xs(9.7), yy + 4, lab, size=11, fill=GREY))
    b.append(text(xs(8.3), 220, "rise and fall time, 20 % to 80 %:",
                  anchor="middle", size=12, fill=ACCENT))
    b.append(text(xs(8.3), 236, "0.75 ns or less", anchor="middle", size=12,
                  fill=ACCENT))
    b += _axis(xs, 0, 10, 2, 255, "time (ns)")
    return svg(w, h + 12, b)


# ---------------------------------------------------------------------------
# meander-*.svg: a clock trace lengthened by a meander.
# ---------------------------------------------------------------------------

def meander(extra_mm, note):
    w, h = 660, 230
    b = [rect(20, 50, 110, 130, "#dbe8f5", INK),
         text(75, 120, "evampire", anchor="middle"),
         rect(530, 50, 110, 130, "#ffffff", INK),
         text(585, 112, "Ethernet", anchor="middle"),
         text(585, 128, "transceiver", anchor="middle")]
    for k, y in enumerate((70, 85, 100)):
        b.append(line(130, y, 530, y, "#7f7f7f", 2))
    b.append(text(330, 64, "data traces, straight", anchor="middle",
                  size=11, fill=GREY))
    # Clock trace with a meander between x = 200 and 460.
    y0, amp, pitch = 150, 22, 20
    pts = [(130, y0), (200, y0)]
    x = 200
    up = True
    while x + pitch <= 460:
        yy = y0 - amp if up else y0 + amp
        pts += [(x, yy), (x + pitch, yy)]
        x += pitch
        up = not up
    pts += [(x, y0), (530, y0)]
    b.append(_poly(pts, ACCENT, 2.2))
    b.append(text(150, y0 - 8, "clock", size=11, fill=ACCENT))
    b.append(text(330, 205, f"meander: about {extra_mm} mm of extra clock "
                  "trace", anchor="middle", size=12, fill=ACCENT))
    b.append(text(330, 222, note, anchor="middle", size=12))
    return svg(w, h + 12, b)


# ---------------------------------------------------------------------------
# Pad figures.
# ---------------------------------------------------------------------------

def pad_delay():
    """TXC and TXD through identical pads: the same delay, so the skew at
    the pins is unchanged. TT corner: 3.04 ns rising, 3.20 ns falling;
    each data edge is drawn with the direction of the clock edge."""
    w, h = 660, 250
    left, right, t0, t1 = 160, 640, -1.0, 12.0

    def xs(t):
        return left + (t - t0) / (t1 - t0) * (right - left)

    def edges_of(d):
        rise, fall = d
        return [rise, 4 + fall, 8 + rise]

    def clk(y, d):
        e = edges_of(d)
        pts = [(xs(t0), y + 20), (xs(e[0]), y + 20), (xs(e[0]), y),
               (xs(e[1]), y), (xs(e[1]), y + 20), (xs(e[2]), y + 20),
               (xs(e[2]), y), (xs(t1), y)]
        return _poly(pts)

    def dat(y, d, names):
        out = []
        edges = [t0] + edges_of(d) + [t1]
        for k in range(4):
            a, c = edges[k], edges[k + 1]
            out.append(rect(xs(a) + 2, y, xs(c) - xs(a) - 4, 20, DATA_FILL,
                            INK))
            if names[k]:
                out.append(text((xs(a) + xs(c)) / 2, y + 15, names[k],
                                anchor="middle", size=11))
        return out

    b = []
    rows = (("TXC, inside", 30, (0, 0), clk),
            ("TXD, inside", 60, (0, 0), dat),
            ("TXC at the pin", 120, (3.04, 3.20), clk),
            ("TXD at the pin", 150, (3.04, 3.20), dat))
    for lab, y, d, fn in rows:
        b.append(text(left - 10, y + 15, lab, anchor="end", size=12))
        b += [fn(y, d)] if fn is clk else fn(y, d, ["", "n0", "n1", ""])
    b.append(line(xs(0), 95, xs(3.04), 95, INK, 1.2, arrows=True))
    b.append(text(xs(3.2), 99, "the same pad delay on both: 3.04 ns rising, "
                  "3.20 ns falling, at TT", size=11))
    b += _axis(xs, 0, 12, 2, 200, "time (ns)")
    return svg(w, h, b)


def pad_duty():
    """Internal 50 % clock and the pin clock at the SS corner."""
    w, h = 660, 230
    left, right, t0, t1 = 150, 640, -1.0, 16.0

    def xs(t):
        return left + (t - t0) / (t1 - t0) * (right - left)

    def wave(y, r, f):
        return _poly([(xs(t0), y + 22), (xs(r), y + 22), (xs(r), y),
                      (xs(f), y), (xs(f), y + 22), (xs(r + 8), y + 22),
                      (xs(r + 8), y), (xs(t1), y)])

    b = [text(left - 10, 50, "inside, 50 %", anchor="end", size=12),
         wave(34, 0.0, 4.0),
         text(left - 10, 120, "TXC at the pin", anchor="end", size=12),
         wave(104, 5.74, 4.0 + 6.01)]
    for x0, x1, y, lab in ((0, 5.74, 80, "tpr = 5.74 ns"),
                           (4.0, 10.01, 92, "tpf = 6.01 ns")):
        b.append(line(xs(x0), y, xs(x1), y, INK, 1.1, arrows=True))
        b.append(text(xs(x1) + 6, y + 4, lab, size=11))
    b.append(line(xs(5.74), 150, xs(10.01), 150, ACCENT, 1.3, arrows=True))
    b.append(text(xs(7.9), 168, "thi = 4.27 ns: 53 % of 8.00 ns, inside "
                  "45 % to 55 %", anchor="middle", size=12, fill=ACCENT))
    b += _axis(xs, 0, 16, 2, 190, "time (ns)")
    return svg(w, h, b)


def pad_edges():
    """Edges of the standard pad against the RGMII 0.75 ns limit."""
    w, h = 660, 290
    left, right, t0, t1 = 80, 640, 0.0, 4.0
    top, bot = 30, 210

    def xs(t):
        return left + (t - t0) / (t1 - t0) * (right - left)

    def yv(p):
        return bot - p / 100 * (bot - top)

    b = [line(left, top, left, bot), line(left, bot, right, bot)]
    for p in (0, 20, 50, 80, 100):
        b.append(line(left - 5, yv(p), left, yv(p)))
        b.append(text(left - 8, yv(p) + 4, f"{p}", anchor="end", size=11))
        if p in (20, 80):
            b.append(line(left, yv(p), right, yv(p), GREY, 0.6, dash="3,3"))
    b.append(f'<text x="22" y="{(top + bot) / 2:.0f}" text-anchor="middle" '
             f'font-size="12" fill="{INK}" transform="rotate(-90 22 '
             f'{(top + bot) / 2:.0f})">voltage (% of VDD)</text>')
    # Linear ramps whose 20-80 % time is the edge time; start at 0.2 ns.
    for k, (t, col, lab) in enumerate((
                        (0.53, "#548235", "FF falling 0.53 ns"),
                        (0.63, "#548235", "FF rising 0.63 ns"),
                        (0.75, ACCENT, "RGMII limit 0.75 ns"),
                        (1.67, "#c55a11", "SS falling 1.67 ns"),
                        (1.89, "#c55a11", "SS rising 1.89 ns"))):
        full = t / 0.6
        b.append(_poly([(xs(0), yv(0)), (xs(0.2), yv(0)),
                        (xs(0.2 + full), yv(100)), (xs(4.0), yv(100))],
                       col, 2.4 if "limit" in lab else 1.6,
                       dash="6,4" if "limit" in lab else None))
        yl = yv(62 - 10 * k)
        b.append(line(xs(2.65), yl - 4, xs(2.95), yl - 4, col,
                      2.4 if "limit" in lab else 1.6,
                      dash="6,4" if "limit" in lab else None))
        b.append(text(xs(3.0), yl, lab, size=11, fill=col))
    for t in (0, 1, 2, 3, 4):
        b.append(line(xs(t), bot, xs(t), bot + 5))
        b.append(text(xs(t), bot + 18, f"{t}", anchor="middle", size=11))
    b.append(text((left + right) / 2, bot + 36, "time (ns)",
                  anchor="middle", size=12))
    return svg(w, h, b)
