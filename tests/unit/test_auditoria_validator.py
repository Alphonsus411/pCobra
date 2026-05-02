import logging
import pcobra  # garantiza rutas para submódulos
import pytest
from core.interpreter import InterpretadorCobra
from core.ast_nodes import NodoLlamadaFuncion, NodoValor
from core.semantic_validators import PrimitivaPeligrosaError
from core.semantic_validators.auditoria import ValidadorAuditoria


def test_auditoria_no_emite_en_analysis_durante_semantica(caplog):
    interp = InterpretadorCobra()
    nodo = NodoLlamadaFuncion("leer_archivo", [NodoValor("x")])
    with caplog.at_level(logging.WARNING):
        with pytest.raises(PrimitivaPeligrosaError):
            interp.ejecutar_ast([nodo])
    assert not caplog.records


def test_validador_auditoria_emite_solo_en_execution(caplog):
    nodo = NodoLlamadaFuncion("funcion_demo", [])

    validador_analysis = ValidadorAuditoria(emitir_side_effects=False)
    with caplog.at_level(logging.WARNING):
        validador_analysis.visit_llamada_funcion(nodo)
    assert not caplog.records

    caplog.clear()
    validador_execution = ValidadorAuditoria(emitir_side_effects=True)
    with caplog.at_level(logging.WARNING):
        validador_execution.visit_llamada_funcion(nodo)
    assert any("funcion_demo" in rec.message for rec in caplog.records)
