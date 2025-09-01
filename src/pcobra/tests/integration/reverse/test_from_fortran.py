"""Pruebas para el transpilador inverso de Fortran."""

from cobra.transpilers.reverse.from_fortran import ReverseFromFortran
from core.ast_nodes import (
    NodoAsignacion,
    NodoDeclaracion,
    NodoFuncion,
    NodoIdentificador,
    NodoModulo,
    NodoValor,
)


def test_reverse_from_fortran_program():
    code = "program hola\ninteger :: a\na = 5\nend program hola\n"
    ast = ReverseFromFortran().generate_ast(code)
    assert len(ast) == 1
    modulo = ast[0]
    assert isinstance(modulo, NodoModulo)
    assert modulo.nombre == "hola"
    assert len(modulo.cuerpo) == 2

    decl = modulo.cuerpo[0]
    assert isinstance(decl, NodoDeclaracion)
    assert decl.nombre == "a"
    assert decl.tipo == "integer"

    asign = modulo.cuerpo[1]
    assert isinstance(asign, NodoAsignacion)
    assert isinstance(asign.variable, NodoIdentificador)
    assert asign.variable.nombre == "a"
    assert isinstance(asign.expresion, NodoValor)
    assert asign.expresion.valor == 5


def test_reverse_from_fortran_subroutine():
    code = "subroutine foo(x)\ninteger :: x\nend subroutine foo\n"
    ast = ReverseFromFortran().generate_ast(code)
    assert len(ast) == 1
    func = ast[0]
    assert isinstance(func, NodoFuncion)
    assert func.nombre == "foo"
    assert func.parametros == ["x"]
    assert len(func.cuerpo) == 1
    decl = func.cuerpo[0]
    assert isinstance(decl, NodoDeclaracion)
    assert decl.nombre == "x"
