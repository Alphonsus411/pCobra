from pcobra.cobra.core import Lexer
from pcobra.cobra.core import Parser
from pcobra.core.ast_nodes import NodoEnum
from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython
from pcobra.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from pcobra.cobra.transpilers.import_helper import get_standard_imports

IMPORTS_PY = get_standard_imports("python")
IMPORTS_JS = "".join(f"{line}\n" for line in get_standard_imports("javascript"))


def test_parser_enumeracion_color():
    codigo = "enumeracion Color: ROJO, VERDE fin"
    ast = Parser(Lexer(codigo).analizar_token()).parsear()
    assert type(ast[0]).__name__ == "NodoEnum"
    assert ast[0].nombre == "Color"
    assert ast[0].miembros == ["ROJO", "VERDE"]


def test_parser_enumeracion_estado():
    codigo = "enumeracion Estado: ACTIVO, INACTIVO fin"
    parser = Parser(Lexer(codigo).analizar_token())
    ast = parser.parsear()
    assert type(ast[0]).__name__ == "NodoEnum"
    assert ast[0].nombre == "Estado"
    assert ast[0].miembros == ["ACTIVO", "INACTIVO"]


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
