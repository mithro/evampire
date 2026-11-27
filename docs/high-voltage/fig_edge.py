"""Draw the curved-edge figure for the junctions page.

curved-edge.svg shows an N-well in a P substrate, in cross-section and in
plan view. The equipotentials in the cross-section are computed, not
sketched: the script solves Poisson's equation in the depletion
approximation for a well whose edge is a quarter circle of radius equal to
its depth. The depleted substrate holds a uniform negative charge, the well
is one equipotential, and the depletion edge is where the potential falls
to zero, found as an obstacle problem by projected over-relaxation. The
geometry is in grid cells, so the drawing is to its own scale but not tied
to a particular doping or voltage.

figures.py calls this module; it writes no files itself.

SPDX-License-Identifier: Apache-2.0
"""

import math

from svgdraw import (ARROW, BLUE, DEPL, GREY, INK, NWELL, SUB, line, path,
                     rect, svg, text)

NX, NY = 300, 112     # grid cells across and down
XM, D = 100, 22       # implant window edge and well depth, in cells
WP = 66               # depletion width under the flat bottom, in cells
CELL = 2              # pixels per cell
X0, Y0 = 20, 84       # pixel position of the cross-section's top left


def in_well(i, j):
    if i < XM:
        return j <= D
    return (i - XM) ** 2 + j ** 2 <= D * D


def solve():
    """Potential (1 at the well, 0 in the neutral substrate) on the grid."""
    c = 2.0 / WP ** 2          # charge term that gives WP under a flat bottom
    phi = [[0.0] * NY for _ in range(NX)]
    fixed = [[in_well(i, j) for j in range(NY)] for i in range(NX)]
    for i in range(NX):
        for j in range(NY):
            if fixed[i][j]:
                phi[i][j] = 1.0
            else:
                # Start from the flat-junction solution.
                dist = j - D if i < XM else math.hypot(i - XM, j) - D
                phi[i][j] = max(0.0, 1 - dist / WP) ** 2
    omega = 1.94
    for _ in range(1500):
        for i in range(NX - 1):
            col, left = phi[i], phi[i - 1] if i else phi[1]
            right, fx = phi[i + 1], fixed[i]
            for j in range(NY - 1):
                if fx[j]:
                    continue
                up = col[j - 1] if j else col[1]
                new = (left[j] + right[j] + up + col[j + 1] - c) / 4
                v = col[j] + omega * (new - col[j])
                col[j] = v if v > 0 else 0.0
    return phi


def contour(phi, level):
    """Marching squares: the lines, in pixels, where phi = level. The
    segments are chained into continuous lines so that a dash pattern runs
    along each line and does not restart in every cell."""
    point = {}     # grid edge the line crosses -> pixel position
    links = {}     # grid edge -> the edges its segments lead to

    for i in range(NX - 1):
        for j in range(NY - 1):
            corners = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            vals = [phi[a][b] for a, b in corners]
            edges = []
            for k in range(4):
                (a1, b1), (a2, b2) = corners[k], corners[(k + 1) % 4]
                v1, v2 = vals[k], vals[(k + 1) % 4]
                if (v1 - level) * (v2 - level) < 0:
                    t = (level - v1) / (v2 - v1)
                    edge = frozenset((corners[k], corners[(k + 1) % 4]))
                    point[edge] = (X0 + (a1 + t * (a2 - a1)) * CELL,
                                   Y0 + (b1 + t * (b2 - b1)) * CELL)
                    edges.append(edge)
            for a, b in zip(edges[::2], edges[1::2]):
                links.setdefault(a, []).append(b)
                links.setdefault(b, []).append(a)

    d, seen = "", set()
    # Open lines from their ends first, then any closed loops.
    starts = [e for e in links if len(links[e]) == 1] + list(links)
    for edge in starts:
        chain = []
        while edge is not None and edge not in seen:
            seen.add(edge)
            chain.append(point[edge])
            edge = next((n for n in links[edge] if n not in seen), None)
        if len(chain) > 1:
            d += "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in chain)
    return d


