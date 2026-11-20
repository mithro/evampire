# /// script
# requires-python = ">=3.10"
# ///
"""Write tx-mask.svg and rx-mask.svg: the USB PD BMC transmit and receive
masks, drawn from the coordinates in PD Tables 5.6, 5.7 and 5.8, with the
shapes of PD Figures 5.12 to 5.19. Run with:

    uv run docs/power/usb-pd/masks.py

The transmit figure also draws an RC-shaped waveform for the fastest
allowed edge (10 %-90 % time 300 ns) and, dashed, for the slowest RC edge
that stays out of the mask at the nominal swing and the fastest bit rate.

SPDX-License-Identifier: Apache-2.0
"""

import math
import pathlib

HERE = pathlib.Path(__file__).parent

# PD Table 5.6 (UI) and Table 5.7 (V): transmit mask.
TX_X = {1: 0.015, 2: 0.07, 3: 0.15, 4: 0.25, 5: 0.35, 6: 0.43, 7: 0.485,
        8: 0.515, 9: 0.57, 10: 0.65, 11: 0.75, 12: 0.85, 13: 0.93,
        14: 0.985}
TX_Y = {1: -0.075, 2: 0.075, 3: 0.15, 4: 0.325, 5: 0.5625, 6: 0.8,
        7: 0.975, 8: 1.04, 9: 1.2}

# PD Table 5.8: receive mask.
RX_X = {1: 0.07, 2: 0.15, 3: 0.35, 4: 0.43, 5: 0.57, 6: 0.65, 7: 0.85,
        8: 0.93}
RX_Y1, RX_Y5 = -0.3325, 1.5325
RX_ROLES = [  # (title, centre line Y3Rx, half height of the inner mask)
    ("Port sinking power", 0.4375, 0.205),
    ("Port neither sinking nor sourcing", 0.5625, 0.33),
    ("Port sourcing power", 0.6875, 0.205),
]

# Edge shapes for the example waveforms (an assumption: first-order RC).
V_SWING = 1.125                         # nominal vSwing, PD Table 5.10
TAU_FAST = 300e-9 / math.log(9)         # 10 %-90 % = 300 ns
UI_NOM = 1 / 300e3
UI_FAST = 1 / 330e3
# Slowest RC edge at nominal swing, 330 kbit/s: limited by (X3Tx, Y7Tx).
TAU_SLOW = TX_X[3] * UI_FAST / math.log(
    (V_SWING - TX_Y[5]) / (V_SWING - TX_Y[7]))

FONT = 'font-family="Helvetica, Arial, sans-serif"'
WIDTH = 500
LEFT, RIGHT = 62, 490         # plot area, px
XMIN, XMAX = -0.06, 1.06       # UI shown


def xpx(ui):
    return LEFT + (ui - XMIN) / (XMAX - XMIN) * (RIGHT - LEFT)


class Panel:
    """One plot: voltage (vmin..vmax) against time in UI."""

    def __init__(self, top, height, vmin, vmax):
        self.top, self.height = top, height
        self.vmin, self.vmax = vmin, vmax

    def y(self, v):
        return self.top + (self.vmax - v) / (self.vmax - self.vmin) * self.height

    def pts(self, points):
        return " ".join(f"{xpx(u):.1f},{self.y(v):.1f}" for u, v in points)


def text(x, y, s, size=13, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" {FONT} font-size="{size}" '
            f'text-anchor="{anchor}" font-weight="{weight}" '
            f'fill="#000000">{s}</text>')


