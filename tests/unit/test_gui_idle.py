"""Smoke tests para el entrypoint GUI ``pcobra.gui.idle``."""

from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock

from pcobra.gui import idle


def _motor_disponible():
    return idle.runtime.MotorIASugerencias(disponible=True)


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
        def __init__(self, text, on_click=None, **kwargs):
            self.text = text
            self.on_click = on_click
            self.disabled = kwargs.get("disabled", False)
            self.tooltip = kwargs.get("tooltip")

    class TextButton(ElevatedButton):
        pass

    class Layout:
        def __init__(self, controls=None, **_kwargs):
            self.controls = controls or []
            self.data = _kwargs.get("data")
            self.on_click = _kwargs.get("on_click")
            self.on_change = _kwargs.get("on_change")

    class Container:
        def __init__(self, content=None, **_kwargs):
            self.content = content

    class ListTile(TextButton):
        def __init__(self, title=None, leading=None, data=None, on_click=None, **_kwargs):
            texto = getattr(title, "value", "")
            def _click(_e=None):
                if on_click is not None:
                    on_click(SimpleNamespace(control=self))

            super().__init__(f"📄 {texto}", on_click=_click)
            self.title = title
            self.leading = leading
            self.data = data

    class ExpansionTile(Layout):
        pass

    class Icon:
        def __init__(self, name):
            self.name = name

    class Page:
        def __init__(self):
            self.controls = []
            self.update = MagicMock()

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
        ListTile=ListTile,
        ExpansionTile=ExpansionTile,
        Icon=Icon,
        icons=SimpleNamespace(INSERT_DRIVE_FILE="file", FOLDER="folder"),
        ScrollMode=SimpleNamespace(ALWAYS="always"),
        Page=Page,
        dropdown=SimpleNamespace(Option=lambda v: v),
    )


