from src.cobra.transpilers.transpiler.to_pascal import TranspiladorPascal
from src.core.ast_nodes import NodoAsignacion, NodoFuncion, NodoLlamadaFuncion, NodoImprimir, NodoValor


def test_transpilador_asignacion_pascal():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorPascal()
    resultado = t.transpilar(ast)
    assert resultado == "x := 10;"


def test_transpilador_funcion_pascal():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorPascal()
    resultado = t.transpilar(ast)
    esperado = "procedure miFuncion(a, b);\nbegin\n    x := a + b;\nend;"
    assert resultado == esperado


def test_transpilador_llamada_funcion_pascal():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorPascal()
    resultado = t.transpilar(ast)
    assert resultado == "miFuncion(a, b);"


def test_transpilador_imprimir_pascal():
    ast = [NodoImprimir(NodoValor("x"))]
    t = TranspiladorPascal()
    resultado = t.transpilar(ast)
    assert resultado == "writeln(x);"
