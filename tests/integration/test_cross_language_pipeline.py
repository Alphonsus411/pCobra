import cobra.macro  # type: ignore
import pcobra  # noqa: F401  # asegura el registro de paquetes extendidos
from cobra.transpilers.hololang_bridge import ensure_cobra_ast
from cobra.transpilers.reverse.from_js import ReverseFromJS
from cobra.transpilers.reverse.from_python import ReverseFromPython
from cobra.transpilers.transpiler.to_asm import TranspiladorASM
from cobra.transpilers.transpiler.to_hololang import TranspiladorHololang
from cobra.transpilers.transpiler.to_java import TranspiladorJava
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.transpiler.to_rust import TranspiladorRust
from pcobra.cobra.core import Lexer as CobraLexer, Parser as CobraParser
from pcobra.cobra.reverse import ReverseFromHololang
from pcobra.core.hololang_ir import build_hololang_ir
import pytest

if not hasattr(cobra.macro, "expandir_macros"):  # pragma: no cover - fallback
    cobra.macro.expandir_macros = lambda nodos: nodos


def test_python_to_java():
    codigo = "x = 1\nprint(x)"
    ast = ReverseFromPython().generate_ast(codigo)
    java_code = TranspiladorJava().generate_code(ast)
    esperado = "\n".join(
        [
            "public class Main {",
            "    public static void main(String[] args) {",
            "        var x = 1;",
            "        print(x);",
            "    }",
            "}",
        ]
    )
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


def test_cobra_to_hololang_to_asm():
    codigo = "x = 1\nimprimir(x)\n"
    tokens = CobraLexer(codigo).tokenizar()
    ast = CobraParser(tokens).parsear()

    hololang_code = TranspiladorHololang().generate_code(ast)
    ast_desde_hololang = ReverseFromHololang().generate_ast(hololang_code)
    modulo_ir = build_hololang_ir(ast_desde_hololang)
    asm_code = TranspiladorASM().generate_code(modulo_ir)

    esperado = "\n".join(
        [
            "; Nodo NodoUsar no soportado",
            "; Nodo NodoUsar no soportado",
            "SET x, 1",
            "CALL print x",
        ]
    )
    assert asm_code == esperado


def test_hololang_to_python():
    codigo_holo = "let x = 1;\nprint(x);\n"
    ast = ReverseFromHololang().generate_ast(codigo_holo)
    modulo_ir = build_hololang_ir(ast)
    ast_cobra = ensure_cobra_ast(modulo_ir)

    python_code = TranspiladorPython().generate_code(ast_cobra)
    esperado = "\n".join(
        [
            "from core.nativos import *",
            "from corelibs import *",
            "from standard_library import *",
            "x = 1",
            "print(x)",
            "",
        ]
    )
    assert python_code == esperado


def test_hololang_to_js():
    codigo_holo = "let x = 1;\nprint(x);\n"
    ast = ReverseFromHololang().generate_ast(codigo_holo)
    modulo_ir = build_hololang_ir(ast)
    ast_cobra = ensure_cobra_ast(modulo_ir)

    js_code = TranspiladorJavaScript().generate_code(ast_cobra)
    esperado = "\n".join(
        [
            "import * as io from './nativos/io.js';",
            "import * as net from './nativos/red.js';",
            "import * as matematicas from './nativos/matematicas.js';",
            "import { Pila, Cola } from './nativos/estructuras.js';",
            "import * as archivo from './nativos/archivo.js';",
            "import * as coleccion from './nativos/coleccion.js';",
            "import * as numero from './nativos/numero.js';",
            "import * as red from './nativos/red.js';",
            "import * as seguridad from './nativos/seguridad.js';",
            "import * as sistema from './nativos/sistema.js';",
            "import * as texto from './nativos/texto.js';",
            "import * as tiempo from './nativos/tiempo.js';",
            "let x = 1;",
            "print(x);",
        ]
    )
    assert js_code == esperado
