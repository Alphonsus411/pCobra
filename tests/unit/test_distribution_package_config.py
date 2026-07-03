from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = ROOT / "pyproject.toml"
MANIFEST = ROOT / "MANIFEST.in"

_RESOURCE_PATTERNS = {
    "**/*.toml",
    "**/*.yaml",
    "**/*.yml",
    "**/*.json",
    "**/*.ini",
    "**/*.cfg",
    "**/*.md",
    "**/*.txt",
    "**/*.html",
    "**/*.j2",
    "**/*.template",
}


def test_cobra_installer_se_descubre_como_paquete_distribuido() -> None:
    """Evita regresiones que excluyan pcobra.cobra_installer del wheel."""

    config = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    setuptools_config = config["tool"]["setuptools"]

    assert setuptools_config["package-dir"] == {"": "src"}
    assert setuptools_config["packages"]["find"]["where"] == ["src"]
    assert "pcobra*" in setuptools_config["packages"]["find"]["include"]


def test_cobra_installer_declara_recursos_no_python_en_wheel_y_sdist() -> None:
    """Asegura recursos futuros de runtime/spec/templates en wheel y sdist."""

    config = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    package_data = config["tool"]["setuptools"]["package-data"]

    assert set(package_data["pcobra.cobra_installer"]) >= _RESOURCE_PATTERNS

    manifest = MANIFEST.read_text(encoding="utf-8")
    assert "recursive-include src/pcobra *.py" in manifest
    assert "recursive-include src/pcobra/cobra_installer" in manifest
    for suffix in ("*.toml", "*.yaml", "*.yml", "*.json", "*.j2", "*.template"):
        assert suffix in manifest
