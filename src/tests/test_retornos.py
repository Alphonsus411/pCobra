import pytest
from src.core.interpreter import InterpretadorCobra
from src.core.parser import NodoFuncion, NodoRetorno, NodoValor, NodoLlamadaFuncion
from src.core.transpiler.to_python import TranspiladorPython
from src.core.transpiler.to_js import TranspiladorJavaScript


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
    codigo_py = py.transpilar([func])
    assert "return 7" in codigo_py

    js = TranspiladorJavaScript()
    codigo_js = js.transpilar([func])
    assert "return 7;" in codigo_js
