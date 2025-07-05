from src.cobra.transpilers.transpiler.to_matlab import TranspiladorMatlab
from src.core.ast_nodes import NodoAsignacion, NodoFuncion, NodoLlamadaFuncion, NodoImprimir, NodoValor


def test_transpilador_asignacion_matlab():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorMatlab()
    resultado = t.generate_code(ast)
    assert resultado == "x = 10;"


def test_transpilador_funcion_matlab():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorMatlab()
    resultado = t.generate_code(ast)
    esperado = "function miFuncion(a, b)\n    x = a + b;\nend"
    assert resultado == esperado


def test_transpilador_llamada_funcion_matlab():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorMatlab()
    resultado = t.generate_code(ast)
    assert resultado == "miFuncion(a, b);"


def test_transpilador_imprimir_matlab():
    ast = [NodoImprimir(NodoValor("x"))]
    t = TranspiladorMatlab()
    resultado = t.generate_code(ast)
    assert resultado == "disp(x);"
