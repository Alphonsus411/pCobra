from src.cobra.transpilers.transpiler.to_rust import TranspiladorRust
from src.core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoHolobit,
    NodoClase,
    NodoMetodo,
    NodoYield,
    NodoValor,
    NodoSwitch,
    NodoCase,
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

def test_transpilador_clase():
    metodo = NodoMetodo("saludar", ["self"], [NodoAsignacion("x", 1)])
    ast = [NodoClase("Persona", [metodo])]
    t = TranspiladorRust()
    resultado = t.transpilar(ast)
    esperado = (
        "struct Persona {}\n\n"
        "impl Persona {\n"
        "    fn saludar(self) {\n"
        "        let x = 1;\n"
        "    }\n"
        "}"
    )
    assert resultado == esperado


def test_transpilador_yield():
    ast = [NodoFuncion("generador", [], [NodoYield(NodoValor(1))])]
    t = TranspiladorRust()
    resultado = t.transpilar(ast)
    esperado = "fn generador() {\n    yield 1;\n}"
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
    t = TranspiladorRust()
    resultado = t.transpilar(ast)
    esperado = (
        "match x {\n"
        "    1 => {\n"
        "        let y = 1;\n"
        "    },\n"
        "    2 => {\n"
        "        let y = 2;\n"
        "    },\n"
        "    _ => {\n"
        "        let y = 0;\n"
        "    },\n"
        "}"
    )
    assert resultado == esperado
