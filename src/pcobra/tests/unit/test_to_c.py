from cobra.transpilers.transpiler.to_c import TranspiladorC
from core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoRetorno,
)


def test_transpilador_asignacion_c():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorC()
    resultado = t.generate_code(ast)
    assert resultado == "int x = 10;"


def test_transpilador_condicional_c():
    ast = [
        NodoCondicional(
            "x > 5",
            [NodoAsignacion("y", 2)],
            [NodoAsignacion("y", 3)],
        )
    ]
    t = TranspiladorC()
    resultado = t.generate_code(ast)
    esperado = "if (x > 5) {\n    int y = 2;\n} else {\n    int y = 3;\n}"
    assert resultado == esperado


def test_transpilador_mientras_c():
    ast = [NodoBucleMientras("x > 0", [NodoAsignacion("x", "x - 1")])]
    t = TranspiladorC()
    resultado = t.generate_code(ast)
    esperado = "while (x > 0) {\n    int x = x - 1;\n}"
    assert resultado == esperado


def test_transpilador_funcion_c():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorC()
    resultado = t.generate_code(ast)
    esperado = "void miFuncion(int a, int b) {\n    int x = a + b;\n}"
    assert resultado == esperado


def test_transpilador_retorno_c():
    ast = [NodoFuncion("main", [], [NodoRetorno("2 + 2")])]
    t = TranspiladorC()
    resultado = t.generate_code(ast)
    esperado = "int main() {\n    return 2 + 2;\n}"
    assert resultado == esperado


def test_transpilador_llamada_funcion_c():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorC()
    resultado = t.generate_code(ast)
    assert resultado == "miFuncion(a, b);"
