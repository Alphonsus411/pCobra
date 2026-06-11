import pytest
from core.ast_nodes import NodoFuncion, NodoRetorno, NodoValor, NodoAsignacion, NodoLlamadaFuncion
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.import_helper import get_standard_imports

IMPORTS = get_standard_imports("python")


def _ast_inline():
    return [
        NodoFuncion("uno", [], [NodoRetorno(NodoValor(1))]),
        NodoAsignacion("x", NodoLlamadaFuncion("uno", [])),
    ]


def test_python_transpiler_preserves_inlineable_function_declarations():
    codigo = TranspiladorPython().generate_code(_ast_inline())

    assert codigo == IMPORTS + "def uno():\n    return 1\nx = uno()\n"
    assert "def uno():" in codigo


def test_inline_js_transpiler():
    codigo = TranspiladorJavaScript().generate_code(_ast_inline())
    assert codigo.startswith("\n".join(get_standard_imports("javascript")) + "\n")
    assert codigo.endswith("let x = 1;")
    assert "function uno" not in codigo
