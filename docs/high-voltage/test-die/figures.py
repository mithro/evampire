"""Write every figure and table of the test-die pages.

Usage: uv run python docs/high-voltage/test-die/figures.py

Writes, into this folder: the structure catalogue (catalogue.rst and
the pages and figures in catalogue/, through gen_catalogue.py), the
hvt-*.svg figures of fig_struct.py,
fig_floor.py, fig_method.py, fig_sim.py and fig_pred.py, and the
hvt-tab-*.csv tables of tables.py and pred_data.py. Inputs:
silicon/hvtest/structures.json, manifest.json (the floor plan written by
silicon/hvtest/chip.py), predictions.json (simulated breakdown voltages,
written by import_predictions.py) and crosscheck.json (results of the
second simulator), and the catalogue texts in catalogue.py. Standard library only;
the output is the same on every run.

SPDX-License-Identifier: Apache-2.0
"""

import pathlib
import re
import sys

import tdkit  # noqa: F401  (sets the import path for svgdraw)
import fig_floor
import fig_method
import fig_pred
import fig_sim
import fig_struct
import gen_catalogue
import pred_data
import pred_extra
import tables


# Structures that the pages name on purpose although they are no longer on
# the die: the record of what the reviews removed.
REMOVED = {"DT5", "DT35", "DC15", "DW3", "DW6", "DM1_3", "CVD2", "NT35",
           "NA4", "NA0p6T35", "DT10", "DAo1T35"}
NAME = re.compile(r"\b(?:[ND][A-Za-z]{1,3}\d[A-Za-z0-9_]*|CV[NDA]+2?|OPEN)\b")
PAGES = ("structures.rst", "method.rst", "predictions.rst", "submission.rst",
         "../test-die.rst", "cat_plain.py", "cat_nat.py", "cat_rings.py",
         "cat_deep.py", "cat_groups.py")


def check_names(out, files):
    """Stop if a hand-written page names a structure that is not on the
    die. Names of removed structures are allowed on the submission page."""
    on_die = set(tdkit.load()[0])
    bad = []
    for page in PAGES:
        text = (out / page).read_text(encoding="utf-8")
        for name in sorted(set(NAME.findall(text))):
            if name in on_die or name.split(".")[0] in on_die:
                continue
            if name in REMOVED and page == "submission.rst":
                continue
            bad.append(f"{page}: {name}")
    if bad:
        raise SystemExit("structure names that are not on the die:\n  "
                         + "\n  ".join(bad))


def main():
    out = pathlib.Path(__file__).resolve().parent
    files = {}
    for module in (fig_struct, fig_floor, fig_method, fig_sim, fig_pred):
        for name, draw in module.FIGURES.items():
            files[name] = draw()
    files.update(tables.tables())
    files.update(pred_data.tables())
    files.update(pred_extra.tables())
    files.update(gen_catalogue.generate())
    check_names(out, files)
    (out / "catalogue").mkdir(exist_ok=True)
    for old in (out / "catalogue").iterdir():   # entries of removed structures
        if f"catalogue/{old.name}" not in files:
            old.unlink()
    for name, content in sorted(files.items()):
        (out / name).write_text(content, encoding="utf-8")
    print(f"{len(files)} files written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
