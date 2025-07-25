import pytest
from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.import_helper import get_standard_imports

IMPORTS = get_standard_imports("python")


def test_integracion_python():
    codigo = "var x = 10"
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    resultado = TranspiladorPython().generate_code(ast)
    esperado = IMPORTS + "x = 10\n"
    assert resultado == esperado


def test_integracion_js():
    codigo = "var x = 10\nimprimir(x)"
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    resultado = TranspiladorJavaScript().generate_code(ast)
    esperado = (
        "import * as io from './nativos/io.js';\n"
        + "import * as net from './nativos/io.js';\n"
        + "import * as matematicas from './nativos/matematicas.js';\n"
        + "import { Pila, Cola } from './nativos/estructuras.js';\n"
        + "let x = 10;\n"
        + "console.log(x);"
    )
    assert resultado == esperado


def test_integracion_condicional_python():
    codigo = "var x = 10\nsi x > 5 :\n    imprimir(x)\nfin"
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    resultado = TranspiladorPython().generate_code(ast)
    esperado = (
        IMPORTS
        + "x = 10\n"
        + "if x > 5:\n"
        + "    print(x)\n"
    )
    assert resultado == esperado
