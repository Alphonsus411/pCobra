import os
import sys
from datetime import datetime
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

sys.modules.setdefault("yaml", ModuleType("yaml"))

import backend.corelibs as core
from cobra.transpilers.import_helper import get_standard_imports
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from core.ast_nodes import NodoLlamadaFuncion, NodoValor

IMPORTS_PY = get_standard_imports("python")
IMPORTS_JS = "".join(f"{line}\n" for line in get_standard_imports("js"))


def test_texto_funcs():
    assert core.mayusculas("hola") == "HOLA"
    assert core.minusculas("HOLA") == "hola"
    assert core.invertir("abc") == "cba"
    assert core.concatenar("a", "b") == "ab"


def test_numero_funcs():
    assert core.es_par(4) is True
    assert core.es_par(5) is False
    assert core.es_primo(7) is True
    assert core.es_primo(4) is False
    assert core.factorial(5) == 120
    assert core.promedio([1, 2, 3]) == 2.0


def test_archivo_funcs(tmp_path):
    ruta = tmp_path / "f.txt"
    core.escribir(ruta, "data")
    assert core.existe(ruta)
    assert core.leer(ruta) == "data"
    core.eliminar(ruta)
    assert not core.existe(ruta)


def test_tiempo_funcs(monkeypatch):
    ahora = core.ahora()
    assert isinstance(ahora, datetime)
    fecha = datetime(2020, 1, 2, 3, 4, 5)
    assert core.formatear(fecha, "%Y") == "2020"
    called = {}

    def fake_sleep(seg):
        called["v"] = seg

    monkeypatch.setattr(core.tiempo.time, "sleep", fake_sleep)
    core.dormir(0.01)
    assert called["v"] == 0.01


def test_coleccion_funcs():
    datos = [3, 1, 2, 1]
    assert core.ordenar(datos) == [1, 1, 2, 3]
    assert core.maximo(datos) == 3
    assert core.minimo(datos) == 1
    assert core.sin_duplicados(datos) == [3, 1, 2]


def test_seguridad_funcs():
    assert (
        core.hash_sha256("a")
        == "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb"
    )
    uuid = core.generar_uuid()
    assert isinstance(uuid, str) and len(uuid) == 36


def test_red_funcs(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "x")
    mock_resp_get = MagicMock(url="https://x", encoding="utf-8")
    mock_resp_get.iter_content.return_value = [b"ok"]
    mock_resp_get.raise_for_status.return_value = None
    mock_resp_post = MagicMock(url="https://x", encoding="utf-8")
    mock_resp_post.iter_content.return_value = [b"ok"]
    mock_resp_post.raise_for_status.return_value = None
    with patch(
        "backend.corelibs.red.requests.get", return_value=mock_resp_get
    ) as mock_get, patch(
        "backend.corelibs.red.requests.post", return_value=mock_resp_post
    ) as mock_post:
        assert core.obtener_url("https://x") == "ok"
        assert core.enviar_post("https://x", {"a": 1}) == "ok"
        mock_get.assert_called_once_with(
            "https://x", timeout=5, allow_redirects=False, stream=True
        )
        mock_post.assert_called_once_with(
            "https://x", data={"a": 1}, timeout=5, allow_redirects=False, stream=True
        )


