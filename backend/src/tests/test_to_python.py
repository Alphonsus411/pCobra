from src.core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoHolobit,
    NodoValor,
)
from src.core.ast_nodes import NodoSwitch, NodoCase, NodoAsignacion
from src.cobra.transpilers.transpiler.to_python import TranspiladorPython


def test_transpilador_asignacion():
    ast = [NodoAsignacion("x", NodoValor(10))]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    esperado = "from src.core.nativos import *\nx = 10\n"
    assert resultado == esperado


def test_transpilador_condicional():
    ast = [
        NodoCondicional(
            "x > 5",
            [NodoAsignacion("y", NodoValor(2))],
            [NodoAsignacion("y", NodoValor(3))],
        )
    ]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    esperado = (
        "from src.core.nativos import *\n"
        "if x > 5:\n    y = 2\nelse:\n    y = 3\n"
    )
    assert resultado == esperado


def test_transpilador_mientras():
    ast = [
        NodoBucleMientras(
            "x > 0", [NodoAsignacion("x", NodoValor("x - 1"))]
        )
    ]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    esperado = (
        "from src.core.nativos import *\nwhile x > 0:\n    x = x - 1\n"
    )
    assert resultado == esperado


def test_transpilador_funcion():
    ast = [
        NodoFuncion(
            "miFuncion",
            ["a", "b"],
            [NodoAsignacion("x", NodoValor("a + b"))],
        )
    ]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    esperado = (
        "from src.core.nativos import *\n"
        "def miFuncion(a, b):\n    x = a + b\n"
    )
    assert resultado == esperado


def test_transpilador_llamada_funcion():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    esperado = "from src.core.nativos import *\nmiFuncion(a, b)\n"
    assert resultado == esperado


def test_transpilador_holobit():
    ast = [NodoHolobit("miHolobit", [0.8, -0.5, 1.2])]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    esperado = (
        "from src.core.nativos import *\nmiHolobit = holobit([0.8, -0.5, 1.2])\n"
    )
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
    t = TranspiladorPython()
    resultado = t.transpilar(ast)
    esperado = (
        "from src.core.nativos import *\n"
        "match x:\n"
        "    case 1:\n"
        "        y = 1\n"
        "    case 2:\n"
        "        y = 2\n"
        "    case _:\n"
        "        y = 0\n"
    )
    assert resultado == esperado
