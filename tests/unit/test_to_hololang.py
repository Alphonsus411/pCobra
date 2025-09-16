"""Pruebas unitarias para el transpilador de Hololang."""

from cobra.core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoHolobit,
    NodoValor,
    NodoRetorno,
    NodoIdentificador,
    NodoEsperar,
)
from cobra.transpilers.import_helper import get_standard_imports
from cobra.transpilers.transpiler.to_hololang import TranspiladorHololang

IMPORTS = "".join(f"{line}\n" for line in get_standard_imports("hololang"))


def test_transpilador_hololang_asignacion():
    ast = [NodoAsignacion("x", NodoValor(10))]
    transpiler = TranspiladorHololang()
    resultado = transpiler.generate_code(ast)
    esperado = IMPORTS + "let x = 10;\n"
    assert resultado == esperado


def test_transpilador_hololang_condicional():
    ast = [
        NodoCondicional(
            "x > 5",
            [NodoAsignacion("y", NodoValor(2))],
            [NodoAsignacion("y", NodoValor(3))],
        )
    ]
    transpiler = TranspiladorHololang()
    resultado = transpiler.generate_code(ast)
    esperado = (
        IMPORTS
        + "if (x > 5) {\n"
        + "    let y = 2;\n"
        + "} else {\n"
        + "    let y = 3;\n"
        + "}\n"
    )
    assert resultado == esperado


def test_transpilador_hololang_mientras():
    ast = [NodoBucleMientras("x > 0", [NodoAsignacion("x", "x - 1")])]
    transpiler = TranspiladorHololang()
    resultado = transpiler.generate_code(ast)
    esperado = IMPORTS + "while (x > 0) {\n    let x = x - 1;\n}\n"
    assert resultado == esperado


def test_transpilador_hololang_funcion():
    ast = [
        NodoFuncion(
            "sumar",
            ["a", "b"],
            [
                NodoAsignacion("resultado", "a + b"),
                NodoRetorno(NodoIdentificador("resultado")),
            ],
        )
    ]
    transpiler = TranspiladorHololang()
    resultado = transpiler.generate_code(ast)
    esperado = (
        IMPORTS
        + "fn sumar(a, b) {\n"
        + "    let resultado = a + b;\n"
        + "    return resultado;\n"
        + "}\n"
    )
    assert resultado == esperado


def test_transpilador_hololang_llamada_funcion():
    ast = [NodoLlamadaFuncion("sumar", [1, 2])]
    transpiler = TranspiladorHololang()
    resultado = transpiler.generate_code(ast)
    esperado = IMPORTS + "sumar(1, 2);\n"
    assert resultado == esperado


def test_transpilador_hololang_holobit():
    ast = [NodoHolobit("miHolobit", [0.8, -0.5, 1.2])]
    transpiler = TranspiladorHololang()
    resultado = transpiler.generate_code(ast)
    esperado = IMPORTS + "let miHolobit = Holobit::new([0.8, -0.5, 1.2]);\n"
    assert resultado == esperado


def test_transpilador_hololang_async_inserta_import():
    ast = [
        NodoFuncion(
            "principal",
            [],
            [NodoEsperar(NodoLlamadaFuncion("trabajo", []))],
            asincronica=True,
        )
    ]
    transpiler = TranspiladorHololang()
    resultado = transpiler.generate_code(ast)
    esperado = (
        "use holo.async::*;\n"
        + IMPORTS
        + "async fn principal() {\n"
        + "    await trabajo();\n"
        + "}\n"
    )
    assert resultado == esperado
