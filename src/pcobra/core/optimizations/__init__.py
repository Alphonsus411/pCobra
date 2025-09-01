"""Herramientas de optimizacion para el AST de Cobra."""

from core.optimizations.constant_folder import optimize_constants
from core.optimizations.dead_code import remove_dead_code
from core.optimizations.inliner import inline_functions
from core.optimizations.common_subexpr import eliminate_common_subexpressions

__all__ = [
    "optimize_constants",
    "remove_dead_code",
    "inline_functions",
    "eliminate_common_subexpressions",
]
