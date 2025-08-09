import pytest
from cobra.core import Lexer, TipoToken, LexerError


def test_simple_assignment_tokens():
    codigo = "var x = 42"
    tokens = Lexer(codigo).analizar_token()
    tipos_valores = [(t.tipo, t.valor) for t in tokens]
    assert tipos_valores == [
        (TipoToken.VAR, "var"),
        (TipoToken.IDENTIFICADOR, "x"),
        (TipoToken.ASIGNAR, "="),
        (TipoToken.ENTERO, 42),
        (TipoToken.EOF, None),
    ]


def test_invalid_symbol_raises_error():
    codigo = "var x = €"
    lexer = Lexer(codigo)
    with pytest.raises(LexerError):
        lexer.analizar_token()
