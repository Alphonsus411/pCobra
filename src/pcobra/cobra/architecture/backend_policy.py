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


def assert_public_command_uses_only_public_backends(*, command: str, targets: tuple[str, ...]) -> None:
    """Falla si un comando público consume cualquier backend fuera de PUBLIC_BACKENDS."""
    legacy_targets = tuple(target for target in targets if target not in PUBLIC_BACKENDS)
    if legacy_targets:
        raise RuntimeError(
            "[PUBLIC CONTRACT] Comando público fuera de contrato: "
            f"command={command}; legacy={legacy_targets}; allowed={PUBLIC_BACKENDS}"
        )
