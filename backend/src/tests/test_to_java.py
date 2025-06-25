from src.cobra.transpilers.transpiler.to_java import TranspiladorJava
from src.core.ast_nodes import NodoAsignacion, NodoFuncion, NodoLlamadaFuncion, NodoImprimir, NodoValor


def test_transpilador_asignacion_java():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorJava()
    resultado = t.transpilar(ast)
    assert resultado == "var x = 10;"


def test_transpilador_funcion_java():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorJava()
    resultado = t.transpilar(ast)
    esperado = "static void miFuncion(a, b) {\n    var x = a + b;\n}"
    assert resultado == esperado


def test_transpilador_llamada_funcion_java():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorJava()
    resultado = t.transpilar(ast)
    assert resultado == "miFuncion(a, b);"


def test_transpilador_imprimir_java():
    ast = [NodoImprimir(NodoValor("x"))]
    t = TranspiladorJava()
    resultado = t.transpilar(ast)
    assert resultado == "System.out.println(x);"
