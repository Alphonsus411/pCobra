import pcobra
from core.ast_nodes import NodoImprimir, NodoValor
from cobra.transpilers.transpiler.to_python import TranspiladorPython


def test_transpilador_python_generacion():
    ast = [NodoImprimir(NodoValor("'hola'"))]
    codigo = TranspiladorPython().generate_code(ast)
    assert "print('hola')" in codigo
