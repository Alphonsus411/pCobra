from src.core.transpiler.to_python import TranspiladorPython


# Clases de nodo simuladas para pruebas
class NodoAsignacion:
    def __init__(self, identificador, valor):
        self.identificador = identificador
        self.valor = valor


class NodoCondicional:
    def __init__(self, condicion, cuerpo_si, cuerpo_sino=None):
        self.condicion = condicion
        self.cuerpo_si = cuerpo_si
        self.cuerpo_sino = cuerpo_sino or []


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


# Nuevos nodos avanzados para pruebas
class NodoFor:
    def __init__(self, variable, iterable, cuerpo):
        self.variable = variable
        self.iterable = iterable
        self.cuerpo = cuerpo


class NodoLista:
    def __init__(self, elementos):
        self.elementos = elementos


class NodoDiccionario:
    def __init__(self, pares):
        self.pares = pares


class NodoClase:
    def __init__(self, nombre, cuerpo):
        self.nombre = nombre
        self.cuerpo = cuerpo


class NodoMetodo:
    def __init__(self, nombre, parametros, cuerpo):
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo


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


# Pruebas para nuevas estructuras avanzadas

def test_transpilar_for():
    nodo = NodoFor("i", "lista", [NodoAsignacion("suma", "suma + i")])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "for i in lista:\n    suma = suma + i\n"
    assert result == expected, "Error en la transpilación de bucle for"


def test_transpilar_lista():
    nodo = NodoLista(["1", "2", "3"])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "[1, 2, 3]\n"
    assert result == expected, "Error en la transpilación de lista"


def test_transpilar_diccionario():
    nodo = NodoDiccionario([("clave1", "valor1"), ("clave2", "valor2")])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "{clave1: valor1, clave2: valor2}\n"
    assert result == expected, "Error en la transpilación de diccionario"


def test_transpilar_clase():
    metodo = NodoMetodo("miMetodo", ["param"], [NodoAsignacion("x", "param + 1")])
    nodo = NodoClase("MiClase", [metodo])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "class MiClase:\n    def miMetodo(param):\n        x = param + 1\n"
    assert result == expected, "Error en la transpilación de clase"


def test_transpilar_metodo():
    nodo = NodoMetodo("miMetodo", ["a", "b"], [NodoAsignacion("resultado", "a + b")])
    transpiler = TranspiladorPython()
    result = transpiler.transpilar([nodo])
    expected = "def miMetodo(a, b):\n    resultado = a + b\n"
    assert result == expected, "Error en la transpilación de método"
