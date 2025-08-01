import pytest
from core.ast_nodes import NodoAsignacion, NodoCondicional, NodoBucleMientras, NodoFuncion, NodoLlamadaFuncion, NodoHolobit, NodoFor, NodoLista, NodoDiccionario, NodoClase, NodoMetodo, NodoValor, NodoRetorno
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.import_helper import get_standard_imports

IMPORTS = get_standard_imports("python")


def test_transpilar_asignacion():
    nodo = NodoAsignacion("variable", NodoValor("10"))
    transpiler = TranspiladorPython()
    result = transpiler.generate_code([nodo])
    expected = IMPORTS + "variable = 10\n"
    assert result == expected, "Error en la transpilación de asignación"


def test_transpilar_condicional():
    nodo = NodoCondicional("x > 5", [NodoAsignacion("y", NodoValor("10"))], [NodoAsignacion("y", NodoValor("0"))])
    transpiler = TranspiladorPython()
    result = transpiler.generate_code([nodo])
    expected = (
        IMPORTS
        + "if x > 5:\n    y = 10\nelse:\n    y = 0\n"
    )
    assert result == expected, "Error en la transpilación de condicional"


def test_transpilar_mientras():
    nodo = NodoBucleMientras("i < 10", [NodoAsignacion("i", NodoValor("i + 1"))])
    transpiler = TranspiladorPython()
    result = transpiler.generate_code([nodo])
    expected = IMPORTS + "while i < 10:\n    i = i + 1\n"
    assert result == expected, "Error en la transpilación de bucle mientras"


def test_transpilar_funcion():
    nodo = NodoFuncion("sumar", ["a", "b"], [NodoAsignacion("resultado", NodoValor("a + b"))])
    transpiler = TranspiladorPython()
    result = transpiler.generate_code([nodo])
    expected = (
        IMPORTS
        + "def sumar(a, b):\n    resultado = a + b\n"
    )
    assert result == expected, "Error en la transpilación de función"


def test_transpilar_llamada_funcion():
    nodo = NodoLlamadaFuncion("sumar", ["5", "3"])
    transpiler = TranspiladorPython()
    result = transpiler.generate_code([nodo])
    expected = IMPORTS + "sumar(5, 3)\n"
    assert result == expected, "Error en la transpilación de llamada a función"


def test_transpilar_holobit():
    nodo = NodoHolobit([NodoValor(1), NodoValor(2), NodoValor(3)])
    transpiler = TranspiladorPython()
    result = transpiler.generate_code([nodo])
    expected = IMPORTS + "holobit([1, 2, 3])\n"
    assert result == expected, "Error en la transpilación de holobit"


def test_transpilar_for():
    nodo = NodoFor("i", "lista", [NodoAsignacion("suma", NodoValor("suma + i"))])
    transpiler = TranspiladorPython()
    result = transpiler.generate_code([nodo])
    expected = (
        IMPORTS + "for i in lista:\n    suma = suma + i\n"
    )
    assert result == expected, "Error en la transpilación de bucle for"


def test_transpilar_lista():
    nodo = NodoLista([NodoValor("1"), NodoValor("2"), NodoValor("3")])
    transpiler = TranspiladorPython()
    result = transpiler.generate_code([nodo])
    expected = IMPORTS + "[1, 2, 3]\n"
    assert result == expected, "Error en la transpilación de lista"


def test_transpilar_diccionario():
    nodo = NodoDiccionario([(NodoValor("clave1"), NodoValor("valor1")), (NodoValor("clave2"), NodoValor("valor2"))])
    transpiler = TranspiladorPython()
    result = transpiler.generate_code([nodo])
    expected = (
        IMPORTS + "{clave1: valor1, clave2: valor2}\n"
    )
    assert result == expected, "Error en la transpilación de diccionario"


def test_transpilar_clase():
    metodo = NodoMetodo("mi_metodo", ["param"], [NodoAsignacion("x", NodoValor("param + 1"))])
    nodo = NodoClase("MiClase", [metodo])
    transpiler = TranspiladorPython()
    result = transpiler.generate_code([nodo])
    expected = (
        IMPORTS
        + "class MiClase:\n    def mi_metodo(param):\n        x = param + 1\n"
    )
    assert result == expected, "Error en la transpilación de clase"


def test_transpilar_clase_multibase():
    metodo = NodoMetodo("m", ["self"], [NodoRetorno(NodoValor(1))])
    nodo = NodoClase("Hija", [metodo], ["Base1", "Base2"])
    transpiler = TranspiladorPython()
    result = transpiler.generate_code([nodo])
    expected = (
        IMPORTS
        + "class Hija(Base1, Base2):\n    def m(self):\n        return 1\n"
    )
    assert result == expected, "Error en herencia múltiple"


def test_transpilar_metodo():
    nodo = NodoMetodo("mi_metodo", ["a", "b"], [NodoAsignacion("resultado", NodoValor("a + b"))])
    transpiler = TranspiladorPython()
    result = transpiler.generate_code([nodo])
    expected = (
        IMPORTS
        + "def mi_metodo(a, b):\n    resultado = a + b\n"
    )
    assert result == expected, "Error en la transpilación de método"
