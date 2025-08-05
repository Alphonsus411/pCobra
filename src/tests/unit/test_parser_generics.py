from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from core.ast_nodes import NodoFuncion, NodoClase


def test_parser_funcion_generica():
    codigo = """
    func identidad<T>(x):
        fin
    """
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    assert len(ast) == 1
    func = ast[0]
    assert isinstance(func, NodoFuncion)
    assert func.type_params == ["T"]


def test_parser_clase_generica():
    codigo = """
    clase Caja<T>:
        fin
    """
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    assert len(ast) == 1
    clase = ast[0]
    assert isinstance(clase, NodoClase)
    assert clase.type_params == ["T"]
