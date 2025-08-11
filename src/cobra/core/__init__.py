"""Componentes principales del núcleo de Cobra.

Este paquete reúne el analizador léxico, el analizador sintáctico y
utilidades relacionadas con el núcleo del lenguaje. La importación del
AST se realiza de forma explícita en los módulos que lo necesitan para
evitar dependencias circulares durante la inicialización del paquete.
"""

from .lexer import (
    Lexer,
    Token,
    TipoToken,
    LexerError,
    InvalidTokenError,
    UnclosedStringError,
)
from .parser import Parser, ParserError

__all__ = [
    "Lexer",
    "Parser",
    "ParserError",
    "LexerError",
    "InvalidTokenError",
    "UnclosedStringError",
    "Token",
    "TipoToken",
]
