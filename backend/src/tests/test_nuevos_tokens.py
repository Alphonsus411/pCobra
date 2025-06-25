import pytest
from src.cobra.lexico.lexer import Lexer, TipoToken


def test_lexer_palabras_nuevas():
    codigo = (
        "afirmar x\n"
        "eliminar y\n"
        "global a, b\n"
        "nolocal c\n"
        "lambda x: x\n"
        "con recurso como r: pasar fin\n"
        "try: pasar finalmente: pasar fin\n"
        "desde 'm' import n como q\n"
        "asincronico func f(): pasar fin\n"
        "esperar f()"
    )
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
    assert TipoToken.ASINCRONICO in tipos
    assert TipoToken.ESPERAR in tipos
