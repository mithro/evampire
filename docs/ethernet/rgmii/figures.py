# /// script
# requires-python = ">=3.10"
# ///
"""Draw the figures for the RGMII pages as SVG files.

Usage: uv run docs/ethernet/rgmii/figures.py

Writes timing-params.svg (what each skew, setup and hold parameter of
tab-rgmii-timing measures) and timing-budget.svg (the setup and hold
margins of the worked budget), from the values quoted on timing.rst, and
speed-change.svg (TXC changing speed with a stretched phase, and a
forbidden glitch), frame.svg (the fields of a frame) and levels.svg
(logic levels, from electrical.rst), next to this script. The drawing
code is in timing_figs.py and interface_figs.py, with shared helpers in
svgkit.py.

SPDX-License-Identifier: Apache-2.0
"""

import pathlib

from interface_figs import frame, levels
from timing_figs import speed_change, timing_budget, timing_params

HERE = pathlib.Path(__file__).parent


if __name__ == "__main__":
    for name, fn in (("timing-params", timing_params),
                     ("timing-budget", timing_budget),
                     ("speed-change", speed_change), ("frame", frame),
                     ("levels", levels)):
        (HERE / f"{name}.svg").write_text(fn())
