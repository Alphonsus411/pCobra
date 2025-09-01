from cobra.transpilers.transpiler.to_swift import TranspiladorSwift
from core.ast_nodes import (
    NodoAsignacion,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoImprimir,
    NodoValor,
)


def test_transpilador_asignacion_swift():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorSwift()
    resultado = t.generate_code(ast)
    assert resultado == "var x = 10"


def test_transpilador_funcion_swift():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorSwift()
    resultado = t.generate_code(ast)
    esperado = "func miFuncion(a, b) {\n    var x = a + b\n}"
    assert resultado == esperado


def test_transpilador_llamada_funcion_swift():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorSwift()
    resultado = t.generate_code(ast)
    assert resultado == "miFuncion(a, b)"


def test_transpilador_imprimir_swift():
    ast = [NodoImprimir(NodoValor("x"))]
    t = TranspiladorSwift()
    resultado = t.generate_code(ast)
    assert resultado == "print(x)"

