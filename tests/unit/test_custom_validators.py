import pytest
from src.core.interpreter import InterpretadorCobra
from src.core.semantic_validators.base import ValidadorBase
from src.core.ast_nodes import NodoValor

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
        'from core.semantic_validators.base import ValidadorBase\n'
        'class V(ValidadorBase):\n'
        '    def visit_valor(self, nodo):\n'
        '        raise Exception("file")\n'
        'VALIDADORES_EXTRA = [V()]\n'
    )
    interp = InterpretadorCobra(safe_mode=True, extra_validators=str(mod))
    with pytest.raises(Exception):
        interp.ejecutar_ast([NodoValor(2)])

