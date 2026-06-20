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
            self.kwargs = _kwargs
            self.data = _kwargs.get("data")
            self.expand = _kwargs.get("expand")
            self.on_click = _kwargs.get("on_click")
            self.on_change = _kwargs.get("on_change")
            self.scroll = _kwargs.get("scroll")

    class Container:
        def __init__(self, content=None, **_kwargs):
            self.content = content
            self.kwargs = _kwargs
            self.width = _kwargs.get("width")

    class ListTile(TextButton):
        def __init__(
            self, title=None, leading=None, data=None, on_click=None, **_kwargs
        ):
            texto = getattr(title, "value", "")

            def _click(_e=None):
                if on_click is not None:
                    on_click(SimpleNamespace(control=self))

            super().__init__(f"📄 {texto}", on_click=_click)
            self.title = title
            self.leading = leading
            self.data = data

    class ExpansionTile(Layout):
        def __init__(self, title=None, leading=None, controls=None, **_kwargs):
            super().__init__(controls=controls, **_kwargs)
            self.title = title
            self.leading = leading

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
        Icons=SimpleNamespace(INSERT_DRIVE_FILE="file", FOLDER="folder"),
        ScrollMode=SimpleNamespace(ALWAYS="always"),
        Page=Page,
        dropdown=SimpleNamespace(Option=lambda v: v),
    )


def test_fake_flet_expone_icons_moderno():
    ft = _fake_flet()

    assert ft.Icons.INSERT_DRIVE_FILE == "file"
    assert ft.Icons.FOLDER == "folder"


def test_main_renderiza_botones_esperados(monkeypatch):
    ft = _fake_flet()
    monkeypatch.setattr(idle.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(
        idle.runtime, "detectar_motor_ia_sugerencias", _motor_disponible
    )
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
        idle.runtime,
        "generar_sugerencias",
        lambda _codigo: ["Usa nombres descriptivos"],
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
    monkeypatch.setattr(
        idle.runtime, "detectar_motor_ia_sugerencias", _motor_disponible
    )
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
        idle.runtime,
        "generar_sugerencias",
        lambda _codigo: ["Usa nombres descriptivos"],
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
    monkeypatch.setattr(
        idle.runtime, "detectar_motor_ia_sugerencias", _motor_disponible
    )
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
        idle.runtime,
        "generar_sugerencias",
        lambda _codigo: ["Usa nombres descriptivos"],
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


def test_main_inicializa_workspace_root_desde_env_y_ruta_visible_vacia(
    monkeypatch, tmp_path
):
    ft = _fake_flet()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("COBRA_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setattr(idle.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(
        idle.runtime, "detectar_motor_ia_sugerencias", _motor_disponible
    )
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
        idle.runtime,
        "generar_sugerencias",
        lambda _codigo: ["Usa nombres descriptivos"],
    )
    monkeypatch.setattr(
        idle.runtime, "formatear_error", lambda exc, **_kwargs: f"error: {exc}"
    )

    page = ft.Page()
    idle.main(page)

    ruta_input = next(
        c
        for c in page.controls
        if isinstance(c, ft.TextField) and c.kwargs.get("label") == "Ruta"
    )
    raiz_input = next(
        c
        for c in page.controls
        if isinstance(c, ft.TextField) and c.kwargs.get("label") == "Raíz del árbol"
    )

    assert ruta_input.value == ""
    assert raiz_input.value == str(tmp_path.resolve())


