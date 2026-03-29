"""Smoke tests para el entrypoint GUI ``pcobra.gui.app``."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from pcobra.gui import app


def _fake_flet():
    class TextField:
        def __init__(self, **_kwargs):
            self.value = ""

    class Text:
        def __init__(self, value="", **_kwargs):
            self.value = value

    class Dropdown:
        def __init__(self, options=None, **_kwargs):
            self.options = options or []
            self.value = None

    class Switch:
        def __init__(self, **_kwargs):
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


def test_main_renderiza_componentes_minimos(monkeypatch):
    ft = _fake_flet()
    monkeypatch.setattr(app.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(app.runtime, "gui_target_choices", lambda: ("python",))
    monkeypatch.setattr(
        app.runtime,
        "require_gui_dependencies",
        lambda: {
            "TRANSPILERS": {"python": object},
            "LexerError": RuntimeError,
            "ParserError": ValueError,
        },
    )
    monkeypatch.setattr(app.runtime, "normalizar_codigo", lambda value: value or "")
    monkeypatch.setattr(app.runtime, "ejecutar_codigo", lambda _codigo: "ok")
    monkeypatch.setattr(app.runtime, "transpilar_codigo", lambda _codigo, _lang: "transpilado")
    monkeypatch.setattr(app.runtime, "formatear_error", lambda exc, **_kwargs: f"error: {exc}")

    page = ft.Page()
    app.main(page)

    botones = [c for c in page.controls if isinstance(c, ft.ElevatedButton)]
    assert [b.text for b in botones] == ["Ejecutar"]


def test_main_handler_actualiza_salida(monkeypatch):
    ft = _fake_flet()
    monkeypatch.setattr(app.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(app.runtime, "gui_target_choices", lambda: ("python",))
    monkeypatch.setattr(
        app.runtime,
        "require_gui_dependencies",
        lambda: {
            "TRANSPILERS": {"python": object},
            "LexerError": RuntimeError,
            "ParserError": ValueError,
        },
    )
    monkeypatch.setattr(app.runtime, "normalizar_codigo", lambda value: value or "")
    monkeypatch.setattr(app.runtime, "ejecutar_codigo", lambda _codigo: "ejecutado")
    monkeypatch.setattr(app.runtime, "transpilar_codigo", lambda _codigo, _lang: "transpilado")
    monkeypatch.setattr(app.runtime, "formatear_error", lambda exc, **_kwargs: f"error: {exc}")

    page = ft.Page()
    app.main(page)

    entrada = next(c for c in page.controls if isinstance(c, ft.TextField))
    selector = next(c for c in page.controls if isinstance(c, ft.Dropdown))
    activar = next(c for c in page.controls if isinstance(c, ft.Switch))
    salida = next(c for c in page.controls if isinstance(c, ft.Text))
    ejecutar_btn = next(
        c for c in page.controls if isinstance(c, ft.ElevatedButton) and c.text == "Ejecutar"
    )

    entrada.value = "imprimir('x')"
    ejecutar_btn.on_click(None)
    assert salida.value == "ejecutado"

    activar.value = True
    selector.value = "python"
    ejecutar_btn.on_click(None)
    assert salida.value == "transpilado"
    assert page.update.call_count == 2
