from src.cobra.transpilers.transpiler.to_r import TranspiladorR
from src.core.ast_nodes import NodoAsignacion, NodoFuncion, NodoLlamadaFuncion, NodoImprimir, NodoValor


def test_transpilador_asignacion_r():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorR()
    resultado = t.transpilar(ast)
    assert resultado == "x <- 10"


def test_transpilador_funcion_r():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorR()
    resultado = t.transpilar(ast)
    esperado = "miFuncion <- function(a, b) {\n    x <- a + b\n}"
    assert resultado == esperado


def test_transpilador_llamada_funcion_r():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorR()
    resultado = t.transpilar(ast)
    assert resultado == "miFuncion(a, b)"


def test_transpilador_imprimir_r():
    ast = [NodoImprimir(NodoValor("x"))]
    t = TranspiladorR()
    resultado = t.transpilar(ast)
    assert resultado == "print(x)"
