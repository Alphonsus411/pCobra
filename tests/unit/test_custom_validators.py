import pytest
import logging
from core.interpreter import InterpretadorCobra, IMPORT_WHITELIST
from core.semantic_validators.base import ValidadorBase
from core.ast_nodes import NodoValor

class DummyError(Exception):
    pass

class DummyValidator(ValidadorBase):
    def visit_valor(self, nodo):
        raise DummyError('validado')


@pytest.fixture(autouse=True)
def _evitar_limites_reales_en_tests(monkeypatch):
    monkeypatch.setattr("core.interpreter._lim_cpu", lambda *_: None)
    monkeypatch.setattr("core.interpreter._lim_mem", lambda *_: None)


def test_interpreter_extra_validators_list():
    interp = InterpretadorCobra(extra_validators=[DummyValidator()])
    with pytest.raises(DummyError):
        interp.ejecutar_ast([NodoValor(1)])


def test_interpreter_extra_validators_file(tmp_path):
    mod = tmp_path / 'vals.py'
    mod.write_text(
        'class V(ValidadorBase):\n'
        '    def visit_valor(self, nodo):\n'
        '        raise Exception("file")\n'
        'VALIDADORES_EXTRA = [V()]\n'
    )
    IMPORT_WHITELIST.add(str(tmp_path))
    try:
        interp = InterpretadorCobra(extra_validators=str(mod))
        with pytest.raises(Exception):
            interp.ejecutar_ast([NodoValor(2)])
    finally:
        IMPORT_WHITELIST.discard(str(tmp_path))


def test_interpreter_rejects_unwhitelisted_validators(tmp_path):
    mod = tmp_path / 'vals.py'
    mod.write_text('VALIDADORES_EXTRA = []')
    with pytest.raises(ImportError):
        InterpretadorCobra(extra_validators=str(mod))


def test_validator_open_blocked(tmp_path):
    mod = tmp_path / "vals.py"
    mod.write_text("open('archivo.txt', 'w')\nVALIDADORES_EXTRA = []\n")
    IMPORT_WHITELIST.add(str(tmp_path))
    try:
        with pytest.raises(ImportError, match="forma segura"):
            InterpretadorCobra._cargar_validadores(str(mod))
    finally:
        IMPORT_WHITELIST.discard(str(tmp_path))


def test_validator_import_blocked(tmp_path):
    mod = tmp_path / "vals.py"
    mod.write_text("__import__('os').system('echo hola')\nVALIDADORES_EXTRA = []\n")
    IMPORT_WHITELIST.add(str(tmp_path))
    try:
        with pytest.raises(ImportError, match="__import__"):
            InterpretadorCobra._cargar_validadores(str(mod))
    finally:
        IMPORT_WHITELIST.discard(str(tmp_path))


def test_validator_getattr_introspeccion_blocked(tmp_path):
    mod = tmp_path / "vals.py"
    mod.write_text(
        "x = getattr(__builtins__, '__subclasses__', None)\n"
        "VALIDADORES_EXTRA = []\n"
    )
    IMPORT_WHITELIST.add(str(tmp_path))
    try:
        with pytest.raises(ImportError, match="introspección"):
            InterpretadorCobra._cargar_validadores(str(mod))
    finally:
        IMPORT_WHITELIST.discard(str(tmp_path))


def test_validator_magic_attribute_blocked(tmp_path):
    mod = tmp_path / "vals.py"
    mod.write_text("x = object.__subclasses__\nVALIDADORES_EXTRA = []\n")
    IMPORT_WHITELIST.add(str(tmp_path))
    try:
        with pytest.raises(ImportError, match="atributo mágico"):
            InterpretadorCobra._cargar_validadores(str(mod))
    finally:
        IMPORT_WHITELIST.discard(str(tmp_path))


def test_validator_symlink_outside_blocked(tmp_path, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside")
    mod = outside / "vals.py"
    mod.write_text("VALIDADORES_EXTRA = []")

    inside = tmp_path / "inside"
    inside.mkdir()
    link = inside / "vals_link.py"
    link.symlink_to(mod)

    IMPORT_WHITELIST.add(str(inside))
    try:
        with pytest.raises(ImportError):
            InterpretadorCobra._cargar_validadores(str(link))
    finally:
        IMPORT_WHITELIST.discard(str(inside))


def test_validator_malicioso_timeout_controlado(tmp_path, monkeypatch):
    mod = tmp_path / "vals_loop.py"
    mod.write_text("while True:\n    pass\n")
    IMPORT_WHITELIST.add(str(tmp_path))
    def _compile_timeout(*_args, **_kwargs):
        raise TimeoutError("timeout interno sensible")

    monkeypatch.setattr("RestrictedPython.compile_restricted", _compile_timeout)
    try:
        with pytest.raises(ImportError, match="tiempo permitido"):
            InterpretadorCobra._cargar_validadores(str(mod))
    finally:
        IMPORT_WHITELIST.discard(str(tmp_path))


def test_validator_malicioso_estructura_enorme_rechazo_controlado(tmp_path, monkeypatch):
    mod = tmp_path / "vals_big.py"
    mod.write_text("VALIDADORES_EXTRA = [0] * 10_000_000\n")
    IMPORT_WHITELIST.add(str(tmp_path))
    def _compile_mem(*_args, **_kwargs):
        raise MemoryError("detalle sensible de memoria")

    monkeypatch.setattr("RestrictedPython.compile_restricted", _compile_mem)
    try:
        with pytest.raises(ImportError, match="límites de memoria"):
            InterpretadorCobra._cargar_validadores(str(mod))
    finally:
        IMPORT_WHITELIST.discard(str(tmp_path))


def test_validator_error_sin_filtrar_internals(tmp_path):
    mod = tmp_path / "vals_bad.py"
    mod.write_text("def x(:\n    pass\n")
    IMPORT_WHITELIST.add(str(tmp_path))
    try:
        with pytest.raises(ImportError) as excinfo:
            InterpretadorCobra._cargar_validadores(str(mod))
        assert "syntax" not in str(excinfo.value).lower()
        assert str(mod) not in str(excinfo.value)
    finally:
        IMPORT_WHITELIST.discard(str(tmp_path))


def test_validator_auditoria_con_ruta_real_y_resultado(tmp_path, caplog):
    mod = tmp_path / "vals.py"
    mod.write_text("VALIDADORES_EXTRA = []\n")
    IMPORT_WHITELIST.add(str(tmp_path))
    try:
        with caplog.at_level(logging.WARNING):
            InterpretadorCobra._cargar_validadores(str(mod))
        assert any(
            "ruta_real" in rec.message
            and str(mod.resolve()) in rec.message
            and "permitido" in rec.message
            and "hash_corto" in rec.message
            and "fase" in rec.message
            for rec in caplog.records
        )
    finally:
        IMPORT_WHITELIST.discard(str(tmp_path))
