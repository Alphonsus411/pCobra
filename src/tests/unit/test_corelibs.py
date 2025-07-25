from types import ModuleType
import sys
import os
from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest

sys.modules.setdefault('yaml', ModuleType('yaml'))

import backend.corelibs as core
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.import_helper import get_standard_imports
from core.ast_nodes import NodoLlamadaFuncion, NodoValor

IMPORTS_PY = get_standard_imports("python")
IMPORTS_JS = "".join(f"{line}\n" for line in get_standard_imports("js"))


def test_texto_funcs():
    assert core.mayusculas('hola') == 'HOLA'
    assert core.minusculas('HOLA') == 'hola'
    assert core.invertir('abc') == 'cba'
    assert core.concatenar('a', 'b') == 'ab'


def test_numero_funcs():
    assert core.es_par(4) is True
    assert core.es_par(5) is False
    assert core.es_primo(7) is True
    assert core.es_primo(4) is False
    assert core.factorial(5) == 120
    assert core.promedio([1, 2, 3]) == 2.0


def test_archivo_funcs(tmp_path):
    ruta = tmp_path / 'f.txt'
    core.escribir(ruta, 'data')
    assert core.existe(ruta)
    assert core.leer(ruta) == 'data'
    core.eliminar(ruta)
    assert not core.existe(ruta)


def test_tiempo_funcs(monkeypatch):
    ahora = core.ahora()
    assert isinstance(ahora, datetime)
    fecha = datetime(2020, 1, 2, 3, 4, 5)
    assert core.formatear(fecha, '%Y') == '2020'
    called = {}
    def fake_sleep(seg):
        called['v'] = seg
    monkeypatch.setattr(core.tiempo.time, 'sleep', fake_sleep)
    core.dormir(0.01)
    assert called['v'] == 0.01


def test_coleccion_funcs():
    datos = [3, 1, 2, 1]
    assert core.ordenar(datos) == [1, 1, 2, 3]
    assert core.maximo(datos) == 3
    assert core.minimo(datos) == 1
    assert core.sin_duplicados(datos) == [3, 1, 2]


def test_seguridad_funcs():
    assert core.hash_sha256('a') == 'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb'
    uuid = core.generar_uuid()
    assert isinstance(uuid, str) and len(uuid) == 36


