from core.ast_nodes import (
    NodoAssert, NodoDel, NodoGlobal, NodoNoLocal, NodoLambda, NodoValor, NodoWith, NodoPasar
)
from cobra.transpilers.transpiler.to_python import TranspiladorPython


def test_transpilar_afirmar():
    nodo = NodoAssert(NodoValor("True"))
    codigo = TranspiladorPython().generate_code([nodo])
    assert "assert True" in codigo


def test_transpilar_lambda():
    nodo = NodoLambda(["x"], NodoValor("x"))
    t = TranspiladorPython()
    expr = t.obtener_valor(nodo)
    assert expr == "lambda x: x"
