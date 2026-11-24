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
(logic levels, from electrical.rst), and the clock-cycle, meander,
pad, chain-delay and speed-buffer figures, next to this script. The
drawing code is in timing_figs.py, interface_figs.py, board_figs.py and
logic_figs.py, with shared helpers in svgkit.py.

SPDX-License-Identifier: Apache-2.0
"""

import pathlib

from board_figs import (clock_cycle, meander, pad_delay, pad_duty,
                        pad_edges)
from interface_figs import frame, levels
from logic_figs import chain_delay, speed_buffer
from timing_figs import speed_change, timing_budget, timing_params

HERE = pathlib.Path(__file__).parent


if __name__ == "__main__":
    for name, fn in (("timing-params", timing_params),
                     ("timing-budget", timing_budget),
                     ("speed-change", speed_change), ("frame", frame),
                     ("levels", levels), ("clock-cycle", clock_cycle),
                     ("pad-delay", pad_delay), ("pad-duty", pad_duty),
                     ("pad-edges", pad_edges),
                     ("chain-delay", chain_delay),
                     ("speed-buffer", speed_buffer)):
        (HERE / f"{name}.svg").write_text(fn())
    (HERE / "meander-280.svg").write_text(meander(
        280, "2 ns at 7.2 ps/mm; recommended total under 51 mm, "
        "at most 152 mm"))
    (HERE / "meander-86.svg").write_text(meander(
        86, "0.62 ns for the KSZ9031RNX, added to its 1.38 ns: 2.0 ns"))
