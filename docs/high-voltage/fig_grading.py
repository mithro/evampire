"""Draw the figures for the grading page, apart from grading.svg.

even-fall.svg      the potential and field of an abrupt and an even fall.
rings-steps.svg    floating rings taking the voltage in steps, with the
                   surface potential below.
plate-variants.svg field plates on thin, thick and stepped insulator.
substrate-slab.svg a slab of substrate graded by a current.
floating-well.svg  a half-bridge gate driver with a floating well.

The drawings are schematic. figures.py calls this module; it writes no
files itself.

SPDX-License-Identifier: Apache-2.0
"""

from svgdraw import (ARROW, BLUE, DEPL, FOX, GREY, INK, METAL, NWELL, OXIDE,
                     POLY, PPLUS, SUB, line, path, polyline, rect, svg,
                     text)


def even_fall():
    """Potential and field against distance for an abrupt and an even fall."""
    w, h = 640, 330
    body = [ARROW]
    for k, (title, pot, fld, lab) in enumerate((
            ("Abrupt fall", [(0, 1), (0.42, 1), (0.5, 0), (1, 0)],
             [(0, 0), (0.42, 0), (0.42, 1), (0.5, 1), (0.5, 0), (1, 0)],
             "field peaked at one edge"),
            ("Even fall over L", [(0, 1), (0.1, 1), (0.9, 0), (1, 0)],
             [(0, 0), (0.1, 0), (0.1, 0.125), (0.9, 0.125), (0.9, 0),
              (1, 0)], "field V/L everywhere"))):
        ox = 50 + k * 300
        body.append(text(ox + 120, 22, title, size=14, weight="bold"))
        for j, (pts, name, col, top) in enumerate((
                (pot, "potential", BLUE, 40), (fld, "field", DEPL, 180))):
            x0, y0, pw, ph = ox, top, 240, 110
            body.append(line(x0, y0 + ph, x0 + pw, y0 + ph, width=1))
            body.append(line(x0, y0, x0, y0 + ph, width=1))
            body.append(text(x0 - 8, y0 + ph / 2, name, size=12,
                             rotate=-90))
            body.append(polyline([(x0 + pw * x, y0 + ph * (1 - 0.85 * y))
                                  for x, y in pts], stroke=col, width=2.5))
        body.append(text(ox + 120, 310, "distance along the surface", size=12))
        body.append(text(ox - 4, 64, "V", anchor="end", size=12))
        body.append(text(ox + 236, 168, "0", anchor="end", size=12))
        body.append(text(ox + 132 if k == 0 else ox + 120,
                         206 if k == 0 else 254, lab,
                         anchor="start" if k == 0 else "middle", size=12,
                         fill=DEPL))
    xl0, xl1 = 50 + 300 + 24, 50 + 300 + 216
    body.append(line(xl0, 158, xl1, 158, width=1, marker=True, start=True))
    body.append(text((xl0 + xl1) / 2, 172, "L", size=13, style="italic"))
    return svg(w, h, body)


