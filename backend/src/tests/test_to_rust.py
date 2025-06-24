from src.cobra.transpilers.transpiler.to_rust import TranspiladorRust
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
    t = TranspiladorRust()
    resultado = t.transpilar(ast)
    assert resultado == "let x = 10;"


def test_transpilador_condicional():
    ast = [
        NodoCondicional(
            "x > 5",
            [NodoAsignacion("y", 2)],
            [NodoAsignacion("y", 3)],
        )
    ]
    t = TranspiladorRust()
    resultado = t.transpilar(ast)
    esperado = "if x > 5 {\n    let y = 2;\n} else {\n    let y = 3;\n}"
    assert resultado == esperado


def test_transpilador_mientras():
    ast = [NodoBucleMientras("x > 0", [NodoAsignacion("x", "x - 1")])]
    t = TranspiladorRust()
    resultado = t.transpilar(ast)
    esperado = "while x > 0 {\n    let x = x - 1;\n}"
    assert resultado == esperado


def test_transpilador_funcion():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorRust()
    resultado = t.transpilar(ast)
    esperado = "fn miFuncion(a, b) {\n    let x = a + b;\n}"
    assert resultado == esperado


def test_transpilador_llamada_funcion():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorRust()
    resultado = t.transpilar(ast)
    assert resultado == "miFuncion(a, b);"


def test_transpilador_holobit():
    ast = [NodoHolobit("miHolobit", [0.8, -0.5, 1.2])]
    t = TranspiladorRust()
    resultado = t.transpilar(ast)
    assert resultado == "let miHolobit = holobit(vec![0.8, -0.5, 1.2]);"
