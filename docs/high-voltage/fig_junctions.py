"""Draw the depletion-region figure for the junctions page.

depletion.svg shows a one-sided abrupt N+/P junction at breakdown, for
P-side doping of 1e15 cm^-3: the structure, the fixed charge, the field and
the potential, on one distance axis. The P side is drawn to scale from the
page's numbers (W_B = 20 um, V_B = 300 V, critical field 3e5 V/cm). The N+
side is far thinner in reality, so it is drawn wider than scale.

figures.py calls this module; it writes no files itself.

SPDX-License-Identifier: Apache-2.0
"""

from svgdraw import (ARROW, DEPL, FIELD_FILL, GREY, INK, METAL, NPLUS, SUB,
                     BLUE, line, path, polyline, rect, sub, svg, text)

XL = 100           # left end of the N+ region
XJ = 180           # the junction
XN = 172           # N+ side edge of the depletion region (schematic)
S = 16             # pixels per micrometre on the P side
WB = 20.0          # depletion width at breakdown (um)
VB = 300.0         # breakdown voltage (V)
XR = XJ + 26 * S   # right end of the drawing
XW = XJ + WB * S   # P side edge of the depletion region


def structure(y0):
    """Panel (a): the junction in cross-section, y0 is the top of the
    silicon."""
    h = 70
    b = [text(10, y0 - 22, "(a) Cross-section at breakdown", anchor="start",
              weight="bold")]
    b.append(rect(XL, y0, XJ - XL, h, NPLUS))
    b.append(rect(XJ, y0, XR - XJ, h, SUB))
    # The depletion region: emptied of free carriers, so drawn paler.
    b.append(rect(XN, y0, XW - XN, h, "white", stroke="none", opacity=0.6))
    b.append(rect(XN, y0, XW - XN, h, "none", stroke=DEPL, dash="6 4"))
    # Fixed ions left behind: donors (+) on the N+ side, acceptors (-) on
    # the P side.
    for k in range(6):
        b.append(text(XN + 4, y0 + 13 + k * 10.5, "+", size=11,
                      weight="bold"))
    for col in range(8):
        for row in range(3):
            b.append(text(XJ + 24 + col * 40, y0 + 20 + row * 20, "−",
                          size=15, weight="bold"))
    b.append(text((XL + XN) / 2, y0 + 41, "N+", size=15, weight="bold"))
    b.append(text((XW + XR) / 2, y0 + 32, "neutral P", size=13))
    b.append(text((XW + XR) / 2, y0 + 50, "N = 10¹⁵ cm⁻³", size=12))
    b.append(text((XN + XW) / 2, y0 - 6,
                  "depletion region: no free carriers, only fixed ions",
                  size=13))
    # Contacts and the reverse bias.
    b.append(rect(XL - 8, y0, 8, h, METAL))
    b.append(rect(XR, y0, 8, h, METAL))
    b.append(text(XL - 4, y0 - 6, "+300 V", anchor="end", size=13,
                  weight="bold"))
    b.append(text(XR + 8, y0 - 6, "0 V", anchor="end", size=13,
                  weight="bold"))
    b.append(text((XL + XJ) / 2, y0 + h + 18, "heavily doped", size=12))
    ya = y0 + h + 14
    b.append(line(XJ + 2, ya, XW - 2, ya, marker=True, start=True,
                  width=1.2))
    b.append(text((XJ + XW) / 2, ya + 16, sub("W", "B") + "= 20 µm",
                  size=13))
    return b


def axis(y0, label):
    """The zero line and the rotated quantity label of one plot panel."""
    return [line(XL - 8, y0, XR, y0, stroke=INK, width=1),
            text(66, y0 - 40, label, rotate=-90, size=13)]


