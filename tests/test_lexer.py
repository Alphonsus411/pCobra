import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from pcobra.cobra.core.lexer import InvalidTokenError, Lexer, TipoToken



def test_lexer_aritmetica_simple() -> None:
    codigo = "1 + 2"
    lexer = Lexer(codigo)
    tokens = lexer.tokenizar()
    tipos = [token.tipo for token in tokens]
    assert tipos == [
        TipoToken.ENTERO,
        TipoToken.SUMA,
        TipoToken.ENTERO,
        TipoToken.EOF,
    ]


def test_lexer_token_invalido() -> None:
    with pytest.raises(InvalidTokenError):
        lexer = Lexer("$")
        lexer.tokenizar()
