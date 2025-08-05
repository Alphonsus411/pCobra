import importlib
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock


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

        def add(self, *args):
            self.controls.extend(args)

        def update(self):
            pass

    return SimpleNamespace(
        TextField=TextField,
        Text=Text,
        Dropdown=Dropdown,
        Switch=Switch,
        ElevatedButton=ElevatedButton,
        Page=Page,
        dropdown=SimpleNamespace(Option=lambda v: v),
    )


def _prepare_module(monkeypatch, module_name):
    fake_ft = _fake_flet()
    dummy_compile = SimpleNamespace(TRANSPILERS={"py": object()})
    monkeypatch.setitem(sys.modules, "flet", fake_ft)
    monkeypatch.setitem(sys.modules, "cobra.cli.commands.compile_cmd", dummy_compile)
    module = importlib.import_module(module_name)
    importlib.reload(module)
    return module, fake_ft


def _prepare_transpiler(monkeypatch, module):
    inst = MagicMock()
    cls = MagicMock(return_value=inst)
    monkeypatch.setattr(module, "TRANSPILERS", {"py": cls})
    lexer_inst = MagicMock()
    parser_inst = MagicMock()
    lexer_inst.tokenizar.return_value = "TOK"
    parser_inst.parsear.return_value = "AST"
    monkeypatch.setattr(module, "Lexer", MagicMock(return_value=lexer_inst))
    monkeypatch.setattr(module, "Parser", MagicMock(return_value=parser_inst))
    return cls, inst


def _run_handler(ft, page, text):
    entrada = next(c for c in page.controls if isinstance(c, ft.TextField))
    selector = next(c for c in page.controls if isinstance(c, ft.Dropdown))
    switch = next(c for c in page.controls if isinstance(c, ft.Switch))
    boton = next(
        c
        for c in page.controls
        if isinstance(c, ft.ElevatedButton) and c.text == "Ejecutar"
    )
    entrada.value = text
    selector.value = "py"
    switch.value = True
    boton.on_click(None)


def test_app_transpiler_invocado(monkeypatch):
    module, ft = _prepare_module(monkeypatch, "gui.app")
    _, inst = _prepare_transpiler(monkeypatch, module)
    page = ft.Page()
    module.main(page)
    _run_handler(ft, page, "print(1)")
    inst.generate_code.assert_called_once_with("AST")


def test_idle_transpiler_invocado(monkeypatch):
    module, ft = _prepare_module(monkeypatch, "gui.idle")
    _, inst = _prepare_transpiler(monkeypatch, module)
    page = ft.Page()
    module.main(page)
    _run_handler(ft, page, "print(1)")
    inst.generate_code.assert_called_once_with("AST")
