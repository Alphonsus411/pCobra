import pytest
from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from core.ast_nodes import (
    NodoBucleMientras,
    NodoPara,
    NodoRomper,
    NodoContinuar,
    NodoValor,
)
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.import_helper import get_standard_imports

IMPORTS = get_standard_imports("python")


def test_parser_romper_continuar():
    codigo = """
    mientras x > 5:
        romper
    fin
    para i in lista:
        continuar
    fin
    """
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    assert isinstance(ast[0], NodoBucleMientras)
    assert isinstance(ast[0].cuerpo[0], NodoRomper)
    assert isinstance(ast[1], NodoPara)
    assert isinstance(ast[1].cuerpo[0], NodoContinuar)


def test_transpilar_romper_python():
    nodo = NodoBucleMientras("i < 3", [NodoRomper()])
    t = TranspiladorPython()
    resultado = t.generate_code([nodo])
    esperado = IMPORTS + "while i < 3:\n    break\n"
    assert resultado == esperado


def test_transpilar_continuar_js():
    nodo = NodoPara("x", NodoValor("datos"), [NodoContinuar()])
    t = TranspiladorJavaScript()
    resultado = t.generate_code([nodo])
    esperado = (
        "import * as io from './nativos/io.js';\n"
        "import * as net from './nativos/io.js';\n"
        "import * as matematicas from './nativos/matematicas.js';\n"
        "import { Pila, Cola } from './nativos/estructuras.js';\n"
        "for (let x of datos) {\ncontinue;\n}"
    )
    assert resultado == esperado
