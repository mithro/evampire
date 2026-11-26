# /// script
# requires-python = ">=3.11"
# dependencies = ["gdstk", "shapely"]
# ///
"""Draw annotated views of the gf180mcu_fd_io pad cell layouts.

Reads the 5-metal GDS files of the foundry I/O library and writes the
docs/esd/figures/gds-*.svg figures of docs/esd/layout.rst. GF180_IO names
a checkout of the library at the commit docs/esd/simulation.rst pins:

    GF180_IO=$PWD/globalfoundries-pdk-libs-gf180mcu_fd_io \\
        uv run docs/esd/gds/figures.py [figure ...]

With no arguments it draws every figure. Merged layers are cached in
docs/esd/gds/cache/, which is git-ignored.

SPDX-License-Identifier: Apache-2.0
"""

import pathlib
import sys

import figs_pad

OUT = pathlib.Path(__file__).resolve().parent.parent / "figures"
FIGURES = {**figs_pad.FIGURES}


def main(names):
    for name in names or FIGURES:
        fig = FIGURES[name]()
        fig.save(OUT / f"{name}.svg")
        print("wrote", OUT / f"{name}.svg")


if __name__ == "__main__":
    main(sys.argv[1:])