def test_main_arbol_inicial_muestra_subdirectorios_y_archivos_cobra(
    monkeypatch, tmp_path
):
    ft = _fake_flet()
    programa_cobra = tmp_path / "programa.cobra"
    programa_cobra.write_text("imprimir('cobra')", encoding="utf-8")
    programa_co = tmp_path / "programa.co"
    programa_co.write_text("imprimir('co')", encoding="utf-8")
    subdirectorio = tmp_path / "subdirectorio"
    subdirectorio.mkdir()

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("COBRA_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setattr(idle.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(
        idle.runtime, "detectar_motor_ia_sugerencias", _motor_disponible
    )
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

    page = ft.Page()
    idle.main(page)

    arbol = next(
        c
        for c in page.controls
        if isinstance(c, ft.ListView)
        and getattr(getattr(c, "controls", [None])[0], "value", "").startswith(
            "Directorio raíz:"
        )
    )
    entradas = arbol.controls[1:]
    titulos = [getattr(control.title, "value", "") for control in entradas]

    assert arbol.controls[0].value == f"Directorio raíz: {tmp_path.resolve()}"
    assert "subdirectorio" in titulos
    assert "programa.cobra" in titulos
    assert "programa.co" in titulos
    assert len(entradas) == 3
    assert entradas
    assert (
        next(
            control for control in entradas if control.title.value == "subdirectorio"
        ).leading.name
        == ft.Icons.FOLDER
    )
    assert (
        next(
            control for control in entradas if control.title.value == "programa.cobra"
        ).leading.name
        == ft.Icons.INSERT_DRIVE_FILE
    )
    assert (
        next(
            control for control in entradas if control.title.value == "programa.co"
        ).leading.name
        == ft.Icons.INSERT_DRIVE_FILE
    )


def test_main_arbol_inicial_muestra_estado_vacio_en_tmp_path_vacio(
    monkeypatch, tmp_path
):
    ft = _fake_flet()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("COBRA_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setattr(idle.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(
        idle.runtime, "detectar_motor_ia_sugerencias", _motor_disponible
    )
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
        idle.runtime,
        "generar_sugerencias",
        lambda _codigo: ["Usa nombres descriptivos"],
    )
    monkeypatch.setattr(
        idle.runtime, "formatear_error", lambda exc, **_kwargs: f"error: {exc}"
    )

    page = ft.Page()
    idle.main(page)

    arbol = next(
        c
        for c in page.controls
        if isinstance(c, ft.ListView)
        and getattr(getattr(c, "controls", [None])[0], "value", "").startswith(
            "Directorio raíz:"
        )
    )

    assert any(
        getattr(control, "value", "") == "No hay archivos Cobra en esta carpeta"
        for control in arbol.controls[1:]
    )
    assert len(arbol.controls) > 1


def test_main_panel_lateral_conserva_ancho_contenido_y_arbol(monkeypatch, tmp_path):
    ft = _fake_flet()
    programa_cobra = tmp_path / "programa.cobra"
    programa_cobra.write_text("imprimir('cobra')", encoding="utf-8")
    programa_co = tmp_path / "programa.co"
    programa_co.write_text("imprimir('co')", encoding="utf-8")
    subdirectorio = tmp_path / "subdirectorio"
    subdirectorio.mkdir()

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("COBRA_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setattr(idle.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(
        idle.runtime, "detectar_motor_ia_sugerencias", _motor_disponible
    )
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

    page = ft.Page()
    idle.main(page)

    panel_lateral = next(
        c
        for c in page.controls
        if isinstance(c, ft.Container)
        and getattr(getattr(c, "content", None), "controls", [None])[0].value
        == "Archivos Cobra"
    )
    columna = panel_lateral.content
    arbol = columna.controls[-1]
    entradas = [control for control in arbol.controls[1:] if hasattr(control, "title")]
    titulos = [getattr(control.title, "value", "") for control in entradas]

    assert panel_lateral.width == 280
    assert panel_lateral.kwargs["padding"] == 12
    assert panel_lateral.kwargs["border_radius"] == 8
    assert getattr(columna, "controls", None)
    assert columna.expand is True
    assert arbol.expand is True
    assert columna.controls[0].value == "Archivos Cobra"
    assert columna.controls[-1] is arbol
    assert arbol.controls[0].value == f"Directorio raíz: {tmp_path.resolve()}"
    assert {"subdirectorio", "programa.cobra", "programa.co"}.issubset(titulos)
    assert entradas


