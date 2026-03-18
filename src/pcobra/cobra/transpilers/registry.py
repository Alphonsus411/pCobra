"""Registro canónico de transpiladores oficiales."""

from __future__ import annotations

from importlib import import_module
from typing import Final

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


def ordered_official_transpiler_paths() -> tuple[tuple[str, tuple[str, str]], ...]:
    """Devuelve el registro canónico en el orden de ``OFFICIAL_TARGETS``."""
    missing = [target for target in OFFICIAL_TARGETS if target not in TRANSPILER_CLASS_PATHS]
    extra = [target for target in TRANSPILER_CLASS_PATHS if target not in OFFICIAL_TARGETS]
    if missing or extra:
        details = []
        if missing:
            details.append(f"faltan: {', '.join(missing)}")
        if extra:
            details.append(f"sobran: {', '.join(extra)}")
        raise RuntimeError(
            "Registro canónico de transpiladores desalineado con OFFICIAL_TARGETS ("
            + "; ".join(details)
            + ")"
        )
    return tuple((target, TRANSPILER_CLASS_PATHS[target]) for target in OFFICIAL_TARGETS)



def build_official_transpilers() -> dict[str, type]:
    """Carga las clases oficiales desde el registro canónico."""
    registry: dict[str, type] = {}
    for target, (module_name, class_name) in ordered_official_transpiler_paths():
        module = import_module(module_name)
        registry[target] = getattr(module, class_name)
    return registry



def official_transpiler_targets() -> tuple[str, ...]:
    """Devuelve los targets del registro canónico en el orden oficial."""
    return tuple(target for target, _ in ordered_official_transpiler_paths())
