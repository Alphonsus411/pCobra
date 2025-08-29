"""Pruebas para el transpilador inverso de Perl."""

from cobra.transpilers.reverse.from_perl import ReverseFromPerl
from core.ast_nodes import NodoAsignacion, NodoIdentificador, NodoValor


def test_reverse_from_perl_simple_assignment():
    code = "my $x = 10;"
    ast = ReverseFromPerl().generate_ast(code)
    assert len(ast) == 1
    nodo = ast[0]
    assert isinstance(nodo, NodoAsignacion)
    assert isinstance(nodo.variable, NodoIdentificador)
    assert nodo.variable.nombre == "x"
    assert isinstance(nodo.expresion, NodoValor)
    assert nodo.expresion.valor == 10


def test_reverse_from_perl_multiple_assignment():
    code = "my ($x, $y) = (1, 2);"
    ast = ReverseFromPerl().generate_ast(code)
    assert len(ast) == 2
    primero, segundo = ast
    assert isinstance(primero, NodoAsignacion)
    assert isinstance(segundo, NodoAsignacion)
    assert primero.variable.nombre == "x"
    assert primero.expresion.valor == 1
    assert segundo.variable.nombre == "y"
    assert segundo.expresion.valor == 2