def frame(p, title, levels, keep_lo, keep_hi):
    """Axes, the outer keep-out bands, a title and level labels."""
    out = []
    out.append(text(LEFT, p.top - 8, title, size=14, weight="bold"))
    # Outer keep-out bands.
    for v0, v1 in ((p.vmax, keep_hi), (keep_lo, p.vmin)):
        y0, y1 = p.y(v0), p.y(v1)
        out.append(f'<rect x="{LEFT}" y="{y0:.1f}" width="{RIGHT - LEFT}" '
                   f'height="{y1 - y0:.1f}" fill="#d9d9d9" stroke="#000000" '
                   f'stroke-width="0.8"/>')
    # Dashed lines at the labelled levels.
    for v in levels:
        out.append(f'<line x1="{LEFT}" x2="{RIGHT}" y1="{p.y(v):.1f}" '
                   f'y2="{p.y(v):.1f}" stroke="#7f7f7f" stroke-width="0.6" '
                   f'stroke-dasharray="3,3"/>')
        out.append(text(LEFT - 6, p.y(v) + 4, f"{v:g}", size=12,
                        anchor="end"))
    # Bit boundaries.
    for u in (0, 0.5, 1):
        out.append(f'<line x1="{xpx(u):.1f}" x2="{xpx(u):.1f}" '
                   f'y1="{p.top}" y2="{p.top + p.height}" stroke="#7f7f7f" '
                   f'stroke-width="0.6" stroke-dasharray="1,3"/>')
    out.append(f'<rect x="{LEFT}" y="{p.top}" width="{RIGHT - LEFT}" '
               f'height="{p.height}" fill="none" stroke="#000000" '
               f'stroke-width="1"/>')
    return out


def keep_out(p, points, label=None):
    out = [f'<polygon points="{p.pts(points)}" fill="#d9d9d9" '
           f'stroke="#000000" stroke-width="1"/>']
    if label:
        cu = sum(u for u, _ in points) / len(points)
        cv = sum(v for _, v in points) / len(points)
        out.append(text(xpx(cu), p.y(cv) + 4, label, size=12,
                        anchor="middle"))
    return out


def x_ticks(p, ticks):
    out = []
    yb = p.top + p.height
    for u in ticks:
        out.append(f'<line x1="{xpx(u):.1f}" x2="{xpx(u):.1f}" y1="{yb}" '
                   f'y2="{yb + 5}" stroke="#000000" stroke-width="1"/>')
        out.append(text(xpx(u), yb + 18, f"{u:g}", size=12, anchor="middle"))
    out.append(text((LEFT + RIGHT) / 2, yb + 36,
                    "time from the start of the bit (UI)", size=13,
                    anchor="middle"))
    return out


def rc_wave(edges, tau_ui, swing):
    """Points of the output of a first-order RC filter driven by steps.

    edges: list of (time in UI at which the output crosses the mid level,
    new level 0 or 1), starting from level 0. Each step starts tau x ln 2
    before its crossing time, so that a settled edge crosses the mid level
    on time. The output is the sum of the step responses."""
    shift = tau_ui * math.log(2)
    steps, prev = [], 0
    for t, lvl in edges:
        steps.append((t - shift, swing * (lvl - prev)))
        prev = lvl
    pts = []
    n = 600
    for i in range(n + 1):
        u = XMIN + (XMAX - XMIN) * i / n
        v = sum(a * (1 - math.exp(-(u - s) / tau_ui))
                for s, a in steps if u >= s)
        pts.append((u, v))
    return pts


def polyline(p, pts, dash=None, width=2.2):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{p.pts(pts)}" fill="none" stroke="#000000" '
            f'stroke-width="{width}"{d}/>')


def svg(height, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" '
            f'height="{height}" viewBox="0 0 {WIDTH} {height}">\n'
            f'<title>{title}</title>\n'
            f'<rect width="{WIDTH}" height="{height}" fill="#ffffff"/>\n'
            + "\n".join(body) + "\n</svg>\n")


