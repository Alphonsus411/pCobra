"""Matriz de capacidades canónicas por módulo `usar`."""

from __future__ import annotations

from dataclasses import dataclass

from pcobra.cobra.usar_policy import CANONICAL_MODULE_SURFACE_CONTRACTS


@dataclass(frozen=True)
class ModuleCapabilityMatrix:
    """Define capacidades mínimas/opcionales y soporte por backend oficial."""

    required_functions: tuple[str, ...]
    optional_functions: tuple[str, ...]
    backend_support: dict[str, str]


_DEFAULT_BACKEND_SUPPORT: dict[str, str] = {
    "python": "full",
    "rust": "partial",
    "javascript": "partial",
}

MODULE_CAPABILITY_MATRIX: dict[str, ModuleCapabilityMatrix] = {
    module: ModuleCapabilityMatrix(
        required_functions=contract.required_functions,
        optional_functions=tuple(),
        backend_support=dict(_DEFAULT_BACKEND_SUPPORT),
    )
    for module, contract in CANONICAL_MODULE_SURFACE_CONTRACTS.items()
}


for _module, _cap in MODULE_CAPABILITY_MATRIX.items():
    if tuple(_cap.required_functions) != tuple(CANONICAL_MODULE_SURFACE_CONTRACTS[_module].required_functions):
        raise RuntimeError(
            f"[STARTUP CONTRACT] Matriz de capacidades desalineada para módulo canónico: {_module}."
        )


__all__ = ["ModuleCapabilityMatrix", "MODULE_CAPABILITY_MATRIX"]
