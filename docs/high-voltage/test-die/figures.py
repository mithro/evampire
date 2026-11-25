"""Write every figure and table of the test-die pages.

Usage: uv run python docs/high-voltage/test-die/figures.py

Writes, into this folder: the hvt-*.svg figures of fig_struct.py,
fig_floor.py, fig_method.py and fig_pred.py, and the hvt-tab-*.csv tables
of tables.py and fig_pred.py. Inputs: silicon/hvtest/structures.json,
manifest.json (the floor plan written by silicon/hvtest/chip.py) and
predictions.json (simulated breakdown voltages). Standard library only;
the output is the same on every run.

SPDX-License-Identifier: Apache-2.0
"""

import pathlib
import sys

import tdkit  # noqa: F401  (sets the import path for svgdraw)
import fig_floor
import fig_method
import fig_pred
import fig_struct
import tables


def main():
    out = pathlib.Path(__file__).resolve().parent
    files = {}
    for module in (fig_struct, fig_floor, fig_method, fig_pred):
        for name, draw in module.FIGURES.items():
            files[name] = draw()
    files.update(tables.tables())
    files.update(fig_pred.tables())
    for name, content in sorted(files.items()):
        (out / name).write_text(content, encoding="utf-8")
    print(f"{len(files)} files written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
