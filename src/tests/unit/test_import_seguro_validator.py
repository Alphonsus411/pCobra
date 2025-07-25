import pytest
from types import SimpleNamespace
from core.semantic_validators.import_seguro import ValidadorImportSeguro
from core.semantic_validators.primitiva_peligrosa import PrimitivaPeligrosaError
from core.ast_nodes import NodoImport


def test_import_seguro_fuera_de_ruta(tmp_path, monkeypatch):
    validator = ValidadorImportSeguro()
    nodo = NodoImport(str(tmp_path / "m.co"))
    monkeypatch.setattr('src.core.interpreter.MODULES_PATH', str(tmp_path / 'mods'))
    monkeypatch.setattr('src.core.interpreter.IMPORT_WHITELIST', set())
    with pytest.raises(PrimitivaPeligrosaError):
        nodo.aceptar(validator)
