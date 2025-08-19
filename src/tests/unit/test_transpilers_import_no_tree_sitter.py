import builtins
import sys


def test_import_cobra_transpilers_without_tree_sitter(monkeypatch):
    """Importar cobra.transpilers no requiere tree_sitter."""

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("tree_sitter"):
            raise ModuleNotFoundError
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    sys.modules.pop("cobra.transpilers", None)
    sys.modules.pop("cobra.transpilers.reverse", None)

    import cobra.transpilers as tr

    assert hasattr(tr, "BaseTranspiler")
    assert tr.BaseReverseTranspiler.__name__ == "BaseReverseTranspiler"

