import pytest
from src.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from src.core.ast_nodes import NodoAsignacion, NodoCondicional, NodoBucleMientras, NodoFuncion, NodoLlamadaFuncion, NodoHolobit


def test_transpilador_asignacion():
    ast = [NodoAsignacion("x", 10)]
    transpilador = TranspiladorJavaScript()
    resultado = transpilador.transpilar(ast)
    assert resultado == "let x = 10;"


def test_transpilador_condicional():
    ast = [NodoCondicional("x > 5", [NodoAsignacion("y", 2)], [NodoAsignacion("y", 3)])]
    transpilador = TranspiladorJavaScript()
    resultado = transpilador.transpilar(ast)
    expected = "if (x > 5) {\n    let y = 2;\n} else {\n    let y = 3;\n}"
    assert resultado == expected


def test_transpilador_mientras():
    ast = [NodoBucleMientras("x > 0", [NodoAsignacion("x", "x - 1")])]
    transpilador = TranspiladorJavaScript()
    resultado = transpilador.transpilar(ast)
    expected = "while (x > 0) {\n    let x = x - 1;\n}"
    assert resultado == expected


def test_transpilador_funcion():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    transpilador = TranspiladorJavaScript()
    resultado = transpilador.transpilar(ast)
    expected = "function miFuncion(a, b) {\n    let x = a + b;\n}"
    assert resultado == expected


def test_transpilador_llamada_funcion():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    transpilador = TranspiladorJavaScript()
    resultado = transpilador.transpilar(ast)
    expected = "miFuncion(a, b);"
    assert resultado == expected


def test_transpilador_holobit():
    ast = [NodoHolobit("miHolobit", [0.8, -0.5, 1.2])]
    transpilador = TranspiladorJavaScript()
    resultado = transpilador.transpilar(ast)
    expected = "let miHolobit = new Holobit([0.8, -0.5, 1.2]);"
    assert resultado == expected


def test_transpilador_yield():
    ast = [NodoFuncion("generador", [], [NodoYield(NodoValor(1))])]
    t = TranspiladorJavaScript()
    resultado = t.transpilar(ast)
    esperado = "function generador() {\n    yield 1;\n}"
    assert resultado == esperado
