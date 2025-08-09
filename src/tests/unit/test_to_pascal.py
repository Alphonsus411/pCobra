from cobra.core import TipoToken, Token
from cobra.transpilers.transpiler.to_pascal import TranspiladorPascal
from core.ast_nodes import (
    NodoAsignacion,
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoImprimir,
    NodoValor,
    NodoIdentificador,
    NodoAtributo,
    NodoOperacionBinaria,
    NodoOperacionUnaria,
)


def test_transpilador_asignacion_pascal():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorPascal()
    resultado = t.generate_code(ast)
    assert resultado == "x := 10;"


def test_transpilador_funcion_pascal():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorPascal()
    resultado = t.generate_code(ast)
    esperado = "procedure miFuncion(a, b);\nbegin\n    x := a + b;\nend;"
    assert resultado == esperado


def test_transpilador_llamada_funcion_pascal():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorPascal()
    resultado = t.generate_code(ast)
    assert resultado == "miFuncion(a, b);"


def test_transpilador_imprimir_pascal():
    ast = [NodoImprimir(NodoValor("x"))]
    t = TranspiladorPascal()
    resultado = t.generate_code(ast)
    assert resultado == "writeln(x);"


def test_pascal_atributo_y_operaciones():
    ast = [
        NodoAsignacion(
            NodoAtributo(NodoIdentificador("obj"), "campo"),
            NodoValor(5),
        ),
        NodoAsignacion(
            "a",
            NodoOperacionBinaria(
                NodoValor(1), Token(TipoToken.SUMA, "+"), NodoValor(2)
            ),
        ),
        NodoAsignacion(
            "b",
            NodoOperacionUnaria(Token(TipoToken.NOT, "not"), NodoIdentificador("c")),
        ),
    ]
    t = TranspiladorPascal()
    resultado = t.generate_code(ast)
    esperado = (
        "obj.campo := 5;\n"
        + "a := 1 + 2;\n"
        + "b := not c;"
    )
    assert resultado == esperado
