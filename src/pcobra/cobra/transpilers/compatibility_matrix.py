"""Matriz mínima de compatibilidad de transpiladores por tier.

Esta matriz documenta qué garantías ofrece cada backend para:
- primitivas Holobit (`holobit`, `proyectar`, `transformar`, `graficar`)
- imports base de runtime (`corelibs`, `standard_library`)

Niveles:
- ``full``: soportado y cubierto por regresión.
- ``partial``: soporte limitado (fallback explícito, hooks o passthrough sin semántica completa).
- ``none``: no garantizado por backend.
"""

from __future__ import annotations

from typing import Final

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
    "js": {
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
        "proyectar": "partial",
        "transformar": "partial",
        "graficar": "partial",
        "corelibs": "partial",
        "standard_library": "partial",
    },
}


BACKEND_COMPATIBILITY_NOTES: Final[dict[str, dict[str, str]]] = {
    "python": {
        "contract": "full",
        "evidence": "Emite imports de corelibs/standard_library y llamadas directas a primitivas Holobit.",
    },
    "js": {
        "contract": "mixed",
        "evidence": "Holobit completo; corelibs/standard_library en modo parcial con runtime JS nativo.",
    },
    "rust": {
        "contract": "partial",
        "evidence": "Primitivas Holobit vía hooks cobra_* y llamadas runtime passthrough para librerías.",
    },
    "wasm": {
        "contract": "partial",
        "evidence": "Soporte por comentarios/hooks de runtime (fallback explícito).",
    },
    "go": {
        "contract": "partial",
        "evidence": "Hooks cobra* para primitivas y llamadas passthrough a librerías.",
    },
    "cpp": {
        "contract": "partial",
        "evidence": "Hooks cobra_* inline para primitivas y llamadas passthrough a librerías.",
    },
    "java": {
        "contract": "partial",
        "evidence": "Hooks cobra* estáticos para primitivas y llamadas passthrough a librerías.",
    },
    "asm": {
        "contract": "partial",
        "evidence": "Fallback por hooks/comentarios y llamadas CALL para runtime base.",
    },
}

__all__ = ["BACKEND_COMPATIBILITY", "BACKEND_COMPATIBILITY_NOTES"]
