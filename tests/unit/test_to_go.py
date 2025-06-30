from src.cobra.transpilers.transpiler.to_go import TranspiladorGo
from src.core.ast_nodes import NodoAsignacion, NodoFuncion, NodoLlamadaFuncion, NodoImprimir, NodoValor


def test_transpilador_asignacion_go():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorGo()
    resultado = t.transpilar(ast)
    assert resultado == "x := 10"


def test_transpilador_funcion_go():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorGo()
    resultado = t.transpilar(ast)
    esperado = "func miFuncion(a, b) {\n    x := a + b\n}"
    assert resultado == esperado


def test_transpilador_llamada_funcion_go():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorGo()
    resultado = t.transpilar(ast)
    assert resultado == "miFuncion(a, b)"


def test_transpilador_imprimir_go():
    ast = [NodoImprimir(NodoValor("x"))]
    t = TranspiladorGo()
    resultado = t.transpilar(ast)
    assert resultado == "fmt.Println(x)"
