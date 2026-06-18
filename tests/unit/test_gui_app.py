"""Smoke tests para el entrypoint GUI ``pcobra.gui.app``."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from pcobra.gui import app


def _fake_flet():
    class TextField:
        def __init__(self, **_kwargs):
            self.kwargs = _kwargs
            self.value = _kwargs.get("value", "")

    class Text:
        def __init__(self, value="", **_kwargs):
            self.kwargs = _kwargs
            self.value = value

    class Dropdown:
        def __init__(self, options=None, **_kwargs):
            self.options = options or []
            self.value = None

    class Switch:
        def __init__(self, **kwargs):
            self.value = False
            self.disabled = kwargs.get("disabled", False)

    class ElevatedButton:
        def __init__(self, text, on_click=None):
            self.text = text
            self.on_click = on_click

    class TextButton(ElevatedButton):
        pass

    class Layout:
        def __init__(self, controls=None, *args, **_kwargs):
            if controls is None and args:
                controls = args[0]
            self.controls = controls or []

    class Container:
        def __init__(self, content=None, **_kwargs):
            self.content = content

    class ExpansionTile:
        def __init__(self, title=None, leading=None, controls=None):
            self.title = title
            self.leading = leading
            self.controls = controls or []

    class ListTile:
        def __init__(self, title=None, leading=None, data=None, on_click=None):
            self.title = title
            self.leading = leading
            self.data = data
            self.on_click = on_click

    class Icon:
        def __init__(self, name):
            self.name = name

    class Page:
        def __init__(self):
            self.controls = []
            self.update = MagicMock()
            self.overlay = []
            self.snack_bar = SimpleNamespace(open=False, content=None)

        def add(self, *args):
            def _flatten(control):
                self.controls.append(control)
                for child in getattr(control, "controls", []) or []:
                    _flatten(child)
                content = getattr(control, "content", None)
                if content is not None:
                    _flatten(content)

            for arg in args:
                _flatten(arg)

    return SimpleNamespace(
        TextField=TextField,
        Text=Text,
        Dropdown=Dropdown,
        Switch=Switch,
        ElevatedButton=ElevatedButton,
        TextButton=TextButton,
        Row=Layout,
        Column=Layout,
        Container=Container,
        ListView=Layout,
        ExpansionTile=ExpansionTile,
        ListTile=ListTile,
        Icon=Icon,
        icons=SimpleNamespace(FOLDER="folder", INSERT_DRIVE_FILE="file"),
        ScrollMode=SimpleNamespace(ALWAYS="always"),
        Page=Page,
        dropdown=SimpleNamespace(Option=lambda v: v),
    )


def test_main_renderiza_componentes_minimos(monkeypatch):
    ft = _fake_flet()
    monkeypatch.setattr(app.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(
        app.runtime, "crear_arbol_directorios", lambda _ft, on_click: _ft.Column([])
    )
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
    monkeypatch.setattr(
        app.runtime, "transpilar_codigo", lambda _codigo, _lang: "transpilado"
    )
    monkeypatch.setattr(
        app.runtime, "formatear_error", lambda exc, **_kwargs: f"error: {exc}"
    )

    page = ft.Page()
    app.main(page)

    botones = [
        c
        for c in page.controls
        if isinstance(c, ft.ElevatedButton)
        and c.text
        in {
            "Nuevo",
            "Abrir",
            "Guardar",
            "Guardar como",
            "Recargar",
            "Ejecutar",
            "Tokens",
            "AST",
            "Sugerencias del Libro",
        }
    ]
    assert [b.text for b in botones] == [
        "Nuevo",
        "Abrir",
        "Guardar",
        "Guardar como",
        "Recargar",
        "Ejecutar",
        "Tokens",
        "AST",
        "Sugerencias del Libro",
    ]


def test_main_handler_actualiza_salida(monkeypatch):
    ft = _fake_flet()
    monkeypatch.setattr(app.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(
        app.runtime, "crear_arbol_directorios", lambda _ft, on_click: _ft.Column([])
    )
    monkeypatch.setattr(app.runtime, "gui_target_choices", lambda: ("python",))
    ejecutar_mock = MagicMock(return_value="ejecutado")
    transpilar_mock = MagicMock(return_value="transpilado")
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
    monkeypatch.setattr(app.runtime, "ejecutar_codigo", ejecutar_mock)
    monkeypatch.setattr(app.runtime, "transpilar_codigo", transpilar_mock)
    monkeypatch.setattr(
        app.runtime, "formatear_error", lambda exc, **_kwargs: f"error: {exc}"
    )

    page = ft.Page()
    app.main(page)

    entrada = next(
        c
        for c in page.controls
        if isinstance(c, ft.TextField) and c.kwargs.get("multiline")
    )
    selector = next(c for c in page.controls if isinstance(c, ft.Dropdown))
    activar = next(c for c in page.controls if isinstance(c, ft.Switch))
    salida = next(
        c
        for c in page.controls
        if isinstance(c, ft.Text) and c.kwargs.get("selectable")
    )
    ejecutar_btn = next(
        c
        for c in page.controls
        if isinstance(c, ft.ElevatedButton) and c.text == "Ejecutar"
    )

    entrada.value = "imprimir('x')"
    ejecutar_btn.on_click(None)
    assert salida.value == "ejecutado"

    activar.value = True
    selector.value = "python"
    ejecutar_btn.on_click(None)
    assert salida.value == "transpilado"

    selector.value = None
    ejecutar_btn.on_click(None)
    assert salida.value == "Selecciona un lenguaje destino para transpilar"
    assert ejecutar_mock.call_count == 1
    assert transpilar_mock.call_count == 1
    assert page.update.call_count == 3


def test_main_configura_selector_por_defecto_y_switch_deshabilitado_si_no_hay_targets(
    monkeypatch,
):
    ft = _fake_flet()
    monkeypatch.setattr(app.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(
        app.runtime, "crear_arbol_directorios", lambda _ft, on_click: _ft.Column([])
    )
    monkeypatch.setattr(app.runtime, "gui_target_choices", lambda: ())
    monkeypatch.setattr(
        app.runtime,
        "require_gui_dependencies",
        lambda: {
            "TRANSPILERS": {},
            "LexerError": RuntimeError,
            "ParserError": ValueError,
        },
    )
    monkeypatch.setattr(app.runtime, "normalizar_codigo", lambda value: value or "")
    monkeypatch.setattr(app.runtime, "ejecutar_codigo", lambda _codigo: "ejecutado")
    monkeypatch.setattr(
        app.runtime, "transpilar_codigo", lambda _codigo, _lang: "transpilado"
    )
    monkeypatch.setattr(
        app.runtime, "formatear_error", lambda exc, **_kwargs: f"error: {exc}"
    )

    page = ft.Page()
    app.main(page)

    selector = next(c for c in page.controls if isinstance(c, ft.Dropdown))
    activar = next(c for c in page.controls if isinstance(c, ft.Switch))

    assert selector.value is None
    assert activar.disabled is True


def _text_value(control):
    return getattr(getattr(control, "title", None), "value", None)


def test_crear_arbol_directorios_lista_solo_nivel_inicial(tmp_path):
    from pcobra.gui import runtime

    ft = _fake_flet()
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "anidado.cobra").write_text("imprimir('anidado')")
    (tmp_path / "programa.co").write_text("imprimir('co')")
    (tmp_path / "programa.cobra").write_text("imprimir('cobra')")
    (tmp_path / "ignorado.txt").write_text("no cobra")

    arbol = runtime.crear_arbol_directorios(
        ft, on_click=lambda _e: None, root_path=tmp_path
    )

    nombres = [_text_value(control) for control in arbol.controls]
    assert nombres == ["subdir", "programa.co", "programa.cobra"]
    subdir = arbol.controls[0]
    assert isinstance(subdir, ft.ExpansionTile)
    assert subdir.controls == []


def test_crear_arbol_directorios_carga_hijos_bajo_demanda_y_filtra(tmp_path):
    from pcobra.gui import runtime

    ft = _fake_flet()
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "hijo").mkdir()
    (tmp_path / "subdir" / "codigo.co").write_text("imprimir('co')")
    (tmp_path / "subdir" / "codigo.cobra").write_text("imprimir('cobra')")
    (tmp_path / "subdir" / "notas.txt").write_text("no cobra")
    (tmp_path / "raiz.cobra").write_text("imprimir('raiz')")

    arbol = runtime.crear_arbol_directorios(
        ft, on_click=lambda _e: None, root_path=tmp_path
    )
    subdir = arbol.controls[0]

    subdir.on_change(SimpleNamespace(control=subdir))

    nombres = [_text_value(control) for control in subdir.controls]
    assert nombres == ["hijo", "codigo.co", "codigo.cobra"]
    hijo = subdir.controls[0]
    assert isinstance(hijo, ft.ExpansionTile)
    assert hijo.controls == []
