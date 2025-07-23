from cobra.transpilers.transpiler.to_visualbasic import TranspiladorVisualBasic
from core.ast_nodes import (
    NodoAsignacion,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoImprimir,
    NodoValor,
    NodoIdentificador,
)


def test_transpilador_asignacion_vb():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorVisualBasic()
    resultado = t.generate_code(ast)
    assert resultado == "Dim x = 10"


def test_transpilador_funcion_vb():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", NodoIdentificador("a"))])]
    t = TranspiladorVisualBasic()
    resultado = t.generate_code(ast)
    esperado = "Sub miFuncion(a, b)\n    Dim x = a\nEnd Sub"
    assert resultado == esperado


def test_transpilador_llamada_funcion_vb():
    ast = [NodoLlamadaFuncion("miFuncion", [NodoIdentificador("x"), NodoValor(3)])]
    t = TranspiladorVisualBasic()
    resultado = t.generate_code(ast)
    assert resultado == "miFuncion(x, 3)"


def test_transpilador_imprimir_vb():
    ast = [NodoImprimir(NodoIdentificador("x"))]
    t = TranspiladorVisualBasic()
    resultado = t.generate_code(ast)
    assert resultado == "Console.WriteLine(x)"
