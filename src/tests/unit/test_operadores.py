import pytest
from cobra.lexico.lexer import Lexer, Token, TipoToken
from cobra.parser.parser import Parser
from core.ast_nodes import NodoOperacionBinaria, NodoOperacionUnaria
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.import_helper import get_standard_imports

IMPORTS = get_standard_imports("python")
from core.interpreter import InterpretadorCobra


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


def test_menorque_operador():
    lexer = Lexer("1 < 2")
    tokens = lexer.tokenizar()
    tipos = [t.tipo for t in tokens[:-1]]
    assert tipos == [TipoToken.ENTERO, TipoToken.MENORQUE, TipoToken.ENTERO]

    parser = Parser(tokens)
    ast = parser.parsear()[0]
    assert isinstance(ast, NodoOperacionBinaria)
    assert ast.operador.tipo == TipoToken.MENORQUE


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
    py_code = TranspiladorPython().generate_code([expr])
    js_code = TranspiladorJavaScript().generate_code([expr])
    assert py_code == IMPORTS + "True"
    assert js_code == (
        "import * as io from './nativos/io.js';\n"
        "import * as net from './nativos/io.js';\n"
        "import * as matematicas from './nativos/matematicas.js';\n"
        "import { Pila, Cola } from './nativos/estructuras.js';\n"
        "True"
    )
