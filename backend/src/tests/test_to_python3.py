from src.cobra.transpilers.transpiler.to_python import TranspiladorPython
from src.core.ast_nodes import (
    NodoAsignacion,
    NodoCondicional,
    NodoBucleMientras,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoHolobit,
    NodoFor,
    NodoLista,
    NodoDiccionario,
    NodoClase,
    NodoMetodo,
    NodoValor,
)


def test_transpilar_asignacion():
    nodo = NodoAsignacion("variable", NodoValor("10"))
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    esperado = "from src.core.nativos import *\nvariable = 10\n"
    assert result == esperado, "Error en la transpilaci\u00f3n de asignaci\u00f3n"


def test_transpilar_condicional():
    nodo = NodoCondicional(
        "x > 5",
        [NodoAsignacion("y", NodoValor("10"))],
        [NodoAsignacion("y", NodoValor("0"))],
    )
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = (
        "from src.core.nativos import *\n"
        "if x > 5:\n    y = 10\nelse:\n    y = 0\n"
    )
    assert result == expected, "Error en la transpilaci\u00f3n de condicional"


def test_transpilar_mientras():
    nodo = NodoBucleMientras("i < 10", [NodoAsignacion("i", NodoValor("i + 1"))])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = (
        "from src.core.nativos import *\nwhile i < 10:\n    i = i + 1\n"
    )
    assert result == expected, "Error en la transpilaci\u00f3n de bucle mientras"


def test_transpilar_funcion():
    nodo = NodoFuncion(
        "sumar",
        ["a", "b"],
        [NodoAsignacion("resultado", NodoValor("a + b"))],
    )
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = (
        "from src.core.nativos import *\n"
        "def sumar(a, b):\n    resultado = a + b\n"
    )
    assert result == expected, "Error en la transpilaci\u00f3n de funci\u00f3n"


def test_transpilar_llamada_funcion():
    nodo = NodoLlamadaFuncion("sumar", ["5", "3"])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    esperado = "from src.core.nativos import *\nsumar(5, 3)\n"
    assert result == esperado, "Error en la transpilaci\u00f3n de llamada a funci\u00f3n"


def test_transpilar_holobit():
    nodo = NodoHolobit("miHolobit", [1, 2, 3])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    esperado = "from src.core.nativos import *\nmiHolobit = holobit([1, 2, 3])\n"
    assert result == esperado, "Error en la transpilaci\u00f3n de Holobit"


def test_transpilar_for():
    nodo = NodoFor("i", "lista", [NodoAsignacion("suma", NodoValor("suma + i"))])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = (
        "from src.core.nativos import *\nfor i in lista:\n    suma = suma + i\n"
    )
    assert result == expected, "Error en la transpilaci\u00f3n de bucle for"


def test_transpilar_lista():
    nodo = NodoLista([NodoValor("1"), NodoValor("2"), NodoValor("3")])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "from src.core.nativos import *\n[1, 2, 3]\n"
    assert result == expected, "Error en la transpilaci\u00f3n de lista"


def test_transpilar_diccionario():
    nodo = NodoDiccionario([
        (NodoValor("clave1"), NodoValor("valor1")),
        (NodoValor("clave2"), NodoValor("valor2"))
    ])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = (
        "from src.core.nativos import *\n{clave1: valor1, clave2: valor2}\n"
    )
    assert result == expected, "Error en la transpilaci\u00f3n de diccionario"


def test_transpilar_clase():
    metodo = NodoMetodo("miMetodo", ["param"], [NodoAsignacion("x", NodoValor("param + 1"))])
    nodo = NodoClase("MiClase", [metodo])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = (
        "from src.core.nativos import *\n"
        "class MiClase:\n    def miMetodo(param):\n        x = param + 1\n"
    )
    assert result == expected, "Error en la transpilaci\u00f3n de clase"


def test_transpilar_metodo():
    nodo = NodoMetodo("miMetodo", ["a", "b"], [NodoAsignacion("resultado", NodoValor("a + b"))])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = (
        "from src.core.nativos import *\n"
        "def miMetodo(a, b):\n    resultado = a + b\n"
    )
    assert result == expected, "Error en la transpilaci\u00f3n de m\u00e9todo"
