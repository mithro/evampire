# /// script
# requires-python = ">=3.10"
# ///
"""Draw the timing figures for the RGMII pages as SVG files.

Usage: uv run docs/ethernet/rgmii/figures.py

Writes timing-params.svg (what each skew, setup and hold parameter of
tab-rgmii-timing measures) and timing-budget.svg (the setup and hold
margins of the worked budget), from the values quoted on timing.rst, and
speed-change.svg (TXC changing speed with a stretched phase, and a
forbidden glitch) and frame.svg (the fields of a frame), next to this
script.

SPDX-License-Identifier: Apache-2.0
"""

import pathlib

HERE = pathlib.Path(__file__).parent

INK = "#222222"
GREY = "#7f7f7f"
CLOCK = "#1f4e79"
DATA_FILL = "#dbe8f5"
ZONE = "#d9d9d9"        # where an edge may fall
STABLE = "#a9d18e"      # where the data must not change
ACCENT = "#c00000"


def svg(w, h, body):
    defs = ('<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" '
            f'height="{h}" viewBox="0 0 {w} {h}" '
            'font-family="Helvetica, Arial, sans-serif" font-size="13">\n'
            f'<rect width="{w}" height="{h}" fill="white"/>\n{defs}\n'
            + "\n".join(body) + "\n</svg>\n")


def text(x, y, s, anchor="start", size=13, weight="normal", fill=INK):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}">{s}</text>')


def line(x1, y1, x2, y2, stroke=INK, width=1.2, dash=None, arrows=False):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = (' marker-start="url(#a)" marker-end="url(#a)"' if arrows else "")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{width}"{d}{m}/>')


