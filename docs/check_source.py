"""Fail if a page mentions a standard's clause without linking to it.

Every reference to an IEEE 802.3 clause or subclause must use the
``:clause:`` role (for example ``:clause:`40.8.3.1```), so that it links to
the clause's entry on the standards page. This script finds clause numbers
written as plain text.

Usage: python check_source.py <docs-source-directory>

SPDX-License-Identifier: Apache-2.0
"""

import pathlib
import re
import sys

# Uses of the role, removed before searching for plain-text clause numbers.
ROLE = re.compile(r":clause:`[^`]*`")
# "Clause 40", "clauses 24", "Clause 40.8.3.1", "subclause 25.4.5", ...
PLAIN = re.compile(r"\b(sub)?clauses?\s+\d", re.IGNORECASE)
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
                print(f"{path.relative_to(root)}:{lineno}: clause written as "
                      f"plain text near '{stripped[match.start():][:40]}'; "
                      f"use the :clause: role")
    print(f"checked {len(sources)} source files, {problems} problem(s) found")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
