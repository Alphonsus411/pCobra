"""Inventario legacy interno, aislado del startup path oficial."""

from __future__ import annotations

from importlib import import_module
from typing import Final

INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS: Final[dict[str, tuple[str, str]]] = {
    "go": ("pcobra.cobra.transpilers.transpiler.legacy.to_go", "TranspiladorGo"),
    "cpp": ("pcobra.cobra.transpilers.transpiler.legacy.to_cpp", "TranspiladorCPP"),
    "java": ("pcobra.cobra.transpilers.transpiler.legacy.to_java", "TranspiladorJava"),
    "wasm": ("pcobra.cobra.transpilers.transpiler.legacy.to_wasm", "TranspiladorWasm"),
    "asm": ("pcobra.cobra.transpilers.transpiler.legacy.to_asm", "TranspiladorASM"),
}

INTERNAL_LEGACY_TRANSPILER_CLASS_PATHS: Final[dict[str, tuple[str, str]]] = (
    INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS
)

_ORDERED_INTERNAL_LEGACY_TARGETS_CACHE: tuple[str, ...] | None = None


def _internal_compat_legacy_contracts():
    """Carga diferida de contratos legacy internos (no públicos)."""
    from pcobra.cobra.internal_compat.legacy_contracts import (
        INTERNAL_BACKENDS,
        INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW,
        lifecycle_status_for_backend,
    )

    return {
        "INTERNAL_BACKENDS": INTERNAL_BACKENDS,
        "INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW": INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW,
        "lifecycle_status_for_backend": lifecycle_status_for_backend,
    }


def _validate_internal_legacy_registry_contract() -> tuple[str, ...]:
    """Valida inventario separado para backends legacy internos."""
    contracts = _internal_compat_legacy_contracts()
    internal_backends = contracts["INTERNAL_BACKENDS"]
    internal_retirement_window = contracts["INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW"]

    configured_keys = tuple(INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS)
    missing = tuple(
        target for target in internal_backends if target not in configured_keys
    )
    extras = tuple(
        target for target in configured_keys if target not in internal_backends
    )

    if missing or extras:
        raise RuntimeError(
            "[CI CONTRACT] INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS debe usar exactamente INTERNAL_BACKENDS. "
            f"missing={missing or '∅'}; extras={extras or '∅'}; "
            f"current={configured_keys}; expected={internal_backends}"
        )

    lifecycle_keys = set(internal_retirement_window)
    internal_keys = set(internal_backends)
    if lifecycle_keys != internal_keys:
        extras = tuple(sorted(lifecycle_keys - internal_keys))
        missing = tuple(sorted(internal_keys - lifecycle_keys))
        raise RuntimeError(
            "[CI CONTRACT] INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW debe cubrir "
            "exactamente INTERNAL_BACKENDS. "
            f"missing={missing or '∅'}; extras={extras or '∅'}"
        )

    if configured_keys != internal_backends:
        raise RuntimeError(
            "[CI CONTRACT] INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS debe preservar el orden de backend_policy.INTERNAL_BACKENDS. "
            f"current={configured_keys}; expected={internal_backends}"
        )
    return configured_keys


def _ordered_internal_legacy_targets() -> tuple[str, ...]:
    """Resuelve y cachea el orden de backends legacy internos de forma lazy."""
    global _ORDERED_INTERNAL_LEGACY_TARGETS_CACHE
    if _ORDERED_INTERNAL_LEGACY_TARGETS_CACHE is None:
        _ORDERED_INTERNAL_LEGACY_TARGETS_CACHE = _validate_internal_legacy_registry_contract()
    return _ORDERED_INTERNAL_LEGACY_TARGETS_CACHE


def ordered_internal_legacy_transpiler_paths() -> tuple[tuple[str, tuple[str, str]], ...]:
    """Devuelve el inventario legacy interno en orden contractual."""
    return tuple(
        (target, INTERNAL_LEGACY_TRANSPILER_CLASS_PATHS[target])
        for target in _ordered_internal_legacy_targets()
    )


def ordered_internal_legacy_transpiler_entries() -> tuple[tuple[str, tuple[str, str], str], ...]:
    """Devuelve inventario interno legacy con etiqueta de estado lifecycle."""
    contracts = _internal_compat_legacy_contracts()
    lifecycle_status_for_backend = contracts["lifecycle_status_for_backend"]
    return tuple(
        (
            target,
            INTERNAL_LEGACY_TRANSPILER_CLASS_PATHS[target],
            lifecycle_status_for_backend(target),
        )
        for target in _ordered_internal_legacy_targets()
    )


def build_internal_legacy_transpilers() -> dict[str, type]:
    """Carga las clases legacy internas para procesos de migración interna."""
    registry: dict[str, type] = {}
    for target, (module_name, class_name) in ordered_internal_legacy_transpiler_paths():
        module = import_module(module_name)
        registry[target] = getattr(module, class_name)
    return registry
