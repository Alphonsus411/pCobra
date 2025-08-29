"""Componentes principales del núcleo de Cobra.

Este paquete reúne el analizador léxico, el analizador sintáctico y
utilidades relacionadas con el núcleo del lenguaje. La importación del
AST se realiza de forma explícita en los módulos que lo necesitan para
evitar dependencias circulares durante la inicialización del paquete.
"""

from cobra.core.lexer import (
    Lexer,
    Token,
    TipoToken,
    LexerError,
    InvalidTokenError,
    UnclosedStringError,
)

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


def __getattr__(name: str):
    """Importa dinámicamente el analizador cuando se solicita.

    Esto mantiene una importación perezosa del módulo ``parser`` para
    evitar dependencias circulares y tiempos de carga innecesarios.
    """
    if name in {"Parser", "ParserError"}:
        from . import parser as _parser

        globals().update({"Parser": _parser.Parser, "ParserError": _parser.ParserError})
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
