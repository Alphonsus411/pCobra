import pytest
from types import SimpleNamespace
from core.semantic_validators.import_seguro import ValidadorImportSeguro
from core.semantic_validators.primitiva_peligrosa import PrimitivaPeligrosaError
from core.ast_nodes import NodoImport
from core.interpreter import InterpretadorCobra, IMPORT_WHITELIST


def test_import_seguro_fuera_de_ruta(tmp_path, monkeypatch):
    validator = ValidadorImportSeguro()
    nodo = NodoImport(str(tmp_path / "m.co"))
    monkeypatch.setattr('core.interpreter.MODULES_PATH', str(tmp_path / 'mods'))
    monkeypatch.setattr('core.interpreter.IMPORT_WHITELIST', set())
    with pytest.raises(PrimitivaPeligrosaError):
        nodo.aceptar(validator)


def test_validadores_extra_rechaza_cadena_subclasses(tmp_path):
    mod = tmp_path / "vals.py"
    mod.write_text("x = '__subclasses__'\nVALIDADORES_EXTRA = []\n")
    IMPORT_WHITELIST.add(str(tmp_path))
    try:
        with pytest.raises(ImportError, match="introspección"):
            InterpretadorCobra._cargar_validadores(str(mod))
    finally:
        IMPORT_WHITELIST.discard(str(tmp_path))
