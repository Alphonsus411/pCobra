import pytest
from src.core.lexer import Lexer, Token, TipoToken
from src.core.parser import Parser, NodoOperacionBinaria, NodoOperacionUnaria
from src.core.interpreter import InterpretadorCobra
from src.core.transpiler.to_python import TranspiladorPython
from src.core.transpiler.to_js import TranspiladorJavaScript


def test_lexer_nuevos_operadores():
    codigo = "var x = 1 == 1 && 2 != 3 || !0 >= 1 <= 2 % 2"
    lexer = Lexer(codigo)
    tokens = lexer.tokenizar()
    tipos = [t.tipo for t in tokens[:-1]]
    assert tipos == [
        TipoToken.VAR, TipoToken.IDENTIFICADOR, TipoToken.ASIGNAR,
        TipoToken.ENTERO, TipoToken.IGUAL, TipoToken.ENTERO,
        TipoToken.AND, TipoToken.ENTERO, TipoToken.DIFERENTE, TipoToken.ENTERO,
        TipoToken.OR, TipoToken.NOT, TipoToken.ENTERO,
        TipoToken.MAYORIGUAL, TipoToken.ENTERO,
        TipoToken.MENORIGUAL, TipoToken.ENTERO,
        TipoToken.MOD, TipoToken.ENTERO,
    ]


def test_parser_precedencia_operadores():
    tokens = [
        Token(TipoToken.ENTERO, 1),
        Token(TipoToken.SUMA, '+'),
        Token(TipoToken.ENTERO, 2),
        Token(TipoToken.MULT, '*'),
        Token(TipoToken.ENTERO, 3),
        Token(TipoToken.IGUAL, '=='),
        Token(TipoToken.ENTERO, 7),
        Token(TipoToken.AND, '&&'),
        Token(TipoToken.NOT, '!'),
        Token(TipoToken.ENTERO, 0),
        Token(TipoToken.EOF, None),
    ]
    parser = Parser(tokens)
    ast = parser.parsear()
    expr = ast[0]
    assert isinstance(expr, NodoOperacionBinaria)
    assert expr.operador.tipo == TipoToken.AND
    assert isinstance(expr.izquierda, NodoOperacionBinaria)
    assert isinstance(expr.derecha, NodoOperacionUnaria)
    assert expr.izquierda.operador.tipo == TipoToken.IGUAL


def test_interpreter_operaciones():
    tokens = [
        Token(TipoToken.ENTERO, 1),
        Token(TipoToken.SUMA, '+'),
        Token(TipoToken.ENTERO, 2),
        Token(TipoToken.MULT, '*'),
        Token(TipoToken.ENTERO, 3),
        Token(TipoToken.IGUAL, '=='),
        Token(TipoToken.ENTERO, 7),
        Token(TipoToken.AND, '&&'),
        Token(TipoToken.NOT, '!'),
        Token(TipoToken.ENTERO, 0),
        Token(TipoToken.EOF, None),
    ]
    parser = Parser(tokens)
    expr = parser.parsear()[0]
    interp = InterpretadorCobra()
    resultado = interp.evaluar_expresion(expr)
    assert resultado is True


def test_transpiladores_operaciones():
    tokens = [
        Token(TipoToken.ENTERO, 1),
        Token(TipoToken.SUMA, '+'),
        Token(TipoToken.ENTERO, 2),
        Token(TipoToken.MULT, '*'),
        Token(TipoToken.ENTERO, 3),
        Token(TipoToken.IGUAL, '=='),
        Token(TipoToken.ENTERO, 7),
        Token(TipoToken.AND, '&&'),
        Token(TipoToken.NOT, '!'),
        Token(TipoToken.ENTERO, 0),
        Token(TipoToken.EOF, None),
    ]
    parser = Parser(tokens)
    expr = parser.parsear()[0]
    py_code = TranspiladorPython().transpilar([expr])
    js_code = TranspiladorJavaScript().transpilar([expr])
    assert py_code == "1 + 2 * 3 == 7 and not 0"
    assert js_code == "1 + 2 * 3 == 7 && !0"
