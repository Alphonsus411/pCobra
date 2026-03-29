from __future__ import annotations

import importlib
import runpy
import sys
from types import ModuleType

import pytest


ALIASES_RELEVANTES = ("pcobra.cli", "pcobra.cli.cli", "cli", "cli.cli")


def _limpiar_aliases() -> None:
    for name in ALIASES_RELEVANTES:
        sys.modules.pop(name, None)


def test_import_pcobra_cli_no_colisiona_con_paquete_canonico():
    _limpiar_aliases()

    modulo_pcobra_cli = importlib.import_module("pcobra.cli")
    paquete_canonico = importlib.import_module("pcobra.cobra.cli")

    assert sys.modules["pcobra.cli"] is modulo_pcobra_cli
    assert modulo_pcobra_cli is not paquete_canonico


def test_import_cli_no_sobrescribe_pcobra_cli():
    _limpiar_aliases()

    modulo_pcobra_cli = importlib.import_module("pcobra.cli")
    modulo_legacy_cli = importlib.import_module("cli")

    assert sys.modules["pcobra.cli"] is modulo_pcobra_cli
    assert sys.modules["cli"] is modulo_legacy_cli
    assert modulo_legacy_cli is not modulo_pcobra_cli


def test_python_m_pcobra_cli_no_colisiona(monkeypatch: pytest.MonkeyPatch):
    _limpiar_aliases()

    fake_cli_module = ModuleType("pcobra.cobra.cli.cli")

    class _FakeCliApplication:
        def run(self, _argv):
            return 0

    fake_cli_module.CliApplication = _FakeCliApplication
    monkeypatch.setitem(sys.modules, "pcobra.cobra.cli.cli", fake_cli_module)
    monkeypatch.setattr(sys, "argv", ["pcobra.cli"])

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("pcobra.cli", run_name="__main__")

    assert exc_info.value.code == 0
    assert sys.modules["pcobra.cli"].__name__ == "pcobra.cli"


def test_python_m_cli_cli_no_colisiona(monkeypatch: pytest.MonkeyPatch):
    _limpiar_aliases()

    fake_cli_module = ModuleType("pcobra.cobra.cli.cli")
    fake_cli_module.main = lambda _argv=None: 0
    monkeypatch.setitem(sys.modules, "pcobra.cobra.cli.cli", fake_cli_module)
    monkeypatch.setattr(sys, "argv", ["cli.cli"])

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("cli.cli", run_name="__main__")

    assert exc_info.value.code == 0
    assert sys.modules["pcobra.cli"].__name__ == "pcobra.cli"
    cli_cli_mod = sys.modules.get("cli.cli")
    if cli_cli_mod is not None:
        assert cli_cli_mod.__name__ in {"cli.cli", "pcobra.cobra.cli.cli"}
