from src.cobra.transpilers.transpiler.to_cpp import TranspiladorCPP
from src.core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoHolobit,
    NodoSwitch,
    NodoCase,
    NodoAsignacion,
    NodoMetodo,
    NodoClase,
    NodoYield,
    NodoValor,
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

def test_transpilador_clase():
    metodo = NodoMetodo("saludar", ["self"], [NodoAsignacion("x", 1)])
    ast = [NodoClase("Persona", [metodo])]
    t = TranspiladorCPP()
    resultado = t.transpilar(ast)
    esperado = (
        "class Persona {\n"
        "    auto saludar(auto self) {\n"
        "        auto x = 1;\n"
        "    }\n"
        "};"
    )
    assert resultado == esperado


def test_transpilador_yield():
    ast = [NodoFuncion("generador", [], [NodoYield(NodoValor(1))])]
    t = TranspiladorCPP()
    resultado = t.transpilar(ast)
    esperado = "void generador() {\n    co_yield 1;\n}"
    assert resultado == esperado


def test_transpilador_switch():
    ast = [
        NodoSwitch(
            "x",
            [
                NodoCase(NodoValor(1), [NodoAsignacion("y", NodoValor(1))]),
                NodoCase(NodoValor(2), [NodoAsignacion("y", NodoValor(2))]),
            ],
            [NodoAsignacion("y", NodoValor(0))],
        )
    ]
    t = TranspiladorCPP()
    resultado = t.transpilar(ast)
    esperado = (
        "switch (x) {\n"
        "    case 1:\n"
        "        auto y = 1;\n"
        "        break;\n"
        "    case 2:\n"
        "        auto y = 2;\n"
        "        break;\n"
        "    default:\n"
        "        auto y = 0;\n"
        "        break;\n"
        "}"
    )
    assert resultado == esperado
