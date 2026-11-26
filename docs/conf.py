# Sphinx configuration for the evampire documentation.
#
# SPDX-License-Identifier: Apache-2.0

import datetime
import os
import pathlib
import re
import sys

from docutils import nodes
from sphinx import addnodes
from sphinx.util.nodes import split_explicit_title

# Extensions written for this site live in docs/_ext.
sys.path.insert(0, str(pathlib.Path(__file__).parent / "_ext"))

project = "evampire"
author = "The evampire Authors"
# The year of the build, so the notice never needs editing by hand.
copyright = f"{datetime.date.today().year}, The evampire Authors"

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
    # Short roles for external links, for example :wikipedia:`Ethernet frame
    # <Ethernet_frame>`.
    "sphinx.ext.extlinks",
    # Identifies each figure and table by its label instead of a running
    # number (docs/_ext/stable_ids.py).
    "stable_ids",
]

# :wikipedia:`Page_title` links to that English Wikipedia article. An
# explicit title gives the link text, for example
# :wikipedia:`frames <Ethernet_frame>`.
extlinks = {
    "wikipedia": ("https://en.wikipedia.org/wiki/%s", "%s"),
}

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

exclude_patterns = ["_build", "_extra"]

# Give figures, tables and code blocks an identifier so they can be
# referenced with :numref:. The stable_ids extension replaces the running
# number that Sphinx assigns with the item's label, so the table labelled
# "tab-power-roles" is "Table power-roles".
numfig = True

# Render WaveDrom diagrams to SVG at build time (no JavaScript needed when
# viewing the pages).
render_using_wavedrompy = True
wavedrom_html_jsinline = False

graphviz_output_format = "svg"

# "make linkcheck" checks every external link. External sites fail briefly,
# so each link is tried several times before it counts as broken.
linkcheck_retries = 3
linkcheck_timeout = 60
# Sites that refuse automated requests (they answer 403 or time out for
# any client that is not a browser). Links to them are checked by hand.
linkcheck_ignore = [
    r"https://ieeexplore\.ieee\.org/.*",
    r"https://tiaonline\.org/.*",
    r"https://webstore\.ansi\.org/.*",
    r"https://www\.analog\.com/.*",
    r"https://www\.st\.com/.*",
    r"https://www\.microchip\.com/.*",
    # JEDEC answers 403 to the GitHub Actions runners.
    r"https://www\.jedec\.org/.*",
    # AIP Publishing answers 403 to automated clients; its DOIs redirect there.
    r"https://doi\.org/10\.1063/.*",
    r"https://pubs\.aip\.org/.*",
    # Wiley and IOP Publishing also answer 403 to automated clients.
    r"https://doi\.org/10\.1049/.*",
    r"https://ietresearch\.onlinelibrary\.wiley\.com/.*",
    r"https://doi\.org/10\.1088/.*",
    r"https://iopscience\.iop\.org/.*",
    # MDPI and Littelfuse also answer 403 to automated clients.
    r"https://doi\.org/10\.3390/.*",
    r"https://www\.mdpi\.com/.*",
    r"https://www\.littelfuse\.com/.*",
    # SourceForge answers 403 to the GitHub Actions runners.
    r"https://ngspice\.sourceforge\.io/.*",
    # Cisco and DigiKey answer 403 to automated clients.
    r"https://www\.cisco\.com/.*",
    r"https://www\.digikey\.co\.uk/.*",
]
# GitHub draws its line anchors (#L16-L52) with JavaScript, so the checker
# never finds them in the page. The page itself is still checked.
linkcheck_anchors_ignore_for_url = [
    r"https://github\.com/.*",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "tasklist",
]

html_theme = "furo"
html_title = "evampire"
html_static_path = ["_static"]
# Files copied to the top of the site as they are: pages that redirect an
# address that used to be a page to the page that replaced it.
html_extra_path = ["_extra"]
html_css_files = ["custom.css"]
# Opens a diagram over the whole window when it is clicked, where the reader
# can zoom in and pan around.
html_js_files = ["diagram-viewer.js"]

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


# Roles that link references to a standard to that standard's entry on the
# standards page (docs/standards.rst):
#
#   :clause:`40.8.3.1`    -> "Clause 40.8.3.1", links to IEEE 802.3 Clause 40
#   :pd:`Table 5.10`      -> "PD Table 5.10", links to the USB PD spec
#   :typec:`Section 4.2`  -> "Type-C Section 4.2", links to the USB Type-C spec
#   :std:`802.1AB`        -> "802.1AB", links to the IEEE 802.1AB entry
#
# An explicit title can be given, as in :clause:`Clauses 24 <24>`,
# :typec:`Section 4.2 <Section 4.2>` or :std:`Section 8.5 <usb2>`.
#
# The :std: role links to the label "std-" followed by the target written in
# lower case, with each run of characters other than letters and digits
# replaced by "-" and a leading publisher name "IEEE" or "ANSI" dropped. For
# example :std:`802.1AB`, :std:`IEEE 802.1AB` and
# :std:`LLDP <802.1AB>` all link to the label "std-802-1ab", and
# :std:`IEC 61000-4-2` links to "std-iec-61000-4-2". Each entry on the
# standards page carries its label.
#
# A reference whose target has no entry on the standards page is a build
# error (the reference cannot be resolved).
def _make_standard_role(prefix, label):
    def role(name, rawtext, text, lineno, inliner, options=None,
             content=None):
        has_title, title, target = split_explicit_title(text)
        target = target.strip()
        if not has_title:
            title = f"{prefix} {target}" if prefix else target
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


def _std_label(target):
    slug = re.sub(r"[^a-z0-9]+", "-", target.lower()).strip("-")
    slug = re.sub(r"^(ieee|ansi)-", "", slug)
    return f"std-{slug}"


def setup(app):
    app.add_role("clause", _make_standard_role(
        "Clause", lambda n: f"ieee8023-clause-{n.split('.')[0]}"))
    app.add_role("pd", _make_standard_role(
        "PD", lambda n: "usb-pd-specification"))
    app.add_role("typec", _make_standard_role(
        # U+2011 NON-BREAKING HYPHEN: keep "Type-C" on one line.
        "Type\u2011C", lambda n: "usb-type-c-specification"))
    app.add_role("std", _make_standard_role("", _std_label))
