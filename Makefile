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
        pytest tests --cov=src \
        --cov-report=term-missing --cov-fail-under=95

lint:
        flake8 src
        mypy src
        bandit -r src
        flake8 src/ tests/

format:
        isort src
        black src
        black src/ tests/

typecheck:
                mypy src
                @if command -v pyright >/dev/null 2>&1; then \
                pyright src; \
	fi

benchmarks:
	python scripts/benchmarks/run_benchmarks.py > bench_results.json

secrets:
	gitleaks detect --source . --redact

install:
	pip install -e .[dev]

test:
	pytest --cov=src tests/