def test_main_renderiza_botones_esperados(monkeypatch):
    ft = _fake_flet()
    monkeypatch.setattr(idle.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(idle.runtime, "detectar_motor_ia_sugerencias", _motor_disponible)
    monkeypatch.setattr(idle.runtime, "gui_target_choices", lambda: ("python",))
    monkeypatch.setattr(
        idle.runtime,
        "require_gui_dependencies",
        lambda: {
            "TRANSPILERS": {"python": object},
            "LexerError": RuntimeError,
            "ParserError": ValueError,
            "Lexer": lambda _codigo: SimpleNamespace(tokenizar=lambda: []),
            "Parser": lambda _tokens: SimpleNamespace(parsear=lambda: []),
        },
    )
    monkeypatch.setattr(idle.runtime, "normalizar_codigo", lambda value: value or "")
    monkeypatch.setattr(idle.runtime, "ejecutar_codigo", lambda _codigo: "ok")
    monkeypatch.setattr(
        idle.runtime, "transpilar_codigo", lambda _codigo, _lang: "transpilado"
    )
    monkeypatch.setattr(idle.runtime, "mostrar_tokens", lambda _codigo: "Token(X)")
    monkeypatch.setattr(idle.runtime, "mostrar_ast", lambda _codigo: "[Nodo]")
    monkeypatch.setattr(
        idle.runtime, "generar_sugerencias", lambda _codigo: ["Usa nombres descriptivos"]
    )
    monkeypatch.setattr(
        idle.runtime, "formatear_error", lambda exc, **_kwargs: f"error: {exc}"
    )
    page = ft.Page()
    idle.main(page)

    botones = [c for c in page.controls if isinstance(c, ft.ElevatedButton)]
    assert [
        b.text
        for b in botones
        if b.text in {"Ejecutar", "Tokens", "AST", "Sugerencias del Libro"}
    ] == [
        "Ejecutar",
        "Tokens",
        "AST",
        "Sugerencias del Libro",
    ]


def test_main_muestra_sugerencias_deshabilitadas_sin_motor(monkeypatch):
    ft = _fake_flet()
    monkeypatch.setattr(idle.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(idle.runtime, "gui_target_choices", lambda: ("python",))
    monkeypatch.setattr(
        idle.runtime,
        "detectar_motor_ia_sugerencias",
        lambda: idle.runtime.MotorIASugerencias(
            disponible=False,
            detalle="Sugerencias deshabilitadas: falta 'agix'.",
        ),
    )
    monkeypatch.setattr(
        idle.runtime,
        "require_gui_dependencies",
        lambda: {
            "TRANSPILERS": {"python": object},
            "LexerError": RuntimeError,
            "ParserError": ValueError,
        },
    )

    page = ft.Page()
    idle.main(page)

    sugerencias_btn = next(
        c
        for c in page.controls
        if isinstance(c, ft.ElevatedButton) and c.text == "Sugerencias del Libro"
    )

    assert sugerencias_btn.disabled is True
    assert sugerencias_btn.on_click is None
    assert "falta 'agix'" in sugerencias_btn.tooltip


def test_main_handlers_smoke(monkeypatch):
    ft = _fake_flet()
    monkeypatch.setattr(idle.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(idle.runtime, "detectar_motor_ia_sugerencias", _motor_disponible)
    monkeypatch.setattr(idle.runtime, "gui_target_choices", lambda: ("python",))
    ejecutar_mock = MagicMock(return_value="ejecutado")
    transpilar_mock = MagicMock(return_value="transpilado")
    monkeypatch.setattr(
        idle.runtime,
        "require_gui_dependencies",
        lambda: {
            "TRANSPILERS": {"python": object},
            "LexerError": RuntimeError,
            "ParserError": ValueError,
            "Lexer": lambda _codigo: SimpleNamespace(tokenizar=lambda: []),
            "Parser": lambda _tokens: SimpleNamespace(parsear=lambda: []),
        },
    )
    monkeypatch.setattr(idle.runtime, "normalizar_codigo", lambda value: value or "")
    monkeypatch.setattr(idle.runtime, "ejecutar_codigo", ejecutar_mock)
    monkeypatch.setattr(idle.runtime, "transpilar_codigo", transpilar_mock)
    monkeypatch.setattr(idle.runtime, "mostrar_tokens", lambda _codigo: "Token(X)")
    monkeypatch.setattr(idle.runtime, "mostrar_ast", lambda _codigo: "[Nodo]")
    monkeypatch.setattr(
        idle.runtime, "generar_sugerencias", lambda _codigo: ["Usa nombres descriptivos"]
    )
    monkeypatch.setattr(
        idle.runtime, "formatear_error", lambda exc, **_kwargs: f"error: {exc}"
    )
    analizador = ModuleType("pcobra.ia.analizador_agix")
    analizador.generar_sugerencias = lambda _codigo: ["Usa nombres descriptivos"]
    monkeypatch.setitem(sys.modules, "pcobra.ia.analizador_agix", analizador)

    page = ft.Page()
    idle.main(page)

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
    botones = {
        c.text: c
        for c in page.controls
        if isinstance(c, ft.ElevatedButton)
        and c.text in {"Ejecutar", "Tokens", "AST", "Sugerencias del Libro"}
    }
    ejecutar_btn = botones["Ejecutar"]
    tokens_btn = botones["Tokens"]
    ast_btn = botones["AST"]
    sugerencias_btn = botones["Sugerencias del Libro"]

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

    tokens_btn.on_click(None)
    assert salida.value == "Token(X)"

    ast_btn.on_click(None)
    assert salida.value == "[Nodo]"

    sugerencias_btn.on_click(None)
    assert "Errores léxicos/sintácticos" in salida.value
    assert "- No se detectaron errores" in salida.value
    assert "- Usa nombres descriptivos" in salida.value
    ejecutar_mock.assert_called_once_with("imprimir('x')")
    transpilar_mock.assert_called_once_with("imprimir('x')", "python")
    assert page.update.call_count == 6


def test_main_selector_y_switch_sin_targets(monkeypatch):
    ft = _fake_flet()
    monkeypatch.setattr(idle.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(idle.runtime, "detectar_motor_ia_sugerencias", _motor_disponible)
    monkeypatch.setattr(idle.runtime, "gui_target_choices", lambda: ())
    monkeypatch.setattr(
        idle.runtime,
        "require_gui_dependencies",
        lambda: {
            "TRANSPILERS": {},
            "LexerError": RuntimeError,
            "ParserError": ValueError,
        },
    )
    monkeypatch.setattr(idle.runtime, "normalizar_codigo", lambda value: value or "")
    monkeypatch.setattr(idle.runtime, "ejecutar_codigo", lambda _codigo: "ejecutado")
    monkeypatch.setattr(
        idle.runtime, "transpilar_codigo", lambda _codigo, _lang: "transpilado"
    )
    monkeypatch.setattr(idle.runtime, "mostrar_tokens", lambda _codigo: "Token(X)")
    monkeypatch.setattr(idle.runtime, "mostrar_ast", lambda _codigo: "[Nodo]")
    monkeypatch.setattr(
        idle.runtime, "generar_sugerencias", lambda _codigo: ["Usa nombres descriptivos"]
    )
    monkeypatch.setattr(
        idle.runtime, "formatear_error", lambda exc, **_kwargs: f"error: {exc}"
    )

    page = ft.Page()
    idle.main(page)

    selector = next(c for c in page.controls if isinstance(c, ft.Dropdown))
    activar = next(c for c in page.controls if isinstance(c, ft.Switch))

    assert selector.value is None
    assert activar.disabled is True


def test_main_acciones_publicas_de_archivo(monkeypatch, tmp_path):
    ft = _fake_flet()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(idle.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(idle.runtime, "detectar_motor_ia_sugerencias", _motor_disponible)
    monkeypatch.setattr(idle.runtime, "gui_target_choices", lambda: ("python",))
    monkeypatch.setattr(
        idle.runtime,
        "require_gui_dependencies",
        lambda: {
            "TRANSPILERS": {"python": object},
            "LexerError": RuntimeError,
            "ParserError": ValueError,
            "Lexer": lambda _codigo: SimpleNamespace(tokenizar=lambda: []),
            "Parser": lambda _tokens: SimpleNamespace(parsear=lambda: []),
        },
    )
    monkeypatch.setattr(idle.runtime, "normalizar_codigo", lambda value: value or "")
    monkeypatch.setattr(idle.runtime, "ejecutar_codigo", lambda _codigo: "ok")
    monkeypatch.setattr(
        idle.runtime, "transpilar_codigo", lambda _codigo, _lang: "transpilado"
    )
    monkeypatch.setattr(idle.runtime, "mostrar_tokens", lambda _codigo: "Token(X)")
    monkeypatch.setattr(idle.runtime, "mostrar_ast", lambda _codigo: "[Nodo]")
    monkeypatch.setattr(
        idle.runtime, "formatear_error", lambda exc, **_kwargs: f"error: {exc}"
    )

    archivo_abrir = tmp_path / "abrir.cobra"
    archivo_abrir.write_text("imprimir('abrir')", encoding="utf-8")
    archivo_arbol = tmp_path / "arbol.co"
    archivo_arbol.write_text("imprimir('arbol')", encoding="utf-8")
    destino_guardar_como = tmp_path / "guardar_como.cobra"

    page = ft.Page()
    idle.main(page)

    entrada = next(
        c
        for c in page.controls
        if isinstance(c, ft.TextField) and c.kwargs.get("multiline")
    )
    ruta_input = next(
        c
        for c in page.controls
        if isinstance(c, ft.TextField) and c.kwargs.get("label") == "Ruta"
    )
    salida = next(
        c
        for c in page.controls
        if isinstance(c, ft.Text) and c.kwargs.get("selectable")
    )
    estado_archivo = next(
        c
        for c in page.controls
        if isinstance(c, ft.Text) and not c.kwargs.get("selectable")
        and "Archivo nuevo" in c.value
    )
    botones = {
        c.text: c for c in page.controls if isinstance(c, ft.ElevatedButton)
    }

    botones["Nuevo"].on_click(None)
    assert entrada.value == ""
    assert salida.value == "Archivo nuevo creado en memoria."
    assert "Archivo nuevo (sin guardar)" in estado_archivo.value

    ruta_input.value = str(archivo_abrir)
    botones["Abrir"].on_click(None)
    assert entrada.value == "imprimir('abrir')"
    assert salida.value == f"Archivo cargado: {archivo_abrir.resolve()}"
    assert estado_archivo.value == str(archivo_abrir.resolve())

    entrada.value = "imprimir('guardado')"
    botones["Guardar"].on_click(None)
    assert archivo_abrir.read_text(encoding="utf-8") == "imprimir('guardado')"
    assert salida.value == f"Archivo guardado: {archivo_abrir.resolve()}"

    ruta_input.value = str(destino_guardar_como)
    entrada.value = "imprimir('como')"
    botones["Guardar como"].on_click(None)
    assert destino_guardar_como.read_text(encoding="utf-8") == "imprimir('como')"
    assert salida.value == f"Archivo guardado: {destino_guardar_como.resolve()}"

    destino_guardar_como.write_text("imprimir('recargado')", encoding="utf-8")
    entrada.value = "imprimir('memoria')"
    botones["Recargar"].on_click(None)
    assert entrada.value == "imprimir('recargado')"
    assert salida.value == f"Archivo cargado: {destino_guardar_como.resolve()}"

    boton_arbol = next(
        c
        for c in page.controls
        if isinstance(c, ft.TextButton) and c.text == f"📄 {archivo_arbol.name}"
    )
    boton_arbol.on_click(None)
    assert entrada.value == "imprimir('arbol')"
    assert salida.value == f"Archivo cargado: {archivo_arbol.resolve()}"
