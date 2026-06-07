import logging

import pytest

from pcobra.cobra.core import Lexer, Parser
from pcobra.core.interpreter import InterpretadorCobra


def generar_ast(codigo: str):
    tokens = Lexer(codigo).analizar_token()
    return Parser(tokens).parsear()


def test_usar_numpy_rechaza_con_error_corto_sin_detalle_tecnico():
    interp = InterpretadorCobra()

    with pytest.raises(PermissionError) as excinfo:
        interp.ejecutar_ast(generar_ast('usar "numpy"'))

    assert str(excinfo.value) == "No se puede usar 'numpy': módulo fuera del catálogo público."
    assert "usar_error[" not in str(excinfo.value)
    assert "USAR_COBRA_PUBLIC_MODULES" not in str(excinfo.value)


def test_usar_numpy_no_filtra_detalle_tecnico_en_log_normal(caplog):
    interp = InterpretadorCobra()

    with caplog.at_level(logging.DEBUG), pytest.raises(PermissionError):
        interp.ejecutar_ast(generar_ast('usar "numpy"'))

    mensajes = "\n".join(record.message for record in caplog.records)
    assert "usar_error[" not in mensajes
    assert "USAR_COBRA_PUBLIC_MODULES" not in mensajes


def test_usar_numpy_incluye_detalle_tecnico_solo_con_debug(monkeypatch):
    monkeypatch.setenv("PCOBRA_DEBUG_RUNTIME", "1")
    interp = InterpretadorCobra()

    with pytest.raises(PermissionError) as excinfo:
        interp.ejecutar_ast(generar_ast('usar "numpy"'))

    mensaje = str(excinfo.value)
    assert mensaje.startswith("No se puede usar 'numpy': módulo fuera del catálogo público.")
    assert "usar_error[modulo_fuera_catalogo_publico]" in mensaje
    assert "USAR_COBRA_PUBLIC_MODULES" in mensaje
