from cobra.transpilers.transpiler.to_mojo import TranspiladorMojo
from core.ast_nodes import NodoAsignacion, NodoFuncion, NodoLlamadaFuncion, NodoImprimir, NodoValor, NodoIdentificador


def test_transpilador_asignacion_mojo():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorMojo()
    resultado = t.generate_code(ast)
    assert resultado == "var x = 10"


def test_transpilador_funcion_mojo():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", NodoIdentificador("a"))])]
    t = TranspiladorMojo()
    resultado = t.generate_code(ast)
    esperado = "fn miFuncion(a, b) {\n    var x = a\n}"
    assert resultado == esperado


def test_transpilador_llamada_funcion_mojo():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorMojo()
    resultado = t.generate_code(ast)
    assert resultado == "miFuncion(a, b)"


def test_transpilador_imprimir_mojo():
    ast = [NodoImprimir(NodoValor("x"))]
    t = TranspiladorMojo()
    resultado = t.generate_code(ast)
    assert resultado == "print(x)"
