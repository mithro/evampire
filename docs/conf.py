# Sphinx configuration for the evampire documentation.
#
# SPDX-License-Identifier: Apache-2.0

import os

from docutils import nodes
from sphinx import addnodes
from sphinx.util.nodes import split_explicit_title

project = "evampire"
author = "The evampire Authors"
copyright = "2026, The evampire Authors"

extensions = [
    # Markdown pages alongside reStructuredText.
    "myst_parser",
    # Block diagrams and state machines written in the Graphviz "dot" language.
    "sphinx.ext.graphviz",
    # Equations, rendered in the browser with MathJax.
    "sphinx.ext.mathjax",
    # Digital timing diagrams and register bit-field diagrams.
    "sphinxcontrib.wavedrom",
    # Tabs, cards and grids.
    "sphinx_design",
    # "Copy" button on code blocks.
    "sphinx_copybutton",
    # Short roles for external links, e.g. :wikipedia:`Ethernet frame
    # <Ethernet_frame>`.
    "sphinx.ext.extlinks",
]

# :wikipedia:`Page_title` links to that English Wikipedia article; an
# explicit title gives the link text, e.g. :wikipedia:`frames <Ethernet_frame>`.
extlinks = {
    "wikipedia": ("https://en.wikipedia.org/wiki/%s", "%s"),
}

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

exclude_patterns = ["_build"]

# Number figures, tables and code blocks so they can be referenced as
# "Figure 3" with :numref:.
numfig = True

# Render WaveDrom diagrams to SVG at build time (no JavaScript needed when
# viewing the pages).
render_using_wavedrompy = True
wavedrom_html_jsinline = False

graphviz_output_format = "svg"

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "tasklist",
]

html_theme = "furo"
html_title = "evampire"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Pull request previews on Read the Docs are built from a commit that is not
# on main; point the "view source" links at that commit.
if os.environ.get("READTHEDOCS_VERSION_TYPE") == "external":
    _source_branch = os.environ.get("READTHEDOCS_GIT_COMMIT_HASH", "main")
else:
    _source_branch = "main"

html_theme_options = {
    "source_repository": "https://github.com/mithro/evampire/",
    "source_branch": _source_branch,
    "source_directory": "docs/",
}


# Roles that link references to parts of a standard to that standard's
# entry on the standards page (docs/standards.rst):
#
#   :clause:`40.8.3.1`    -> "Clause 40.8.3.1", links to IEEE 802.3 Clause 40
#   :pd:`Table 5.10`      -> "PD Table 5.10", links to the USB PD spec
#   :typec:`Section 4.2`  -> "Type-C Section 4.2", links to the USB Type-C spec
#
# An explicit title can be given, as in :clause:`Clauses 24 <24>` or
# :typec:`Section 4.2 <Section 4.2>`. A reference whose target has no entry
# on the standards page is a build error (the reference cannot be resolved).
def _make_standard_role(prefix, label):
    def role(name, rawtext, text, lineno, inliner, options=None,
             content=None):
        has_title, title, target = split_explicit_title(text)
        target = target.strip()
        if not has_title:
            title = f"{prefix} {target}"
        env = inliner.document.settings.env
        node = addnodes.pending_xref(
            rawtext,
            refdomain="std",
            reftype="ref",
            reftarget=label(target),
            refexplicit=True,
            refwarn=True,
            refdoc=env.docname,
        )
        node += nodes.inline(title, title)
        return [node], []
    return role


def setup(app):
    app.add_role("clause", _make_standard_role(
        "Clause", lambda n: f"ieee8023-clause-{n.split('.')[0]}"))
    app.add_role("pd", _make_standard_role(
        "PD", lambda n: "usb-pd-specification"))
    app.add_role("typec", _make_standard_role(
        # U+2011 NON-BREAKING HYPHEN: keep "Type-C" on one line.
        "Type\u2011C", lambda n: "usb-type-c-specification"))
