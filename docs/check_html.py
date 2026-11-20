"""Fail if the built HTML has problems that Sphinx does not report.

Some problems only show up in the rendered pages, not as Sphinx warnings:

* The Furo theme draws a red error box over every ``.. contents::``
  directive. The message comes from a CSS ``::before`` rule, so it never
  appears in the HTML text; the check looks for the element the rule targets.
* docutils turns some markup errors into "system message" boxes.
* A numbered figure or table that no link on the site points to has a
  number nobody uses. Refer to it with ``:numref:``, or remove its caption
  so that it is not numbered.
* A Graphviz diagram without an ``:alt:`` option gets the diagram's source
  code as its alternative text, and an image without ``alt`` has none.

Usage: python check_html.py <html-output-directory>

SPDX-License-Identifier: Apache-2.0
"""

import html.parser
import pathlib
import posixpath
import sys
import urllib.parse

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


class PageParser(html.parser.HTMLParser):
    """Collect the links, numbered figures and tables, and images of a page.

    ``links`` holds every link target except the "link to this" anchors
    beside headings and captions. ``numbered`` holds, for each numbered
    figure or table, its caption number and every ``id`` inside it, because
    a label can land on the figure, on the table or on an element within it.
    ``missing_alt`` lists images and diagrams without alternative text.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.numbered = []
        self.missing_alt = []
        # Open <figure> and <table> elements, each as [ids, caption number].
        self._open = []
        self._caption = None
        # The data file and the text of an open Graphviz <object>.
        self._object = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = (attrs.get("class") or "").split()
        if tag == "a" and "href" in attrs and "headerlink" not in classes:
            self.links.append(attrs["href"])
        if tag in ("figure", "table"):
            self._open.append([set(), None])
        if "id" in attrs:
            for element in self._open:
                element[0].add(attrs["id"])
        if tag == "span" and "caption-number" in classes:
            self._caption = ""
        if tag == "img" and not (attrs.get("alt") or "").strip():
            self.missing_alt.append(f"image {attrs.get('src')}")
        if tag == "object" and "graphviz" in classes:
            self._object = [attrs.get("data"), ""]

    def handle_data(self, data):
        if self._caption is not None:
            self._caption += data
        if self._object is not None:
            self._object[1] += data

    def handle_endtag(self, tag):
        if tag == "span" and self._caption is not None:
            if self._open:
                self._open[-1][1] = self._caption.strip()
            self._caption = None
        if tag in ("figure", "table") and self._open:
            ids, number = self._open.pop()
            if number:
                self.numbered.append((number, ids))
        if tag == "object" and self._object is not None:
            data, alt = self._object
            alt = alt.strip()
            # Without :alt:, Sphinx uses the Graphviz source as the text.
            if (not alt or "->" in alt
                    or alt.startswith(("//", "/*", "digraph", "graph"))):
                self.missing_alt.append(f"Graphviz diagram {data}")
            self._object = None


def reference_and_alt_problems(root, pages):
    """Return unreferenced figure and table numbers and missing alt text."""
    parsed = {}
    for page in pages:
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        parsed[page.relative_to(root).as_posix()] = parser
    # Every (page, fragment) pair that some link on the site points to.
    targets = set()
    for name, parser in parsed.items():
        for href in parser.links:
            url = urllib.parse.urlsplit(href)
            if url.scheme or url.netloc or not url.fragment:
                continue
            path = url.path or posixpath.basename(name)
            path = posixpath.normpath(
                posixpath.join(posixpath.dirname(name), path))
            targets.add((path, url.fragment))
    problems = []
    for name, parser in parsed.items():
        for number, ids in parser.numbered:
            if not any((name, i) in targets for i in ids):
                problems.append(
                    f"{name}: '{number}' is numbered but no page refers to "
                    f"it; add a :numref: reference or remove its caption")
        for item in parser.missing_alt:
            problems.append(f"{name}: {item} has no alt text; give the "
                            f"directive an :alt: option")
    return problems


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
    for problem in reference_and_alt_problems(root, pages):
        failures += 1
        print(problem)
    print(f"checked {len(pages)} pages, {failures} problem(s) found")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
