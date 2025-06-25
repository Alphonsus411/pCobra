import pytest
from src.cobra.lexico.lexer import Lexer, TipoToken


def test_lexer_palabras_nuevas():
    codigo = "afirmar x\neliminar y\nglobal a, b\nnolocal c\nlambda x: x\ncon recurso como r: pasar fin\ntry: pasar finalmente: pasar fin\ndesde 'm' import n como q"
    tokens = Lexer(codigo).analizar_token()
    tipos = [t.tipo for t in tokens if t.tipo != TipoToken.EOF]
    assert TipoToken.AFIRMAR in tipos
    assert TipoToken.ELIMINAR in tipos
    assert TipoToken.GLOBAL in tipos
    assert TipoToken.NOLOCAL in tipos
    assert TipoToken.LAMBDA in tipos
    assert TipoToken.CON in tipos
    assert TipoToken.FINALMENTE in tipos
    assert TipoToken.DESDE in tipos and TipoToken.COMO in tipos
