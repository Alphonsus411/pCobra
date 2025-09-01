from cobra.transpilers.transpiler.to_latex import TranspiladorLatex
from core.ast_nodes import (
    NodoAsignacion,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoImprimir,
    NodoValor,
    NodoRetorno,
)


def test_transpilador_asignacion_latex():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorLatex()
    resultado = t.generate_code(ast)
    esperado = "\\documentclass{article}\n\\begin{document}\nx = 10\n\\end{document}"
    assert resultado == esperado


def test_transpilador_funcion_latex():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorLatex()
    resultado = t.generate_code(ast)
    cuerpo = "function miFuncion(a, b)\n    x = a + b\nend"
    esperado = "\\documentclass{article}\n\\begin{document}\n" + cuerpo + "\n\\end{document}"
    assert resultado == esperado


def test_transpilador_llamada_funcion_latex():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorLatex()
    resultado = t.generate_code(ast)
    esperado = "\\documentclass{article}\n\\begin{document}\nmiFuncion(a, b)\n\\end{document}"
    assert resultado == esperado


def test_transpilador_imprimir_latex():
    ast = [NodoImprimir(NodoValor("x"))]
    t = TranspiladorLatex()
    resultado = t.generate_code(ast)
    esperado = "\\documentclass{article}\n\\begin{document}\n\\texttt{x}\n\\end{document}"
    assert resultado == esperado


def test_transpilador_retorno_latex():
    ast = [NodoFuncion("main", [], [NodoRetorno(NodoValor(4))])]
    t = TranspiladorLatex()
    resultado = t.generate_code(ast)
    cuerpo = "function main()\n    return 4\nend"
    esperado = "\\documentclass{article}\n\\begin{document}\n" + cuerpo + "\n\\end{document}"
    assert resultado == esperado
