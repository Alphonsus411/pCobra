from io import StringIO
from unittest.mock import patch
import asyncio
import subprocess

from src.cobra.lexico.lexer import Token, TipoToken
from src.cobra.parser.parser import Parser
from src.core.ast_nodes import (
    NodoFuncion,
    NodoLlamadaFuncion,
    NodoImprimir,
    NodoValor,
    NodoEsperar,
)
from src.cobra.transpilers.transpiler.to_python import TranspiladorPython
from src.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript


def test_parser_funcion_asincronica():
    tokens = [
        Token(TipoToken.ASINCRONICO, 'asincronico'),
        Token(TipoToken.FUNC, 'func'),
        Token(TipoToken.IDENTIFICADOR, 'tarea'),
        Token(TipoToken.LPAREN, '('),
        Token(TipoToken.RPAREN, ')'),
        Token(TipoToken.DOSPUNTOS, ':'),
        Token(TipoToken.ESPERAR, 'esperar'),
        Token(TipoToken.IDENTIFICADOR, 'otro'),
        Token(TipoToken.LPAREN, '('),
        Token(TipoToken.RPAREN, ')'),
        Token(TipoToken.FIN, 'fin'),
        Token(TipoToken.EOF, None),
    ]
    ast = Parser(tokens).parsear()
    assert ast[0].asincronica
    assert isinstance(ast[0].cuerpo[0], NodoEsperar)


def test_transpiler_python_async_exec():
    ast = [
        NodoFuncion('saluda', [], [NodoImprimir(NodoValor('1'))], asincronica=True),
        NodoFuncion('principal', [], [NodoEsperar(NodoLlamadaFuncion('saluda', []))], asincronica=True),
    ]
    code = TranspiladorPython().generate_code(ast)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    patcher = patch('sys.stdout', new=StringIO())
    salida = patcher.start()
    ns = {'asyncio': asyncio}
    exec(code, ns)
    loop.run_until_complete(ns['principal']())
    loop.close()
    patcher.stop()
    assert salida.getvalue().strip() == '1'


def test_transpiler_js_async_exec(tmp_path):
    ast = [
        NodoFuncion('saluda', [], [NodoImprimir(NodoValor(1))], asincronica=True),
        NodoFuncion('principal', [], [NodoEsperar(NodoLlamadaFuncion('saluda', []))], asincronica=True),
    ]
    code = TranspiladorJavaScript().generate_code(ast)
    code = "\n".join(l for l in code.splitlines() if not l.startswith('import'))
    code += "\nprincipal();"
    archivo = tmp_path / 'async.js'
    archivo.write_text(code)
    output = subprocess.check_output(['node', str(archivo)], text=True)
    assert output.strip() == '1'
