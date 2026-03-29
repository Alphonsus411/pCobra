"""Smoke tests para el entrypoint GUI ``pcobra.gui.idle``."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from pcobra.gui import idle


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


def test_main_renderiza_botones_esperados(monkeypatch):
    ft = _fake_flet()
    monkeypatch.setattr(idle.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(idle.runtime, "gui_target_choices", lambda: ("python",))
    monkeypatch.setattr(
        idle.runtime,
        "require_gui_dependencies",
        lambda: {
            "TRANSPILERS": {"python": object},
            "LexerError": RuntimeError,
            "ParserError": ValueError,
        },
    )
    monkeypatch.setattr(idle.runtime, "normalizar_codigo", lambda value: value or "")
    monkeypatch.setattr(idle.runtime, "ejecutar_codigo", lambda _codigo: "ok")
    monkeypatch.setattr(idle.runtime, "transpilar_codigo", lambda _codigo, _lang: "transpilado")
    monkeypatch.setattr(idle.runtime, "mostrar_tokens", lambda _codigo: "Token(X)")
    monkeypatch.setattr(idle.runtime, "mostrar_ast", lambda _codigo: "[Nodo]")
    monkeypatch.setattr(idle.runtime, "formatear_error", lambda exc, **_kwargs: f"error: {exc}")

    page = ft.Page()
    idle.main(page)

    botones = [c for c in page.controls if isinstance(c, ft.ElevatedButton)]
    assert [b.text for b in botones] == ["Ejecutar", "Tokens", "AST"]


def test_main_handlers_smoke(monkeypatch):
    ft = _fake_flet()
    monkeypatch.setattr(idle.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(idle.runtime, "gui_target_choices", lambda: ("python",))
    monkeypatch.setattr(
        idle.runtime,
        "require_gui_dependencies",
        lambda: {
            "TRANSPILERS": {"python": object},
            "LexerError": RuntimeError,
            "ParserError": ValueError,
        },
    )
    monkeypatch.setattr(idle.runtime, "normalizar_codigo", lambda value: value or "")
    monkeypatch.setattr(idle.runtime, "ejecutar_codigo", lambda _codigo: "ejecutado")
    monkeypatch.setattr(idle.runtime, "transpilar_codigo", lambda _codigo, _lang: "transpilado")
    monkeypatch.setattr(idle.runtime, "mostrar_tokens", lambda _codigo: "Token(X)")
    monkeypatch.setattr(idle.runtime, "mostrar_ast", lambda _codigo: "[Nodo]")
    monkeypatch.setattr(idle.runtime, "formatear_error", lambda exc, **_kwargs: f"error: {exc}")

    page = ft.Page()
    idle.main(page)

    entrada = next(c for c in page.controls if isinstance(c, ft.TextField))
    selector = next(c for c in page.controls if isinstance(c, ft.Dropdown))
    activar = next(c for c in page.controls if isinstance(c, ft.Switch))
    salida = next(c for c in page.controls if isinstance(c, ft.Text))
    botones = [c for c in page.controls if isinstance(c, ft.ElevatedButton)]
    ejecutar_btn, tokens_btn, ast_btn = botones

    entrada.value = "imprimir('x')"
    ejecutar_btn.on_click(None)
    assert salida.value == "ejecutado"

    activar.value = True
    selector.value = "python"
    ejecutar_btn.on_click(None)
    assert salida.value == "transpilado"

    tokens_btn.on_click(None)
    assert salida.value == "Token(X)"

    ast_btn.on_click(None)
    assert salida.value == "[Nodo]"
    assert page.update.call_count == 4
