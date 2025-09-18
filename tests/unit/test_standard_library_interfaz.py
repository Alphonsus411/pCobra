from __future__ import annotations

import builtins
import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pytest
from rich.console import Console
from rich.json import JSON
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree
from rich.pretty import Pretty


def _cargar_interfaz() -> ModuleType:
    ruta = Path(__file__).resolve().parents[2] / "src" / "pcobra" / "standard_library" / "interfaz.py"
    spec = importlib.util.spec_from_file_location("pcobra.standard_library.interfaz", ruta)
    if spec is None or spec.loader is None:  # pragma: no cover - error al cargar
        raise RuntimeError("No se pudo preparar el módulo de interfaz")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


interfaz = _cargar_interfaz()
barra_progreso = interfaz.barra_progreso
imprimir_aviso = interfaz.imprimir_aviso
iniciar_gui = interfaz.iniciar_gui
iniciar_gui_idle = interfaz.iniciar_gui_idle
limpiar_consola = interfaz.limpiar_consola
mostrar_panel = interfaz.mostrar_panel
mostrar_tabla = interfaz.mostrar_tabla
mostrar_codigo = interfaz.mostrar_codigo
mostrar_markdown = interfaz.mostrar_markdown
mostrar_json = interfaz.mostrar_json
mostrar_arbol = interfaz.mostrar_arbol
preguntar_confirmacion = interfaz.preguntar_confirmacion


def test_mostrar_codigo_resalta_codigo_en_console_mock():
    console = Mock(spec=Console)

    resaltado = mostrar_codigo("print('hola')", "python", console=console)

    console.print.assert_called_once()
    render = console.print.call_args.args[0]
    assert isinstance(render, Syntax)
    assert render.code == "print('hola')"
    assert getattr(render.lexer, "name", "").lower() == "python"
    assert resaltado is render


