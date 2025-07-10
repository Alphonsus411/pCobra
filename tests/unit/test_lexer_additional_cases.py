import pytest
from src.cobra.lexico.lexer import (
    Lexer,
    TipoToken,
    InvalidTokenError,
    UnclosedStringError,
)


def test_unclosed_comment_triggers_unclosed_string():
    codigo = "var x = 1 /* comentario ' sin cerrar"
    lexer = Lexer(codigo)
    with pytest.raises(UnclosedStringError):
        lexer.tokenizar()


def test_unclosed_comment_with_invalid_symbol():
    codigo = "var x = 1 /* comentario €"
    lexer = Lexer(codigo)
    with pytest.raises(InvalidTokenError):
        lexer.tokenizar()


def test_illegal_symbol_mix():
    codigo = "var x = 10€$"
    lexer = Lexer(codigo)
    with pytest.raises(InvalidTokenError):
        lexer.tokenizar()


def test_extremely_large_integer():
    numero = 1234567890123456789012345678901234567890
    codigo = str(numero)
    tokens = Lexer(codigo).analizar_token()
    assert tokens[0].tipo == TipoToken.ENTERO
    assert tokens[0].valor == numero
    assert tokens[-1].tipo == TipoToken.EOF
