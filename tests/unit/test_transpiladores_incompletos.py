import pytest

from cobra.transpilers.transpiler.to_cpp import TranspiladorCPP
from cobra.transpilers.transpiler.to_rust import TranspiladorRust
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.base import BaseTranspiler
from core.ast_nodes import NodoAST, NodoGlobal


class NodoInvalido(NodoAST):
    def aceptar(self, visitante):
        raise AttributeError("Nodo invalido")


class NodoDesconocido(NodoAST):
    pass


def test_transpiladores_cpp_rust_global_vacio():
    ast = [NodoGlobal(["x"])]
    cpp_code = TranspiladorCPP().generate_code(ast)
    rust_code = TranspiladorRust().generate_code(ast)

    assert "#include <pcobra/corelibs.hpp>" in cpp_code
    assert "#include <pcobra/standard_library.hpp>" in cpp_code
    assert cpp_code.endswith("// global x")

    assert "use crate::corelibs::*;" in rust_code
    assert "use crate::standard_library::*;" in rust_code
    assert "fn longitud<T: ToString>(valor: T) -> usize {" in rust_code
    assert rust_code.endswith("// global x")


def test_transpilador_js_nodo_invalido_attribute_error():
    with pytest.raises(AttributeError):
        TranspiladorJavaScript().generate_code([NodoInvalido()])


def test_generic_visit_lanza_not_implemented_error():
    class DummyTranspiler(BaseTranspiler):
        def generate_code(self, ast):
            for nodo in ast:
                nodo.aceptar(self)
            return ""

    with pytest.raises(NotImplementedError):
        DummyTranspiler().generate_code([NodoDesconocido()])