def tx_figure():
    X, Y = TX_X, TX_Y
    one = [
        [(X[1], Y[5]), (X[2], Y[6]), (X[3], Y[7]), (X[4], Y[8]),
         (X[5], Y[8]), (X[6], Y[6]), (X[7], Y[5]), (X[6], Y[4]),
         (X[5], Y[2]), (X[4], Y[2]), (X[3], Y[3]), (X[2], Y[4])],
        [(X[8], Y[5]), (X[9], Y[6]), (X[10], Y[7]), (X[11], Y[8]),
         (X[12], Y[8]), (X[13], Y[6]), (X[14], Y[5]), (X[13], Y[4]),
         (X[12], Y[2]), (X[11], Y[2]), (X[10], Y[3]), (X[9], Y[4])],
    ]
    zero = [[(X[1], Y[5]), (X[2], Y[6]), (X[3], Y[7]), (X[4], Y[8]),
             (X[12], Y[8]), (X[13], Y[6]), (X[14], Y[5]), (X[13], Y[4]),
             (X[12], Y[2]), (X[4], Y[2]), (X[3], Y[3]), (X[2], Y[4])]]
    levels = [Y[1], Y[2], Y[5], Y[8], Y[9]]
    body = []
    ph = 230
    p1 = Panel(30, ph, -0.25, 1.35)
    p2 = Panel(30 + ph + 75, ph, -0.25, 1.35)
    fast = TAU_FAST / UI_NOM
    slow = TAU_SLOW / UI_FAST
    for p, title, polys, edges in (
            (p1, "Transmitting a 1", one, [(0, 1), (0.5, 0), (1, 1)]),
            (p2, "Transmitting a 0", zero, [(0, 1), (1, 0)])):
        body += frame(p, title, levels, Y[1], Y[9])
        for poly in polys:
            body += keep_out(p, poly, "keep out")
        body.append(polyline(p, rc_wave(edges, fast, V_SWING)))
        body.append(polyline(p, rc_wave(edges, slow, V_SWING),
                             dash="6,4", width=1.6))
        body.append(text(RIGHT - 4, p.y(1.27) + 4, "keep out", size=12,
                         anchor="end"))
        body.append(text(RIGHT - 4, p.y(-0.17) + 4, "keep out", size=12,
                         anchor="end"))
    body += x_ticks(p2, [0, 0.25, 0.5, 0.75, 1])
    # Tick labels under panel 1 too, without the axis title.
    yb = p1.top + p1.height
    for u in (0, 0.25, 0.5, 0.75, 1):
        body.append(text(xpx(u), yb + 18, f"{u:g}", size=12,
                         anchor="middle"))
    # Legend: a sample of each line style with its meaning.
    ly = p2.top + p2.height + 64
    for dash, width, label in (
            (None, 2.2, "fastest allowed edge (300 ns, 10 %-90 %)"),
            ("6,4", 1.6, "slowest RC edge that stays out (estimate)")):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        body.append(f'<line x1="{LEFT}" x2="{LEFT + 40}" y1="{ly - 4}" '
                    f'y2="{ly - 4}" stroke="#000000" '
                    f'stroke-width="{width}"{d}/>')
        body.append(text(LEFT + 48, ly, label, size=13))
        ly += 20
    height = int(ly)
    body.insert(0, text(8, 16, "V", size=13))
    return svg(height, body, "USB PD BMC transmit masks")


def rx_figure():
    X = RX_X
    body = []
    ph = 150
    top = 30
    panels = []
    for title, centre, half in RX_ROLES:
        p = Panel(top, ph, -0.62, 1.82)
        lo, hi = centre - half, centre + half
        polys = [
            [(X[1], centre), (X[2], hi), (X[3], hi), (X[4], centre),
             (X[3], lo), (X[2], lo)],
            [(X[5], centre), (X[6], hi), (X[7], hi), (X[8], centre),
             (X[7], lo), (X[6], lo)],
        ]
        body += frame(p, title, [RX_Y1, lo, centre, hi, RX_Y5], RX_Y1,
                      RX_Y5)
        for poly in polys:
            body += keep_out(p, poly)
        body.append(text(xpx(0.25), p.y(centre) + 4, "keep out", size=12,
                         anchor="middle"))
        body.append(text(xpx(0.75), p.y(centre) + 4, "keep out", size=12,
                         anchor="middle"))
        for v in ((p.vmax + RX_Y5) / 2, (p.vmin + RX_Y1) / 2):
            body.append(text(RIGHT - 4, p.y(v) + 4, "keep out", size=12,
                             anchor="end"))
        panels.append(p)
        top += ph + 52
    last = panels[-1]
    body += x_ticks(last, [0, 0.07, 0.43, 0.57, 0.93, 1])
    for p in panels[:-1]:
        yb = p.top + p.height
        for u in (0.07, 0.43, 0.57, 0.93):
            body.append(text(xpx(u), yb + 16, f"{u:g}", size=12,
                             anchor="middle"))
    height = int(last.top + last.height + 48)
    body.insert(0, text(8, 16, "V", size=13))
    return svg(height, body, "USB PD BMC receive masks for a 1")


for name, content in (("tx-mask.svg", tx_figure()),
                      ("rx-mask.svg", rx_figure())):
    path = HERE / name
    path.write_text(content)
    print(f"wrote {path}")
print(f"tau fast {TAU_FAST * 1e9:.1f} ns, tau slow {TAU_SLOW * 1e9:.1f} ns")
