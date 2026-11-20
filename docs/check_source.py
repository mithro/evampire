"""Fail if a page refers to a standard without linking to it.

Every reference to an IEEE 802.3 clause or subclause must use the
``:clause:`` role (for example ``:clause:`40.8.3.1```), and every reference
to a section, table or figure of the USB Power Delivery or USB Type-C
specification must use the ``:pd:`` or ``:typec:`` role (for example
``:pd:`Table 5.10```), so that it links to the standard's entry on the
standards page. Other standards that the pages name, such as IEEE 802.1AB
or IEC 61000-4-2, must use the ``:std:`` role (for example
``:std:`IEEE 802.1AB```). This script finds such references written as
plain text.

The title of a cited document in a citation entry (a ``.. [KEY]`` block)
names the standard by design, so no pattern is applied
there.

Usage: python check_source.py <docs-source-directory>

SPDX-License-Identifier: Apache-2.0
"""

import pathlib
import re
import sys

# Uses of the roles, removed before searching for plain-text references.
ROLE = re.compile(r":(clause|pd|typec|std):`[^`]*`")
# "Clause 40", "clauses 24", "Clause 40.8.3.1", "subclause 25.4.5", and
# USB specification references such as "PD Table 5.10" or
# "Type-C Sections 4.5.2.2". IEEE 802.3 tables, figures and annexes use the
# :clause: role with an explicit title, for example
# :clause:`Table 145-24 <145>`.
PLAIN = re.compile(
    r"\b(sub)?clauses?\s+\d"
    r"|\b(PD|Type-C)\s+(sections?|tables?|figures?)\s+\d"
    # IEEE 802.3 tables, figures and annexes, for example "Table 145-24" or
    # "Annex 33A".
    r"|\b(tables?|figures?)\s+\d+-\d+"
    r"|\bannex(es)?\s+\d+[A-Z]\b",
    re.IGNORECASE,
)
# Names of other standards that must use the :std: role. Only names that
# cannot mean anything else are listed.
PLAIN_STD = re.compile(
    r"\bIEEE\s+802\.1(AB|Q)\b"
    r"|\bIEC\s+61000-4-[245]\b"
    r"|\bIEC\s+62368"
    r"|\bUSB\s+2\.0\s+specification"
    r"|\bTIA-568",
    re.IGNORECASE,
)
# The first line of a citation entry, such as ".. [IEC61000-4-2] IEC ...".
CITATION = re.compile(r"^\.\.\s+\[[^\]]+\]")
# The standards page itself names every standard in its entries.
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
        in_citation = False
        for lineno, line in enumerate(path.read_text(encoding="utf-8")
                                      .splitlines(), start=1):
            # A citation entry runs from its ".. [KEY]" line to the next
            # line that is neither blank nor indented.
            if CITATION.match(line):
                in_citation = True
            elif line.strip() and not line[0].isspace():
                in_citation = False
            stripped = ROLE.sub("", line)
            found = []
            if not in_citation:
                found += [(m, ":clause:, :pd: or :typec:")
                          for m in PLAIN.finditer(stripped)]
                found += [(m, ":std:") for m in PLAIN_STD.finditer(stripped)]
            for match, roles in found:
                problems += 1
                print(f"{path.relative_to(root)}:{lineno}: standard reference "
                      f"written as plain text near "
                      f"'{stripped[match.start():][:40]}'; use the {roles} "
                      f"role")
    print(f"checked {len(sources)} source files, {problems} problem(s) found")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
