from cobra.transpilers.transpiler.to_latex import TranspiladorLatex
from core.ast_nodes import NodoAsignacion, NodoFuncion, NodoLlamadaFuncion, NodoImprimir, NodoValor


def test_transpilador_asignacion_latex():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorLatex()
    resultado = t.generate_code(ast)
    assert resultado == "x = 10"


def test_transpilador_funcion_latex():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorLatex()
    resultado = t.generate_code(ast)
    esperado = "function miFuncion(a, b)\n    x = a + b\nend"
    assert resultado == esperado


def test_transpilador_llamada_funcion_latex():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorLatex()
    resultado = t.generate_code(ast)
    assert resultado == "miFuncion(a, b)"


def test_transpilador_imprimir_latex():
    ast = [NodoImprimir(NodoValor("x"))]
    t = TranspiladorLatex()
    resultado = t.generate_code(ast)
    assert resultado == "\\texttt{x}"