def test_main_muestra_error_visible_si_falla_arbol_directorios(monkeypatch, tmp_path):
    ft = _fake_flet()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("COBRA_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setattr(idle.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(
        idle.runtime, "detectar_motor_ia_sugerencias", _motor_disponible
    )
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
    monkeypatch.setattr(
        idle.runtime, "formatear_error", lambda exc, **_kwargs: f"error: {exc}"
    )

    def _crear_arbol_falla(*_args, **_kwargs):
        raise FileNotFoundError("directorio inaccesible")

    monkeypatch.setattr(idle.runtime, "crear_arbol_directorios", _crear_arbol_falla)

    page = ft.Page()
    idle.main(page)

    salida = next(
        c
        for c in page.controls
        if isinstance(c, ft.Text) and c.kwargs.get("selectable")
    )
    arbol = next(
        c
        for c in page.controls
        if isinstance(c, ft.ListView)
        and getattr(getattr(c, "controls", [None])[0], "value", "").startswith(
            "Directorio raíz:"
        )
    )

    assert salida.value == "error: directorio inaccesible"
    assert any(
        getattr(control, "value", "")
        == "No se pudo listar la ruta: error: directorio inaccesible"
        for control in arbol.controls
    )


def test_main_establecer_raiz_arbol_muestra_error_si_listado_falla(
    monkeypatch, tmp_path
):
    ft = _fake_flet()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("COBRA_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setattr(idle.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(
        idle.runtime, "detectar_motor_ia_sugerencias", _motor_disponible
    )
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
    monkeypatch.setattr(
        idle.runtime, "formatear_error", lambda exc, **_kwargs: f"error: {exc}"
    )

    raiz_bloqueada = tmp_path / "bloqueada"
    raiz_bloqueada.mkdir()
    llamadas = {"total": 0}
    crear_arbol_real = idle.runtime.crear_arbol_directorios

    def _crear_arbol_falla_en_raiz_bloqueada(*args, **kwargs):
        llamadas["total"] += 1
        if kwargs.get("root_path") == raiz_bloqueada.resolve():
            raise PermissionError("sin permiso portable")
        return crear_arbol_real(*args, **kwargs)

    monkeypatch.setattr(
        idle.runtime, "crear_arbol_directorios", _crear_arbol_falla_en_raiz_bloqueada
    )

    page = ft.Page()
    idle.main(page)

    raiz_input = next(
        c
        for c in page.controls
        if isinstance(c, ft.TextField) and c.kwargs.get("label") == "Raíz del árbol"
    )
    boton_raiz = next(
        c
        for c in page.controls
        if isinstance(c, ft.ElevatedButton) and c.text == "Establecer raíz"
    )
    salida = next(
        c
        for c in page.controls
        if isinstance(c, ft.Text) and c.kwargs.get("selectable")
    )
    arbol = next(
        c
        for c in page.controls
        if isinstance(c, ft.ListView)
        and getattr(getattr(c, "controls", [None])[0], "value", "").startswith(
            "Directorio raíz:"
        )
    )

    raiz_input.value = str(raiz_bloqueada)
    boton_raiz.on_click(None)

    assert llamadas["total"] >= 2
    assert salida.value == "error: sin permiso portable"
    assert any(
        getattr(control, "value", "")
        == "No se pudo listar la ruta: error: sin permiso portable"
        for control in arbol.controls
    )
    assert len(arbol.controls) > 1


