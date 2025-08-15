import pytest
from core.interpreter import InterpretadorCobra, IMPORT_WHITELIST
from core.semantic_validators.base import ValidadorBase
from core.ast_nodes import NodoValor

class DummyError(Exception):
    pass

class DummyValidator(ValidadorBase):
    def visit_valor(self, nodo):
        raise DummyError('validado')

def test_interpreter_extra_validators_list():
    interp = InterpretadorCobra(safe_mode=True, extra_validators=[DummyValidator()])
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
        interp = InterpretadorCobra(safe_mode=True, extra_validators=str(mod))
        with pytest.raises(Exception):
            interp.ejecutar_ast([NodoValor(2)])
    finally:
        IMPORT_WHITELIST.discard(str(tmp_path))


def test_interpreter_rejects_unwhitelisted_validators(tmp_path):
    mod = tmp_path / 'vals.py'
    mod.write_text('VALIDADORES_EXTRA = []')
    with pytest.raises(ImportError):
        InterpretadorCobra(safe_mode=True, extra_validators=str(mod))


def test_validator_open_blocked(tmp_path):
    mod = tmp_path / "vals.py"
    mod.write_text("open('archivo.txt', 'w')\nVALIDADORES_EXTRA = []\n")
    IMPORT_WHITELIST.add(str(tmp_path))
    try:
        with pytest.raises(NameError):
            InterpretadorCobra._cargar_validadores(str(mod))
    finally:
        IMPORT_WHITELIST.discard(str(tmp_path))


def test_validator_import_blocked(tmp_path):
    mod = tmp_path / "vals.py"
    mod.write_text("__import__('os').system('echo hola')\nVALIDADORES_EXTRA = []\n")
    IMPORT_WHITELIST.add(str(tmp_path))
    try:
        with pytest.raises(SyntaxError):
            InterpretadorCobra._cargar_validadores(str(mod))
    finally:
        IMPORT_WHITELIST.discard(str(tmp_path))

