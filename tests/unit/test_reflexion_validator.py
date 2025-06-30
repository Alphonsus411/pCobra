import pytest
from src.core.semantic_validators.reflexion_segura import ValidadorProhibirReflexion
from src.core.semantic_validators.primitiva_peligrosa import PrimitivaPeligrosaError
from src.core.ast_nodes import NodoLlamadaFuncion, NodoAtributo, NodoIdentificador


def test_reflexion_funcion_prohibida():
    validator = ValidadorProhibirReflexion()
    nodo = NodoLlamadaFuncion("eval", [])
    with pytest.raises(PrimitivaPeligrosaError):
        nodo.aceptar(validator)


def test_reflexion_atributo_prohibido():
    validator = ValidadorProhibirReflexion()
    nodo = NodoAtributo(NodoIdentificador("obj"), "__dict__")
    with pytest.raises(PrimitivaPeligrosaError):
        nodo.aceptar(validator)