def rect(x, y, w, h, fill, stroke="none", opacity=1.0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{stroke}" fill-opacity="{opacity}"/>')


# ---------------------------------------------------------------------------
# timing-params.svg
# ---------------------------------------------------------------------------

T0, T1 = -4.5, 5.5          # ns shown
X0, X1 = 150, 630           # px
H_WAVE = 22


def tx(t):
    return X0 + (t - T0) / (T1 - T0) * (X1 - X0)


def clock(y, rise, label):
    """Clock with a rising edge at `rise` ns and an 8 ns period."""
    out = [text(X0 - 10, y + 16, label, anchor="end")]
    edges = sorted(e for k in range(-2, 3)
                   for e in (rise + 8 * k, rise + 8 * k + 4)
                   if T0 < e < T1)

    def ylev(t):
        return y if (t - rise) % 8 < 4 else y + H_WAVE

    pts, t = [], T0
    for e in edges:
        pts += [(tx(t), ylev(t)), (tx(e), ylev(t))]
        t = e
    pts += [(tx(t), ylev(t)), (tx(T1), ylev(t))]
    # Vertical segments come from consecutive points sharing x.
    out.append('<polyline fill="none" stroke="%s" stroke-width="1.6" '
               'points="%s"/>' % (CLOCK, " ".join(f"{a:.1f},{b:.1f}"
                                                  for a, b in pts)))
    return out


def bus(y, changes, names, label):
    """Data bus with transitions at the times in `changes` (ns)."""
    out = [text(X0 - 10, y + 16, label, anchor="end")]
    s = 0.15
    bounds = [T0] + list(changes) + [T1]
    for k in range(len(bounds) - 1):
        a, b = bounds[k], bounds[k + 1]
        la = tx(a) if k == 0 else tx(a + s)
        lb = tx(b) if k == len(bounds) - 2 else tx(b - s)
        ma = tx(a) if k == 0 else tx(a + 2 * s)
        mb = tx(b) if k == len(bounds) - 2 else tx(b - 2 * s)
        pts = [(la, y + H_WAVE / 2), (ma, y), (mb, y), (lb, y + H_WAVE / 2),
               (mb, y + H_WAVE), (ma, y + H_WAVE)]
        out.append('<polygon fill="%s" stroke="%s" stroke-width="1.2" '
                   'points="%s"/>' % (DATA_FILL, INK, " ".join(
                       f"{p:.1f},{q:.1f}" for p, q in pts)))
        if names[k]:
            out.append(text((tx(a) + tx(b)) / 2, y + 16, names[k],
                            anchor="middle", size=12))
    return out


def dim(t_a, t_b, y, label, above=True):
    """Dimension arrow from t_a to t_b with a label."""
    out = [line(tx(t_a), y, tx(t_b), y, arrows=True)]
    out.append(text((tx(t_a) + tx(t_b)) / 2, y + (-5 if above else 15),
                    label, anchor="middle", size=12))
    return out


def timing_params():
    w, h = 660, 590
    b = []
    # Panel A: no internal delay.
    b.append(text(10, 22, "Without internal delay: the board delays the clock",
                  weight="bold", size=14))
    y = 44
    b.append(text(10, y + 6, "At the transmitter pins", size=12, fill=GREY))
    y += 14
    b.append(line(tx(0), y - 4, tx(0), y + 60, stroke=GREY, dash="3,3"))
    b += clock(y, 0, "TXC")
    b += bus(y + 28, [-4, 0, 4], ["", "n0", "n1", ""], "TXD")
    for c in (-4, 0, 4):
        b.append(rect(tx(c - 0.5), y + 28, tx(c + 0.5) - tx(c - 0.5),
                      H_WAVE, ZONE, opacity=0.7))
    b += dim(-0.5, 0.5, y + 70, "TskewT: −0.5 to +0.5 ns", above=False)

    y = 160
    b.append(text(10, y + 6, "At the receiver pins", size=12, fill=GREY))
    y += 14
    b.append(line(tx(0), y - 4, tx(0), y + 60, stroke=GREY, dash="3,3"))
    b.append(rect(tx(1.0), y, tx(2.6) - tx(1.0), H_WAVE, ZONE))
    b += clock(y, 1.8, "RXC or TXC")
    b += bus(y + 28, [-4, 0, 4], ["", "n0", "n1", ""], "data")
    b += dim(0, 1.8, y + 70, "", above=False)
    b.append(text(tx(2.6) + 6, y + 74, "TskewR: 1.0 to 2.6 ns", size=12))

    # Panel B: internal delay.
    y0 = 300
    b.append(line(10, y0 - 16, w - 10, y0 - 16, stroke=GREY, width=0.8))
    b.append(text(10, y0 + 6,
                  "With internal delay (RGMII-ID): a chip delays the clock",
                  weight="bold", size=14))
    rows = ((y0 + 22, "At the transmitter pins, guaranteed", "TsetupT",
             "TholdT", 1.2, "TXC or RXC"),
            (y0 + 142, "At the receiver pins, required", "TsetupR",
             "TholdR", 1.0, "clock"))
    for y, title, su, ho, v, clk in rows:
        b.append(text(10, y + 6, title, size=12, fill=GREY))
        y += 14
        b.append(line(tx(0), y - 4, tx(0), y + 60, stroke=GREY, dash="3,3"))
        b += clock(y, 0, clk)
        b += bus(y + 28, [-2, 2], ["", "", ""], "data")
        b.append(rect(tx(-v), y + 28, tx(v) - tx(-v), H_WAVE, STABLE,
                      opacity=0.8))
        b.append(text(tx(0), y + 44, "stable", anchor="middle", size=11))
        b += dim(-v, 0, y + 70, "", above=False)
        b += dim(0, v, y + 70, "", above=False)
        b.append(text(tx(-v) - 6, y + 74, f"{su} ≥ {v:.1f} ns",
                      anchor="end", size=12))
        b.append(text(tx(v) + 6, y + 74, f"{ho} ≥ {v:.1f} ns", size=12))
    # Time axis.
    ya = h - 26
    b.append(line(X0, ya, X1, ya))
    for t in range(-4, 6):
        b.append(line(tx(t), ya, tx(t), ya + 5))
        b.append(text(tx(t), ya + 18, f"{t}", anchor="middle", size=11))
    b.append(text(X0 - 10, ya + 18, "time (ns)", anchor="end", size=12))
    return svg(w, h, b)


# ---------------------------------------------------------------------------
# timing-budget.svg
# ---------------------------------------------------------------------------

def timing_budget():
    w, h = 660, 230
    left, right = 90, 560
    tmax = 3.75

    def xp(v):
        return left + v / tmax * (right - left)

    b = []
    terms_s = [("Δtd", 0.2), ("tT", 0.5), ("tIO", 0.35), ("tB", 0.1),
               ("tsu", 0.5)]
    terms_h = [("td", 2.0), ("Δtd", 0.2), ("tT", 0.5), ("tIO", 0.35),
               ("tB", 0.1), ("th", 0.25)]
    colours = {"td": "#f2f2f2", "Δtd": "#fbe5d6", "tT": "#fff2cc",
               "tIO": "#e4dcef", "tB": "#dbe8f5", "tsu": "#f8cbad",
               "th": "#f8cbad"}
    rows = (("Setup", 2.0, "td = 2.0 ns", terms_s, 0.35, 40),
            ("Hold", 3.6, "thi = 3.6 ns", terms_h, 0.2, 130))
    for name, total, tlabel, terms, margin, y in rows:
        b.append(text(left - 10, y + 15, name, anchor="end", weight="bold"))
        b.append(rect(xp(0), y - 22, xp(total) - xp(0), 14, "#ffffff",
                      stroke=INK))
        b.append(text(xp(total / 2), y - 11, tlabel, anchor="middle",
                      size=11))
        t = 0.0
        for k, (n, v) in enumerate(terms):
            b.append(rect(xp(t), y, xp(t + v) - xp(t), 22, colours[n],
                          stroke=INK))
            yl = y + 37 if k % 2 == 0 else y + 51
            b.append(text((xp(t) + xp(t + v)) / 2, yl, n, anchor="middle",
                          size=11))
            t += v
        b.append(rect(xp(t), y, xp(t + margin) - xp(t), 22, "#a9d18e",
                      stroke=INK))
        b.append(text(xp(t + margin) + 6, y + 15,
                      f"margin {margin:g} ns", size=12, fill="#385723",
                      weight="bold"))
    ya = h - 34
    b.append(line(xp(0), ya, xp(tmax), ya))
    for k in range(0, 8):
        v = k * 0.5
        b.append(line(xp(v), ya, xp(v), ya + 5))
        b.append(text(xp(v), ya + 18, f"{v:g}", anchor="middle", size=11))
    b.append(text((left + right) / 2, ya + 32, "time (ns)", anchor="middle",
                  size=12))
    return svg(w, h, b)


# ---------------------------------------------------------------------------
# speed-change.svg
# ---------------------------------------------------------------------------

def speed_change():
    """TXC changing from 125 MHz to 25 MHz: a stretched phase is allowed,
    a glitch is not. Schematic stretch length; clock periods to scale."""
    w, h = 660, 250
    left, right, t_end = 150, 640, 120.0

    def xs(t):
        return left + t / t_end * (right - left)

    def wave(y, edges, start_high=True):
        lvl, t, pts = start_high, 0.0, []
        for e in edges + [t_end]:
            yy = y if lvl else y + 22
            pts += [(xs(t), yy), (xs(e), yy)]
            lvl, t = not lvl, e
        return ('<polyline fill="none" stroke="%s" stroke-width="1.6" '
                'points="%s"/>' % (CLOCK, " ".join(f"{a:.1f},{c:.1f}"
                                                  for a, c in pts)))

    fast = [4, 8, 12, 16, 20, 24]          # 125 MHz edges, ns
    stretch_end = 52                       # end of the stretched high phase
    slow = [stretch_end + 20 * k for k in range(1, 4) if
            stretch_end + 20 * k < t_end]
    good = fast + [stretch_end] + slow
    bad = fast + [30, 31.5] + [stretch_end] + slow
    b = []
    b.append(text(left - 10, 46, "TXC, allowed", anchor="end"))
    b.append(wave(30, good[:6] + [good[6]] + good[7:], True))
    b.append(text(left - 10, 106, "TXC, not allowed", anchor="end"))
    b.append(wave(90, bad, True))
    b.append(text(xs(31) + 16, 84, "glitch", size=12, fill=ACCENT,
                  weight="bold"))
    b.append(f'<circle cx="{xs(30.75):.1f}" cy="101" r="14" fill="none" '
             f'stroke="{ACCENT}" stroke-width="2"/>')
    b.append(text(left - 10, 162, "TX_CTL", anchor="end"))
    b.append(line(xs(0), 168, xs(t_end), 168, CLOCK, 1.6))
    # Phase labels.
    for t0, t1, lab in ((0, 24, "125 MHz"), (24, stretch_end,
                                             "stretched phase"),
                        (stretch_end, t_end, "25 MHz")):
        b.append(line(xs(t0), 190, xs(t1), 190, GREY, 0.8))
        b.append(line(xs(t0), 186, xs(t0), 194, GREY, 0.8))
        b.append(text((xs(t0) + xs(t1)) / 2, 206, lab, anchor="middle",
                      size=12, fill=GREY))
    ya = 222
    b.append(line(xs(0), ya, xs(t_end), ya))
    for t in range(0, 121, 20):
        b.append(line(xs(t), ya, xs(t), ya + 5))
        b.append(text(xs(t), ya + 18, f"{t}", anchor="middle", size=11))
    b.append(text(left - 10, ya + 18, "time (ns)", anchor="end", size=12))
    return svg(w, h + 12, b)


# ---------------------------------------------------------------------------
# frame.svg
# ---------------------------------------------------------------------------

def frame():
    """The fields of a frame in the order they are sent, with the optional
    VLAN tag. Widths are schematic, not to scale."""
    w, h = 660, 200
    fields = [("preamble", "7", 70, "#f2f2f2"), ("SFD", "1", 40, "#f2f2f2"),
              ("destination", "6", 80, "#dbe8f5"),
              ("source", "6", 70, "#dbe8f5"),
              ("VLAN tag", "4, optional", 80, "#ffffff"),
              ("length or type", "2", 90, "#dbe8f5"),
              ("payload", "46 to 1500", 120, "#e2f0d9"),
              ("FCS", "4", 50, "#fbe5d6")]
    x, y = 15, 75
    pos = {}
    b = []
    for name, size, wd, col in fields:
        dash = ' stroke-dasharray="4,3"' if "optional" in size else ""
        b.append(f'<rect x="{x}" y="{y}" width="{wd}" height="40" '
                 f'fill="{col}" stroke="{INK}"{dash}/>')
        b.append(text(x + wd / 2, y + 17, name, anchor="middle", size=11))
        b.append(text(x + wd / 2, y + 32, size, anchor="middle", size=10,
                      fill=GREY))
        pos[name] = (x, x + wd)
        x += wd
    b.append(text(15, y - 44, "bytes, in the order sent:", size=12,
                  fill=GREY))

    def bracket(x0, x1, yb, label, up):
        d = -8 if up else 8
        out = [line(x0, yb, x0, yb + d, INK, 1), line(x1, yb, x1, yb + d,
                                                      INK, 1),
               line(x0, yb + d, x1, yb + d, INK, 1)]
        out.append(text((x0 + x1) / 2, yb + d + (-6 if up else 15), label,
                        anchor="middle", size=11))
        return out

    b += bracket(pos["preamble"][0], pos["SFD"][1], y - 4,
                 "lets the receiver lock on", True)
    b += bracket(pos["destination"][0], pos["FCS"][1], y + 44,
                 "frame: 64 to 1518 bytes, 1522 with one VLAN tag, "
                 "at most 2000", False)
    b += bracket(pos["destination"][0], pos["payload"][1], y + 84,
                 "covered by the FCS", False)
    return svg(w, h, b)


if __name__ == "__main__":
    (HERE / "timing-params.svg").write_text(timing_params())
    (HERE / "timing-budget.svg").write_text(timing_budget())
    (HERE / "speed-change.svg").write_text(speed_change())
    (HERE / "frame.svg").write_text(frame())
