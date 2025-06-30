from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser
from src.core.ast_nodes import NodoAssert, NodoDel, NodoGlobal, NodoNoLocal, NodoLambda, NodoWith, NodoTryCatch


def test_parser_afirmar():
    ast = Parser(Lexer("afirmar 1").analizar_token()).parsear()
    assert isinstance(ast[0], NodoAssert)


def test_parser_lambda():
    ast = Parser(Lexer("lambda x: x").analizar_token()).parsear()
    assert isinstance(ast[0], NodoLambda)
