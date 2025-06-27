import pytest
from src.cobra.lexico.lexer import (
    Lexer,
    LexerError,
    InvalidTokenError,
    UnclosedStringError,
)


def test_mensaje_cadena_no_cerrada():
    codigo = "'hola"
    lexer = Lexer(codigo)
    with pytest.raises(UnclosedStringError, match="Cadena sin cerrar en linea 1, columna 1"):
        lexer.tokenizar()


def test_mensaje_token_desconocido():
    codigo = "var x = €"
    lexer = Lexer(codigo)
    with pytest.raises(InvalidTokenError) as exc:
        lexer.tokenizar()
    assert "Token no reconocido: '€' en linea 1, columna 9" in str(exc.value)

