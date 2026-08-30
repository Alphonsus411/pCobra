import pytest
from types import SimpleNamespace
from pcobra.core.semantic_validators.import_seguro import ValidadorImportSeguro
from pcobra.core.semantic_validators.primitiva_peligrosa import PrimitivaPeligrosaError
from pcobra.core.ast_nodes import NodoImport
from pcobra.core.interpreter import InterpretadorCobra, IMPORT_WHITELIST


def test_import_seguro_fuera_de_ruta(tmp_path, monkeypatch):
    validator = ValidadorImportSeguro()
    nodo = NodoImport(str(tmp_path / "m.co"))
    monkeypatch.setattr("pcobra.core.interpreter.MODULES_PATH", str(tmp_path / "mods"))
    monkeypatch.setattr("pcobra.core.interpreter.IMPORT_WHITELIST", set())
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


def _cargar_modulo_validador(tmp_path, source, monkeypatch):
    mod = tmp_path / "validadores.py"
    mod.write_text(source, encoding="utf-8")
    IMPORT_WHITELIST.add(str(tmp_path))
    monkeypatch.setenv("PCOBRA_VALIDATOR_TIMEOUT", "3")
    try:
        return InterpretadorCobra._cargar_validadores(str(mod))
    finally:
        IMPORT_WHITELIST.discard(str(tmp_path))


def test_worker_validador_resultado_valido(tmp_path, monkeypatch):
    validadores = _cargar_modulo_validador(
        tmp_path,
        "VALIDADORES_EXTRA = [{'nombre': 'reflexion_segura', 'parametros': {}}]\n",
        monkeypatch,
    )
    assert len(validadores) == 1
    assert validadores[0].__class__.__name__ == "ValidadorProhibirReflexion"


@pytest.mark.parametrize(
    ("source", "mensaje"),
    [
        ("while True:\n    pass\n", "tiempo permitido"),
        ("VALIDADORES_EXTRA = [0] * 100_000_000\n", "memoria|proceso"),
        ("import os\n", "importaciones"),
        ("x = object.__subclasses__\n", "mágico"),
        ("raise Exception('detalle privado')\n", "forma segura"),
        ("VALIDADORES_EXTRA = [lambda: None]\n", "serializable"),
    ],
)
def test_worker_validador_fallos_controlados(tmp_path, monkeypatch, source, mensaje):
    with pytest.raises(ImportError, match=mensaje):
        _cargar_modulo_validador(tmp_path, source, monkeypatch)


def test_import_relativo_resuelto_desde_archivo_principal(tmp_path):
    proyecto = tmp_path / "proyecto"
    proyecto.mkdir()

    principal = proyecto / "main.cobra"
    modulo = proyecto / "persona.cobra"

    principal.write_text("", encoding="utf-8")
    modulo.write_text("var x = 1\n", encoding="utf-8")

    interpretador = InterpretadorCobra(main_file=principal)
    nodo = NodoImport("persona.cobra")

    nodo.aceptar(interpretador._validador)