def rings_steps():
    """Rings taking the voltage in steps, and the surface potential."""
    w, h = 640, 440
    body = [ARROW]
    top = 90
    body.append(rect(20, top, 600, 150, SUB))
    body.append(rect(20, top, 110, 60, NWELL, rx=10))
    body.append(text(70, top + 36, "well, V", size=13, weight="bold"))
    xs = (190, 290, 390, 490)
    for k, x in enumerate(xs):
        body.append(rect(x, top, 30, 34, NWELL, rx=6))
        body.append(text(x + 15, top - 8, f"ring {k + 1}", size=12))
    body.append(rect(580, top, 34, 16, PPLUS))
    body.append(text(597, top - 8, "0 V", size=12))
    # Depletion edges at a lower and a higher voltage.
    body.append(path(f"M20,{top + 105} Q120,{top + 110} 150,{top + 70} "
                     f"Q175,{top + 40} 190,{top + 20}", dash="4 3",
                     stroke=GREY))
    body.append(path(f"M20,{top + 135} Q140,{top + 140} 205,{top + 70} "
                     f"Q240,{top + 60} 280,{top + 60} Q300,{top + 55} "
                     f"305,{top + 40} Q330,{top + 30} 345,{top}"))
    body.append(text(250, top + 118, "edge at a lower voltage: reaches "
                     "ring 1", anchor="start", size=12, fill=GREY))
    body.append(text(250, top + 136, "at a higher voltage: spreads on from "
                     "ring 1 to ring 2", anchor="start", size=12, fill=DEPL))
    body.append(line(130, top - 16, 190, top - 16, width=1, marker=True,
                     start=True))
    body.append(line(130, top - 22, 130, top, width=1, stroke=GREY))
    body.append(text(140, top - 50, "≈ ⅓ of the flat", size=11))
    body.append(text(140, top - 36, "depletion width", size=11))
    # Surface potential: a staircase.
    y0, y1 = 290, 410
    body.append(line(20, y1, 620, y1, width=1))
    body.append(line(20, y0 - 10, 20, y1, width=1))
    body.append(text(12, (y0 + y1) / 2, "surface potential", size=12,
                     rotate=-90))
    levels = (1.0, 0.78, 0.56, 0.36, 0.17, 0.0)
    pts, xe = [], [130] + [x + 30 for x in xs] + [620]
    starts = [20] + list(xs) + [580]
    for k, v in enumerate(levels):
        y = y1 - (y1 - y0) * v
        pts += [(starts[k], y), (xe[k] if k < 5 else 620, y)]
    body.append(polyline(pts, stroke=BLUE, width=2.5))
    body.append(text(26, y0 - 4, "V", anchor="start", size=12))
    for k, x in enumerate(xs):
        y = y1 - (y1 - y0) * levels[k + 1]
        body.append(text(x + 15, y - 6, f"V − ΔV{'₁₂₃₄'[k]}", size=11))
    body.append(text(400, 22, "each ring sits a fixed step below the one "
                     "inside it", size=13))
    return svg(w, h, body)


def plate_panel(ox, title, kind):
    b = [text(ox + 100, 20, title, size=13, weight="bold")]
    top = 80
    b.append(rect(ox, top, 200, 130, SUB))
    b.append(rect(ox, top, 60, 40, NWELL, rx=8))
    b.append(text(ox + 28, top + 26, "well", size=12))
    if kind == "thin":
        b.append(rect(ox + 40, top - 8, 130, 8, OXIDE))
        b.append(rect(ox + 40, top - 18, 110, 10, METAL))
        b.append(path(f"M{ox},{top + 85} Q{ox + 110},{top + 85} {ox + 150},"
                      f"{top + 30} Q{ox + 160},{top + 10} {ox + 165},{top}"))
        bx, by = ox + 150, top + 2
        note = "breaks down at the plate's end"
    elif kind == "thick":
        b.append(rect(ox + 40, top - 40, 130, 40, OXIDE))
        b.append(rect(ox + 40, top - 50, 110, 10, METAL))
        b.append(path(f"M{ox},{top + 80} Q{ox + 90},{top + 80} {ox + 100},"
                      f"{top + 30} Q{ox + 105},{top + 10} {ox + 110},{top}"))
        bx, by = ox + 60, top + 32
        note = "breaks down at the junction"
    else:
        b.append(rect(ox + 40, top - 14, 150, 14, FOX))
        b.append(rect(ox + 40, top - 50, 150, 36, OXIDE))
        b.append(rect(ox + 40, top - 22, 60, 8, POLY))
        b.append(rect(ox + 40, top - 36, 100, 8, METAL))
        b.append(rect(ox + 40, top - 50, 140, 8, METAL))
        b.append(path(f"M{ox},{top + 90} Q{ox + 120},{top + 92} {ox + 170},"
                      f"{top + 30} Q{ox + 180},{top + 10} {ox + 185},{top}"))
        bx, by = None, None
        note = "field shared between the steps"
    if bx:
        b.append(f'<circle cx="{bx}" cy="{by}" r="7" fill="none" '
                 f'stroke="{DEPL}" stroke-width="2.5"/>')
    b.append(text(ox + 100, top + 150, note, size=12, fill=DEPL))
    return b


def plate_variants():
    w, h = 660, 250
    body = [ARROW]
    body += plate_panel(10, "Thin insulator", "thin")
    body += plate_panel(230, "Thick insulator", "thick")
    body += plate_panel(450, "Stepped plate", "stepped")
    body.append(text(560, 245, "polysilicon, then each metal layer",
                     size=11, fill=GREY))
    return svg(w, h, body)


