"""Fail if a page refers to part of a standard without linking to it.

Every reference to an IEEE 802.3 clause or subclause must use the
``:clause:`` role (for example ``:clause:`40.8.3.1```), and every reference
to a section, table or figure of the USB Power Delivery or USB Type-C
specification must use the ``:pd:`` or ``:typec:`` role (for example
``:pd:`Table 5.10```), so that it links to the standard's entry on the
standards page. This script finds such references written as plain text.

Usage: python check_source.py <docs-source-directory>

SPDX-License-Identifier: Apache-2.0
"""

import pathlib
import re
import sys

# Uses of the roles, removed before searching for plain-text references.
ROLE = re.compile(r":(clause|pd|typec):`[^`]*`")
# "Clause 40", "clauses 24", "Clause 40.8.3.1", "subclause 25.4.5", and
# USB specification references such as "PD Table 5.10" or
# "Type-C Sections 4.5.2.2". IEEE 802.3 tables, figures and annexes use the
# :clause: role with an explicit title, e.g. :clause:`Table 145-24 <145>`.
PLAIN = re.compile(
    r"\b(sub)?clauses?\s+\d"
    r"|\b(PD|Type-C)\s+(sections?|tables?|figures?)\s+\d"
    # IEEE 802.3 tables, figures and annexes, e.g. "Table 145-24", "Annex 33A".
    r"|\b(tables?|figures?)\s+\d+-\d+"
    r"|\bannex(es)?\s+\d+[A-Z]\b",
    re.IGNORECASE,
)
# The standards page itself names every clause in its entries.
EXEMPT = {"standards.rst"}


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    root = pathlib.Path(argv[1])
    sources = sorted(
        p for p in root.rglob("*")
        if p.suffix in {".rst", ".md"} and "_build" not in p.parts
    )
    problems = 0
    for path in sources:
        if path.name in EXEMPT and path.parent == root:
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8")
                                      .splitlines(), start=1):
            stripped = ROLE.sub("", line)
            for match in PLAIN.finditer(stripped):
                problems += 1
                print(f"{path.relative_to(root)}:{lineno}: standard reference written as "
                      f"plain text near '{stripped[match.start():][:40]}'; "
                      f"use the :clause:, :pd: or :typec: role")
    print(f"checked {len(sources)} source files, {problems} problem(s) found")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
