from __future__ import annotations

from cobra.core import Lexer, TipoToken


def test_var_x_igual_y_trata_y_como_identificador() -> None:
    tokens = Lexer("var x = y").tokenizar()

    assert tokens[0].tipo == TipoToken.VAR
    assert tokens[1].tipo == TipoToken.IDENTIFICADOR
    assert tokens[1].valor == "x"
    assert tokens[2].tipo == TipoToken.ASIGNAR
    assert tokens[3].tipo == TipoToken.IDENTIFICADOR
    assert tokens[3].valor == "y"


def test_operadores_logicos_simbolicos_siguen_validos() -> None:
    tokens = Lexer("verdadero && falso || !falso").tokenizar()
    tipos = [token.tipo for token in tokens]

    assert TipoToken.AND in tipos
    assert TipoToken.OR in tipos
    assert TipoToken.NOT in tipos
