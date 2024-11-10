from src.core.transpiler.to_python import TranspiladorPython


# Clases de nodo para pruebas
class NodoAsignacion:
    def __init__(self, identificador, valor):
        self.identificador = identificador
        self.valor = valor


class NodoCondicional:
    def __init__(self, condicion, bloque_si, bloque_sino=None):
        self.condicion = condicion
        self.bloque_si = bloque_si
        self.bloque_sino = bloque_sino or []


class NodoBucleMientras:
    def __init__(self, condicion, cuerpo):
        self.condicion = condicion
        self.cuerpo = cuerpo


class NodoFuncion:
    def __init__(self, nombre, parametros, cuerpo):
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo


class NodoLlamadaFuncion:
    def __init__(self, nombre, argumentos):
        self.nombre = nombre
        self.argumentos = argumentos


class NodoHolobit:
    def __init__(self, nombre):
        self.nombre = nombre


# Pruebas para el transpilador a Python

def test_transpilar_asignacion():
    nodo = NodoAsignacion("variable", "10")
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    assert result == "variable = 10\n", "Error en la transpilación de asignación"


def test_transpilar_condicional():
    nodo = NodoCondicional("x > 5", [NodoAsignacion("y", "10")], [NodoAsignacion("y", "0")])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "if x > 5:\n    y = 10\nelse:\n    y = 0\n"
    assert result == expected, "Error en la transpilación de condicional"


def test_transpilar_mientras():
    nodo = NodoBucleMientras("i < 10", [NodoAsignacion("i", "i + 1")])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "while i < 10:\n    i = i + 1\n"
    assert result == expected, "Error en la transpilación de bucle mientras"


def test_transpilar_funcion():
    nodo = NodoFuncion("sumar", ["a", "b"], [NodoAsignacion("resultado", "a + b")])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "def sumar(a, b):\n    resultado = a + b\n"
    assert result == expected, "Error en la transpilación de función"


def test_transpilar_llamada_funcion():
    nodo = NodoLlamadaFuncion("sumar", ["5", "3"])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    assert result == "sumar(5, 3)\n", "Error en la transpilación de llamada a función"


def test_transpilar_holobit():
    nodo = NodoHolobit("miHolobit")
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    assert result == "holobit(miHolobit)\n", "Error en la transpilación de Holobit"
