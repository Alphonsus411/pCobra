from src.core.ast_nodes import NodoAsignacion, NodoCondicional, NodoBucleMientras, NodoFuncion, NodoLlamadaFuncion, NodoHolobit
from src.cobra.transpilers.transpiler.to_python import TranspiladorPython


def test_transpilador_asignacion():
    ast = [NodoAsignacion("x", 10)]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    assert resultado == "x = 10"


def test_transpilador_condicional():
    ast = [NodoCondicional("x > 5", [NodoAsignacion("y", 2)], [NodoAsignacion("y", 3)])]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    expected = "if x > 5:\n    y = 2\nelse:\n    y = 3"
    assert resultado == expected


def test_transpilador_mientras():
    ast = [NodoBucleMientras("x > 0", [NodoAsignacion("x", "x - 1")])]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    expected = "while x > 0:\n    x = x - 1"
    assert resultado == expected


def test_transpilador_funcion():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    expected = "def miFuncion(a, b):\n    x = a + b"
    assert resultado == expected


def test_transpilador_llamada_funcion():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    expected = "miFuncion(a, b)"
    assert resultado == expected


def test_transpilador_holobit():
    ast = [NodoHolobit("miHolobit", [0.8, -0.5, 1.2])]
    transpilador = TranspiladorPython()
    resultado = transpilador.transpilar(ast)
    expected = "miHolobit = holobit([0.8, -0.5, 1.2])"
    assert resultado == expected
