from io import StringIO
from unittest.mock import patch
import asyncio
import subprocess

from src.cobra.lexico.lexer import Token, TipoToken
from src.cobra.parser.parser import Parser
from src.core.ast_nodes import NodoHilo, NodoLlamadaFuncion, NodoValor, NodoImprimir, NodoIdentificador, NodoAsignacion, NodoFuncion
from src.core.interpreter import InterpretadorCobra
from src.cobra.transpilers.transpiler.to_python import TranspiladorPython
from src.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript


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
    code = TranspiladorPython().generate_code(ast)
    assert 'asyncio.create_task(tarea())' in code


def test_transpiler_js_hilo():
    ast = [NodoHilo(NodoLlamadaFuncion('tarea', []))]
    code = TranspiladorJavaScript().generate_code(ast)
    assert 'Promise.resolve().then(() => tarea());' in code


def test_interpreter_varios_hilos():
    interp = InterpretadorCobra()
    funcion = NodoFuncion(
        'tarea',
        ['msg'],
        [NodoLlamadaFuncion('imprimir', [Token(TipoToken.IDENTIFICADOR, 'msg')])],
    )
    interp.ejecutar_funcion(funcion)
    patcher = patch('sys.stdout', new=StringIO())
    salida = patcher.start()
    h1 = interp.ejecutar_hilo(NodoHilo(NodoLlamadaFuncion('tarea', [NodoValor('uno')])))
    h2 = interp.ejecutar_hilo(NodoHilo(NodoLlamadaFuncion('tarea', [NodoValor('dos')])))
    h3 = interp.ejecutar_hilo(NodoHilo(NodoLlamadaFuncion('tarea', [NodoValor('tres')])))
    for h in (h1, h2, h3):
        h.join()
        assert not h.is_alive()
    patcher.stop()
    lineas = salida.getvalue().strip().splitlines()
    assert set(lineas) == {'uno', 'dos', 'tres'}


def test_hilos_preservan_variables_globales():
    interp = InterpretadorCobra()
    interp.ejecutar_asignacion(NodoAsignacion('contador', NodoValor(0)))
    funcion = NodoFuncion('trabajo', [], [NodoAsignacion('contador', NodoValor(5))])
    interp.ejecutar_funcion(funcion)
    h1 = interp.ejecutar_hilo(NodoHilo(NodoLlamadaFuncion('trabajo', [])))
    h2 = interp.ejecutar_hilo(NodoHilo(NodoLlamadaFuncion('trabajo', [])))
    h1.join(); h2.join()
    assert interp.variables['contador'] == 0


def test_transpiled_python_hilos_exec():
    ast = [
        NodoFuncion('tarea', ['n'], [NodoImprimir(NodoIdentificador('n'))]),
        NodoHilo(NodoLlamadaFuncion('tarea', [NodoValor(1)])),
        NodoHilo(NodoLlamadaFuncion('tarea', [NodoValor(2)])),
    ]
    code = TranspiladorPython().generate_code(ast)
    code = code.replace('def tarea(', 'async def tarea(')
    code = code.replace('asyncio.create_task', 'loop.create_task')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    patcher = patch('sys.stdout', new=StringIO())
    salida = patcher.start()
    exec(code, {'loop': loop, 'asyncio': asyncio})
    loop.run_until_complete(asyncio.sleep(0.01))
    loop.close()
    patcher.stop()
    lineas = salida.getvalue().strip().splitlines()
    assert set(lineas) == {'1', '2'}


def test_transpiled_js_hilos_exec(tmp_path):
    ast = [
        NodoFuncion('tarea', [], [NodoImprimir(NodoValor(1))]),
        NodoHilo(NodoLlamadaFuncion('tarea', [])),
        NodoHilo(NodoLlamadaFuncion('tarea', [])),
    ]
    code = TranspiladorJavaScript().generate_code(ast)
    code = "\n".join(l for l in code.splitlines() if not l.startswith('import'))
    archivo = tmp_path / 'script.js'
    archivo.write_text(code)
    output = subprocess.check_output(['node', str(archivo)], text=True)
    assert output.strip().splitlines() == ['1', '1']
