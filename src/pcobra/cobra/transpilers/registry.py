"""Registro canónico de transpiladores oficiales."""

from __future__ import annotations

from importlib import import_module
from typing import Final

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
    """Valida que el registro declare exactamente los 8 targets oficiales."""
    try:
        return require_exact_official_targets(
            TRANSPILER_CLASS_PATHS,
            context="pcobra.cobra.transpilers.registry.TRANSPILER_CLASS_PATHS",
        )
    except RuntimeError as exc:
        configured_keys = tuple(TRANSPILER_CLASS_PATHS)
        extras = tuple(key for key in configured_keys if key not in OFFICIAL_TARGETS)
        if extras:
            raise RuntimeError(
                "TRANSPILER_CLASS_PATHS solo puede declarar los 8 targets canónicos "
                f"{OFFICIAL_TARGETS}. Se detectaron claves fuera de contrato: {extras}."
            ) from exc
        raise


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
