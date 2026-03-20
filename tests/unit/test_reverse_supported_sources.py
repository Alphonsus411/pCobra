import pytest

from cobra.transpilers.reverse.from_java import ReverseFromJava
from cobra.transpilers.reverse.from_js import ReverseFromJS
from cobra.transpilers.reverse.from_python import ReverseFromPython
from core.ast_nodes import (
    NodoAsignacion,
    NodoClase,
    NodoCondicional,
    NodoFuncion,
    NodoMetodo,
    NodoPara,
    NodoRetorno,
)


def test_reverse_from_python_basic_control_flow():
    codigo = (
        "def foo(x):\n"
        "    y = x\n"
        "    if y:\n"
        "        y = y\n"
        "    for i in [1, 2, 3]:\n"
        "        y = y\n"
    )

    ast = ReverseFromPython().generate_ast(codigo)
    assert len(ast) == 1
    fn = ast[0]
    assert isinstance(fn, NodoFuncion)
    assert fn.nombre == "foo"
    assert fn.parametros == ["x"]
    assert len(fn.cuerpo) == 3
    assert isinstance(fn.cuerpo[0], NodoAsignacion)
    assert isinstance(fn.cuerpo[1], NodoCondicional)
    assert isinstance(fn.cuerpo[2], NodoPara)


def test_reverse_from_js_basic_function():
    try:
        transpiler = ReverseFromJS()
    except NotImplementedError:
        pytest.skip("tree-sitter JavaScript no disponible")

    ast = transpiler.generate_ast("function foo(x) { let y = x; return y; }")

    assert len(ast) == 1
    fn = ast[0]
    assert isinstance(fn, NodoFuncion)
    assert fn.nombre == "foo"
    assert fn.parametros == ["x"]
    assert len(fn.cuerpo) == 2
    assert isinstance(fn.cuerpo[0], NodoAsignacion)
    assert isinstance(fn.cuerpo[1], NodoRetorno)


def test_reverse_from_java_basic_class_method():
    try:
        transpiler = ReverseFromJava()
    except NotImplementedError:
        pytest.skip("tree-sitter Java no disponible")

    codigo = (
        "class Foo { "
        "int bar(int x) { "
        "if (x > 0) { return x; } "
        "return 0; "
        "} "
        "}"
    )
    ast = transpiler.generate_ast(codigo)

    assert len(ast) == 1
    clase = ast[0]
    assert isinstance(clase, NodoClase)
    assert clase.nombre == "Foo"
    assert len(clase.metodos) == 1

    metodo = clase.metodos[0]
    assert isinstance(metodo, NodoMetodo)
    assert metodo.nombre == "bar"
    assert metodo.parametros == ["x"]
    assert len(metodo.cuerpo) == 2
    assert isinstance(metodo.cuerpo[0], NodoCondicional)
    assert isinstance(metodo.cuerpo[1], NodoRetorno)
