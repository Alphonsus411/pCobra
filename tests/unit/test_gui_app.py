"""Pruebas para funciones de la aplicación GUI basadas en Flet."""

import importlib
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def app_module(monkeypatch):
    """Importa el módulo de la app con Flet y transpiladores simulados."""
    monkeypatch.setitem(sys.modules, "flet", MagicMock())

    class DummyTranspiler:
        def generate_code(self, ast):
            return "codigo"

    dummy_compile = SimpleNamespace(TRANSPILERS={"python": DummyTranspiler})
    monkeypatch.setitem(sys.modules, "cobra.cli.commands.compile_cmd", dummy_compile)
    monkeypatch.setitem(sys.modules, "pcobra.cobra.cli.commands.compile_cmd", dummy_compile)

    module = importlib.import_module("gui.app")
    importlib.reload(module)
    return module


def test_ejecutar_codigo_captura_salida(app_module):
    codigo = "imprimir('Hola, mundo!')"
    salida = app_module._ejecutar_codigo(codigo)
    assert salida == "Hola, mundo!\n"


def test_transpilar_codigo_no_vacio(app_module):
    codigo = "imprimir('Hola, mundo!')"
    generado = app_module._transpilar_codigo(codigo, "python")
    assert generado.strip() != ""


def test_ejecutar_codigo_restaura_stdout_stderr_tras_excepcion(app_module, monkeypatch):
    class DummyInterpreter:
        def ejecutar_ast(self, ast):
            print("salida parcial")
            print("error parcial", file=sys.stderr)
            raise RuntimeError("fallo forzado")

    monkeypatch.setattr(app_module, "InterpretadorCobra", DummyInterpreter)

    stdout_original = sys.stdout
    stderr_original = sys.stderr

    with pytest.raises(RuntimeError, match="fallo forzado"):
        app_module._ejecutar_codigo("imprimir('x')")

    assert sys.stdout is stdout_original
    assert sys.stderr is stderr_original
