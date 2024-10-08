# src/tests/test_js_transpiler.py
import pytest
from src.core.lexer import Lexer
from src.core.transpiler.js_transpiler import JSTranspiler


def test_js_transpiler():
    source_code = 'si 5 mas 10 mientras 20'
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    transpiler = JSTranspiler(tokens)
    transpiled_code = transpiler.transpile()

    assert transpiled_code == 'if 5 else 10 while 20'


def test_js_with_loops_and_return():
    source_code = 'funcion loop() { mientras x < 10 { si x mas 1 break } return x }'
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    transpiler = JSTranspiler(tokens)
    transpiled_code = transpiler.transpile()

    expected_code = 'function loop() { while (x < 10) { if (x) else 1 break } return x }'
    assert transpiled_code == expected_code