def test_main_acciones_publicas_de_archivo(monkeypatch, tmp_path):
    ft = _fake_flet()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("COBRA_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setattr(idle.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(
        idle.runtime, "detectar_motor_ia_sugerencias", _motor_disponible
    )
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

    subdir_abrir = tmp_path / "subdir_abrir"
    subdir_abrir.mkdir()
    archivo_abrir = subdir_abrir / "abrir.cobra"
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
    assert ruta_input.value == ""
    salida = next(
        c
        for c in page.controls
        if isinstance(c, ft.Text) and c.kwargs.get("selectable")
    )
    arbol = next(
        c
        for c in page.controls
        if isinstance(c, ft.ListView)
        and getattr(getattr(c, "controls", [None])[0], "value", "").startswith(
            "Directorio raíz:"
        )
    )
    estado_archivo = next(
        c
        for c in page.controls
        if isinstance(c, ft.Text)
        and not c.kwargs.get("selectable")
        and "Archivo nuevo" in c.value
    )
    botones = {c.text: c for c in page.controls if isinstance(c, ft.ElevatedButton)}

    botones["Nuevo"].on_click(None)
    assert entrada.value == ""
    assert salida.value == "Archivo nuevo creado en memoria."
    assert "Archivo nuevo (sin guardar)" in estado_archivo.value

    ruta_input.value = str(archivo_abrir)
    botones["Abrir"].on_click(None)
    assert entrada.value == "imprimir('abrir')"
    assert salida.value == f"Archivo cargado: {archivo_abrir.resolve()}"
    assert estado_archivo.value == str(archivo_abrir.resolve())
    assert ruta_input.value == str(archivo_abrir.resolve())
    assert arbol.controls[0].value == f"Directorio raíz: {tmp_path.resolve()}"

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


def test_main_establecer_raiz_arbol_valida_directorios(monkeypatch, tmp_path):
    ft = _fake_flet()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("COBRA_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setattr(idle.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(
        idle.runtime, "detectar_motor_ia_sugerencias", _motor_disponible
    )
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

    subdir = tmp_path / "subdir"
    subdir.mkdir()
    archivo = tmp_path / "archivo.cobra"
    archivo.write_text("imprimir('x')", encoding="utf-8")

    page = ft.Page()
    idle.main(page)

    boton_raiz = next(
        c
        for c in page.controls
        if isinstance(c, ft.ElevatedButton) and c.text == "Establecer raíz"
    )
    raiz_input = next(
        c
        for c in page.controls
        if isinstance(c, ft.TextField) and c.kwargs.get("label") == "Raíz del árbol"
    )
    salida = next(
        c
        for c in page.controls
        if isinstance(c, ft.Text) and c.kwargs.get("selectable")
    )
    arbol = next(
        c
        for c in page.controls
        if isinstance(c, ft.ListView)
        and getattr(getattr(c, "controls", [None])[0], "value", "").startswith(
            "Directorio raíz:"
        )
    )

    raiz_input.value = str(archivo)
    boton_raiz.on_click(None)
    assert (
        salida.value == f"La raíz del árbol debe ser un directorio: {archivo.resolve()}"
    )

    raiz_input.value = str(subdir)
    boton_raiz.on_click(None)
    assert salida.value == f"Raíz del árbol actualizada: {subdir.resolve()}"
    assert raiz_input.value == str(subdir.resolve())
    assert arbol.controls[0].value == f"Directorio raíz: {subdir.resolve()}"


def test_crear_arbol_directorios_muestra_estado_vacio_en_carpeta_sin_cobras(tmp_path):
    ft = _fake_flet()

    arbol = idle.runtime.crear_arbol_directorios(
        ft, on_click=lambda _e: None, root_path=tmp_path
    )

    assert arbol.scroll == ft.ScrollMode.ALWAYS
    assert len(arbol.controls) == 1
    assert arbol.controls[0].value == "No hay archivos Cobra en esta carpeta"


