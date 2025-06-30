import backend
from backend.src.core.ast_nodes import NodoImprimir, NodoValor
from backend.src.cobra.transpilers.transpiler.to_python import TranspiladorPython


def test_transpilador_python_generacion():
    ast = [NodoImprimir(NodoValor("'hola'"))]
    codigo = TranspiladorPython().transpilar(ast)
    assert "print('hola')" in codigo
