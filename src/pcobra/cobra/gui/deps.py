"""Dependencias neutrales de runtime para GUI.

Este módulo evita acoplar GUI con rutas de comandos CLI concretas.
Expone únicamente:
- Lexer/Parser (+ tipos de error asociados)
- intérprete
- registro de transpiladores
- helpers/choices de targets
"""

from __future__ import annotations

from pcobra.cobra.core import Lexer, LexerError, Parser, ParserError
from pcobra.cobra.transpilers.registry import get_transpilers
from pcobra.cobra.transpilers.target_utils import target_cli_choices
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS
from pcobra.core.interpreter import InterpretadorCobra

__all__ = [
    "Lexer",
    "LexerError",
    "Parser",
    "ParserError",
    "InterpretadorCobra",
    "get_transpilers",
    "target_cli_choices",
    "OFFICIAL_TARGETS",
]

