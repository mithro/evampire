# Build the documentation with Sphinx.
#
#   make html       one-off build into _build/html
#   make check      check that references to standards are links, build with
#                   warnings treated as errors, then check the rendered
#                   pages for error boxes, unreferenced figure and table
#                   numbers and missing alt text (same as CI)
#   make linkcheck  check that every external link opens a page
#   make clean      remove the build output

SPHINXBUILD = uv run --with-requirements requirements.txt sphinx-build
SOURCEDIR   = .
BUILDDIR    = _build

.PHONY: html check linkcheck clean

html:
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html

check:
	uv run python check_source.py $(SOURCEDIR)
	$(SPHINXBUILD) -W --keep-going -b html $(SOURCEDIR) $(BUILDDIR)/html
	uv run python check_html.py $(BUILDDIR)/html

linkcheck:
	$(SPHINXBUILD) -b linkcheck $(SOURCEDIR) $(BUILDDIR)/linkcheck

clean:
	rm -rf $(BUILDDIR)
