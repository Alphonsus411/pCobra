from cobra.transpilers.transpiler.to_fortran import TranspiladorFortran
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


def test_transpilador_asignacion_fortran():
    ast = [NodoAsignacion("x", 10)]
    t = TranspiladorFortran()
    resultado = t.generate_code(ast)
    assert resultado == "x = 10"


def test_transpilador_funcion_fortran():
    ast = [NodoFuncion("miFuncion", ["a", "b"], [NodoAsignacion("x", "a + b")])]
    t = TranspiladorFortran()
    resultado = t.generate_code(ast)
    esperado = "subroutine miFuncion(a, b)\n    x = a + b\nend subroutine"
    assert resultado == esperado


def test_transpilador_llamada_funcion_fortran():
    ast = [NodoLlamadaFuncion("miFuncion", ["a", "b"])]
    t = TranspiladorFortran()
    resultado = t.generate_code(ast)
    assert resultado == "call miFuncion(a, b)"


def test_transpilador_imprimir_fortran():
    ast = [NodoImprimir(NodoValor("x"))]
    t = TranspiladorFortran()
    resultado = t.generate_code(ast)
    assert resultado == "print *, x"


def test_fortran_atributo_y_operaciones():
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
            NodoOperacionUnaria(Token(TipoToken.NOT, ".NOT."), NodoIdentificador("c")),
        ),
    ]
    t = TranspiladorFortran()
    resultado = t.generate_code(ast)
    esperado = (
        "obj%campo = 5\n"
        "a = 1 + 2\n"
        "b = .NOT. c"
    )
    assert resultado == esperado
