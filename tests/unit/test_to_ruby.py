from src.cobra.transpilers.transpiler.to_ruby import TranspiladorRuby
from src.core.ast_nodes import NodoAsignacion, NodoFuncion, NodoLlamadaFuncion, NodoImprimir, NodoValor


def test_transpilador_asignacion_ruby():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorRuby()
    resultado = t.generate_code(ast)
    assert resultado == "x = 10"


def test_transpilador_funcion_ruby():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorRuby()
    resultado = t.generate_code(ast)
    esperado = "def miFuncion(a, b)\n    x = a + b\nend"
    assert resultado == esperado


def test_transpilador_llamada_funcion_ruby():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorRuby()
    resultado = t.generate_code(ast)
    assert resultado == "miFuncion(a, b)"


def test_transpilador_imprimir_ruby():
    ast = [NodoImprimir(NodoValor("x"))]
    t = TranspiladorRuby()
    resultado = t.generate_code(ast)
    assert resultado == "puts x"
