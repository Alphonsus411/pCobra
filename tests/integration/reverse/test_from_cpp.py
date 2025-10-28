import pytest

pytest.importorskip("tree_sitter")

from cobra.transpilers.reverse.from_cpp import ReverseFromCPP
from core.ast_nodes import NodoClase, NodoMetodo, NodoAsignacion, NodoBloque


def test_reverse_from_cpp_class_members():
    code = """
    class Persona { int edad; void saludar() {} };
    """
    transpiler = ReverseFromCPP()
    ast_nodes = transpiler.generate_ast(code)
    clase = next(n for n in ast_nodes if isinstance(n, NodoClase))
    assert any(isinstance(m, NodoAsignacion) for m in clase.metodos)
    assert any(isinstance(m, NodoMetodo) for m in clase.metodos)


def test_reverse_from_cpp_namespace():
    code = """
    namespace N { class A {}; }
    """
    transpiler = ReverseFromCPP()
    ast_nodes = transpiler.generate_ast(code)
    bloque = next(n for n in ast_nodes if isinstance(n, NodoBloque))
    assert any(isinstance(n, NodoClase) for n in getattr(bloque, 'sentencias', []))

