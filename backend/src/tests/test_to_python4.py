import pytest
from src.core.ast_nodes import NodoAsignacion, NodoCondicional, NodoBucleMientras, NodoFuncion, NodoLlamadaFuncion, NodoHolobit, NodoFor, NodoLista, NodoDiccionario, NodoClase, NodoMetodo, NodoValor
from src.core.transpiler.to_python import TranspiladorPython


def test_transpilar_asignacion():
    nodo = NodoAsignacion("variable", NodoValor("10"))
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "variable = 10\n"
    assert result == expected, "Error en la transpilación de asignación"


def test_transpilar_condicional():
    nodo = NodoCondicional("x > 5", [NodoAsignacion("y", NodoValor("10"))], [NodoAsignacion("y", NodoValor("0"))])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "if x > 5:\n    y = 10\nelse:\n    y = 0\n"
    assert result == expected, "Error en la transpilación de condicional"


def test_transpilar_mientras():
    nodo = NodoBucleMientras("i < 10", [NodoAsignacion("i", NodoValor("i + 1"))])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "while i < 10:\n    i = i + 1\n"
    assert result == expected, "Error en la transpilación de bucle mientras"


def test_transpilar_funcion():
    nodo = NodoFuncion("sumar", ["a", "b"], [NodoAsignacion("resultado", NodoValor("a + b"))])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "def sumar(a, b):\n    resultado = a + b\n"
    assert result == expected, "Error en la transpilación de función"


def test_transpilar_llamada_funcion():
    nodo = NodoLlamadaFuncion("sumar", ["5", "3"])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "sumar(5, 3)\n"
    assert result == expected, "Error en la transpilación de llamada a función"


def test_transpilar_holobit():
    nodo = NodoHolobit([NodoValor(1), NodoValor(2), NodoValor(3)])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "holobit([1, 2, 3])\n"
    assert result == expected, "Error en la transpilación de holobit"


def test_transpilar_for():
    nodo = NodoFor("i", "lista", [NodoAsignacion("suma", NodoValor("suma + i"))])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "for i in lista:\n    suma = suma + i\n"
    assert result == expected, "Error en la transpilación de bucle for"


def test_transpilar_lista():
    nodo = NodoLista([NodoValor("1"), NodoValor("2"), NodoValor("3")])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "[1, 2, 3]\n"
    assert result == expected, "Error en la transpilación de lista"


def test_transpilar_diccionario():
    nodo = NodoDiccionario([(NodoValor("clave1"), NodoValor("valor1")), (NodoValor("clave2"), NodoValor("valor2"))])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "{clave1: valor1, clave2: valor2}\n"
    assert result == expected, "Error en la transpilación de diccionario"


def test_transpilar_clase():
    metodo = NodoMetodo("mi_metodo", ["param"], [NodoAsignacion("x", NodoValor("param + 1"))])
    nodo = NodoClase("MiClase", [metodo])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "class MiClase:\n    def mi_metodo(param):\n        x = param + 1\n"
    assert result == expected, "Error en la transpilación de clase"


def test_transpilar_metodo():
    nodo = NodoMetodo("mi_metodo", ["a", "b"], [NodoAsignacion("resultado", NodoValor("a + b"))])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "def mi_metodo(a, b):\n    resultado = a + b\n"
    assert result == expected, "Error en la transpilación de método"
