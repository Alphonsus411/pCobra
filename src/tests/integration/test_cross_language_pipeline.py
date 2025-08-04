from cobra.transpilers.reverse.from_python import ReverseFromPython
from cobra.transpilers.reverse.from_js import ReverseFromJS
import cobra.macro  # type: ignore

if not hasattr(cobra.macro, "expandir_macros"):  # pragma: no cover - fallback
    cobra.macro.expandir_macros = lambda nodos: nodos

from cobra.transpilers.transpiler.to_java import TranspiladorJava
from cobra.transpilers.transpiler.to_rust import TranspiladorRust
import pytest


def test_python_to_java():
    codigo = "x = 1\nprint(x)"
    ast = ReverseFromPython().generate_ast(codigo)
    java_code = TranspiladorJava().generate_code(ast)
    esperado = "var x = 1;\nprint(x);"
    assert java_code == esperado


def test_js_to_rust():
    codigo = "x = 1;\nprint(x);"
    try:
        ast = ReverseFromJS().generate_ast(codigo)
    except NotImplementedError:
        pytest.skip("Parser de JavaScript no disponible")
    rust_code = TranspiladorRust().generate_code(ast)
    esperado = "let x = 1;\nprint(x);"
    assert rust_code == esperado
