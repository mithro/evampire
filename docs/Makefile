# Build the documentation with Sphinx.
#
#   make html       one-off build into _build/html
#   make check      build with warnings treated as errors, then check the
#                   rendered pages for error boxes (same as CI)
#   make clean      remove the build output

SPHINXBUILD = uv run --with-requirements requirements.txt sphinx-build
SOURCEDIR   = .
BUILDDIR    = _build

.PHONY: html check clean

html:
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html

check:
	$(SPHINXBUILD) -W --keep-going -b html $(SOURCEDIR) $(BUILDDIR)/html
	uv run python check_html.py $(BUILDDIR)/html

clean:
	rm -rf $(BUILDDIR)
