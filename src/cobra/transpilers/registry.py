"""Shim histórico de compatibilidad para ``cobra.transpilers.registry``.

Fuente canónica: :mod:`pcobra.cobra.transpilers.registry`.
"""

from pcobra.cobra.transpilers.registry import (
    TRANSPILER_CLASS_PATHS,
    build_official_transpilers,
    official_transpiler_module_filenames,
    official_transpiler_registry_literal,
    official_transpiler_targets,
    ordered_official_transpiler_paths,
)

__all__ = [
    "TRANSPILER_CLASS_PATHS",
    "ordered_official_transpiler_paths",
    "build_official_transpilers",
    "official_transpiler_targets",
    "official_transpiler_module_filenames",
    "official_transpiler_registry_literal",
]
