from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pytest
from rich.console import Console
from rich.table import Table


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
