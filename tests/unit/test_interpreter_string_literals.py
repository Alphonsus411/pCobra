"""Regresiones de la frontera entre literales léxicos y texto runtime."""

import pytest

from pcobra.core.ast_nodes import (
    NodoAsignacion,
    NodoIdentificador,
    NodoImprimir,
    NodoLlamadaFuncion,
    NodoValor,
)
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core.lexer import TipoToken, Token

TEXTOS_RUNTIME = (
    'texto con "comillas"',
    "texto con 'comillas'",
    "barra C:\\directorio\\archivo",
    "primera línea\nsegunda línea",
    "España 🐍",
    "'parece un literal Python'",
    '"también parece un literal Python"',
    "['no', 'evaluar']",
)


def _formas_de_imprimir(texto):
    return (
        [NodoImprimir(NodoValor(texto))],
        [NodoLlamadaFuncion("imprimir", [NodoValor(texto)])],
        [
            NodoAsignacion("mensaje", NodoValor(texto), declaracion=True),
            NodoImprimir(NodoIdentificador("mensaje")),
        ],
    )


@pytest.mark.parametrize("texto", TEXTOS_RUNTIME)
def test_imprimir_preserva_texto_runtime_en_sus_tres_formas(texto, capsys):
    for ast in _formas_de_imprimir(texto):
        InterpretadorCobra().ejecutar_ast(ast)
        assert capsys.readouterr().out == f"{texto}\n"


def test_token_crudo_se_decodifica_pero_nodo_valor_runtime_no():
    interprete = InterpretadorCobra()
    token_crudo = Token(TipoToken.CADENA, r'"línea\ncon \"comillas\""')
    texto_runtime = '"literal Python conservado"'

    assert interprete.evaluar_expresion(token_crudo) == 'línea\ncon "comillas"'
    assert interprete.evaluar_expresion(NodoValor(texto_runtime)) == texto_runtime


def test_regresion_nodo_valor_no_pierde_sus_comillas_exteriores():
    texto_runtime = "'contenido entre comillas'"

    assert (
        InterpretadorCobra().evaluar_expresion(NodoValor(texto_runtime))
        == texto_runtime
    )
