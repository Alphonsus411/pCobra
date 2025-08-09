"""Compatibilidad retrocompatible para utilidades de importación."""

from cobra.transpilers.common.utils import (
    STANDARD_IMPORTS,
    get_standard_imports,
    load_mapped_module,
)

__all__ = ["STANDARD_IMPORTS", "get_standard_imports", "load_mapped_module"]
