"""Inventario contractual de compatibilidad de librerías por backend oficial.

Este módulo centraliza una capa de adaptación estable para documentación, tests
integración y gates de CI. El objetivo es evitar que los consumidores dependan de
estructuras ad-hoc en distintos sitios del repositorio.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS

LIBRARY_AREAS: Final[tuple[str, ...]] = (
    "runtime",
    "parser",
    "serializacion",
    "red",
)

SEVERITY_ORDER: Final[dict[str, int]] = {
    "baja": 0,
    "media": 1,
    "alta": 2,
    "critica": 3,
}


@dataclass(frozen=True)
class LibraryCompatibilityRecord:
    """Contrato estable para exponer compatibilidad de librerías por backend."""

    level: str
    severity: str
    incompatibility: str
    workaround: str


LIBRARY_COMPATIBILITY: Final[dict[str, dict[str, LibraryCompatibilityRecord]]] = {
    "python": {
        "runtime": LibraryCompatibilityRecord(
            level="full",
            severity="baja",
            incompatibility="Ninguna en contrato oficial; usa runtime Python del proyecto.",
            workaround="No aplica.",
        ),
        "parser": LibraryCompatibilityRecord(
            level="full",
            severity="baja",
            incompatibility="Sin incompatibilidades contractuales con parser Lark.",
            workaround="No aplica.",
        ),
        "serializacion": LibraryCompatibilityRecord(
            level="full",
            severity="baja",
            incompatibility="Soporte completo con json/yaml/toml del runtime Python.",
            workaround="No aplica.",
        ),
        "red": LibraryCompatibilityRecord(
            level="full",
            severity="baja",
            incompatibility="Soporte completo con requests/httpx en runtime Python.",
            workaround="No aplica.",
        ),
    },
    "javascript": {
        "runtime": LibraryCompatibilityRecord(
            level="partial",
            severity="media",
            incompatibility="Adaptadores corelibs/standard_library sin paridad completa del SDK Python.",
            workaround="Usar solo primitivas cubiertas por adaptador cobraJsCorelibs/cobraJsStandardLibrary.",
        ),
        "parser": LibraryCompatibilityRecord(
            level="partial",
            severity="baja",
            incompatibility="Parsing ocurre en pCobra (Python), no hay parser JS equivalente publicado.",
            workaround="Transpilar desde AST generado por frontend Python oficial.",
        ),
        "serializacion": LibraryCompatibilityRecord(
            level="partial",
            severity="media",
            incompatibility="Serialización avanzada depende del host JS; cobertura mínima en contrato.",
            workaround="Limitarse a estructuras JSON planas en rutas transpiladas.",
        ),
        "red": LibraryCompatibilityRecord(
            level="partial",
            severity="media",
            incompatibility="No hay cliente HTTP oficial equivalente a requests/httpx en contrato JS.",
            workaround="Inyectar cliente de red del host y encapsular en plugin.",
        ),
    },
    "rust": {
        "runtime": LibraryCompatibilityRecord(
            level="partial",
            severity="media",
            incompatibility="Runtime adaptado; operaciones avanzadas Holobit devuelven error contractual.",
            workaround="Manejar Result explícitamente y evitar operaciones fuera del subset soportado.",
        ),
        "parser": LibraryCompatibilityRecord(
            level="partial",
            severity="baja",
            incompatibility="No existe parser Rust oficial; solo generación desde AST Python.",
            workaround="Mantener parsing en frontend pCobra.",
        ),
        "serializacion": LibraryCompatibilityRecord(
            level="partial",
            severity="media",
            incompatibility="No hay capa serde oficial expuesta por contrato.",
            workaround="Serializar/deserializar en frontera de host o vía FFI externa.",
        ),
        "red": LibraryCompatibilityRecord(
            level="partial",
            severity="alta",
            incompatibility="Sin API de red oficial equivalente en runtime Rust generado.",
            workaround="Delegar llamadas HTTP al host y pasar resultados al binario transpìlado.",
        ),
    },
}


def _diff_report(*, current: tuple[str, ...], expected: tuple[str, ...]) -> str:
    missing = tuple(target for target in expected if target not in current)
    extras = tuple(target for target in current if target not in expected)
    return f"missing={missing or '∅'}; extras={extras or '∅'}; current={current}; expected={expected}"


def validate_public_library_compatibility_keys() -> None:
    """Valida que la matriz pública coincida con los backends oficiales."""
    public_keys = tuple(LIBRARY_COMPATIBILITY)
    expected = tuple(OFFICIAL_TARGETS)
    if public_keys != expected or public_keys != tuple(PUBLIC_BACKENDS):
        raise RuntimeError(
            "LIBRARY_COMPATIBILITY debe exponer exactamente los backends públicos oficiales. "
            + _diff_report(current=public_keys, expected=expected)
        )
    for backend, areas in LIBRARY_COMPATIBILITY.items():
        area_keys = tuple(areas)
        if area_keys != LIBRARY_AREAS:
            raise RuntimeError(
                f"LIBRARY_COMPATIBILITY[{backend!r}] debe exponer exactamente LIBRARY_AREAS. "
                + _diff_report(current=area_keys, expected=LIBRARY_AREAS)
            )


validate_public_library_compatibility_keys()


def get_library_compatibility(backend: str, area: str) -> LibraryCompatibilityRecord:
    """Devuelve un registro estable para ``backend`` y ``area``."""
    if backend not in OFFICIAL_TARGETS:
        raise KeyError(f"Backend no oficial: {backend}")
    if area not in LIBRARY_AREAS:
        raise KeyError(f"Área no soportada: {area}")
    return LIBRARY_COMPATIBILITY[backend][area]


def highest_severity_for_backend(backend: str) -> str:
    """Retorna la severidad máxima detectada para un backend oficial."""
    if backend not in OFFICIAL_TARGETS:
        raise KeyError(f"Backend no oficial: {backend}")
    severities = [record.severity for record in LIBRARY_COMPATIBILITY[backend].values()]
    return max(severities, key=lambda sev: SEVERITY_ORDER[sev])
