"""Pruebas de preflight/errores de import para el comando ``gui``."""

import builtins
import sys
from types import SimpleNamespace

from pcobra.cobra.cli.commands.flet_cmd import FletCommand


def _args(ui: str = "idle") -> SimpleNamespace:
    return SimpleNamespace(ui=ui)


def _default_module(name: str) -> SimpleNamespace:
    if name == "pcobra.cobra.cli.commands.compile_cmd":
        return SimpleNamespace(TRANSPILERS={})
    if name == "pcobra.cobra.core":
        return SimpleNamespace(Lexer=object, Parser=object)
    if name == "pcobra.cobra.transpilers.target_utils":
        return SimpleNamespace(target_cli_choices=lambda _targets: ())
    if name == "pcobra.core.interpreter":
        return SimpleNamespace(InterpretadorCobra=object)
    return SimpleNamespace()


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
    assert "falta el módulo 'flet'" in mensajes[0]
    assert "pip install flet" in mensajes[0]


def test_cli_gui_reporta_falta_de_modulo_core_en_preflight(monkeypatch):
    mensajes: list[str] = []
    cmd = FletCommand()
    fake_flet = SimpleNamespace(app=lambda **_kwargs: None)

    def _import_module(name: str):
        if name == "pcobra.cobra.core":
            raise ModuleNotFoundError("No module named 'pcobra.cobra.core'", name=name)
        if name == "pcobra.gui.idle":
            return SimpleNamespace(main=lambda _page: None)
        return _default_module(name)

    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.mostrar_error", mensajes.append)
    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.importlib.import_module", _import_module)
    monkeypatch.setitem(sys.modules, "flet", fake_flet)

    result = cmd.run(_args())

    assert result == 1
    assert "Error interno del paquete" in mensajes[0]
    assert "pcobra.cobra.core" in mensajes[0]
    assert "pip install -e ." in mensajes[0]


def test_cli_gui_reporta_falta_de_modulo_transpiler_en_preflight(monkeypatch):
    mensajes: list[str] = []
    cmd = FletCommand()
    fake_flet = SimpleNamespace(app=lambda **_kwargs: None)

    def _import_module(name: str):
        if name == "pcobra.cobra.transpilers.targets":
            raise ModuleNotFoundError("No module named 'pcobra.cobra.transpilers.targets'", name=name)
        if name == "pcobra.gui.idle":
            return SimpleNamespace(main=lambda _page: None)
        return _default_module(name)

    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.mostrar_error", mensajes.append)
    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.importlib.import_module", _import_module)
    monkeypatch.setitem(sys.modules, "flet", fake_flet)

    result = cmd.run(_args())

    assert result == 1
    assert "Error interno del paquete" in mensajes[0]
    assert "pcobra.cobra.transpilers.targets" in mensajes[0]
    assert "pip install -e ." in mensajes[0]


def test_cli_gui_idle_reporta_modulo_faltante_con_contexto_accionable(monkeypatch):
    mensajes: list[str] = []
    cmd = FletCommand()
    fake_flet = SimpleNamespace(app=lambda **_kwargs: None)

    def _import_module(name: str):
        if name == "pcobra.core.interpreter":
            raise ModuleNotFoundError("No module named 'pcobra.core.interpreter'", name=name)
        if name == "pcobra.gui.idle":
            return SimpleNamespace(main=lambda _page: None)
        return SimpleNamespace(
            Lexer=object,
            Parser=object,
            TRANSPILERS={},
            target_cli_choices=lambda _targets: (),
        )

    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.mostrar_error", mensajes.append)
    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.importlib.import_module", _import_module)
    monkeypatch.setitem(sys.modules, "flet", fake_flet)

    result = cmd.run(_args("idle"))

    assert result == 1
    assert "pcobra.core.interpreter" in mensajes[0]
    assert "pip install -e ." in mensajes[0]


def test_cli_gui_app_reporta_modulo_faltante_con_contexto_accionable(monkeypatch):
    mensajes: list[str] = []
    cmd = FletCommand()
    fake_flet = SimpleNamespace(app=lambda **_kwargs: None)

    def _import_module(name: str):
        if name == "pcobra.cobra.cli.commands.compile_cmd":
            raise ModuleNotFoundError(
                "No module named 'pcobra.cobra.cli.commands.compile_cmd'", name=name
            )
        if name == "pcobra.gui.app":
            return SimpleNamespace(main=lambda _page: None)
        return SimpleNamespace(
            Lexer=object,
            Parser=object,
            InterpretadorCobra=object,
            target_cli_choices=lambda _targets: (),
        )

    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.mostrar_error", mensajes.append)
    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.importlib.import_module", _import_module)
    monkeypatch.setitem(sys.modules, "flet", fake_flet)

    result = cmd.run(_args("app"))

    assert result == 1
    assert "pcobra.cobra.cli.commands.compile_cmd" in mensajes[0]
    assert "pip install -e ." in mensajes[0]


def test_cli_gui_reporta_error_interno_de_import(monkeypatch):
    mensajes: list[str] = []
    cmd = FletCommand()
    fake_flet = SimpleNamespace(app=lambda **_kwargs: None)

    def _import_module(name: str):
        if name == "pcobra.gui.idle":
            raise ImportError("cannot import name 'main' from partially initialized module")
        return _default_module(name)

    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.mostrar_error", mensajes.append)
    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.importlib.import_module", _import_module)
    monkeypatch.setitem(sys.modules, "flet", fake_flet)

    result = cmd.run(_args())

    assert result == 1
    assert "Error interno de importación" in mensajes[0]
    assert "pcobra.gui.idle" in mensajes[0]


def test_cli_gui_reporta_simbolo_faltante_en_preflight(monkeypatch):
    mensajes: list[str] = []
    cmd = FletCommand()
    fake_flet = SimpleNamespace(app=lambda **_kwargs: None)

    def _import_module(name: str):
        if name == "pcobra.cobra.core":
            return SimpleNamespace(Lexer=object)
        if name == "pcobra.gui.idle":
            return SimpleNamespace(main=lambda _page: None)
        return SimpleNamespace(
            TRANSPILERS={},
            target_cli_choices=lambda _targets: (),
            InterpretadorCobra=object,
        )

    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.mostrar_error", mensajes.append)
    monkeypatch.setattr("pcobra.cobra.cli.commands.flet_cmd.importlib.import_module", _import_module)
    monkeypatch.setitem(sys.modules, "flet", fake_flet)

    result = cmd.run(_args("idle"))

    assert result == 1
    assert "falta el símbolo 'Parser'" in mensajes[0]
    assert "pcobra.cobra.core" in mensajes[0]
