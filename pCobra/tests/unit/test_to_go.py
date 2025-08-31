from cobra.transpilers.transpiler.to_go import TranspiladorGo
from core.ast_nodes import NodoAsignacion, NodoFuncion, NodoLlamadaFuncion, NodoImprimir, NodoValor


def test_transpilador_asignacion_go():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorGo()
    resultado = t.generate_code(ast)
    assert resultado == "package main\n\nfunc main() {\n    x := 10\n}"


def test_transpilador_funcion_go():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorGo()
    resultado = t.generate_code(ast)
    esperado = "package main\n\nfunc miFuncion(a, b) {\n    x := a + b\n}"
    assert resultado == esperado


def test_transpilador_llamada_funcion_go():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorGo()
    resultado = t.generate_code(ast)
    assert resultado == "package main\n\nfunc main() {\n    miFuncion(a, b)\n}"


def test_transpilador_imprimir_go():
    ast = [NodoImprimir(NodoValor("x"))]
    t = TranspiladorGo()
    resultado = t.generate_code(ast)
    esperado = (
        "package main\n\nimport (\n    \"fmt\"\n)\n\nfunc main() {\n    fmt.Println(\"x\")\n}"
    )
    assert resultado == esperado
