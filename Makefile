	# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = frontend/docs
BUILDDIR      = frontend/build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

coverage:
	pytest backend/src/tests --cov=backend/src
	--cov-report=term-missing --cov-fail-under=85

lint:
	flake8 backend/src
	mypy backend/src
	bandit -r backend/src

typecheck:
		mypy backend/src
		@if command -v pyright >/dev/null 2>&1; then \
		pyright backend/src; \
	fi

benchmarks:
		python scripts/benchmarks/run_benchmarks.py > bench_results.json
