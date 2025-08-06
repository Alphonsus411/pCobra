from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.transpiler.to_cpp import TranspiladorCPP
from cobra.transpilers.reverse.from_js import ReverseFromJS
from cobra.transpilers.reverse.from_cpp import ReverseFromCPP
from cobra.transpilers.import_helper import get_standard_imports
import pytest
from core.ast_nodes import (
    NodoAsignacion,
    NodoOption,
    NodoValor,
    NodoIdentificador,
    NodoSwitch,
    NodoCase,
    NodoPattern,
)


def _strip_js_imports(code: str) -> str:
    lines = code.splitlines()
    return "\n".join(lines[len(get_standard_imports("js")):])


def test_roundtrip_js_option_pattern():
    try:
        parser = ReverseFromJS()
    except NotImplementedError:
        pytest.skip("tree-sitter JS no disponible")
    ast = [
        NodoAsignacion("a", NodoOption(None)),
        NodoSwitch(
            NodoIdentificador("a"),
            [NodoCase(NodoPattern(NodoValor(1)), [NodoAsignacion("y", NodoValor(1))])],
            [NodoAsignacion("y", NodoValor(0))],
        ),
    ]
    code = TranspiladorJavaScript().generate_code(ast)
    code = _strip_js_imports(code)
    ast_back = parser.generate_ast(code)
    assert ast_back == ast


def test_roundtrip_cpp_option_pattern():
    try:
        parser = ReverseFromCPP()
    except NotImplementedError:
        pytest.skip("tree-sitter C++ no disponible")
    ast = [
        NodoAsignacion("a", NodoOption(None)),
        NodoSwitch(
            NodoIdentificador("a"),
            [NodoCase(NodoPattern(NodoValor(1)), [NodoAsignacion("y", NodoValor(1))])],
            [NodoAsignacion("y", NodoValor(0))],
        ),
    ]
    code = TranspiladorCPP().generate_code(ast)
    ast_back = parser.generate_ast(code)
    assert ast_back == ast
