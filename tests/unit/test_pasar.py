from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser
from src.core.ast_nodes import NodoBucleMientras, NodoPasar
from src.cobra.transpilers.transpiler.to_python import TranspiladorPython
from src.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from src.cobra.transpilers.import_helper import get_standard_imports

IMPORTS = get_standard_imports("python")


def test_parser_pasar():
    codigo = """
    mientras x > 0:
        pasar
    fin
    """
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    assert isinstance(ast[0], NodoBucleMientras)
    assert isinstance(ast[0].cuerpo[0], NodoPasar)


def test_transpilar_pasar_python():
    nodo = NodoPasar()
    t = TranspiladorPython()
    resultado = t.generate_code([nodo])
    esperado = IMPORTS + "pass\n"
    assert resultado == esperado


def test_transpilar_pasar_js():
    nodo = NodoPasar()
    t = TranspiladorJavaScript()
    resultado = t.generate_code([nodo])
    esperado = (
        "import * as io from './nativos/io.js';\n"
        "import * as net from './nativos/io.js';\n"
        "import * as matematicas from './nativos/matematicas.js';\n"
        "import { Pila, Cola } from './nativos/estructuras.js';\n"
        ";"
    )
    assert resultado == esperado

