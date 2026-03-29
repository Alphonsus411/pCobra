from __future__ import annotations

import sys
from types import ModuleType

import pytest

from pcobra import cli as pcobra_cli


def _install_canonical_main_stub(monkeypatch: pytest.MonkeyPatch):
    modulo_canonico = ModuleType("pcobra.cobra.cli.cli")

    def _main_stub(argv=None):
        return 11 if argv is None else len(argv)

    modulo_canonico.main = _main_stub
    monkeypatch.setitem(sys.modules, "pcobra.cobra.cli.cli", modulo_canonico)
    return modulo_canonico


def test_build_legacy_cli_shim_main_contrato_cobra_cli_cli(monkeypatch):
    _install_canonical_main_stub(monkeypatch)
    monkeypatch.delitem(sys.modules, "cli", raising=False)
    monkeypatch.delitem(sys.modules, "cli.cli", raising=False)

    main = pcobra_cli.build_legacy_cli_shim_main("cobra.cli.cli")

    assert callable(main)
    assert "pcobra.cli" in sys.modules
    assert "cli" not in sys.modules
    assert "cli.cli" not in sys.modules


def test_build_legacy_cli_shim_main_contrato_cli_cli(monkeypatch):
    modulo_canonico = _install_canonical_main_stub(monkeypatch)
    monkeypatch.delitem(sys.modules, "cli", raising=False)
    monkeypatch.delitem(sys.modules, "cli.cli", raising=False)
    monkeypatch.setattr(pcobra_cli, "get_cli_module", lambda: modulo_canonico)

    main = pcobra_cli.build_legacy_cli_shim_main("cli.cli")

    assert main is modulo_canonico.main
    assert sys.modules["cli"] is pcobra_cli
    assert sys.modules["cli.cli"] is modulo_canonico
