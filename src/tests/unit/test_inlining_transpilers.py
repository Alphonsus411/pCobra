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


def test_inline_python_transpiler():
    codigo = TranspiladorPython().generate_code(_ast_inline())
    assert codigo == IMPORTS + "x = 1\n"


def test_inline_js_transpiler():
    codigo = TranspiladorJavaScript().generate_code(_ast_inline())
    esperado = (
        "import * as io from './nativos/io.js';\n"
        "import * as net from './nativos/io.js';\n"
        "import * as matematicas from './nativos/matematicas.js';\n"
        "import { Pila, Cola } from './nativos/estructuras.js';\n"
        "let x = 1;"
    )
    assert codigo == esperado
