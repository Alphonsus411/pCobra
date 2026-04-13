"""Registro canónico de transpiladores oficiales."""

from __future__ import annotations

from importlib import import_module
from typing import Final

from pcobra.cobra.architecture.backend_policy import ALL_BACKENDS

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


def _validate_registry_contract() -> tuple[str, ...]:
    """Valida que el registro mantenga backends públicos e internos legacy."""
    configured_keys = tuple(TRANSPILER_CLASS_PATHS)
    missing = tuple(target for target in ALL_BACKENDS if target not in configured_keys)
    extras = tuple(target for target in configured_keys if target not in ALL_BACKENDS)

    if missing or extras:
        raise RuntimeError(
            "[CI CONTRACT] TRANSPILER_CLASS_PATHS tiene claves fuera de contrato y debe usar exactamente los backends declarados en la política de arquitectura. "
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
    """Devuelve los targets del registro canónico en el orden contractual."""
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
