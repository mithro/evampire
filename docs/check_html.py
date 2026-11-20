"""Fail if the built HTML contains error boxes that Sphinx does not report.

Some problems only show up in the rendered pages, not as Sphinx warnings:

* The Furo theme draws a red error box over every ``.. contents::``
  directive. The message comes from a CSS ``::before`` rule, so it never
  appears in the HTML text; the check looks for the element the rule targets.
* docutils turns some markup errors into "system message" boxes.

Usage: python check_html.py <html-output-directory>

SPDX-License-Identifier: Apache-2.0
"""

import pathlib
import sys

# Text or markup that only appears in a page when something is wrong.
MARKERS = {
    'class="contents':
        "a '.. contents::' directive, which Furo shows as a red error box; "
        "remove it (Furo lists the page contents in the right-hand sidebar)",
    'class="system-message"':
        "a docutils error or warning box is shown in the page",
    'class="problematic"':
        "a reference or role could not be resolved",
}


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    root = pathlib.Path(argv[1])
    pages = sorted(root.rglob("*.html"))
    if not pages:
        print(f"error: no HTML files found under {root}")
        return 2
    failures = 0
    for page in pages:
        text = page.read_text(encoding="utf-8")
        for marker, meaning in MARKERS.items():
            count = text.count(marker)
            if count:
                failures += 1
                print(f"{page.relative_to(root)}: {count} x '{marker}': {meaning}")
    print(f"checked {len(pages)} pages, {failures} problem(s) found")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
