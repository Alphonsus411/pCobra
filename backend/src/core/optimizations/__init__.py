"""Herramientas de optimizacion para el AST de Cobra."""

from .constant_folder import optimize_constants
from .dead_code import remove_dead_code
from .inliner import inline_functions
from .common_subexpr import eliminate_common_subexpressions

__all__ = [
    "optimize_constants",
    "remove_dead_code",
    "inline_functions",
    "eliminate_common_subexpressions",
]
