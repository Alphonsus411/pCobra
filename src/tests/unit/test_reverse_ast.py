from cobra.transpilers.reverse.from_python import ReverseFromPython
from core.ast_nodes import (
    NodoAsignacion,
    NodoLlamadaFuncion,
    NodoValor,
    NodoIdentificador,
    NodoOperacionBinaria,
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


def test_reverse_from_python_chain_compare():
    codigo = "res = a < b < c"
    ast = ReverseFromPython().generate_ast(codigo)
    nodo = ast[0]
    assert isinstance(nodo, NodoAsignacion)
    expr = nodo.expresion
    assert isinstance(expr, NodoOperacionBinaria)
    assert expr.operador.valor == "and"

    izquierda = expr.izquierda
    derecha = expr.derecha
    assert isinstance(izquierda, NodoOperacionBinaria)
    assert isinstance(derecha, NodoOperacionBinaria)
    assert izquierda.operador.valor == "<"
    assert derecha.operador.valor == "<"

    assert isinstance(izquierda.izquierda, NodoIdentificador)
    assert izquierda.izquierda.nombre == "a"
    assert isinstance(izquierda.derecha, NodoIdentificador)
    assert izquierda.derecha.nombre == "b"
    assert isinstance(derecha.izquierda, NodoIdentificador)
    assert derecha.izquierda.nombre == "b"
    assert isinstance(derecha.derecha, NodoIdentificador)
    assert derecha.derecha.nombre == "c"


def test_reverse_from_python_chain_compare_mixed():
    codigo = "res = a < b <= c"
    ast = ReverseFromPython().generate_ast(codigo)
    expr = ast[0].expresion
    assert isinstance(expr, NodoOperacionBinaria)
    assert expr.operador.valor == "and"

    izquierda = expr.izquierda
    assert isinstance(izquierda, NodoOperacionBinaria)
    assert izquierda.operador.valor == "<"

    derecha = expr.derecha
    assert isinstance(derecha, NodoOperacionBinaria)
    assert derecha.operador.valor == "<="


def test_reverse_from_python_chain_compare_three():
    codigo = "res = a < b < c < d"
    ast = ReverseFromPython().generate_ast(codigo)
    expr = ast[0].expresion
    assert isinstance(expr, NodoOperacionBinaria)
    assert expr.operador.valor == "and"

    izquierda = expr.izquierda
    derecha = expr.derecha
    assert isinstance(izquierda, NodoOperacionBinaria)
    assert isinstance(derecha, NodoOperacionBinaria)
    assert izquierda.operador.valor == "and"
    assert derecha.operador.valor == "<"

    primera = izquierda.izquierda
    segunda = izquierda.derecha
    assert isinstance(primera, NodoOperacionBinaria)
    assert isinstance(segunda, NodoOperacionBinaria)
    assert primera.operador.valor == "<"
    assert segunda.operador.valor == "<"
