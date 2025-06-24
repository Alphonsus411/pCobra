from src.cobra.transpilers.transpiler.to_cpp import TranspiladorCPP
from src.core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoHolobit,
)


def test_transpilador_asignacion():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorCPP()
    resultado = t.transpilar(ast)
    assert resultado == "auto x = 10;"


def test_transpilador_condicional():
    ast = [
        NodoCondicional(
            "x > 5",
            [NodoAsignacion("y", 2)],
            [NodoAsignacion("y", 3)],
        )
    ]
    t = TranspiladorCPP()
    resultado = t.transpilar(ast)
    esperado = "if (x > 5) {\n    auto y = 2;\n} else {\n    auto y = 3;\n}"
    assert resultado == esperado


def test_transpilador_mientras():
    ast = [NodoBucleMientras("x > 0", [NodoAsignacion("x", "x - 1")])]
    t = TranspiladorCPP()
    resultado = t.transpilar(ast)
    esperado = "while (x > 0) {\n    auto x = x - 1;\n}"
    assert resultado == esperado


def test_transpilador_funcion():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorCPP()
    resultado = t.transpilar(ast)
    esperado = "void miFuncion(auto a, auto b) {\n    auto x = a + b;\n}"
    assert resultado == esperado


def test_transpilador_llamada_funcion():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorCPP()
    resultado = t.transpilar(ast)
    assert resultado == "miFuncion(a, b);"


def test_transpilador_holobit():
    ast = [NodoHolobit("miHolobit", [0.8, -0.5, 1.2])]
    t = TranspiladorCPP()
    resultado = t.transpilar(ast)
    assert resultado == "auto miHolobit = holobit({ 0.8, -0.5, 1.2 });"
