"""Draw the Power over Ethernet start-up voltage timeline as an SVG file.

The figure shows the voltage at the powered device input while a Type 3
power source detects it, runs four class events (granting class 6) and then
turns the power on. The time axis is not to scale; durations are written on
the figure instead.

Usage: python voltage_timeline.py OUTPUT.svg

SPDX-License-Identifier: Apache-2.0
"""

import sys

W, H = 960, 470
X0, X1 = 80, 800          # plot area, left and right
Y0, Y1 = 40, 400          # plot area, top and bottom
VMAX = 60.0

# (label, relative duration, voltage) for each flat segment of the waveform.
SEGMENTS = [
    ("", 1.0, 0.0),
    ("detect", 1.3, 4.0),
    ("detect", 1.3, 8.0),
    ("class 1\n88–105 ms", 2.2, 17.5),
    ("mark", 1.0, 8.5),
    ("class 2", 1.3, 17.5),
    ("mark", 1.0, 8.5),
    ("class 3", 1.3, 17.5),
    ("mark", 1.0, 8.5),
    ("class 4", 1.3, 17.5),
    ("mark", 1.0, 8.5),
]
RAMP = 0.5                # rise from the last mark event to full voltage
POWERED = [("inrush\n50–75 ms", 2.2), ("power delay\nto 80 ms", 2.0),
           ("full power", 1.7)]
V_ON = 54.0

BANDS = [
    # (low V, high V, fill colour, label)
    (2.7, 10.1, "#dbe8f5", "detection 2.7–10.1 V\nmark 6.9–10.1 V"),
    (14.5, 20.5, "#e2f0d9", "classification\n14.5–20.5 V"),
    (30.0, 42.0, "#fbe5d6", "turn on between\n30 and 42 V"),
    (42.5, 57.0, "#ececec", "operating\nup to 57 V"),
]


def ty(v):
    return Y1 - (Y1 - Y0) * v / VMAX


def text(x, y, s, size=12, anchor="middle", weight="normal", fill="#222"):
    lines = s.split("\n")
    out = []
    for i, line in enumerate(lines):
        dy = (i - (len(lines) - 1) / 2) * (size + 2)
        out.append(
            f'<text x="{x:.1f}" y="{y + dy:.1f}" font-size="{size}" '
            f'text-anchor="{anchor}" font-weight="{weight}" fill="{fill}" '
            f'dominant-baseline="middle">{line}</text>')
    return "\n".join(out)


def main(out_path):
    total = (sum(d for _, d, _ in SEGMENTS) + RAMP
             + sum(d for _, d in POWERED))
    scale = (X1 - X0) / total
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">',
        f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
    ]

    # Voltage bands with their labels on the right.
    for lo, hi, fill, label in BANDS:
        parts.append(f'<rect x="{X0}" y="{ty(hi):.1f}" width="{X1 - X0}" '
                     f'height="{ty(lo) - ty(hi):.1f}" fill="{fill}"/>')
        parts.append(text(X1 + 8, (ty(lo) + ty(hi)) / 2, label, size=11,
                          anchor="start", fill="#444"))

    # Axes and voltage ticks.
    parts.append(f'<line x1="{X0}" y1="{Y1}" x2="{X1}" y2="{Y1}" '
                 'stroke="#222" stroke-width="1.2"/>')
    parts.append(f'<line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y1}" '
                 'stroke="#222" stroke-width="1.2"/>')
    for v in range(0, 61, 10):
        parts.append(f'<line x1="{X0 - 5}" y1="{ty(v):.1f}" x2="{X0}" '
                     f'y2="{ty(v):.1f}" stroke="#222"/>')
        parts.append(text(X0 - 9, ty(v), f"{v}", size=11, anchor="end"))
    parts.append(f'<text x="24" y="{(Y0 + Y1) / 2}" font-size="12" '
                 'text-anchor="middle" transform="rotate(-90 24 '
                 f'{(Y0 + Y1) / 2})">Voltage at powered device input (V)'
                 '</text>')
    parts.append(text((X0 + X1) / 2, H - 14,
                      "time (not to scale)", size=12))

    # Waveform.
    pts = []
    x = X0
    seg_spans = []
    for label, d, v in SEGMENTS:
        x2 = x + d * scale
        pts += [(x, ty(v)), (x2, ty(v))]
        seg_spans.append((label, x, x2, v))
        x = x2
    x_ramp_end = x + RAMP * scale
    pts.append((x_ramp_end, ty(V_ON)))
    x = x_ramp_end
    power_spans = []
    for label, d in POWERED:
        x2 = x + d * scale
        power_spans.append((label, x, x2))
        x = x2
    pts.append((x, ty(V_ON)))
    path = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    parts.append(f'<polyline points="{path}" fill="none" stroke="#1f4e79" '
                 'stroke-width="2.5" stroke-linejoin="round"/>')

    # Segment labels above each level.
    for label, xa, xb, v in seg_spans:
        if not label:
            continue
        parts.append(text((xa + xb) / 2, ty(v) - 20, label, size=11))
    for i, (label, xa, xb) in enumerate(power_spans):
        if i:
            parts.append(f'<line x1="{xa:.1f}" y1="{ty(V_ON) - 4:.1f}" '
                         f'x2="{xa:.1f}" y2="{ty(V_ON) + 4:.1f}" '
                         'stroke="#1f4e79" stroke-width="1.5"/>')
        parts.append(text((xa + xb) / 2, ty(V_ON) + 24, label, size=11))

    # Phase brackets under the time axis.
    det = (seg_spans[1][1], seg_spans[2][2], "detection")
    cls = (seg_spans[3][1], seg_spans[-1][2],
           "classification: 4 class events, each followed by a mark event")
    pwr = (seg_spans[-1][2], power_spans[-1][2], "power on")
    for xa, xb, label in (det, cls, pwr):
        yb = Y1 + 18
        parts.append(f'<path d="M{xa + 2:.1f},{yb - 6} L{xa + 2:.1f},{yb} '
                     f'L{xb - 2:.1f},{yb} L{xb - 2:.1f},{yb - 6}" '
                     'fill="none" stroke="#555" stroke-width="1.2"/>')
        parts.append(text((xa + xb) / 2, yb + 16, label, size=12,
                          weight="bold"))

    parts.append("</svg>")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
