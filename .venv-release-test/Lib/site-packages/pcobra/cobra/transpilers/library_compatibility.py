"""Inventario contractual de compatibilidad de librerías por backend oficial.

Este módulo centraliza una capa de adaptación estable para documentación, tests
integración y gates de CI. El objetivo es evitar que los consumidores dependan de
estructuras ad-hoc en distintos sitios del repositorio.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

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
    "wasm": {
        "runtime": LibraryCompatibilityRecord(
            level="partial",
            severity="alta",
            incompatibility="Dependencia contractual del host-managed runtime (pcobra:* imports).",
            workaround="Implementar host runtime completo antes de ejecución.",
        ),
        "parser": LibraryCompatibilityRecord(
            level="none",
            severity="media",
            incompatibility="No se distribuye parser WASM oficial.",
            workaround="Parsear en pCobra y enviar AST/IR al módulo WASM.",
        ),
        "serializacion": LibraryCompatibilityRecord(
            level="partial",
            severity="alta",
            incompatibility="Serialización depende del protocolo de handles del host.",
            workaround="Definir ABI host estable y validar buffers en integración.",
        ),
        "red": LibraryCompatibilityRecord(
            level="none",
            severity="alta",
            incompatibility="Sin red directa en contrato WASM de pCobra.",
            workaround="Proxy de red en host con imports explícitos.",
        ),
    },
    "go": {
        "runtime": LibraryCompatibilityRecord(
            level="partial",
            severity="media",
            incompatibility="Runtime best-effort; operaciones fuera del adaptador hacen panic.",
            workaround="Restringir features a subset contractual y envolver ejecución en proceso supervisor.",
        ),
        "parser": LibraryCompatibilityRecord(
            level="none",
            severity="media",
            incompatibility="No hay parser Go oficial para código fuente Cobra.",
            workaround="Mantener parser en frontend Python.",
        ),
        "serializacion": LibraryCompatibilityRecord(
            level="partial",
            severity="media",
            incompatibility="Sin contrato público de serialización más allá de tipos básicos.",
            workaround="Usar JSON básico y validar forma antes de invocar runtime.",
        ),
        "red": LibraryCompatibilityRecord(
            level="none",
            severity="alta",
            incompatibility="No existe API de red oficial del runtime Go de pCobra.",
            workaround="Implementar red fuera del runtime y pasar datos por stdin/archivos.",
        ),
    },
    "cpp": {
        "runtime": LibraryCompatibilityRecord(
            level="partial",
            severity="media",
            incompatibility="Runtime oficial parcial, sin paridad SDK Python completa.",
            workaround="Mantenerse en operaciones core del adaptador C++.",
        ),
        "parser": LibraryCompatibilityRecord(
            level="none",
            severity="media",
            incompatibility="No hay parser C++ oficial del lenguaje Cobra.",
            workaround="Compilar siempre desde frontend pCobra Python.",
        ),
        "serializacion": LibraryCompatibilityRecord(
            level="partial",
            severity="media",
            incompatibility="Sin capa de serialización estándar expuesta contractualmente.",
            workaround="Integrar librería de serialización del host (ej. JSON) en frontera C++.",
        ),
        "red": LibraryCompatibilityRecord(
            level="none",
            severity="alta",
            incompatibility="No se incluye stack de red en runtime C++ oficial.",
            workaround="Delegar red al host/aplicación embebedora.",
        ),
    },
    "java": {
        "runtime": LibraryCompatibilityRecord(
            level="partial",
            severity="media",
            incompatibility="Runtime best-effort con UnsupportedOperationException en operaciones no cubiertas.",
            workaround="Controlar excepciones y usar solo subset contractual.",
        ),
        "parser": LibraryCompatibilityRecord(
            level="none",
            severity="media",
            incompatibility="Sin parser Java oficial para Cobra.",
            workaround="Mantener parsing en frontend Python.",
        ),
        "serializacion": LibraryCompatibilityRecord(
            level="partial",
            severity="media",
            incompatibility="No existe API Java oficial de serialización avanzada.",
            workaround="Serializar en host Java fuera del runtime transpìlado.",
        ),
        "red": LibraryCompatibilityRecord(
            level="none",
            severity="alta",
            incompatibility="Sin API de red oficial en contrato Java de pCobra.",
            workaround="Consumir APIs de red Java desde código anfitrión y no desde runtime pCobra.",
        ),
    },
    "asm": {
        "runtime": LibraryCompatibilityRecord(
            level="partial",
            severity="alta",
            incompatibility="Runtime solo de inspección/diagnóstico con TRAP para operaciones avanzadas.",
            workaround="Usar backend ASM solo para auditoría/transpilación, no ejecución funcional completa.",
        ),
        "parser": LibraryCompatibilityRecord(
            level="none",
            severity="media",
            incompatibility="No aplica parser ASM para Cobra.",
            workaround="Parsear y analizar siempre en frontend Python.",
        ),
        "serializacion": LibraryCompatibilityRecord(
            level="none",
            severity="alta",
            incompatibility="Sin serialización oficial en backend ASM.",
            workaround="Resolver serialización fuera del backend.",
        ),
        "red": LibraryCompatibilityRecord(
            level="none",
            severity="critica",
            incompatibility="Sin stack de red ni llamadas host estandarizadas en contrato ASM.",
            workaround="No usar ASM para casos con IO/red; mover flujo a host.",
        ),
    },
}


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
