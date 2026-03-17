"""Matriz mínima de compatibilidad de transpiladores por tier.

Esta matriz documenta qué garantías ofrece cada backend para:
- primitivas Holobit (`holobit`, `proyectar`, `transformar`, `graficar`)
- imports base de runtime (`corelibs`, `standard_library`)

Niveles:
- ``full``: soportado con aserciones estrictas (símbolos/hooks/imports esperados).
- ``partial``: soporte limitado validado por fallback explícito y no rotura de generación.
- ``none``: no garantizado por backend.
"""

from __future__ import annotations

from typing import Final

from pcobra.cobra.transpilers.targets import normalize_target_name

BACKEND_COMPATIBILITY: Final[dict[str, dict[str, str]]] = {
    "python": {
        "tier": "tier1",
        "holobit": "full",
        "proyectar": "full",
        "transformar": "full",
        "graficar": "full",
        "corelibs": "full",
        "standard_library": "full",
    },
    "javascript": {
        "tier": "tier1",
        "holobit": "full",
        "proyectar": "full",
        "transformar": "full",
        "graficar": "full",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "rust": {
        "tier": "tier1",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "wasm": {
        "tier": "tier1",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "go": {
        "tier": "tier2",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "cpp": {
        "tier": "tier2",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "java": {
        "tier": "tier2",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "asm": {
        "tier": "tier2",
        "holobit": "partial",
        "proyectar": "none",
        "transformar": "none",
        "graficar": "none",
        "corelibs": "partial",
        "standard_library": "partial",
    },
}


# Piso contractual: nivel mínimo que cada backend debe mantener por feature.
# Si BACKEND_COMPATIBILITY baja por debajo de este umbral, debe considerarse regresión.
MIN_REQUIRED_BACKEND_COMPATIBILITY: Final[dict[str, dict[str, str]]] = {
    "python": {
        "tier": "tier1",
        "holobit": "full",
        "proyectar": "full",
        "transformar": "full",
        "graficar": "full",
        "corelibs": "full",
        "standard_library": "full",
    },
    "javascript": {
        "tier": "tier1",
        "holobit": "full",
        "proyectar": "full",
        "transformar": "full",
        "graficar": "full",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "rust": {
        "tier": "tier1",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "wasm": {
        "tier": "tier1",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "go": {
        "tier": "tier2",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "cpp": {
        "tier": "tier2",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "java": {
        "tier": "tier2",
        "holobit": "partial",
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
    "asm": {
        "tier": "tier2",
        "holobit": "partial",
        "proyectar": "none",
        "transformar": "none",
        "graficar": "none",
        "corelibs": "partial",
        "standard_library": "partial",
    },
}

COMPATIBILITY_LEVEL_ORDER: Final[dict[str, int]] = {"none": 0, "partial": 1, "full": 2}


BACKEND_COMPATIBILITY_NOTES: Final[dict[str, dict[str, str]]] = {
    "python": {
        "contract": "full",
        "evidence": "Imports explícitos (`corelibs`, `standard_library`) + llamadas a hooks `cobra_*` con firmas consistentes para primitivas Holobit.",
    },
    "javascript": {
        "contract": "mixed",
        "evidence": "Primitivas Holobit en JS resueltas con hooks explícitos `cobra_*` inyectados en codegen; `corelibs` y `standard_library` quedan en passthrough JS (sin quoting/semántica completa).",
    },
    "rust": {
        "contract": "partial",
        "evidence": "Hooks `cobra_*` para primitivas Holobit y llamadas passthrough (`longitud(cobra)`, `mostrar(hola)`).",
    },
    "wasm": {
        "contract": "partial",
        "evidence": "Llamadas WAT explícitas a hooks `cobra_*`; cuando el runtime no está implementado, los hooks ejecutan `unreachable` (error explícito, sin no-op).",
    },
    "go": {
        "contract": "partial",
        "evidence": "Hooks `cobra*` para primitivas y passthrough de runtime base (`longitud`/`mostrar`).",
    },
    "cpp": {
        "contract": "partial",
        "evidence": "Hooks inline `cobra_*` para primitivas y passthrough de runtime base.",
    },
    "java": {
        "contract": "partial",
        "evidence": "Hooks estáticos `cobra*` para primitivas y passthrough de runtime base.",
    },
    "asm": {
        "contract": "mixed",
        "evidence": "`holobit` se emite como instrucción ASM/IR; `proyectar`/`transformar`/`graficar` fallan con `NotImplementedError` explícito. Las llamadas `CALL` conservan argumentos.",
    },
}

def get_backend_compatibility(backend: str) -> dict[str, str] | None:
    """Obtiene compatibilidad por backend aplicando normalización canónica."""
    return BACKEND_COMPATIBILITY.get(normalize_target_name(backend, allow_legacy_aliases=True))


def get_backend_compatibility_notes(backend: str) -> dict[str, str] | None:
    """Obtiene notas de compatibilidad por backend con normalización."""
    return BACKEND_COMPATIBILITY_NOTES.get(normalize_target_name(backend, allow_legacy_aliases=True))


__all__ = [
    "BACKEND_COMPATIBILITY",
    "MIN_REQUIRED_BACKEND_COMPATIBILITY",
    "COMPATIBILITY_LEVEL_ORDER",
    "BACKEND_COMPATIBILITY_NOTES",
    "get_backend_compatibility",
    "get_backend_compatibility_notes",
]
