"""Registro canónico de transpiladores oficiales."""

from __future__ import annotations

from importlib import import_module
from typing import Final

from pcobra.cobra.config.transpile_targets import LEGACY_INTERNAL_TARGETS
from pcobra.cobra.transpilers.target_utils import (
    require_exact_official_targets,
    target_cli_choices,
)
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS

TRANSPILER_CLASS_PATHS: Final[dict[str, tuple[str, str]]] = {
    "python": ("pcobra.cobra.transpilers.transpiler.to_python", "TranspiladorPython"),
    "rust": ("pcobra.cobra.transpilers.transpiler.to_rust", "TranspiladorRust"),
    "javascript": ("pcobra.cobra.transpilers.transpiler.to_js", "TranspiladorJavaScript"),
    "wasm": ("pcobra.cobra.transpilers.transpiler.to_wasm", "TranspiladorWasm"),
    "go": ("pcobra.cobra.transpilers.transpiler.to_go", "TranspiladorGo"),
    "cpp": ("pcobra.cobra.transpilers.transpiler.to_cpp", "TranspiladorCPP"),
    "java": ("pcobra.cobra.transpilers.transpiler.to_java", "TranspiladorJava"),
    "asm": ("pcobra.cobra.transpilers.transpiler.to_asm", "TranspiladorASM"),
}


def _validate_registry_contract() -> tuple[str, ...]:
    """Valida que el registro cubra el canon oficial y solo admita legacy conocido."""
    configured_keys = tuple(TRANSPILER_CLASS_PATHS)
    official_set = set(OFFICIAL_TARGETS)
    legacy_set = set(LEGACY_INTERNAL_TARGETS)

    missing = tuple(target for target in OFFICIAL_TARGETS if target not in configured_keys)
    extras = tuple(
        target
        for target in configured_keys
        if target not in official_set and target not in legacy_set
    )

    if missing or extras:
        raise RuntimeError(
            "[CI CONTRACT] TRANSPILER_CLASS_PATHS debe cubrir todos los targets oficiales y solo puede añadir targets legacy/internal conocidos. "
            f"missing={missing or '∅'}; extras={extras or '∅'}; "
            f"current={configured_keys}; official={OFFICIAL_TARGETS}; legacy={LEGACY_INTERNAL_TARGETS}"
        )

    official_keys_in_registry = tuple(target for target in configured_keys if target in official_set)

    return require_exact_official_targets(
        official_keys_in_registry,
        context="pcobra.cobra.transpilers.registry.TRANSPILER_CLASS_PATHS",
    )


_ORDERED_OFFICIAL_TARGETS: Final[tuple[str, ...]] = _validate_registry_contract()


def ordered_official_transpiler_paths() -> tuple[tuple[str, tuple[str, str]], ...]:
    """Devuelve el registro canónico en el orden de ``OFFICIAL_TARGETS``."""
    return tuple((target, TRANSPILER_CLASS_PATHS[target]) for target in _ORDERED_OFFICIAL_TARGETS)


def build_official_transpilers() -> dict[str, type]:
    """Carga las clases oficiales desde el registro canónico."""
    registry: dict[str, type] = {}
    for target, (module_name, class_name) in ordered_official_transpiler_paths():
        module = import_module(module_name)
        registry[target] = getattr(module, class_name)
    return registry


def official_transpiler_targets() -> tuple[str, ...]:
    """Devuelve los targets del registro canónico en el orden oficial."""
    return target_cli_choices(_ORDERED_OFFICIAL_TARGETS)


def official_transpiler_module_filenames() -> tuple[str, ...]:
    """Devuelve los nombres de archivo ``to_*.py`` canónicos del registro oficial."""
    return tuple(
        module_name.rsplit(".", 1)[-1] + ".py"
        for _, (module_name, _) in ordered_official_transpiler_paths()
    )


def official_transpiler_registry_literal() -> dict[str, tuple[str, str]]:
    """Devuelve el literal esperado del registro canónico para auditorías."""
    return {target: value for target, value in ordered_official_transpiler_paths()}