def charge(y0):
    """Panel (b): the fixed charge density."""
    b = [text(10, y0 - 70, "(b) Fixed charge", anchor="start",
              weight="bold")]
    # Donor charge on the N+ side: a thin, very tall block, cut short.
    top = y0 - 58
    b.append(f'<path d="M{XN},{y0} L{XN},{top} L{XJ},{top - 5} L{XJ},{y0} Z" '
             f'fill="{NPLUS}" stroke="{INK}"/>')
    b.append(text(XN - 6, top + 10, "+q" + sub("N", "D"), anchor="end",
                  size=13))
    b.append(text(XN - 6, top + 28, "(off scale)", anchor="end", size=11))
    # Acceptor charge on the P side: wide and shallow.
    b.append(rect(XJ, y0, XW - XJ, 14, SUB))
    b.append(text((XJ + XW) / 2, y0 + 30,
                  "−qN = −1.6 × 10⁻⁴ C/cm³ over the whole 20 µm", size=13))
    b.append(text(XJ + 14, y0 - 22, "equal total charge, opposite sign",
                  anchor="start", size=13))
    b += axis(y0, "ρ (C/cm³)")
    b.append(text(XR - 2, y0 - 6, "0", anchor="end", size=12, fill=GREY))
    return b


def field(y0):
    """Panel (c): the field, a triangle whose area is the voltage."""
    hmax = 100
    b = [text(10, y0 - hmax - 26, "(c) Electric field", anchor="start",
              weight="bold")]
    b.append(f'<path d="M{XN},{y0} L{XJ},{y0 - hmax} L{XW},{y0} Z" '
             f'fill="{FIELD_FILL}" stroke="{DEPL}" stroke-width="2"/>')
    b.append(line(XL - 8, y0 - hmax, XR, y0 - hmax, stroke=DEPL, dash="5 4",
                  width=1.2))
    b.append(text(XR, y0 - hmax - 7, "critical field, about 3 × 10⁵ V/cm",
                  anchor="end", size=13, fill=DEPL))
    b.append(line(XJ + 116, y0 - hmax + 12, XJ + 4, y0 - hmax + 2,
                  width=1, marker=True))
    b.append(text(XJ + 120, y0 - hmax + 16,
                  "peak, at the junction: avalanche", anchor="start",
                  size=13))
    b.append(text(XJ + 120, y0 - hmax + 32, "when it reaches the critical "
                  "field", anchor="start", size=13))
    b.append(text(XJ + 24, y0 - 14, "area under the line = 300 V",
                  anchor="start", size=13, weight="bold"))
    b += axis(y0, "E (V/cm)")
    return b


def potential(y0):
    """Panel (d): the potential, which falls as a parabola across the
    depletion region and is flat outside it."""
    hv = 90
    b = [text(10, y0 - hv - 26, "(d) Potential", anchor="start",
              weight="bold")]
    pts = [(XL, y0 - hv), (XN, y0 - hv)]
    for k in range(41):
        x = WB * k / 40
        v = VB * (1 - x / WB) ** 2
        pts.append((XJ + x * S, y0 - hv * v / VB))
    pts.append((XR, y0))
    b.append(polyline(pts, stroke=BLUE, width=2.5))
    b.append(text(XL + 4, y0 - hv - 7, "300 V", anchor="start", size=13))
    b.append(text(XJ + 150, y0 - hv + 18,
                  "all 300 V falls across the depletion region",
                  anchor="start", size=13))
    b.append(text(XR, y0 - 8, "0 V", anchor="end", size=13))
    b += axis(y0, "V (V)")
    return b


def depletion():
    w, h = 640, 660
    body = [ARROW]
    body += structure(60)
    body += charge(250)
    body += field(420)
    body += potential(570)
    # The junction and the depletion edge, through every panel.
    body.append(line(XJ, 60, XJ, 600, stroke=GREY, dash="2 4", width=1))
    body.append(line(XW, 60, XW, 250, stroke=GREY, dash="2 4", width=1))
    # Distance axis, drawn to scale on the P side only.
    ya = 600
    body.append(line(XJ, ya, XR, ya, width=1))
    for um in range(0, 26, 5):
        x = XJ + um * S
        body.append(line(x, ya, x, ya + 5, width=1))
        body.append(text(x, ya + 19, str(um), size=12))
    body.append(text((XJ + XR) / 2, ya + 40,
                     "distance into the P side, x (µm)", size=13))
    body.append(path(f"M{XL},{ya} L{XJ},{ya}", stroke=GREY, dash="2 3",
                     width=1))
    body.append(text(XJ - 12, ya + 19, "N+, not to scale", anchor="end",
                     size=11, fill=GREY))
    return svg(w, h, body)


FIGURES = {"depletion.svg": depletion}
