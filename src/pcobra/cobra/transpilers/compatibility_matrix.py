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
        "evidence": "Imports explícitos (`corelibs`, `standard_library`) + llamadas directas a primitivas Holobit.",
    },
    "js": {
        "contract": "mixed",
        "evidence": "Holobit/proyección/transformación/graficado con símbolos directos; `corelibs` y `standard_library` quedan en passthrough JS (sin quoting/semántica completa).",
    },
    "rust": {
        "contract": "partial",
        "evidence": "Hooks `cobra_*` para primitivas Holobit y llamadas passthrough (`longitud(cobra)`, `mostrar(hola)`).",
    },
    "wasm": {
        "contract": "partial",
        "evidence": "Fallback explícito por comentarios/hooks de runtime (`;; runtime hook` / `;; call runtime`).",
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
        "contract": "partial",
        "evidence": "Fallback por hooks/comentarios (`Nodo ... no soportado`) y `CALL` para runtime base.",
    },
}

__all__ = ["BACKEND_COMPATIBILITY", "BACKEND_COMPATIBILITY_NOTES"]
