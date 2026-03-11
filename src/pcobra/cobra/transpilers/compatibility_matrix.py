"""Matriz mínima de compatibilidad de transpiladores por tier.

Esta matriz documenta qué garantías ofrece cada backend para:
- primitivas Holobit (`holobit`, `proyectar`, `transformar`, `graficar`)
- imports base de runtime (`corelibs`, `standard_library`)

Niveles:
- ``full``: soportado y cubierto por regresión.
- ``partial``: soporte limitado (fallback o subconjunto).
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

__all__ = ["BACKEND_COMPATIBILITY"]
