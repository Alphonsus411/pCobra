# src/tests/test_lexer.py
import pytest
from src.core.lexer import Lexer


def test_lexer():
    source_code = "funcion sumar si 5 mientras"
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    assert tokens == [('KEYWORD', 'funcion'), ('IDENTIFIER', 'sumar'), ('KEYWORD', 'si'), ('NUMBER', '5'),
                      ('KEYWORD', 'mientras')]
