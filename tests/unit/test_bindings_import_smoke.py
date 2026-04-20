from __future__ import annotations

import importlib
import runpy
import sys
from types import ModuleType

import pytest


def test_import_pcobra_cobra_bindings_smoke() -> None:
    modulo = importlib.import_module("pcobra.cobra.bindings")

    assert hasattr(modulo, "resolve_binding")
    assert hasattr(modulo, "BindingRoute")


def test_import_bindings_legacy_smoke() -> None:
    modulo = importlib.import_module("bindings")

    assert hasattr(modulo, "resolve_binding")
    assert modulo.__name__ == "bindings"


def test_python_m_pcobra_delega_en_pcobra_cli_main(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_cli = ModuleType("pcobra.cli")
    fake_cli.main = lambda: 0
    monkeypatch.setitem(sys.modules, "pcobra.cli", fake_cli)

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module("pcobra", run_name="__main__")

    assert excinfo.value.code == 0
