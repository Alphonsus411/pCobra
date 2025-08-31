from cobra.transpilers.transpiler.to_kotlin import TranspiladorKotlin
from core.ast_nodes import (
    NodoAsignacion,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoImprimir,
    NodoValor,
    NodoRetorno,
)


def test_transpilador_asignacion_kotlin():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorKotlin()
    resultado = t.generate_code(ast)
    assert resultado == "var x = 10"


def test_transpilador_funcion_kotlin():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorKotlin()
    resultado = t.generate_code(ast)
    esperado = "fun miFuncion(a, b) {\n    var x = a + b\n}"
    assert resultado == esperado


def test_transpilador_llamada_funcion_kotlin():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorKotlin()
    resultado = t.generate_code(ast)
    assert resultado == "miFuncion(a, b)"


def test_transpilador_imprimir_kotlin():
    ast = [NodoImprimir(NodoValor("x"))]
    t = TranspiladorKotlin()
    resultado = t.generate_code(ast)
    assert resultado == "println(x)"


def test_transpilador_main_retorno_kotlin():
    ast = [NodoFuncion("main", [], [NodoRetorno(NodoValor(5))])]
    t = TranspiladorKotlin()
    resultado = t.generate_code(ast)
    esperado = "fun main() {\n    println(5)\n}"
    assert resultado == esperado