def section(phi):
    b = []
    w, h = NX * CELL, (NY - 1) * CELL
    b.append(rect(X0, Y0, w, h, SUB, stroke="none"))
    well = (f"M{X0},{Y0} L{X0 + XM * CELL},{Y0} "
            f"L{X0 + (XM + D) * CELL},{Y0} "
            f"A{D * CELL},{D * CELL} 0 0 1 {X0 + XM * CELL},"
            f"{Y0 + D * CELL} L{X0},{Y0 + D * CELL} Z")
    b.append(f'<path d="{well}" fill="{NWELL}" stroke="{INK}" '
             'stroke-width="1.5"/>')
    for lev in (0.8, 0.6, 0.4, 0.2):
        b.append(path(contour(phi, lev), stroke=BLUE, dash=None, width=1.3))
    b.append(path(contour(phi, 0.004), stroke=DEPL, dash="6 4", width=1.8))
    b.append(rect(X0, Y0, w, h, "none"))
    # The implant enters through the window and spreads down and sideways.
    xm = X0 + XM * CELL
    for x in range(X0 + 30, xm, 50):
        b.append(line(x, Y0 - 26, x, Y0 - 4, marker=True, width=1.2))
    b.append(text(X0 + 4, Y0 - 32, "implant through the drawn window",
                  anchor="start", size=15))
    b.append(line(xm, Y0 - 30, xm, Y0 + 2, stroke=GREY, dash="3 3", width=1))
    b.append(line(xm + 2, Y0 - 10, xm + D * CELL + 4, Y0 - 10, marker=True,
                  width=1.2))
    b.append(text(xm + D * CELL + 10, Y0 - 6, "and spreads sideways",
                  anchor="start", size=15))
    b.append(text(X0 + 90, Y0 + 38, "N-well, at +V", size=16,
                  weight="bold"))
    b.append(text(X0 + w - 8, Y0 + h - 12, "P substrate, 0 V",
                  anchor="end", size=16))
    # Where the field is highest, and where it is even.
    px = X0 + (XM + D * 0.71) * CELL
    py = Y0 + D * 0.71 * CELL
    b.append(f'<circle cx="{px}" cy="{py}" r="7" fill="none" '
             f'stroke="{DEPL}" stroke-width="2.5"/>')
    b.append(line(px + 112, py + 46, px + 7, py + 5, marker=True, width=1.2))
    b.append(text(px + 116, py + 50, "lines crowd at the curved edge:",
                  anchor="start", size=15))
    b.append(text(px + 116, py + 66, "the field reaches its critical",
                  anchor="start", size=15))
    b.append(text(px + 116, py + 82, "value here first",
                  anchor="start", size=15))
    b.append(text(X0 + 8, Y0 + (D + WP) * CELL + 22,
                  "under the flat bottom the lines lie further apart: "
                  "a lower field", anchor="start", size=15))
    return b


def plan(y0):
    b = [text(X0, y0 - 14, "Plan view", anchor="start", size=14,
              weight="bold")]
    x1, y1, x2, y2, r = 80, y0 + 30, 300, y0 + 150, 26
    b.append(rect(x1 - r, y1 - r, x2 - x1 + 2 * r, y2 - y1 + 2 * r, NWELL,
                  rx=r))
    b.append(rect(x1, y1, x2 - x1, y2 - y1, "none", stroke=GREY, dash="4 3"))
    b.append(text((x1 + x2) / 2, (y1 + y2) / 2 - 8, "drawn window",
                  size=12, fill=GREY))
    b.append(text((x1 + x2) / 2, (y1 + y2) / 2 + 10, "(dashed)",
                  size=12, fill=GREY))
    # Section line through the middle of the right-hand side.
    ys = (y1 + y2) / 2 + 40
    b.append(line((x1 + x2) / 2, ys, x2 + r + 30, ys, stroke=INK,
                  dash="8 3 2 3",
                  width=1.2))
    b.append(text((x1 + x2) / 2 - 6, ys + 4, "A", anchor="end", size=13,
                  weight="bold"))
    b.append(text(x2 + r + 34, ys + 4, "A′", anchor="start", size=13,
                  weight="bold"))
    # Labels for a straight side and a corner.
    b.append(line(x2 + r + 70, y1 + 22, x2 + r + 3, y1 + 22, marker=True,
                  width=1.2))
    b.append(text(x2 + r + 74, y1 + 26, "straight side: cylindrical edge",
                  anchor="start", size=13))
    cx, cy = x2 + r * 0.71, y1 - r * 0.71
    b.append(line(x2 + r + 70, y1 - 22, cx + 3, cy - 2, marker=True,
                  width=1.2))
    b.append(text(x2 + r + 74, y1 - 18, "corner: spherical edge",
                  anchor="start", size=13))
    # Breakdown for a 1 um edge radius at 1e15 cm^-3, from the page's tables.
    tx = x2 + r + 74
    b.append(text(tx, y0 + 96, "Breakdown, edge radius 1 µm,",
                  anchor="start", size=13, weight="bold"))
    b.append(text(tx, y0 + 113, "substrate 10¹⁵ cm⁻³:",
                  anchor="start", size=13, weight="bold"))
    rows = (("flat bottom", "300 V"), ("straight side", "74 V"),
            ("corner", "35 V"))
    for k, (name, v) in enumerate(rows):
        b.append(text(tx + 8, y0 + 134 + k * 19, name, anchor="start",
                      size=13))
        b.append(text(tx + 190, y0 + 134 + k * 19, v, anchor="end",
                      size=13))
    return b


def curved_edge():
    w, h = 640, Y0 + NY * CELL + 50 + 190
    body = [ARROW]
    body.append(text(X0, 22, "Section A–A′", anchor="start", size=14,
                     weight="bold"))
    body.append(line(360, 12, 384, 12, stroke=BLUE, width=1.3))
    body.append(text(390, 17, "equipotentials, 20 % of V apart",
                     anchor="start", size=13))
    body.append(path("M360,30 L384,30", dash="6 4"))
    body.append(text(390, 35, "edge of the depletion region",
                     anchor="start", size=13))
    body += section(solve())
    body += plan(Y0 + NY * CELL + 50)
    return svg(w, h, body)


FIGURES = {"curved-edge.svg": curved_edge}
