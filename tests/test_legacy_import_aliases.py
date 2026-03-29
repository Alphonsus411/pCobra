import importlib
import sys
import types


def _instalar_cli_application_stub(monkeypatch):
    modulo_cli = types.ModuleType("pcobra.cobra.cli.cli")

    class _CliApplicationStub:
        def run(self, _argv):
            return 0

    modulo_cli.CliApplication = _CliApplicationStub
    monkeypatch.setitem(sys.modules, "pcobra.cobra.cli.cli", modulo_cli)


def _limpiar_aliases_legacy():
    for alias in ("cobra", "cobra.core", "core"):
        sys.modules.pop(alias, None)


def test_sin_legacy_no_hay_aliases_en_sys_modules(monkeypatch):
    _limpiar_aliases_legacy()
    monkeypatch.delenv("PCOBRA_ENABLE_LEGACY_IMPORTS", raising=False)
    _instalar_cli_application_stub(monkeypatch)

    pcobra_cli = importlib.import_module("pcobra.cli")
    monkeypatch.setattr(pcobra_cli, "configurar_entorno", lambda: None)

    assert pcobra_cli.main([]) == 0
    assert "cobra" not in sys.modules
    assert "cobra.core" not in sys.modules
    assert "core" not in sys.modules


def test_con_legacy_explicito_se_registran_aliases(monkeypatch):
    _limpiar_aliases_legacy()
    monkeypatch.setenv("PCOBRA_ENABLE_LEGACY_IMPORTS", "1")
    _instalar_cli_application_stub(monkeypatch)

    pcobra_cli = importlib.import_module("pcobra.cli")
    monkeypatch.setattr(pcobra_cli, "configurar_entorno", lambda: None)

    assert pcobra_cli.main([]) == 0
    assert "cobra" in sys.modules
    assert "cobra.core" in sys.modules
    assert "core" in sys.modules
