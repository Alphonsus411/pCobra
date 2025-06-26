import pytest
from src.cobra.lexico.lexer import Lexer, LexerError


def test_unclosed_string():
    codigo = "'hola"
    lexer = Lexer(codigo)
    with pytest.raises(LexerError):
        lexer.tokenizar()


def test_multiple_decimal_points():
    codigo = "123.45.67"
    lexer = Lexer(codigo)
    with pytest.raises(LexerError):
        lexer.tokenizar()


def test_invalid_symbol():
    codigo = "var x = €"
    lexer = Lexer(codigo)
    with pytest.raises(LexerError):
        lexer.tokenizar()
