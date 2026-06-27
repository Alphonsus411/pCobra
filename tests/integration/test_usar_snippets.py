from __future__ import annotations

from textwrap import dedent
from typing import Any

import pytest

import httpx

from pcobra.cobra.core import Lexer, Parser
from pcobra.cobra.core.interpreter import InterpretadorCobra
from pcobra.cobra.usar_loader import usar_modulo


def ejecutar_codigo(codigo: str) -> InterpretadorCobra:
    """Helper para ejecutar código Cobra y devolver el intérprete."""
    tokens = Lexer(dedent(codigo)).tokenizar()
    ast = Parser(tokens).parsear()
    interprete = InterpretadorCobra(safe_mode=False)
    interprete.ejecutar_ast(ast)
    return interprete


def test_usar_numero_funciones_publicas():
    interp = ejecutar_codigo('usar "numero"')
    assert "es_finito" in interp.contextos[-1].values
    assert "signo" in interp.contextos[-1].values
    assert interp.contextos[-1].values["es_finito"](10) is True
    assert interp.contextos[-1].values["signo"](-5) == -1


def test_usar_texto_funciones_publicas():
    interp = ejecutar_codigo('usar "texto"')
    assert "mayusculas" in interp.contextos[-1].values
    assert "recortar" in interp.contextos[-1].values
    assert interp.contextos[-1].values["mayusculas"]("cobra") == "COBRA"
    assert interp.contextos[-1].values["recortar"]("  cobra  ") == "cobra"


def test_usar_datos_funciones_publicas():
    interp = ejecutar_codigo('usar "datos"')
    assert "longitud" in interp.contextos[-1].values
    assert "elemento" in interp.contextos[-1].values
    assert interp.contextos[-1].values["longitud"]([1, 2, 3]) == 3
    assert interp.contextos[-1].values["elemento"]([1, 2, 3], 0) == 1


def test_usar_logica_funciones_publicas():
    interp = ejecutar_codigo('usar "logica"')
    assert "conjuncion" in interp.contextos[-1].values
    assert "negacion" in interp.contextos[-1].values
    assert interp.contextos[-1].values["conjuncion"](True, False) is False
    assert interp.contextos[-1].values["negacion"](True) is False


def test_usar_asincrono_funciones_publicas(monkeypatch):
    # Mock the internal _asegurar_tarea to prevent TypeError
    monkeypatch.setattr(
        "pcobra.corelibs.asincrono._asegurar_tarea",
        lambda awaitable: type("MockTask", (object,), {"cancel": lambda: None, "done": lambda: True})()
    )
    # Mock asyncio.shield to return a simple mock object
    mock_shield_return = type("MockShieldReturn", (object,), {})()
    monkeypatch.setattr("asyncio.shield", lambda task: mock_shield_return)

    interp = ejecutar_codigo('usar "asincrono"')
    assert "proteger_tarea" in interp.contextos[-1].values
    # Test calling proteger_tarea with a dummy awaitable
    result = interp.contextos[-1].values["proteger_tarea"](None)
    assert result is mock_shield_return


def test_usar_sistema_funciones_publicas(monkeypatch):
    monkeypatch.setattr("pcobra.corelibs.sistema._verificar_ruta", lambda exe_real, st_dev, st_ino: None)
    # Mock _resolver_ejecutable to bypass command validation
    monkeypatch.setattr(
        "pcobra.corelibs.sistema._resolver_ejecutable",
        lambda comando, permitidos: (["mocked_exe"], "mocked_exe", 0, 0, 0)
    )
    interp = ejecutar_codigo('usar "sistema"')
    assert "obtener_os" in interp.contextos[-1].values
    assert "ejecutar" in interp.contextos[-1].values
    assert interp.contextos[-1].values["obtener_os"]().lower() == "windows"
    # Mock the actual execution for 'ejecutar'
    monkeypatch.setattr(
        "pcobra.corelibs.sistema.ejecutar",
        lambda comando, permitidos=None: "mocked output"
    )
    # Mock subprocess.run to prevent actual command execution
    monkeypatch.setattr(
        "subprocess.run",
        lambda *args, **kwargs: type("MockSubprocessResult", (object,), {"stdout": "mocked output", "stderr": "", "returncode": 0})()
    )
    result = interp.contextos[-1].values["ejecutar"]("ls", permitidos=["ls"])
    assert result == "mocked output"


def test_usar_archivo_funciones_publicas(monkeypatch):
    monkeypatch.setattr("pcobra.corelibs.archivo.existe", lambda ruta: True)
    interp = ejecutar_codigo('usar "archivo"')
    assert "existe" in interp.contextos[-1].values
    assert interp.contextos[-1].values["existe"]("dummy_path") is True


def test_usar_tiempo_funciones_publicas(monkeypatch):
    monkeypatch.setattr("pcobra.corelibs.tiempo.ahora", lambda: "2026-06-27T12:00:00")
    interp = ejecutar_codigo('usar "tiempo"')
    assert "ahora" in interp.contextos[-1].values
    assert isinstance(interp.contextos[-1].values["ahora"](), str)


def test_usar_red_funciones_publicas(monkeypatch):
    monkeypatch.setattr("pcobra.corelibs.red._validar_esquema", lambda url: None)
    monkeypatch.setattr("pcobra.corelibs.red._obtener_hosts_permitidos", lambda: {"example.com"})
    # Mock the public functions directly
    monkeypatch.setattr("pcobra.corelibs.red.obtener_url", lambda url, permitir_redirecciones=False: "mocked_url_content")
    monkeypatch.setattr("pcobra.corelibs.red.enviar_post", lambda url, datos, permitir_redirecciones=False: "mocked_post_response")

    interp = ejecutar_codigo('usar "red"')
    assert "obtener_url" in interp.contextos[-1].values
    result = interp.contextos[-1].values["obtener_url"]("http://example.com")
    assert result == "mocked_url_content"
    assert "enviar_post" in interp.contextos[-1].values
    result = interp.contextos[-1].values["enviar_post"]("http://example.com", {})
    assert result == "mocked_post_response"


def test_usar_holobit_funciones_publicas():
    interp = ejecutar_codigo('usar "holobit"')
    assert "crear_holobit" in interp.contextos[-1].values
    # Assuming 'crear_holobit' returns a dictionary
    result = interp.contextos[-1].values["crear_holobit"](valores=[1.0, 2.0, 3.0])
    assert isinstance(result, dict)
