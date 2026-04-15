"""Registro canónico de transpiladores oficiales."""

from __future__ import annotations

from importlib import import_module
from typing import Final

from pcobra.cobra.architecture.backend_policy import (
    ALL_BACKENDS,
    INTERNAL_BACKENDS,
    PUBLIC_BACKENDS,
)
from pcobra.cobra.architecture.legacy_backend_lifecycle import (
    lifecycle_status_for_backend,
)
from pcobra.cobra.config.transpile_targets import OFFICIAL_TARGETS

TRANSPILER_CLASS_PATHS: Final[dict[str, tuple[str, str]]] = {
    "python": ("pcobra.cobra.transpilers.transpiler.to_python", "TranspiladorPython"),
    "javascript": ("pcobra.cobra.transpilers.transpiler.to_js", "TranspiladorJavaScript"),
    "rust": ("pcobra.cobra.transpilers.transpiler.to_rust", "TranspiladorRust"),
    "go": ("pcobra.cobra.transpilers.transpiler.to_go", "TranspiladorGo"),
    "cpp": ("pcobra.cobra.transpilers.transpiler.to_cpp", "TranspiladorCPP"),
    "java": ("pcobra.cobra.transpilers.transpiler.to_java", "TranspiladorJava"),
    "wasm": ("pcobra.cobra.transpilers.transpiler.to_wasm", "TranspiladorWasm"),
    "asm": ("pcobra.cobra.transpilers.transpiler.to_asm", "TranspiladorASM"),
}


PUBLIC_TRANSPILER_CLASS_PATHS: Final[dict[str, tuple[str, str]]] = {
    target: TRANSPILER_CLASS_PATHS[target] for target in PUBLIC_BACKENDS
}

INTERNAL_LEGACY_TRANSPILER_CLASS_PATHS: Final[dict[str, tuple[str, str]]] = {
    target: TRANSPILER_CLASS_PATHS[target] for target in INTERNAL_BACKENDS
}
INTERNAL_LEGACY_TRANSPILER_LIFECYCLE_STATUS: Final[
    dict[str, str]
] = {
    target: lifecycle_status_for_backend(target)
    for target in INTERNAL_BACKENDS
}


def _validate_complete_registry_contract() -> tuple[str, ...]:
    """Valida que el inventario completo preserve el contrato total de backends."""
    configured_keys = tuple(TRANSPILER_CLASS_PATHS)
    missing = tuple(target for target in ALL_BACKENDS if target not in configured_keys)
    extras = tuple(target for target in configured_keys if target not in ALL_BACKENDS)

    if missing or extras:
        raise RuntimeError(
            "[CI CONTRACT] TRANSPILER_CLASS_PATHS tiene claves fuera de contrato y debe usar exactamente ALL_BACKENDS. "
            f"missing={missing or '∅'}; extras={extras or '∅'}; "
            f"current={configured_keys}; expected={ALL_BACKENDS}"
        )

    if len(configured_keys) != len(ALL_BACKENDS):
        raise RuntimeError(
            "[CI CONTRACT] TRANSPILER_CLASS_PATHS tiene cardinalidad inválida. "
            f"len(current)={len(configured_keys)}; len(expected)={len(ALL_BACKENDS)}; "
            f"current={configured_keys}; expected={ALL_BACKENDS}"
        )

    if configured_keys != ALL_BACKENDS:
        raise RuntimeError(
            "[CI CONTRACT] TRANSPILER_CLASS_PATHS debe preservar el orden de backend_policy.ALL_BACKENDS. "
            f"current={configured_keys}; expected={ALL_BACKENDS}"
        )
    return configured_keys


def _validate_public_registry_contract() -> tuple[str, ...]:
    """Valida contrato estricto del registro público frente a OFFICIAL_TARGETS/PUBLIC_BACKENDS."""
    if OFFICIAL_TARGETS != PUBLIC_BACKENDS:
        raise RuntimeError(
            "[CI CONTRACT] OFFICIAL_TARGETS debe ser equivalente a PUBLIC_BACKENDS para rutas públicas. "
            f"official={OFFICIAL_TARGETS}; public={PUBLIC_BACKENDS}"
        )

    configured_keys = tuple(PUBLIC_TRANSPILER_CLASS_PATHS)
    missing = tuple(target for target in PUBLIC_BACKENDS if target not in configured_keys)
    extras = tuple(target for target in configured_keys if target not in PUBLIC_BACKENDS)

    if missing or extras:
        raise RuntimeError(
            "[CI CONTRACT] PUBLIC_TRANSPILER_CLASS_PATHS debe usar exactamente PUBLIC_BACKENDS. "
            f"missing={missing or '∅'}; extras={extras or '∅'}; "
            f"current={configured_keys}; expected={PUBLIC_BACKENDS}"
        )

    if configured_keys != PUBLIC_BACKENDS:
        raise RuntimeError(
            "[CI CONTRACT] PUBLIC_TRANSPILER_CLASS_PATHS debe preservar el orden de backend_policy.PUBLIC_BACKENDS. "
            f"current={configured_keys}; expected={PUBLIC_BACKENDS}"
        )
    return configured_keys


