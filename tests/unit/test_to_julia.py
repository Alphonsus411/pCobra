from src.cobra.transpilers.transpiler.to_julia import TranspiladorJulia
from src.core.ast_nodes import NodoAsignacion, NodoFuncion, NodoLlamadaFuncion, NodoImprimir, NodoValor


def test_transpilador_asignacion_julia():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorJulia()
    resultado = t.generate_code(ast)
    assert resultado == "x = 10"


def test_transpilador_funcion_julia():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorJulia()
    resultado = t.generate_code(ast)
    esperado = "function miFuncion(a, b)\n    x = a + b\nend"
    assert resultado == esperado


def test_transpilador_llamada_funcion_julia():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorJulia()
    resultado = t.generate_code(ast)
    assert resultado == "miFuncion(a, b)"


def test_transpilador_imprimir_julia():
    ast = [NodoImprimir(NodoValor("x"))]
    t = TranspiladorJulia()
    resultado = t.generate_code(ast)
    assert resultado == "println(x)"
