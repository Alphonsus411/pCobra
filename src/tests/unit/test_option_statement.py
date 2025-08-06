from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from core.ast_nodes import NodoAsignacion, NodoOption, NodoValor
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.transpiler.to_cpp import TranspiladorCPP
from cobra.transpilers.transpiler.to_rust import TranspiladorRust
from cobra.transpilers.import_helper import get_standard_imports


def test_parser_option():
    codigo = "option a = 5\noption b = None"
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()
    esperado = [
        NodoAsignacion("a", NodoOption(NodoValor(5))),
        NodoAsignacion("b", NodoOption(None)),
    ]
    assert ast == esperado


def test_transpilacion_option():
    codigo = "option a = 5\noption b = None"
    tokens = Lexer(codigo).tokenizar()
    ast = Parser(tokens).parsear()

    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    cpp = TranspiladorCPP().generate_code(ast)
    rust = TranspiladorRust().generate_code(ast)

    assert py == get_standard_imports("python") + "a = 5\nb = None\n"
    js_imports = "\n".join(get_standard_imports("js")) + "\n"
    assert js == js_imports + "let a = 5;\nlet b = null;"
    assert cpp == "auto a = 5;\nauto b = std::nullopt;"
    assert rust == "let a = Some(5);\nlet b = None;"
