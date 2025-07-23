"""Componentes para convertir código de otros lenguajes a Cobra."""

from src.cobra.transpilers.reverse.base import BaseReverseTranspiler
from src.cobra.transpilers.reverse.from_python import ReverseFromPython

__all__ = ["BaseReverseTranspiler", "ReverseFromPython"]
