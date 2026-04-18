"""Política normativa de backends (públicos vs internos).

Fuente canónica contractual única para política de backends públicos/legacy.
"""

from __future__ import annotations

from typing import Final

# Cobra es la única interfaz pública soportada para usuarios e integraciones.
PUBLIC_INTERFACE_NAME: Final[str] = "cobra"

# Superficie pública soportada por CLI y documentación de usuario.
PUBLIC_BACKENDS: Final[tuple[str, ...]] = (
    "python",
    "javascript",
    "rust",
)

# Criterio de salida: toda API pública o doc de usuario solo puede listar 3 targets.
PUBLIC_TARGET_LISTING_LIMIT: Final[int] = 3

# Backends legacy mantenidos exclusivamente para compatibilidad interna.
INTERNAL_BACKENDS: Final[tuple[str, ...]] = (
    "go",
    "cpp",
    "java",
    "wasm",
    "asm",
)

# Ventana de retiro contractual para compatibilidad interna no pública.
INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW: Final[dict[str, str]] = {
    "go": "Q4 2026",
    "cpp": "Q4 2026",
    "java": "Q1 2027",
    "wasm": "Q2 2027",
    "asm": "Q3 2026",
}

# Fecha de corte global para retirar la compatibilidad legacy internal-only.
INTERNAL_LEGACY_RETIREMENT_DATE: Final[str] = "2027-06-30"

ALL_BACKENDS: Final[tuple[str, ...]] = PUBLIC_BACKENDS + INTERNAL_BACKENDS


def assert_public_targets_contract(targets: tuple[str, ...], *, source: str) -> None:
    """Valida que una superficie pública cumpla el contrato oficial de 3 targets."""
    if len(targets) != PUBLIC_TARGET_LISTING_LIMIT:
        raise RuntimeError(
            "[PUBLIC CONTRACT] Toda API pública o doc de usuario debe listar exactamente "
            f"{PUBLIC_TARGET_LISTING_LIMIT} targets. source={source}; targets={targets}"
        )

    if targets != PUBLIC_BACKENDS:
        raise RuntimeError(
            "[PUBLIC CONTRACT] La superficie pública debe usar exactamente PUBLIC_BACKENDS. "
            f"source={source}; current={targets}; expected={PUBLIC_BACKENDS}"
        )
