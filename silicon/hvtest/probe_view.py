"""Render the layout as it looks from above under a microscope.

    uv run --with klayout python silicon/hvtest/probe_view.py IN.gds OUT.png WIDTH_PX [X0 Y0 X1 Y1]

Top metal and pad openings are drawn bright and the lower layers dimmer, each opaque, in the
order of the stack. The colours are chosen for legibility; they are not a model of the films.
With no box the whole die is drawn. docs/high-voltage/test-die/hvt-die-view.png and
hvt-die-view-detail.png are made with it from the layout of chip.py (widths 1400 and 1500,
the detail with the box 40 40 700 520).

SPDX-License-Identifier: Apache-2.0
"""
import sys
import klayout.db as kdb
import klayout.lay as lay

src, out, w = sys.argv[1], sys.argv[2], int(sys.argv[3])
box = [float(a) for a in sys.argv[4:8]] if len(sys.argv) >= 8 else None
view = lay.LayoutView()
view.load_layout(src, True)
view.set_config("background-color", "#3a4a3f")   # oxide over silicon
view.set_config("grid-visible", "false")
view.set_config("text-visible", "false")
# drawn bottom to top; (layer, datatype, fill, frame, stipple: 0 solid)
STACK = [(12, 0, "#34503f"), (21, 0, "#2f5a4a"), (5, 0, "#4a5a3a"), (204, 0, "#3d4433"),
         (22, 0, "#5b6b4a"), (30, 0, "#8a5a4a"), (34, 0, "#7f8a9a"), (36, 0, "#8f98a6"),
         (42, 0, "#9aa3b0"), (46, 0, "#a8b0bb"), (81, 0, "#d9c58a"), (37, 0, "#f3e3a6")]
it = view.begin_layers()
while not it.at_end():
    view.delete_layer(it)
for l, d, col in STACK:
    p = lay.LayerProperties()
    p.source = f"{l}/{d}"
    c = int(col[1:], 16)
    p.fill_color = p.frame_color = c
    p.dither_pattern = 0
    p.transparent = False
    view.insert_layer(view.end_layers(), p)
view.max_hier()
ly = view.active_cellview().layout()
bb = kdb.DBox(*box) if box else kdb.DBox(0, 0, 1936, 2531)
h = int(w * bb.height() / bb.width())
view.resize(w, h)
view.zoom_box(bb)
view.save_image(out, w, h)
print(out, w, h)
