"""Registro canónico de transpiladores oficiales."""

from __future__ import annotations

from importlib import import_module
from typing import Final

from pcobra.cobra.transpilers.targets import (
    OFFICIAL_TARGETS,
    require_exact_official_targets,
    target_cli_choices,
)

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


def ordered_official_transpiler_paths() -> tuple[tuple[str, tuple[str, str]], ...]:
    """Devuelve el registro canónico en el orden de ``OFFICIAL_TARGETS``."""
    ordered_targets = require_exact_official_targets(
        TRANSPILER_CLASS_PATHS,
        context="pcobra.cobra.transpilers.registry.TRANSPILER_CLASS_PATHS",
    )
    return tuple((target, TRANSPILER_CLASS_PATHS[target]) for target in ordered_targets)



def build_official_transpilers() -> dict[str, type]:
    """Carga las clases oficiales desde el registro canónico."""
    registry: dict[str, type] = {}
    for target, (module_name, class_name) in ordered_official_transpiler_paths():
        module = import_module(module_name)
        registry[target] = getattr(module, class_name)
    return registry



def official_transpiler_targets() -> tuple[str, ...]:
    """Devuelve los targets del registro canónico en el orden oficial."""
    require_exact_official_targets(
        TRANSPILER_CLASS_PATHS,
        context="pcobra.cobra.transpilers.registry.TRANSPILER_CLASS_PATHS",
    )
    return target_cli_choices(OFFICIAL_TARGETS)
