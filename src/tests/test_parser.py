# src/tests/test_parser.py
import pytest
from src.core.lexer import Lexer
from src.core.parser import Parser


def test_parser():
    source_code = "funcion sumar si 5 mientras"
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    parser.parse()
