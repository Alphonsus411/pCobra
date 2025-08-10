"""Pruebas unitarias para la funcionalidad de ``gui.idle``."""

import importlib
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


def _fake_flet():
    class TextField:
        def __init__(self, **kwargs):
            self.value = ""

    class Text:
        def __init__(self, value="", **kwargs):
            self.value = value

    class Dropdown:
        def __init__(self, options=None, **kwargs):
            self.options = options or []
            self.value = None

    class Switch:
        def __init__(self, **kwargs):
            self.value = False

    class ElevatedButton:
        def __init__(self, text, on_click=None):
            self.text = text
            self.on_click = on_click

    class Page:
        def __init__(self):
            self.controls = []
            self.update = MagicMock()

        def add(self, *args):
            self.controls.extend(args)

    return SimpleNamespace(
        TextField=TextField,
        Text=Text,
        Dropdown=Dropdown,
        Switch=Switch,
        ElevatedButton=ElevatedButton,
        Page=Page,
        dropdown=SimpleNamespace(Option=lambda v: v),
    )


@pytest.fixture
def idle_module(monkeypatch):
    """Importa ``gui.idle`` con dependencias simuladas."""

    fake_ft = _fake_flet()

    transpiler_inst = MagicMock()
    transpiler_inst.generate_code.return_value = "codigo"
    transpiler_cls = MagicMock(return_value=transpiler_inst)
    dummy_compile = SimpleNamespace(TRANSPILERS={"py": transpiler_cls})

    class DummyInterpreter:
        def ejecutar_ast(self, ast):
            pass

    monkeypatch.setitem(sys.modules, "flet", fake_ft)
    monkeypatch.setitem(sys.modules, "cobra.cli.commands.compile_cmd", dummy_compile)
    monkeypatch.setitem(
        sys.modules, "core.interpreter", SimpleNamespace(InterpretadorCobra=DummyInterpreter)
    )

    module = importlib.import_module("gui.idle")
    importlib.reload(module)
    return module, fake_ft, transpiler_cls, transpiler_inst


def test_mostrar_tokens_formato(idle_module):
    module, *_ = idle_module
    codigo = "imprimir('x')"
    salida = module._mostrar_tokens(codigo)
    lineas = salida.splitlines()
    assert lineas[0].startswith("Token(")
    assert "IMPRIMIR" in lineas[0]
    assert lineas[-1].startswith("Token(") and "EOF" in lineas[-1]


def test_mostrar_ast_formato(idle_module):
    module, *_ = idle_module
    codigo = "imprimir('x')"
    salida = module._mostrar_ast(codigo)
    assert salida.startswith("[")
    assert "NodoImprimir" in salida
    assert "NodoValor" in salida


def test_transpilar_codigo_invoca_transpiler(idle_module):
    module, _, transpiler_cls, transpiler_inst = idle_module
    codigo = "imprimir('x')"
    generado = module._transpilar_codigo(codigo, "py")
    transpiler_cls.assert_called_once_with()
    transpiler_inst.generate_code.assert_called_once()
    assert generado == "codigo"


def test_event_handlers_actualizan_salida(idle_module):
    module, ft, _, _ = idle_module
    page = ft.Page()
    module.main(page)

    entrada = next(c for c in page.controls if isinstance(c, ft.TextField))
    selector = next(c for c in page.controls if isinstance(c, ft.Dropdown))
    switch = next(c for c in page.controls if isinstance(c, ft.Switch))
    salida = next(c for c in page.controls if isinstance(c, ft.Text))
    ejecutar_btn = next(
        c
        for c in page.controls
        if isinstance(c, ft.ElevatedButton) and c.text == "Ejecutar"
    )
    tokens_btn = next(
        c
        for c in page.controls
        if isinstance(c, ft.ElevatedButton) and c.text == "Tokens"
    )
    ast_btn = next(
        c for c in page.controls if isinstance(c, ft.ElevatedButton) and c.text == "AST"
    )

    entrada.value = "imprimir('x')"
    selector.value = "py"
    switch.value = True
    ejecutar_btn.on_click(None)
    assert salida.value == "codigo"
    page.update.assert_called_once()
    page.update.reset_mock()

    entrada.value = "imprimir('t')"
    tokens_btn.on_click(None)
    assert "Token(" in salida.value
    page.update.assert_called_once()
    page.update.reset_mock()

    entrada.value = "imprimir('a')"
    ast_btn.on_click(None)
    assert "NodoImprimir" in salida.value
    page.update.assert_called_once()

