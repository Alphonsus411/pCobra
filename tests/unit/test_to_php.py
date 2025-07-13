from cobra.transpilers.transpiler.to_php import TranspiladorPHP
from cobra.lexico.lexer import TipoToken, Token
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


def test_transpilador_asignacion_php():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorPHP()
    resultado = t.generate_code(ast)
    assert resultado == "$x = 10;"


def test_transpilador_funcion_php():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", NodoIdentificador("a"))])]
    t = TranspiladorPHP()
    resultado = t.generate_code(ast)
    esperado = "function miFuncion($a, $b) {\n    $x = $a;\n}"
    assert resultado == esperado


def test_transpilador_llamada_funcion_php():
    ast = [NodoLlamadaFuncion("miFuncion", [NodoIdentificador("x"), NodoValor(3)])]
    t = TranspiladorPHP()
    resultado = t.generate_code(ast)
    assert resultado == "miFuncion($x, 3);"


def test_transpilador_imprimir_php():
    ast = [NodoImprimir(NodoIdentificador("x"))]
    t = TranspiladorPHP()
    resultado = t.generate_code(ast)
    assert resultado == "echo $x;"


def test_php_atributo_y_operaciones():
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
            NodoOperacionUnaria(Token(TipoToken.NOT, "!"), NodoIdentificador("c")),
        ),
    ]
    t = TranspiladorPHP()
    resultado = t.generate_code(ast)
    esperado = (
        "$obj->campo = 5;\n"
        "$a = 1 + 2;\n"
        "$b = !$c;"
    )
    assert resultado == esperado