def substrate_slab():
    w, h = 640, 300
    body = [ARROW]
    body.append('<defs><linearGradient id="fall" x1="0" x2="1" y1="0" '
                'y2="0"><stop offset="0" stop-color="#f5b46e"/>'
                f'<stop offset="1" stop-color="{SUB}"/></linearGradient>'
                '</defs>')
    x0, y0, ln, th, dp = 110, 120, 420, 60, 60
    body.append(f'<path d="M{x0},{y0} L{x0 + dp},{y0 - dp * 0.6} '
                f'L{x0 + ln + dp},{y0 - dp * 0.6} L{x0 + ln},{y0} Z" '
                f'fill="url(#fall)" stroke="{INK}"/>')
    body.append(f'<path d="M{x0 + ln},{y0} L{x0 + ln + dp},{y0 - dp * 0.6} '
                f'L{x0 + ln + dp},{y0 - dp * 0.6 + th} L{x0 + ln},{y0 + th} '
                f'Z" fill="{SUB}" stroke="{INK}"/>')
    body.append(f'<rect x="{x0}" y="{y0}" width="{ln}" height="{th}" '
                f'fill="url(#fall)" stroke="{INK}"/>')
    for x in (x0 - 14, x0 + ln):
        body.append(rect(x, y0, 14, th, METAL))
    body.append(text(x0 - 20, y0 + 36, "57 V", anchor="end", size=14,
                     weight="bold"))
    body.append(text(x0 + ln + dp + 10, y0 + 6, "0 V", anchor="start",
                     size=14, weight="bold"))
    body.append(line(x0, y0 + th + 24, x0 + ln, y0 + th + 24, width=1,
                     marker=True, start=True))
    body.append(text(x0 + ln / 2, y0 + th + 40, "1 mm long, 1 mm wide, "
                     "300 µm thick: the voltage falls evenly along it",
                     size=13))
    body.append(text(320, 30, "P-type silicon at 10¹⁵ cm⁻³, about 14 Ω·cm",
                     size=13))
    body.append(text(320, 250, "about 450 Ω between the contacts: 130 mA "
                     "and 7 W at 57 V", size=14, weight="bold"))
    return svg(w, h, body)


def floating_well():
    w, h = 640, 380
    body = [ARROW]
    top = 150
    body.append(rect(20, top, 360, 170, SUB))
    body.append(text(200, top + 158, "P substrate, 0 V", size=13))
    body.append(rect(40, top, 120, 50, NWELL, rx=8))
    body.append(text(100, top + 30, "low-side circuits", size=12))
    body.append(rect(200, top, 160, 90, NWELL, rx=14))
    body.append(text(280, top + 30, "high-side circuits", size=12))
    body.append(text(280, top + 48, "in a floating", size=12))
    body.append(text(280, top + 64, "N-type tub", size=12))
    body.append(path(f"M190,{top} L190,{top + 92} Q190,{top + 102} 204,"
                     f"{top + 102} L356,{top + 102} Q370,{top + 102} 370,"
                     f"{top + 92} L370,{top}", stroke=DEPL, dash="5 3",
                     width=2))
    body.append(text(280, top + 122, "its junction to the substrate",
                     size=11, fill=DEPL))
    body.append(text(280, top + 136, "holds up to 500 V or 1200 V",
                     size=11, fill=DEPL))
    # Half bridge outside the die.
    xb = 520
    body.append(line(xb, 40, xb, 340, width=1.5))
    body.append(text(xb, 30, "bus, hundreds of volts", size=12))
    for y, name in ((110, "high-side switch"), (250, "low-side switch")):
        body.append(rect(xb - 22, y - 26, 44, 52, "#e2f0d9"))
        body.append(text(xb + 28, y + 4, name, anchor="start", size=11))
    body.append(text(xb, 356, "0 V", size=12))
    body.append(f'<circle cx="{xb}" cy="180" r="4" fill="{INK}"/>')
    body.append(text(xb + 8, 184, "switching node", anchor="start",
                     size=11))
    body.append(polyline([(xb, 180), (420, 180), (420, top + 20),
                          (360, top + 20)], width=1.5))
    body.append(polyline([(300, top), (300, 110), (xb - 22, 110)],
                         width=1.5))
    body.append(text(400, 104, "gate drive", size=11))
    body.append(polyline([(100, top), (100, 64), (460, 64), (460, 250),
                          (xb - 22, 250)], width=1.5))
    body.append(text(xb + 8, 200, "the tub follows it,", anchor="start",
                     size=11))
    body.append(text(xb + 8, 214, "down to −5 V", anchor="start", size=11))
    return svg(w, h, body)


FIGURES = {"even-fall.svg": even_fall, "rings-steps.svg": rings_steps,
           "plate-variants.svg": plate_variants,
           "substrate-slab.svg": substrate_slab,
           "floating-well.svg": floating_well}
