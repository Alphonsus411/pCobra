"""Política de exposición de backends (públicos vs internos)."""

from __future__ import annotations

from typing import Final

# Superficie pública soportada por CLI y documentación.
PUBLIC_BACKENDS: Final[tuple[str, ...]] = (
    "python",
    "javascript",
    "rust",
)

# Backends legacy mantenidos para compatibilidad interna del registro.
INTERNAL_BACKENDS: Final[tuple[str, ...]] = (
    "go",
    "cpp",
    "java",
    "wasm",
    "asm",
)

ALL_BACKENDS: Final[tuple[str, ...]] = PUBLIC_BACKENDS + INTERNAL_BACKENDS

