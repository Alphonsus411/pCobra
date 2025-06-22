"""Herramientas de optimizacion para el AST de Cobra."""

from .constant_folder import optimize_constants
from .dead_code import remove_dead_code

__all__ = ["optimize_constants", "remove_dead_code"]
