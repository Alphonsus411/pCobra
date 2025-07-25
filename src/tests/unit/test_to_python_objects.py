from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.import_helper import get_standard_imports

IMPORTS = get_standard_imports("python")
from core.ast_nodes import NodoInstancia, NodoLlamadaMetodo, NodoIdentificador, NodoValor


def test_transpilar_instancia():
    nodo = NodoInstancia("Clase")
    transpiler = TranspiladorPython()
    result = transpiler.generate_code([nodo])
    esperado = IMPORTS + "Clase()\n"
    assert result == esperado


def test_transpilar_llamada_metodo():
    nodo = NodoLlamadaMetodo(NodoIdentificador("obj"), "metodo", [NodoValor(1)])
    transpiler = TranspiladorPython()
    result = transpiler.generate_code([nodo])
    esperado = IMPORTS + "obj.metodo(1)\n"
    assert result == esperado
