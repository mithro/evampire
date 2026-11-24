"""Port-logic figures for the RGMII pages: chain-delay (an uncalibrated
delay chain at three corners against the allowed window) and
speed-buffer (bytes held when the two ports run at different speeds).
Called from figures.py. Values are those quoted on port-logic.rst and
speed-policy.rst.

SPDX-License-Identifier: Apache-2.0
"""

from svgkit import INK, GREY, CLOCK, STABLE, ACCENT, svg, text, line, rect


def chain_delay():
    w, h = 660, 290
    left, right, top, bot, vmax = 90, 620, 30, 230, 4.5

    def yv(v):
        return bot - v / vmax * (bot - top)

    b = [line(left, top, left, bot), line(left, bot, right, bot)]
    b.append(rect(left, yv(2.8), right - left, yv(1.2) - yv(2.8), STABLE,
                  opacity=0.5))
    b.append(text(left + 6, yv(2.8) + 14, "allowed: 1.2 ns to 2.8 ns",
                  size=12, fill="#385723"))
    for v in (0, 1, 2, 3, 4):
        b.append(line(left - 5, yv(v), left, yv(v)))
        b.append(text(left - 8, yv(v) + 4, f"{v}", anchor="end", size=11))
    b.append(f'<text x="30" y="{(top + bot) / 2:.0f}" text-anchor="middle" '
             f'font-size="12" fill="{INK}" transform="rotate(-90 30 '
             f'{(top + bot) / 2:.0f})">delay of 11 buf_2 stages (ns)</text>')
    for k, (corner, v, lab) in enumerate((("FF", 1.3, "1.3 ns"),
                                         ("TT", 2.1, "about 2.1 ns"),
                                         ("SS", 4.0, "4.0 ns, outside"))):
        x = left + 90 + 170 * k
        col = ACCENT if v > 2.8 else CLOCK
        b.append(rect(x - 30, yv(v), 60, bot - yv(v), "#dbe8f5", col))
        b.append(text(x, yv(v) - 6, lab, anchor="middle", size=12, fill=col))
        b.append(text(x, bot + 18, corner, anchor="middle", size=12))
    b.append(text((left + right) / 2, bot + 38, "process corner",
                  anchor="middle", size=12))
    return svg(w, h, b)


def speed_buffer():
    """Two panels for a 1518-byte frame: (a) bytes stored, 1000 in and 100
    out; (b) bytes arrived against bytes the transmitter needs, 100 in and
    1000 out."""
    w, h = 660, 300
    n = 1518
    b = []

    def panel(x0, title, tmax, series, ylab):
        left, right, top, bot = x0 + 60, x0 + 300, 40, 220
        out = [text(x0 + 180, 20, title, anchor="middle", size=12,
                    weight="bold"),
               line(left, top, left, bot), line(left, bot, right, bot)]
        for v in (0, 500, 1000, 1500):
            yy = bot - v / 1600 * (bot - top)
            out.append(line(left - 4, yy, left, yy))
            out.append(text(left - 6, yy + 4, f"{v}", anchor="end", size=10))
        for k in range(6):
            t = tmax * k / 5
            xx = left + t / tmax * (right - left)
            out.append(line(xx, bot, xx, bot + 4))
            out.append(text(xx, bot + 16, f"{t:g}", anchor="middle",
                            size=10))
        out.append(text((left + right) / 2, bot + 32, "time (µs)",
                        anchor="middle", size=11))
        out.append(f'<text x="{x0 + 14}" y="{(top + bot) / 2:.0f}" '
                   'text-anchor="middle" font-size="11" '
                   f'fill="{INK}" transform="rotate(-90 {x0 + 14} '
                   f'{(top + bot) / 2:.0f})">{ylab}</text>')
        for pts, col, lab, (lt, lv) in series:
            p = " ".join(f"{left + t / tmax * (right - left):.1f},"
                         f"{bot - v / 1600 * (bot - top):.1f}"
                         for t, v in pts)
            out.append(f'<polyline points="{p}" fill="none" stroke="{col}" '
                       'stroke-width="2"/>')
            out.append(text(left + lt / tmax * (right - left),
                            bot - lv / 1600 * (bot - top), lab, size=10,
                            fill=col))
        return out

    t_in, t_out = n * 0.008, n * 0.080      # µs
    stored = [(0, 0), (t_in, n - n * 0.1), (t_out, 0)]
    b += panel(0, "1000 Mbit/s in, 100 Mbit/s out", 125,
               [(stored, ACCENT, "bytes held: up to 90 % of the frame",
                 (20, 1450))], "bytes held")
    arrived = [(0, 0), (t_out, n)]
    needed = [(0, 0), (t_in, n)]
    b += panel(330, "100 Mbit/s in, 1000 Mbit/s out", 125,
               [(needed, ACCENT, "bytes the transmitter needs",
                 (16, 1450)),
                (arrived, CLOCK, "bytes arrived", (60, 500))], "bytes")
    b.append(text(510, 250 + 26, "the transmitter runs out after the "
                  "first byte", anchor="middle", size=11, fill=GREY))
    return svg(w, h, b)
