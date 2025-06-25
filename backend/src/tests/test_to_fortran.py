from src.cobra.transpilers.transpiler.to_fortran import TranspiladorFortran
from src.core.ast_nodes import (
    NodoAsignacion,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoImprimir,
    NodoValor,
)


def test_transpilador_asignacion_fortran():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorFortran()
    resultado = t.transpilar(ast)
    assert resultado == "x = 10"


def test_transpilador_funcion_fortran():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorFortran()
    resultado = t.transpilar(ast)
    esperado = "subroutine miFuncion(a, b)\n    x = a + b\nend subroutine"
    assert resultado == esperado


def test_transpilador_llamada_funcion_fortran():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorFortran()
    resultado = t.transpilar(ast)
    assert resultado == "call miFuncion(a, b)"


def test_transpilador_imprimir_fortran():
    ast = [NodoImprimir(NodoValor("x"))]
    t = TranspiladorFortran()
    resultado = t.transpilar(ast)
    assert resultado == "print *, x"
