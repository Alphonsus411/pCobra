from src.core.transpiler.to_python import TranspiladorPython
from src.core.parser import NodoInstancia, NodoLlamadaMetodo, NodoIdentificador, NodoValor


def test_transpilar_instancia():
    nodo = NodoInstancia("Clase")
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    assert result == "Clase()\n"


def test_transpilar_llamada_metodo():
    nodo = NodoLlamadaMetodo(NodoIdentificador("obj"), "metodo", [NodoValor(1)])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    assert result == "obj.metodo(1)\n"
