"""Pruebas de preflight/errores de import para el comando ``gui``."""

import builtins
import sys
from types import SimpleNamespace

from pcobra.cobra.cli.commands.flet_cmd import FletCommand


def _args(ui: str = "idle") -> SimpleNamespace:
    return SimpleNamespace(ui=ui)


def _deps_module(**overrides):
    attrs = {
        "Lexer": object,
        "Parser": object,
        "InterpretadorCobra": object,
        "get_transpilers": lambda: {},
        "target_cli_choices": lambda _targets: (),
        "OFFICIAL_TARGETS": ("python", "javascript", "rust"),
    }
    attrs.update(overrides)
    return SimpleNamespace(**attrs)


def test_cli_gui_reporta_falta_de_flet(monkeypatch):
    mensajes: list[str] = []
    cmd = FletCommand()

    real_import = builtins.__import__

    def _import_fail_flet(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "flet":
            raise ModuleNotFoundError("No module named 'flet'", name="flet")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.mostrar_error", mensajes.append)
    monkeypatch.setattr(builtins, "__import__", _import_fail_flet)

    result = cmd.run(_args())

    assert result == 1
    assert "faltante detectado 'flet'" in mensajes[0]
    assert "pip install flet" in mensajes[0]


def test_cli_gui_reporta_falta_de_modulo_deps_en_preflight(monkeypatch):
    mensajes: list[str] = []
    cmd = FletCommand()
    fake_flet = SimpleNamespace(app=lambda **_kwargs: None)

    def _import_module(name: str):
        if name == "pcobra.cobra.gui.deps":
            raise ModuleNotFoundError("No module named 'pcobra.cobra.gui.deps'", name=name)
        if name == "pcobra.gui.idle":
            return SimpleNamespace(main=lambda _page: None)
        return _deps_module()

    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.mostrar_error", mensajes.append)
    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.importlib.import_module", _import_module)
    monkeypatch.setitem(sys.modules, "flet", fake_flet)

    result = cmd.run(_args())

    assert result == 1
    assert "Error de importación GUI" in mensajes[0]
    assert "pcobra.cobra.gui.deps" in mensajes[0]
    assert "pip install -e ." in mensajes[0]


def test_cli_gui_idle_reporta_simbolo_faltante_con_contexto_accionable(monkeypatch):
    mensajes: list[str] = []
    cmd = FletCommand()
    fake_flet = SimpleNamespace(app=lambda **_kwargs: None)

    def _import_module(name: str):
        if name == "pcobra.cobra.gui.deps":
            deps = _deps_module()
            delattr(deps, "InterpretadorCobra")
            return deps
        if name == "pcobra.gui.idle":
            return SimpleNamespace(main=lambda _page: None)
        return _deps_module()

    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.mostrar_error", mensajes.append)
    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.importlib.import_module", _import_module)
    monkeypatch.setitem(sys.modules, "flet", fake_flet)

    result = cmd.run(_args("idle"))

    assert result == 1
    assert "pcobra.cobra.gui.deps.InterpretadorCobra" in mensajes[0]
    assert "corrige el import local" in mensajes[0]


def test_cli_gui_app_reporta_simbolo_faltante_con_contexto_accionable(monkeypatch):
    mensajes: list[str] = []
    cmd = FletCommand()
    fake_flet = SimpleNamespace(app=lambda **_kwargs: None)

    def _import_module(name: str):
        if name == "pcobra.cobra.gui.deps":
            deps = _deps_module()
            delattr(deps, "get_transpilers")
            return deps
        if name == "pcobra.gui.app":
            return SimpleNamespace(main=lambda _page: None)
        return _deps_module()

    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.mostrar_error", mensajes.append)
    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.importlib.import_module", _import_module)
    monkeypatch.setitem(sys.modules, "flet", fake_flet)

    result = cmd.run(_args("app"))

    assert result == 1
    assert "pcobra.cobra.gui.deps.get_transpilers" in mensajes[0]
    assert "corrige el import local" in mensajes[0]


def test_cli_gui_reporta_error_interno_de_import(monkeypatch):
    mensajes: list[str] = []
    cmd = FletCommand()
    fake_flet = SimpleNamespace(app=lambda **_kwargs: None)

    def _import_module(name: str):
        if name == "pcobra.gui.idle":
            raise ImportError("cannot import name 'main' from partially initialized module")
        return _deps_module()

    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.mostrar_error", mensajes.append)
    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.importlib.import_module", _import_module)
    monkeypatch.setitem(sys.modules, "flet", fake_flet)

    result = cmd.run(_args())

    assert result == 1
    assert "Error de importación GUI" in mensajes[0]
    assert "pcobra.gui.idle" in mensajes[0]


def test_cli_gui_reporta_simbolo_faltante_en_preflight(monkeypatch):
    mensajes: list[str] = []
    cmd = FletCommand()
    fake_flet = SimpleNamespace(app=lambda **_kwargs: None)

    def _import_module(name: str):
        if name == "pcobra.cobra.gui.deps":
            return SimpleNamespace(
                Lexer=object,
                InterpretadorCobra=object,
                get_transpilers=lambda: {},
                target_cli_choices=lambda _targets: (),
                OFFICIAL_TARGETS=("python", "javascript", "rust"),
            )
        if name == "pcobra.gui.idle":
            return SimpleNamespace(main=lambda _page: None)
        return _deps_module()

    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.mostrar_error", mensajes.append)
    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.importlib.import_module", _import_module)
    monkeypatch.setitem(sys.modules, "flet", fake_flet)

    result = cmd.run(_args("idle"))

    assert result == 1
    assert "pcobra.cobra.gui.deps.Parser" in mensajes[0]


def test_cli_gui_importerror_sin_name_extrae_modulo_desde_mensaje(monkeypatch):
    mensajes: list[str] = []
    cmd = FletCommand()
    fake_flet = SimpleNamespace(app=lambda **_kwargs: None)

    def _import_module(name: str):
        if name == "pcobra.gui.idle":
            err = ImportError("No module named 'rich'")
            err.name = None
            raise err
        return _deps_module()

    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.mostrar_error", mensajes.append)
    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.importlib.import_module", _import_module)
    monkeypatch.setitem(sys.modules, "flet", fake_flet)

    result = cmd.run(_args())

    assert result == 1
    assert "faltante detectado 'rich'" in mensajes[0]
    assert "instala la dependencia" in mensajes[0]
