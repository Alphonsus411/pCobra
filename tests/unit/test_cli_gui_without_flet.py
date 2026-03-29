"""Pruebas de CLI cuando ``flet`` no está instalado."""

import builtins
import importlib
import sys


def test_importar_cli_no_falla_sin_flet_hasta_invocar_gui(monkeypatch, capsys):
    """Los imports de CLI deben funcionar sin ``flet`` hasta ejecutar ``gui``."""
    monkeypatch.delitem(sys.modules, "flet", raising=False)

    real_import = builtins.__import__

    def _import_fail_flet(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "flet":
            raise ModuleNotFoundError("No module named 'flet'", name="flet")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _import_fail_flet)

    importlib.import_module("pcobra.cobra.cli.commands.flet_cmd")
    cli_module = importlib.import_module("pcobra.cobra.cli.cli")

    result = cli_module.main(["gui"])

    captured = capsys.readouterr()
    assert result == 1
    assert "Falta la dependencia 'flet'. Ejecuta: pip install flet." in captured.out
