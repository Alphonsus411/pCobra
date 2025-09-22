from io import StringIO
from unittest.mock import patch
import asyncio
import subprocess

from cobra.core import Token, TipoToken
from cobra.core import Parser

try:
    from pcobra.core.ast_nodes import (
        NodoFuncion,
        NodoLlamadaFuncion,
        NodoImprimir,
        NodoValor,
        NodoEsperar,
        NodoPara,
        NodoWith,
    )
except ImportError:  # pragma: no cover - entorno heredado
    from core.ast_nodes import (  # type: ignore
        NodoFuncion,
        NodoLlamadaFuncion,
        NodoImprimir,
        NodoValor,
        NodoEsperar,
        NodoPara,
        NodoWith,
    )
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript


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


def test_parser_para_asincronico():
    tokens = [
        Token(TipoToken.ASINCRONICO, "asincronico"),
        Token(TipoToken.PARA, "para"),
        Token(TipoToken.IDENTIFICADOR, "item"),
        Token(TipoToken.IN, "in"),
        Token(TipoToken.IDENTIFICADOR, "datos"),
        Token(TipoToken.DOSPUNTOS, ":"),
        Token(TipoToken.PASAR, "pasar"),
        Token(TipoToken.FIN, "fin"),
        Token(TipoToken.EOF, None),
    ]
    parser = Parser(tokens)
    ast = parser.parsear()
    assert isinstance(ast[0], NodoPara)
    assert ast[0].asincronico is True


def test_parser_con_asincronico():
    tokens = [
        Token(TipoToken.ASINCRONICO, "asincronico"),
        Token(TipoToken.CON, "con"),
        Token(TipoToken.IDENTIFICADOR, "recurso"),
        Token(TipoToken.DOSPUNTOS, ":"),
        Token(TipoToken.PASAR, "pasar"),
        Token(TipoToken.FIN, "fin"),
        Token(TipoToken.EOF, None),
    ]
    parser = Parser(tokens)
    ast = parser.parsear()
    assert isinstance(ast[0], NodoWith)
    assert ast[0].asincronico is True


def test_parser_con_alias_mixto_emite_advertencia():
    tokens = [
        Token(TipoToken.ASINCRONICO, "asincronico"),
        Token(TipoToken.WITH, "with"),
        Token(TipoToken.IDENTIFICADOR, "resource"),
        Token(TipoToken.COMO, "como"),
        Token(TipoToken.IDENTIFICADOR, "alias"),
        Token(TipoToken.DOSPUNTOS, ":"),
        Token(TipoToken.PASAR, "pasar"),
        Token(TipoToken.FIN, "fin"),
        Token(TipoToken.EOF, None),
    ]
    parser = Parser(tokens)
    ast = parser.parsear()
    assert isinstance(ast[0], NodoWith)
    assert parser.advertencias
    assert any("mezcla de alias" in mensaje for mensaje in parser.advertencias)


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
