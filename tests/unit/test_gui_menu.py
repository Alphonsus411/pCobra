import importlib
from types import SimpleNamespace
from unittest.mock import MagicMock


class FakeTextField:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.value = ""


class FakeText:
    def __init__(self, value="", **kwargs):
        self.kwargs = kwargs
        self.value = value


class FakeDropdown:
    def __init__(self, options=None, **kwargs):
        self.kwargs = kwargs
        self.options = options or []
        self.value = None


class FakeSwitch:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.value = False


class FakeElevatedButton:
    def __init__(self, text, on_click=None):
        self.text = text
        self.on_click = on_click


class FakePage:
    def __init__(self):
        self.controls = []
        self.updated = 0

    def add(self, *args):
        self.controls.extend(args)

    def update(self):
        self.updated += 1


def _fake_flet(*, root_option=None, dropdown_option=None, app=None):
    attrs = {
        "TextField": FakeTextField,
        "Text": FakeText,
        "Dropdown": FakeDropdown,
        "Switch": FakeSwitch,
        "ElevatedButton": FakeElevatedButton,
        "Page": FakePage,
        "dropdown": SimpleNamespace(Option=dropdown_option or (lambda value: f"dropdown:{value}")),
        "app": app or (lambda **kwargs: kwargs),
    }
    if root_option is not None:
        attrs["Option"] = root_option
    return SimpleNamespace(**attrs)


def _prepare_module(monkeypatch, module_name):
    fake_ft = _fake_flet()
    module = importlib.import_module(module_name)
    importlib.reload(module)
    monkeypatch.setattr(module.runtime, "require_flet", lambda: fake_ft)
    monkeypatch.setattr(module.runtime, "gui_target_choices", lambda: ("py",))
    monkeypatch.setattr(
        module.runtime,
        "require_gui_dependencies",
        lambda: {"TRANSPILERS": {"py": object()}, "LexerError": None, "ParserError": None},
    )
    return module, fake_ft


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
    module, ft = _prepare_module(monkeypatch, "pcobra.gui.app")
    transpilar = MagicMock(return_value="codigo python")
    monkeypatch.setattr(module.runtime, "transpilar_codigo", transpilar)

    page = ft.Page()
    module.main(page)
    _run_handler(ft, page, "print(1)")

    transpilar.assert_called_once_with("print(1)", "py")
    assert next(c for c in page.controls if isinstance(c, ft.Text)).value == "codigo python"
    assert page.updated == 1


def test_idle_transpiler_invocado(monkeypatch):
    module, ft = _prepare_module(monkeypatch, "pcobra.gui.idle")
    transpilar = MagicMock(return_value="codigo python")
    monkeypatch.setattr(module.runtime, "transpilar_codigo", transpilar)

    page = ft.Page()
    module.main(page)
    _run_handler(ft, page, "print(1)")

    transpilar.assert_called_once_with("print(1)", "py")
    assert next(c for c in page.controls if isinstance(c, ft.Text)).value == "codigo python"
    assert page.updated == 1


def test_dropdown_option_prefiere_api_raiz_si_existe():
    from pcobra.gui import runtime

    ft = _fake_flet(root_option=lambda value: f"root:{value}")

    assert runtime.flet_dropdown_option(ft, "py") == "root:py"


def test_dropdown_option_usa_dropdown_option_en_flet_0852():
    from pcobra.gui import runtime

    ft = _fake_flet(dropdown_option=lambda value: f"dropdown:{value}")

    assert runtime.flet_dropdown_option(ft, "py") == "dropdown:py"


def test_flet_app_centraliza_lanzamiento():
    from pcobra.gui import runtime

    app = MagicMock(return_value="ok")
    target = object()
    ft = _fake_flet(app=app)

    assert runtime.flet_app(target, ft=ft, view="web_browser") == "ok"
    app.assert_called_once_with(target=target, view="web_browser")
