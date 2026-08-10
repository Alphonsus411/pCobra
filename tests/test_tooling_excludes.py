"""Contratos de exclusión para herramientas de validación del repositorio."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"

VENV_EXCLUDE_PATHS = (
    "venv/",
    ".venv/",
    ".venv-release-test/",
    "venv-testpypi/",
)


def _pyproject() -> dict[str, object]:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


def test_black_excludes_versioned_virtualenvs_and_site_packages() -> None:
    """Evita que Black inspeccione entornos virtuales versionados."""
    black_config = _pyproject()["tool"]["black"]
    extend_exclude = black_config["extend-exclude"]
    matcher = re.compile(extend_exclude, re.VERBOSE)

    for path in (
        *VENV_EXCLUDE_PATHS,
        "venv-testpypi/Lib/site-packages/pip/__init__.py",
    ):
        assert matcher.search(path), path


def test_black_excludes_only_root_python_transpiler_snapshots() -> None:
    """Limita la exclusión a los snapshots Python generados del nivel raíz."""
    black_config = _pyproject()["tool"]["black"]
    matcher = re.compile(black_config["extend-exclude"], re.VERBOSE)

    assert matcher.search("/tests/data/expected_examples/hola.py")
    for maintained_path in (
        "/tests/test_ejemplos_io.py",
        "/tests/data/expected_examples/features/feature_base/minimal.py",
        "/src/pcobra/cobra/transpilers/transpiler/to_python.py",
    ):
        assert not matcher.search(maintained_path), maintained_path


def test_static_validation_tools_exclude_versioned_virtualenvs() -> None:
    """Mantiene alineadas las exclusiones de Ruff, mypy y pytest."""
    tool_config = _pyproject()["tool"]

    ruff_excludes = set(tool_config["ruff"]["exclude"])
    pytest_norecursedirs = set(tool_config["pytest"]["ini_options"]["norecursedirs"])
    mypy_exclude = tool_config["mypy"]["exclude"]

    for path in VENV_EXCLUDE_PATHS:
        dirname = path.rstrip("/")
        assert dirname in ruff_excludes
        assert dirname in pytest_norecursedirs
        assert dirname in mypy_exclude
