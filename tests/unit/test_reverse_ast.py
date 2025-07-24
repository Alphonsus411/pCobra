from cobra.transpilers.reverse.from_python import ReverseFromPython
from core.ast_nodes import (
    NodoAsignacion,
    NodoLlamadaFuncion,
    NodoValor,
    NodoIdentificador,
)


def test_reverse_from_python_assignment():
    codigo = "x = 42"
    ast = ReverseFromPython().generate_ast(codigo)
    assert len(ast) == 1
    nodo = ast[0]
    assert isinstance(nodo, NodoAsignacion)
    assert nodo.variable == "x"
    assert isinstance(nodo.expresion, NodoValor)
    assert nodo.expresion.valor == 42


def test_reverse_from_python_print():
    codigo = "x = 1\nprint(x)"
    ast = ReverseFromPython().generate_ast(codigo)
    assert len(ast) == 2
    llamada = ast[1]
    assert isinstance(llamada, NodoLlamadaFuncion)
    assert llamada.nombre == "print"
    assert isinstance(llamada.argumentos[0], NodoIdentificador)
    assert llamada.argumentos[0].nombre == "x"
