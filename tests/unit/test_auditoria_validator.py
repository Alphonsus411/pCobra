import logging
import pcobra  # garantiza rutas para submódulos
import pytest
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core.ast_nodes import NodoLlamadaFuncion, NodoUsar, NodoValor
from pcobra.core.semantic_validators import PrimitivaPeligrosaError
from pcobra.core.semantic_validators.auditoria import ValidadorAuditoria


def test_auditoria_no_emite_en_analysis_durante_semantica(caplog):
    interp = InterpretadorCobra()
    nodo = NodoLlamadaFuncion("leer_archivo", [NodoValor("x")])
    with caplog.at_level(logging.WARNING):
        with pytest.raises(PrimitivaPeligrosaError):
            interp.ejecutar_ast([nodo])
    assert not caplog.records


def test_validador_auditoria_diagnostico_solo_en_debug(caplog):
    validador = ValidadorAuditoria(emitir_side_effects=True)

    caplog.clear()
    with caplog.at_level(logging.INFO):
        validador.visit_llamada_funcion(NodoLlamadaFuncion("main", []))
        validador.visit_usar(NodoUsar("archivo"))
    assert not [r for r in caplog.records if "Llamada a funcion" in r.message or "Usar modulo" in r.message]

    caplog.clear()
    with caplog.at_level(logging.DEBUG):
        validador.visit_llamada_funcion(NodoLlamadaFuncion("main", []))
        validador.visit_usar(NodoUsar("archivo"))
    mensajes = [r.message for r in caplog.records]
    assert "Usar modulo: archivo" in mensajes


def test_validador_auditoria_no_emite_side_effects_en_analysis(caplog):
    validador_analysis = ValidadorAuditoria(emitir_side_effects=False)
    with caplog.at_level(logging.DEBUG):
        validador_analysis.visit_usar(NodoUsar("archivo"))
    assert not caplog.records
