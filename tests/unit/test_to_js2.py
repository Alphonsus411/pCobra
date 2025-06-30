from src.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript


# Definición de clases de nodo simuladas con los atributos necesarios para las pruebas

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


# Pruebas para verificar la funcionalidad del transpilador

def test_transpilar_asignacion():
    nodo = NodoAsignacion("variable", "10")
    transpiler = TranspiladorJavaScript()
    result = transpiler.transpilar([nodo])
    assert result == "variable = 10;", "Error en la transpilación de asignación"


def test_transpilar_condicional():
    nodo = NodoCondicional("x > 5", [NodoAsignacion("y", "10")], [NodoAsignacion("y", "0")])
    transpiler = TranspiladorJavaScript()
    result = transpiler.transpilar([nodo])
    expected = "if (x > 5) {\ny = 10;\n}\nelse {\ny = 0;\n}"
    assert result == expected, "Error en la transpilación de condicional"


def test_transpilar_mientras():
    nodo = NodoBucleMientras("i < 10", [NodoAsignacion("i", "i + 1")])
    transpiler = TranspiladorJavaScript()
    result = transpiler.transpilar([nodo])
    expected = "while (i < 10) {\ni = i + 1;\n}"
    assert result == expected, "Error en la transpilación de bucle mientras"


def test_transpilar_funcion():
    nodo = NodoFuncion("sumar", ["a", "b"], [NodoAsignacion("resultado", "a + b")])
    transpiler = TranspiladorJavaScript()
    result = transpiler.transpilar([nodo])
    expected = "function sumar(a, b) {\nresultado = a + b;\n}"
    assert result == expected, "Error en la transpilación de función"


def test_transpilar_llamada_funcion():
    nodo = NodoLlamadaFuncion("sumar", ["5", "3"])
    transpiler = TranspiladorJavaScript()
    result = transpiler.transpilar([nodo])
    assert result == "sumar(5, 3);", "Error en la transpilación de llamada a función"


def test_transpilar_holobit():
    nodo = NodoHolobit("miHolobit", [1, 2, 3])
    transpiler = TranspiladorJavaScript()
    result = transpiler.transpilar([nodo])
    assert result == "let miHolobit = new Holobit([1, 2, 3]);", "Error en la transpilación de Holobit"
