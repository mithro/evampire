# Sphinx configuration for the evampire documentation.
#
# SPDX-License-Identifier: Apache-2.0

import os

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
]

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
