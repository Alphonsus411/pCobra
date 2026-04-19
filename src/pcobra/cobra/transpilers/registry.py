"""Registro canónico de transpiladores oficiales."""

from __future__ import annotations

from importlib import import_module
from typing import Final

from pcobra.cobra.architecture.backend_policy import (
    ALL_BACKENDS,
    PUBLIC_BACKENDS,
    assert_public_targets_contract,
)
from pcobra.cobra.internal_compat.legacy_contracts import (
    INTERNAL_BACKENDS,
    INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW,
    lifecycle_status_for_backend,
)
from pcobra.cobra.config.transpile_targets import OFFICIAL_TARGETS

TRANSPILER_CLASS_PATHS: Final[dict[str, tuple[str, str]]] = {
    "python": ("pcobra.cobra.transpilers.transpiler.to_python", "TranspiladorPython"),
    "javascript": ("pcobra.cobra.transpilers.transpiler.to_js", "TranspiladorJavaScript"),
    "rust": ("pcobra.cobra.transpilers.transpiler.to_rust", "TranspiladorRust"),
}

# Bloque dedicado de compatibilidad interna (no público).
INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS: Final[dict[str, tuple[str, str]]] = {
    "go": ("pcobra.cobra.transpilers.transpiler.to_go", "TranspiladorGo"),
    "cpp": ("pcobra.cobra.transpilers.transpiler.to_cpp", "TranspiladorCPP"),
    "java": ("pcobra.cobra.transpilers.transpiler.to_java", "TranspiladorJava"),
    "wasm": ("pcobra.cobra.transpilers.transpiler.to_wasm", "TranspiladorWasm"),
    "asm": ("pcobra.cobra.transpilers.transpiler.to_asm", "TranspiladorASM"),
}

PUBLIC_TRANSPILER_CLASS_PATHS: Final[dict[str, tuple[str, str]]] = TRANSPILER_CLASS_PATHS

# Alias explícito para continuidad semántica en módulos/tests internos.
INTERNAL_LEGACY_TRANSPILER_CLASS_PATHS: Final[dict[str, tuple[str, str]]] = (
    INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS
)
INTERNAL_LEGACY_TRANSPILER_LIFECYCLE_STATUS: Final[
    dict[str, str]
] = {
    target: lifecycle_status_for_backend(target)
    for target in INTERNAL_BACKENDS
}


def _validate_complete_registry_contract() -> tuple[str, ...]:
    """Valida que el inventario completo preserve el contrato total de backends."""
    configured_keys = tuple(TRANSPILER_CLASS_PATHS) + tuple(
        INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS
    )
    missing = tuple(target for target in ALL_BACKENDS if target not in configured_keys)
    extras = tuple(target for target in configured_keys if target not in ALL_BACKENDS)

    if missing or extras:
        raise RuntimeError(
            "[CI CONTRACT] TRANSPILER_CLASS_PATHS + INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS tienen claves fuera de contrato y deben usar exactamente ALL_BACKENDS. "
            f"missing={missing or '∅'}; extras={extras or '∅'}; "
            f"current={configured_keys}; expected={ALL_BACKENDS}"
        )

    if len(configured_keys) != len(ALL_BACKENDS):
        raise RuntimeError(
            "[CI CONTRACT] TRANSPILER_CLASS_PATHS + INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS tienen cardinalidad inválida. "
            f"len(current)={len(configured_keys)}; len(expected)={len(ALL_BACKENDS)}; "
            f"current={configured_keys}; expected={ALL_BACKENDS}"
        )

    if configured_keys != ALL_BACKENDS:
        raise RuntimeError(
            "[CI CONTRACT] TRANSPILER_CLASS_PATHS + INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS deben preservar el orden de backend_policy.ALL_BACKENDS. "
            f"current={configured_keys}; expected={ALL_BACKENDS}"
        )
    return configured_keys


def _validate_public_registry_contract() -> tuple[str, ...]:
    """Valida contrato estricto del registro público frente a OFFICIAL_TARGETS/PUBLIC_BACKENDS."""
    assert_public_targets_contract(
        OFFICIAL_TARGETS,
        source="transpilers.registry.OFFICIAL_TARGETS",
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
    configured_keys = tuple(INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS)
    missing = tuple(
        target for target in INTERNAL_BACKENDS if target not in configured_keys
    )
    extras = tuple(
        target for target in configured_keys if target not in INTERNAL_BACKENDS
    )

    if missing or extras:
        raise RuntimeError(
            "[CI CONTRACT] INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS debe usar exactamente INTERNAL_BACKENDS. "
            f"missing={missing or '∅'}; extras={extras or '∅'}; "
            f"current={configured_keys}; expected={INTERNAL_BACKENDS}"
        )


    lifecycle_keys = set(INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW)
    internal_keys = set(INTERNAL_BACKENDS)
    if lifecycle_keys != internal_keys:
        extras = tuple(sorted(lifecycle_keys - internal_keys))
        missing = tuple(sorted(internal_keys - lifecycle_keys))
        raise RuntimeError(
            "[CI CONTRACT] INTERNAL_COMPATIBILITY_RETIREMENT_WINDOW debe cubrir "
            "exactamente INTERNAL_BACKENDS. "
            f"missing={missing or '∅'}; extras={extras or '∅'}"
        )

    if configured_keys != INTERNAL_BACKENDS:
        raise RuntimeError(
            "[CI CONTRACT] INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS debe preservar el orden de backend_policy.INTERNAL_BACKENDS. "
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


def get_transpilers() -> dict[str, type]:
    """API pública interna para obtener el registro oficial cargado."""
    return build_official_transpilers()


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
