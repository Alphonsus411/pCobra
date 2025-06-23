from src.cobra.transpilers.transpiler.to_python import TranspiladorPython
from src.core.ast_nodes import NodoInstancia, NodoLlamadaMetodo, NodoIdentificador, NodoValor


def test_transpilar_instancia():
    nodo = NodoInstancia("Clase")
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    esperado = "from src.core.nativos import *\nClase()\n"
    assert result == esperado


def test_transpilar_llamada_metodo():
    nodo = NodoLlamadaMetodo(NodoIdentificador("obj"), "metodo", [NodoValor(1)])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    esperado = "from src.core.nativos import *\nobj.metodo(1)\n"
    assert result == esperado
