import builtins
import importlib
import sys


def test_runtime_import_no_requiere_flet(monkeypatch):
    """El runtime GUI debe importarse aunque Flet no esté instalado."""

    sys.modules.pop("pcobra.gui.runtime", None)
    sys.modules.pop("flet", None)
    real_import = builtins.__import__

    def import_without_flet(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "flet" or name.startswith("flet."):
            raise ModuleNotFoundError("No module named 'flet'", name="flet")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", import_without_flet)

    runtime = importlib.import_module("pcobra.gui.runtime")

    assert callable(runtime.require_flet)
