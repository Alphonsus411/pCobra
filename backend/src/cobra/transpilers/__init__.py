"""Facilita el acceso a los distintos transpiladores de Cobra."""

from src.cobra.transpilers.base import BaseTranspiler
from src.cobra.transpilers.reverse.base import BaseReverseTranspiler

__all__ = ["BaseTranspiler", "BaseReverseTranspiler"]