def test_red_funcs(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.read.return_value = b'ok'
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_resp
    with patch('backend.corelibs.red.urllib.request.urlopen', return_value=mock_cm) as mock_urlopen:
        assert core.obtener_url('http://x') == 'ok'
        assert core.enviar_post('http://x', {'a': 1}) == 'ok'
        mock_urlopen.assert_any_call('http://x', timeout=5)
        mock_urlopen.assert_any_call('http://x', b'a=1', timeout=5)
        assert mock_urlopen.call_count == 2


def test_red_obtener_url_rechaza_esquema_no_http():
    with patch('backend.corelibs.red.urllib.request.urlopen') as mock_urlopen:
        with pytest.raises(ValueError):
            core.obtener_url('ftp://ejemplo.com')
        mock_urlopen.assert_not_called()


def test_red_obtener_url_rechaza_otro_esquema():
    with patch('backend.corelibs.red.urllib.request.urlopen') as mock_urlopen:
        with pytest.raises(ValueError):
            core.obtener_url('file:///tmp/archivo.txt')
        mock_urlopen.assert_not_called()


def test_red_enviar_post_rechaza_esquema_no_http():
    with patch('backend.corelibs.red.urllib.request.urlopen') as mock_urlopen:
        with pytest.raises(ValueError):
            core.enviar_post('ftp://ejemplo.com', {'a': 1})
        mock_urlopen.assert_not_called()


def test_red_enviar_post_rechaza_otro_esquema():
    with patch('backend.corelibs.red.urllib.request.urlopen') as mock_urlopen:
        with pytest.raises(ValueError):
            core.enviar_post('file:///tmp/archivo.txt', {'a': 1})
        mock_urlopen.assert_not_called()


def test_sistema_funcs(tmp_path, monkeypatch):
    assert core.obtener_os() == os.uname().sysname
    proc = MagicMock()
    proc.stdout = 'hola\n'
    monkeypatch.setattr(core.sistema.subprocess, 'run', lambda *a, **k: proc)
    assert core.ejecutar('echo hola') == 'hola\n'
    os.environ['PRUEBA'] = '1'
    assert core.obtener_env('PRUEBA') == '1'
    d = tmp_path
    (d / 'x').write_text('')
    assert 'x' in core.listar_dir(d)


def test_transpile_texto():
    ast = [
        NodoLlamadaFuncion('mayusculas', [NodoValor("'hola'")]),
        NodoLlamadaFuncion('minusculas', [NodoValor("'HOLA'")]),
        NodoLlamadaFuncion('invertir', [NodoValor("'abc'")]),
        NodoLlamadaFuncion('concatenar', [NodoValor("'a'"), NodoValor("'b'")]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "mayusculas('hola')\n"
        + "minusculas('HOLA')\n"
        + "invertir('abc')\n"
        + "concatenar('a', 'b')\n"
    )
    js_exp = (
        IMPORTS_JS
        + "mayusculas('hola');\n"
        + "minusculas('HOLA');\n"
        + "invertir('abc');\n"
        + "concatenar('a', 'b');"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_numero():
    ast = [
        NodoLlamadaFuncion('es_par', [NodoValor(2)]),
        NodoLlamadaFuncion('es_primo', [NodoValor(3)]),
        NodoLlamadaFuncion('factorial', [NodoValor(3)]),
        NodoLlamadaFuncion('promedio', [NodoValor('[1,2]')]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "es_par(2)\n"
        + "es_primo(3)\n"
        + "factorial(3)\n"
        + "promedio([1,2])\n"
    )
    js_exp = (
        IMPORTS_JS
        + "es_par(2);\n"
        + "es_primo(3);\n"
        + "factorial(3);\n"
        + "promedio([1,2]);"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_archivo():
    ast = [
        NodoLlamadaFuncion('leer', [NodoValor("'f.txt'")]),
        NodoLlamadaFuncion('escribir', [NodoValor("'f.txt'"), NodoValor("'x'")]),
        NodoLlamadaFuncion('existe', [NodoValor("'f.txt'")]),
        NodoLlamadaFuncion('eliminar', [NodoValor("'f.txt'")]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "leer('f.txt')\n"
        + "escribir('f.txt', 'x')\n"
        + "existe('f.txt')\n"
        + "eliminar('f.txt')\n"
    )
    js_exp = (
        IMPORTS_JS
        + "leer('f.txt');\n"
        + "escribir('f.txt', 'x');\n"
        + "existe('f.txt');\n"
        + "eliminar('f.txt');"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_tiempo():
    ast = [
        NodoLlamadaFuncion('ahora', []),
        NodoLlamadaFuncion('formatear', [NodoValor('fecha'), NodoValor("'%Y'")]),
        NodoLlamadaFuncion('dormir', [NodoValor(1)]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "ahora()\n"
        + "formatear(fecha, '%Y')\n"
        + "dormir(1)\n"
    )
    js_exp = (
        IMPORTS_JS
        + "ahora();\n"
        + "formatear(fecha, '%Y');\n"
        + "dormir(1);"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_coleccion():
    ast = [
        NodoLlamadaFuncion('ordenar', [NodoValor('[3,1]')]),
        NodoLlamadaFuncion('maximo', [NodoValor('[1,2]')]),
        NodoLlamadaFuncion('minimo', [NodoValor('[1,2]')]),
        NodoLlamadaFuncion('sin_duplicados', [NodoValor('[1,1]')]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "ordenar([3,1])\n"
        + "maximo([1,2])\n"
        + "minimo([1,2])\n"
        + "sin_duplicados([1,1])\n"
    )
    js_exp = (
        IMPORTS_JS
        + "ordenar([3,1]);\n"
        + "maximo([1,2]);\n"
        + "minimo([1,2]);\n"
        + "sin_duplicados([1,1]);"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_seguridad():
    ast = [
        NodoLlamadaFuncion('hash_sha256', [NodoValor("'a'")]),
        NodoLlamadaFuncion('generar_uuid', []),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "hash_sha256('a')\n"
        + "generar_uuid()\n"
    )
    js_exp = (
        IMPORTS_JS
        + "hash_sha256('a');\n"
        + "generar_uuid();"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_red():
    ast = [
        NodoLlamadaFuncion('obtener_url', [NodoValor("'http://x'")]),
        NodoLlamadaFuncion('enviar_post', [NodoValor("'http://x'"), NodoValor('{"a":1}')]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "obtener_url('http://x')\n"
        + "enviar_post('http://x', {\"a\":1})\n"
    )
    js_exp = (
        IMPORTS_JS
        + "obtener_url('http://x');\n"
        + "enviar_post('http://x', {\"a\":1});"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_sistema():
    ast = [
        NodoLlamadaFuncion('obtener_os', []),
        NodoLlamadaFuncion('ejecutar', [NodoValor("'ls'")]),
        NodoLlamadaFuncion('obtener_env', [NodoValor("'PATH'")]),
        NodoLlamadaFuncion('listar_dir', [NodoValor("'.'")]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "obtener_os()\n"
        + "ejecutar('ls')\n"
        + "obtener_env('PATH')\n"
        + "listar_dir('.')\n"
    )
    js_exp = (
        IMPORTS_JS
        + "obtener_os();\n"
        + "ejecutar('ls');\n"
        + "obtener_env('PATH');\n"
        + "listar_dir('.');"
    )
    assert py == py_exp
    assert js == js_exp
