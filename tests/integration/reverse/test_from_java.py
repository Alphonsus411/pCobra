import pytest

pytest.importorskip("tree_sitter")

from cobra.transpilers.reverse.from_java import ReverseFromJava
from core.ast_nodes import (
    NodoClase,
    NodoMetodo,
    NodoBucleMientras,
    NodoCondicional,
    NodoOperacionBinaria,
)


def test_reverse_from_java_constructs():
    code = """
    class Main {
        int test(int a, int b) {
            while (a < b) { a = b; }
            if (a > b) { return a; } else { return b; }
        }
    }
    """
    transpiler = ReverseFromJava()
    ast_nodes = transpiler.generate_ast(code)

    clase = next(n for n in ast_nodes if isinstance(n, NodoClase))
    metodo = next(m for m in clase.metodos if isinstance(m, NodoMetodo))

    assert any(isinstance(n, NodoBucleMientras) for n in metodo.cuerpo)
    cond = next(n for n in metodo.cuerpo if isinstance(n, NodoCondicional))
    assert isinstance(cond.condicion, NodoOperacionBinaria)
