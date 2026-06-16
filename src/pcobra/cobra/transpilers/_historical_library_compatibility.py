"""Compatibilidad histórica de librerías para backends retirados.

Módulo interno no público. Estas referencias se conservan solo como archivo de
migración/regresión y no forman parte de la matriz oficial publicada por
``library_compatibility.LIBRARY_COMPATIBILITY``.
"""

from __future__ import annotations

from typing import Final

from pcobra.cobra.transpilers.library_compatibility import LibraryCompatibilityRecord

HISTORICAL_LIBRARY_COMPATIBILITY: Final[dict[str, dict[str, LibraryCompatibilityRecord]]] = {
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


__all__ = ("HISTORICAL_LIBRARY_COMPATIBILITY",)