def test_mostrar_codigo_sin_rich_syntax_lanza_error(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "rich.syntax":
            raise ModuleNotFoundError("simulado")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(RuntimeError):
        mostrar_codigo("print('hola')", "python")


def test_mostrar_markdown_instancia_render_correcto():
    console = Mock(spec=Console)

    render = mostrar_markdown("# Título\n\nTexto", console=console)

    console.print.assert_called_once_with(render)
    assert isinstance(render, Markdown)


def test_mostrar_markdown_sin_dependencia_lanza_error(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "rich.markdown":
            raise ModuleNotFoundError("sin rich.markdown")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(RuntimeError):
        mostrar_markdown("**Hola**")


def test_mostrar_json_cadena_emplea_json_render():
    console = Mock(spec=Console)

    render = mostrar_json('{"nombre": "Ada"}', console=console)

    console.print.assert_called_once_with(render)
    assert isinstance(render, JSON)


def test_mostrar_json_datos_python_serializa(monkeypatch):
    console = Mock(spec=Console)

    render = mostrar_json({"nombre": "Ada", "rol": "Pionera"}, console=console)

    console.print.assert_called_once_with(render)
    assert isinstance(render, JSON)


def test_mostrar_json_objeto_no_serializable_usa_pretty(monkeypatch):
    console = Mock(spec=Console)

    render = mostrar_json({"obj": object()}, console=console)

    console.print.assert_called_once_with(render)
    assert isinstance(render, Pretty)


def test_mostrar_json_sin_dependencia_lanza_error(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name in {"rich.json", "rich.pretty"}:
            raise ModuleNotFoundError("sin dependencia")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(RuntimeError):
        mostrar_json({"clave": "valor"})


def test_mostrar_arbol_construye_ramas_en_orden():
    console = Mock(spec=Console)
    estructura = [
        ("src", ["app.py", ("utils", ["helpers.py"])]),
        ("tests", ["test_app.py"]),
    ]

    arbol = mostrar_arbol(estructura, titulo="Proyecto", console=console)

    console.print.assert_called_once_with(arbol)
    assert isinstance(arbol, Tree)
    assert arbol.label == "Proyecto"
    assert [rama.label for rama in arbol.children] == ["src", "tests"]
    src = arbol.children[0]
    assert [hijo.label for hijo in src.children] == ["app.py", "utils"]
    utils = src.children[1]
    assert [hoja.label for hoja in utils.children] == ["helpers.py"]


def test_mostrar_arbol_acepta_diccionarios_y_none():
    console = Mock(spec=Console)
    estructura = {"src": {"main.py": None}}

    arbol = mostrar_arbol(estructura, console=console)

    console.print.assert_called_once_with(arbol)
    assert arbol.children[0].label == "src"
    assert arbol.children[0].children[0].label == "main.py"


def test_preguntar_confirmacion_usa_valor_por_defecto(monkeypatch):
    console = Mock(spec=Console)

    class DummyConfirm:
        last_call = None

        @classmethod
        def ask(cls, mensaje, default=None, console=None):
            cls.last_call = (mensaje, default, console)
            return default

    prompt_mod = ModuleType("rich.prompt")
    prompt_mod.Confirm = DummyConfirm
    monkeypatch.setitem(sys.modules, "rich.prompt", prompt_mod)

    respuesta = preguntar_confirmacion("¿Continuar?", console=console)

    assert respuesta is True
    assert DummyConfirm.last_call == ("¿Continuar?", True, console)

    respuesta_no = preguntar_confirmacion(
        "¿Continuar?", por_defecto=False, console=console
    )
    assert respuesta_no is False
    assert DummyConfirm.last_call == ("¿Continuar?", False, console)


def test_mostrar_tabla_emplea_console_mock():
    console = Mock(spec=Console)
    filas = [
        {"nombre": "Ada", "rol": "Pionera"},
        {"nombre": "Grace", "rol": "Arquitecta"},
    ]

    tabla = mostrar_tabla(filas, titulo="Referentes", console=console)

    console.print.assert_called_once()
    renderizable = console.print.call_args[0][0]
    assert isinstance(renderizable, Table)
    assert tabla is renderizable
    assert [col.header for col in tabla.columns] == ["nombre", "rol"]


def test_mostrar_tabla_con_columnas_explicitas():
    console = Mock(spec=Console)
    filas = [
        {"nombre": "Ada", "rol": "Pionera"},
    ]

    tabla = mostrar_tabla(filas, columnas=["rol", "nombre"], console=console)

    console.print.assert_called_once_with(tabla)
    assert [col.header for col in tabla.columns] == ["rol", "nombre"]
    assert tabla.columns[0]._cells == ["Pionera"]
    assert tabla.columns[1]._cells == ["Ada"]


def test_mostrar_tabla_con_secuencias_infiere_columnas_y_ajusta():
    console = Mock(spec=Console)
    filas = [
        ("Ada", "Lovelace", "Pionera"),
        ("Grace",),
    ]

    tabla = mostrar_tabla(filas, console=console)

    console.print.assert_called_once_with(tabla)
    assert [col.header for col in tabla.columns] == ["columna_1", "columna_2", "columna_3"]
    assert tabla.columns[1]._cells == ["Lovelace", ""]
    assert tabla.columns[2]._cells == ["Pionera", ""]


def test_mostrar_tabla_con_valores_simples_crea_columna_generica():
    console = Mock(spec=Console)
    filas = ["unico"]

    tabla = mostrar_tabla(filas, console=console)

    console.print.assert_called_once_with(tabla)
    assert [col.header for col in tabla.columns] == ["valor"]
    assert tabla.columns[0]._cells == ["unico"]


def test_imprimir_aviso_formatea_estilo(monkeypatch):
    console = Mock(spec=Console)
    imprimir_aviso("Proceso finalizado", nivel="exito", console=console)

    console.print.assert_called_once()
    args, kwargs = console.print.call_args
    assert "✔" in args[0]
    assert kwargs.get("style") == "bold green"


def test_limpiar_consola_invoca_clear():
    console = Mock(spec=Console)
    limpiar_consola(console=console)
    console.clear.assert_called_once()


def test_barra_progreso_avanza():
    console = Console(record=True)
    with barra_progreso(total=2, descripcion="Carga", console=console, transient=False) as (progreso, tarea):
        progreso.advance(tarea)
        progreso.advance(tarea)
        assert progreso.tasks[0].completed == pytest.approx(2)


def test_barra_progreso_sin_total_muestra_completados():
    console = Console(record=True)
    with barra_progreso(descripcion="Carga", console=console, transient=False) as (progreso, tarea):
        progreso.advance(tarea, 3)
        assert progreso.tasks[0].completed == pytest.approx(3)


def test_mostrar_panel_devuelve_render():
    console = Mock(spec=Console)
    panel = mostrar_panel("Hola", titulo="Panel", console=console)
    console.print.assert_called_once_with(panel)


def test_iniciar_gui_invoca_flet_app(monkeypatch):
    fake_app = Mock()
    fake_flet = SimpleNamespace(app=fake_app)
    monkeypatch.setitem(sys.modules, "flet", fake_flet)

    def dummy(page):
        return page

    iniciar_gui(destino=dummy, view="web")
    fake_app.assert_called_once()
    assert fake_app.call_args.kwargs["target"] is dummy
    assert fake_app.call_args.kwargs["view"] == "web"


def test_iniciar_gui_usa_destino_por_defecto(monkeypatch):
    fake_app = Mock()
    fake_flet = SimpleNamespace(app=fake_app)
    monkeypatch.setitem(sys.modules, "flet", fake_flet)

    marcador = lambda page: page
    app_mod = ModuleType("pcobra.gui.app")
    app_mod.main = marcador
    monkeypatch.setitem(sys.modules, "pcobra.gui.app", app_mod)

    iniciar_gui(view="web")

    fake_app.assert_called_once()
    assert fake_app.call_args.kwargs["target"] is marcador
    assert fake_app.call_args.kwargs["view"] == "web"


def test_iniciar_gui_idle_usa_objetivo_por_defecto(monkeypatch):
    fake_app = Mock()
    fake_flet = SimpleNamespace(app=fake_app)
    monkeypatch.setitem(sys.modules, "flet", fake_flet)

    def marcador(page):
        return page

    idle_mod = ModuleType("pcobra.gui.idle")
    idle_mod.main = marcador
    monkeypatch.setitem(sys.modules, "pcobra.gui.idle", idle_mod)

    iniciar_gui_idle()
    fake_app.assert_called_once()
    assert fake_app.call_args.kwargs["target"] is marcador