def _preparar_idle_archivos(monkeypatch, tmp_path):
    ft = _fake_flet()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("COBRA_PROJECTS_DIR", str(tmp_path))
    monkeypatch.setattr(idle.runtime, "require_flet", lambda: ft)
    monkeypatch.setattr(
        idle.runtime,
        "detectar_motor_ia_sugerencias",
        _motor_disponible,
    )
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
    guardar_como = next(
        c
        for c in page.controls
        if isinstance(c, ft.ElevatedButton) and c.text == "Guardar como"
    )
    abrir = next(
        c
        for c in page.controls
        if isinstance(c, ft.ElevatedButton) and c.text == "Abrir"
    )
    return ft, page, entrada, ruta_input, salida, abrir, guardar_como


def test_guardar_como_resuelve_ruta_relativa_con_extension_y_normaliza_input(
    monkeypatch, tmp_path
):
    (
        _ft,
        _page,
        entrada,
        ruta_input,
        salida,
        _abrir,
        guardar_como,
    ) = _preparar_idle_archivos(monkeypatch, tmp_path)
    (tmp_path / "src").mkdir()
    destino = (tmp_path / "src" / "main.cobra").resolve()

    entrada.value = "imprimir('main')"
    ruta_input.value = "src/main"
    guardar_como.on_click(None)

    assert destino.read_text(encoding="utf-8") == "imprimir('main')"
    assert salida.value == f"Archivo guardado: {destino}"
    assert ruta_input.value == str(destino)


def test_guardar_como_rechaza_escape_relativo_absoluto_externo_y_directorio(
    monkeypatch, tmp_path
):
    (
        _ft,
        _page,
        entrada,
        ruta_input,
        salida,
        _abrir,
        guardar_como,
    ) = _preparar_idle_archivos(monkeypatch, tmp_path)
    directorio = tmp_path / "existente"
    directorio.mkdir()
    absoluto_externo = (tmp_path.parent / "escape_idle_absoluto.cobra").resolve()
    entrada.value = "imprimir('no guardar')"

    for ruta in ("../escape.cobra", str(absoluto_externo), str(directorio)):
        ruta_input.value = ruta
        guardar_como.on_click(None)
        assert salida.value.startswith("error: ")

    assert not (tmp_path.parent / "escape.cobra").exists()
    assert not absoluto_externo.exists()
    assert directorio.is_dir()


def test_abrir_valida_ruta_relativa_visible_dentro_del_proyecto(
    monkeypatch, tmp_path
):
    (
        _ft,
        _page,
        entrada,
        ruta_input,
        salida,
        abrir,
        _guardar_como,
    ) = _preparar_idle_archivos(monkeypatch, tmp_path)
    (tmp_path / "src").mkdir()
    archivo = (tmp_path / "src" / "abrir.co").resolve()
    archivo.write_text("imprimir('ok')", encoding="utf-8")

    ruta_input.value = "src/abrir.co"
    abrir.on_click(None)

    assert entrada.value == "imprimir('ok')"
    assert salida.value == f"Archivo cargado: {archivo}"
    assert ruta_input.value == str(archivo)


def test_abrir_rechaza_ruta_visible_fuera_del_proyecto_antes_del_runtime(
    monkeypatch, tmp_path
):
    llamadas = []
    abrir_real = idle.runtime.abrir_archivo_desde_ruta

    def _abrir_spy(ruta, estado):
        llamadas.append(ruta)
        return abrir_real(ruta, estado)

    monkeypatch.setattr(idle.runtime, "abrir_archivo_desde_ruta", _abrir_spy)
    (
        _ft,
        _page,
        entrada,
        ruta_input,
        salida,
        abrir,
        _guardar_como,
    ) = _preparar_idle_archivos(monkeypatch, tmp_path)
    externo = (tmp_path.parent / "abrir_fuera_idle.cobra").resolve()
    externo.write_text("imprimir('fuera')", encoding="utf-8")

    try:
        ruta_input.value = str(externo)
        abrir.on_click(None)

        assert llamadas == []
        assert entrada.value == ""
        assert salida.value.startswith("error: ")
        assert "raíz del proyecto" in salida.value
    finally:
        externo.unlink(missing_ok=True)
