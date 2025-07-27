"""Facilita el acceso a los distintos transpiladores de Cobra."""

from cobra.transpilers.base import BaseTranspiler
from cobra.transpilers.reverse.base import BaseReverseTranspiler

__all__ = ["BaseTranspiler", "BaseReverseTranspiler"]
