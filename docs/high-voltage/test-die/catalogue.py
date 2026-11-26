"""The written part of the structure catalogue: one entry per structure.

gen_catalogue.py joins these texts with the drawn parameters
(silicon/hvtest/structures.json), the positions (manifest.json) and the
predictions (predictions.json). It stops if a structure on the die has no
entry here, or an entry names a structure that is not on the die.

Fields of an entry: p purpose, w how it works, c compared with (structure,
what differs), m measurement (added to the generated list of procedures
and pads), r how to read the result (optional), l limits. In the texts,
{NAME} links to a structure's entry and {P1} to {P5} to a procedure.
Simulated voltages do not belong here: they are in the generated tables.

SPDX-License-Identifier: Apache-2.0
"""

import cat_deep
import cat_nat
import cat_plain
import cat_rings
from cat_groups import GROUPS  # noqa: F401

E = {}
for _module in (cat_plain, cat_nat, cat_rings, cat_deep):
    _twice = sorted(set(E) & set(_module.E))
    if _twice:
        raise SystemExit(f"catalogue texts: {_twice} defined twice")
    E.update(_module.E)
