import logging
import backend  # garantiza rutas para submódulos
import pytest
from src.core.interpreter import InterpretadorCobra
from src.core.ast_nodes import NodoLlamadaFuncion, NodoValor
from src.core.semantic_validators import PrimitivaPeligrosaError


def test_auditoria_registra_primitiva(caplog):
    interp = InterpretadorCobra(safe_mode=True)
    nodo = NodoLlamadaFuncion("leer_archivo", [NodoValor("x")])
    with caplog.at_level(logging.WARNING):
        with pytest.raises(PrimitivaPeligrosaError):
            interp.ejecutar_ast([nodo])
    assert any("leer_archivo" in rec.message for rec in caplog.records)
