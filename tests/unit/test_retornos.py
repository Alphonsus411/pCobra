from io import StringIO
from unittest.mock import patch

import pytest
from core.interpreter import InterpretadorCobra
from core.lexer import Token, TipoToken
from core.ast_nodes import (
    NodoFuncion,
    NodoRetorno,
    NodoValor,
    NodoLlamadaFuncion,
    NodoIdentificador,
    NodoOperacionBinaria,
)
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript


from cobra.transpilers.transpiler.to_python import TranspiladorPython
def test_interpreter_funcion_con_retorno():
    inter = InterpretadorCobra()
    func = NodoFuncion("dame_cinco", [], [NodoRetorno(NodoValor(5))])
    inter.ejecutar_funcion(func)
    resultado = inter.ejecutar_llamada_funcion(NodoLlamadaFuncion("dame_cinco", []))
    assert resultado == 5


def test_transpiladores_retorno():
    nodo_ret = NodoRetorno(NodoValor(7))
    func = NodoFuncion("valor", [], [nodo_ret])

    py = TranspiladorPython()
    codigo_py = py.generate_code([func])
    assert "return 7" in codigo_py

    js = TranspiladorJavaScript()
    codigo_js = js.generate_code([func])
    assert "return 7;" in codigo_js


def test_definicion_triple_no_evalua_cuerpo_ni_dispara_warning_o_nameerror(monkeypatch):
    inter = InterpretadorCobra()
    llamadas_durante_definicion = []

    original = inter.ejecutar_llamada_funcion

    def _spy_llamada(nodo):
        llamadas_durante_definicion.append(nodo.nombre)
        return original(nodo)

    monkeypatch.setattr(inter, "ejecutar_llamada_funcion", _spy_llamada)

    doble = NodoFuncion(
        "doble",
        ["x"],
        [
            NodoRetorno(
                NodoOperacionBinaria(
                    NodoIdentificador("x"),
                    Token(TipoToken.MULT, "*"),
                    NodoValor(2),
                )
            )
        ],
    )
    triple = NodoFuncion(
        "triple",
        ["x"],
        [
            NodoRetorno(
                NodoLlamadaFuncion("doble", [NodoIdentificador("x")])
            )
        ],
    )

    with patch("sys.stdout", new_callable=StringIO) as out:
        inter.ejecutar_nodo(doble)
        inter.ejecutar_nodo(triple)

    assert llamadas_durante_definicion == []
    assert out.getvalue() == ""
