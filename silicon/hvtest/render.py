"""Render a region of a layout to PNG with the PDK's layer colours.

    uv run --with klayout python silicon/hvtest/render.py IN.gds OUT.png [X0 Y0 X1 Y1] [LYP]
"""

import sys

import klayout.db as kdb
import klayout.lay as lay


def main(argv):
    src, out = argv[0], argv[1]
    view = lay.LayoutView()
    view.load_layout(src, True)
    lyp = [a for a in argv[2:] if a.endswith(".lyp")]
    if lyp:
        view.load_layer_props(lyp[0])
    else:
        view.add_missing_layers()
    view.max_hier()
    nums = [float(a) for a in argv[2:] if not a.endswith(".lyp")]
    if len(nums) == 4:
        view.zoom_box(kdb.DBox(*nums))
    else:
        view.zoom_fit()
    view.set_config("background-color", "#ffffff")
    view.save_image(out, 1600, 1600)


if __name__ == "__main__":
    main(sys.argv[1:])
