# ========== VARIABLES CONFIGURABLES ==========
PYTHON=python
VENV=.venv
SRC=src
TESTS=src/tests
SPHINXBUILD=sphinx-build
SPHINXOPTS=
SOURCEDIR=frontend/docs
BUILDDIR=frontend/build

# ========= TAREAS GENÉRICAS ==========

help:
	@echo "Comandos disponibles:"
	@echo "  make install         Instala el entorno en modo desarrollo"
	@echo "  make run             Ejecuta Cobra usando dotenv"
	@echo "  make test            Ejecuta tests con pytest y coverage"
	@echo "  make lint            Ejecuta linters: flake8, mypy, bandit"
	@echo "  make format          Formatea con black + isort"
	@echo "  make typecheck       Verifica tipos con mypy + pyright"
	@echo "  make docker          Construye todos los contenedores"
	@echo "  make docs            Genera documentación Sphinx"
	@echo "  make clean           Limpia archivos temporales"
	@echo "  make secrets         Busca secretos con gitleaks"
	@echo "  make check           Linter + Tests + Typecheck (pre-commit/release)"

install:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate 2>/dev/null || . $(VENV)/Scripts/activate && \
		pip install --upgrade pip && \
		pip install -e .[dev]

run:
	$(PYTHON) -m dotenv -f .env run -- $(PYTHON) -m src.main

test:
	pytest --cov=$(SRC) $(TESTS) --cov-report=term-missing --cov-fail-under=90

lint:
	flake8 $(SRC)
	mypy $(SRC)
	bandit -r $(SRC)

format:
	isort $(SRC)
	black $(SRC)

typecheck:
	mypy $(SRC)
	@command -v pyright >/dev/null 2>&1 && pyright $(SRC) || echo "ℹ️ pyright no está instalado"

secrets:
	gitleaks detect --source . --redact

check: lint test typecheck
	@echo "✅ Todo en orden. Código listo para commit o build."

docker:
	docker build -t cobra -f docker/Dockerfile .
	docker build -t cobra-cpp -f docker/cpp.Dockerfile .
	docker build -t cobra-js -f docker/js.Dockerfile .
	docker build -t cobra-python -f docker/python.Dockerfile .
	docker build -t cobra-rust -f docker/rust.Dockerfile .

docs:
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov \
	       $(BUILDDIR) .venv dist build bench_results.json

.PHONY: help install run test lint format typecheck secrets docker docs clean check
