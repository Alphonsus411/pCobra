import pytest

pytest.importorskip("tree_sitter")

from cobra.transpilers.reverse.from_js import ReverseFromJS
from core.ast_nodes import (
    NodoFuncion,
    NodoClase,
    NodoBucleMientras,
    NodoOperacionBinaria,
)


def test_reverse_from_js_constructs():
    code = """
    function add(a, b) { return a + b; }
    class Greeter { greet() { return a; } }
    while (a < b) { a = b; }
    for (; a < b;) { a = b; }
    """
    transpiler = ReverseFromJS()
    ast_nodes = transpiler.generate_ast(code)

    assert any(isinstance(n, NodoFuncion) for n in ast_nodes)
    assert any(isinstance(n, NodoClase) for n in ast_nodes)
    loops = [n for n in ast_nodes if isinstance(n, NodoBucleMientras)]
    assert len(loops) == 2
    func = next(n for n in ast_nodes if isinstance(n, NodoFuncion))
    assert isinstance(func.cuerpo[0].expresion, NodoOperacionBinaria)
