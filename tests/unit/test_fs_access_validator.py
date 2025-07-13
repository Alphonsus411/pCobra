import pytest
from core.semantic_validators.fs_access import ValidadorSistemaArchivos
from core.semantic_validators.primitiva_peligrosa import PrimitivaPeligrosaError
from core.ast_nodes import NodoLlamadaFuncion, NodoLlamadaMetodo


def test_fs_access_funcion_prohibida():
    validator = ValidadorSistemaArchivos()
    nodo = NodoLlamadaFuncion("cargar_funcion", [])
    with pytest.raises(PrimitivaPeligrosaError):
        nodo.aceptar(validator)


def test_fs_access_metodo_prohibido():
    validator = ValidadorSistemaArchivos()
    nodo = NodoLlamadaMetodo("m", "cargar_biblioteca", [])
    with pytest.raises(PrimitivaPeligrosaError):
        nodo.aceptar(validator)
