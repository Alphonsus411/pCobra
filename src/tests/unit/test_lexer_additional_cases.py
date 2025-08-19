import pytest
from cobra.core import (
    Lexer,
    TipoToken,
    InvalidTokenError,
)


def test_unclosed_comment_raises_invalid_token():
    codigo = "var x = 1 /* comentario ' sin cerrar"
    lexer = Lexer(codigo)
    with pytest.raises(InvalidTokenError):
        lexer.tokenizar()


def test_block_comment_without_closing():
    codigo = "/*"
    lexer = Lexer(codigo)
    with pytest.raises(InvalidTokenError) as exc:
        lexer.tokenizar()
    assert "Comentario de bloque sin cerrar en línea 1, columna 3" in str(exc.value)


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
