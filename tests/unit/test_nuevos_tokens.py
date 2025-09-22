import pytest
from pcobra.cobra.core.lexer import Lexer, TipoToken


def test_lexer_palabras_nuevas():
    codigo = (
        "afirmar x\n"
        "eliminar y\n"
        "global a, b\n"
        "nolocal c\n"
        "lambda x: x\n"
        "con recurso como r: pasar fin\n"
        "intentar: lanzar 1 capturar e: pasar finalmente: pasar fin\n"
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
    assert TipoToken.INTENTAR in tipos
    assert TipoToken.CAPTURAR in tipos
    assert TipoToken.LANZAR in tipos


def test_lexer_palabras_nuevas_en():
    codigo = "with recurso as r: pasar fin"
    tokens = Lexer(codigo).analizar_token()
    tipos = [t.tipo for t in tokens if t.tipo != TipoToken.EOF]
    assert TipoToken.WITH in tipos
    assert TipoToken.AS in tipos


def test_lexer_token_defer_y_aplazar():
    codigo = "defer limpiar()\naplazar cerrar()"
    tokens = Lexer(codigo).analizar_token()
    tipos = [t.tipo for t in tokens if t.tipo != TipoToken.EOF]
    assert tipos.count(TipoToken.DEFER) == 2
