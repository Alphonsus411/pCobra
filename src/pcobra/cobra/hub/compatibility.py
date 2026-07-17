"""Compatibilidad de versiones entre CobraHub y el runtime Cobra instalado."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version as distribution_version
from pathlib import Path
import re
import tomllib

from packaging.version import Version


_VERSION_CONSTRAINT_RE = re.compile(
    r"(?:>=|<=|>|<|==|!=)?"
    r"(?:0|[1-9]\d*)(?:\.(?:0|[1-9]\d*)){0,2}"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
)
_COMPARATOR_RE = re.compile(r"(>=|<=|>|<|==|!=)?(.+)")


def validate_version_constraint(value: object, field_name: str) -> str:
    """Valida exclusivamente la intersección de comparadores admitida por Hub."""
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} debe ser una restricción de versiones válida")
    clauses = value.split(",")
    if not clauses or not all(
        clause == clause.strip() and _VERSION_CONSTRAINT_RE.fullmatch(clause)
        for clause in clauses
    ):
        raise ValueError(f"{field_name} debe ser una restricción de versiones válida")
    return value


def cobra_version_satisfies(current_version: str, constraint: str) -> bool:
    """Evalúa una restricción Hub ya validada contra una versión Cobra exacta."""
    validated = validate_version_constraint(constraint, "requires_cobra")
    current = Version(current_version)
    operations = {
        "==": lambda required: current == required,
        "!=": lambda required: current != required,
        ">=": lambda required: current >= required,
        "<=": lambda required: current <= required,
        ">": lambda required: current > required,
        "<": lambda required: current < required,
    }
    for clause in validated.split(","):
        match = _COMPARATOR_RE.fullmatch(clause)
        assert match is not None
        operator = match.group(1) or "=="
        if not operations[operator](Version(match.group(2))):
            return False
    return True


def installed_cobra_version() -> str:
    """Devuelve la versión de la distribución Cobra instalada."""
    try:
        return distribution_version("pcobra")
    except PackageNotFoundError:
        pyproject_path = Path(__file__).resolve().parents[4] / "pyproject.toml"
        project = tomllib.loads(pyproject_path.read_text(encoding="utf-8")).get(
            "project", {}
        )
        version = project.get("version") if isinstance(project, dict) else None
        if not version:
            raise
        return str(version)
