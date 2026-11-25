"""Draw the floor plan of the test die from manifest.json.

hvt-floorplan.svg  every structure, pad and substrate pad at its position
                   on the 1936 µm × 2531 µm die, with the groups coloured.

figures.py calls this module; it writes no files itself.

SPDX-License-Identifier: Apache-2.0
"""

import tdkit
from svgdraw import GREY, INK, METAL, rect, svg, text

S = 0.30               # pixels per micrometre
X0, Y0 = 20, 46        # top-left corner of the die on the page
COLOUR = {"surround": "#fbd9b5", "pwell": "#aac6e6", "nat": "#bfe3c8",
          "dnw": "#f5b46e", "plates": "#c9a0dc", "rings": "#f6d5d1",
          "gated": "#ffe98a", "large": "#e0c9a6", "open": "#ffffff"}


def floorplan():
    structs, man = tdkit.load()
    dw, dh = man["die"]
    w, h = 640, int(Y0 + dh * S + 96)

    def px(x, y):
        return X0 + x * S, Y0 + (dh - y) * S

    b = [text(20, 24, "Floor plan, north up; x and y in µm from the "
              "south-west corner of the die", anchor="start", weight="bold")]
    b.append(rect(X0, Y0, dw * S, dh * S, "#fafafa"))
    pad = 100 * S
    for site in man["sites"]:
        name = site["name"]
        p = structs[name]
        key = tdkit.group_of(name, p)
        cx, cy = px(*site["centre"])
        half = (p["half"] + p["term"] + p["ncomp_w"]) * S
        if p["kind"] != "open":
            b.append(rect(cx - half, cy - half, 2 * half, 2 * half,
                          COLOUR[key]))
        x, y = px(*site["pad"])
        b.append(rect(cx, cy - 1, x - cx, 2, METAL, stroke="none"))
        b.append(rect(x - pad / 2, y - pad / 2, pad, pad, COLOUR[key]))
        b.append(text(x, y - pad / 2 - 3, name, size=9))
        if "aux_pad" in site:
            x, y = px(*site["aux_pad"])
            b.append(rect(x - pad / 2, y - pad / 2, pad, pad, COLOUR[key],
                          dash="3 2"))
            b.append(text(x - pad / 2 - 3, y + 3,
                          f"{name}.{site['aux_role'][0].upper()}",
                          anchor="end", size=9))
    for k, (x, y) in enumerate(man["sub_pads"]):
        x, y = px(x, y)
        b.append(rect(x - pad / 2, y - pad / 2, pad, pad, "#7fa7d6"))
        b.append(text(x + pad / 2 + 3, y + 3, f"SUB{k + 1}", anchor="start",
                      size=9))
    # axes ticks
    for v in range(0, int(dw) + 1, 500):
        x, y = px(v, 0)
        b.append(text(x, y + 13, str(v), size=10, fill=GREY))
    for v in range(0, int(dh) + 1, 500):
        x, y = px(dw, v)
        b.append(text(x + 4, y + 3, str(v), anchor="start", size=10,
                      fill=GREY))
    # legend
    titles = {k: t for k, t, _ in tdkit.GROUPS}
    y = Y0 + dh * S + 34
    for k, key in enumerate(COLOUR):
        x = 20 + (k % 5) * 124
        yy = y + (k // 5) * 20
        b.append(rect(x, yy - 10, 14, 11, COLOUR[key], stroke=INK))
        b.append(text(x + 19, yy, titles[key], anchor="start", size=11))
    b.append(rect(20 + 4 * 124, y + 10, 14, 11, "#7fa7d6", stroke=INK))
    b.append(text(20 + 4 * 124 + 19, y + 20, "Substrate pad",
                  anchor="start", size=11))
    b.append(text(20, y + 46, "Dashed squares are second pads: .R for ring "
                  "1 and .G for the plate.", anchor="start", size=11))
    return svg(w, h, b)


FIGURES = {"hvt-floorplan.svg": floorplan}