def _validate_internal_legacy_registry_contract() -> tuple[str, ...]:
    """Valida inventario separado para backends legacy internos."""
    configured_keys = tuple(INTERNAL_LEGACY_TRANSPILER_CLASS_PATHS)
    missing = tuple(
        target for target in INTERNAL_BACKENDS if target not in configured_keys
    )
    extras = tuple(
        target for target in configured_keys if target not in INTERNAL_BACKENDS
    )

    if missing or extras:
        raise RuntimeError(
            "[CI CONTRACT] INTERNAL_LEGACY_TRANSPILER_CLASS_PATHS debe usar exactamente INTERNAL_BACKENDS. "
            f"missing={missing or '∅'}; extras={extras or '∅'}; "
            f"current={configured_keys}; expected={INTERNAL_BACKENDS}"
        )

    if configured_keys != INTERNAL_BACKENDS:
        raise RuntimeError(
            "[CI CONTRACT] INTERNAL_LEGACY_TRANSPILER_CLASS_PATHS debe preservar el orden de backend_policy.INTERNAL_BACKENDS. "
            f"current={configured_keys}; expected={INTERNAL_BACKENDS}"
        )
    return configured_keys


_ORDERED_ALL_TARGETS: Final[tuple[str, ...]] = _validate_complete_registry_contract()
_ORDERED_OFFICIAL_TARGETS: Final[tuple[str, ...]] = _validate_public_registry_contract()
_ORDERED_INTERNAL_LEGACY_TARGETS: Final[tuple[str, ...]] = (
    _validate_internal_legacy_registry_contract()
)


def ordered_official_transpiler_paths() -> tuple[tuple[str, tuple[str, str]], ...]:
    """Devuelve el registro público en el orden de ``OFFICIAL_TARGETS``."""
    return tuple(
        (target, PUBLIC_TRANSPILER_CLASS_PATHS[target])
        for target in _ORDERED_OFFICIAL_TARGETS
    )


def ordered_internal_legacy_transpiler_paths() -> tuple[tuple[str, tuple[str, str]], ...]:
    """Devuelve el inventario legacy interno en orden contractual."""
    return tuple(
        (target, INTERNAL_LEGACY_TRANSPILER_CLASS_PATHS[target])
        for target in _ORDERED_INTERNAL_LEGACY_TARGETS
    )


def ordered_internal_legacy_transpiler_entries() -> tuple[tuple[str, tuple[str, str], str], ...]:
    """Devuelve inventario interno legacy con etiqueta de estado lifecycle."""
    return tuple(
        (
            target,
            INTERNAL_LEGACY_TRANSPILER_CLASS_PATHS[target],
            INTERNAL_LEGACY_TRANSPILER_LIFECYCLE_STATUS[target],
        )
        for target in _ORDERED_INTERNAL_LEGACY_TARGETS
    )


def build_official_transpilers() -> dict[str, type]:
    """Carga las clases públicas oficiales desde el registro público."""
    registry: dict[str, type] = {}
    for target, (module_name, class_name) in ordered_official_transpiler_paths():
        module = import_module(module_name)
        registry[target] = getattr(module, class_name)
    return registry


def build_internal_legacy_transpilers() -> dict[str, type]:
    """Carga las clases legacy internas para procesos de migración interna."""
    registry: dict[str, type] = {}
    for target, (module_name, class_name) in ordered_internal_legacy_transpiler_paths():
        module = import_module(module_name)
        registry[target] = getattr(module, class_name)
    return registry


def official_transpiler_targets() -> tuple[str, ...]:
    """Devuelve los targets del registro público en el orden contractual."""
    return _ORDERED_OFFICIAL_TARGETS


def official_transpiler_module_filenames() -> tuple[str, ...]:
    """Devuelve los nombres de archivo ``to_*.py`` canónicos del registro oficial."""
    return tuple(
        module_name.rsplit(".", 1)[-1] + ".py"
        for _, (module_name, _) in ordered_official_transpiler_paths()
    )


def official_transpiler_registry_literal() -> dict[str, tuple[str, str]]:
    """Devuelve el literal esperado del registro canónico para auditorías."""
    return {target: value for target, value in ordered_official_transpiler_paths()}