def test_red_obtener_url_rechaza_esquema_no_http(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch("backend.corelibs.red.requests.get") as mock_get:
        with pytest.raises(ValueError):
            core.obtener_url("ftp://ejemplo.com")
        mock_get.assert_not_called()


def test_red_obtener_url_rechaza_otro_esquema(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch("backend.corelibs.red.requests.get") as mock_get:
        with pytest.raises(ValueError):
            core.obtener_url("file:///tmp/archivo.txt")
        mock_get.assert_not_called()


def test_red_enviar_post_rechaza_esquema_no_http(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch("backend.corelibs.red.requests.post") as mock_post:
        with pytest.raises(ValueError):
            core.enviar_post("ftp://ejemplo.com", {"a": 1})
        mock_post.assert_not_called()


def test_red_enviar_post_rechaza_otro_esquema(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch("backend.corelibs.red.requests.post") as mock_post:
        with pytest.raises(ValueError):
            core.enviar_post("file:///tmp/archivo.txt", {"a": 1})
        mock_post.assert_not_called()


def test_red_host_whitelist_permite(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    mock_resp = MagicMock(url="https://example.com", encoding="utf-8")
    mock_resp.iter_content.return_value = [b"ok"]
    mock_resp.raise_for_status.return_value = None
    with patch("backend.corelibs.red.requests.get", return_value=mock_resp) as mock_get:
        assert core.obtener_url("https://example.com") == "ok"
        mock_get.assert_called_once_with(
            "https://example.com", timeout=5, allow_redirects=False, stream=True
        )


def test_red_host_whitelist_rechaza(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    with patch("backend.corelibs.red.requests.get") as mock_get:
        with pytest.raises(ValueError):
            core.obtener_url("https://otro.com")
        mock_get.assert_not_called()


def test_red_obtener_url_redireccion_fuera_whitelist(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    mock_resp = MagicMock(text="ok", url="https://otro.com")
    mock_resp.raise_for_status.return_value = None
    with patch("backend.corelibs.red.requests.get", return_value=mock_resp):
        with pytest.raises(ValueError):
            core.obtener_url("https://example.com", permitir_redirecciones=True)


def test_red_enviar_post_redireccion_fuera_whitelist(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    mock_resp = MagicMock(text="ok", url="https://otro.com")
    mock_resp.raise_for_status.return_value = None
    with patch("backend.corelibs.red.requests.post", return_value=mock_resp):
        with pytest.raises(ValueError):
            core.enviar_post(
                "https://example.com", {"a": 1}, permitir_redirecciones=True
            )


def test_red_obtener_url_respuesta_muy_grande(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    grande = MagicMock(url="https://example.com", encoding="utf-8")
    grande.iter_content.return_value = [b"a" * (1024 * 1024 + 1)]
    grande.raise_for_status.return_value = None
    with patch("backend.corelibs.red.requests.get", return_value=grande):
        with pytest.raises(ValueError):
            core.obtener_url("https://example.com")
    grande.close.assert_called_once()


def test_red_enviar_post_respuesta_muy_grande(monkeypatch):
    monkeypatch.setenv("COBRA_HOST_WHITELIST", "example.com")
    grande = MagicMock(url="https://example.com", encoding="utf-8")
    grande.iter_content.return_value = [b"a" * (1024 * 1024 + 1)]
    grande.raise_for_status.return_value = None
    with patch("backend.corelibs.red.requests.post", return_value=grande):
        with pytest.raises(ValueError):
            core.enviar_post("https://example.com", {"a": 1})
    grande.close.assert_called_once()


def test_sistema_funcs(tmp_path, monkeypatch):
    assert core.obtener_os() == os.uname().sysname
    proc = MagicMock()
    proc.stdout = "hola\n"

    def fake_run(*a, **k):
        assert k["timeout"] == 1
        return proc

    monkeypatch.setattr(core.sistema.subprocess, "run", fake_run)
    permitido = core.sistema.os.path.realpath("/usr/bin/echo")
    assert (
        core.ejecutar(["echo", "hola"], permitidos=[permitido], timeout=1)
        == "hola\n"
    )
    os.environ["PRUEBA"] = "1"
    assert core.obtener_env("PRUEBA") == "1"
    d = tmp_path
    (d / "x").write_text("")
    assert "x" in core.listar_dir(d)


def test_transpile_texto():
    ast = [
        NodoLlamadaFuncion("mayusculas", [NodoValor("'hola'")]),
        NodoLlamadaFuncion("minusculas", [NodoValor("'HOLA'")]),
        NodoLlamadaFuncion("invertir", [NodoValor("'abc'")]),
        NodoLlamadaFuncion("concatenar", [NodoValor("'a'"), NodoValor("'b'")]),
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
        NodoLlamadaFuncion("es_par", [NodoValor(2)]),
        NodoLlamadaFuncion("es_primo", [NodoValor(3)]),
        NodoLlamadaFuncion("factorial", [NodoValor(3)]),
        NodoLlamadaFuncion("promedio", [NodoValor("[1,2]")]),
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
        NodoLlamadaFuncion("leer", [NodoValor("'f.txt'")]),
        NodoLlamadaFuncion("escribir", [NodoValor("'f.txt'"), NodoValor("'x'")]),
        NodoLlamadaFuncion("existe", [NodoValor("'f.txt'")]),
        NodoLlamadaFuncion("eliminar", [NodoValor("'f.txt'")]),
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
        NodoLlamadaFuncion("ahora", []),
        NodoLlamadaFuncion("formatear", [NodoValor("fecha"), NodoValor("'%Y'")]),
        NodoLlamadaFuncion("dormir", [NodoValor(1)]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = IMPORTS_PY + "ahora()\n" + "formatear(fecha, '%Y')\n" + "dormir(1)\n"
    js_exp = IMPORTS_JS + "ahora();\n" + "formatear(fecha, '%Y');\n" + "dormir(1);"
    assert py == py_exp
    assert js == js_exp


def test_transpile_coleccion():
    ast = [
        NodoLlamadaFuncion("ordenar", [NodoValor("[3,1]")]),
        NodoLlamadaFuncion("maximo", [NodoValor("[1,2]")]),
        NodoLlamadaFuncion("minimo", [NodoValor("[1,2]")]),
        NodoLlamadaFuncion("sin_duplicados", [NodoValor("[1,1]")]),
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
        NodoLlamadaFuncion("hash_sha256", [NodoValor("'a'")]),
        NodoLlamadaFuncion("generar_uuid", []),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = IMPORTS_PY + "hash_sha256('a')\n" + "generar_uuid()\n"
    js_exp = IMPORTS_JS + "hash_sha256('a');\n" + "generar_uuid();"
    assert py == py_exp
    assert js == js_exp


def test_transpile_red():
    ast = [
        NodoLlamadaFuncion("obtener_url", [NodoValor("'https://x'")]),
        NodoLlamadaFuncion(
            "enviar_post", [NodoValor("'https://x'"), NodoValor('{"a":1}')]
        ),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "obtener_url('https://x')\n"
        + "enviar_post('https://x', {\"a\":1})\n"
    )
    js_exp = (
        IMPORTS_JS
        + "obtener_url('https://x');\n"
        + "enviar_post('https://x', {\"a\":1});"
    )
    assert py == py_exp
    assert js == js_exp


def test_transpile_sistema():
    ast = [
        NodoLlamadaFuncion("obtener_os", []),
        NodoLlamadaFuncion("ejecutar", [NodoValor("['ls']")]),
        NodoLlamadaFuncion("obtener_env", [NodoValor("'PATH'")]),
        NodoLlamadaFuncion("listar_dir", [NodoValor("'.'")]),
    ]
    py = TranspiladorPython().generate_code(ast)
    js = TranspiladorJavaScript().generate_code(ast)
    py_exp = (
        IMPORTS_PY
        + "obtener_os()\n"
        + "ejecutar(['ls'])\n"
        + "obtener_env('PATH')\n"
        + "listar_dir('.')\n"
    )
    js_exp = (
        IMPORTS_JS
        + "obtener_os();\n"
        + "ejecutar(['ls']);\n"
        + "obtener_env('PATH');\n"
        + "listar_dir('.');"
    )
    assert py == py_exp
    assert js == js_exp
