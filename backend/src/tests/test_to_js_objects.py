from src.core.transpiler.to_js import TranspiladorJavaScript
from src.core.ast_nodes import NodoInstancia, NodoLlamadaMetodo, NodoIdentificador, NodoValor


def test_transpilar_instancia():
    nodo = NodoInstancia("Clase")
    transpiler = TranspiladorJavaScript()
    result = transpiler.transpilar([nodo])
    assert result == "new Clase();"


def test_transpilar_llamada_metodo():
    nodo = NodoLlamadaMetodo(NodoIdentificador("obj"), "metodo", [NodoValor(1)])
    transpiler = TranspiladorJavaScript()
    result = transpiler.transpilar([nodo])
    assert result == "obj.metodo(1);"
