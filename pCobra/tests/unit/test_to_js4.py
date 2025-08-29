from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.import_helper import get_standard_imports


# Nodos simulados para pruebas
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
    def __init__(self, nombre, valores):
        self.nombre = nombre
        self.valores = valores


# Nodos avanzados para pruebas
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
    def __init__(self, nombre, cuerpo, bases=None):
        self.nombre = nombre
        self.cuerpo = cuerpo
        self.bases = bases or []


class NodoMetodo:
    def __init__(self, nombre, parametros, cuerpo):
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo


# Pruebas para TranspiladorJavaScript

def test_transpilar_asignacion():
    nodo = NodoAsignacion("variable", "10")
    transpiler = TranspiladorJavaScript()
    result = transpiler.generate_code([nodo])
    assert result == "variable = 10;", "Error en la transpilación de asignación"


def test_transpilar_condicional():
    nodo = NodoCondicional("x > 5", [NodoAsignacion("y", "10")], [NodoAsignacion("y", "0")])
    transpiler = TranspiladorJavaScript()
    result = transpiler.generate_code([nodo])
    expected = "if (x > 5) {\ny = 10;\n}\nelse {\ny = 0;\n}"
    assert result == expected, "Error en la transpilación de condicional"


def test_transpilar_mientras():
    nodo = NodoBucleMientras("i < 10", [NodoAsignacion("i", "i + 1")])
    transpiler = TranspiladorJavaScript()
    result = transpiler.generate_code([nodo])
    expected = "while (i < 10) {\ni = i + 1;\n}"
    assert result == expected, "Error en la transpilación de bucle mientras"


def test_transpilar_funcion():
    nodo = NodoFuncion("sumar", ["a", "b"], [NodoAsignacion("resultado", "a + b")])
    transpiler = TranspiladorJavaScript()
    result = transpiler.generate_code([nodo])
    expected = "function sumar(a, b) {\nresultado = a + b;\n}"
    assert result == expected, "Error en la transpilación de función"


def test_transpilar_llamada_funcion():
    nodo = NodoLlamadaFuncion("sumar", ["5", "3"])
    transpiler = TranspiladorJavaScript()
    result = transpiler.generate_code([nodo])
    assert result == "sumar(5, 3);", "Error en la transpilación de llamada a función"


def test_transpilar_holobit():
    nodo = NodoHolobit("miHolobit", [1, 2, 3])
    transpiler = TranspiladorJavaScript()
    result = transpiler.generate_code([nodo])
    assert result == "let miHolobit = new Holobit([1, 2, 3]);", "Error en la transpilación de Holobit"


# Pruebas avanzadas

def test_transpilar_for():
    nodo = NodoFor("i", "lista", [NodoAsignacion("suma", "suma + i")])
    transpiler = TranspiladorJavaScript()
    result = transpiler.generate_code([nodo])
    expected = "for (let i of lista) {\nsuma = suma + i;\n}"
    assert result == expected, "Error en la transpilación de bucle for"


def test_transpilar_lista():
    nodo = NodoLista(["1", "2", "3"])
    transpiler = TranspiladorJavaScript()
    result = transpiler.generate_code([nodo])
    expected = "[1, 2, 3]"
    assert result == expected, "Error en la transpilación de lista"


def test_transpilar_diccionario():
    nodo = NodoDiccionario([("clave1", "valor1"), ("clave2", "valor2")])
    transpiler = TranspiladorJavaScript()
    result = transpiler.generate_code([nodo])
    expected = "{clave1: valor1, clave2: valor2}"
    assert result == expected, "Error en la transpilación de diccionario"


def test_transpilar_clase():
    metodo = NodoMetodo("miMetodo", ["param"], [NodoAsignacion("x", "param + 1")])
    nodo = NodoClase("MiClase", [metodo])
    transpiler = TranspiladorJavaScript()
    result = transpiler.generate_code([nodo])
    expected = "class MiClase {\nmiMetodo(param) {\nx = param + 1;\n}\n}"
    assert result == expected, "Error en la transpilación de clase"


def test_transpilar_clase_multibase():
    metodo = NodoMetodo("m", ["p"], [NodoAsignacion("x", "p")])
    nodo = NodoClase("Hija", [metodo], ["Base1", "Base2"])
    transpiler = TranspiladorJavaScript()
    result = transpiler.generate_code([nodo])
    imports = "".join(f"{line}\n" for line in get_standard_imports("js"))
    expected = (
        imports
        + "class Hija extends Base1 { /* bases: Base1, Base2 */\n"
        + "m(p) {\n"
        + "x = p;\n"
        + "}\n"
        + "}"
    )
    assert result == expected, "Error en herencia múltiple"


def test_transpilar_metodo():
    nodo = NodoMetodo("miMetodo", ["a", "b"], [NodoAsignacion("resultado", "a + b")])
    transpiler = TranspiladorJavaScript()
    result = transpiler.generate_code([nodo])
    expected = "miMetodo(a, b) {\nresultado = a + b;\n}"
    assert result == expected, "Error en la transpilación de método"
