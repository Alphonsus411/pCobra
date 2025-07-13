import pytest
from cobra.lexico.lexer import (
    Lexer,
    LexerError,
    InvalidTokenError,
    UnclosedStringError,
)


def test_unclosed_string():
    codigo = "'hola"
    lexer = Lexer(codigo)
    with pytest.raises(LexerError) as exc:
        lexer.tokenizar()
    assert isinstance(exc.value, UnclosedStringError)
    assert "Cadena sin cerrar en linea 1, columna 1" in str(exc.value)


def test_multiple_decimal_points():
    codigo = "123.45.67"
    lexer = Lexer(codigo)
    with pytest.raises(LexerError):
        lexer.tokenizar()


def test_invalid_symbol():
    codigo = "var x = €"
    lexer = Lexer(codigo)
    with pytest.raises(LexerError) as exc:
        lexer.tokenizar()
    assert isinstance(exc.value, InvalidTokenError)
    assert "Token no reconocido: '€' en linea 1, columna 9" in str(exc.value)
