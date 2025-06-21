from io import StringIO
from unittest.mock import patch

from src.core.lexer import Token, TipoToken
from src.core.parser import Parser
from src.core.ast_nodes import NodoHilo, NodoLlamadaFuncion, NodoValor, NodoAsignacion, NodoFuncion
from src.core.interpreter import InterpretadorCobra
from src.core.transpiler.to_python import TranspiladorPython
from src.core.transpiler.to_js import TranspiladorJavaScript


def test_parser_hilo():
    tokens = [
        Token(TipoToken.HILO, 'hilo'),
        Token(TipoToken.IDENTIFICADOR, 'tarea'),
        Token(TipoToken.LPAREN, '('),
        Token(TipoToken.RPAREN, ')'),
        Token(TipoToken.EOF, None),
    ]
    ast = Parser(tokens).parsear()
    assert isinstance(ast[0], NodoHilo)
    assert ast[0].llamada.nombre == 'tarea'


def test_interpreter_hilo():
    interp = InterpretadorCobra()
    funcion = NodoFuncion('marca', [], [NodoLlamadaFuncion('imprimir', [NodoValor('ok')])])
    interp.ejecutar_funcion(funcion)
    with patch('sys.stdout', new_callable=StringIO) as out:
        hilo = interp.ejecutar_hilo(NodoHilo(NodoLlamadaFuncion('marca', [])))
        hilo.join()
        assert out.getvalue().strip() == 'ok'


def test_transpiler_python_hilo():
    ast = [NodoHilo(NodoLlamadaFuncion('tarea', []))]
    code = TranspiladorPython().transpilar(ast)
    assert 'asyncio.create_task(tarea())' in code


def test_transpiler_js_hilo():
    ast = [NodoHilo(NodoLlamadaFuncion('tarea', []))]
    code = TranspiladorJavaScript().transpilar(ast)
    assert 'Promise.resolve().then(() => tarea());' in code
