from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from core.ast_nodes import NodoInstancia, NodoLlamadaMetodo, NodoIdentificador, NodoValor


def test_transpilar_instancia():
    nodo = NodoInstancia("Clase")
    transpiler = TranspiladorJavaScript()
    result = transpiler.generate_code([nodo])
    assert result == "new Clase();"


def test_transpilar_llamada_metodo():
    nodo = NodoLlamadaMetodo(NodoIdentificador("obj"), "metodo", [NodoValor(1)])
    transpiler = TranspiladorJavaScript()
    result = transpiler.generate_code([nodo])
    assert result == "obj.metodo(1);"
