"""Identify figures and tables by their label instead of a running number.

Sphinx numbers figures and tables in one sequence across the whole site, so
adding a table near the start renumbers every table after it. This extension
replaces each number with an identifier taken from the item's own label:
the table labelled ``tab-poe-startup-power`` is captioned
"Table poe-startup-power", and ``:numref:`` shows the same text. The
identifier changes only when somebody renames the label.

Sphinx still does the numbering (``numfig = True``). This extension runs
after it and swaps each number for the identifier, which the HTML writer and
``:numref:`` then print unchanged.

A caption puts a colon after the identifier, as in "Table poe-pairs: The two
pair sets". A ``:numref:`` link has none, so the running text reads "Table
poe-pairs lists the pins". Both take their text from ``numfig_format``, so
the colon is added by the HTML translator, which writes only the caption.

SPDX-License-Identifier: Apache-2.0
"""

import re

from sphinx.util import logging
from sphinx.writers.html5 import HTML5Translator

logger = logging.getLogger(__name__)

# Label prefixes that only repeat the kind of item, which the caption
# already states ("Fig." or "Table").
KIND_PREFIXES = {
    "figure": ("fig-",),
    "table": ("tab-", "tbl-"),
    "code-block": ("lst-",),
}

# An id that Sphinx made up for an item without a label, such as "id3".
_GENERATED_ID = re.compile(r"id\d+")


def stable_id(kind, label):
    """Return the identifier shown for the item of this kind and label.

    This function alone decides what readers see, so a different scheme
    needs changes only here.
    """
    for prefix in KIND_PREFIXES.get(kind, ()):
        if label.startswith(prefix):
            return label[len(prefix):]
    return label


def _replace_numbers(app, env):
    """Swap every number Sphinx assigned for the item's identifier."""
    seen = {}
    for docname in sorted(env.toc_fignumbers):
        for kind, numbers in env.toc_fignumbers[docname].items():
            for label in numbers:
                if _GENERATED_ID.fullmatch(label):
                    logger.warning(
                        "a numbered %s has no label, so it has no stable "
                        "identifier; give it a :name: option", kind,
                        location=docname)
                    continue
                identifier = stable_id(kind, label)
                first = seen.setdefault((kind, identifier), (docname, label))
                if first != (docname, label):
                    logger.warning(
                        "%s '%s' has the same identifier '%s' as '%s' in "
                        "%s; rename one of the labels", kind, label,
                        identifier, first[1], first[0], location=docname)
                numbers[label] = (identifier,)
    return []


class CaptionColonTranslator(HTML5Translator):
    """Write "Table poe-pairs: " at the start of a caption."""

    def add_fignumber(self, node):
        start = len(self.body)
        super().add_fignumber(node)
        # Sphinx appends three strings: the opening <span>, the identifier
        # followed by a space, and the closing </span>.
        added = self.body[start:]
        if len(added) == 3 and added[1].endswith(" "):
            self.body[start + 1] = added[1][:-1] + ": "


def setup(app):
    # Sphinx assigns the numbers in its own handler for this event, at the
    # default priority of 500. A higher number runs later.
    app.connect("env-get-updated", _replace_numbers, priority=900)
    for builder in ("html", "dirhtml", "singlehtml"):
        app.set_translator(builder, CaptionColonTranslator)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
