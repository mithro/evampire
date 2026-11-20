# Build the documentation with Sphinx.
#
#   make html       one-off build into _build/html
#   make check      build with warnings treated as errors (same as CI)
#   make clean      remove the build output

SPHINXBUILD = uv run --with-requirements requirements.txt sphinx-build
SOURCEDIR   = .
BUILDDIR    = _build

.PHONY: html check clean

html:
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html

check:
	$(SPHINXBUILD) -W --keep-going -b html $(SOURCEDIR) $(BUILDDIR)/html

clean:
	rm -rf $(BUILDDIR)
