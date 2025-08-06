import core.visitor as _vis
import sys

# Compatibilidad para pruebas
sys.modules.setdefault("backend.src.core.visitor", _vis)
sys.modules.setdefault("backend.src.core", sys.modules.get("core"))

from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from core.ast_nodes import NodoEnum
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.import_helper import get_standard_imports

IMPORTS_PY = get_standard_imports("python")
IMPORTS_JS = "".join(f"{line}\n" for line in get_standard_imports("js"))


def test_parser_enum():
    codigo = "enum Color: ROJO, VERDE fin"
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    assert isinstance(ast[0], NodoEnum)
    assert ast[0].nombre == "Color"
    assert ast[0].miembros == ["ROJO", "VERDE"]


def test_transpilador_python_enum():
    nodo = NodoEnum("Color", ["ROJO", "VERDE"])
    codigo = TranspiladorPython().generate_code([nodo])
    esperado = IMPORTS_PY + "class Color:\n    ROJO = 0\n    VERDE = 1\n"
    assert codigo == esperado


def test_transpilador_js_enum():
    nodo = NodoEnum("Color", ["ROJO", "VERDE"])
    codigo = TranspiladorJavaScript().generate_code([nodo])
    esperado = IMPORTS_JS + "const Color = {ROJO: 0, VERDE: 1};"
    assert codigo == esperado
