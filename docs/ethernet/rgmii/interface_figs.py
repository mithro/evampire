"""Interface figures for the RGMII pages: frame and levels. Called from
figures.py.

SPDX-License-Identifier: Apache-2.0
"""

from svgkit import (INK, GREY, svg, text, line, rect)


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


# ---------------------------------------------------------------------------
# levels.svg
# ---------------------------------------------------------------------------

def levels():
    """Output and input levels of RGMII 1.3 and of two transceivers with a
    3.3 V I/O supply, from electrical.rst."""
    w, h = 660, 360
    top, bot, vmax = 40, 300, 3.5

    def yv(v):
        return bot - v / vmax * (bot - top)

    b = []
    b.append(line(70, top, 70, bot))
    for v in (0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5):
        b.append(line(65, yv(v), 70, yv(v)))
        b.append(text(60, yv(v) + 4, f"{v:g}", anchor="end", size=11))
        b.append(line(70, yv(v), 640, yv(v), "#eeeeee", 0.8))
    b.append(f'<text x="22" y="{(top + bot) / 2:.0f}" text-anchor="middle" '
             f'font-size="12" fill="{INK}" transform="rotate(-90 22 '
             f'{(top + bot) / 2:.0f})">voltage (V)</text>')
    cols = (("RGMII 1.3", "2.5 V levels", 2.5, (0.40, 2.0), (0.70, 1.7)),
            ("DP83867", "3.3 V supply", 3.3, (0.6, 2.0), (0.7, 1.7)),
            ("KSZ9031RNX", "3.3 V supply", 3.3, None, (1.3, 2.0)))
    x0 = 100
    for name, sub, vdd, out, inp in cols:
        b.append(text(x0 + 85, top - 20, name, anchor="middle", size=12,
                      weight="bold"))
        b.append(text(x0 + 85, top - 6, sub, anchor="middle", size=11,
                      fill=GREY))
        for k, (lab, pair) in enumerate((("outputs", out), ("inputs", inp))):
            xb = x0 + 20 + 90 * k
            b.append(text(xb + 30, bot + 16, lab, anchor="middle", size=11))
            if pair is None:
                b.append(text(xb + 30, yv(1.5), "not", anchor="middle",
                              size=11, fill=GREY))
                b.append(text(xb + 30, yv(1.5) + 14, "used here",
                              anchor="middle", size=11, fill=GREY))
                continue
            lo, hi = pair
            hi_col, lo_col = ("#a9d18e", "#a9d18e") if k == 0 else (
                "#dbe8f5", "#dbe8f5")
            b.append(rect(xb, yv(vdd), 60, yv(hi) - yv(vdd), hi_col, INK))
            b.append(rect(xb, yv(lo), 60, yv(0) - yv(lo), lo_col, INK))
            b.append(rect(xb, yv(hi), 60, yv(lo) - yv(hi), "#f2f2f2", INK))
            hn = "VOH" if k == 0 else "VIH"
            ln = "VOL" if k == 0 else "VIL"
            b.append(text(xb + 30, yv(hi) - 5, f"{hn} {hi:g}",
                          anchor="middle", size=10))
            b.append(text(xb + 30, yv(lo) + 13, f"{ln} {lo:g}",
                          anchor="middle", size=10))
        x0 += 180
    b.append(text(100, bot + 40, "green: guaranteed output levels; blue: "
                  "levels read as high or low; grey: undefined", size=11,
                  fill=GREY))
    return svg(w, h, b)
